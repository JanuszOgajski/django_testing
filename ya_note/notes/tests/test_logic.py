from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

from .t_mixin import TestMixin

User = get_user_model()


class TestLogic(TestMixin, TestCase):

    def test_anon_user_post_notes(self):
        count_before = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, count_before)
        self.author_client.force_login(self.author1)
        self.author_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, count_before + 1)

    def test_duble_slug(self):
        count_before = Note.objects.count()
        slug1 = self.note1.slug
        self.form_data['slug'] = slug1
        self.author_client.force_login(self.author1)
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(slug1 + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, count_before)

    def test_slugify_slug(self):
        slug1 = self.note1.slug
        slug2 = slugify(self.note1.title)[:100]
        self.assertEqual(slug1, slug2)

    def test_edit_delete_reader(self):
        self.reader_client.force_login(self.reader)
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_delete_author(self):
        count_before = Note.objects.count()
        self.author_client.force_login(self.author1)
        self.author_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.text, self.form_data['text'])
        self.author_client.delete(
            reverse('notes:delete', args=(self.note1.slug,))
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, count_before - 1)
