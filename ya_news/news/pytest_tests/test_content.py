import pytest
from django.urls import reverse

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
class TestContent:
    def test_homepage_count(self, many_news, client):
        url = reverse('news:home')
        response = client.get(url)
        object_list = response.context['object_list']
        assert object_list.count() == NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, many_news, client):
        url = reverse('news:home')
        response = client.get(url)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates

    def test_comment_order(self, many_comments, news, client):
        url = reverse('news:detail', args=(news.pk,))
        response = client.get(url)
        new = response.context['news']
        comments = new.comment_set.all()
        all_timestamps = [comment.created for comment in comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    def test_forms(self, author_client, client, news):
        url = reverse('news:detail', args=(news.pk,))
        response = author_client.get(url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
        response = client.get(url)
        assert 'form' not in response.context
