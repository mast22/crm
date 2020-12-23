# from django.contrib.auth.decorators import user_passes_test
# from django.core.exceptions import PermissionDenied
#
# def user_is_manager(perm, login_url=None, raise_exception=False):
#     """
#     Decorator for views that checks whether a user has a particular permission
#     enabled, redirecting to the log-in page if necessary.
#     If the raise_exception parameter is given the PermissionDenied exception
#     is raised.
#     """
#     def check_perms(user):
#         if isinstance(perm, str):
#             perms = (perm,)
#         else:
#             perms = perm
#         # First check if the user has the permission (even anon users)
#         if user.has_perms(perms):
#             return True
#         # In case the 403 handler should be called raise the exception
#         if raise_exception:
#             raise PermissionDenied
#         # As the last resort, show the login form
#         return False
#     return user_passes_test(check_perms, login_url=login_url)
