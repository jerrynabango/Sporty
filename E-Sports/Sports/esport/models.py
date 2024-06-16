from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# Create your models here.
class CustomUser(AbstractUser):
    """
    Custom User model for account management.
    """
    account_picture = models.ImageField(upload_to='pictures/',
                                        blank=True, null=True,
                                        default='account.png')

    bio = models.TextField(blank=True)

    class Meta:
        # Add any custom meta options for your model here
        pass

    def __str__(self):
        return self.username


# Add related_name arguments to resolve clashes
CustomUser.groups.field.remote_field.related_name = 'customuser_groups'
CustomUser.user_permissions.field.remote_field.related_name = 'customuser_permissions'

# Fixing clashes for auth.User model
CustomUser.groups.field.remote_field.related_query_name = 'customuser_groups'
CustomUser.user_permissions.field.remote_field.related_query_name = 'customuser_permissions'


class Post(models.Model):
    """
    Model representing a post.
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='liked_posts', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                      related_name='disliked_posts',
                                      blank=True)
    CATEGORY_CHOICES = [
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('tennis', 'Tennis'),
        ('volleyball', 'Volleyball'),
        ('baseball', 'Baseball'),
        ('golf', 'Golf'),
        ('cycling', 'Cycling'),
        ('cricket', 'Cricket'),
        ('formula 1', 'Formula 1'),
        ('boxing', 'Boxing'),
        ('rugby', 'Rugby'),
        ('hockey', 'Hockey'),
    ]
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES,
                                default='football')

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Model representing a comment on a post.
    """
    post = models.ForeignKey('Post', on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='liked_comments',
                                   blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                      related_name='disliked_comments',
                                      blank=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
