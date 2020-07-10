from django.urls import path
from .views import (
    TaskDetail,
    TaskList,
    CommentDetail,
    comment_create,
    CreateTaskView,
)


app_name = 'tasks'
urlpatterns = [
    path('', TaskList.as_view(), name='task-list'),
    path('create/', CreateTaskView.as_view(), name='task-create'),
    path('<pk>/', TaskDetail.as_view(), name='task-detail'),
    path('comments/create/<int:task>/', comment_create, name='comment-create',),
    path(
        'comments/reply/<int:task>/<int:parent>/', comment_create, name='comment-reply',
    ),
    path('comments/<pk>/', CommentDetail.as_view(), name='comment-detail'),
]
