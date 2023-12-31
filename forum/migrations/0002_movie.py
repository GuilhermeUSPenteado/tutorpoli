# Generated by Django 4.2.7 on 2023-11-25 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('release_year', models.IntegerField()),
                ('poster_url', models.URLField(null=True)),
            ],
        ),
    ]
