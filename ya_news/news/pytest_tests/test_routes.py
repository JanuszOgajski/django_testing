from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
class TestRoutes:
    @pytest.mark.parametrize(
        'name',
        ('news:home', 'users:login', 'users:logout', 'users:signup')
    )
    def test_pages_availability_for_anonymous_user(self, client, name):
        url = reverse(name)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_detail_for_anon(self, client, news):
        url = reverse('news:detail', args=(news.pk,))
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
        ),
    )
    @pytest.mark.parametrize(
        'name',
        ('news:edit', 'news:delete'),
    )
    def test_pages_availability_for_different_users(
            self, parametrized_client, name, comment, expected_status
    ):
        url = reverse(name, args=(comment.pk,))
        response = parametrized_client.get(url)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        'name',
        ('news:edit', 'news:delete'),
    )
    def test_redirects(
            self, name, comment, client
    ):
        login_url = reverse('users:login')
        url = reverse(name, args=(comment.pk,))
        expected_url = f'{login_url}?next={url}'
        response = client.get(url)
        assertRedirects(response, expected_url)
