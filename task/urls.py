from django.urls import path
from . import views

urlpatterns = [
    path("", views.kanban_board, name="kanban_board"),
    path("task/create/", views.task_create, name="task_create"),
    path("task/<int:pk>/", views.task_detail, name="task_detail"),
    path("task/<int:pk>/update/", views.task_update, name="task_update"),
    path("task/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("task/update-status/", views.update_task_status, name="update_task_status"),
]
