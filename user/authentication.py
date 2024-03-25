from django.http import JsonResponse
import jwt
from jwt.exceptions import ExpiredSignatureError,PyJWTError
from django.conf import settings
from user.models import User


# 必须是已登录状态
def validate_login(func):
    def valid_per(request, *args, **kwargs):
        token = request.META.get('HTTP_Authorization'.upper())
        if not token:
            return JsonResponse({'errno': 401, 'msg': "请登录"})
        token = token.replace('Bearer ', '')
        try:
            jwt_token = jwt.decode(token, settings.SECRET_KEY, options={'verify_signature': False})
        except ExpiredSignatureError:
            return JsonResponse({'errno': 401, 'msg': "登录已过期，请重新登录"})
        except PyJWTError:
            return JsonResponse({'errno': 401, 'msg': "用户未登录，请先登录"})
        try:
            user = User.objects.get(id=jwt_token.get('id'))
        except User.DoesNotExist:
            return JsonResponse({'errno': 401, 'msg': "用户不存在，请先注册"})
        print("用户id  :",user.id)
        request.user = user
        return func(request, *args, **kwargs)
    return valid_per


# 游客/已登录用户都可访问
def validate_all(func):
    def valid_per(request, *args, **kwargs):
        token = request.META.get('HTTP_Authorization'.upper())
        if token:
            token = token.replace('Bearer ', '')
            try:
                jwt_token = jwt.decode(token, settings.SECRET_KEY)
            except ExpiredSignatureError:
                return JsonResponse({'errno': 401, 'msg': "登录已过期，请重新登录"})
            except PyJWTError:
                return JsonResponse({'errno': 401, 'msg': "用户未登录，请先登录"})
            try:
                user = User.objects.get(id=jwt_token.get('id'))
            except User.DoesNotExist:
                return JsonResponse({'errno': 401, 'msg': "用户不存在，请先注册"})
            request.user = user
        return func(request, *args, **kwargs)
    return valid_per
