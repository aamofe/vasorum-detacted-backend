import json
import os
import uuid

from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from backend import settings

from medical.models import Patient, CT, Photo
from user.authentication import validate_login, validate_all


#患者 增删查改
@validate_login 
def add_patient(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    json_data = json.loads(request.body.decode('utf-8'))
    name =json_data.get("name")
    patient=Patient.objects.create(
        name=name
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
    patients=Patient.objects.all()
    patient_list=[]
    for p in patients:
        patient_list.append(p.to_dict())
    return JsonResponse({'errno': 0,'patient_list':patient_list, 'msg': "获取所有患者成功"})

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


# 上传ct（并处理）
# 没有病历号，我就创建默认病历号，
@validate_login
def test(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    patient_id = request.POST.get("patient_id")
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        patient = Patient.objects.create(name=None)
    ct = CT.objects.create(
        patient=patient,
        created_at=now()
    )
    src_file = request.FILES.get('file')
    photo = Photo.objects.create(
        ct=ct,
        img=src_file,
    )
    src_base = f'http://101.42.32.89:8000/media/'
    src_path=src_base + photo.img.name
    ct.src_list=src_path
    ct.save()
    return JsonResponse({'errno': 0,'url':src_path, 'msg': "CT上传成功"})



@validate_login
def upload(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
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
    src_files = request.FILES.getlist('files')
    if not src_files:
        return JsonResponse({'errno': 1, 'msg': "未传入ct图片"})
    src_list = []
    src_base = f'http://101.42.32.89:8000/media/'
    for file in src_files:
        photo = Photo.objects.create(
            ct=ct,
            img=file,
            path='src'
        )
        src_list.append(src_base + photo.img.name)
    dst_list = []
    dst_base = f'http://101.42.32.89:8000/media/'
    dst_files = generate(src_files)  # 这里需要重新处理
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


def generate(src_files):
    

    dst_files = src_files

    return dst_files

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
    print("你好 "+case_id)
    if case_id is None or case_id=='':
        ct = CT.objects.filter(patient=patient).order_by('-created_at').first()
    else:
        ct=CT.objects.get(id=case_id)
    if ct is None:
        return JsonResponse({'errno': 1, 'msg': "CT不存在"})
    if ct.src_list is None or ct.dst_list is None:
        srcPath=f"./media/{ct.id}/src"
        src_base = f'http://101.42.32.89:8000/media/{ct.id}/src/'
        src_list=[]
        for file_name in os.listdir(srcPath):
            src_list.append(src_base + file_name)
        ct.src_list=src_list
        dstPath=f"./media/{ct.id}/dst"
        dst_base = f'http://101.42.32.89:8000/media/{ct.id}/dst/'
        dst_list=[]
        for file_name in os.listdir(dstPath):
            dst_list.append(dst_base + file_name)    
        ct.dst_list=dst_list
        ct.save()
    return JsonResponse({'errno': 0,
                         "src_list": ct.src_list,
                         "dst_list": ct.dst_list,
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
        cases.append(ct.to_dict())
    return JsonResponse({'errno': 0,'cases':cases, 'msg': "获取所有ct成功"})