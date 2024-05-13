from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from .mixins import TestMixin

User = get_user_model()


class TestContent(TestMixin, TestCase):
    NOTES_LIST = reverse('notes:list')

    def test_note_in_context(self):
        self.client.force_login(self.author1)
        response = self.client.get(self.NOTES_LIST)
        object_list = response.context['object_list']
        self.assertIn(self.note1, object_list)

    def test_note_notin_context(self):
        self.client.force_login(self.author1)
        response = self.client.get(self.NOTES_LIST)
        object_list = response.context['object_list']
        self.assertNotIn(self.note2, object_list)

    def test_forms(self):
        self.client.force_login(self.author1)
        for url in (self.add_url, self.edit_url):
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
