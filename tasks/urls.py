from django.urls import path
from . import views as v


app_name = 'tasks'
urlpatterns = [
    path('', v.AllTaskList.as_view(), name='task-list'),
    path('create/', v.CreateTaskView.as_view(), name='task-create'),
    path('<int:pk>/', v.TaskDetail.as_view(), name='task-detail'),
    path('<int:pk>/accept/', v.accept_task_status, name='accept-task'),
    path('<int:pk>/change-status/', v.change_task_status, name='change-task-status'),
    path('<int:pk>/put-to-work/', v.put_to_work, name='put-to-work'),
    path('<int:task_id>/reject/', v.reject_task, name='reject-task'),
    path(
        '<str:status>/', v.FilterByStatusTaskView.as_view(), name='filter-task-status',
    ),
    path('<int:pk>/accept-from-rejected/', v.accept_from_rejected, name='accept-from-rejected'),
    path('file/<int:pk>/update/', v.FileUpdate.as_view(), name='update-file-comment'),
    path('<int:pk>/delete/', v.DeleteTaskView.as_view(), name='delete-task'),
    path('<int:pk>/change/', v.change_task_view, name='change-task'),
    path('<int:pk>/delete-file/', v.delete_file, name='delete-file'),
]
