"""Cifras y gráficos de la versión final (tras la mentoría). TODO EN EUROS DE HOY.
Uso: python v2/resultados_v5.py   (unos 5 minutos)

Convención: hoy = inicio de los 26 años. "A los 33" = final de los 32 (7 años de inflación del 2 %).
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import modelo_v2 as M
import ltcma_v2 as L

OUT = Path(__file__).resolve().parent / "resultados"
OUT.mkdir(exist_ok=True)
for f in Path("/root/.fonts").glob("Montserrat*.ttf"):
    fm.fontManager.addfont(str(f))
plt.rcParams.update({"font.family": "Montserrat", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 220})
NAVY, BLUE, ORANGE, LILAC, LIL2, PEACH, GREY, GOLD = "#14163A", "#3C44D7", "#FF8041", "#ECEBFD", "#8A90E8", "#FDE6DA", "#6B6E80", "#D9A441"
N = 20000
E = list(M.EDADES)
KW = dict(regla_flexible=True)
R = {}
fmt = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
r0 = lambda x: int(np.floor(x + 0.5))
DEF = np.array([1.02 ** (a - 26 + 1) for a in E])      # deflactor del final de cada año


def real(x):
    return x / DEF


# ---------------- gasto
R["gasto_90"] = M.gasto_sostenible(0.90, n=N, **KW)
GASTO = round(R["gasto_90"], 1)
R["prob_gasto"] = {g: float(M.simular(g, n=N, **KW)["vivo"].mean()) for g in (0.9, 1.0, 1.1, 1.2, 1.3, 1.5)}
R["gasto_90_fijo"] = M.gasto_sostenible(0.90, n=N)
R["gasto_90_6040"] = M.gasto_sostenible(0.90, n=N, carteras={k: {"dev": .6, "multi": .4} for k in M.CARTERAS}, **KW)
old = {"dev": .34, "em": .06, "multi": .30, "cash": .15, "infra": .07, "gold": .08}
R["gasto_90_cartera_v1"] = M.gasto_sostenible(0.90, n=N, carteras={k: old for k in M.CARTERAS}, **KW)
R["gasto_90_sin_pisos_extra"] = M.gasto_sostenible(0.90, n=N, compras_pisos=(), objetivo_inmuebles=0.40, **KW)
R["lesion28_con_plan"] = M.gasto_sostenible(0.90, n=N, lesion_edad=28, **KW)
R["lesion28_sin_plan"] = M.gasto_sostenible(0.90, n=N, lesion_edad=28, con_seguro=False, con_colchon=False, **KW)
R["residencia_FR"] = M.gasto_sostenible(0.90, n=N, residencia_retiro="FR", **KW)

# ---------------- patrimonio (euros de hoy)
t = M.simular(GASTO, n=N, **KW)
W = real(t["W"])
j33, j35, j95 = E.index(32), E.index(34), E.index(94)   # "a los X" = final de los X-1
pct = {q: np.percentile(W, q, axis=0) for q in (10, 25, 50, 75, 90)}
R["patrimonio_33"] = {k: float(pct[q][j33]) for k, q in (("negativo", 10), ("realista", 50), ("optimista", 90))}
R["patrimonio_95"] = {k: float(pct[q][j95]) for k, q in (("negativo", 10), ("realista", 50), ("optimista", 90))}
R["patrimonio_33_nominal_realista"] = float(np.median(t["W"][:, j33]))
t2 = M.simular(GASTO, n=N, bruto_segunda=3.0, **KW)
R["patrimonio_33_segunda_mitad"] = float(np.median(real(t2["W"])[:, j33]))
comp = {}
for k in ("P", "F", "C", "A"):
    comp[k] = np.median(real(t[k]), axis=0)
tot = sum(comp.values())
for k in comp:
    comp[k] = comp[k] / tot * pct[50]                      # componentes escalados a la mediana del patrimonio
R["composicion"] = {a: {k: float(comp[k][E.index(a - 1)]) for k in comp} for a in (27, 31, 33, 35, 40)}   # a los a
R["pisos_hoy"] = 14.0
R["pisos_35"] = float(comp["P"][j35])
R["inmuebles_35"] = float(np.median((t["P"][:, j35] + 0.15 * t["F"][:, j35]) / t["W"][:, j35]))
R["pisos_al_volver"] = float(np.median(t["P"][:, E.index(33)]) - np.median(t["P"][:, j33]) * 1.025)
R["gasto_acumulado_33_95"] = float(GASTO * (95 - 33 + 1))

# ---------------- carteras
R["carteras"] = {}
for k, w in M.CARTERAS.items():
    c, v = L.stats(w)
    R["carteras"][k] = dict(rentabilidad=c, volatilidad=v, peor_anio_1_de_20=float(np.expm1(np.log1p(c) - 1.645 * v)), pesos=w)
c6040, v6040 = L.stats({"dev": .6, "multi": .4}); R["vol_6040"] = v6040

# ---------------- primer año (euros de hoy = euros de este año)
neto = M.neto_francia(13.6); cot = 13.6 * 0.85 / 8; irpf = 13.6 * 2.6 / 8
prima = 0.0125 * 27; soli = float(M.itsgf(np.array([14.0]))[0]); alq = 14 * 0.05 * 0.75 * 0.81
R["cascada"] = dict(cotizaciones=cot, impuesto=irpf, sin155=13.6 * 3.6 / 8, neto=neto, prima=prima, solidaridad=soli,
                    alquiler=alq, invierte=neto - 1.5 - prima - soli + alq)
json.dump(R, open(OUT / "cifras_v5.json", "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps({k: v for k, v in R.items() if k not in ("carteras", "composicion")}, indent=1, default=float, ensure_ascii=False))
print("composicion", json.dumps(R["composicion"], default=float))

print("cifras ok; gráficos: python v2/graficos_v5.py")
