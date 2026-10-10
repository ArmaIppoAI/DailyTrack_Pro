import flet as ft
from datetime import date
from .config import APP_NAME, CREAM, PAPER, SAGE_DARK, SAGE_LIGHT, INK, MUTED
from .database import connect_db
from .views.dashboard import build_dashboard
from .views.food import build_food_page
from .views.history import build_history
from .views.workout import build_workout_page

def main(page: ft.Page):
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = CREAM
    page.padding = 0
    conn = connect_db()
    state = {"day": date.today().isoformat()}
    content = ft.Container(expand=True, padding=18)
    pages = {}

    def get_day_key():
        return state["day"]

    def refresh_all():
        for key in ("dashboard", "food", "history", "workout"):
            if key in pages:
                pages[key]["refresh"]()

    def open_day(day_key):
        state["day"] = day_key
        pages["dashboard"]["refresh"]()
        pages["food"]["refresh"]()
        pages["workout"]["refresh"]()
        show_tab("dashboard")

    def data_changed():
        if "history" in pages:
            pages["history"]["refresh"]()

    pages["dashboard"] = build_dashboard(page, conn, get_day_key, data_changed)
    pages["food"] = build_food_page(page, conn, get_day_key, data_changed)
    pages["history"] = build_history(page, conn, open_day)
    pages["workout"] = build_workout_page(page, conn, get_day_key, data_changed)

    nav_items = {}
    def show_tab(tab):
        content.content = pages[tab]["view"]
        for key, button in nav_items.items():
            button.style = ft.ButtonStyle(
                color=SAGE_DARK if key == tab else MUTED,
                bgcolor=SAGE_LIGHT if key == tab else None
            )
        page.update()

    nav_items["dashboard"] = ft.TextButton("Oggi", icon=ft.Icons.DASHBOARD_OUTLINED,
        on_click=lambda e: show_tab("dashboard"))
    nav_items["food"] = ft.TextButton("Cibo", icon=ft.Icons.RESTAURANT_OUTLINED,
        on_click=lambda e: show_tab("food"))
    nav_items["workout"] = ft.TextButton("Allenamento", icon=ft.Icons.DIRECTIONS_WALK,
        on_click=lambda e: show_tab("workout"))
    nav_items["history"] = ft.TextButton("Storico", icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda e: show_tab("history"))

    header = ft.Container(content=ft.Row([
        ft.Container(ft.Icon(ft.Icons.SPA_OUTLINED, color=SAGE_DARK, size=27),
                     bgcolor=SAGE_LIGHT, padding=9, border_radius=13),
        ft.Column([
            ft.Text(APP_NAME, size=20, weight=ft.FontWeight.BOLD, color=INK),
            ft.Text("Il tuo benessere, un giorno alla volta", size=11, color=MUTED)
        ], spacing=0, expand=True)
    ]), padding=ft.Padding(left=18, right=18, top=16, bottom=8))
    nav = ft.Container(content=ft.Row(list(nav_items.values()),
        alignment=ft.MainAxisAlignment.SPACE_AROUND, spacing=0, wrap=True),
        bgcolor=PAPER, padding=6)
    page.add(ft.Column([header, ft.Divider(height=1, color="#E1E4DB"), content, nav],
        spacing=0, expand=True))
    show_tab("dashboard")
