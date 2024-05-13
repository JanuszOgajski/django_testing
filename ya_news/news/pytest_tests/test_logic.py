from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment

C_FORM_DATA = {
    'good_data': {'text': 'tekst'},
    'bad_data': {'text': 'редиска'}
}


@pytest.mark.django_db
class TestLogic:
    def test_user_comment(self, news, author_client, author,):
        count_before = Comment.objects.count()
        url = reverse('news:detail', args=(news.pk,))
        response = author_client.post(url, data=C_FORM_DATA['good_data'])
        assertRedirects(
            response,
            reverse('news:detail', args=(news.pk,)) + '#comments'
        )
        assert Comment.objects.count() == count_before + 1
        new_comment = Comment.objects.get()
        assert new_comment.text == C_FORM_DATA['good_data']['text']

    def test_anon_comment(self, news, client,):
        count_before = Comment.objects.count()
        url = reverse('news:detail', args=(news.pk,))
        response = client.post(url, data=C_FORM_DATA['good_data'])
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        assertRedirects(response, expected_url)
        assert Comment.objects.count() == count_before

    def test_warning(self, author_client, news):
        count_before = Comment.objects.count()
        url = reverse('news:detail', args=(news.pk,))
        response = author_client.post(
            url, data=C_FORM_DATA['bad_data'])
        assertFormError(response, 'form', 'text', errors=WARNING)
        assert Comment.objects.count() == count_before

    def test_author_edit_com(self, author_client, news, comment):
        url = reverse('news:edit', args=(comment.pk,))
        response = author_client.post(url, C_FORM_DATA['good_data'])
        assertRedirects(
            response,
            reverse('news:detail', args=(news.pk,)) + '#comments'
        )
        comment.refresh_from_db()
        assert comment.text == C_FORM_DATA['good_data']['text']

    def test_reader_edit_com(self, not_author_client, comment):
        url = reverse('news:edit', args=(comment.pk,))
        response = not_author_client.post(url, C_FORM_DATA['good_data'])
        assert response.status_code == HTTPStatus.NOT_FOUND
        comment_from_db = Comment.objects.get(pk=comment.pk)
        assert comment.text == comment_from_db.text

    def test_author_delete_com(self, author_client, news, comment):
        count_before = Comment.objects.count()
        url = reverse('news:delete', args=(comment.pk,))
        response = author_client.post(url)
        assertRedirects(
            response,
            reverse('news:detail', args=(news.pk,)) + '#comments'
        )
        assert Comment.objects.count() == count_before - 1

    def test_reader_delete_com(self, not_author_client, comment):
        count_before = Comment.objects.count()
        url = reverse('news:delete', args=(comment.pk,))
        response = not_author_client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Comment.objects.count() == count_before
