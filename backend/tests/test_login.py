import pytest
from django.urls import reverse


@pytest.fixture
def admin_client(token_admin):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_admin["access"]}')
    return client


@pytest.mark.django_db
def test_login(recipe_ingredient, client, user_password, user):
    url = reverse('login')
    payload = {
            'password': user_password,
            'email': user.email,
        }
    response = client.post(url, data=payload, content_type='application/json')
    assert response.status_code == 200, response.data
    assert response.data['auth_token'] is not None


@pytest.mark.django_db
def test_user_list(recipe_ingredient, client, user_password, user):
    url = '/api/users/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_user(recipe_ingredient, client, user_password, user):
    url = '/api/users/'
    payload = {
        "email": "vpupkin@yandex.ru",
        "username": "vasya.pupkin",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "password": "Qwerty123"
    }
    response = client.post(url, payload, content_type='application/json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_me_2(user_password, user):
    from rest_framework.test import APIClient
    client = APIClient()
    url = reverse('login')
    payload = {
        'password': user_password,
        'email': user.email,
    }
    test_response = client.post(url, payload, format='json')
    assert test_response.status_code == 200
    token = test_response.data['auth_token']
    url_me = reverse('user-me')

    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    response = client.get(url_me)
    assert response.status_code == 200
    #assert response.data is None

