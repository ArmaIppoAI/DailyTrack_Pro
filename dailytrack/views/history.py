import flet as ft
from ..config import PAPER, SAGE, SAGE_DARK, INK, MUTED
from ..database import recent_days
from ..helpers import format_short_date, number

def build_history(page, conn, on_open_day):
    items = ft.Column(spacing=10)
    def refresh():
        items.controls.clear()
        rows = recent_days(conn, 90)
        for row in rows:
            has_note = bool(row["note"].strip())
            preview = row["note"][:160] + ("…" if len(row["note"]) > 160 else "")
            items.controls.append(ft.Container(content=ft.Column([
                ft.Row([ft.Column([
                    ft.Text(format_short_date(row["day"]), weight=ft.FontWeight.BOLD, color=INK),
                    ft.Text(f"💧 {row['water_ml']} ml · 👣 {row['steps']} passi · {number(row['calories'])} kcal",
                            size=12, color=MUTED),
                    ft.Text(f"Proteine: {number(row['protein_g'],1)} g", size=12, color=MUTED)
                ], spacing=4, expand=True),
                ft.Icon(ft.Icons.CHECK_CIRCLE if has_note else ft.Icons.RADIO_BUTTON_UNCHECKED,
                        color=SAGE if has_note else "#A5ADA5")]),
                ft.Text(preview if has_note else "Nessuna nota", size=13 if has_note else 12,
                        color=SAGE_DARK if has_note else MUTED, italic=not has_note),
                ft.OutlinedButton("Apri giornata", on_click=lambda e, d=row["day"]: on_open_day(d))
            ], spacing=8), bgcolor=PAPER, padding=14, border_radius=16))
        if not items.controls:
            items.controls.append(ft.Text("Lo storico si popolerà quando registri i tuoi dati.", color=MUTED))
        page.update()
    view = ft.Column([
        ft.Text("Storico", size=27, weight=ft.FontWeight.BOLD, color=INK),
        ft.Text("Rivedi diario, passi e alimentazione delle giornate precedenti.", color=MUTED, size=13),
        items
    ], spacing=13, scroll=ft.ScrollMode.AUTO, expand=True)
    refresh()
    return {"view": view, "refresh": refresh}
