from django.db import models
from django.core.files.base import ContentFile
from picklefield.fields import PickledObjectField
from encrypted_fields import EncryptedCharField
from collections import Counter

class CaptchaToken(models.Model):
    file = models.ImageField(upload_to='static/captchas/')
    # counter object that counts user proposals
    # to this captcha. If captcha is solved None is saved.
    proposals = PickledObjectField()
    resolved = models.BooleanField(default=False)
    result = EncryptedCharField(max_length=256)

    @classmethod
    def create(cls, file_name, file_data, resolved, result=''):
        token = cls()
        token.file.save(file_name, ContentFile(file_data))
        token.proposals = Counter()
        token.resolved = resolved
        token.result = result
        return token

    def add_proposal(self, proposal):
        self.proposals['proposal'] += 1
        self.save()

class CaptchaSession(models.Model):
    session_key = models.CharField(primary_key=True, unique=True, max_length=256)
    solved_captcha = models.ForeignKey(
        CaptchaToken,
        on_delete=models.PROTECT,
        #  limit_choices_to={'resolved': True},
        related_name='solved'
    )
    unsolved_captcha = models.ForeignKey(
        CaptchaToken,
        on_delete=models.PROTECT,
        #  limit_choices_to={'resolved': False},
        related_name='unsolved'
    )
    order = models.BooleanField()# 0 -> solved unsolved 1 -> unsolved solved
    origin = models.CharField(max_length=128) # ip address

    def update_captchas(self, first_c, second_c):
        print(first_c.id)
        self.solved_captcha_id = first_c.id
        # self.solved = first_c
        self.unsolved_captcha_id = second_c.id
        # self.unsolved = second_c
        self.save(force_update=True)
