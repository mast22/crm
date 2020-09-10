from django.urls import path
from . import views as v


app_name = 'comments'
urlpatterns = [
    path('create/<int:task_id>/', v.comment_create, name='comment-create',),
    path('reply/<int:task_id>/<int:parent_id>/', v.comment_create, name='comment-reply',),
    path('edit/<int:pk>/', v.CommentUpdate.as_view(), name='comment-edit'),
    path('add-files/<int:pk>/', v.add_files, name='add-files'),
    path('delete-comment/<int:pk>/', v.delete_comment, name='delete-comment'),
    path('<pk>/', v.CommentDetail.as_view(), name='comment-detail'),
]
