import flet as ft
from ..config import PAPER, SAGE_DARK, SAGE_LIGHT, INK, MUTED, WATER_GOAL_ML, STEPS_GOAL, CALORIE_GOAL_DEFAULT
from ..database import get_profile, save_profile
from ..helpers import safe_float, show_message

def build_settings(page, conn, on_change):
    weight = ft.TextField(label="Peso corporeo (kg)", keyboard_type=ft.KeyboardType.NUMBER)
    water = ft.TextField(label="Obiettivo acqua (ml)", keyboard_type=ft.KeyboardType.NUMBER)
    steps = ft.TextField(label="Obiettivo passi", keyboard_type=ft.KeyboardType.NUMBER)
    calories = ft.TextField(label="Obiettivo calorie giornaliero (kcal)", keyboard_type=ft.KeyboardType.NUMBER)
    protein_info = ft.Text("", color=SAGE_DARK, size=14, weight=ft.FontWeight.BOLD)

    def refresh():
        profile = get_profile(conn)
        weight.value = str(profile["weight_kg"])
        water.value = str(profile["water_goal_ml"])
        steps.value = str(profile["steps_goal"])
        calories.value = str(profile["calorie_goal"])
        protein_info.value = f"Obiettivo proteine calcolato: {profile['weight_kg'] * 2:.0f} g al giorno (2 g/kg)"
        page.update()

    def save(e=None):
        w = safe_float(weight.value)
        wa = safe_float(water.value)
        st = safe_float(steps.value)
        ca = safe_float(calories.value)
        if None in (w, wa, st, ca) or w <= 0 or wa < 250 or st < 500 or ca < 500:
            show_message(page, "Controlla i valori: peso positivo, acqua ≥250, passi ≥500, calorie ≥500.")
            return
        save_profile(conn, w, wa, st, ca)
        refresh(); on_change()
        show_message(page, "Profilo salvato")

    view = ft.Column([
        ft.Text("Profilo e obiettivi", size=26, weight=ft.FontWeight.BOLD, color=INK),
        ft.Text("Personalizza i tuoi obiettivi. Il target proteico è impostato a 2 g per kg di peso corporeo.",
                size=12, color=MUTED),
        ft.Container(content=ft.Column([
            weight, protein_info, water, steps, calories,
            ft.FilledButton("Salva obiettivi", on_click=save,
                style=ft.ButtonStyle(bgcolor=SAGE_DARK, color="#FFFFFF"), width=float("inf"))
        ], spacing=13), bgcolor=PAPER, padding=16, border_radius=18),
        ft.Text("Nota: 2 g/kg è un'impostazione scelta dall'utente, non una prescrizione medica. Il fabbisogno individuale varia in base a salute, età e attività.",
                size=11, color=MUTED),
    ], spacing=14, scroll=ft.ScrollMode.AUTO, expand=True)
    refresh()
    return {"view": view, "refresh": refresh}
