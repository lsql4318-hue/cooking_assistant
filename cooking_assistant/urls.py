from django.contrib import admin
from django.urls import path, include
from recipe.views import hello, recipe_list, recipe_detail, search_recipe, add_recipe, neo4j_dish_ingredients, neo4j_ingredient_dishes, neo4j_taste_dishes, api_dish_ingredients, api_ingredient_dishes, api_taste_dishes, api_graph_by_dish, api_graph_overview, api_qa, api_graph_by_ingredient, api_graph_by_category, api_node_detail, api_dish_detail, api_home_recipes, api_hot_recipes, api_csrf
from users.views import register_view, login_view, logout_view, api_register, api_login, api_logout, api_user_info,api_add_history, api_history_list
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', hello),
    path('recipes/', recipe_list),
    path('recipe/<int:recipe_id>/', recipe_detail),
    path('search/', search_recipe),
    path('add_recipe/', add_recipe),
    path('neo4j_dish_ingredients/', neo4j_dish_ingredients),
    path('neo4j_ingredient_dishes/', neo4j_ingredient_dishes),
    path('neo4j_taste_dishes/', neo4j_taste_dishes),
    path('register/', register_view),
    path('login/', login_view),
    path('logout/', logout_view),
    path('api/dish-ingredients/', api_dish_ingredients),
    path('api/ingredient-dishes/', api_ingredient_dishes),
    path('api/taste-dishes/', api_taste_dishes),
    path('api/register/', api_register),
    path('api/login/', api_login),
    path('api/logout/', api_logout),
    path('api/csrf/', api_csrf),
    path('api/user-info/', api_user_info),
    path('api/home-recipes/', api_home_recipes),
    path('api/hot-recipes/', api_hot_recipes),
    path('api/graph/dish/', api_graph_by_dish),
    path('api/graph/overview/', api_graph_overview),
    path('api/qa/', api_qa),
    path('api/graph/ingredient/', api_graph_by_ingredient),
    path('api/graph/category/', api_graph_by_category),
    path('api/node-detail/', api_node_detail),
    path('api/dish-detail/', api_dish_detail),
    path('api/history/add/', api_add_history),
    path('api/history/', api_history_list),
    path('api/', include('recipe.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)