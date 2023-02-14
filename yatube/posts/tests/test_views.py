from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from posts.forms import PostForm

from posts.tests.constants import (
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
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
)


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NikolaY')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(ViewsTests.user)

        self.templates_pages_names = {
            reverse(INDEX_URL_NAME): INDEX_TEMPLATE,
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}): GROUP_LIST_TEMPLATE,
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.user.username}): PROFILE_TEMPLATE,
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.pk}): POST_DETAIL_TEMPLATE,
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.pk}): CREATE_POST_TEMPLATE,
            reverse(POST_CREATE_URL_NAME): CREATE_POST_TEMPLATE,
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_page_correct_template(self):
        """URL-адрес использует шаблон posts/create_post.html."""
        response = self.authorized_client.get(reverse(POST_CREATE_URL_NAME))
        self.assertTemplateUsed(response, CREATE_POST_TEMPLATE)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group.slug, self.group.slug)

    def test_group_page_show_correct_context(self):
        """Шаблон  group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}
            )
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group.title, self.group.title)

    def test_profile_page_show_correct_context(self):
        """Шаблон  profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.user}
            )
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)

    def test_detail_page_show_correct_context(self):
        """Шаблон  post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id}
            )
        )
        first_object = response.context['post']
        self.assertEqual(first_object.pk, ViewsTests.post.pk)

    def test_create_page_show_correct_context(self):
        """Форма create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(POST_CREATE_URL_NAME))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_create_post_appears_on_pages(self):
        post_pages = {
            reverse(INDEX_URL_NAME): self.post,
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}): self.post,
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.post.author}): self.post,
        }
        for value, expected in post_pages.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                post_page = response.context['page_obj']
                self.assertIn(expected, post_page)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='UserTest')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_slug',
            description='Тестовое описание',
        )
        list_post: list = []
        for i in range(13):
            list_post.append(Post(text=f'Тестовый текст {i}',
                                  group=cls.group,
                                  author=cls.user))
        Post.objects.bulk_create(list_post)

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse(INDEX_URL_NAME))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.guest_client.get(reverse(INDEX_URL_NAME) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_page_contains_ten_records(self):
        response = self.guest_client.get(
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_page_contains_ten_records(self):
        response = self.guest_client.get(
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.user}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)
