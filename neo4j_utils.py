from neo4j import GraphDatabase

URI = "bolt://localhost:7688"
USERNAME = "neo4j"
PASSWORD = "12345678"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

INGREDIENT_RELATIONS = ['USES_MAIN_INGREDIENT', 'USES_AUX_INGREDIENT', 'USES_INGREDIENT']


def get_dish_count():
    with driver.session() as session:
        result = session.run("MATCH (d:Dish) RETURN count(d) AS count")
        record = result.single()
        return record["count"] if record else 0


def get_ingredients_by_dish(dish_name):
    query = """
    MATCH (d:Dish {name: $dish_name})-[r]->(i:Ingredient)
    WHERE type(r) IN $relations
    RETURN d.name AS dish_name, type(r) AS relation, i.name AS ingredient
    """

    with driver.session() as session:
        result = session.run(query, dish_name=dish_name, relations=INGREDIENT_RELATIONS)
        return [record.data() for record in result]


def get_dishes_by_ingredient(ingredient_name):
    query = """
    MATCH (d:Dish)-[r]->(i:Ingredient {name: $ingredient_name})
    WHERE type(r) IN $relations
    RETURN i.name AS ingredient_name, d.name AS dish_name, type(r) AS relation
    LIMIT 50
    """

    with driver.session() as session:
        result = session.run(query, ingredient_name=ingredient_name, relations=INGREDIENT_RELATIONS)
        return [record.data() for record in result]


def get_dishes_by_taste(taste_name):
    query = """
    MATCH (d:Dish)-[:HAS_TASTE]->(t:Taste {name: $taste_name})
    RETURN t.name AS taste_name, d.name AS dish_name
    LIMIT 50
    """

    with driver.session() as session:
        result = session.run(query, taste_name=taste_name)
        return [record.data() for record in result]


def get_graph_by_dish(dish_name):
    query = """
    MATCH (d:Dish {name: $dish_name})
    OPTIONAL MATCH (d)-[r1]->(i:Ingredient)
    WHERE type(r1) IN $relations
    OPTIONAL MATCH (d)-[r2:BELONGS_TO]->(c:Category)

    RETURN d.name AS dish_name,
           d.recipe_id AS dish_id,
           collect(DISTINCT {
               name: i.name,
               relation: type(r1)
           }) AS ingredients,
           collect(DISTINCT c.name) AS categories
    """

    with driver.session() as session:
        result = session.run(query, dish_name=dish_name, relations=INGREDIENT_RELATIONS)
        record = result.single()

    if not record:
        return {'nodes': [], 'links': []}

    nodes = []
    links = []
    node_ids = set()

    dish_node_id = f"dish:{record['dish_name']}"
    nodes.append({
        'id': dish_node_id,
        'name': record['dish_name'],
        'category': 'Dish'
    })
    node_ids.add(dish_node_id)

    ingredients = record.get('ingredients') or []
    for ing in ingredients:
        if not ing or not ing.get('name'):
            continue

        ingredient_node_id = f"ingredient:{ing['name']}"
        if ingredient_node_id not in node_ids:
            nodes.append({
                'id': ingredient_node_id,
                'name': ing['name'],
                'category': 'Ingredient'
            })
            node_ids.add(ingredient_node_id)

        links.append({
            'source': dish_node_id,
            'target': ingredient_node_id,
            'relation': ing.get('relation', 'USES_INGREDIENT')
        })

    categories = record.get('categories') or []
    for category_name in categories:
        if not category_name:
            continue

        category_node_id = f"category:{category_name}"
        if category_node_id not in node_ids:
            nodes.append({
                'id': category_node_id,
                'name': category_name,
                'category': 'Category'
            })
            node_ids.add(category_node_id)

        links.append({
            'source': dish_node_id,
            'target': category_node_id,
            'relation': 'BELONGS_TO'
        })

    return {
        'nodes': nodes,
        'links': links
    }


def get_graph_overview():
    query = """
    MATCH (d:Dish)
    WITH d
    LIMIT 12

    OPTIONAL MATCH (d)-[r1]->(i:Ingredient)
    WHERE type(r1) IN ['USES_MAIN_INGREDIENT', 'USES_AUX_INGREDIENT']

    OPTIONAL MATCH (d)-[r2:BELONGS_TO]->(c:Category)

    RETURN d.name AS dish_name,
           d.menu_id AS dish_id,
           collect(DISTINCT {
               name: i.name,
               relation: type(r1)
           }) AS ingredients,
           collect(DISTINCT c.name) AS categories
    """

    with driver.session() as session:
        result = session.run(query)
        records = [record.data() for record in result]

    nodes = []
    links = []
    node_ids = set()
    link_keys = set()

    for item in records:
        dish_name = item['dish_name']
        if not dish_name:
            continue

        dish_node_id = f"dish:{dish_name}"

        if dish_node_id not in node_ids:
            nodes.append({
                'id': dish_node_id,
                'name': dish_name,
                'category': 'Dish'
            })
            node_ids.add(dish_node_id)

        ingredients = item.get('ingredients') or []
        for ing in ingredients:
            if not ing or not ing.get('name'):
                continue

            ingredient_name = ing['name']
            relation = ing.get('relation', 'USES_INGREDIENT')
            ingredient_node_id = f"ingredient:{ingredient_name}"

            if ingredient_node_id not in node_ids:
                nodes.append({
                    'id': ingredient_node_id,
                    'name': ingredient_name,
                    'category': 'Ingredient'
                })
                node_ids.add(ingredient_node_id)

            link_key = (dish_node_id, ingredient_node_id, relation)
            if link_key not in link_keys:
                links.append({
                    'source': dish_node_id,
                    'target': ingredient_node_id,
                    'relation': relation
                })
                link_keys.add(link_key)

        categories = item.get('categories') or []
        for category_name in categories:
            if not category_name:
                continue

            category_node_id = f"category:{category_name}"

            if category_node_id not in node_ids:
                nodes.append({
                    'id': category_node_id,
                    'name': category_name,
                    'category': 'Category'
                })
                node_ids.add(category_node_id)

            link_key = (dish_node_id, category_node_id, 'BELONGS_TO')
            if link_key not in link_keys:
                links.append({
                    'source': dish_node_id,
                    'target': category_node_id,
                    'relation': 'BELONGS_TO'
                })
                link_keys.add(link_key)

    return {
        'nodes': nodes,
        'links': links
    }


def get_graph_by_ingredient(ingredient_name):
    query = """
    MATCH (d:Dish)-[r]->(i:Ingredient {name: $ingredient_name})
    WHERE type(r) IN $relations
    RETURN i.name AS ingredient_name,
           d.name AS dish_name,
           d.recipe_id AS dish_id,
           type(r) AS relation
    """

    with driver.session() as session:
        result = session.run(query, ingredient_name=ingredient_name, relations=INGREDIENT_RELATIONS)
        records = [record.data() for record in result]

    if not records:
        return {'nodes': [], 'links': []}

    nodes = []
    links = []
    node_ids = set()

    ingredient_node_id = f"ingredient:{records[0]['ingredient_name']}"
    if ingredient_node_id not in node_ids:
        nodes.append({
            'id': ingredient_node_id,
            'name': records[0]['ingredient_name'],
            'category': 'Ingredient'
        })
        node_ids.add(ingredient_node_id)

    for item in records:
        dish_node_id = f"dish:{item['dish_name']}"

        if dish_node_id not in node_ids:
            nodes.append({
                'id': dish_node_id,
                'name': item['dish_name'],
                'category': 'Dish'
            })
            node_ids.add(dish_node_id)

        links.append({
            'source': ingredient_node_id,
            'target': dish_node_id,
            'relation': item['relation']
        })

    return {
        'nodes': nodes,
        'links': links
    }


def get_graph_by_taste(taste_name):
    query = """
    MATCH (d:Dish)-[:HAS_TASTE]->(t:Taste {name: $taste_name})
    RETURN t.name AS taste_name,
           d.name AS dish_name,
           d.recipe_id AS dish_id
    """

    with driver.session() as session:
        result = session.run(query, taste_name=taste_name)
        records = [record.data() for record in result]

    if not records:
        return {'nodes': [], 'links': []}

    nodes = []
    links = []
    node_ids = set()

    taste_node_id = f"taste:{records[0]['taste_name']}"
    if taste_node_id not in node_ids:
        nodes.append({
            'id': taste_node_id,
            'name': records[0]['taste_name'],
            'category': 'Taste'
        })
        node_ids.add(taste_node_id)

    for item in records:
        dish_node_id = f"dish:{item['dish_name']}"

        if dish_node_id not in node_ids:
            nodes.append({
                'id': dish_node_id,
                'name': item['dish_name'],
                'category': 'Dish'
            })
            node_ids.add(dish_node_id)

        links.append({
            'source': taste_node_id,
            'target': dish_node_id,
            'relation': 'HAS_TASTE'
        })

    return {
        'nodes': nodes,
        'links': links
    }


def get_node_detail(node_type, node_name):
    with driver.session() as session:
        if node_type == 'Dish':
            query = """
            MATCH (d:Dish {name: $node_name})
            RETURN d.name AS name,
                   d.recipe_id AS recipe_id,
                   d.rating AS rating,
                   d.difficulty AS difficulty,
                   d.cook_time AS cook_time,
                   d.calories AS calories,
                   d.sugar AS sugar,
                   d.fat AS fat,
                   d.category AS category
            """
            record = session.run(query, node_name=node_name).single()
            if not record:
                return None

            return {
                'type': 'Dish',
                'name': record['name'],
                'recipe_id': record['recipe_id'],
                'rating': record['rating'],
                'difficulty': record['difficulty'],
                'cook_time': record['cook_time'],
                'calories': record['calories'],
                'sugar': record['sugar'],
                'fat': record['fat'],
                'category': record['category'],
            }

        elif node_type == 'Ingredient':
            query = """
            MATCH (d:Dish)-[r]->(i:Ingredient {name: $node_name})
            WHERE type(r) IN $relations
            RETURN i.name AS name, collect(DISTINCT d.name) AS dishes
            """
            record = session.run(query, node_name=node_name, relations=INGREDIENT_RELATIONS).single()
            if not record:
                return None

            dishes = record['dishes'] or []
            return {
                'type': 'Ingredient',
                'name': record['name'],
                'dish_count': len(dishes),
                'dishes': dishes
            }

        elif node_type == 'Category':
            query = """
            MATCH (d:Dish)-[:BELONGS_TO]->(c:Category {name: $node_name})
            RETURN c.name AS name, collect(DISTINCT d.name) AS dishes
            """
            record = session.run(query, node_name=node_name).single()
            if not record:
                return None

            dishes = record['dishes'] or []
            return {
                'type': 'Category',
                'name': record['name'],
                'dish_count': len(dishes),
                'dishes': dishes
            }

    return None


def get_dish_full_detail(dish_name):
    query = """
    MATCH (d:Dish {name: $dish_name})
    OPTIONAL MATCH (d)-[r1]->(i:Ingredient)
    WHERE type(r1) IN $relations
    OPTIONAL MATCH (d)-[:HAS_TASTE]->(t:Taste)
    OPTIONAL MATCH (d)-[:COOKED_BY]->(m:Method)

    RETURN d.name AS name,
           d.recipe_id AS recipe_id,
           d.rating AS rating,
           d.difficulty AS difficulty,
           d.cook_time AS cook_time,
           d.calories AS calories,
           d.sugar AS sugar,
           d.fat AS fat,
           d.category AS category,
           collect(DISTINCT i.name) AS ingredients,
           collect(DISTINCT t.name) AS tastes,
           collect(DISTINCT m.name) AS methods
    """

    with driver.session() as session:
        record = session.run(query, dish_name=dish_name, relations=INGREDIENT_RELATIONS).single()

    if not record:
        return None

    return {
        'name': record['name'],
        'recipe_id': record['recipe_id'],
        'rating': record['rating'],
        'difficulty': record['difficulty'],
        'cook_time': record['cook_time'],
        'calories': record['calories'],
        'sugar': record['sugar'],
        'fat': record['fat'],
        'category': record['category'],
        'ingredients': [x for x in (record['ingredients'] or []) if x],
        'tastes': [x for x in (record['tastes'] or []) if x],
        'methods': [x for x in (record['methods'] or []) if x],
    }

def get_dishes_by_category(category_name):
    query = """
    MATCH (d:Dish)-[:BELONGS_TO]->(c:Category {name: $category_name})
    RETURN c.name AS category_name, d.name AS dish_name
    LIMIT 50
    """

    with driver.session() as session:
        result = session.run(query, category_name=category_name)
        return [record.data() for record in result]

def get_graph_by_category(category_name):
    query = """
    MATCH (d:Dish)-[:BELONGS_TO]->(c:Category {name: $category_name})
    RETURN c.name AS category_name,
           d.name AS dish_name,
           d.recipe_id AS dish_id
    """

    with driver.session() as session:
        result = session.run(query, category_name=category_name)
        records = [record.data() for record in result]

    if not records:
        return {'nodes': [], 'links': []}

    nodes = []
    links = []
    node_ids = set()

    category_node_id = f"category:{records[0]['category_name']}"
    if category_node_id not in node_ids:
        nodes.append({
            'id': category_node_id,
            'name': records[0]['category_name'],
            'category': 'Category'
        })
        node_ids.add(category_node_id)

    for item in records:
        dish_node_id = f"dish:{item['dish_name']}"

        if dish_node_id not in node_ids:
            nodes.append({
                'id': dish_node_id,
                'name': item['dish_name'],
                'category': 'Dish'
            })
            node_ids.add(dish_node_id)

        links.append({
            'source': category_node_id,
            'target': dish_node_id,
            'relation': 'BELONGS_TO'
        })

    return {
        'nodes': nodes,
        'links': links
    }

def sync_recipe_to_neo4j(recipe):
    dish_name = (recipe.title or '').strip()
    if not dish_name:
        return

    ingredients = list(
        recipe.ingredients.exclude(name='').values_list('name', flat=True)
    )

    category = (recipe.category or '').strip()

    query = """
    MERGE (d:Dish {menu_id: $recipe_id})
    SET d.name = $dish_name,
        d.image = $image,
        d.difficulty = $difficulty,
        d.cook_time = $cook_time,
        d.category = $category

    WITH d
    OPTIONAL MATCH (d)-[r:USES_MAIN_INGREDIENT|USES_AUX_INGREDIENT|BELONGS_TO]->()
    DELETE r

    WITH d
    FOREACH (ing IN $ingredients |
        MERGE (i:Ingredient {name: ing})
        MERGE (d)-[:USES_MAIN_INGREDIENT]->(i)
    )

    FOREACH (_ IN CASE WHEN $category <> '' THEN [1] ELSE [] END |
        MERGE (c:Category {name: $category})
        MERGE (d)-[:BELONGS_TO]->(c)
    )
    """

    image_url = recipe.image.url if recipe.image else ''

    with driver.session() as session:
        session.run(
            query,
            recipe_id=recipe.id,
            dish_name=dish_name,
            image=image_url,
            difficulty=recipe.difficulty or '',
            cook_time=recipe.cook_time or '',
            category=category,
            ingredients=ingredients,
        )

def sync_recipe_to_neo4j(recipe):
    dish_name = (recipe.title or '').strip()
    if not dish_name:
        return

    ingredients = list(
        recipe.ingredients.exclude(name='').values_list('name', flat=True)
    )

    category = (recipe.category or '').strip()

    query = """
    MERGE (d:Dish {menu_id: $recipe_id})
    SET d.name = $dish_name,
        d.image = $image,
        d.difficulty = $difficulty,
        d.cook_time = $cook_time,
        d.category = $category

    WITH d
    OPTIONAL MATCH (d)-[r:USES_MAIN_INGREDIENT|USES_AUX_INGREDIENT|BELONGS_TO]->()
    DELETE r

    WITH d
    FOREACH (ing IN $ingredients |
        MERGE (i:Ingredient {name: ing})
        MERGE (d)-[:USES_MAIN_INGREDIENT]->(i)
    )

    FOREACH (_ IN CASE WHEN $category <> '' THEN [1] ELSE [] END |
        MERGE (c:Category {name: $category})
        MERGE (d)-[:BELONGS_TO]->(c)
    )
    """

    image_url = recipe.image.url if recipe.image else ''

    with driver.session() as session:
        session.run(
            query,
            recipe_id=recipe.id,
            dish_name=dish_name,
            image=image_url,
            difficulty=recipe.difficulty or '',
            cook_time=recipe.cook_time or '',
            category=category,
            ingredients=ingredients,
        )

def rebuild_all_approved_recipes_to_neo4j():
    from recipe.models import Recipe

    with driver.session() as session:
        session.run("MATCH (d:Dish) DETACH DELETE d")

    recipes = Recipe.objects.filter(review_status='approved')
    for recipe in recipes:
        sync_recipe_to_neo4j(recipe)

def remove_recipe_from_neo4j(recipe_id):
    query = """
    MATCH (d:Dish {menu_id: $recipe_id})
    DETACH DELETE d
    """
    with driver.session() as session:
        session.run(query, recipe_id=recipe_id)