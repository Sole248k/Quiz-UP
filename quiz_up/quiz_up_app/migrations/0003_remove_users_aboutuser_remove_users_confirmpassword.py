# Generated by Django 5.0.6 on 2024-07-02 01:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_up_app', '0002_document_question'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='aboutuser',
        ),
        migrations.RemoveField(
            model_name='users',
            name='confirmpassword',
        ),
    ]