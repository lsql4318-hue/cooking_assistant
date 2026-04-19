from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BrowseHistory
import json

def register_view(request):
    error_message = ''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not password or not confirm_password:
            error_message = '所有字段都不能为空'
        elif password != confirm_password:
            error_message = '两次输入的密码不一致'
        elif User.objects.filter(username=username).exists():
            error_message = '用户名已存在'
        else:
            User.objects.create_user(username=username, password=password)
            return redirect('/login/')

    return render(request, 'users/register.html', {'error_message': error_message})


def login_view(request):
    error_message = ''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            error_message = '用户名和密码不能为空'
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/recipes/')
            else:
                error_message = '用户名或密码错误'

    return render(request, 'users/login.html', {'error_message': error_message})

def logout_view(request):
    logout(request)
    return redirect('/login/')

@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '只允许 POST 请求'
        }, status=405, json_dumps_params={'ensure_ascii': False})

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()

    if not username or not password or not confirm_password:
        return JsonResponse({
            'success': False,
            'message': '所有字段都不能为空'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    if password != confirm_password:
        return JsonResponse({
            'success': False,
            'message': '两次输入的密码不一致'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'success': False,
            'message': '用户名已存在'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    User.objects.create_user(username=username, password=password)

    return JsonResponse({
        'success': True,
        'message': '注册成功'
    }, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '只允许 POST 请求'
        }, status=405, json_dumps_params={'ensure_ascii': False})

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return JsonResponse({
            'success': False,
            'message': '用户名和密码不能为空'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({
            'success': False,
            'message': '用户名或密码错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    login(request, user)

    return JsonResponse({
        'success': True,
        'message': '登录成功',
        'username': user.username
    }, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def api_logout(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '只允许 POST 请求'
        }, status=405, json_dumps_params={'ensure_ascii': False})

    logout(request)

    return JsonResponse({
        'success': True,
        'message': '退出登录成功'
    }, json_dumps_params={'ensure_ascii': False})

def api_user_info(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'success': True,
            'is_authenticated': True,
            'username': request.user.username
        }, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({
            'success': True,
            'is_authenticated': False
        }, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def api_add_history(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '只允许 POST 请求'
        }, status=405, json_dumps_params={'ensure_ascii': False})

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401, json_dumps_params={'ensure_ascii': False})

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    dish_name = data.get('dish_name', '').strip()

    if not dish_name:
        return JsonResponse({
            'success': False,
            'message': '请提供 dish_name'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    BrowseHistory.objects.create(
        user=request.user,
        dish_name=dish_name
    )

    return JsonResponse({
        'success': True,
        'message': '浏览历史记录成功'
    }, json_dumps_params={'ensure_ascii': False})

def api_history_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401, json_dumps_params={'ensure_ascii': False})

    histories = BrowseHistory.objects.filter(user=request.user)[:50]

    data = []
    for item in histories:
        data.append({
            'dish_name': item.dish_name,
            'viewed_at': item.viewed_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({
        'success': True,
        'histories': data
    }, json_dumps_params={'ensure_ascii': False})