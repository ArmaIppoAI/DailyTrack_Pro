"""Ricerca alimenti tramite Open Food Facts. La rete è opzionale."""
import requests

API_URL = "https://world.openfoodfacts.org/cgi/search.pl"

def search_food(query, limit=8):
    query = (query or "").strip()
    if len(query) < 2:
        return []
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
        "fields": "product_name,brands, nutriments, quantity, code",
    }
    # Rimuovi lo spazio accidentale nel campo fields.
    params["fields"] = "product_name,brands,nutriments,quantity,code"
    headers = {"User-Agent": "DailyTrack/1.0 (personal wellness tracker)"}
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=7)
        response.raise_for_status()
        products = response.json().get("products", [])
    except (requests.RequestException, ValueError):
        return []
    results = []
    for product in products:
        name = (product.get("product_name") or "").strip()
        nutrients = product.get("nutriments") or {}
        kcal = nutrients.get("energy-kcal_100g")
        if kcal is None:
            kj = nutrients.get("energy-kj_100g")
            kcal = float(kj) / 4.184 if kj not in (None, "") else None
        protein = nutrients.get("proteins_100g")
        if not name or kcal is None:
            continue
        try:
            kcal = float(kcal)
            protein = float(protein or 0)
        except (ValueError, TypeError):
            continue
        if kcal < 0 or protein < 0:
            continue
        brand = (product.get("brands") or "").strip()
        results.append({
            "name": f"{name} ({brand})" if brand else name,
            "kcal_100g": kcal,
            "protein_100g": protein,
            "source": "Open Food Facts",
        })
    return results
