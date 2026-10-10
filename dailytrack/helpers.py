from datetime import datetime
import flet as ft

def format_long_date(day):
    return datetime.strptime(day, "%Y-%m-%d").strftime("%A, %d %B %Y").capitalize()

def format_short_date(day):
    return datetime.strptime(day, "%Y-%m-%d").strftime("%d/%m/%Y")

def show_message(page: ft.Page, message: str):
    # API compatibile con versioni di Flet che non espongono page.open()
    snack = ft.SnackBar(content=ft.Text(message, color="#FFFFFF"), bgcolor="#36563D")
    page.snack_bar = snack
    snack.open = True
    page.update()

def number(value, digits=0):
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")
