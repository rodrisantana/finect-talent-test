"""Gráfico de la portada: patrimonio previsto de los 26 a los 33 años en tres escenarios (fondo azul)."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import modelo_v2 as M

for f in Path("/root/.fonts").glob("Montserrat*.ttf"):
    fm.fontManager.addfont(str(f))
plt.rcParams.update({"font.family": "Montserrat"})
E = list(M.EDADES)
t = M.simular(1.1, n=20000, regla_flexible=True)
js = [E.index(a) for a in range(26, 33)]
p10, p50, p90 = (np.concatenate([[20.0], np.percentile(t["W"][:, js], q, axis=0)]) for q in (10, 50, 90))
x = np.arange(26, 34)
W_, L_, O_ = "#FFFFFF", "#DDDEFA", "#FF8041"
fig, ax = plt.subplots(figsize=(3.6, 3.3), dpi=300)
fig.patch.set_alpha(0); ax.patch.set_alpha(0)
ax.fill_between(x, p10, p90, color="#FFFFFF", alpha=0.16, lw=0)
ax.plot(x, p90, color=L_, lw=1.4); ax.plot(x, p10, color=L_, lw=1.4)
ax.plot(x, p50, color=O_, lw=3)
for y, lab, c, dy in ((p90[-1], "Optimista", L_, 4), (p50[-1], "Realista", O_, 0), (p10[-1], "Negativo", L_, -4)):
    ax.text(33.25, y + dy * 0.6, f"{y:.0f} M€".replace(".", ","), color=c, fontsize=10, fontweight="bold", va="center")
    ax.text(33.25, y + dy * 0.6 - 4.2, lab, color=c, fontsize=6.5, va="center")
ax.text(26.05, 34, "20 M€ hoy", color=W_, fontsize=8, fontweight="bold", va="bottom")
ax.set_xlim(26, 35.3); ax.set_ylim(0, 95)
ax.set_xticks(range(26, 34)); ax.tick_params(colors=L_, labelsize=7, length=0)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(L_); ax.set_yticks([])
ax.set_xlabel("Edad", color=L_, fontsize=7)
ax.set_title("Patrimonio previsto, M€", color=W_, fontsize=10, fontweight="bold", loc="left")
fig.tight_layout(pad=0.3)
fig.savefig(Path(__file__).parent / "resultados" / "g0_portada.png", transparent=True)
print([round(v, 1) for v in (p10[-1], p50[-1], p90[-1])])
