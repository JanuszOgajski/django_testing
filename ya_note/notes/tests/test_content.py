from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
# app_name = 'notes'
# path names: home add edit detail delete list success
# model fields: title text slug author
# NoteForm 'title', 'text', 'slug'
#
#
#
#
User = get_user_model()
"""
*отдельная заметка передаётся на страницу со списком заметок в списке
object_list в словаре context;
*в список заметок одного пользователя не попадают заметки другого
пользователя;
*на страницы создания и редактирования заметки передаются формы.
"""


class TestContent(TestCase):
    NOTES_LIST = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.user_client = Client()
        cls.author1 = User.objects.create(username='test1')
        cls.author2 = User.objects.create(username='test2')
        cls.note1 = Note.objects.create(
            title='Заголовок1',
            text='Текст',
            author=cls.author1
        )
        cls.note2 = Note.objects.create(
            title='Заголовок2',
            text='Текст',
            author=cls.author2
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note1.slug,))

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
