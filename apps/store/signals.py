# from django.db.models.signals import post_migrate
# from django.dispatch import receiver
# from django.contrib.auth.models import Group, Permission
# from django.contrib.contenttypes.models import ContentType
# from .models import StoreRequest

# @receiver(post_migrate)
# def create_groups_and_permissions(sender, **kwargs):
#     if sender.name == "apps.store":
#         approver_group, created = Group.objects.get_or_create(name="Approvers")
#         permissions = [
#             "can_view_request",
#             "can_approve_request",
#             "can_delete_request"
#         ]

#         content_type = ContentType.objects.get_for_model(StoreRequest)
#         # for perm in permissions:
#         #     permission, _ = Permission.objects.get_or_create(codename=perm, name=f"Can {perm.replace('_', ' ')}", content_type=content_type)
#         #     approver_group.permissions.add(permission)
#         for codename in permissions:
#             permission, created = Permission.objects.get_or_create(codename=codename, content_type=content_type,defaults={"name": "Approvers"})
#             approver_group.permissions.add(permission)

#         print("✅ Approver group and permissions initialized successfully!")
