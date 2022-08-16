import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login(recipe_ingredient, client, user_password, user):
    url = reverse('login')
    payload = {
            'password': user_password,
            'email': user.email,
        }
    response = client.post(url, data=payload, content_type='application/json')
    assert response.status_code == 201, response.data
    assert response.data['auth_token'] is not None
