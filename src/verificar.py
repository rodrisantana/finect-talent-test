"""
VERIFICACIÓN: comprueba que el código sigue dando las cifras que aparecen en la presentación.

Uso:  python src/verificar.py

Si alguien cambia una hipótesis o el código y una cifra clave se mueve, este script falla y lo
avisa. Es una prueba automática sencilla (un "test"): cada línea compara un resultado con el
valor esperado dentro de un margen razonable.
"""
import sys
import modelo_plan as mp
import backtest_historico as bh

fallos = []


def comprobar(descripcion, valor, esperado, margen):
    ok = abs(valor - esperado) <= margen
    print(f"[{'OK ' if ok else 'FALLO'}] {descripcion}: {valor:,.3f} (esperado {esperado:,.3f} ± {margen})")
    if not ok:
        fallos.append(descripcion)


print("MODELO DEL PLAN (Monte Carlo, 20.000 escenarios)")
comprobar("Gasto sostenible al 90 % de confianza, vendiendo inmuebles (€)",
          mp.gasto_sostenible(0.90, vender_inmuebles=True) * 1e6, 566_000, 5_000)
comprobar("Probabilidad de llegar a 95 con 550.000 €/año, vendiendo inmuebles",
          mp.probabilidad_exito(0.55, vender_inmuebles=True), 0.92, 0.015)
comprobar("Probabilidad de llegar a 95 con 550.000 €/año, sin vender inmuebles",
          mp.probabilidad_exito(0.55), 0.84, 0.015)
comprobar("Probabilidad de llegar a 95 con 1 M€/año (menos de 1 de cada 10)",
          mp.probabilidad_exito(1.0, vender_inmuebles=True), 0.083, 0.02)
comprobar("Gasto central sin azar, sin vender inmuebles (€)", mp.gasto_sostenible() * 1e6, 712_000, 5_000)
base = mp.gasto_sostenible(0.85, vender_inmuebles=True)
lesion = mp.gasto_sostenible(0.85, vender_inmuebles=True, edad_retirada=29)
comprobar("Pérdida de gasto sostenible por lesión a los 29 (%)", (1 - lesion / base) * 100, 43, 2)
_, tray, _ = mp.simular(0.55)
comprobar("Cartera financiera a los 33 años (M€ de hoy)", float(tray[0, 7]), 28.2, 0.2)

print("\nBACKTEST HISTÓRICO (nov-2006 a ago-2026)")
r = bh.cargar_rentabilidades()
v, _ = bh.simular(r, bh.CARTERAS["Cartera propuesta"])
m = bh.metricas(v, r["monetario"])
comprobar("Rentabilidad anual de la cartera propuesta (%)", m["Rentabilidad anual (TAE)"] * 100, 6.0, 0.1)
comprobar("Volatilidad anual (%)", m["Volatilidad anual"] * 100, 6.2, 0.1)
comprobar("Caída máxima (%)", m["Caída máxima"] * 100, -18.5, 0.2)
comprobar("Caída en 2022 (%)", bh.dd_periodo(v, "2021-12", "2022-12") * 100, -9.4, 0.2)
v60, _ = bh.simular(r, bh.CARTERAS["60/40 global"])
comprobar("Caída máxima de la 60/40 (%)", bh.metricas(v60, r["monetario"])["Caída máxima"] * 100, -28.5, 0.2)

if fallos:
    print(f"\n{len(fallos)} comprobaciones han fallado:", *fallos, sep="\n  - ")
    sys.exit(1)
print("\nTodo correcto: el código reproduce las cifras de la presentación.")
