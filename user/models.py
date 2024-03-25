import uuid
from django.db import models

# Create your models here.


def avatar_upload_to(instance,filename):
    unique_id = uuid.uuid4().hex
    ext = filename.split('.')[-1]
    # 组合新的文件名
    new_filename = f"{instance.id}_{unique_id}.{ext}"
    return f"avatar/{new_filename}"

class User(models.Model):
    doctor_id = models.CharField(max_length=10, unique=True, null=False)
    username = models.CharField(verbose_name="昵称", max_length=20)
    password = models.CharField(verbose_name="密码", max_length=20)
    avatar=models.ImageField(verbose_name="头像",null=True,upload_to=avatar_upload_to)
    def to_dict(self):
        avatar="http://101.42.32.89:8000/media/avatar/default.png"
        if self.avatar :
            avatar="http://101.42.32.89:8000/media/"+self.avatar.name
        return {
            'doctor_id': self.doctor_id,
            'username': self.username,
            'avatar':avatar
        }
