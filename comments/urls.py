from django.urls import path
from . import views as v


app_name = 'comments'
urlpatterns = [
    path('create/<int:task_id>/', v.comment_create, name='comment-create',),
    path('reply/<int:task_id>/<int:parent_id>/', v.comment_create, name='comment-reply',),
    path('<pk>/', v.CommentDetail.as_view(), name='comment-detail'),
]
