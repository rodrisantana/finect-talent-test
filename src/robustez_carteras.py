"""
¿POR QUÉ UN 40 % DE RENTA VARIABLE Y NO UN 30 % (U OTRO)?  Pruebas de robustez.

Uso:  python src/robustez_carteras.py
Crea: resultados/robustez/robustez_carteras.csv

La comparación de `alternativas_cartera.py` mira el gasto sostenible con 90 % y 95 % de
confianza y la caída histórica. Aquí se añaden pruebas que miran qué pasa cuando las cosas
salen peor de lo previsto, y cuánto patrimonio deja cada cartera:

  1. Probabilidad de éxito con 550.000 y con 600.000 € de gasto anual.
  2. Patrimonio mediano y patrimonio en el 10 % de peores escenarios a los 95 años.
  3. Gasto sostenible al 90 % si la rentabilidad real es un punto peor que la prevista.
  4. Gasto sostenible al 90 % si la inflación es del 3 % en lugar del 2 %.
  5. Gasto sostenible al 90 % si hay que llegar a los 100 años en lugar de a los 95.
  6. PRUEBA DE ESTRÉS: la crisis de 2007 a 2009 justo al retirarse (a los 33, 34 y 35), con los
     rendimientos históricos reales de cada cartera, y después la rentabilidad esperada.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import modelo_plan as mp
import backtest_historico as bh
import alternativas_cartera as alt

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "resultados" / "robustez"
OUT.mkdir(parents=True, exist_ok=True)

CARTERAS_A_PROBAR = ["Propuesta", "Renta variable 30 %", "Renta variable 50 %", "Renta variable 60 %", "40/60", "60/40"]


def rentabilidades_naturales(v, anios=(2007, 2008, 2009)):
    """Rentabilidad de cada año natural a partir de la serie de valor de la cartera."""
    anual = v[v.index.month == 12].pct_change().dropna()
    return {a: float(anual[anual.index.year == a].iloc[0]) for a in anios}


def evaluar_cartera(nombre, r):
    c = alt.CARTERAS[nombre]
    comp, vol = alt.estadisticas_ltcma(alt.pesos_ltcma(c))
    kw = dict(bruto=comp, vol=vol, vender_inmuebles=True)
    v, _ = bh.simular(r, alt.pesos_backtest(c))
    nat = rentabilidades_naturales(v)

    _, tray, _ = mp.simular(0.55, n=20000, **kw)
    final = tray[:, -1]                                   # patrimonio financiero a los 95 años, M€ de hoy

    central = mp.gasto_sostenible(None, bruto=comp, vender_inmuebles=True)
    crisis = {33: nat[2007], 34: nat[2008], 35: nat[2009]}
    central_crisis = mp.gasto_sostenible(None, bruto=comp, vender_inmuebles=True, rend_forzado=crisis)
    return {
        "cartera": nombre,
        "rent_compuesta_LTCMA_%": round(comp * 100, 2),
        "volatilidad_LTCMA_%": round(vol * 100, 2),
        "prob_éxito_gasto_550.000_%": round(mp.probabilidad_exito(0.55, **kw) * 100, 1),
        "prob_éxito_gasto_600.000_%": round(mp.probabilidad_exito(0.60, **kw) * 100, 1),
        "patrimonio_mediano_a_los_95_M€": round(float(np.median(final)), 1),
        "patrimonio_en_el_10%_peor_M€": round(float(np.percentile(final, 10)), 1),
        "gasto_90%_base_€": round(mp.gasto_sostenible(.90, **kw) * 1e6, -3),
        "gasto_90%_rentabilidad_1_punto_menor_€": round(mp.gasto_sostenible(.90, **{**kw, "bruto": comp - 0.01}) * 1e6, -3),
        "gasto_90%_inflación_3%_€": round(mp.gasto_sostenible(.90, inflacion=0.03, **kw) * 1e6, -3),
        "gasto_90%_hasta_los_100_€": round(mp.gasto_sostenible(.90, edad_objetivo=100, **kw) * 1e6, -3),
        "gasto_central_sin_crisis_€": round(central * 1e6, -3),
        "gasto_central_con_crisis_2008_al_retirarse_€": round(central_crisis * 1e6, -3),
        "pérdida_por_la_crisis_%": round((1 - central_crisis / central) * 100, 1),
        "rent_2007_2008_2009_%": " / ".join(f"{nat[a] * 100:.1f}" for a in (2007, 2008, 2009)),
    }


if __name__ == "__main__":
    r = bh.cargar_rentabilidades()
    filas = []
    for nombre in CARTERAS_A_PROBAR:
        print("Evaluando", nombre, "...")
        filas.append(evaluar_cartera(nombre, r))
    t = pd.DataFrame(filas)
    t.to_csv(OUT / "robustez_carteras.csv", index=False)
    print("\n", t.T.to_string(header=False))
    print("\nResultados guardados en", OUT)
