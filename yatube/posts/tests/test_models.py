from django.test import TestCase

from ..models import Group, Post, User

from posts.tests.constants import (
    AUTHOR_USERNAME,
    GROUP_TITLE,
    GROUP_SLUG,
    GROUP_DESCRIPTION,
    POST_TEXT,
)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__.
         правильно ли отображается значение поля """
        post = PostModelTest.post
        correct_post_name = post.text[:15]
        self.assertEqual(str(post), correct_post_name)

    def test_models_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__.
          правильно ли отображается значение поля """
        title_group = PostModelTest.group
        self.assertEqual(str(title_group), title_group.title)

    def test_models_post_have_correct_verbose_name(self):
        post = PostModelTest.post
        correct_verbose_name = post._meta.get_field('author').verbose_name
        self.assertEqual(correct_verbose_name, 'Автор поста')

    def test_models_post_have_correct_help_text(self):
        post = PostModelTest.post
        correct_help_text = post._meta.get_field('group').help_text
        self.assertEqual(
            correct_help_text, 'Группа, к которой будет относиться пост')
