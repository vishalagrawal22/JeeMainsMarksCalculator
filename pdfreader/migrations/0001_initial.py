# Generated by Django 3.0.5 on 2020-04-06 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MCQQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('QuestionId', models.CharField(max_length=30)),
                ('AnswerId', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='SAQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('QuestionId', models.CharField(max_length=30)),
                ('Answer', models.CharField(max_length=30)),
            ],
        ),
    ]
