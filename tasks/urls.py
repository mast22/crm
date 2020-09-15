from django.urls import path
from . import views as v


app_name = 'tasks'
urlpatterns = [
    path('', v.AllTaskList.as_view(), name='task-list'),

    # Фильтрация для менеджера

    path('create/', v.CreateTaskView.as_view(), name='task-create'),
    path('<int:pk>/', v.TaskDetail.as_view(), name='task-detail'),
    path('<int:pk>/put-to-work/<int:status_id>/', v.put_to_work, name='put-to-work'),
    path('<int:task_id>/add-files/', v.add_files, name='add-files'),
    path('file/<int:pk>/update-comment/', v.FileUpdate.as_view(), name='update-file-comment'),
    path('<int:pk>/delete/', v.DeleteTaskView.as_view(), name='delete-task'),
    path('<int:pk>/change/', v.change_task_view, name='change-task'),
    path('<int:pk>/delete-file/', v.delete_file, name='delete-file'),
    path('<int:pk>/check-actuality/', v.check_actuality, name='check-actuality'),

    # Действия со статусами
    path('<int:pk>/accept/', v.accept_task, name='accept-task'),
    path('<int:pk>/reject/', v.reject_task, name='reject-task'),
    path('<int:pk>/approve-status/', v.approve_status, name='approve-status'),
    path('<int:pk>/change-status/', v.change_status, name='change-status'),

    # Modifier может принимать любое значение. Его необходимо держать в самом низу
    path('<str:modifier>/', v.TaskStatusListView.as_view(), name='filtered-task-list'),
]
