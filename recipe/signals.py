from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Recipe, RecipeIngredient
from neo4j_utils import sync_recipe_to_neo4j, remove_recipe_from_neo4j


@receiver(post_save, sender=Recipe)
def recipe_post_save_sync(sender, instance, **kwargs):
    if instance.review_status == 'approved':
        sync_recipe_to_neo4j(instance)
    else:
        remove_recipe_from_neo4j(instance.id)


@receiver(post_delete, sender=Recipe)
def recipe_post_delete_sync(sender, instance, **kwargs):
    remove_recipe_from_neo4j(instance.id)


@receiver(post_save, sender=RecipeIngredient)
def ingredient_post_save_sync(sender, instance, **kwargs):
    recipe = instance.recipe
    if recipe.review_status == 'approved':
        sync_recipe_to_neo4j(recipe)


@receiver(post_delete, sender=RecipeIngredient)
def ingredient_post_delete_sync(sender, instance, **kwargs):
    recipe = instance.recipe
    if recipe.review_status == 'approved':
        sync_recipe_to_neo4j(recipe)