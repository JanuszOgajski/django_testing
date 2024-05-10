import pytest
from pytest_django.asserts import assertRedirects

from http import HTTPStatus

from django.urls import reverse
# pytest --trace --lf -x
# breakpoint()
# @pytest.mark.<название маркера> skipif xfail usefixtures
# @pytest.mark.parametrize(
#    'input_arg, expected_result',  # Названия аргументов, передаваемых в тест.
#    [(4, 5), (3, 5)]  # Список кортежей со значениями аргументов.
# )
# from forms import BAD_WORDS, WARNING, CommentForm
# CommentForm: fields = ('text',)
# models: News(title text date), Comment(news author text created)
# urls (news:home/edit/delete/detail)
# from pytest_django.asserts import assertRedirects
#

"""
*Главная страница доступна анонимному пользователю.

*Страница отдельной новости доступна анонимному пользователю.

*Страницы удаления и редактирования комментария доступны автору комментария.

*При попытке перейти на страницу редактирования или удаления комментария
анонимный пользователь перенаправляется на страницу авторизации.

*Авторизованный пользователь не может зайти на страницы редактирования
или удаления чужих комментариев (возвращается ошибка 404).

*Страницы регистрации пользователей, входа в учётную запись и выхода из
неё доступны анонимным пользователям.
"""


@pytest.mark.django_db
class TestRoutes:
    @pytest.mark.parametrize(
        'name',
        ('news:home', 'users:login', 'users:logout', 'users:signup')
    )
    def test_pages_availability_for_anonymous_user(self, client, name):
        url = reverse(name)  # Получаем ссылку на нужный адрес.
        response = client.get(url)  # Выполняем запрос.
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
