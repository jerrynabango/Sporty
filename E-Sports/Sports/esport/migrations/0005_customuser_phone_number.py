# Generated by Django 5.0.3 on 2024-04-07 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esport', '0004_remove_like_post_remove_like_user_post_dislikes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]