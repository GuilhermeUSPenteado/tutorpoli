# Generated by Django 4.2.7 on 2023-11-25 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_movie'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='tempo_ativo',
        ),
        migrations.AddField(
            model_name='profile',
            name='filme',
            field=models.ManyToManyField(related_name='profiles', to='forum.movie'),
        ),
    ]
