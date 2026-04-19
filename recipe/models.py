from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Recipe(models.Model):
    REVIEW_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '审核通过'),
        ('rejected', '审核驳回'),
    ]

    SOURCE_CHOICES = [
        ('admin', '管理员创建'),
        ('user', '用户投稿'),
    ]

    title = models.CharField(max_length=255, verbose_name='菜谱名称')
    description = models.TextField(blank=True, verbose_name='菜谱简介')
    image = models.ImageField(upload_to='recipes/', blank=True, null=True, verbose_name='菜谱图片')
    category = models.CharField(max_length=100, blank=True, verbose_name='菜系')
    difficulty = models.CharField(max_length=50, blank=True, verbose_name='难度')
    cook_time = models.CharField(max_length=50, blank=True, verbose_name='耗时')
    servings = models.CharField(max_length=50, default='2人份', verbose_name='份量')
    views = models.IntegerField(default=0, verbose_name='浏览量')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    favorites = models.IntegerField(default=0, verbose_name='收藏数')
    is_recommended = models.BooleanField(default=False, verbose_name='是否推荐')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    rejection_notice_read = models.BooleanField(default=True, verbose_name='驳回通知是否已读')

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_recipes',
        verbose_name='提交用户'
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='admin',
        verbose_name='来源'
    )
    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default='approved',
        verbose_name='审核状态'
    )
    review_comment = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='审核意见'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='审核时间'
    )

    def __str__(self):
        return self.title or f'菜谱#{self.id}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='所属菜谱'
    )
    name = models.CharField(max_length=100, default='', verbose_name='食材名称')
    amount = models.CharField(max_length=50, blank=True, default='', verbose_name='用量')
    unit = models.CharField(max_length=20, blank=True, default='', verbose_name='单位')

    class Meta:
        db_table = 'recipe_ingredient'
        verbose_name = '菜谱食材'
        verbose_name_plural = '菜谱食材'

    def __str__(self):
        return f'{self.recipe.title} - {self.name}'


class RecipeStep(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name='所属菜谱'
    )
    step_no = models.PositiveIntegerField(default=1, verbose_name='步骤序号')
    content = models.TextField(default='', verbose_name='步骤内容')
    time_text = models.CharField(max_length=30, blank=True, default='', verbose_name='步骤耗时')

    class Meta:
        db_table = 'recipe_step'
        verbose_name = '菜谱步骤'
        verbose_name_plural = '菜谱步骤'
        ordering = ['step_no']

    def __str__(self):
        return f'{self.recipe.title} - 步骤{self.step_no}'
    
class RecipeFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_favorites', verbose_name='用户')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='favorite_records', verbose_name='菜谱')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        verbose_name = '菜谱收藏'
        verbose_name_plural = '菜谱收藏'
        unique_together = ('user', 'recipe')


class RecipeLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_likes', verbose_name='用户')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='like_records', verbose_name='菜谱')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    class Meta:
        verbose_name = '菜谱点赞'
        verbose_name_plural = '菜谱点赞'
        unique_together = ('user', 'recipe')

class RecipeComment(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='comment_list',
        verbose_name='所属菜谱'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_comments',
        verbose_name='评论用户'
    )
    content = models.TextField(verbose_name='评论内容')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='父评论'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        ordering = ['created_at']
        verbose_name = '菜谱评论'
        verbose_name_plural = '菜谱评论'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.title[:20]}'