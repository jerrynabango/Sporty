from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Comment, ContactMessage, Post
from .forms import CommentForm, ContactForm

# Create your tests here.
CustomUser = get_user_model()


class TestViews(TestCase):
    def setUp(self):
        """
        Test setup method.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Jerry',
            last_name='Nabango'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user
        )

    def test_SignUp_GET(self):
        """
        Test for SignUp view for GET request.
        """
        response = self.client.get(reverse('SignUp'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'SignUp.html')

    def test_SignIn_GET(self):
        """Test for SignIn view for GET request.
        """
        response = self.client.get(reverse('SignIn'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'SignIn.html')

    def test_LogOut(self):
        """
        Test for LogOut view.
        """
        response = self.client.get(reverse('LogOut'))
        self.assertEqual(response.status_code, 302)  # Redirect to SignIn page

    def test_summary_GET(self):
        """
        Test for summary view for GET request.
        """
        response = self.client.get(reverse('summary', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'summary.html')
        self.assertContains(response, 'Test Post')

    def test_created_GET(self):
        """
        Test for created view for GET request.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('created'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create.html')

    def test_settings_GET(self):
        """
        Test for settings view for GET request.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings.html')

    def test_threads_GET(self):
        """
        Test for threads view for GET request.
        """
        response = self.client.get(reverse('threads'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'threads.html')

    def test_contact_us_GET(self):
        """
        Test for contact_us view for GET request.
        """
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

    def test_contact_us_POST_valid_form(self):
        """
        Test for contact_us view for POST request with valid form data.
        """
        data = {
            'name': 'Jerry Nabango',
            'email': 'nabango@gmail.com',
            'message': 'This is a test message.'
        }
        response = self.client.post(reverse('contact_us'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')
        self.assertContains(response, 'Thank you for contacting us')

        def test_contact_us_POST_invalid_form(self):
            """
            Test for contact_us view for POST request with invalid form data.
            """
            data = {
                'name': 'Jerry Nabango',
                'email': 'invalidemail',
                'message': ''
                }
            response = self.client.post(reverse('contact_us'), data)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'contact.html')
            self.assertContains(response, 'Invalid email address',
                                status_code=200)  # Check for 'Invalid email address' message
            self.assertContains(response, 'Comment cannot be empty.',
                                status_code=200)  # Check for 'Comment cannot be empty.' message
