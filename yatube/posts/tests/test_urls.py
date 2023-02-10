from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nikolo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(URLTests.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Для всех пользователей"""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_url_uses_correct_template_is_author(self):
        """Страница /posts/<post_id>/edit/
        использует шаблон posts/create_post.html.
        Доступно только автору"""
        with self.subTest(author=self.user):
            response = self.authorized_client.get(
                f'/posts/{self.post.id}/edit/'
            )
            self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_url_uses_correct_template(self):
        """Страница /create/ доступна авторизированному пользователю"""
        response_authorized = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response_authorized, 'posts/create_post.html')

    def test_task_added_url_exists_at_desired_location(self):
        """Страница /unexsting_page/ доступна любому пользователю.
        страницы не существует (404)"""
        response = self.guest_client.get('/unexsting_page/')
        self.assertEqual(response.status_code, 404)
