from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse  # type: ignore


pytestmark = pytest.mark.django_db


USERS_LOGIN_URL = reverse('users:login')
USERS_LOGOUT_URL = reverse('users:logout')
USERS_SIGNUP_URL = reverse('users:signup')
CLIENT = pytest.lazy_fixture('client')  # type: ignore
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')  # type: ignore
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')  # type: ignore
HOME_URL = pytest.lazy_fixture('home_url')  # type: ignore
NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail_url')  # type: ignore
EDIT_COMMENT_URL = pytest.lazy_fixture('edit_comment_url')  # type: ignore
DELETE_COMMENT_URL = pytest.lazy_fixture('delete_comment_url')  # type: ignore


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (EDIT_COMMENT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_COMMENT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_COMMENT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_COMMENT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (NEWS_DETAIL_URL, CLIENT, HTTPStatus.OK),
        (USERS_LOGIN_URL, CLIENT, HTTPStatus.OK),
        (USERS_LOGOUT_URL, CLIENT, HTTPStatus.OK),
        (USERS_SIGNUP_URL, CLIENT, HTTPStatus.OK),
    ),
)
def test_pages_availability(url, parametrized_client, expected_status):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (EDIT_COMMENT_URL, DELETE_COMMENT_URL)
)
def test_redirect_for_anonymous_client(client, url):
    redirect_url = f'{USERS_LOGIN_URL}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
