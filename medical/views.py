import json
import os
import uuid
from django.db.models import Q,Max
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from backend import settings

from medical.models import Patient, CT, Photo, Segmentation, Segmentation
from user.authentication import validate_login, validate_all


#患者 增删查改
@validate_login 
def add_patient(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    json_data = json.loads(request.body.decode('utf-8'))
    name =json_data.get("name")
    gender=json_data.get("gender")
    doctor=request.user
    patient=Patient.objects.create(
        name=name,
        gender=gender,
        doctor=doctor
    )
    return JsonResponse({'errno': 0,"patient_info":patient.to_dict(), 'msg': "创建患者成功"})


@validate_login
def delete_patient(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    json_data = json.loads(request.body.decode('utf-8'))
    patient_id=json_data.get("patient_id")
    try:
        patient = Patient.objects.get(id=patient_id)
        patient.delete()
        return JsonResponse({'errno': 0, 'msg': f"患者 {patient_id} 删除成功"})
    except Patient.DoesNotExist:
        return JsonResponse({'errno': 1, 'msg': f"患者 {patient_id} 不存在"})
    except Exception as e:
        return JsonResponse({'errno': 1, 'msg': f"删除患者时发生错误: {str(e)}"})


@validate_login
def get_patient(request):
    if request.method != 'GET':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    patient_id=request.GET.get("patient_id")
    try:
        patient = Patient.objects.get(id=patient_id)
        return JsonResponse({'errno': 0, 'patient_info': patient.to_dict(), 'msg': "获取患者信息成功"})
    except Patient.DoesNotExist:
        return JsonResponse({'errno': 1, 'msg': f"患者 {patient_id} 不存在"})
    except Exception as e:
        return JsonResponse({'errno': 1, 'msg': f"获取患者信息时发生错误: {str(e)}"})

@validate_login
def get_all_patient(request):
    if request.method != 'GET':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    patients1 = Patient.objects.all()
    for patient in patients1:
        if not patient.latest_ct:
            latest_ct = CT.objects.filter(patient=patient).aggregate(latest_ct=Max('created_at'))['latest_ct']
            patient.latest_ct = latest_ct
            patient.save()
            pass
    
    patients = Patient.objects.all().order_by('-latest_ct')
    patient_list=[]
    #查看对应病人
    for p in patients:
        patient_list.append(p.to_dict())
    doctor=request.user
    my_patients = Patient.objects.filter(docter=doctor).order_by('-latest_ct')
    my_patient_list=[]
    #查看对应病人
    for p in my_patients:
        my_patient_list.append(p.to_dict())
    return JsonResponse({'errno': 0,'patient_list':patient_list,'my_patient_list':my_patient_list, 'msg': "获取所有患者成功"})

@validate_login
def update_patient(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    json_data = json.loads(request.body.decode('utf-8'))
    patient_id=json_data.get("patient_id")
    try:
        patient = Patient.objects.get(id=patient_id)
        name = json_data.get("name")
        patient.name = name
        patient.save()
        return JsonResponse({'errno': 0, 'patient_info': patient.to_dict(), 'msg': "患者信息更新成功"})
    except Patient.DoesNotExist:
        return JsonResponse({'errno': 1, 'msg': f"患者 {patient_id} 不存在"})
    except Exception as e:
        return JsonResponse({'errno': 2, 'msg': f"更新患者信息时发生错误: {str(e)}"})




@validate_login
def upload(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    ct_id=request.POST.get("ct_id")
    if ct_id is None:
        patient_id = request.POST.get("patient_id")
        if not patient_id:
            return JsonResponse({'errno': 1, 'msg': "患者ID"})
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            patient = Patient.objects.create(name=None)
        ct = CT.objects.create(
            patient=patient,
            created_at=now()
        )
    else :
        try:
            ct=CT.objects.get(id=ct_id)
        except CT.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "CT不存在"})
    
    
    src_files = request.FILES.getlist('src_file')
    dst_files = request.FILES.getlist('dst_file')
    if not src_files:
        return JsonResponse({'errno': 1, 'msg': "未传入ct图片"})
    if not dst_files:
        return JsonResponse({'errno': 1, 'msg': "未传入处理后图片"})
    src_list = []
    src_base = f'http://101.42.32.89/media/'
    for file in src_files:
        photo = Photo.objects.create(
            ct=ct,
            img=file,
            path='src'
        )
        src_list.append(src_base + photo.img.name)
    dst_list = []
    dst_base = f'http://101.42.32.89/media/'
     # 这里需要重新处理
    for file in dst_files:
        photo = Photo.objects.create(
            ct=ct,
            img=file,
            path='dst'
        )
        dst_list.append(dst_base + photo.img.name)
    ct.src_list = src_list
    ct.dst_list = dst_list
    ct.save()

    return JsonResponse({'errno': 0,
                         "src_list":src_list,
                         "dst_list":dst_list,
                          'msg': "CT上传成功"})


@validate_login
def upload_seg(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    src_files = request.FILES.getlist('src_file')#小图
    ct_id =request.POST.get("ct_id")
    if  src_files:
        src_base = f'http://101.42.32.89/media/'
        for file in src_files:
            file_name = file.name
            ct = CT.objects.get(id=ct_id)
            photo_name = file_name.split('-')[4]
            photo = Photo.objects.get(
                Q(img__contains=photo_name) | Q(img__contains=photo_name.replace('.jpg', '.png')),
                ct=ct,
                path="dst"
            )
            seg=Segmentation.objects.create(
                photo=photo,
                img=file,
                path='src'
            )
            if photo.seg_src is None:
                photo.seg_src=[]
            photo.seg_src.append(src_base + seg.img.name)
            photo.save()
    dst_files = request.FILES.getlist('dst_file')#小图
    if dst_files:
        dst_base = f'http://101.42.32.89/media/'
        for file in dst_files:
            file_name = file.name

            ct = CT.objects.get(id=ct_id)
            photo_name = file_name.split('-')[4]
            photo = Photo.objects.get(
                Q(img__contains=photo_name) | Q(img__contains=photo_name.replace('.png', '.jpg')),
                ct=ct,
                path="dst"
            )
            seg=Segmentation.objects.create(
                photo=photo,
                img=file,
                path='dst'
            )
            if photo.seg_dst is None:
                photo.seg_dst=[]
            photo.seg_dst.append(dst_base + seg.img.name)
            photo.save()
    return JsonResponse({'errno': 0,'msg': "分割图上传成功"})

# 查看指定ct
@validate_login
def get_ct(request):
    
    if request.method != 'GET':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    patient_id=request.GET.get("patient_id")
    if not patient_id:
        return JsonResponse({'errno': 1, 'msg': "患者ID"})
    try:
        patient=Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({'errno': 1, 'msg': "患者不存在"})
    if "case_id" in request.GET:
        case_id=request.GET.get("case_id")
    else :
        case_id=None
    if case_id is None or case_id=='':
        ct = CT.objects.filter(patient=patient).order_by('-created_at').first()
    else:
        ct=CT.objects.get(id=case_id)
    if ct is None:
        return JsonResponse({'errno': 1, 'msg': "CT不存在"})
    if ct.src_list is None:
        srcPath=f"./media/{ct.id}/src"
        src_base = f'http://101.42.32.89/media/{ct.id}/src/'
        src_list=[]
        for file_name in os.listdir(srcPath):
            src_list.append(src_base + file_name)
        ct.src_list=src_list
        ct.save()
    photos=Photo.objects.filter(ct=ct,path="dst")
    dst_list=[]
    for photo in photos:
        # print(photo.img.name)
        map={}
        path=f'http://101.42.32.89/media/'+photo.img.name
        map['path']=path
        
        # segs=Segmentation.objects.filter(photo=photo,path="src")
        # seg_src=[]
        # for seg in segs:
        #     seg_path=f'http://101.42.32.89/media/'+seg.img.name
        #     # print(seg_path)
        #     seg_src.append(seg_path)
        map['seg_src']=photo.seg_src

        # segs=Segmentation.objects.filter(photo=photo,path="dst")
        # seg_dst=[]
        # for seg in segs:
        #     seg_path=f'http://101.42.32.89/media/'+seg.img.name
        #     # print(seg_path)
        #     seg_dst.append(seg_path)
        map['seg_dst']=photo.seg_dst

        dst_list.append(map)

    return JsonResponse({'errno': 0,
                         "src_list": ct.src_list,
                         "dst_list": dst_list,
                         "diagnosis":ct.diagnosis,
                         "comment":ct.comment,
                         'msg': "获取最近ct成功"})
@validate_login
def get_case(request):
    if request.method != 'GET':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    patient_id=request.GET.get("patient_id")
    if patient_id is None or patient_id=='':
        return JsonResponse({'errno': 1, 'msg': "未传入患者ID"})
    try:
        patient=Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({'errno': 1, 'msg': "患者不存在"})
    cts = CT.objects.filter(patient=patient).order_by('-created_at')
    cases=[]
    for ct in cts:
        cover_url=ct.src_list[0]
        ct_dict=ct.to_dict()
        ct_dict["cover_url"]=cover_url
        cases.append(ct_dict)
    return JsonResponse({'errno': 0,'cases':cases, 'msg': "获取所有ct成功"})

#获取/修改 诊断结果

@validate_login
def update_diagnosis(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    ct_id=request.POST.get('ct_id')
    diagnosis=request.POST.get('diagnosis')
    try:
        ct=CT.objects.get(id=ct_id)
    except CT.DoesNotExist:
        return JsonResponse({'errno': 1, 'msg': "CT不存在"})
    ct.diagnosis=diagnosis
    ct.save()
    return JsonResponse({'errno': 0, 'msg': "修改成功"})
@validate_login
def update_comment(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    ct_id=request.POST.get('ct_id')
    comment=request.POST.get('comment')
    try:
        ct=CT.objects.get(id=ct_id)
    except CT.DoesNotExist:
        return JsonResponse({'errno': 1, 'msg': "CT不存在"})
    ct.comment=comment
    ct.save()
    return JsonResponse({'errno': 0, 'msg': "修改成功"})

@validate_login
def get_diagnosis(request):
    if request.method != 'GET':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    ct_id=request.GET.get('ct_id')
    try:
        ct=CT.objects.get(id=ct_id)
    except CT.DoesNotExist:
        return JsonResponse({'errno': 1, 'msg': "CT不存在"})
    
    return JsonResponse({'errno': 0,'ct_info':ct.to_dict(), 'msg': "修改成功"})

def annotate(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'errno': 1, 'msg': "JSON 解析错误"})
    url = data.get('url')
    img_name=url.replace("http://101.42.32.89/media/","")
    # print("img_name:",img_name)
    idx=data.get('idx')
    try:
        seg=Segmentation.objects.get(img__contains=img_name)
    except Segmentation.DoesNotExist:
        return JsonResponse({'errno': 1, 'msg': "小图不存在"})
    # 找到图片名字
    
    url=f'http://101.42.32.89/media/'+seg.img.name #dst/dst
    # url=url.replace("dst/dst","dst/annotate")
    if idx==1:
        url=url.replace("dst/src","dst/annotate/first")
    else:
        url=url.replace("dst/src","dst/annotate/second")
    # print(url)
    return JsonResponse({'errno': 0,"url":url, 'msg': "标注成功"})
# 标注
# def annotate(request):
#     if request.method != 'POST':
#         return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
#     try:
#         data = json.loads(request.body.decode('utf-8'))
#     except json.JSONDecodeError:
#         return JsonResponse({'errno': 1, 'msg': "JSON 解析错误"})
#     seg_id = data.get('seg_id')
#     try:
#         seg=Segmentation.objects.get(id=seg_id)
#     except Segmentation.DoesNotExist:
#         return JsonResponse({'errno': 1, 'msg': "小图不存在"})
#     # 找到图片名字
#     seg=Segmentation.objects.get(id=seg_id)
#     img_name=seg.img.name
#     photo_name = img_name.split("/")[3]
#     arr = {}
#     points = data.get('data')
#     seg.point_list=points
#     seg.save()
#     point_coords = []
#     value = {}
#     boxes = []  
#     point_labels = []  
#     for point in points:
#         x = point.get('x')
#         y = point.get('y')
#         point_coords.append([x, y])  
#         point_labels.append(point.get('point_labels'))  
#     value["boxes"] = boxes
#     value["point_coords"] = point_coords
#     value["point_labels"] = point_labels
#     arr[photo_name] = value

#     #发给模型，然后生成一张图片，
#     return JsonResponse({'errno': 0,"arr":arr, 'msg': "标注成功"})
#展示所有标注

@validate_login
def get_point_list(request):
    if request.method != 'GET':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    seg_url=request.GET.get("seg_url")
    seg_name = seg_url.replace("http://101.42.32.89/media/", "")
    seg=Segmentation.objects.get(img__name=seg_name)
    return JsonResponse({'errno': 0,"point_list":seg.point_list, 'msg': "标注成功"})

def update(request):
    photos=Photo.objects.all()
    for photo in photos:
        src_list=photo.seg_src
        new_src=[]
        if src_list is None:
            continue
        for s in src_list:
            new_s=s.replace("jpg","png")
            new_src.append(new_s)
        photo.seg_src=new_src
        photo.save()
    return JsonResponse({'errno': 0, 'msg': "修改成功"})    