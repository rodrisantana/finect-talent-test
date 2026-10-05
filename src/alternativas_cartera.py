"""
¿POR QUÉ ESTOS PORCENTAJES Y NO OTROS?  Comparación de la cartera propuesta con alternativas.

Uso:  python src/alternativas_cartera.py
Crea: resultados/alternativas/*.csv y *.png

QUÉ SE HIZO (y qué NO) EN LA ELECCIÓN DE LOS PESOS
--------------------------------------------------
Los pesos (40 % renta variable, 30 % renta fija, 15 % monetario, 7 % infraestructuras, 8 % oro)
NO salen de un optimizador. Se eligieron con criterios de sentido común:
  * liquidez: 15 % en monetario para cubrir una lesión sin vender en mal momento,
  * poca renta variable para un cliente cuyos ingresos ya son muy arriesgados,
  * diversificadores (oro, infraestructuras) con poco peso,
  * productos baratos y simples.
Después se CONTRASTARON con simulaciones: este script compara la propuesta con 14 alternativas
usando tres pruebas distintas.
  1. Hipótesis a largo plazo de J.P. Morgan (rentabilidad, volatilidad y correlaciones).
  2. Simulación Monte Carlo del plan completo (gasto sostenible con 90 % y 95 % de confianza,
     y gasto sostenible si una lesión le retira a los 29).
  3. Backtest con datos reales de 2006 a 2026 (caída máxima en 2008 y en 2022).
Además se comprueba dónde queda la propuesta frente a la "frontera eficiente" (las carteras que
dan la máxima rentabilidad para cada nivel de riesgo).
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import modelo_plan as mp
import backtest_historico as bh
import graficos as g

g.aplicar_estilo()
RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "resultados" / "alternativas"
OUT.mkdir(parents=True, exist_ok=True)

LTCMA = json.load(open(RAIZ / "datos" / "ltcma_2026_eur.json", encoding="utf-8"))
EST = LTCMA["estadisticas"]      # clase: [compuesta %, aritmética %, volatilidad %, -]
CORR = LTCMA["correlaciones"]

# Cada cartera: pesos por bloque. "tipo" indica cómo se reparte la renta variable:
#   propuesta = 85 % mundo desarrollado + 15 % emergentes (como la nuestra)
#   mundial   = un solo índice de renta variable global
CARTERAS = {
    "Propuesta":                   dict(rv=.40, rf=.30, mon=.15, infra=.07, oro=.08, tipo="propuesta"),
    "Renta variable 30 %":         dict(rv=.30, rf=.40, mon=.15, infra=.07, oro=.08, tipo="propuesta"),
    "Renta variable 50 %":         dict(rv=.50, rf=.20, mon=.15, infra=.07, oro=.08, tipo="propuesta"),
    "Renta variable 60 %":         dict(rv=.60, rf=.10, mon=.15, infra=.07, oro=.08, tipo="propuesta"),
    "Sin oro":                     dict(rv=.40, rf=.38, mon=.15, infra=.07, oro=0.0, tipo="propuesta"),
    "Sin infraestructuras":        dict(rv=.47, rf=.30, mon=.15, infra=0.0, oro=.08, tipo="propuesta"),
    "Sin monetario":               dict(rv=.40, rf=.45, mon=0.0, infra=.07, oro=.08, tipo="propuesta"),
    "20/80":                       dict(rv=.20, rf=.80, mon=0.0, infra=0.0, oro=0.0, tipo="mundial"),
    "40/60":                       dict(rv=.40, rf=.60, mon=0.0, infra=0.0, oro=0.0, tipo="mundial"),
    "60/40":                       dict(rv=.60, rf=.40, mon=0.0, infra=0.0, oro=0.0, tipo="mundial"),
    "80/20":                       dict(rv=.80, rf=.20, mon=0.0, infra=0.0, oro=0.0, tipo="mundial"),
    "100 % renta variable":        dict(rv=1.0, rf=0.0, mon=0.0, infra=0.0, oro=0.0, tipo="mundial"),
}


def pesos_ltcma(c):
    rv = c["rv"]
    w = ({"Developed World Equity": .85 * rv, "Emerging Markets Equity": .15 * rv}
         if c["tipo"] == "propuesta" else {"AC World Equity": rv})
    w.update({"Global Multiverse Bonds hedged": c["rf"], "Euro Cash": c["mon"],
              "Global Core Infrastructure": c["infra"], "Gold": c["oro"]})
    return {k: v for k, v in w.items() if v > 0}


def pesos_backtest(c):
    rv = c["rv"]
    w = ({"msci_world": .75 * rv, "msci_em": .15 * rv, "msci_world_small": .10 * rv}
         if c["tipo"] == "propuesta" else {"msci_world": rv})
    w.update({"renta_fija": c["rf"], "monetario": c["mon"], "infraestructuras": c["infra"], "oro": c["oro"]})
    return {k: v for k, v in w.items() if v > 0}


def estadisticas_ltcma(w):
    """Rentabilidad compuesta y volatilidad de una cartera con las hipótesis de J.P. Morgan."""
    n = list(w)
    pesos = np.array([w[k] for k in n])
    media = np.array([EST[k][1] for k in n]) / 100          # rentabilidad aritmética de cada activo
    vol = np.array([EST[k][2] for k in n]) / 100
    corr = np.array([[CORR[a][b] for b in n] for a in n])
    cov = np.outer(vol, vol) * corr                          # matriz de covarianzas
    varianza = pesos @ cov @ pesos
    return float(pesos @ media - varianza / 2), float(np.sqrt(varianza))   # compuesta = media - varianza/2


def evaluar():
    r = bh.cargar_rentabilidades()
    filas = []
    for nombre, c in CARTERAS.items():
        comp, vol = estadisticas_ltcma(pesos_ltcma(c))
        v, _ = bh.simular(r, pesos_backtest(c))
        m = bh.metricas(v, r["monetario"])
        kw = dict(bruto=comp, vol=vol, vender_inmuebles=True)
        fila = {
            "cartera": nombre,
            "rent_compuesta_LTCMA_%": round(comp * 100, 2),
            "volatilidad_LTCMA_%": round(vol * 100, 2),
            "gasto_central_€": round(mp.gasto_sostenible(None, bruto=comp, vender_inmuebles=True) * 1e6, -3),
            "gasto_90%_€": round(mp.gasto_sostenible(.90, **kw) * 1e6, -3),
            "gasto_95%_€": round(mp.gasto_sostenible(.95, **kw) * 1e6, -3),
            "gasto_90%_si_lesion_29_€": round(mp.gasto_sostenible(.90, edad_retirada=29, **kw) * 1e6, -3),
            "backtest_TAE_%": round(m["Rentabilidad anual (TAE)"] * 100, 1),
            "backtest_vol_%": round(m["Volatilidad anual"] * 100, 1),
            "backtest_caida_max_%": round(m["Caída máxima"] * 100, 1),
            "backtest_2022_%": round(bh.dd_periodo(v, "2021-12", "2022-12") * 100, 1),
        }
        filas.append(fila)
        print(f"  {nombre:24s} vol {fila['volatilidad_LTCMA_%']:5.2f}  gasto 90 %: {fila['gasto_90%_€']:>9,.0f}  "
              f"caída máx. histórica {fila['backtest_caida_max_%']:6.1f} %")
    # La propuesta con la volatilidad prudente del 7,6 % que usa la presentación
    comp, _ = estadisticas_ltcma(pesos_ltcma(CARTERAS["Propuesta"]))
    prud = {"cartera": "Propuesta (volatilidad prudente 7,6 %, como en la presentación)",
            "rent_compuesta_LTCMA_%": round(comp * 100, 2), "volatilidad_LTCMA_%": 7.6,
            "gasto_central_€": round(mp.gasto_sostenible(None, bruto=comp, vender_inmuebles=True) * 1e6, -3),
            "gasto_90%_€": round(mp.gasto_sostenible(.90, bruto=comp, vol=.076, vender_inmuebles=True) * 1e6, -3),
            "gasto_95%_€": round(mp.gasto_sostenible(.95, bruto=comp, vol=.076, vender_inmuebles=True) * 1e6, -3),
            "gasto_90%_si_lesion_29_€": round(mp.gasto_sostenible(.90, bruto=comp, vol=.076, edad_retirada=29, vender_inmuebles=True) * 1e6, -3)}
    filas.insert(1, prud)
    t = pd.DataFrame(filas)
    t.to_csv(OUT / "comparacion_carteras.csv", index=False)
    return t


def grafico_comparacion(t):
    d = t[~t["cartera"].str.contains("prudente")]
    fig, ax = plt.subplots(figsize=(9, 5))
    for _, f in d.iterrows():
        color = g.AZUL if f["cartera"] == "Propuesta" else (g.NARANJA if "/" in f["cartera"] or "100" in f["cartera"] else g.GRIS)
        ax.scatter(f["backtest_caida_max_%"], f["gasto_90%_€"] / 1000, s=90 if f["cartera"] == "Propuesta" else 50, color=color, zorder=3)
        ax.annotate(f["cartera"], (f["backtest_caida_max_%"], f["gasto_90%_€"] / 1000), xytext=(5, 4),
                    textcoords="offset points", fontsize=8)
    ax.set_xlabel("Caída máxima histórica 2006-2026 (%), más a la derecha = menos caída")
    ax.set_ylabel("Gasto anual sostenible con 90 % de confianza (miles de €)")
    ax.set_title("Más o menos gasto sostenible frente al riesgo de caída", loc="left", fontweight="bold")
    fig.tight_layout(); fig.savefig(OUT / "gasto_frente_a_caida.png"); plt.close(fig)


def frontera_eficiente():
    """Mil carteras al azar para ver dónde queda la propuesta frente al óptimo matemático."""
    activos = ["AC World Equity", "Global Multiverse Bonds hedged", "Euro Cash", "Global Core Infrastructure", "Gold"]
    etiquetas = ["Renta variable", "Renta fija", "Monetario", "Infraestructuras", "Oro"]
    media = np.array([EST[k][1] for k in activos]) / 100
    vol = np.array([EST[k][2] for k in activos]) / 100
    cov = np.outer(vol, vol) * np.array([[CORR[a][b] for b in activos] for a in activos])
    rng = np.random.default_rng(1)
    W = rng.dirichlet(np.ones(5), 300000)                     # 300.000 repartos al azar que suman 100 %
    var = np.einsum("ij,jk,ik->i", W, cov, W)
    comp, riesgo = W @ media - var / 2, np.sqrt(var)
    nuestra = np.array([.40, .30, .15, .07, .08])
    var_n = nuestra @ cov @ nuestra
    comp_n, riesgo_n = nuestra @ media - var_n / 2, np.sqrt(var_n)

    # Mejor cartera con el mismo riesgo y con liquidez >= 15 % (la restricción que nos importa)
    ok = (riesgo <= riesgo_n + 1e-4) & (W[:, 2] >= .15)
    i = np.argmax(np.where(ok, comp, -1))
    mejor = pd.DataFrame({"bloque": etiquetas, "propuesta_%": (nuestra * 100).round(0), "optimo_con_liquidez_15%_%": (W[i] * 100).round(0)})
    mejor.to_csv(OUT / "frontera_pesos.csv", index=False)
    resumen = {"rent_propuesta_%": round(comp_n * 100, 2), "vol_propuesta_%": round(riesgo_n * 100, 2),
               "rent_optimo_mismo_riesgo_%": round(comp[i] * 100, 2), "vol_optimo_%": round(riesgo[i] * 100, 2)}
    pd.Series(resumen).to_csv(OUT / "frontera_resumen.csv", header=["valor"])

    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.scatter(riesgo * 100, comp * 100, s=2, color=g.GRIS, alpha=0.15, label="300.000 repartos al azar")
    ax.scatter(riesgo_n * 100, comp_n * 100, s=110, color=g.AZUL, zorder=4, label="Propuesta")
    ax.scatter(riesgo[i] * 100, comp[i] * 100, s=110, color=g.VERDE, zorder=4, marker="D",
               label="Máxima rentabilidad al mismo riesgo (con 15 % de liquidez)")
    clasica = [(c.copy()) for c in [np.array([x, 1 - x, 0, 0, 0]) for x in np.linspace(0, 1, 11)]]
    cl = np.array(clasica); vc = np.einsum("ij,jk,ik->i", cl, cov, cl)
    ax.plot(np.sqrt(vc) * 100, (cl @ media - vc / 2) * 100, color=g.NARANJA, lw=2, label="Mezclas clásicas renta variable / renta fija")
    ax.set_xlabel("Volatilidad esperada (%)"); ax.set_ylabel("Rentabilidad compuesta esperada (%)")
    ax.set_title("Dónde queda la propuesta frente al óptimo matemático (hipótesis J.P. Morgan 2026)", loc="left", fontweight="bold", fontsize=10)
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    fig.tight_layout(); fig.savefig(OUT / "frontera_eficiente.png"); plt.close(fig)
    return mejor, resumen


if __name__ == "__main__":
    print("Evaluando carteras (puede tardar un par de minutos)...")
    t = evaluar()
    grafico_comparacion(t)
    print("\n", t.to_string(index=False))
    mejor, resumen = frontera_eficiente()
    print("\nFrontera eficiente:", resumen)
    print(mejor.to_string(index=False))
    print("\nResultados guardados en", OUT)
