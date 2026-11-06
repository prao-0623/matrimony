from django.db import migrations, models


def rename_published_status(apps, schema_editor):
    Profile = apps.get_model('profiles', 'Profile')
    Profile.objects.filter(status='PUBLISHED').update(status='APPROVED')


def restore_published_status(apps, schema_editor):
    Profile = apps.get_model('profiles', 'Profile')
    Profile.objects.filter(status='APPROVED').update(status='PUBLISHED')


class Migration(migrations.Migration):
    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(rename_published_status, restore_published_status),
        migrations.AlterField(
            model_name='profile',
            name='status',
            field=models.CharField(
                choices=[
                    ('DRAFT', 'Draft'),
                    ('PENDING_REVIEW', 'Pending Review'),
                    ('APPROVED', 'Approved'),
                    ('REJECTED', 'Rejected'),
                    ('ARCHIVED', 'Archived'),
                ],
                default='DRAFT',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(
                blank=True,
                choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                max_length=20,
            ),
        ),
    ]