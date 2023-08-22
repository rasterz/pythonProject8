from typing import Callable
import pytest
from django.urls import reverse
from rest_framework import status
from todolist.goals.models import Board, BoardParticipant


@pytest.fixture()
def board_create_data(faker) -> Callable:
    def _wrapper(**kwargs) -> dict:
        data = {'title': faker.sentence(2)}
        data |= kwargs
        return data

    return _wrapper


@pytest.mark.django_db
class TestBoardCreateView:
    url = reverse('todolist.goals:create-board')

    def test_auth_required(self, client, board_create_data):
        """
        Test that auth is required to create a board
        """
        response = client.post(self.url, data=board_create_data())
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_create_deleted_board(self, auth_client, board_create_data):
        """
        Test that it is not possible to create a board with a deleted tag
        """
        response = auth_client.post(self.url, data=board_create_data(is_deleted=True))
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['is_deleted'] is False
        assert Board.objects.last().is_deleted is False

    def test_request_user_became_board_owner(self, auth_client, user, board_create_data):
        """
        Test that the user who created the board becomes its owner
        """
        response = auth_client.post(self.url, data=board_create_data())
        board_participants = BoardParticipant.objects.get(user_id=user.id)

        assert response.status_code == status.HTTP_201_CREATED
        assert board_participants.board_id == response.data['id']
        assert board_participants.role == BoardParticipant.Role.owner
