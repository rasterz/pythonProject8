from typing import Callable

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture()
def category_create_data(faker, goal_category) -> Callable:
    def _wrapper(**kwargs) -> dict:
        data = {'title': faker.sentence(2),
                'category': goal_category.id}
        data |= kwargs
        return data
    return _wrapper


@pytest.mark.django_db
class TestBoardCreateView:
    url = reverse('todolist.goals:create-goal')

    def test_auth_required(self, client, category_create_data):
        """
        Test that auth is required to create a goal
        """
        response = client.post(self.url, data=category_create_data())
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auth_user_can_create_goal(self, client, category_create_data, user):
        """
        Test that a goal can be created
        """
        client.force_authenticate(user)
        response = client.post(self.url, data=category_create_data())
        assert response.status_code == status.HTTP_201_CREATED
