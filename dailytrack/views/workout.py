import flet as ft
from datetime import datetime
from time import monotonic
from ..config import PAPER, SAGE_DARK, SAGE_LIGHT, INK, MUTED, GOLD
from ..database import add_workout, workouts_for_day
from ..helpers import number, show_message

def build_workout_page(page, conn, get_day_key, on_change):
    
    state = {"running": False, "start_clock": None, "started_at": None, "elapsed": 0}
    timer_text = ft.Text("00:00:00", size=36, weight=ft.FontWeight.BOLD, color=INK)
    steps_field = ft.TextField(label="Passi della sessione (da sensore o inseriti)", value="0",
                               keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    distance_field = ft.TextField(label="Distanza (km, facoltativa)", value="0",
                                  keyboard_type=ft.KeyboardType.NUMBER, width=180)
    status = ft.Text("Avvia una sessione quando inizi a camminare.", color=MUTED)
    workouts_list = ft.Column(spacing=8)
    start_button = ft.FilledButton("Inizia camminata", icon=ft.Icons.PLAY_ARROW)
    stop_button = ft.OutlinedButton("Termina e salva", icon=ft.Icons.STOP, disabled=True)

    def format_seconds(sec):
        sec = max(0, int(sec))
        h, rem = divmod(sec, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def refresh_history():
        workouts_list.controls.clear()
        rows = workouts_for_day(conn, get_day_key())
        if not rows:
            workouts_list.controls.append(ft.Text("Nessuna sessione registrata oggi.", color=MUTED))
        for row in rows:
            workouts_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text(f"Camminata · {format_seconds(row['duration_seconds'])}",
                            weight=ft.FontWeight.BOLD, color=INK),
                    ft.Text(f"{row['steps']} passi · {number(row['distance_km'],2)} km",
                            size=12, color=MUTED)
                ], spacing=3), bgcolor=PAPER, padding=12, border_radius=12))
        page.update()

    def tick():
        if state["running"]:
            timer_text.value = format_seconds(monotonic() - state["start_clock"])
            page.update()

    def start(e=None):
        if state["running"]:
            return
        state["running"] = True
        state["start_clock"] = monotonic()
        state["started_at"] = datetime.now()
        start_button.disabled = True
        stop_button.disabled = False
        status.value = "Sessione attiva. Il timer misura la durata, non i passi del sensore."
        page.update()
        # Timer periodico compatibile con Flet; non effettua rilevamento passi.
        page.run_task(timer_loop)

    async def timer_loop():
        import asyncio
        while state["running"]:
            tick()
            await asyncio.sleep(1)

    def stop(e=None):
        if not state["running"]:
            show_message(page, "Non c'è una sessione attiva.")
            return
        elapsed = int(monotonic() - state["start_clock"])
        try:
            steps = int((steps_field.value or "0").strip())
            distance = float((distance_field.value or "0").replace(",", "."))
            if steps < 0 or distance < 0: raise ValueError
        except ValueError:
            show_message(page, "Passi e distanza devono essere numeri non negativi.")
            return
        ended = datetime.now()
        add_workout(conn, get_day_key(), state["started_at"].isoformat(timespec="seconds"),
                    ended.isoformat(timespec="seconds"), elapsed, steps, distance)
        state["running"] = False
        start_button.disabled = False
        stop_button.disabled = True
        status.value = "Sessione salvata nello storico."
        timer_text.value = format_seconds(elapsed)
        steps_field.value = "0"
        distance_field.value = "0"
        refresh_history()
        on_change()
        page.update()
        show_message(page, "Allenamento salvato")

    start_button.on_click = start
    stop_button.on_click = stop
    view = ft.Column([
        ft.Text("Allenamento", size=27, weight=ft.FontWeight.BOLD, color=INK),
        ft.Text("Registra una camminata e aggiungi i passi della sessione.", color=MUTED, size=13),
        ft.Container(content=ft.Column([
            ft.Icon(ft.Icons.DIRECTIONS_WALK, size=38, color=SAGE_DARK),
            timer_text, status,
            ft.Row([start_button, stop_button], wrap=True)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            bgcolor=PAPER, padding=20, border_radius=18),
        ft.Text("Riepilogo sessione", size=18, weight=ft.FontWeight.BOLD, color=INK),
        steps_field, distance_field,
        ft.Text("Nota: il timer non può leggere da solo il sensore passi. L'integrazione automatica Android richiede un modulo nativo e permessi dedicati.", size=11, color=MUTED),
        ft.Divider(color="#DDE2D8"),
        ft.Text("Sessioni di oggi", size=18, weight=ft.FontWeight.BOLD, color=INK),
        workouts_list
    ], spacing=13, scroll=ft.ScrollMode.AUTO, expand=True)
    refresh_history()
    
    def refresh():
        refresh_history()

    return {"view": view, "refresh": refresh}

