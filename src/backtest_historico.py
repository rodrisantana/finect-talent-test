"""
Backtest histórico de la cartera financiera propuesta (Finect Talent 2026, Caso A, Equipo 1 UCM).

Uso:  python src/backtest_historico.py
Lee   datos/indices_eur_mensual.csv  (niveles mensuales de índices de rentabilidad total en euros)
Crea  resultados/backtest/*.csv y resultados/backtest/*.png

QUÉ ES UN BACKTEST: coger los datos reales del pasado y ver cómo se habría comportado la cartera
si la hubiéramos tenido. No predice el futuro, pero comprueba que la cartera no se rompe en las
crisis reales (2008, 2020, 2022). Aquí sirve para contrastar las cifras de riesgo de la presentación.

Supuestos:
- Periodo: nov-2006 a ago-2026 (limitado por el inicio de la serie de infraestructuras).
- Rentabilidades de índices, en euros, con dividendos reinvertidos. La versión "neta" resta
  un 0,9 % anual de costes (fondos 0,22 % + contrato y custodia ~0,4 % + asesoramiento 0,3 %).
- Rebalanceo: cada diciembre y, además, cualquier mes en que un activo se desvíe más de
  5 puntos de su peso objetivo.
- Renta fija: FTSE WGBI cubierto a euros hasta abr-2019 y, desde may-2019, el índice que replica
  el fondo Vanguard Global Bond Index (Bloomberg Global Aggregate Float Adjusted and Scaled, cubierto).
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "resultados" / "backtest"
OUT.mkdir(parents=True, exist_ok=True)

COSTE_ANUAL = 0.009
BANDA = 0.05

CARTERAS = {
    "Cartera propuesta": {
        "msci_world": 0.30, "msci_em": 0.06, "msci_world_small": 0.04,   # 40 % renta variable
        "renta_fija": 0.30, "monetario": 0.15,
        "infraestructuras": 0.07, "oro": 0.08,
    },
    "60/40 global": {"msci_world": 0.60, "renta_fija": 0.40},
    "100 % MSCI World": {"msci_world": 1.00},
}

NOMBRES = {
    "msci_world": "MSCI World", "msci_em": "MSCI Emergentes", "msci_world_small": "MSCI World Small Cap",
    "renta_fija": "Renta fija global cubierta", "monetario": "Monetario euro",
    "infraestructuras": "Infraestructuras cotizadas", "oro": "Oro",
}

CRISIS = {
    "Crisis financiera (jun-2007 a dic-2009)": ("2007-06", "2009-12"),
    "Crisis deuda euro (2011)": ("2011-01", "2011-12"),
    "COVID (ene-jun 2020)": ("2020-01", "2020-06"),
    "Subida de tipos (2022)": ("2021-12", "2022-12"),
}


# ---------------------------------------------------------------- datos
def cargar_rentabilidades() -> pd.DataFrame:
    lv = pd.read_csv(RAIZ / "datos" / "indices_eur_mensual.csv", index_col="mes")
    lv = lv.loc[lv["ftse_global_core_infra"].first_valid_index():]
    r = lv.pct_change().iloc[1:]
    out = pd.DataFrame(index=r.index)
    out["msci_world"] = r["msci_world"]
    out["msci_em"] = r["msci_em"]
    out["msci_world_small"] = r["msci_world_small"]
    out["renta_fija"] = r["bbg_global_agg_fas_hedged_eur"].fillna(r["ftse_wgbi_hedged_eur"])
    out["monetario"] = r["euro_overnight"]
    out["infraestructuras"] = r["ftse_global_core_infra"]
    out["oro"] = r["gold_eur"]
    out.index = pd.PeriodIndex(out.index, freq="M")
    assert not out.isna().any().any()
    return out


# ---------------------------------------------------------------- simulación
def simular(r: pd.DataFrame, pesos: dict, coste=0.0, banda=BANDA, rebalanceo="anual+banda"):
    """Devuelve serie de valor (base 100) y nº de rebalanceos."""
    w = pd.Series(pesos)
    tenencia = w * 100.0
    coste_m = (1 + coste) ** (1 / 12) - 1
    valores, n_reb = [], 0
    for mes, fila in r.iterrows():
        tenencia = tenencia * (1 + fila[w.index]) * (1 - coste_m)
        v = tenencia.sum()
        valores.append(v)
        desvio = (tenencia / v - w).abs().max()
        toca = (rebalanceo == "mensual") or \
               (rebalanceo == "anual+banda" and (mes.month == 12 or desvio > banda)) or \
               (rebalanceo == "anual" and mes.month == 12)
        if toca and rebalanceo != "nunca":
            tenencia = w * v
            n_reb += 1
    s = pd.Series(valores, index=r.index)
    inicio = pd.Series([100.0], index=[r.index[0] - 1])
    return pd.concat([inicio, s]), n_reb


# ---------------------------------------------------------------- métricas
def max_dd(v: pd.Series):
    pico = v.cummax()
    dd = v / pico - 1
    fondo = dd.idxmin()
    inicio = v.loc[:fondo].idxmax()
    rec = v.loc[fondo:][v.loc[fondo:] >= v.loc[inicio]]
    fin = rec.index[0] if len(rec) else None
    meses = (fin - inicio).n if fin is not None else None
    return dd.min(), inicio, fondo, fin, meses


def dd_periodo(v, a, b):
    a, b = pd.Period(a, "M"), pd.Period(b, "M")
    tramo = v.loc[:b]
    dd = tramo / tramo.cummax() - 1
    return dd.loc[a:b].min()


def metricas(v: pd.Series, rf: pd.Series):
    r = v.pct_change().dropna()
    anos = len(r) / 12
    cagr = (v.iloc[-1] / v.iloc[0]) ** (1 / anos) - 1
    vol = r.std(ddof=1) * np.sqrt(12)
    exc = r - rf.loc[r.index]
    sharpe = exc.mean() * 12 / vol
    neg = exc[exc < 0]
    sortino = exc.mean() * 12 / (np.sqrt((neg ** 2).sum() / len(exc)) * np.sqrt(12))
    mdd, ini, fondo, fin, meses = max_dd(v)
    anual = v[v.index.month == 12]
    cal = anual.pct_change().dropna()
    var5 = r.quantile(0.05)
    cvar5 = r[r <= var5].mean()
    roll5 = (v / v.shift(60)) ** (1 / 5) - 1
    return {
        "Rentabilidad anual (TAE)": cagr,
        "Volatilidad anual": vol,
        "Ratio de Sharpe": sharpe,
        "Ratio de Sortino": sortino,
        "Caída máxima": mdd,
        "Inicio caída máxima": str(ini),
        "Mínimo": str(fondo),
        "Meses hasta recuperar": meses,
        "Peor año natural": cal.min(),
        "Año del peor": int(cal.idxmin().year),
        "Mejor año natural": cal.max(),
        "Años en negativo": f"{(cal < 0).sum()} de {len(cal)}",
        "Peor mes": r.min(),
        "CVaR 95 % mensual": cvar5,
        "Peor rentabilidad anualizada a 5 años": roll5.min(),
        "% de ventanas de 5 años en positivo": (roll5.dropna() > 0).mean(),
    }


def fmt(k, x):
    if isinstance(x, (float, np.floating)) and ("Ratio" not in k):
        return f"{x * 100:,.1f} %".replace(".", ",")
    if isinstance(x, (float, np.floating)):
        return f"{x:,.2f}".replace(".", ",")
    return x


# ---------------------------------------------------------------- gráficos
plt.rcParams.update({
    "font.family": ["Roboto", "Lexend", "Poppins", "DejaVu Sans"], "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.alpha": 0.25, "figure.dpi": 150,
})
COL = {"Cartera propuesta": "#1f3b8c", "Cartera propuesta (neta de costes)": "#1f3b8c",
       "60/40 global": "#d9822b", "100 % MSCI World": "#9aa0a6"}


def eje_fechas(ax, idx):
    x = idx.to_timestamp()
    return x


def grafico_evolucion(series):
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for n, v in series.items():
        ls = "--" if "neta" in n else "-"
        ax.plot(v.index.to_timestamp(), v.values, ls, color=COL[n], lw=2 if "propuesta" in n else 1.4, label=n)
    ax.set_yscale("log")
    ax.set_yticks([70, 100, 150, 200, 300, 500]); ax.set_yticklabels(["70", "100", "150", "200", "300", "500"]); ax.minorticks_off()
    ax.set_title("Evolución de 100 € invertidos (escala logarítmica, euros)", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(OUT / "evolucion.png"); plt.close(fig)


def grafico_drawdown(series):
    fig, ax = plt.subplots(figsize=(9, 3.8))
    for n, v in series.items():
        if "neta" in n:
            continue
        dd = (v / v.cummax() - 1) * 100
        ax.fill_between(dd.index.to_timestamp(), dd.values, 0, color=COL[n], alpha=0.35 if "propuesta" in n else 0.15,
                        label=n, lw=0)
        ax.plot(dd.index.to_timestamp(), dd.values, color=COL[n], lw=1)
    ax.set_title("Caída desde máximos (%)", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="lower left")
    fig.tight_layout(); fig.savefig(OUT / "caidas.png"); plt.close(fig)


def grafico_anual(series):
    nombres = ["Cartera propuesta", "60/40 global"]
    cal = pd.DataFrame({n: series[n][series[n].index.month == 12].pct_change().dropna() * 100 for n in nombres})
    cal.index = cal.index.year
    fig, ax = plt.subplots(figsize=(9, 3.8))
    x = np.arange(len(cal)); w = 0.4
    for i, n in enumerate(nombres):
        ax.bar(x + (i - 0.5) * w, cal[n], w, color=COL[n], label=n)
    ax.set_xticks(x); ax.set_xticklabels(cal.index, rotation=90)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_title("Rentabilidad por año natural (%)", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(OUT / "anual.png"); plt.close(fig)
    return cal


def grafico_rolling(series):
    fig, ax = plt.subplots(figsize=(9, 3.6))
    for n in ["Cartera propuesta", "60/40 global"]:
        v = series[n]; r5 = ((v / v.shift(60)) ** (1 / 5) - 1).dropna() * 100
        ax.plot(r5.index.to_timestamp(), r5.values, color=COL[n], lw=1.8, label=n)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_title("Rentabilidad anualizada en ventanas móviles de 5 años (%)", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(OUT / "ventanas_5_anos.png"); plt.close(fig)


# ---------------------------------------------------------------- principal
def main():
    r = cargar_rentabilidades()
    rf = r["monetario"]
    print(f"Periodo: {r.index[0]} a {r.index[-1]} ({len(r)} meses)")

    series, nreb = {}, {}
    for n, w in CARTERAS.items():
        series[n], nreb[n] = simular(r, w)
    series["Cartera propuesta (neta de costes)"], _ = simular(r, CARTERAS["Cartera propuesta"], coste=COSTE_ANUAL)

    # Tabla principal
    tabla = pd.DataFrame({n: metricas(v, rf) for n, v in series.items()})
    tabla_fmt = tabla.apply(lambda c: [fmt(k, x) for k, x in zip(tabla.index, c)])
    tabla_fmt.to_csv(OUT / "metricas.csv")
    print("\n", tabla_fmt.to_string())
    print("\nRebalanceos:", nreb)

    # Crisis
    crisis = pd.DataFrame({n: {c: dd_periodo(v, a, b) for c, (a, b) in CRISIS.items()} for n, v in series.items()})
    (crisis * 100).round(1).to_csv(OUT / "crisis.csv")
    print("\nCaída máxima en cada crisis (%):\n", (crisis * 100).round(1).to_string())

    # Activos sueltos y correlaciones
    act = pd.DataFrame({NOMBRES[k]: {
        "Rentabilidad anual": (1 + r[k]).prod() ** (12 / len(r)) - 1,
        "Volatilidad": r[k].std() * np.sqrt(12),
        "Caída máxima": max_dd(pd.concat([pd.Series([1.0]), (1 + r[k]).cumprod()]).set_axis(series["Cartera propuesta"].index))[0],
    } for k in r.columns}).T
    (act * 100).round(1).to_csv(OUT / "activos.csv")
    corr = r.rename(columns=NOMBRES).corr().round(2)
    corr.to_csv(OUT / "correlaciones.csv")
    print("\nActivos (%):\n", (act * 100).round(1).to_string())
    print("\nCorrelaciones:\n", corr.to_string())

    # Sensibilidad a la regla de rebalanceo
    sens = {}
    for reg in ["anual+banda", "anual", "mensual", "nunca"]:
        v, k = simular(r, CARTERAS["Cartera propuesta"], rebalanceo=reg)
        m = metricas(v, rf)
        sens[reg] = {"TAE": m["Rentabilidad anual (TAE)"], "Volatilidad": m["Volatilidad anual"],
                     "Caída máxima": m["Caída máxima"], "Rebalanceos": k}
    sens = pd.DataFrame(sens).T
    for c in ["TAE", "Volatilidad", "Caída máxima"]:
        sens[c] = (sens[c].astype(float) * 100).round(1)
    sens["Rebalanceos"] = sens["Rebalanceos"].astype(int)
    sens.to_csv(OUT / "sensibilidad_rebalanceo.csv")
    print("\nSensibilidad a la regla de rebalanceo:\n", sens.to_string())

    # Contribución de cada bloque a la rentabilidad (aprox. pesos objetivo x rentabilidad media)
    w = pd.Series(CARTERAS["Cartera propuesta"])
    contrib = (r[w.index].mean() * 12 * w).rename(index=NOMBRES)
    (contrib * 100).round(2).to_csv(OUT / "contribucion.csv", header=["puntos % anuales"])

    # Series y gráficos
    pd.DataFrame({n: v for n, v in series.items()}).round(3).to_csv(OUT / "series_base100.csv")
    grafico_evolucion(series)
    grafico_drawdown(series)
    cal = grafico_anual(series)
    cal.round(1).to_csv(OUT / "rentabilidad_anual.csv")
    grafico_rolling(series)
    print("\nGráficos y tablas guardados en", OUT)


if __name__ == "__main__":
    main()
