from django.urls import path
from . import views as v


app_name = 'tasks'
urlpatterns = [
    path('', v.AllTaskList.as_view(), name='task-list'),
    path('create/', v.CreateTaskView.as_view(), name='task-create'),
    path('<int:pk>/', v.TaskDetail.as_view(), name='task-detail'),
    path('<int:pk>/accept/', v.AcceptTaskStatusView.as_view(), name='accept-task'),
    path('<int:pk>/change/', v.ChangeTaskStatusView.as_view(), name='change-task'),
    path('<int:pk>/put-to-work/', v.put_to_work, name='put-to-work'),
    path('<int:task_id>/reject/', v.reject_task, name='reject-task'),
    path(
        '<str:status>/', v.FilterByStatusTaskView.as_view(), name='filter-task-status',
    ),
    path('file/<int:pk>/update/', v.FileUpdate.as_view(), name='update-file-comment'),
    path('<int:pk>/delete/', v.DeleteTaskView.as_view(), name='delete-task'),
]
