# Generated by Django 5.1.3 on 2024-12-06 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_remove_application_category_application_categories_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
