from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Task, TaskStatus
from .forms import TaskForm
import json


# 기본 사용자 가져오기 (없으면 생성)
def get_default_user():
    if User.objects.filter(username="admin").exists():
        return User.objects.get(username="admin")
    else:
        return User.objects.create_superuser("admin", "admin@example.com", "admin123")


def kanban_board(request):
    # 상태별로 업무 가져오기
    todo_tasks = Task.objects.filter(status=TaskStatus.TODO)
    in_progress_tasks = Task.objects.filter(status=TaskStatus.IN_PROGRESS)
    done_tasks = Task.objects.filter(status=TaskStatus.DONE)

    form = TaskForm()

    context = {
        "todo_tasks": todo_tasks,
        "in_progress_tasks": in_progress_tasks,
        "done_tasks": done_tasks,
        "form": form,
    }
    return render(request, "task/kanban_board.html", context)


def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = get_default_user()  # 기본 사용자로 설정

            # 담당자가 지정되지 않았으면 기본 사용자로 설정
            if not task.assigned_to:
                task.assigned_to = get_default_user()

            task.save()
            return redirect("kanban_board")
    else:
        form = TaskForm()

    return render(request, "task/task_form.html", {"form": form})


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # AJAX 요청인 경우 JSON 반환
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "status": task.status,
            "status_display": task.get_status_display(),
            "priority": task.priority,
            "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
            "assigned_to": task.assigned_to.username if task.assigned_to else None,
            "created_at": task.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": task.updated_at.strftime("%Y-%m-%d %H:%M"),
            "created_by": task.created_by.username if task.created_by else None,
        }
        return JsonResponse(data)

    # 일반 요청인 경우 템플릿 반환
    return render(request, "task/task_detail.html", {"task": task})


def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("kanban_board")
    else:
        form = TaskForm(instance=task)

    return render(request, "task/task_form.html", {"form": form, "task": task})


def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        task.delete()
        return redirect("kanban_board")

    return render(request, "task/task_confirm_delete.html", {"task": task})


@require_POST
def update_task_status(request):
    data = json.loads(request.body)
    task_id = data.get("task_id")
    new_status = data.get("status")

    task = get_object_or_404(Task, pk=task_id)

    # 유효한 상태값인지 확인
    if new_status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE]:
        task.status = new_status
        task.save()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "유효하지 않은 상태값입니다."})
