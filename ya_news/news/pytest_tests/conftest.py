import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
# @pytest.fixture def fx(autouse=True)
# @pytest.fixture def test(fx):
# @pytest.mark.usefixtures('start_engine')
# from forms import BAD_WORDS, WARNING, CommentForm
# CommentForm: fields = ('text',)
# models: News(title text date), Comment(news author text created)
# urls (news:home/edit/delete/detail)


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст novosty',
    )
    return news


@pytest.fixture
def many_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Заголовок {index}',
            text='novost',
            date=today - timedelta(days=index)
        )
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст novosty',
        author=author,
        news=news,
    )
    return comment


@pytest.fixture
def many_comments(author, news):
    now = timezone.now()
    all_comments = [
        Comment(
            news=news,
            author=author,
            text=f'text {index}',
            created=now + timedelta(days=index)
        )
        for index in range(10)
    ]
    Comment.objects.bulk_create(all_comments)


@pytest.fixture
def c_form_data():
    data = {
        'good_data': {'text': 'tekst'},
        'bad_data': {'text': 'редиска'}
    }
    return data
