from http import HTTPStatus
from pytils.translit import slugify

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
# app_name = 'notes'
# path names: home add edit detail delete list success
# model fields: title text slug author
# slug = slugify(title)[:100]
# NoteForm 'title', 'text', 'slug'
#
#
#
User = get_user_model()
"""
*Залогиненный пользователь может создать заметку, а анонимный — не может.

*Невозможно создать две заметки с одинаковым slug.

*Если при создании заметки не заполнен slug, то он формируется
автоматически, с помощью функции pytils.translit.slugify.

*Пользователь может редактировать и удалять свои заметки, но не может
редактировать или удалять чужие.
"""


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author_client = Client()
        cls.author1 = User.objects.create(username='test1')
        cls.reader_client = Client()
        cls.reader = User.objects.create(username='test2')
        cls.note1 = Note.objects.create(
            title='Заголовок1',
            text='Текст',
            author=cls.author1
        )
        cls.form_data = {'title': 'nazvanie', 'text': 'Tekst zametky'}
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note1.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note1.slug,))

    def test_anon_user_post_notes(self):
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.author_client.force_login(self.author1)
        self.author_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_duble_slug(self):
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
        self.assertEqual(notes_count, 1)

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
        self.assertEqual(notes_count, 0)
