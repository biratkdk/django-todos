from datetime import timedelta

from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .forms import TodoForm
from .models import Todo


def get_showing_todos(request, todos):
    search_query = request.GET.get('q', '').strip()
    active_filter = request.GET.get('filter', 'all')
    today = timezone.localdate()
    due_soon_cutoff = today + timedelta(days=7)

    if search_query:
        todos = todos.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    if active_filter == 'complete':
        todos = todos.filter(is_completed=True)
    elif active_filter == 'incomplete':
        todos = todos.filter(is_completed=False)
    elif active_filter == 'overdue':
        todos = todos.filter(is_completed=False, due_date__lt=today)
    elif active_filter == 'due-soon':
        todos = todos.filter(
            is_completed=False,
            due_date__gte=today,
            due_date__lte=due_soon_cutoff,
        )
    elif active_filter == 'high-priority':
        todos = todos.filter(is_completed=False, priority=Todo.Priority.HIGH)

    return todos, active_filter, search_query


@login_required
def index(request):
    todos = (
        Todo.objects.filter(owner=request.user)
        .order_by('is_completed', 'due_date', '-created_at')
    )
    today = timezone.localdate()
    due_soon_cutoff = today + timedelta(days=7)

    completed_count = todos.filter(is_completed=True).count()
    incomplete_count = todos.filter(is_completed=False).count()
    all_count = todos.count()
    overdue_count = todos.filter(is_completed=False, due_date__lt=today).count()
    due_soon_count = todos.filter(
        is_completed=False,
        due_date__gte=today,
        due_date__lte=due_soon_cutoff,
    ).count()
    high_priority_count = todos.filter(
        is_completed=False,
        priority=Todo.Priority.HIGH,
    ).count()

    showing_todos, active_filter, search_query = get_showing_todos(request, todos)

    context = {
        'todos': showing_todos,
        'all_count': all_count,
        'completed_count': completed_count,
        'incomplete_count': incomplete_count,
        'overdue_count': overdue_count,
        'due_soon_count': due_soon_count,
        'high_priority_count': high_priority_count,
        'active_filter': active_filter,
        'search_query': search_query,
    }
    return render(request, 'todo/index.html', context)


@login_required
def create_todo(request):
    form = TodoForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            todo = form.save(commit=False)
            todo.owner = request.user
            todo.save()

            messages.add_message(request, messages.SUCCESS, "Todo created successfully")
            return redirect("todo", id=todo.pk)

        messages.add_message(request, messages.ERROR, "Please correct the errors below.")
        return render(request, 'todo/create-todo.html', {'form': form}, status=400)

    return render(request, 'todo/create-todo.html', {'form': form})


@login_required
def todo_detail(request, id):
    todo = get_object_or_404(Todo, pk=id, owner=request.user)
    context = {'todo': todo}
    return render(request, 'todo/todo-detail.html', context)


@login_required
def todo_delete(request, id):
    todo = get_object_or_404(Todo, pk=id, owner=request.user)
    context = {'todo': todo}

    if request.method == 'POST':
        todo.delete()
        messages.add_message(request, messages.SUCCESS, "Todo deleted successfully")
        return redirect('home')

    return render(request, 'todo/todo-delete.html', context)


@login_required
def todo_edit(request, id):
    todo = get_object_or_404(Todo, pk=id, owner=request.user)
    form = TodoForm(request.POST or None, instance=todo)
    context = {'todo': todo, 'form': form}

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Todo updated successfully")
            return redirect("todo", id=todo.pk)

        messages.add_message(request, messages.ERROR, "Please correct the errors below.")
        return render(request, 'todo/todo-edit.html', context, status=400)

    return render(request, 'todo/todo-edit.html', context)
