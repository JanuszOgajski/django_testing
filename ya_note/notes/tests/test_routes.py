from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .mixins import TestMixin

User = get_user_model()


class TestRoutes(TestMixin, TestCase):
    URLS = ('notes:add', 'notes:list', 'notes:success',)
    SLUG_URLS = ('notes:edit', 'notes:delete', 'notes:detail',)

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
        urls = ((path, None) for path in self.URLS)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_pages(self):
        users_statuses = (
            (self.author1, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in self.SLUG_URLS:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note1.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in self.SLUG_URLS:
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': self.note1.slug})
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in self.URLS:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
