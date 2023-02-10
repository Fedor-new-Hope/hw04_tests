from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
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
