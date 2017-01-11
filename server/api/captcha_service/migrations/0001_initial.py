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
                ('origin', models.CharField(max_length=128)),
                ('sessiontype', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='CaptchaToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.ImageField(upload_to=b'static/captchas/')),
                ('proposals', picklefield.fields.PickledObjectField(editable=False)),
                ('resolved', models.BooleanField(default=False)),
                ('captcha_type', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='TextCaptchaSession',
            fields=[
                ('captchasession_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='captcha_service.CaptchaSession')),
                ('order', models.BooleanField()),
            ],
            bases=('captcha_service.captchasession',),
        ),
        migrations.CreateModel(
            name='TextCaptchaToken',
            fields=[
                ('captchatoken_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='captcha_service.CaptchaToken')),
                ('result', encrypted_fields.fields.EncryptedCharField(max_length=256)),
            ],
            bases=('captcha_service.captchatoken',),
        ),
        migrations.AddField(
            model_name='textcaptchasession',
            name='solved_captcha',
            field=models.ForeignKey(related_name='solved', on_delete=django.db.models.deletion.PROTECT, to='captcha_service.TextCaptchaToken'),
        ),
        migrations.AddField(
            model_name='textcaptchasession',
            name='unsolved_captcha',
            field=models.ForeignKey(related_name='unsolved', on_delete=django.db.models.deletion.PROTECT, to='captcha_service.TextCaptchaToken'),
        ),
    ]
