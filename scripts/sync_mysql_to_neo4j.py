import os
import sys
from pathlib import Path
import django
from neo4j import GraphDatabase

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooking_assistant.settings')
django.setup()

from recipe.models import Recipe

URI = "bolt://localhost:7688"
USERNAME = "neo4j"
PASSWORD = "12345678"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


def clear_graph():
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("已清空 Neo4j 图数据库")


def sync_recipes_and_relations():
    recipes = Recipe.objects.prefetch_related('ingredients').all()

    with driver.session() as session:
        for recipe in recipes:
            # 1. 同步菜品节点
            session.run(
                """
                MERGE (d:Dish {recipe_id: $recipe_id})
                SET d.name = $name,
                    d.category = $category,
                    d.difficulty = $difficulty,
                    d.cook_time = $cook_time
                """,
                recipe_id=recipe.id,
                name=recipe.title or "",
                category=recipe.category or "",
                difficulty=recipe.difficulty or "",
                cook_time=recipe.cook_time or "",
            )

            # 2. 同步菜系节点 + 归属关系
            if recipe.category:
                session.run(
                    """
                    MATCH (d:Dish {recipe_id: $recipe_id})
                    MERGE (c:Category {name: $category})
                    MERGE (d)-[:BELONGS_TO]->(c)
                    """,
                    recipe_id=recipe.id,
                    category=recipe.category,
                )

            # 3. 同步食材节点 + 关系
            for ingredient in recipe.ingredients.all():
                if not ingredient.name:
                    continue

                session.run(
                    """
                    MATCH (d:Dish {recipe_id: $recipe_id})
                    MERGE (i:Ingredient {name: $ingredient_name})
                    MERGE (d)-[:USES_INGREDIENT]->(i)
                    """,
                    recipe_id=recipe.id,
                    ingredient_name=ingredient.name,
                )

    print("菜品、食材、菜系关系同步完成")


def main():
    clear_graph()
    sync_recipes_and_relations()
    driver.close()
    print("MySQL -> Neo4j 同步完成")


if __name__ == "__main__":
    main()