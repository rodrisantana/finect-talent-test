"""Cifras y gráficos del plan v2 (para la presentación). Uso: python v2/resultados_v2.py"""
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

# ---------------- cifras
R["neto_anual"] = M.neto_francia(13.6)
R["gasto_90"] = M.gasto_sostenible(0.90, n=N, **KW)
R["gasto_75"] = M.gasto_sostenible(0.75, n=N, **KW)
R["gasto_50"] = M.gasto_sostenible(0.50, n=N, **KW)
GASTO = round(R["gasto_90"], 1)                       # presupuesto de por vida que presentamos
t = M.simular(GASTO, n=N, **KW)
R["prob_gasto"] = {g: float(M.simular(g, n=N, **KW)["vivo"].mean()) for g in (0.9, 1.0, 1.1, 1.2, 1.3, 1.5)}
W = t["W"]
R["patrimonio_33"] = dict(zip(("negativo", "realista", "optimista"), np.percentile(W[:, E.index(32)], [10, 50, 90]).round(1).tolist()))
R["patrimonio_95_real"] = dict(zip(("negativo", "realista", "optimista"),
                                   (np.percentile(W[:, -1], [10, 50, 90]) / 1.02 ** 69).round(1).tolist()))
R["patrimonio_33_real_mediana"] = float(np.median(W[:, E.index(32)]) / 1.02 ** 6)
old = {"dev": .34, "em": .06, "multi": .30, "cash": .15, "infra": .07, "gold": .08}
R["gasto_90_cartera_antigua"] = M.gasto_sostenible(0.90, n=N, carteras={k: old for k in M.CARTERAS}, **KW)
R["gasto_90_6040"] = M.gasto_sostenible(0.90, n=N, carteras={k: {"dev": .6, "multi": .4} for k in M.CARTERAS}, **KW)
R["lesion28_con_plan"] = M.gasto_sostenible(0.90, n=N, lesion_edad=28, **KW)
R["lesion28_sin_plan"] = M.gasto_sostenible(0.90, n=N, lesion_edad=28, con_seguro=False, con_colchon=False, **KW)
R["compra_5M_ya"] = M.gasto_sostenible(0.90, n=N, compra_ya=5.0, **KW)
R["residencia_FR"] = M.gasto_sostenible(0.90, n=N, residencia_retiro="FR", **KW)
R["gasto_90_fijo"] = M.gasto_sostenible(0.90, n=N)
R["carteras"] = {}
for k, w in M.CARTERAS.items():
    c, v = L.stats(w)
    R["carteras"][k] = dict(rentabilidad=c, volatilidad=v, peor_anio_1_de_20=float(np.expm1(np.log1p(c) - 1.645 * v)), pesos=w)
re_share = np.median((t["P"] + 0.15 * t["F"]) / W, axis=0)
R["peso_inmuebles"] = {a: float(re_share[E.index(a)]) for a in range(26, 41)}
R["pisos_mediana"] = {a: float(np.median(t["P"][:, E.index(a)])) for a in (32, 33)}
json.dump(R, open(OUT / "cifras_v2.json", "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps({k: v for k, v in R.items() if k not in ("carteras", "peso_inmuebles")}, indent=1, default=float, ensure_ascii=False))

fmt = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------- 1. escenarios del patrimonio (26-40, nominal)
edades0 = np.arange(26, 40); js = [E.index(a) for a in edades0]
p10, p25, p50, p75, p90 = (np.concatenate([[20.0], np.percentile(W[:, js], q, axis=0)]) for q in (10, 25, 50, 75, 90))
edades = np.arange(26, 41)
fig, ax = plt.subplots(figsize=(6.2, 3.4))
ax.fill_between(edades, p10, p90, color=LILAC, label="Entre el escenario negativo y el optimista")
ax.plot(edades, p90, color=BLUE, lw=1.6, label="Optimista")
ax.plot(edades, p50, color=ORANGE, lw=2.6, label="Realista")
ax.plot(edades, p10, color=NAVY, lw=1.6, label="Negativo")
i33 = edades.tolist().index(33)
for y, c, dy in ((p90, BLUE, 8), (p50, ORANGE, 8), (p10, NAVY, -12)):
    ax.annotate(f"{fmt(y[i33],0)} M€", (33, y[i33]), xytext=(-4, dy), textcoords="offset points", ha="right",
                color=c, fontweight="bold", va="center", fontsize=9)
    ax.plot([33], [y[i33]], "o", color=c, ms=4)
ax.axvline(33, color=GREY, lw=0.8, ls="--"); ax.text(33.15, 6, "retirada (33)", color=GREY, fontsize=8)
ax.set_xlim(26, 40); ax.set_ylim(0, None); ax.set_ylabel("M€"); ax.set_xlabel("Edad")
ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig(OUT / "g1_patrimonio_escenarios.png", transparent=True); plt.close(fig)

# ---------------- 2. probabilidad según el gasto
gs = sorted(R["prob_gasto"]); ps = [R["prob_gasto"][g] * 100 for g in gs]
fig, ax = plt.subplots(figsize=(5.2, 2.6))
cols = [ORANGE if abs(g - GASTO) < 1e-9 else (GREY if g == 1.5 else LIL2) for g in gs]
ax.bar([fmt(g) for g in gs], ps, color=cols, width=0.6)
for i, p in enumerate(ps):
    ax.text(i, p + 1.5, f"{p:.0f} %", ha="center", fontsize=9, fontweight="bold", color=NAVY)
ax.set_ylim(0, 110); ax.set_yticks([]); ax.spines["left"].set_visible(False)
ax.set_xlabel("Gasto anual de por vida, M€ de hoy")
fig.tight_layout(); fig.savefig(OUT / "g2_prob_gasto.png", transparent=True); plt.close(fig)

# ---------------- 3. carteras por etapa
grupos = [("Renta variable", ("dev", "euro", "em"), NAVY), ("Inmobiliario cotizado", ("reits",), ORANGE),
          ("Renta fija", ("ig", "multi", "ilb", "govt"), LIL2), ("Oro", ("gold",), GOLD), ("Liquidez", ("cash",), "#C9CBF3")]
fig, ax = plt.subplots(figsize=(6.2, 2.6))
nombres = list(M.CARTERAS)[::-1]
for i, nom in enumerate(nombres):
    w = M.CARTERAS[nom]; left = 0
    for lab, ks, c in grupos:
        v = sum(w.get(k, 0) for k in ks)
        if v > 0:
            ax.barh(i, v * 100, left=left, color=c, height=0.62, label=lab if i == 0 else None)
            if v >= .05:
                ax.text(left + v * 50, i, f"{v*100:.0f} %", ha="center", va="center", fontsize=8.5,
                        color="white" if c in (NAVY, ORANGE, LIL2) else NAVY, fontweight="bold")
            left += v * 100
ax.set_yticks(range(len(nombres)), [f"{n}" for n in nombres], fontweight="bold")
ax.set_xlim(0, 100); ax.set_xticks([]); ax.spines["bottom"].set_visible(False); ax.spines["left"].set_visible(False)
ax.legend(ncol=5, frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.02), handlelength=1)
fig.tight_layout(); fig.savefig(OUT / "g3_carteras.png", transparent=True); plt.close(fig)

# ---------------- 4. peso de los inmuebles
a = np.arange(26, 41); v = [70.0] + [R["peso_inmuebles"][x] * 100 for x in range(26, 40)]
fig, ax = plt.subplots(figsize=(4.6, 2.7))
ax.plot(a, v, color=ORANGE, lw=2.6, marker="o", ms=3.5)
ax.axhline(40, color=BLUE, lw=1, ls="--"); ax.text(39.9, 41.5, "objetivo 40 %", color=BLUE, fontsize=8, ha="right")
ax.annotate("compra de pisos\nal volver a España", (34, v[8]), xytext=(34.6, 55), fontsize=8, color=NAVY,
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=.8))
ax.text(26.3, v[0] + 1, "hoy 70 %", fontsize=8.5, color=NAVY, fontweight="bold")
ax.set_ylim(20, 75); ax.set_ylabel("% del patrimonio"); ax.set_xlabel("Edad"); ax.grid(axis="y", alpha=.25)
fig.tight_layout(); fig.savefig(OUT / "g4_inmuebles.png", transparent=True); plt.close(fig)

# ---------------- 5. del bruto a lo que invierte (primer año)
neto = M.neto_francia(13.6); cot = 13.6 * 0.85 / 8; irpf = 13.6 * 2.6 / 8
prima = 0.0125 * 27; soli = float(M.itsgf(np.array([14.0]))[0]); alq = 14 * M.SUPUESTOS["rent_bruta_pisos"] * 0.75 * 0.81
ahorro = neto - 1.5 - prima - soli + alq
pasos = [("Sueldo\nbruto", 13.6, "t"), ("Cotiza-\nciones", -cot, "d"), ("Impuesto\n(155 B)", -irpf, "d"), ("Neto", neto, "t"),
         ("Gasto\nde vida", -1.5, "d"), ("Seguro", -prima, "d"), ("Solidaridad\npisos", -soli, "d"), ("Alquileres\nnetos", alq, "u"),
         ("Invierte", ahorro, "t")]
fig, ax = plt.subplots(figsize=(6.4, 3.0)); nivel = 0
for i, (lab, val, tp) in enumerate(pasos):
    if tp == "t":
        ax.bar(i, val, color=BLUE if lab not in ("Invierte",) else ORANGE, width=.62); nivel = val; y = val
    else:
        base = nivel + min(val, 0); ax.bar(i, abs(val), bottom=base, color=LIL2 if val < 0 else "#7FC79A", width=.62)
        nivel += val; y = max(nivel, nivel - val)
    ax.text(i, y + .25, fmt(val, 2 if abs(val) < 1 else 1), ha="center", fontsize=8, fontweight="bold", color=NAVY)
ax.set_xticks(range(len(pasos)), [p[0] for p in pasos], fontsize=7.2, rotation=0, wrap=True)
for lbl in ax.get_xticklabels(): lbl.set_text(lbl.get_text())
ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.set_ylim(0, 15.5)
ax.set_title("Primer año, M€", fontsize=9, loc="left", color=GREY)
fig.tight_layout(); fig.savefig(OUT / "g5_cascada.png", transparent=True); plt.close(fig)
R["cascada"] = dict(cotizaciones=cot, impuesto=irpf, neto=neto, prima=prima, solidaridad=soli, alquiler=alq, invierte=ahorro)

# ---------------- 6. lesión: con y sin plan
fig, ax = plt.subplots(figsize=(5.0, 2.6))
labs = ["Sin lesión", "Lesión a los 28\ncon el plan", "Lesión a los 28\nsin el plan"]
vals = [R["gasto_90"], R["lesion28_con_plan"], R["lesion28_sin_plan"]]
ax.bar(labs, vals, color=[BLUE, ORANGE, GREY], width=.58)
for i, v_ in enumerate(vals):
    ax.text(i, v_ + .03, f"{fmt(v_,2)} M€", ha="center", fontsize=9, fontweight="bold", color=NAVY)
ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.set_ylim(0, 1.45)
fig.tight_layout(); fig.savefig(OUT / "g6_lesion.png", transparent=True); plt.close(fig)

# ---------------- 7. colchón y seguro
fig, ax = plt.subplots(figsize=(4.6, 2.6))
anios = ["2026", "2027", "2028", "2029", "2030"]; aseg = [27, 21.6, 16.2, 10.8, 5.4]
ax.bar(anios, [3] * 5, color=ORANGE, width=.6, label="Colchón (3 M€)")
ax.bar(anios, aseg, bottom=3, color=LIL2, width=.6, label="Seguro de fin de carrera")
for i, v_ in enumerate(aseg):
    ax.text(i, v_ + 3.6, fmt(v_), ha="center", fontsize=8.5, fontweight="bold", color=NAVY)
ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.legend(frameon=False, fontsize=8)
ax.set_title("Protección si una lesión le retira, M€", fontsize=8.5, loc="left", color=GREY)
fig.tight_layout(); fig.savefig(OUT / "g7_seguro.png", transparent=True); plt.close(fig)

json.dump(R, open(OUT / "cifras_v2.json", "w"), indent=1, ensure_ascii=False, default=float)
print("cascada", {k: round(v, 3) for k, v in R["cascada"].items()})
