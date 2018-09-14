# Generated by Django 2.1.1 on 2018-09-14 05:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personality.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Personality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('slug', models.SlugField(max_length=128, unique=True)),
            ],
            options={
                'verbose_name_plural': 'personalities',
            },
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote_text', models.CharField(max_length=255)),
                ('action', models.CharField(choices=[('action', '/me'), ('say', 'say')], default='say', max_length=10)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('last_used', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personality.Category')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='personality',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personality.Personality'),
        ),
        migrations.AlterUniqueTogether(
            name='quote',
            unique_together={('quote_text', 'category')},
        ),
        migrations.AlterUniqueTogether(
            name='keyword',
            unique_together={('name', 'category')},
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('name', 'personality')},
        ),
    ]
