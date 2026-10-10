import flet as ft

from ..config import PAPER, SAGE_DARK, SAGE_LIGHT, INK, MUTED, GOLD
from ..database import (
    add_meal,
    meals_for_day,
    delete_meal,
    nutrition_totals,
)
from ..helpers import number, show_message
from ..services.food_api import search_food


def build_food_page(page, conn, get_day_key, on_change):
    query_field = ft.TextField(
        label="Cerca un alimento",
        hint_text="Es. banana, pasta, yogurt",
        expand=True,
    )

    quantity_field = ft.TextField(
        label="Quantità (g)",
        value="100",
        width=130,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    results_column = ft.Column(spacing=8)
    meals_column = ft.Column(spacing=8)

    status = ft.Text(
        "Cerca un alimento per ottenere una stima nutrizionale.",
        size=12,
        color=MUTED,
    )

    manual_name = ft.TextField(
        label="Nome alimento",
        expand=True,
    )

    manual_qty = ft.TextField(
        label="Quantità (g)",
        value="100",
        width=130,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    manual_kcal = ft.TextField(
        label="kcal / 100 g",
        value="0",
        width=130,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    manual_protein = ft.TextField(
        label="Proteine / 100 g",
        value="0",
        width=145,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    manual_carbs = ft.TextField(
        label="Carboidrati / 100 g",
        value="0",
        width=155,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    manual_fat = ft.TextField(
        label="Grassi / 100 g",
        value="0",
        width=130,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    selected = {"food": None}

    totals_text = ft.Text(
        "",
        size=14,
        weight=ft.FontWeight.BOLD,
        color=INK,
    )

    def update_page():
        try:
            page.update()
        except Exception:
            pass

    def refresh():
        meals_column.controls.clear()

        totals = nutrition_totals(conn, get_day_key())

        totals_text.value = (
            f"Totale: {number(totals['calories'])} kcal\n"
            f"Proteine: {number(totals['protein_g'], 1)} g · "
            f"Carboidrati: {number(totals['carbs_g'], 1)} g · "
            f"Grassi: {number(totals['fat_g'], 1)} g"
        )

        rows = meals_for_day(conn, get_day_key())

        if not rows:
            meals_column.controls.append(
                ft.Text(
                    "Nessun alimento inserito oggi.",
                    color=MUTED,
                )
            )

        for row in rows:
            meal_id = row["id"]

            meals_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        row["name"],
                                        weight=ft.FontWeight.BOLD,
                                        color=INK,
                                    ),
                                    ft.Text(
                                        f"{number(row['quantity_g'], 0)} g · "
                                        f"{number(row['calories'])} kcal · "
                                        f"P {number(row['protein_g'], 1)} g · "
                                        f"C {number(row['carbs_g'], 1)} g · "
                                        f"G {number(row['fat_g'], 1)} g",
                                        size=12,
                                        color=MUTED,
                                    ),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Elimina alimento",
                                on_click=lambda e, mid=meal_id: remove_meal(mid),
                            ),
                        ],
                    ),
                    bgcolor=PAPER,
                    padding=12,
                    border_radius=14,
                )
            )

        update_page()
    """
    Vecchia versione

    def choose_food(food):
        selected["food"] = food

        status.value = (
            f"{food['name']} — valori per 100 g: "
            f"{number(food['calories'])} kcal · "
            f"P {number(food['protein_g'], 1)} g · "
            f"C {number(food['carbs_g'], 1)} g · "
            f"G {number(food['fat_g'], 1)} g"
        )

        quantity_field.value = "100"
        update_page()
        
        """
    def choose_food(food):
        # Normalizza i campi restituiti dalle diverse versioni dell'API.
        food = dict(food)

        food["calories"] = float(
            food.get("calories", food.get("kcal_100g", 0)) or 0
        )
        food["protein_g"] = float(
            food.get("protein_g", food.get("protein_100g", 0)) or 0
        )
        food["carbs_g"] = float(
            food.get("carbs_g", food.get("carbs_100g", 0)) or 0
        )
        food["fat_g"] = float(
            food.get("fat_g", food.get("fat_100g", 0)) or 0
        )

        selected["food"] = food

        status.value = (
            f"{food['name']} — valori per 100 g: "
            f"{number(food['calories'])} kcal · "
            f"P {number(food['protein_g'], 1)} g · "
            f"C {number(food['carbs_g'], 1)} g · "
            f"G {number(food['fat_g'], 1)} g"
        )

        quantity_field.value = "100"
        page.update()


    def search(e=None):
        query = (query_field.value or "").strip()

        results_column.controls.clear()
        selected["food"] = None

        if not query:
            status.value = "Scrivi il nome di un alimento da cercare."
            update_page()
            return

        status.value = "Ricerca in corso..."
        update_page()

        try:
            results = search_food(query)

            if not results:
                status.value = (
                    "Nessun risultato trovato. Controlla la connessione "
                    "oppure prova un altro termine."
                )
            else:
                status.value = (
                    f"Trovati {len(results)} risultati. "
                    "Seleziona l'alimento corretto."
                )

                for food in results:
                    name = food.get("name") or "Alimento senza nome"
                    brand = food.get("brand") or ""
                    title = f"{name} · {brand}" if brand else name

                    results_column.controls.append(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                title,
                                                weight=ft.FontWeight.BOLD,
                                                color=INK,
                                            ),
                                            ft.Text(
                                                f"{number(food.get('calories', 0))} kcal · "
                                                f"P {number(food.get('protein_g', 0), 1)} g · "
                                                "per 100 g",
                                                size=11,
                                                color=MUTED,
                                            ),
                                        ],
                                        spacing=3,
                                        expand=True,
                                    ),
                                    ft.FilledButton(
                                        "Scegli",
                                        on_click=lambda e, item=food: choose_food(item),
                                        style=ft.ButtonStyle(
                                            bgcolor=SAGE_DARK,
                                            color="#FFFFFF",
                                        ),
                                    ),
                                ],
                            ),
                            bgcolor=PAPER,
                            padding=10,
                            border_radius=12,
                        )
                    )

        except Exception as ex:
            status.value = (
                f"Errore durante la ricerca: {type(ex).__name__}. "
                "Verifica la connessione e il file nutrition_api.py."
            )

        update_page()

    def add_selected(e=None):
        food = selected["food"]

        if not food:
            show_message(page, "Prima cerca e seleziona un alimento.")
            return

        try:
            qty = float(
                (quantity_field.value or "100").replace(",", ".")
            )

            if qty <= 0:
                raise ValueError

        except ValueError:
            show_message(page, "Inserisci una quantità valida in grammi.")
            return

        factor = qty / 100

        add_meal(
            conn,
            get_day_key(),
            food["name"],
            qty,
            float(food.get("calories") or 0) * factor,
            float(food.get("protein_g") or 0) * factor,
            float(food.get("carbs_g") or 0) * factor,
            float(food.get("fat_g") or 0) * factor,
            "Open Food Facts",
        )

        selected["food"] = None
        refresh()
        on_change()
        show_message(page, "Alimento aggiunto al diario.")

    def add_manual(e=None):
        try:
            name = (manual_name.value or "").strip()

            qty = float((manual_qty.value or "100").replace(",", "."))
            kcal = float((manual_kcal.value or "0").replace(",", "."))
            protein = float((manual_protein.value or "0").replace(",", "."))
            carbs = float((manual_carbs.value or "0").replace(",", "."))
            fat = float((manual_fat.value or "0").replace(",", "."))

            if not name or qty <= 0:
                raise ValueError

            if min(kcal, protein, carbs, fat) < 0:
                raise ValueError

        except ValueError:
            show_message(
                page,
                "Controlla il nome, la quantità e i valori nutrizionali.",
            )
            return

        factor = qty / 100

        add_meal(
            conn,
            get_day_key(),
            name,
            qty,
            kcal * factor,
            protein * factor,
            carbs * factor,
            fat * factor,
            "manuale",
        )

        manual_name.value = ""
        refresh()
        on_change()
        show_message(page, "Alimento inserito.")

    def remove_meal(meal_id):
        delete_meal(conn, meal_id)
        refresh()
        on_change()
        show_message(page, "Alimento eliminato.")

    view = ft.Column(
        controls=[
            ft.Text(
                "Alimentazione",
                size=27,
                weight=ft.FontWeight.BOLD,
                color=INK,
            ),
            ft.Text(
                "Registra i pasti e controlla i valori nutrizionali.",
                color=MUTED,
                size=13,
            ),
            ft.Column(
                controls=[
                    query_field,
                    ft.Row(
                        controls=[
                            ft.FilledButton(
                                "Cerca",
                                icon=ft.Icons.SEARCH,
                                on_click=search,
                                style=ft.ButtonStyle(
                                    bgcolor=SAGE_DARK,
                                    color="#FFFFFF",
                                ),
                            ),
                        ],
                    ),
                ],
                spacing=8,
                width=float("inf"),
            ),
            status,
            results_column,
            ft.Row(
                controls=[
                    quantity_field,
                    ft.FilledButton(
                        "Aggiungi alimento",
                        on_click=add_selected,
                        style=ft.ButtonStyle(
                            bgcolor=SAGE_DARK,
                            color="#FFFFFF",
                        ),
                    ),
                ],
                wrap=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Divider(color="#DDE2D8"),
            ft.Text(
                "Inserimento manuale",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=INK,
            ),
            manual_name,
            ft.Row(
                controls=[manual_qty, manual_kcal],
                wrap=True,
            ),
            ft.Row(
                controls=[manual_protein, manual_carbs, manual_fat],
                wrap=True,
            ),
            ft.FilledButton(
                "Salva alimento manuale",
                icon=ft.Icons.ADD,
                on_click=add_manual,
                style=ft.ButtonStyle(
                    bgcolor=SAGE_LIGHT,
                    color=SAGE_DARK,
                ),
            ),
            ft.Divider(color="#DDE2D8"),
            ft.Text(
                "Riepilogo alimentare",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=INK,
            ),
            totals_text,
            meals_column,
            ft.Text(
                "I valori nutrizionali possono essere incompleti o approssimativi. "
                "Controlla sempre l'etichetta del prodotto.",
                size=10,
                color=MUTED,
            ),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    refresh()

    return {
        "view": view,
        "refresh": refresh,
    }
