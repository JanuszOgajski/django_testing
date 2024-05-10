import pytest

from django.urls import reverse

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from news.forms import CommentForm
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
*Количество новостей на главной странице — не более 10.

*Новости отсортированы от самой свежей к самой старой. Свежие новости
в начале списка.

*Комментарии на странице отдельной новости отсортированы в хронологическом
порядке: старые в начале списка, новые — в конце.

*Анонимному пользователю недоступна форма для отправки комментария на
странице отдельной новости, а авторизованному доступна.
"""


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
