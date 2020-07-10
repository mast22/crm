import dramatiq

# from django.core.mail import send_mail
from django.contrib.auth import get_user_model

User = get_user_model()


@dramatiq.actor
def reply_email(user, reply_comment):
    print(user.id, reply_comment.text)
    # send_mail(subject, message, "webmaster@example.com", [customer.email])
