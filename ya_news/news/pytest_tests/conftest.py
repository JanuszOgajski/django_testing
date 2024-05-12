import pytest

from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст novosty',
    )


@pytest.fixture
def many_news():
    today = timezone.now()
    all_news = [
        News(
            title=f'Заголовок {index}',
            text='novost',
            date=today - timezone.timedelta(days=index)
        )
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        text='Текст novosty',
        author=author,
        news=news,
    )


@pytest.fixture
def many_comments(author, news):
    now = timezone.now()
    all_comments = [
        Comment(
            news=news,
            author=author,
            text=f'text {index}',
            created=now + timezone.timedelta(days=index)
        )
        for index in range(10)
    ]
    Comment.objects.bulk_create(all_comments)
