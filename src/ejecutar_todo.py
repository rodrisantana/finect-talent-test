"""Ejecuta todo el análisis en orden y regenera la carpeta resultados/.

Uso:  python src/ejecutar_todo.py     (tarda unos minutos)
"""
import runpy
from pathlib import Path

AQUI = Path(__file__).resolve().parent
for script in ["backtest_historico.py", "plan_montecarlo.py", "sensibilidades.py",
               "alternativas_cartera.py", "verificar.py"]:
    print(f"\n{'=' * 70}\n  {script}\n{'=' * 70}")
    runpy.run_path(str(AQUI / script), run_name="__main__")
