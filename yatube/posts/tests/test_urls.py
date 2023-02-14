# Доброго времени суток, Антон, не стал писать в пачке в столь поздний час,
# доделал и решил сюда написать перед отправкой.
# У меня вопрос по замечаниям к этому файлу 9 строка.
#
"""В файле должны быть тесты:
 Страницы доступны и работают:
 1. главная страница /,
 2. страница группы /group/<slug>/,
 3. страница создания поста /new/:
                                     (- почему ? ведь в проекте  /create/)
 a) доступа только зарегистрированным пользователям;
 4. профайла пользователя /<username>/;
                                      (/profile/<username>/ в теории так)
 5. отдельного поста /<username>/<post_id>/;
                                                 (/posts/<post_id>/и так)
    (- почему только зарегистрированным ?
      в проекте и исходя и логики эти страницы должны быть доступны всем)

 Для следующих страниц вызываются ожидаемые шаблоны,
 при обращении к ним по URL:
 1. главная страница /,
 2. страница группы /group/<slug>/,
 3. страница создания поста /new/                   ( в проекте  /create/)
 Для страницы редактирования поста /<username>/<post_id>/edit/ для:
                                    (/posts/<post_id>/edit/ в теории так)
 1. у анонимного пользователя должен проверяться редирект.
 2. у авторизованного пользователя, автора поста нужно проверить какой
   вызывается шаблон.
 3. у авторизованного пользователя — не автора поста должен проверяться
   редирект."""
#
# Если делать согласно замечаниям то теты будут падать,
#                        соответственно надо переписывать отсальной код.
# Поправил исходя из разумных соображений))
from http import HTTPStatus

from django.test import TestCase, Client

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
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.id}/',
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
