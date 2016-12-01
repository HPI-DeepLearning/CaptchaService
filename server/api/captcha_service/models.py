from django.db import models
from picklefield.fields import PickledObjectField
from encrypted_fields import EncryptedCharField

class CaptchaToken(models.Model):
    file = models.ImageField(upload_to='captchas')
    # counter object that counts user proposals
    # to this captcha. If captcha is solved None is saved.
    proposals = PickledObjectField()
    resolved = models.BooleanField(default=False)
    result = EncryptedCharField(max_length=256)

class CaptchaSession(models.Model):
    session_key = models.CharField(primary_key=True, unique=True, max_length=256)
    solved_captcha_id = models.ForeignKey(
        CaptchaToken,
        on_delete=models.PROTECT,
        limit_choices_to={'resolved': True},
        related_name='solved'
    )
    unsolved_captcha_id = models.ForeignKey(
        CaptchaToken,
        on_delete=models.PROTECT,
        limit_choices_to={'resolved': False},
        related_name='unsolved'
    )
    order = models.BooleanField()# 0 -> solved unsolved 1 -> unsolved solved
    origin = models.CharField(max_length=128) # ip address
