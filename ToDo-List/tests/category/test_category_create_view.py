from typing import Callable
import pytest
from django.urls import reverse
from rest_framework import status
from todolist.goals.models import GoalCategory


@pytest.fixture()
def category_create_data(faker, board) -> Callable:
    def _wrapper(**kwargs) -> dict:
        data = {'title': faker.sentence(2),
                'board': board.id}
        data |= kwargs
        return data

    return _wrapper


@pytest.mark.django_db
class TestBoardCreateView:
    url = reverse('todolist.goals:create-category')

    def test_auth_required(self, client, category_create_data):
        """
        Test that auth is required to create a category
        """
        response = client.post(self.url, data=category_create_data())
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_create_deleted_category(self, auth_client, category_create_data):
        """
        Test that it is not possible to create a category with a deleted tag
        """
        response = auth_client.post(self.url, data=category_create_data(is_deleted=True))
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['is_deleted'] is False
        assert GoalCategory.objects.last().is_deleted is False
