import os
from uuid import uuid4

from django.db import models
import pytz
shanghai_tz = pytz.timezone('Asia/Shanghai')
# Create your models here.

'''
一个病人 对应 多个ct，一个ct对应照片路径

上传 n
'''


class Patient(models.Model):
    name=models.CharField(verbose_name="姓名",max_length=20,null=True)

    def to_dict(self):
        return{
            "name":self.name,
            "patient_id":self.id
        }
class CT(models.Model):
    patient=models.ForeignKey(Patient,on_delete=models.CASCADE,related_name="cts")
    # path=models.URLField(verbose_name="所有ct路径")
    src_list=models.JSONField(verbose_name="处理前图片路径",null=True)
    dst_list=models.JSONField(verbose_name="处理后图片路径",null=True)
    created_at=models.DateTimeField(verbose_name="创建时间")

    def to_dict(self):
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return {
            "id":self.id,
            "date":created_at_shanghai
        }


def photo_upload_to(instance,filename):
    # extension = filename.split('.')[-1]
    # unique_filename = f'{uuid4()}.{extension}'
    ct_id = instance.ct.id
    path=instance.path
    return f'{ct_id}/{path}/{filename}'

class Photo(models.Model):
    ct=models.ForeignKey(CT,on_delete=models.CASCADE,related_name="切片")
    img=models.ImageField(upload_to=photo_upload_to)
    path=models.CharField(verbose_name="上传路径",max_length=20,default="src")