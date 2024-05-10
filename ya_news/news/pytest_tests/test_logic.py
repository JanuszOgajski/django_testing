import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from http import HTTPStatus

from django.urls import reverse

from news.models import Comment
from news.forms import WARNING
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
*Анонимный пользователь не может отправить комментарий.

*Авторизованный пользователь может отправить комментарий.

*Если комментарий содержит запрещённые слова, он не будет опубликован, а
форма вернёт ошибку.

Авторизованный пользователь может редактировать или удалять свои
комментарии.

Авторизованный пользователь не может редактировать или удалять чужие
комментарии.
"""


@pytest.mark.django_db
class TestLogic:
    def test_user_comment(self, news, author_client, author, c_form_data):
        url = reverse('news:detail', args=(news.pk,))
        response = author_client.post(url, data=c_form_data['good_data'])
        assertRedirects(
            response,
            reverse('news:detail', args=(news.pk,)) + '#comments'
        )
        assert Comment.objects.count() == 1
        new_comment = Comment.objects.get()
        assert new_comment.text == c_form_data['good_data']['text']

    def test_anon_comment(self, news, client, c_form_data):
        url = reverse('news:detail', args=(news.pk,))
        response = client.post(url, data=c_form_data['good_data'])
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        assertRedirects(response, expected_url)
        assert Comment.objects.count() == 0

    def test_warning(self, author_client, c_form_data, news):
        url = reverse('news:detail', args=(news.pk,))
        response = author_client.post(
            url, data=c_form_data['bad_data'])
        assertFormError(response, 'form', 'text', errors=WARNING)
        assert Comment.objects.count() == 0

    def test_author_edit_com(self, author_client, c_form_data, news, comment):
        url = reverse('news:edit', args=(comment.pk,))
        response = author_client.post(url, c_form_data['good_data'])
        assertRedirects(
            response,
            reverse('news:detail', args=(news.pk,)) + '#comments'
        )
        comment.refresh_from_db()
        assert comment.text == c_form_data['good_data']['text']

    def test_reader_edit_com(self, not_author_client, c_form_data, comment):
        url = reverse('news:edit', args=(comment.pk,))
        response = not_author_client.post(url, c_form_data['good_data'])
        assert response.status_code == HTTPStatus.NOT_FOUND
        comment_from_db = Comment.objects.get(pk=comment.pk)
        assert comment.text == comment_from_db.text

    def test_author_delete_com(self, author_client, news, comment):
        url = reverse('news:delete', args=(comment.pk,))
        response = author_client.post(url)
        assertRedirects(
            response,
            reverse('news:detail', args=(news.pk,)) + '#comments'
        )
        assert Comment.objects.count() == 0

    def test_reader_delete_com(self, not_author_client, c_form_data, comment):
        url = reverse('news:delete', args=(comment.pk,))
        response = not_author_client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Comment.objects.count() == 1
