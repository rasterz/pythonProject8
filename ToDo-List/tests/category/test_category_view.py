import pytest
from django.urls import reverse
from rest_framework import status
from todolist.goals.models import BoardParticipant, GoalCategory


@pytest.mark.django_db
class TestCategoryRetrieveView:

    @pytest.fixture(autouse=True)
    def setup(self, goal_category, user):
        self.category = goal_category
        self.board = goal_category.board
        self.owner = user
        BoardParticipant.objects.create(board=self.board, user=self.owner, role=BoardParticipant.Role.owner)
        self.url = self.get_url(self.category.pk)

    @staticmethod
    def get_url(category_pk: int) -> str:
        return reverse('todolist.goals:category', kwargs={'pk': category_pk})

    def test_owner_can_retrieve_category(self, client):
        client.force_login(user=self.owner)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_auth_required_to_get_category(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_retrieve_deleted_category(self, auth_client, goal_category):
        goal_category.is_deleted = True
        goal_category.save()

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert GoalCategory.objects.last().is_deleted is True


@pytest.mark.django_db()
class TestCategoryDeleteView:

    @pytest.fixture(autouse=True)
    def setup(self, goal_category, user):
        self.category = goal_category
        self.board = goal_category.board
        self.owner = user
        BoardParticipant.objects.create(board=self.board, user=self.owner, role=BoardParticipant.Role.owner)
        self.url = self.get_url(self.category.pk)

    @staticmethod
    def get_url(category_pk: int) -> str:
        return reverse('todolist.goals:category', kwargs={'pk': category_pk})

    def test_auth_required_to_delete_category(self, client):
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_delete_category(self, client):
        client.force_login(user=self.owner)
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
