from django.contrib import admin
from django.utils import timezone
from .models import Recipe, RecipeIngredient, RecipeStep, RecipeFavorite, RecipeLike, RecipeComment


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1


@admin.action(description='审核通过所选菜谱')
def approve_recipes(modeladmin, request, queryset):
    for obj in queryset:
        obj.review_status = 'approved'
        obj.review_comment = '审核通过'
        obj.reviewed_at = timezone.now()
        obj.rejection_notice_read = True
        obj.save()


@admin.action(description='驳回所选菜谱')
def reject_recipes(modeladmin, request, queryset):
    for obj in queryset:
        obj.review_status = 'rejected'
        obj.review_comment = obj.review_comment or '审核未通过，请修改后重新提交'
        obj.reviewed_at = timezone.now()
        obj.rejection_notice_read = False
        obj.save()



@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'category', 'difficulty', 'cook_time',
        'source', 'created_by', 'review_status', 'views'
    )
    list_filter = ('category', 'difficulty', 'source', 'review_status')
    search_fields = ('title', 'description')
    inlines = [RecipeIngredientInline, RecipeStepInline]
    actions = [approve_recipes, reject_recipes]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'name', 'amount', 'unit')


@admin.register(RecipeStep)
class RecipeStepAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'step_no', 'time_text')


@admin.register(RecipeFavorite)
class RecipeFavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', 'created_at')


@admin.register(RecipeLike)
class RecipeLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', 'created_at')

@admin.register(RecipeComment)
class RecipeCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user', 'parent', 'short_content', 'created_at', 'is_deleted')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('content', 'user__username', 'recipe__title')

    def short_content(self, obj):
        return obj.content[:30]
    short_content.short_description = '评论内容'