from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestMixin():
    @classmethod
    def setUpTestData(cls):
        cls.author_client = Client()
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
        cls.reader_client = Client()
        cls.reader = User.objects.create(username='test3')
        cls.form_data = {'title': 'nazvanie', 'text': 'Tekst zametky'}
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note1.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note1.slug,))
