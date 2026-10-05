"""
SIMULACIÓN MONTE CARLO DEL PLAN (cifras de la diapositiva 7 y del bloque "SI PREGUNTAN")

Uso:  python src/plan_montecarlo.py
Crea: resultados/plan/*.csv y resultados/plan/*.png

Qué contesta:
  1. ¿Cuánto patrimonio tiene a los 33 años? (gráfico de la portada)
  2. ¿Con qué probabilidad le llega el dinero a los 95 según lo que gaste al año?
  3. ¿Cuánto puede gastar según lo seguros que queramos estar?
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import modelo_plan as mp
import graficos as g

g.aplicar_estilo()
RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "resultados" / "plan"
OUT.mkdir(parents=True, exist_ok=True)
INMUEBLES = 6.3      # M€ de hoy, valor real constante


def patrimonio_hasta_la_retirada():
    """Patrimonio previsto de los 26 a los 33 años (escenario central, sin azar)."""
    edades, tray, _ = mp.simular(0.55)                 # determinista: n=1, vol=0
    cartera = tray[0, :8]                              # 26..33
    tabla = pd.DataFrame({"edad": edades[:8], "cartera_financiera": cartera.round(1),
                          "inmuebles": INMUEBLES})
    tabla["total"] = (tabla["cartera_financiera"] + tabla["inmuebles"]).round(1)
    tabla.to_csv(OUT / "patrimonio_26_33.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar(tabla["edad"], tabla["cartera_financiera"], color=g.AZUL, label="Cartera financiera (incluye la reserva de la agencia)")
    ax.bar(tabla["edad"], tabla["inmuebles"], bottom=tabla["cartera_financiera"], color=g.GRIS, label="Inmuebles")
    for e, t in zip(tabla["edad"], tabla["total"]):
        ax.text(e, t + 0.5, f"{t:.1f}", ha="center", fontweight="bold")
    ax.set_xlabel("Edad"); ax.set_ylabel("M€ de hoy")
    ax.set_title("Patrimonio previsto durante la carrera (M€ de hoy)", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(OUT / "patrimonio_26_33.png"); plt.close(fig)
    return tabla


def tabla_probabilidades():
    """Probabilidad de que el dinero llegue a los 95 según el gasto anual."""
    filas = []
    for gasto in (0.45, 0.50, 0.55, 0.575, 0.60, 0.65, 0.70, 0.80, 1.00):
        filas.append({
            "gasto_anual_€": int(gasto * 1_000_000),
            "prob_llegar_a_95_con_venta_inmuebles_%": round(100 * mp.probabilidad_exito(gasto, vender_inmuebles=True), 1),
            "prob_llegar_a_95_sin_vender_inmuebles_%": round(100 * mp.probabilidad_exito(gasto), 1),
        })
    t = pd.DataFrame(filas)
    t.to_csv(OUT / "probabilidad_por_gasto.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 4))
    x = t["gasto_anual_€"] / 1000
    ax.plot(x, t["prob_llegar_a_95_con_venta_inmuebles_%"], "-o", color=g.AZUL, label="Vendiendo inmuebles si hace falta")
    ax.plot(x, t["prob_llegar_a_95_sin_vender_inmuebles_%"], "--o", color=g.NARANJA, label="Sin vender nunca los inmuebles")
    ax.axhline(90, color=g.GRIS, lw=0.8)
    ax.set_xlabel("Gasto anual desde la retirada (miles de € de hoy)")
    ax.set_ylabel("% de escenarios que llegan a los 95")
    ax.set_title("Probabilidad de que el dinero llegue a los 95 años", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(OUT / "probabilidad_por_gasto.png"); plt.close(fig)
    return t


def tabla_gasto_por_confianza():
    """Gasto máximo sostenible según lo seguros que queramos estar."""
    filas = []
    for conf in (0.50, 0.75, 0.80, 0.85, 0.90, 0.95):
        filas.append({
            "confianza_%": int(conf * 100),
            "gasto_sostenible_con_venta_€": round(1e6 * mp.gasto_sostenible(conf, vender_inmuebles=True), -3),
            "gasto_sostenible_sin_vender_€": round(1e6 * mp.gasto_sostenible(conf), -3),
        })
    filas.append({
        "confianza_%": "central (sin azar)",
        "gasto_sostenible_con_venta_€": round(1e6 * mp.gasto_sostenible(vender_inmuebles=True), -3),
        "gasto_sostenible_sin_vender_€": round(1e6 * mp.gasto_sostenible(), -3),
    })
    t = pd.DataFrame(filas)
    t.to_csv(OUT / "gasto_por_confianza.csv", index=False)
    return t


def grafico_abanico(gasto=0.55):
    """Evolución de la cartera en 20.000 escenarios: mediana y rangos."""
    edades, tray, _ = mp.simular(gasto, n=20000, vol=mp.VOL_PRUDENTE, vender_inmuebles=False)
    pct = {p: np.percentile(tray, p, axis=0) for p in (5, 25, 50, 75, 95)}
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.fill_between(edades, pct[5], pct[95], color=g.AZUL, alpha=0.12, label="Del 5 % al 95 % de los escenarios")
    ax.fill_between(edades, pct[25], pct[75], color=g.AZUL, alpha=0.28, label="Del 25 % al 75 %")
    ax.plot(edades, pct[50], color=g.AZUL, lw=2, label="Escenario mediano")
    ax.set_ylim(0, 60)
    ax.axvline(33, color=g.GRIS, ls="--", lw=0.8); ax.text(33.5, 55, "retirada", color=g.GRIS)
    ax.set_xlabel("Edad"); ax.set_ylabel("Cartera financiera, M€ de hoy")
    ax.set_title(f"Cartera financiera con un gasto de {int(gasto*1000)}.000 € al año desde los 33 (sin vender inmuebles)",
                 loc="left", fontweight="bold", fontsize=10)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(OUT / "abanico_cartera.png"); plt.close(fig)


if __name__ == "__main__":
    print("Patrimonio de los 26 a los 33 años (M€ de hoy):")
    print(patrimonio_hasta_la_retirada().to_string(index=False))
    print("\nProbabilidad de llegar a los 95 según el gasto:")
    print(tabla_probabilidades().to_string(index=False))
    print("\nGasto sostenible según la confianza:")
    print(tabla_gasto_por_confianza().to_string(index=False))
    grafico_abanico()
    print("\nResultados guardados en", OUT)
