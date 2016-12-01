# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import encrypted_fields.fields
import django.db.models.deletion
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CaptchaSession',
            fields=[
                ('session_key', models.CharField(max_length=256, unique=True, serialize=False, primary_key=True)),
                ('order', models.BooleanField()),
                ('origin', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='CaptchaToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.ImageField(upload_to=b'captchas')),
                ('proposals', picklefield.fields.PickledObjectField(editable=False)),
                ('resolved', models.BooleanField(default=False)),
                ('result', encrypted_fields.fields.EncryptedCharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='captchasession',
            name='solved_captcha_id',
            field=models.ForeignKey(related_name='solved', on_delete=django.db.models.deletion.PROTECT, to='captcha_service.CaptchaToken'),
        ),
        migrations.AddField(
            model_name='captchasession',
            name='unsolved_captcha_id',
            field=models.ForeignKey(related_name='unsolved', on_delete=django.db.models.deletion.PROTECT, to='captcha_service.CaptchaToken'),
        ),
    ]
