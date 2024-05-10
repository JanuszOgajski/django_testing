from http import HTTPStatus

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
# app_name = 'notes'
# path names: home add edit detail delete list success
# model fields: title text slug author
#
#
#
#
#
User = get_user_model()


"""
*Главная страница доступна анонимному пользователю.

*Аутентифицированному пользователю доступна страница со списком заметок
notes/, страница успешного добавления заметки done/, страница добавления
новой заметки add/.

*Страницы отдельной заметки, удаления и редактирования заметки доступны
только автору заметки. Если на эти страницы попытается зайти другой
пользователь — вернётся ошибка 404.

*При попытке перейти на страницу списка заметок, страницу успешного
добавления записи, страницу добавления заметки, отдельной заметки,
редактирования или удаления заметки анонимный пользователь
перенаправляется на страницу логина.

*Страницы регистрации пользователей, входа в учётную запись и выхода из
неё доступны всем пользователям.
"""


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_client = Client()
        cls.author = User.objects.create(username='test1')
        cls.reader = User.objects.create(username='test2')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_anon_pages(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_done_add(self):
        self.client.force_login(self.reader)
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_pages(self):
        users_statuses = (
            # автор комментария должен получить ответ OK,
            (self.author, HTTPStatus.OK),
            # читатель должен получить ответ NOT_FOUND.
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in (
            'notes:edit',
            'notes:delete',
            'notes:detail',
        ):
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': self.note.slug})
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in (
            'notes:add',
            'notes:list',
            'notes:success',
        ):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    """def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        paths = (
            'notes:edit',
            'notes:delete',
            'notes:detail',
            'notes:add',
            'notes:list',
            'notes:success',
        )
        for name in paths:
            if name in ('notes:add', 'notes:list', 'notes:success',):
                args = None
            else:
                args = self.note.slug
            name = name, args

        for name, args in paths:  # не распаковывается
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)"""
