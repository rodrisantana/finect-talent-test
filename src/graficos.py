"""Estilo común de los gráficos (mismos colores y tipografía en todos los scripts)."""
import matplotlib
matplotlib.use("Agg")          # dibuja en archivos, sin abrir ventanas
import matplotlib.pyplot as plt

AZUL = "#1f3b8c"
NARANJA = "#d9822b"
GRIS = "#9aa0a6"
ROJO = "#c0392b"
VERDE = "#2e7d32"


def aplicar_estilo():
    plt.rcParams.update({
        "font.family": ["Roboto", "Lexend", "Poppins", "DejaVu Sans"], "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "grid.alpha": 0.25, "figure.dpi": 150,
    })
