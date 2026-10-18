"""Gráficos de la versión final, en euros de hoy. Necesita resultados/cifras_v5.json (resultados_v5.py).
Uso: python v2/graficos_v5.py   (segundos)"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import modelo_v2 as M

OUT = Path(__file__).resolve().parent / "resultados"
for f in Path("/root/.fonts").glob("Montserrat*.ttf"):
    fm.fontManager.addfont(str(f))
plt.rcParams.update({"font.family": "Montserrat", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 220})
NAVY, BLUE, ORANGE, LILAC, LIL2, PEACH, GREY, GOLD = "#14163A", "#3C44D7", "#FF8041", "#ECEBFD", "#8A90E8", "#FDE6DA", "#6B6E80", "#D9A441"
N = 20000
E = list(M.EDADES)
KW = dict(regla_flexible=True)
R = json.load(open(OUT / "cifras_v5.json"))
fmt = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
r0 = lambda x: int(np.floor(x + 0.5))
DEF = np.array([1.02 ** (a - 26 + 1) for a in E])
GASTO = round(R["gasto_90"], 1)
t = M.simular(GASTO, n=N, **KW)                        # misma semilla que resultados_v5.py
W = t["W"] / DEF
j33 = E.index(32)
pct = {q: np.percentile(W, q, axis=0) for q in (10, 25, 50, 75, 90)}
comp = {k: np.median(t[k] / DEF, axis=0) for k in ("P", "F", "C", "A")}
tot = sum(comp.values())
for k in comp:
    comp[k] = comp[k] / tot * pct[50]
assert abs(pct[50][j33] - R["patrimonio_33"]["realista"]) < 1e-6

# ================= GRÁFICOS
# h0. portada: 26-33 sobre fondo azul
x = np.arange(26, 34)
p10, p50, p90 = (np.concatenate([[20.0], pct[q][:j33 + 1]]) for q in (10, 50, 90))
W_, L_, O_ = "#FFFFFF", "#DDDEFA", "#FF8041"
fig, ax = plt.subplots(figsize=(3.6, 3.3), dpi=300)
fig.patch.set_alpha(0); ax.patch.set_alpha(0)
ax.fill_between(x, p10, p90, color="#FFFFFF", alpha=0.16, lw=0)
ax.plot(x, p90, color=L_, lw=1.4); ax.plot(x, p10, color=L_, lw=1.4); ax.plot(x, p50, color=O_, lw=3)
for y, lab, c, dy in ((p90[-1], "Optimista", L_, 4), (p50[-1], "Realista", O_, 0), (p10[-1], "Negativo", L_, -4)):
    ax.text(33.25, y + dy * 0.6, f"{r0(y)} M€", color=c, fontsize=10, fontweight="bold", va="center")
    ax.text(33.25, y + dy * 0.6 - 4.2, lab, color=c, fontsize=6.5, va="center")
ax.text(26.6, 9, "20 M€ hoy", color=W_, fontsize=8, fontweight="bold", va="bottom")
ax.set_xlim(26, 35.3); ax.set_ylim(0, 85)
ax.set_xticks(range(26, 34)); ax.tick_params(colors=L_, labelsize=7, length=0)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(L_); ax.set_yticks([]); ax.set_xlabel("Edad", color=L_, fontsize=7)
ax.set_title("Patrimonio previsto, M€ de hoy", color=W_, fontsize=10, fontweight="bold", loc="left")
fig.tight_layout(pad=0.3); fig.savefig(OUT / "h0_portada.png", transparent=True); plt.close(fig)

# h1. patrimonio de por vida (26-95), escenarios, euros de hoy
ed = np.arange(26, 97)
def serie(q):
    return np.concatenate([[20.0], pct[q]])
TOP = 140
fig, ax = plt.subplots(figsize=(6.0, 3.4))
ax.axvspan(26, 33, color=PEACH, alpha=.55, lw=0)
ax.fill_between(ed, serie(10), np.minimum(serie(90), TOP), color=LILAC, lw=0, label="Entre el negativo y el optimista")
ax.fill_between(ed, serie(25), serie(75), color="#D5D7F7", lw=0, label="La mitad central de los escenarios")
ax.plot(ed, np.where(serie(90) <= TOP, serie(90), np.nan), color=BLUE, lw=1.4, label="Optimista")
ax.plot(ed, serie(50), color=ORANGE, lw=2.8, label="Realista")
ax.plot(ed, serie(10), color=NAVY, lw=1.4, label="Negativo")
for q, c, dx, dy in ((90, BLUE, -7, 8), (50, ORANGE, 9, -8), (10, NAVY, -7, -9)):
    v_ = serie(q)[list(ed).index(33)]
    ax.plot([33], [v_], "o", color=c, ms=3.5)
    ax.annotate(f"{r0(v_)}", (33, v_), xytext=(dx, dy), textcoords="offset points", ha="center",
                color=c, fontweight="bold", fontsize=10, va="center")
for q, c, dy in ((50, ORANGE, 9), (10, NAVY, 8)):
    v_ = serie(q)[list(ed).index(95)]
    ax.plot([95], [v_], "o", color=c, ms=3.5)
    ax.annotate(f"{r0(v_)}", (95, v_), xytext=(-3, dy), textcoords="offset points", ha="right",
                color=c, fontweight="bold", fontsize=10, va="center")
opt95 = serie(90)[list(ed).index(95)]
ax.text(94.5, TOP - 6, f"optimista a los 95: {r0(opt95)} M€ ↑", ha="right", color=BLUE, fontsize=8)
ax.text(29.5, 4, "juega", ha="center", color=ORANGE, fontsize=9, fontweight="bold")
ax.text(64, 4, "vive de rentas: 1,1 M€ al año", ha="center", color=GREY, fontsize=9)
ax.set_xlim(26, 95.5); ax.set_ylim(0, TOP)
ax.set_xticks([26, 33, 40, 50, 60, 70, 80, 95]); ax.set_xlabel("Edad", fontsize=9.5); ax.set_ylabel("M€ de hoy", fontsize=9.5)
ax.tick_params(labelsize=9); ax.grid(axis="y", alpha=.25)
x_o = 48; ax.text(x_o, serie(90)[list(ed).index(x_o)] + 6, "Optimista", color=BLUE, fontsize=9.5, fontweight="bold", ha="right")
ax.text(80, serie(50)[list(ed).index(80)] + 5, "Realista", color=ORANGE, fontsize=9.5, fontweight="bold", ha="center")
ax.text(55, serie(10)[list(ed).index(55)] - 10, "Negativo", color=NAVY, fontsize=9.5, fontweight="bold", ha="center")
fig.tight_layout(); fig.savefig(OUT / "h1_patrimonio_vida.png", transparent=True); plt.close(fig)

# h2. probabilidad según el gasto
gs = sorted(float(k) for k in R["prob_gasto"]); ps = [R["prob_gasto"][str(g)] * 100 for g in gs]
fig, ax = plt.subplots(figsize=(5.2, 2.7))
cols = [ORANGE if abs(g - GASTO) < 1e-9 else (GREY if g == 1.5 else LIL2) for g in gs]
ax.bar([fmt(g) for g in gs], ps, color=cols, width=0.6)
for i, p in enumerate(ps):
    ax.text(i, p + 1.8, f"{p:.0f} %", ha="center", fontsize=9, fontweight="bold", color=NAVY)
ax.axhline(90, color=NAVY, lw=.8, ls="--"); ax.text(5.45, 91.5, "9 de cada 10", fontsize=7.5, color=NAVY, ha="right")
ax.text(gs.index(GASTO), 6, "plan", ha="center", color="white", fontsize=7.5, fontweight="bold")
ax.text(5, 6, "su gasto\nactual", ha="center", color="white", fontsize=7, fontweight="bold")
ax.set_ylim(0, 112); ax.set_yticks([]); ax.spines["left"].set_visible(False)
ax.set_xlabel("Gasto anual de por vida, M€ de hoy")
fig.tight_layout(); fig.savefig(OUT / "h2_prob_gasto.png", transparent=True); plt.close(fig)

# h3. carteras por etapa
grupos = [("Renta variable", ("dev", "euro", "em"), NAVY), ("Inmobiliario cotizado", ("reits",), ORANGE),
          ("Renta fija", ("ig", "multi", "ilb", "govt"), LIL2), ("Oro", ("gold",), GOLD), ("Liquidez", ("cash",), "#C9CBF3")]
edades_et = {"Carrera": "26-30 años", "Puente": "31-39 años", "Rentas": "desde los 40"}
fig, ax = plt.subplots(figsize=(6.2, 2.7))
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
ax.set_yticks(range(len(nombres)), [f"{n}\n{edades_et[n]}" for n in nombres], fontsize=8.5)
for lbl in ax.get_yticklabels(): lbl.set_fontweight("bold")
ax.set_xlim(0, 100); ax.set_xticks([]); ax.spines["bottom"].set_visible(False); ax.spines["left"].set_visible(False)
ax.legend(ncol=5, frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.02), handlelength=1)
fig.tight_layout(); fig.savefig(OUT / "h3_carteras.png", transparent=True); plt.close(fig)

# h4. composición del patrimonio (escenario realista), euros de hoy
ed2 = np.arange(26, 46); js2 = [E.index(a) for a in range(26, 45)]
capas = [("Pisos en España", "P", NAVY, 14.0), ("Colchón de liquidez", "C", "#C9CBF3", 3.0),
         ("Cartera financiera", "F", BLUE, 3.0), ("Agencia", "A", ORANGE, 0.0)]
ys = [np.concatenate([[v0], comp[k][js2]]) for _, k, _, v0 in capas]
fig, ax = plt.subplots(figsize=(11, 2.55))
ax.stackplot(ed2, *ys, colors=[c for _, _, c, _ in capas], labels=[l for l, _, _, _ in capas], lw=0)
P_ = ys[0]; TOT = sum(ys)
ax.axvline(33, color="white", lw=1, ls=(0, (3, 2)))
for a_, ha, dx in ((26, "left", 0.15), (33, "center", 0), (45, "right", -0.15)):
    j = list(ed2).index(a_)
    ax.text(a_ + dx, P_[j] - 3.6, f"{r0(P_[j])} M€", color="white", fontsize=10, fontweight="bold", ha=ha, va="center")
    ax.text(a_ + dx, TOT[j] + 2.2, f"{r0(TOT[j])} M€", color=NAVY, fontsize=10, fontweight="bold", ha=ha)
ax.text(29.5, 3.6, "un piso al año mientras juega", color="#C9CBF3", fontsize=9.5, ha="center", va="center")
ax.text(39, 3.6, "más pisos al volver a España", color="#C9CBF3", fontsize=9.5, ha="center", va="center")
ax.text(39, 40, "cartera financiera", color="white", fontsize=10, ha="center", va="center", alpha=.9)
ax.set_xlim(26, 45); ax.set_ylim(0, 72); ax.set_xticks([26, 28, 30, 33, 35, 40, 45])
ax.set_xticklabels(["hoy (26)", "28", "30", "33", "35", "40", "45 años"])
ax.set_ylabel("M€ de hoy", fontsize=9.5); ax.tick_params(labelsize=9.5); ax.grid(axis="y", alpha=.2)
ax.legend(frameon=False, fontsize=9.5, loc="upper center", ncol=4, bbox_to_anchor=(0.5, -0.14))
fig.tight_layout(); fig.savefig(OUT / "h4_composicion.png", transparent=True); plt.close(fig)
print("graficos ok")
