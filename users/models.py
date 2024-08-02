from django.contrib.auth.models import AbstractUser, Group, Permission # type: ignore
from django.db import models # type: ignore
from django.utils.translation import gettext_lazy as _ # type: ignore

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
    )

    friends = models.ManyToManyField('self', symmetrical=True, blank=True)

class FriendRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )

    class Meta:
        unique_together = ('from_user', 'to_user')
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='unique_friend_request')
        ]
