import flet as ft
from ..config import PAPER, SAGE, SAGE_DARK, SAGE_LIGHT, INK, MUTED, BLUE, GOLD, WATER_GOAL_ML, STEPS_GOAL, DEFAULT_WEIGHT_KG, PROTEIN_G_PER_KG
from ..database import get_day, save_day, nutrition_totals
from ..helpers import format_long_date, number, show_message

def build_dashboard(page, conn, get_day_key, on_change):
    date_label = ft.Text("", size=12, color=MUTED)
    water_value = ft.Text("", size=24, weight=ft.FontWeight.BOLD, color=INK)
    water_goal = ft.Text("", size=12, color=MUTED)
    water_progress = ft.ProgressBar(value=0, color=BLUE, bgcolor="#E6EDF2", bar_height=8)
    steps_value = ft.Text("", size=24, weight=ft.FontWeight.BOLD, color=INK)
    steps_goal = ft.Text("", size=12, color=MUTED)
    steps_progress = ft.ProgressBar(value=0, color=SAGE, bgcolor="#E6E9E1", bar_height=8)
    calories_value = ft.Text("0 kcal", size=24, weight=ft.FontWeight.BOLD, color=INK)
    calories_sub = ft.Text("Stima alimentare", size=12, color=MUTED)
    protein_value = ft.Text("0 / 140 g", size=24, weight=ft.FontWeight.BOLD, color=INK)
    protein_sub = ft.Text("Obiettivo: 2 g per kg", size=12, color=MUTED)
    protein_progress = ft.ProgressBar(value=0, color=GOLD, bgcolor="#F2EBDD", bar_height=8)
    note_status = ft.Text("Da scrivere", size=17, weight=ft.FontWeight.BOLD, color=INK)
    summary = ft.Text("", size=12, color=SAGE_DARK)
    weight_field = ft.TextField(label="Peso corporeo (kg)", keyboard_type=ft.KeyboardType.NUMBER, width=160)
    steps_field = ft.TextField(label="Passi fatti oggi", value="0", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    note_field = ft.TextField(label="Com'è andata oggi?", hint_text="Pensieri, attività o cose da ricordare…",
        multiline=True, min_lines=20, max_lines=30, border_color="#C7D3C3", focused_border_color=SAGE, bgcolor=PAPER)

    def card(content):
        return ft.Container(content=content, bgcolor=PAPER, padding=15, border_radius=18)

    def refresh():
        day = get_day_key()
        row = get_day(conn, day)
        totals = nutrition_totals(conn, day)
        weight = row["weight_kg"] or DEFAULT_WEIGHT_KG
        protein_target = weight * PROTEIN_G_PER_KG
        date_label.value = format_long_date(day)
        water_value.value = f"{number(row['water_ml'])} ml"
        water_goal.value = f"Obiettivo indicativo: {number(WATER_GOAL_ML)} ml"
        water_progress.value = min(row["water_ml"] / WATER_GOAL_ML, 1)
        steps_value.value = number(row["steps"])
        steps_goal.value = f"Obiettivo: {number(STEPS_GOAL)} passi"
        steps_progress.value = min(row["steps"] / STEPS_GOAL, 1)
        calories_value.value = f"{number(totals['calories'])} kcal"
        calories_sub.value = f"Carboidrati {number(totals['carbs_g'],1)} g · Grassi {number(totals['fat_g'],1)} g"
        protein_value.value = f"{number(totals['protein_g'],1)} / {number(protein_target,1)} g"
        protein_sub.value = f"Target proteine: 2 g/kg · peso {number(weight,1)} kg"
        protein_progress.value = min(totals["protein_g"] / protein_target, 1) if protein_target else 0
        note_field.value = row["note"]
        steps_field.value = str(row["steps"])
        weight_field.value = str(weight)
        note_status.value = "Nota completata" if row["note"].strip() else "Nota da scrivere"
        summary.value = "Check-in: " + " · ".join([
            "✓ acqua" if row["water_ml"] else "○ acqua",
            "✓ passi" if row["steps"] else "○ passi",
            "✓ diario" if row["note"].strip() else "○ diario",
            "✓ cibo" if totals["calories"] else "○ cibo"])
    def adjust_water(amount):
        row = get_day(conn, get_day_key())
        save_day(conn, get_day_key(), water_ml=max(0, row["water_ml"] + amount))
        refresh(); on_change(); page.update()
        show_message(page, "Acqua aggiornata")
    def save_steps(e=None):
        try:
            val = int((steps_field.value or "0").strip())
            if val < 0: raise ValueError
        except ValueError:
            show_message(page, "Inserisci un numero di passi valido.")
            return
        save_day(conn, get_day_key(), steps=val)
        refresh(); on_change(); page.update()
        show_message(page, "Passi salvati")
    def save_weight(e=None):
        try:
            val = float((weight_field.value or "").replace(",", "."))
            if val <= 0 or val > 500: raise ValueError
        except ValueError:
            show_message(page, "Inserisci un peso valido in kg.")
            return
        save_day(conn, get_day_key(), weight_kg=val)
        refresh(); on_change(); page.update()
        show_message(page, "Peso salvato: obiettivo proteine aggiornato")
    def save_note(e=None):
        save_day(conn, get_day_key(), note=note_field.value or "")
        refresh(); on_change(); page.update()
        show_message(page, "Nota salvata")

    water_card = card(ft.Column([
        ft.Row([ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color=BLUE, size=27),
                ft.Column([ft.Text("Acqua bevuta", color=MUTED), water_value, water_goal], spacing=2, expand=True)]),
        water_progress,
        ft.Row([
            ft.OutlinedButton("-250 ml", on_click=lambda e: adjust_water(-250)),
            ft.FilledButton("+250 ml", on_click=lambda e: adjust_water(250), style=ft.ButtonStyle(bgcolor=SAGE_DARK, color="#FFFFFF")),
            ft.FilledButton("+500 ml", on_click=lambda e: adjust_water(500), style=ft.ButtonStyle(bgcolor=SAGE_LIGHT, color=SAGE_DARK)),
        ], wrap=True, spacing=6)
    ], spacing=11))
    steps_card = card(ft.Column([
        ft.Row([ft.Icon(ft.Icons.DIRECTIONS_WALK, color=SAGE_DARK, size=27),
                ft.Column([ft.Text("Passi", color=MUTED), steps_value, steps_goal], spacing=2, expand=True)]),
        steps_progress,
        ft.Row([steps_field, ft.FilledButton("Salva", on_click=save_steps, style=ft.ButtonStyle(bgcolor=SAGE_DARK, color="#FFFFFF"))])
    ], spacing=11))
    food_card = card(ft.Column([
        ft.Row([ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_OUTLINED, color=GOLD, size=27),
                ft.Column([ft.Text("Alimentazione di oggi", color=MUTED), calories_value, calories_sub], spacing=2, expand=True)]),
        ft.Divider(height=1, color="#E8E8DF"),
        ft.Text("Proteine", color=MUTED),
        protein_value, protein_sub, protein_progress,
        ft.Row([weight_field, ft.FilledButton("Salva peso", on_click=save_weight,
            style=ft.ButtonStyle(bgcolor=SAGE_DARK, color="#FFFFFF"))], wrap=True)
    ], spacing=8))
    note_card = card(ft.Column([
        ft.Row([ft.Icon(ft.Icons.EDIT_NOTE, color=GOLD, size=27),
                ft.Column([ft.Text("Diario giornaliero", color=MUTED), note_status], spacing=2)]),
        note_field,
        ft.FilledButton("Salva nota", on_click=save_note, style=ft.ButtonStyle(bgcolor=SAGE_DARK, color="#FFFFFF"), width=float("inf"))
    ], spacing=10))
    view = ft.Column([
        ft.Text("La tua giornata", size=27, weight=ft.FontWeight.BOLD, color=INK),
        date_label, summary, water_card, steps_card, food_card, note_card,
        ft.Text("Calorie e macronutrienti sono stime, non indicazioni mediche.", size=10, color=MUTED,
                text_align=ft.TextAlign.CENTER)
    ], spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    refresh()
    return {"view": view, "refresh": refresh}
