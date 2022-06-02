from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from utils.setup_test import TestSetup
from todo.models import Todo


class TestModel(TestSetup):

    def test_should_create_atodo(self):

        user = self.create_test_user()
        self.client.force_login(user)

        todos = Todo.objects.all()

        self.assertEqual(todos.count(), 0)

        response = self.client.post(reverse('create-todo'), {
            'title': "Hello do this",
            'description': "Remember to do this"
            ,
            'priority': Todo.Priority.HIGH,
            'due_date': (timezone.localdate() + timedelta(days=3)).isoformat(),
        })

        updated_todos = Todo.objects.all()
        created_todo = updated_todos.first()

        self.assertEqual(updated_todos.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(created_todo.priority, Todo.Priority.HIGH)
        self.assertIsNotNone(created_todo.due_date)

    def test_should_not_create_invalid_todo(self):
        user = self.create_test_user()
        self.client.force_login(user)

        response = self.client.post(reverse('create-todo'), {
            'title': '   ',
            'description': '   ',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Todo.objects.count(), 0)

    def test_should_edit_owned_todo(self):
        user = self.create_test_user()
        todo = Todo.objects.create(
            owner=user,
            title="Old title",
            description="Old description",
        )

        self.client.force_login(user)
        response = self.client.post(reverse('todo-edit', kwargs={'id': todo.pk}), {
            'title': 'New title',
            'description': 'New description',
            'priority': Todo.Priority.HIGH,
            'due_date': (timezone.localdate() + timedelta(days=2)).isoformat(),
            'is_completed': 'on',
        })

        todo.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(todo.title, 'New title')
        self.assertEqual(todo.description, 'New description')
        self.assertEqual(todo.priority, Todo.Priority.HIGH)
        self.assertTrue(todo.is_completed)
        self.assertIsNotNone(todo.completed_at)

    def test_should_filter_completed_todos(self):
        user = self.create_test_user()
        self.client.force_login(user)
        Todo.objects.create(owner=user, title="Done", description="Complete", is_completed=True)
        Todo.objects.create(owner=user, title="Todo", description="Incomplete", is_completed=False)

        response = self.client.get(f"{reverse('home')}?filter=complete")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['todos'].count(), 1)
        self.assertTrue(response.context['todos'].first().is_completed)

    def test_should_filter_overdue_todos(self):
        user = self.create_test_user()
        self.client.force_login(user)
        Todo.objects.create(
            owner=user,
            title="Late report",
            description="Needs attention",
            due_date=timezone.localdate() - timedelta(days=1),
        )
        Todo.objects.create(
            owner=user,
            title="Upcoming report",
            description="Later this week",
            due_date=timezone.localdate() + timedelta(days=3),
        )

        response = self.client.get(f"{reverse('home')}?filter=overdue")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['todos'].count(), 1)
        self.assertTrue(response.context['todos'].first().is_overdue)

    def test_should_filter_todos_by_search_query(self):
        user = self.create_test_user()
        self.client.force_login(user)
        Todo.objects.create(owner=user, title="Database project", description="Work on models")
        Todo.objects.create(owner=user, title="Read chapter", description="Distributed systems notes")

        response = self.client.get(f"{reverse('home')}?q=database")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['todos'].count(), 1)
        self.assertEqual(response.context['todos'].first().title, "Database project")

    def test_should_not_view_another_users_todo(self):
        user = self.create_test_user()
        other_user = self.create_test_user_two()
        todo = Todo.objects.create(
            owner=other_user,
            title="Private task",
            description="Should not be visible",
        )

        self.client.force_login(user)
        response = self.client.get(reverse("todo", kwargs={"id": todo.pk}))

        self.assertEqual(response.status_code, 404)

    def test_should_not_delete_another_users_todo(self):
        user = self.create_test_user()
        other_user = self.create_test_user_two()
        todo = Todo.objects.create(
            owner=other_user,
            title="Private task",
            description="Should not be deletable",
        )

        self.client.force_login(user)
        response = self.client.post(reverse("todo-delete", kwargs={"id": todo.pk}))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Todo.objects.filter(pk=todo.pk).exists())
