from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Book
from .forms import BookForm


class BookModelTest(TestCase):

    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            publication_date=timezone.now().date(),
            pages=123
        )

    def tearDown(self):
        self.book.delete()

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Test Author")
        self.assertEqual(self.book.pages, 123)
        self.assertIsNotNone(self.book.publication_date)

    def test_str_method(self):
        self.assertEqual(str(self.book), "Test Book")

    def test_book_fields(self):
        self.assertIsInstance(self.book.title, str)
        self.assertIsInstance(self.book.author, str)
        self.assertIsInstance(self.book.pages, int)
        self.assertTrue(self.book.pages > 0)


class BookListViewTest(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('book_list'))
        self.assertTemplateUsed(response, 'book_list.html')


class BookCreateView(TestCase):
    def test_create_book(self):
        response = self.client.post(reverse('book_create'), {
            'title': "New Book",
            'author': "New Author",
            'publication_date': timezone.now().date(),
            'pages': 100
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('book_list'))
        self.assertEqual(Book.objects.first().title, 'New Book')


class BookDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            publication_date=timezone.now().date(),
            pages=123
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/{self.book.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_templates(self):
        response = self.client.get(reverse('book_detail', kwargs={'pk': self.book.pk}))
        self.assertTemplateUsed(response, 'book_detail.html')


class BookUpdateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Original Title",
            author="Original Author",
            publication_date=timezone.now().date(),
            pages=125
        )

    def test_update_book(self):
        response = self.client.post(reverse('book_update', args=[self.book.pk]), {
            'title': "Updated Title",
            'author': "Updated Author",
            'publication_date': timezone.now().date(),
            'pages': 200
        })
        self.book.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.book.title, "Updated Title")
        self.assertEqual(self.book.author, "Updated Author")
        self.assertRedirects(response, reverse('book_detail', args=[self.book.pk]))

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('book_update', args=[self.book.pk]))
        self.assertTemplateUsed(response, 'book_form.html')


class BookDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="To be deleted",
            author="Author",
            publication_date=timezone.now().date(),
            pages=150
        )

    def test_delete_book(self):
        response = self.client.post(reverse('book_delete', args=[self.book.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('book_list'))

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('book_delete', args=[self.book.pk]))
        self.assertTemplateUsed(response, 'book_confirm_delete.html')


class BookFormTest(TestCase):
    def test_valid_form(self):
        data = {'title': 'Valid Title', 'author': 'Valid Author', 'publication_date': timezone.now().date(), 'pages': 200}
        form = BookForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {'title': '', 'author': 'Valid Author', 'publication_date': timezone.now().date(),'pages': 200}
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class RequiredFieldsTest(TestCase):

    def test_required_fields(self):
        form = BookForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['title'], ['This field is required.'])


class FormToSaveTest(TestCase):
    def test_form_save(self):
        data = {'title': 'Valid Title', 'author': 'Valid Author', 'publication_date': timezone.now().date(), 'pages': 200}
        form = BookForm(data=data)
        if form.is_valid():
            book = form.save()
            self.assertEqual(book.title, 'Valid Title')


class FormErrorMessages(TestCase):
    def test_form_is_invalid_with_incorrect_page_count(self):
        form_data = {
            'title': 'Title',
            'author': 'Author',
            'publication_date': timezone.now().date(),
            'pages': -10  # Недопустиме значення
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('pages', form.errors)

    def test_field_max_length(self):
        form_data = {
            'title': 'T' * 21,
            'author': 'A' * 21,
            'publication_date': timezone.now().date(),
            'pages': 100
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('author', form.errors)
