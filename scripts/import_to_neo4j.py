import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://localhost:7688"
USERNAME = "neo4j"
PASSWORD = "12345678"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


def clear_graph():
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("已清空 Neo4j 图数据库")


def import_dishes():
    df = pd.read_csv("data/processed/cleaned_dishes.csv", encoding="utf-8-sig")

    query = """
    MERGE (d:Dish {menu_id: $menu_id})
    SET d.name = $name,
        d.rating = $rating,
        d.favorite = $favorite,
        d.views = $views,
        d.method = $method,
        d.taste = $taste,
        d.cook_time = $cook_time,
        d.difficulty = $difficulty,
        d.sugar = $sugar,
        d.fat = $fat,
        d.calories = $calories
    """

    with driver.session() as session:
        for _, row in df.iterrows():
            session.run(
                query,
                menu_id=str(row.get("menu_id", "")),
                name=str(row.get("name", "")),
                rating=str(row.get("rating", "")),
                favorite=str(row.get("favorite", "")),
                views=str(row.get("views", "")),
                method=str(row.get("method", "")),
                taste=str(row.get("taste", "")),
                cook_time=str(row.get("cook_time", "")),
                difficulty=str(row.get("difficulty", "")),
                sugar=str(row.get("sugar", "")),
                fat=str(row.get("fat", "")),
                calories=str(row.get("calories", "")),
            )

    print("Dish 节点导入完成")


def import_ingredients():
    df = pd.read_csv("data/processed/dish_ingredients.csv", encoding="utf-8-sig")

    query = """
MERGE (d:Dish {menu_id: $menu_id})
MERGE (i:Ingredient {name: $ingredient_name})
FOREACH (_ IN CASE WHEN $ingredient_type = 'MAIN' THEN [1] ELSE [] END |
    MERGE (d)-[:USES_MAIN_INGREDIENT]->(i)
)
FOREACH (_ IN CASE WHEN $ingredient_type = 'AUX' THEN [1] ELSE [] END |
    MERGE (d)-[:USES_AUX_INGREDIENT]->(i)
)
"""

    with driver.session() as session:
        for _, row in df.iterrows():
            session.run(
                query,
                menu_id=str(row.get("menu_id", "")),
                ingredient_name=str(row.get("ingredient_text", "")),
                ingredient_type=str(row.get("ingredient_type", "")),
            )

    print("Ingredient 节点和食材关系导入完成")


def import_tastes():
    df = pd.read_csv("data/processed/cleaned_dishes.csv", encoding="utf-8-sig")

    query = """
    MERGE (d:Dish {menu_id: $menu_id})
    MERGE (t:Taste {name: $taste})
    MERGE (d)-[:HAS_TASTE]->(t)
    """

    with driver.session() as session:
        for _, row in df.iterrows():
            taste = str(row.get("taste", "")).strip()
            if taste:
                session.run(
                    query,
                    menu_id=str(row.get("menu_id", "")),
                    taste=taste,
                )

    print("Taste 节点和口味关系导入完成")


def import_methods():
    df = pd.read_csv("data/processed/cleaned_dishes.csv", encoding="utf-8-sig")

    query = """
    MERGE (d:Dish {menu_id: $menu_id})
    MERGE (m:Method {name: $method})
    MERGE (d)-[:COOKED_BY]->(m)
    """

    with driver.session() as session:
        for _, row in df.iterrows():
            method = str(row.get("method", "")).strip()
            if method:
                session.run(
                    query,
                    menu_id=str(row.get("menu_id", "")),
                    method=method,
                )

    print("Method 节点和工艺关系导入完成")


def main():
    clear_graph()
    import_dishes()
    import_ingredients()
    import_tastes()
    import_methods()
    print("Neo4j 图谱数据导入全部完成")


if __name__ == "__main__":
    main()