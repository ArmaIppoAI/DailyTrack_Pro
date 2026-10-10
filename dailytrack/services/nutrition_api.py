
import requests

BASE_URL = "https://world.openfoodfacts.org"

HEADERS = {
    "User-Agent": "DailyTrack/1.0 (personal nutrition tracker)"
}


def search_food(query: str):
    query = query.strip()

    if not query:
        return []

    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 20,
        "lc": "it",
        "cc": "it",
        "fields": (
            "code,product_name,product_name_it,"
            "brands,nutriments,quantity"
        ),
    }

    try:
        response = requests.get(
            f"{BASE_URL}/cgi/search.pl",
            params=params,
            headers=HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError):
        return []

    results = []

    for product in data.get("products", []):
        nutriments = product.get("nutriments") or {}

        name = (
            product.get("product_name_it")
            or product.get("product_name")
            or ""
        ).strip()

        if not name:
            continue

        calories = nutriments.get("energy-kcal_100g")

        if calories is None:
            energy_kj = nutriments.get("energy-kj_100g")

            if energy_kj is not None:
                try:
                    calories = float(energy_kj) / 4.184
                except (TypeError, ValueError):
                    calories = 0
            else:
                calories = 0

        def nutrient_value(key):
            try:
                return float(nutriments.get(key) or 0)
            except (TypeError, ValueError):
                return 0

        try:
            calories = float(calories or 0)
        except (TypeError, ValueError):
            calories = 0

        results.append({
            "name": name,
            "brand": product.get("brands") or "",
            "code": product.get("code") or "",
            "quantity": product.get("quantity") or "",
            "calories": calories,
            "protein_g": nutrient_value("proteins_100g"),
            "carbs_g": nutrient_value("carbohydrates_100g"),
            "fat_g": nutrient_value("fat_100g"),
        })

    return results
