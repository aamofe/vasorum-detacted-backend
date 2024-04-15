import os
from uuid import uuid4

from django.db import models
import pytz

from user.models import User
shanghai_tz = pytz.timezone('Asia/Shanghai')
# Create your models here.

'''
一个病人 对应 多个ct，一个ct对应照片路径

上传 n
'''


class Patient(models.Model):
    name=models.CharField(verbose_name="姓名",max_length=20,null=True)
    docter=models.ForeignKey(User,on_delete=models.CASCADE,related_name="patients",null=True)
    gender=models.CharField(verbose_name="性别",max_length=10,default="男")
    #1.性别，
    #新增对应医生字段
    #排序=最新ct的时间
    latest_ct=models.DateTimeField(verbose_name="最近一次ct的时间",null=True)
    def to_dict(self):
        if self.latest_ct :
            latest_ct_shanghai = (self.latest_ct.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            latest_ct_shanghai= None
        if self.gender=="男":
            avatar_url="http://101.42.32.89/media/avatar/male.png"
        else:
            avatar_url="http://101.42.32.89/media/avatar/female.png"
        return{
            "name":self.name,
            "patient_id":self.id,
            "avatar_url":avatar_url,
            "latest_ct":latest_ct_shanghai,
            "gender":self.gender
        }
#新增诊断结果
class CT(models.Model):
    patient=models.ForeignKey(Patient,on_delete=models.CASCADE,related_name="cts")
    # path=models.URLField(verbose_name="所有ct路径")
    src_list=models.JSONField(verbose_name="处理前图片路径",null=True)
    dst_list=models.JSONField(verbose_name="处理后图片路径",null=True)
    created_at=models.DateTimeField(verbose_name="创建时间")
    diagnosis=models.TextField(verbose_name="诊断结果",null=True)
    comment=models.TextField(verbose_name="诊断结果",null=True)
    #2.备注 诊断结果
    model_url=models.URLField(verbose_name="模型路径",null=True)
    def to_dict(self):
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return {
            "id":self.id,
            "date":created_at_shanghai,
            "diagnosis":self.diagnosis,
            "model_url":self.model_url
        }


def photo_upload_to(instance,filename):
    # extension = filename.split('.')[-1]
    # unique_filename = f'{uuid4()}.{extension}'
    ct_id = instance.ct.id
    path=instance.path
    return f'{ct_id}/{path}/{filename}'

class Photo(models.Model):#大图 切割图的组织  dst/src dst/dst 右1左2
    ct=models.ForeignKey(CT,on_delete=models.CASCADE,related_name="切片")
    img=models.ImageField(upload_to=photo_upload_to)
    path=models.CharField(verbose_name="上传路径",max_length=20,default="src")
    seg_src=models.JSONField(verbose_name="切割图路径",null=True)
    seg_dst=models.JSONField(verbose_name="处理后的切割图路径",null=True)
    #标注 存储

def seg_upload_to(instance,filename):
    # extension = filename.split('.')[-1]
    # unique_filename = f'{uuid4()}.{extension}'
    ct_id = instance.photo.ct.id
    path=instance.path
    return f'{ct_id}/dst/{path}/{filename}'

class Segmentation(models.Model):#这是切割图
    photo=models.ForeignKey(Photo,on_delete=models.CASCADE,related_name="切割图")
    img=models.ImageField(upload_to=seg_upload_to)
    path=models.CharField(verbose_name="上传路径",max_length=20,default="src")
    point_list=models.JSONField(verbose_name="标记点列表",null=True)

#标注表 坐标 历史记录 +-
#python manage.py makemigration
#python manage.py migrate
