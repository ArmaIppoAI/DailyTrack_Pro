from pathlib import Path
import os

APP_NAME = "DailyTrack Pro"
DB_PATH = Path(__file__).resolve().parent.parent / "dailytrack.db"

CREAM = "#F4F3EC"
PAPER = "#FFFFFF"
SAGE = "#6F8F72"
SAGE_DARK = "#36563D"
SAGE_LIGHT = "#DCE7D5"
INK = "#24372C"
MUTED = "#68766B"
BLUE = "#6A9FC4"
GOLD = "#9A7C4D"

WATER_GOAL_ML = 2000
STEPS_GOAL = 8000
DEFAULT_WEIGHT_KG = 70.0
PROTEIN_G_PER_KG = 2.0
USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
