# Generated by Django 4.2.7 on 2023-11-30 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0005_alter_profile_movie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='movie',
            field=models.ManyToManyField(blank=True, to='forum.movie'),
        ),
    ]