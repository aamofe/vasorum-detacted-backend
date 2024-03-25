import json
from datetime import datetime, timedelta
import pprint

from django.http import JsonResponse
from django.shortcuts import render
import jwt

from backend import settings
from user.authentication import validate_all, validate_login
from user.models import User


# Create your views here.

@validate_all
def register(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    json_data = json.loads(request.body.decode('utf-8'))
    username=json_data.get('username')
    doctor_id=json_data.get('doctor_id')
    password=json_data.get('password')
    if not username or not doctor_id or not password:
        return JsonResponse({'errno': 1, 'msg': "未传入用户名、医生ID或密码"})
    try:
        user=User.objects.get(doctor_id=doctor_id)

        return JsonResponse({'errno': 1, 'msg': "用户已注册"})
    except User.DoesNotExist:
        user=User.objects.create(
            doctor_id=doctor_id,
            username=username,
            password=password
        )
        return JsonResponse({'errno': 0, 'msg': "用户注册成功"})


@validate_all
def login(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))

        # 从 JSON 数据中获取 doctor_id 和 password
        doctor_id = json_data.get('doctor_id')
        password = json_data.get('password')
        if not doctor_id or not password:
            return JsonResponse({'errno': 1, 'msg': "未传入医生ID或密码"})
        try:
            user = User.objects.get(doctor_id=doctor_id, password=password)
        except User.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "用户不存在！"})
        payload = {'exp': datetime.utcnow() + timedelta(days=5), 'id': user.id}
        encode = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        token = str(encode)
        user_info=user.to_dict()
        user_info['token']=token
        user.is_new=False
        user.save()
        return JsonResponse({ 'user_info':user_info, 'errno': 0, 'msg': "登录成功"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})

@validate_login
def logout(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    request.session.flush()
    return JsonResponse({'errno': 0, 'msg': "登出成功"})


@validate_login
def get_info(request):
    if request.method != 'GET':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    user=request.user
    print("userId : ",user.id)
    user_info=user.to_dict()
    pprint.pprint(user_info)
    return JsonResponse({ 'user_info':user_info, 'errno': 0, 'msg': "登录成功"})

@validate_login
def upload_avatar(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})
    avatar=request.FILES.get('avatar')
    user=request.user
    if avatar:
        user.avatar=avatar
        user.save()
        print(user.avatar.name)
        return JsonResponse({'errno': 0,'user_info':user.to_dict(), 'msg': "头像上传成功"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请上传正确头像"})