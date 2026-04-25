from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe, RecipeIngredient, RecipeStep, RecipeFavorite, RecipeLike, RecipeComment
from neo4j_utils import get_ingredients_by_dish, get_dishes_by_ingredient, get_dishes_by_taste,get_graph_by_dish,get_graph_overview,get_graph_by_ingredient, get_graph_by_taste,get_node_detail,get_dish_full_detail
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET,require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
import re
from collections import Counter
from django.db.models import Q
from users.models import BrowseHistory
import random

def hello(request):
    return HttpResponse("这是我的第一个接口")

def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipe/recipe_list.html', {'recipes': recipes})

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(request, 'recipe/recipe_detail.html', {'recipe': recipe})

def search_recipe(request):
    keyword = request.GET.get('keyword', '')
    recipes = Recipe.objects.filter(name__icontains=keyword)

    return render(request, 'recipe/search_result.html', {
        'keyword': keyword,
        'recipes': recipes
    })

def add_recipe(request):
    error_message = ''
    form_data = {
        'name': '',
        'ingredients': '',
        'steps': '',
        'cooking_time': ''
    }

    if request.method == 'POST':
        form_data['name'] = request.POST.get('name', '')
        form_data['ingredients'] = request.POST.get('ingredients', '')
        form_data['steps'] = request.POST.get('steps', '')
        form_data['cooking_time'] = request.POST.get('cooking_time', '')

        if not form_data['name'] or not form_data['ingredients'] or not form_data['steps'] or not form_data['cooking_time']:
            error_message = '提交失败：所有字段都不能为空！'
        else:
            Recipe.objects.create(
                name=form_data['name'],
                ingredients=form_data['ingredients'],
                steps=form_data['steps'],
                cooking_time=form_data['cooking_time']
            )
            return redirect('/recipes/')

    return render(request, 'recipe/add_recipe.html', {
        'error_message': error_message,
        'form_data': form_data
    })

def neo4j_dish_ingredients(request):
    dish_name = request.GET.get('name', '')
    results = []

    if dish_name:
        results = get_ingredients_by_dish(dish_name)

    return render(request, 'recipe/neo4j_dish_ingredients.html', {
        'dish_name': dish_name,
        'results': results
    })

def neo4j_ingredient_dishes(request):
    ingredient_name = request.GET.get('name', '')
    results = []

    if ingredient_name:
        results = get_dishes_by_ingredient(ingredient_name)

    return render(request, 'recipe/neo4j_ingredient_dishes.html', {
        'ingredient_name': ingredient_name,
        'results': results
    })

def neo4j_taste_dishes(request):
    taste_name = request.GET.get('name', '')
    results = []

    if taste_name:
        results = get_dishes_by_taste(taste_name)

    return render(request, 'recipe/neo4j_taste_dishes.html', {
        'taste_name': taste_name,
        'results': results
    })

def api_dish_ingredients(request):
    dish_name = request.GET.get('name', '').strip()

    if not dish_name:
        return JsonResponse({
            'success': False,
            'message': '请提供菜名参数 name'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    results = get_ingredients_by_dish(dish_name)

    ingredients = []
    for item in results:
        ingredients.append({
            'ingredient': item['ingredient'],
            'relation': item['relation']
        })

    return JsonResponse({
        'success': True,
        'dish_name': dish_name,
        'ingredients': ingredients
    }, json_dumps_params={'ensure_ascii': False})

def api_ingredient_dishes(request):
    ingredient_name = request.GET.get('name', '').strip()

    if not ingredient_name:
        return JsonResponse({
            'success': False,
            'message': '请提供食材参数 name'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    results = get_dishes_by_ingredient(ingredient_name)

    dishes = []
    for item in results:
        dishes.append({
            'dish_name': item['dish_name'],
            'relation': item['relation']
        })

    return JsonResponse({
        'success': True,
        'ingredient_name': ingredient_name,
        'dishes': dishes
    }, json_dumps_params={'ensure_ascii': False})

def api_taste_dishes(request):
    taste_name = request.GET.get('name', '').strip()

    if not taste_name:
        return JsonResponse({
            'success': False,
            'message': '请提供口味参数 name'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    results = get_dishes_by_taste(taste_name)

    dishes = []
    for item in results:
        dishes.append({
            'dish_name': item['dish_name']
        })

    return JsonResponse({
        'success': True,
        'taste_name': taste_name,
        'dishes': dishes
    }, json_dumps_params={'ensure_ascii': False})

def api_graph_by_dish(request):
    dish_name = request.GET.get('name', '').strip()

    if not dish_name:
        return JsonResponse({
            'success': False,
            'message': '请提供菜名参数 name'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    graph_data = get_graph_by_dish(dish_name)

    return JsonResponse({
        'success': True,
        'dish_name': dish_name,
        'nodes': graph_data['nodes'],
        'links': graph_data['links']
    }, json_dumps_params={'ensure_ascii': False})

def api_graph_overview(request):
    graph_data = get_graph_overview()

    return JsonResponse({
        'success': True,
        'nodes': graph_data['nodes'],
        'links': graph_data['links']
    }, json_dumps_params={'ensure_ascii': False})

def api_qa(request):
    question = request.GET.get('question', '').strip()

    if not question:
        return JsonResponse({
            'success': False,
            'message': '请提供问题参数 question'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    normalized_question = question.replace('？', '').replace('?', '').strip()

    def extract_minutes(text):
        match = re.search(r'(\d+)\s*分钟', text)
        if match:
            return int(match.group(1))
        if '半小时' in text:
            return 30
        if '一小时' in text or '1小时' in text:
            return 60
        return None

    def parse_cook_time_to_minutes(cook_time_text):
        if not cook_time_text:
            return None

        text = str(cook_time_text).strip()

        match = re.search(r'(\d+)\s*分钟', text)
        if match:
            return int(match.group(1))

        match = re.search(r'(\d+)\s*小时', text)
        if match:
            return int(match.group(1)) * 60

        if '半小时' in text:
            return 30

        return None

    def extract_difficulty(text):
        if '简单' in text or '新手' in text or '容易' in text:
            return '简单'
        if '中等' in text:
            return '中等'
        if '较难' in text or '困难' in text:
            return '较难'
        return None

    def extract_category(text):
        category_keywords = [
            '家常菜', '川菜', '粤菜', '鲁菜', '苏菜',
            '浙菜', '湘菜', '闽菜', '徽菜', '西餐'
        ]
        for item in category_keywords:
            if item in text:
                return item
        return None

    def build_recipe_answer(recipes, prefix_text, qa_type, entity='', category=''):
        recipe_names = [item.title for item in recipes if item.title and item.title.strip()]
        return JsonResponse({
            'success': True,
            'question': question,
            'type': qa_type,
            'entity': entity,
            'category': category,
            'answer': f"{prefix_text}：{'、'.join(recipe_names)}" if recipe_names else f"没有查询到符合条件的菜品",
            'data': recipe_names
        }, json_dumps_params={'ensure_ascii': False})

    # -----------------------------
    # 规则 1：菜品查食材
    # -----------------------------
    if '食材' in normalized_question or '材料' in normalized_question:
        for keyword in ['需要什么食材', '有哪些食材', '需要哪些材料', '有哪些材料']:
            if keyword in normalized_question:
                entity = normalized_question.replace(keyword, '').strip()
                results = get_ingredients_by_dish(entity)
                answer_items = [item['ingredient'] for item in results]

                return JsonResponse({
                    'success': True,
                    'question': question,
                    'type': 'dish_ingredients',
                    'entity': entity,
                    'category': '',
                    'answer': f"{entity} 的食材有：{'、'.join(answer_items)}" if answer_items else f"没有查询到 {entity} 的食材信息",
                    'data': answer_items
                }, json_dumps_params={'ensure_ascii': False})

    # -----------------------------
    # 规则 2：时间 / 难度 / 菜系 组合筛选
    # -----------------------------
    has_time_query = ('分钟' in normalized_question or '半小时' in normalized_question or '小时' in normalized_question)
    has_difficulty_query = any(word in normalized_question for word in ['简单', '中等', '较难', '新手', '容易', '困难'])
    has_category_query = extract_category(normalized_question) is not None
    has_recipe_query = any(
        word in normalized_question
        for word in ['什么菜', '哪些菜', '有哪些', '有啥菜', '推荐', '做什么菜', '做哪些菜']
    )

    if has_recipe_query and (has_time_query or has_difficulty_query or has_category_query):
        limit_minutes = extract_minutes(normalized_question)
        difficulty_value = extract_difficulty(normalized_question)
        category_value = extract_category(normalized_question)

        recipes = Recipe.objects.filter(review_status='approved')

        if category_value:
            recipes = recipes.filter(category=category_value)

        if difficulty_value:
            recipes = recipes.filter(difficulty=difficulty_value)

        filtered_recipes = []
        for recipe in recipes:
            if limit_minutes is not None:
                recipe_minutes = parse_cook_time_to_minutes(recipe.cook_time)
                if recipe_minutes is None or recipe_minutes > limit_minutes:
                    continue
            filtered_recipes.append(recipe)

        if limit_minutes is not None and difficulty_value and category_value:
            return build_recipe_answer(
                filtered_recipes,
                f"{category_value}中{limit_minutes}分钟内的{difficulty_value}菜有",
                'category_time_difficulty_dishes',
                f"{category_value} {limit_minutes}分钟 {difficulty_value}",
                category_value
            )

        if limit_minutes is not None and difficulty_value:
            return build_recipe_answer(
                filtered_recipes,
                f"{limit_minutes}分钟内的{difficulty_value}菜有",
                'time_difficulty_dishes',
                f"{limit_minutes}分钟 {difficulty_value}",
                ''
            )

        if category_value and difficulty_value:
            return build_recipe_answer(
                filtered_recipes,
                f"{category_value}中的{difficulty_value}菜有",
                'category_difficulty_dishes',
                f"{category_value} {difficulty_value}",
                category_value
            )

        if category_value and limit_minutes is not None:
            return build_recipe_answer(
                filtered_recipes,
                f"{category_value}中{limit_minutes}分钟内能做的菜有",
                'category_time_dishes',
                f"{category_value} {limit_minutes}分钟",
                category_value
            )

        if limit_minutes is not None:
            return build_recipe_answer(
                filtered_recipes,
                f"{limit_minutes}分钟内能做的菜有",
                'time_dishes',
                f"{limit_minutes}分钟",
                ''
            )

        if difficulty_value:
            return build_recipe_answer(
                filtered_recipes,
                f"{difficulty_value}的菜有",
                'difficulty_dishes',
                difficulty_value,
                ''
            )

        if category_value:
            return build_recipe_answer(
                filtered_recipes,
                f"{category_value}对应的菜有",
                'category_dishes',
                category_value,
                category_value
            )

    # -----------------------------
    # 规则 3：食材查菜品
    # -----------------------------
    if '可以做什么菜' in normalized_question or '能做什么菜' in normalized_question or '能做哪些菜' in normalized_question:
        entity = normalized_question
        for keyword in ['可以做什么菜', '能做什么菜', '能做哪些菜']:
            entity = entity.replace(keyword, '')
        entity = entity.strip()

        results = get_dishes_by_ingredient(entity)
        answer_items = [item['dish_name'] for item in results]

        return JsonResponse({
            'success': True,
            'question': question,
            'type': 'ingredient_dishes',
            'entity': entity,
            'category': '',
            'answer': f"{entity} 可以做的菜有：{'、'.join(answer_items)}" if answer_items else f"没有查询到使用 {entity} 的菜品",
            'data': answer_items
        }, json_dumps_params={'ensure_ascii': False})

    # -----------------------------
    # 规则 4：口味查菜品
    # -----------------------------
    if '有哪些菜' in normalized_question or normalized_question.endswith('有哪些'):
        entity = normalized_question.replace('有哪些菜', '').replace('有哪些', '').strip()

        results = get_dishes_by_taste(entity)
        answer_items = [item['dish_name'] for item in results]

        return JsonResponse({
            'success': True,
            'question': question,
            'type': 'taste_dishes',
            'entity': entity,
            'category': '',
            'answer': f"{entity} 对应的菜有：{'、'.join(answer_items)}" if answer_items else f"没有查询到 {entity} 对应的菜品",
            'data': answer_items
        }, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({
        'success': False,
        'question': question,
        'message': '暂时无法识别该问题，请尝试提问：某道菜有哪些食材、某种食材能做什么菜、某种口味有哪些菜、20分钟内能做什么菜、简单的家常菜有哪些'
    }, json_dumps_params={'ensure_ascii': False})

def api_graph_by_ingredient(request):
    ingredient_name = request.GET.get('name', '').strip()

    if not ingredient_name:
        return JsonResponse({
            'success': False,
            'message': '请提供食材参数 name'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    graph_data = get_graph_by_ingredient(ingredient_name)

    return JsonResponse({
        'success': True,
        'ingredient_name': ingredient_name,
        'nodes': graph_data['nodes'],
        'links': graph_data['links']
    }, json_dumps_params={'ensure_ascii': False})

def api_graph_by_taste(request):
    taste_name = request.GET.get('name', '').strip()

    if not taste_name:
        return JsonResponse({
            'success': False,
            'message': '请提供口味参数 name'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    graph_data = get_graph_by_taste(taste_name)

    return JsonResponse({
        'success': True,
        'taste_name': taste_name,
        'nodes': graph_data['nodes'],
        'links': graph_data['links']
    }, json_dumps_params={'ensure_ascii': False})

def api_node_detail(request):
    node_type = request.GET.get('type', '').strip()
    name = request.GET.get('name', '').strip()

    if not node_type or not name:
        return JsonResponse({
            'success': False,
            'message': '缺少参数'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    if node_type == 'Dish':
        recipe = Recipe.objects.filter(title=name, review_status='approved').first()

        if recipe:
            detail = {
                'type': 'Dish',
                'name': recipe.title,
                'difficulty': recipe.difficulty or '',
                'cook_time': recipe.cook_time or '',
                'category': recipe.category or '',
                'recipe_id': recipe.id,
                'image': recipe.image.url if recipe.image else '',
                'items': [item.name for item in recipe.ingredients.all()]
            }
        else:
            detail = {
                'type': 'Dish',
                'name': name,
                'difficulty': '',
                'cook_time': '',
                'category': '',
                'recipe_id': None,
                'image': '',
                'items': []
            }

        return JsonResponse({
            'success': True,
            'detail': detail
        }, json_dumps_params={'ensure_ascii': False})

    elif node_type == 'Category':
        recipes = Recipe.objects.filter(category=name, review_status='approved')
        dish_names = [recipe.title for recipe in recipes if recipe.title and recipe.title.strip()]

        detail = {
            'type': 'Category',
            'name': name,
            'dish_count': len(dish_names),
            'dishes': dish_names
        }

        return JsonResponse({
            'success': True,
            'detail': detail
        }, json_dumps_params={'ensure_ascii': False})

    elif node_type == 'Ingredient':
        ingredient_rows = RecipeIngredient.objects.filter(
            name=name,
            recipe__review_status='approved'
        ).select_related('recipe')

        recipe_map = {}
        for row in ingredient_rows:
            if row.recipe_id not in recipe_map and row.recipe.title and row.recipe.title.strip():
                recipe_map[row.recipe_id] = row.recipe.title

        dish_names = list(recipe_map.values())

        detail = {
            'type': 'Ingredient',
            'name': name,
            'dish_count': len(dish_names),
            'dishes': dish_names
        }

        return JsonResponse({
            'success': True,
            'detail': detail
        }, json_dumps_params={'ensure_ascii': False})

    elif node_type in ['Method', 'Taste']:
        detail = {
            'type': node_type,
            'name': name,
            'dish_count': 0,
            'dishes': []
        }

        return JsonResponse({
            'success': True,
            'detail': detail
        }, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({
        'success': True,
        'detail': {
            'type': node_type,
            'name': name
        }
    }, json_dumps_params={'ensure_ascii': False})

def api_dish_detail(request):
    dish_name = request.GET.get('name', '').strip()

    if not dish_name:
        return JsonResponse({
            'success': False,
            'message': '请提供菜名参数 name'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    detail = get_dish_full_detail(dish_name)

    if not detail:
        return JsonResponse({
            'success': False,
            'message': '未查询到该菜品详情'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({
        'success': True,
        'detail': detail
    }, json_dumps_params={'ensure_ascii': False})

from django.views.decorators.http import require_GET

@require_GET
def api_home_recipes(request):
    recipes = Recipe.objects.all().order_by('-id')[:8]

    data = []
    for recipe in recipes:
        ingredients_preview = recipe.ingredients[:36] + '...' if len(recipe.ingredients) > 36 else recipe.ingredients
        level = '简单' if recipe.cooking_time <= 20 else '中等' if recipe.cooking_time <= 40 else '较难'
        level_class = 'easy' if recipe.cooking_time <= 20 else 'medium' if recipe.cooking_time <= 40 else 'hard'

        data.append({
            'id': recipe.id,
            'title': recipe.name,
            'desc': ingredients_preview or '暂无简介',
            'time': f'{recipe.cooking_time}分钟',
            'level': level,
            'levelClass': level_class,
            'tag': '家常菜',
            'views': 0,
            'favorites': 0,
            'comments': 0,
            'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80',
        })

    return JsonResponse({
        'success': True,
        'recipes': data
    }, json_dumps_params={'ensure_ascii': False})

@require_GET
def api_hot_recipes(request):
    recipes = Recipe.objects.all().order_by('-id')[:8]

    data = []
    for recipe in recipes:
        ingredients_preview = recipe.ingredients[:36] + '...' if len(recipe.ingredients) > 36 else recipe.ingredients
        level = '简单' if recipe.cooking_time <= 20 else '中等' if recipe.cooking_time <= 40 else '较难'
        level_class = 'easy' if recipe.cooking_time <= 20 else 'medium' if recipe.cooking_time <= 40 else 'hard'

        data.append({
            'id': recipe.id,
            'title': recipe.name,
            'desc': ingredients_preview or '暂无简介',
            'time': f'{recipe.cooking_time}分钟',
            'level': level,
            'levelClass': level_class,
            'tag': '热门',
            'views': 0,
            'favorites': 0,
            'comments': 0,
            'image': 'https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=80',
        })

    return JsonResponse({
        'success': True,
        'recipes': data
    }, json_dumps_params={'ensure_ascii': False})

from django.views.decorators.http import require_GET
from .models import Recipe


@require_GET
def api_recommend_recipes_db(request):
    recipes = Recipe.objects.filter(
        is_recommended=True,
        review_status='approved'
    ).order_by('-created_at')[:4]

    data = []
    for item in recipes:
        data.append({
            'id': item.id,
            'title': item.title,
            'desc': item.description,
            'time': item.cook_time,
            'level': item.difficulty,
            'tag': item.category,
            'views': item.views,
            'favorites': item.favorites,
            'comments': 0,
            'image': item.image.url if item.image else '',
        })

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


@require_GET
def api_recipe_detail_db(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id, review_status='approved')
    except Recipe.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '菜谱不存在'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    recipe.views += 1
    recipe.save(update_fields=['views'])

    ingredients = []
    for ingredient in recipe.ingredients.all():
        ingredients.append({
            'name': ingredient.name,
            'amount': ingredient.amount,
            'unit': ingredient.unit,
        })

    steps = []
    for step in recipe.steps.all().order_by('step_no'):
        steps.append({
            'content': step.content,
            'time': step.time_text,
        })

    is_favorited = False
    is_liked = False

    if request.user.is_authenticated:
        is_favorited = RecipeFavorite.objects.filter(user=request.user, recipe=recipe).exists()
        is_liked = RecipeLike.objects.filter(user=request.user, recipe=recipe).exists()

    data = {
        'id': recipe.id,
        'title': recipe.title,
        'desc': recipe.description,
        'time': recipe.cook_time,
        'level': recipe.difficulty,
        'tag': recipe.category,
        'views': recipe.views,
        'favorites': recipe.favorites,
        'likes': recipe.likes,
        'image': recipe.image.url if recipe.image else '',
        'ingredients': ingredients,
        'steps': steps,
        'servings': recipe.servings,
        'is_favorited': is_favorited,
        'is_liked': is_liked,
    }

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

@require_GET
def api_recipe_list_db(request):
    recipes = Recipe.objects.filter(review_status='approved').order_by('-created_at')

    data = []
    for item in recipes:
        data.append({
            'id': item.id,
            'title': item.title,
            'desc': item.description,
            'time': item.cook_time,
            'level': item.difficulty,
            'tag': item.category,
            'views': item.views,
            'favorites': item.favorites,
            'comments': 0,
            'image': item.image.url if item.image else '',
        })

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

def api_graph_by_category(request):
    category_name = request.GET.get('name', '').strip()
    if not category_name:
        return JsonResponse({
            'success': False,
            'message': '请输入菜系名称'
        }, json_dumps_params={'ensure_ascii': False})

    from neo4j_utils import get_graph_by_category

    graph_data = get_graph_by_category(category_name)

    if not graph_data['nodes']:
        return JsonResponse({
            'success': False,
            'message': '未找到该菜系对应的图谱数据'
        }, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({
        'success': True,
        'category_name': category_name,
        'nodes': graph_data['nodes'],
        'links': graph_data['links'],
    }, json_dumps_params={'ensure_ascii': False})

@require_GET
def api_hot_recipes_db(request):
    recipes = Recipe.objects.filter(review_status='approved').order_by('-views', '-created_at')[:4]

    data = []
    for item in recipes:
        data.append({
            'id': item.id,
            'title': item.title,
            'desc': item.description,
            'time': item.cook_time,
            'level': item.difficulty,
            'tag': item.category,
            'views': item.views,
            'favorites': item.favorites,
            'comments': 0,
            'image': item.image.url if item.image else '',
        })

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

@require_POST
@login_required
def api_toggle_recipe_favorite(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
        recipe_id = body.get('recipe_id')
    except Exception:
        return JsonResponse({
            'success': False,
            'message': '请求参数错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '菜谱不存在'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    favorite = RecipeFavorite.objects.filter(user=request.user, recipe=recipe).first()

    if favorite:
        favorite.delete()
        recipe.favorites = RecipeFavorite.objects.filter(recipe=recipe).count()
        recipe.save(update_fields=['favorites'])

        return JsonResponse({
            'success': True,
            'action': 'unfavorite',
            'favorites': recipe.favorites,
            'message': '已取消收藏'
        }, json_dumps_params={'ensure_ascii': False})
    else:
        RecipeFavorite.objects.create(user=request.user, recipe=recipe)
        recipe.favorites = RecipeFavorite.objects.filter(recipe=recipe).count()
        recipe.save(update_fields=['favorites'])

        return JsonResponse({
            'success': True,
            'action': 'favorite',
            'favorites': recipe.favorites,
            'message': '收藏成功'
        }, json_dumps_params={'ensure_ascii': False})
    
@require_POST
@login_required
def api_toggle_recipe_like(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
        recipe_id = body.get('recipe_id')
    except Exception:
        return JsonResponse({
            'success': False,
            'message': '请求参数错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '菜谱不存在'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    like = RecipeLike.objects.filter(user=request.user, recipe=recipe).first()

    if like:
        like.delete()
        recipe.likes = RecipeLike.objects.filter(recipe=recipe).count()
        recipe.save(update_fields=['likes'])

        return JsonResponse({
            'success': True,
            'action': 'unlike',
            'likes': recipe.likes,
            'message': '已取消点赞'
        }, json_dumps_params={'ensure_ascii': False})
    else:
        RecipeLike.objects.create(user=request.user, recipe=recipe)
        recipe.likes = RecipeLike.objects.filter(recipe=recipe).count()
        recipe.save(update_fields=['likes'])

        return JsonResponse({
            'success': True,
            'action': 'like',
            'likes': recipe.likes,
            'message': '点赞成功'
        }, json_dumps_params={'ensure_ascii': False})
    
@ensure_csrf_cookie
def api_csrf(request):
    return JsonResponse({
        'success': True,
        'message': 'CSRF cookie 已设置'
    }, json_dumps_params={'ensure_ascii': False})

@require_GET
def api_recipe_favorite_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401, json_dumps_params={'ensure_ascii': False})

    favorites = RecipeFavorite.objects.filter(user=request.user).select_related('recipe').order_by('-created_at')

    data = []
    for item in favorites:
        recipe = item.recipe
        data.append({
            'id': item.id,
            'recipe_id': recipe.id,
            'dish_name': recipe.title,
            'category': recipe.category,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    return JsonResponse({
        'success': True,
        'favorites': data
    }, json_dumps_params={'ensure_ascii': False})

@require_POST
def api_remove_recipe_favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401, json_dumps_params={'ensure_ascii': False})

    try:
        body = json.loads(request.body.decode('utf-8'))
        recipe_id = body.get('recipe_id')
    except Exception:
        return JsonResponse({
            'success': False,
            'message': '请求参数错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '菜谱不存在'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    favorite = RecipeFavorite.objects.filter(user=request.user, recipe=recipe).first()
    if not favorite:
        return JsonResponse({
            'success': False,
            'message': '该菜谱未收藏'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    favorite.delete()
    recipe.favorites = RecipeFavorite.objects.filter(recipe=recipe).count()
    recipe.save(update_fields=['favorites'])

    return JsonResponse({
        'success': True,
        'message': '已取消收藏',
        'favorites': recipe.favorites
    }, json_dumps_params={'ensure_ascii': False})

@require_POST
def api_submit_recipe(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401, json_dumps_params={'ensure_ascii': False})

    try:
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '').strip()
        difficulty = request.POST.get('difficulty', '').strip()
        cook_time = request.POST.get('cook_time', '').strip()
        servings = request.POST.get('servings', '2人份').strip()

        ingredients_json = request.POST.get('ingredients_json', '[]')
        steps_json = request.POST.get('steps_json', '[]')

        ingredients = json.loads(ingredients_json)
        steps = json.loads(steps_json)
        image = request.FILES.get('image')
    except Exception:
        return JsonResponse({
            'success': False,
            'message': '提交数据格式错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    if not title:
        return JsonResponse({
            'success': False,
            'message': '菜谱名称不能为空'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    recipe = Recipe.objects.create(
        title=title,
        description=description,
        category=category,
        difficulty=difficulty,
        cook_time=cook_time,
        servings=servings,
        image=image,
        created_by=request.user,
        source='user',
        review_status='pending',
        review_comment='等待管理员审核'
    )

    for item in ingredients:
        name = str(item.get('name', '')).strip()
        amount = str(item.get('amount', '')).strip()
        unit = str(item.get('unit', '')).strip()
        if name:
            RecipeIngredient.objects.create(
                recipe=recipe,
                name=name,
                amount=amount,
                unit=unit
            )

    for index, item in enumerate(steps, start=1):
        content = str(item.get('content', '')).strip()
        time_text = str(item.get('time', '')).strip()
        if content:
            RecipeStep.objects.create(
                recipe=recipe,
                step_no=index,
                content=content,
                time_text=time_text
            )

    return JsonResponse({
        'success': True,
        'message': '菜谱提交成功，等待管理员审核'
    }, json_dumps_params={'ensure_ascii': False})

@require_GET
def api_my_recipe_submissions(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401, json_dumps_params={'ensure_ascii': False})

    recipes = Recipe.objects.filter(created_by=request.user, source='user').order_by('-created_at')

    data = []
    has_unread_rejection = False

    for recipe in recipes:
        if recipe.review_status == 'rejected' and not recipe.rejection_notice_read:
            has_unread_rejection = True

        data.append({
            'id': recipe.id,
            'title': recipe.title,
            'review_status': recipe.review_status,
            'review_comment': recipe.review_comment or '',
            'created_at': recipe.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'reviewed_at': recipe.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if recipe.reviewed_at else '',
            'can_resubmit': recipe.review_status == 'rejected',
            'rejection_notice_read': recipe.rejection_notice_read,
        })

    return JsonResponse({
        'success': True,
        'submissions': data,
        'has_unread_rejection': has_unread_rejection,
    }, json_dumps_params={'ensure_ascii': False})

@require_POST
def api_mark_submission_notifications_read(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401, json_dumps_params={'ensure_ascii': False})

    Recipe.objects.filter(
        created_by=request.user,
        source='user',
        review_status='rejected',
        rejection_notice_read=False
    ).update(rejection_notice_read=True)

    return JsonResponse({
        'success': True,
        'message': '已标记为已读'
    }, json_dumps_params={'ensure_ascii': False})

@require_GET
def api_submission_detail(request, recipe_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401, json_dumps_params={'ensure_ascii': False})

    try:
        recipe = Recipe.objects.get(id=recipe_id, created_by=request.user, source='user')
    except Recipe.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '投稿不存在'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    ingredients = []
    for item in recipe.ingredients.all():
        ingredients.append({
            'name': item.name,
            'amount': item.amount,
            'unit': item.unit,
        })

    steps = []
    for step in recipe.steps.all().order_by('step_no'):
        steps.append({
            'content': step.content,
            'time': step.time_text,
        })

    return JsonResponse({
        'success': True,
        'detail': {
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'category': recipe.category,
            'difficulty': recipe.difficulty,
            'cook_time': recipe.cook_time,
            'servings': recipe.servings,
            'image': recipe.image.url if recipe.image else '',
            'review_status': recipe.review_status,
            'review_comment': recipe.review_comment or '',
            'ingredients': ingredients,
            'steps': steps,
        }
    }, json_dumps_params={'ensure_ascii': False})

@require_POST
def api_resubmit_recipe(request, recipe_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401, json_dumps_params={'ensure_ascii': False})

    try:
        recipe = Recipe.objects.get(id=recipe_id, created_by=request.user, source='user')
    except Recipe.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '投稿不存在'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    if recipe.review_status != 'rejected':
        return JsonResponse({
            'success': False,
            'message': '当前状态不可重新提交'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    try:
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '').strip()
        difficulty = request.POST.get('difficulty', '').strip()
        cook_time = request.POST.get('cook_time', '').strip()
        servings = request.POST.get('servings', '2人份').strip()

        ingredients = json.loads(request.POST.get('ingredients_json', '[]'))
        steps = json.loads(request.POST.get('steps_json', '[]'))
        image = request.FILES.get('image')
    except Exception:
        return JsonResponse({
            'success': False,
            'message': '提交数据格式错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    if not title:
        return JsonResponse({
            'success': False,
            'message': '菜谱名称不能为空'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    recipe.title = title
    recipe.description = description
    recipe.category = category
    recipe.difficulty = difficulty
    recipe.cook_time = cook_time
    recipe.servings = servings
    recipe.review_status = 'pending'
    recipe.review_comment = '用户已修改，等待重新审核'
    recipe.reviewed_at = None
    recipe.rejection_notice_read = True

    if image:
        recipe.image = image

    recipe.save()

    recipe.ingredients.all().delete()
    for item in ingredients:
        name = str(item.get('name', '')).strip()
        amount = str(item.get('amount', '')).strip()
        unit = str(item.get('unit', '')).strip()
        if name:
            RecipeIngredient.objects.create(
                recipe=recipe,
                name=name,
                amount=amount,
                unit=unit
            )

    recipe.steps.all().delete()
    for index, item in enumerate(steps, start=1):
        content = str(item.get('content', '')).strip()
        time_text = str(item.get('time', '')).strip()
        if content:
            RecipeStep.objects.create(
                recipe=recipe,
                step_no=index,
                content=content,
                time_text=time_text
            )

    return JsonResponse({
        'success': True,
        'message': '已重新提交审核'
    }, json_dumps_params={'ensure_ascii': False})

@require_http_methods(["GET"])
def api_recipe_comments(request, recipe_id):
    recipe = Recipe.objects.filter(id=recipe_id).first()
    if not recipe:
        return JsonResponse({
            'success': False,
            'message': '菜谱不存在'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    parent_comments = RecipeComment.objects.filter(
        recipe=recipe,
        parent__isnull=True,
        is_deleted=False
    ).select_related('user')

    comment_list = []
    for comment in parent_comments:
        replies = comment.replies.filter(is_deleted=False).select_related('user')

        comment_list.append({
            'id': comment.id,
            'username': comment.user.username,
            'user_id': comment.user.id,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'can_delete': request.user.is_authenticated and (
                request.user == comment.user or request.user.is_staff
            ),
            'replies': [
                {
                    'id': reply.id,
                    'username': reply.user.username,
                    'user_id': reply.user.id,
                    'content': reply.content,
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'can_delete': request.user.is_authenticated and (
                        request.user == reply.user or request.user.is_staff
                    ),
                }
                for reply in replies
            ]
        })

    return JsonResponse({
        'success': True,
        'comments': comment_list
    }, json_dumps_params={'ensure_ascii': False})

@require_http_methods(["POST"])
@login_required
def api_add_recipe_comment(request, recipe_id):
    recipe = Recipe.objects.filter(id=recipe_id).first()
    if not recipe:
        return JsonResponse({
            'success': False,
            'message': '菜谱不存在'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    content = (data.get('content') or '').strip()
    parent_id = data.get('parent_id')

    if not content:
        return JsonResponse({
            'success': False,
            'message': '评论内容不能为空'
        }, status=400, json_dumps_params={'ensure_ascii': False})

    parent_comment = None
    if parent_id:
        parent_comment = RecipeComment.objects.filter(
            id=parent_id,
            recipe=recipe,
            is_deleted=False
        ).first()
        if not parent_comment:
            return JsonResponse({
                'success': False,
                'message': '父评论不存在'
            }, status=404, json_dumps_params={'ensure_ascii': False})

    comment = RecipeComment.objects.create(
        recipe=recipe,
        user=request.user,
        content=content,
        parent=parent_comment
    )

    return JsonResponse({
        'success': True,
        'message': '评论发表成功',
        'comment_id': comment.id
    }, json_dumps_params={'ensure_ascii': False})

@require_http_methods(["POST"])
@login_required
def api_delete_recipe_comment(request, comment_id):
    comment = RecipeComment.objects.filter(id=comment_id, is_deleted=False).first()
    if not comment:
        return JsonResponse({
            'success': False,
            'message': '评论不存在'
        }, status=404, json_dumps_params={'ensure_ascii': False})

    if request.user != comment.user and not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': '无权限删除该评论'
        }, status=403, json_dumps_params={'ensure_ascii': False})

    comment.is_deleted = True
    comment.save()

    return JsonResponse({
        'success': True,
        'message': '评论删除成功'
    }, json_dumps_params={'ensure_ascii': False})

@require_GET
@login_required
def api_weekly_recommend_recipes(request):
    user = request.user
    refresh = request.GET.get('refresh', '')

    day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    # 1. 获取用户收藏、点赞、浏览记录
    favorite_recipe_ids = list(
        RecipeFavorite.objects.filter(user=user).values_list('recipe_id', flat=True)
    )

    liked_recipe_ids = list(
        RecipeLike.objects.filter(user=user).values_list('recipe_id', flat=True)
    )

    history_dish_names = list(
        BrowseHistory.objects.filter(user=user)
        .values_list('dish_name', flat=True)[:80]
    )

    # 2. 找出用户产生过行为的菜谱
    interacted_recipes = Recipe.objects.filter(
        Q(id__in=favorite_recipe_ids) |
        Q(id__in=liked_recipe_ids) |
        Q(title__in=history_dish_names)
    ).prefetch_related('ingredients')

    # 3. 统计用户偏好的菜系、食材、难度
    category_counter = Counter()
    ingredient_counter = Counter()
    difficulty_counter = Counter()

    interacted_ids = set()

    for recipe in interacted_recipes:
        interacted_ids.add(recipe.id)

        if recipe.category:
            category_counter[recipe.category] += 3

        if recipe.difficulty:
            difficulty_counter[recipe.difficulty] += 2

        for ingredient in recipe.ingredients.all():
            if ingredient.name:
                ingredient_counter[ingredient.name] += 1

    for recipe_id in favorite_recipe_ids:
        interacted_ids.add(recipe_id)

    for recipe_id in liked_recipe_ids:
        interacted_ids.add(recipe_id)

    # 4. 获取候选菜谱：优先推荐未浏览/未点赞/未收藏过的审核通过菜谱
    candidate_recipes = Recipe.objects.filter(
        review_status='approved'
    ).exclude(
        id__in=interacted_ids
    ).prefetch_related('ingredients')

    scored_recipes = []

    for recipe in candidate_recipes:
        score = 0

        # 系统推荐菜加分
        if recipe.is_recommended:
            score += 5

        # 浏览热度加分
        score += min(recipe.views or 0, 100) * 0.05

        # 点赞、收藏加分
        score += (recipe.likes or 0) * 0.5
        score += (recipe.favorites or 0) * 0.8

        # 菜系偏好加分
        if recipe.category:
            score += category_counter.get(recipe.category, 0) * 4

        # 难度偏好加分
        if recipe.difficulty:
            score += difficulty_counter.get(recipe.difficulty, 0) * 2

        # 食材偏好加分
        for ingredient in recipe.ingredients.all():
            score += ingredient_counter.get(ingredient.name, 0) * 2

        # 点击“换一组推荐”时加入随机扰动，避免每次结果完全一样
        if refresh:
            score += random.uniform(0, 8)

        scored_recipes.append((score, recipe))

    # 5. 按分数排序
    scored_recipes.sort(key=lambda x: x[0], reverse=True)

    # 6. 先从前 14 个候选中选 7 个
    top_candidates = [item[1] for item in scored_recipes[:14]]

    if refresh and len(top_candidates) > 7:
        recommended_recipes = random.sample(top_candidates, 7)
    else:
        recommended_recipes = top_candidates[:7]

    # 7. 如果个性化候选不足 7 个，用热门菜谱补足
    if len(recommended_recipes) < 7:
        existing_ids = [recipe.id for recipe in recommended_recipes]

        fallback_recipes = list(
            Recipe.objects.filter(
                review_status='approved'
            ).exclude(
                id__in=existing_ids
            ).order_by('-is_recommended', '-views', '-favorites', '-likes')[:20]
        )

        if refresh and len(fallback_recipes) > 7:
            random.shuffle(fallback_recipes)

        needed_count = 7 - len(recommended_recipes)
        recommended_recipes.extend(fallback_recipes[:needed_count])

    # 8. 如果还是不足 7 个，说明数据库审核通过菜谱本身太少
    weekly_menu = []

    for index, recipe in enumerate(recommended_recipes[:7]):
        weekly_menu.append({
            'day': day_names[index],
            'id': recipe.id,
            'title': recipe.title,
            'category': recipe.category or '',
            'difficulty': recipe.difficulty or '',
            'cook_time': recipe.cook_time or '',
            'description': recipe.description or '',
            'image': recipe.image.url if recipe.image else '',
            'reason': build_recommend_reason(
                recipe,
                category_counter,
                ingredient_counter,
                difficulty_counter
            ),
        })

    return JsonResponse({
        'success': True,
        'message': '一周推荐菜谱生成成功',
        'weekly_menu': weekly_menu
    }, json_dumps_params={'ensure_ascii': False})


def build_recommend_reason(recipe, category_counter, ingredient_counter, difficulty_counter):
    reasons = []

    if recipe.category and category_counter.get(recipe.category, 0) > 0:
        reasons.append(f'你近期偏好{recipe.category}')

    if recipe.difficulty and difficulty_counter.get(recipe.difficulty, 0) > 0:
        reasons.append(f'符合你常看的{recipe.difficulty}难度')

    matched_ingredients = []
    for ingredient in recipe.ingredients.all():
        if ingredient_counter.get(ingredient.name, 0) > 0:
            matched_ingredients.append(ingredient.name)

    if matched_ingredients:
        reasons.append(f'包含你常关注的食材：{"、".join(matched_ingredients[:2])}')

    if recipe.is_recommended:
        reasons.append('系统推荐菜品')

    if recipe.views and recipe.views > 0:
        reasons.append('近期浏览热度较高')

    if recipe.favorites and recipe.favorites > 0:
        reasons.append('收藏热度较高')

    if recipe.likes and recipe.likes > 0:
        reasons.append('点赞热度较高')

    if not reasons:
        reasons.append('根据热门菜谱为你推荐')

    return '；'.join(reasons)


def build_recommend_reason(recipe, category_counter, ingredient_counter, difficulty_counter):
    reasons = []

    if getattr(recipe, 'category', '') and category_counter.get(recipe.category, 0) > 0:
        reasons.append(f'你近期偏好{recipe.category}')

    if getattr(recipe, 'difficulty', '') and difficulty_counter.get(recipe.difficulty, 0) > 0:
        reasons.append(f'符合你常看的{recipe.difficulty}难度')

    matched_ingredients = []
    for ingredient in recipe.ingredients.all():
        if ingredient_counter.get(ingredient.name, 0) > 0:
            matched_ingredients.append(ingredient.name)

    if matched_ingredients:
        reasons.append(f'包含你常关注的食材：{"、".join(matched_ingredients[:2])}')

    if getattr(recipe, 'is_recommended', False):
        reasons.append('系统推荐菜品')

    if getattr(recipe, 'views', 0):
        reasons.append('近期浏览热度较高')

    if getattr(recipe, 'favorites', 0):
        reasons.append('收藏热度较高')

    if getattr(recipe, 'likes', 0):
        reasons.append('点赞热度较高')

    if not reasons:
        reasons.append('根据热门菜谱为你推荐')

    return '；'.join(reasons)