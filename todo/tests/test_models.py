from datetime import timedelta

from django.utils import timezone

from utils.setup_test import TestSetup
from todo.models import Todo


class TestModel(TestSetup):

    def test_should_create_user(self):
        user = self.create_test_user()
        todo = Todo(owner=user, title="Buy milk", description='get it done')
        todo.save()
        self.assertEqual(str(todo), 'Buy milk')

    def test_should_set_completed_at_for_completed_todo(self):
        user = self.create_test_user()
        todo = Todo.objects.create(
            owner=user,
            title="Ship project",
            description='Push the finished work',
            is_completed=True,
        )

        self.assertIsNotNone(todo.completed_at)

    def test_should_mark_todo_as_overdue(self):
        user = self.create_test_user()
        todo = Todo.objects.create(
            owner=user,
            title="Past due",
            description='Already late',
            due_date=timezone.localdate() - timedelta(days=1),
        )

        self.assertTrue(todo.is_overdue)
