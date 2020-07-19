from django.urls import path
from . import views as v


app_name = 'tasks'
urlpatterns = [
    path('', v.AllTaskList.as_view(), name='task-list'),
    path('create/', v.CreateTaskView.as_view(), name='task-create'),
    path('<int:pk>/', v.TaskDetail.as_view(), name='task-detail'),
    # path('<int:pk>/accept/', v.AcceptTaskView, name='accept-task'),
    # path('<int:pk>/reject/', v.RejectTaskView, name='reject-task'),
    path('comments/create/<int:task>/', v.comment_create, name='comment-create',),
    path(
        'comments/reply/<int:task>/<int:parent>/',
        v.comment_create,
        name='comment-reply',
    ),
    path('comments/<pk>/', v.CommentDetail.as_view(), name='comment-detail'),
    path(
        '<str:status>/', v.FilterByStatusTaskView.as_view(), name='filter-task-status',
    ),
]
