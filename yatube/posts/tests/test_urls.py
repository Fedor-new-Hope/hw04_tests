from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

from posts.tests.constants import (
    AUTHOR_USERNAME,
    USER_USERNAME,
    GROUP_TITLE,
    GROUP_SLUG,
    GROUP_DESCRIPTION,
    POST_TEXT,
    INDEX_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    CREATE_POST_TEMPLATE,
    INDEX_URL_NAME,
    GROUP_LIST_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
)


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.user_2 = User.objects.create_user(username=USER_USERNAME)
        super().setUpClass()
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)
        self.url_names_all_user = [
            reverse(INDEX_URL_NAME),
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}),
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.post.author}),
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id}),
        ]

        self.url_names_not_found = [
            '/unexisting_page/',
            '/new/',
        ]

        self.templates_url_names = {
            '/': INDEX_TEMPLATE,
            f'/group/{self.group.slug}/': GROUP_LIST_TEMPLATE,
            f'/profile/{self.user}/': PROFILE_TEMPLATE,
            f'/posts/{self.post.id}/': POST_DETAIL_TEMPLATE,
            f'/posts/{self.post.id}/edit/': CREATE_POST_TEMPLATE,
            '/create/': CREATE_POST_TEMPLATE,
        }

    def test_urls_uses_correct_template(self):
        """Страницы используют соответствующий шаблон."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_anonymous(self):
        """Страницы доступна любому пользователю."""
        for address in self.url_names_all_user:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_edit_post_guest_client(self):
        """Страница post_edit для анонимного поьователя сделает редирект."""
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_edit_url_uses_correct_template_is_author(self):
        """Страница /posts/<post_id>/edit/
        использует шаблон posts/create_post.html.
        Доступно только автору"""
        with self.subTest(author=self.user):
            response = self.authorized_client.get(
                f'/posts/{self.post.id}/edit/'
            )
            self.assertTemplateUsed(response, CREATE_POST_TEMPLATE)

    def test_edit_post_authorized_client_no_autor(self):
        """Страница post_edit авторизированного пользователя,
        не автора, сделает редирект."""
        response = self.authorized_client_2.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_not_found_404(self):
        """Страницы не существует (404)."""
        for address in self.url_names_not_found:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)
