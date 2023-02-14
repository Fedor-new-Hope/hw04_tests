from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.forms import PostForm

from posts.tests.constants import (
    PROFILE_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
    AUTHOR_USERNAME,
    GROUP_TITLE,
    GROUP_SLUG,
    GROUP_DESCRIPTION,
    POST_TEXT,
)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group
        )
        cls.form = PostForm()

    def test_create_post(self):
        """Валидная форма создает запись"""
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse(POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            PROFILE_URL_NAME, kwargs={'username': PostCreateFormTests.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Антон, не знаю как лучше сделать, написал два варианта.
        # Вариант 1
        self.assertTrue(
            Post.objects.filter(group=PostCreateFormTests.group).exists())
        self.assertTrue(
            Post.objects.filter(author=PostCreateFormTests.user).exists())
        self.assertTrue(Post.objects.filter(text=POST_TEXT).exists())
        # Вариант 2
        self.assertTrue(self.post.text == POST_TEXT)
        self.assertTrue(self.post.author == PostCreateFormTests.user)
        self.assertTrue(self.post.group == PostCreateFormTests.group)

    def test_authorized_edit_post(self):
        """Редактирование записи создателем поста"""
        form_data = {
            'text': POST_TEXT,
            'group': self.group.pk
        }
        response = self.authorized_client.post(reverse(
            POST_EDIT_URL_NAME,
            kwargs={
                'post_id': self.post.pk
            }),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(pk=self.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.group.id, form_data['group'])
