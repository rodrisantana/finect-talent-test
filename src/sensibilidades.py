"""
SENSIBILIDADES: ¿cuánto cambia el resultado si una hipótesis es distinta?

Uso:  python src/sensibilidades.py
Crea: resultados/sensibilidades/*.csv

Para cada caso se calcula el gasto anual que llega a los 95 años con un 90 % de confianza
(vendiendo los inmuebles si la cartera se agota). El caso base da unos 566.000 €.
Sirve para responder a preguntas del tipo "¿y si...?" con números, y para ver qué hipótesis
mueven más el resultado.
"""
from pathlib import Path
import pandas as pd
import modelo_plan as mp

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "resultados" / "sensibilidades"
OUT.mkdir(parents=True, exist_ok=True)
CONF = 0.90


def p90(**kw):
    """Gasto sostenible al 90 % de confianza, en euros."""
    kw.setdefault("vender_inmuebles", True)
    return mp.gasto_sostenible(CONF, **kw) * 1e6


BASE = p90()


def fila(escenario, valor):
    return {"escenario": escenario, "gasto_sostenible_90%_€": round(valor, -3),
            "diferencia_vs_base_%": round((valor / BASE - 1) * 100, 1)}


def guardar(nombre, filas):
    t = pd.DataFrame(filas)
    t.to_csv(OUT / f"{nombre}.csv", index=False)
    print(f"\n== {nombre} ==")
    print(t.to_string(index=False))
    return t


# 1) COSTES: ¿cuánto pesa el 0,9 % anual?
guardar("costes", [
    fila("Base: costes 0,9 % anual", BASE),
    fila("Costes 0,6 % (asesoramiento y contrato más baratos)", p90(coste=0.006)),
    fila("Costes 0,4 % (solo fondos y contrato)", p90(coste=0.004)),
    fila("Sin costes (ideal imposible)", p90(coste=0.0)),
])

# 2) INSTRUMENTO: contrato de capitalización frente a cuenta de valores
guardar("instrumento", [
    fila("Contrato de capitalización (coste 0,9 %, impuesto 30 %)", BASE),
    fila("Cuenta de valores (coste 0,55 %, impuesto 31,4 %, sin diferimiento al cambiar de fondo)",
         p90(coste=0.0055, impuesto=0.314)),
])

# 3) EDAD DE RETIRADA: ¿y si aguanta más años jugando?
guardar("edad_retirada", [
    fila("Retirada a los 33 (caso base)", BASE),
    fila("Retirada a los 35, sueldo reducido (2 M€ netos)", p90(edad_retirada=35, renta_tardia=2.0)),
    fila("Retirada a los 35, mismo sueldo (límite superior)", p90(edad_retirada=35)),
    fila("Retirada a los 36, sueldo reducido (2 M€ netos)", p90(edad_retirada=36, renta_tardia=2.0)),
    fila("Retirada a los 36, mismo sueldo (límite superior)", p90(edad_retirada=36)),
    fila("Lesión grave: retirada a los 29", p90(edad_retirada=29)),
    fila("Retirada a los 31", p90(edad_retirada=31)),
])

# 4) HIPÓTESIS DE MERCADO
guardar("mercado", [
    fila("Base: 5,2 % compuesto bruto, volatilidad 7,6 %", BASE),
    fila("Rentabilidad un punto menor (4,2 % bruto)", p90(bruto=0.0422)),
    fila("Rentabilidad medio punto menor (4,7 % bruto)", p90(bruto=0.0472)),
    fila("Volatilidad 6,6 % (la de la LTCMA)", p90(vol=0.066)),
    fila("Volatilidad 10 %", p90(vol=0.10)),
    fila("Inflación 3 % en lugar de 2 %", p90(inflacion=0.03)),
])

# 5) HIPÓTESIS PERSONALES Y FISCALES
guardar("personal_y_fiscal", [
    fila("Base", BASE),
    fila("Gasto de carrera 1,5 M€ en lugar de 1 M€", p90(gasto_carrera=1.5)),
    fila("Renta disponible 3,6 M€ (sin régimen de impatriados)", p90(renta_disponible=3.55)),
    fila("Reserva de agencia 0 (no monta agencia)", p90(reserva_agencia=0.0)),
    fila("Impuesto sobre la ganancia 40 %", p90(impuesto=0.40)),
    fila("Impuesto sobre la ganancia 19 % (tipo mínimo español del ahorro)", p90(impuesto=0.19)),
    fila("No hay inmuebles que vender", p90(vender_inmuebles=False)),
])

# 6) LESIÓN A LOS 29: pérdida de gasto sostenible a distintos niveles de confianza
filas = []
for conf in (0.80, 0.85, 0.90):
    base = mp.gasto_sostenible(conf, vender_inmuebles=True)
    les = mp.gasto_sostenible(conf, vender_inmuebles=True, edad_retirada=29)
    filas.append({"confianza_%": int(conf * 100), "gasto_base_€": round(base * 1e6, -3),
                  "gasto_con_lesion_a_los_29_€": round(les * 1e6, -3),
                  "pérdida_%": round((1 - les / base) * 100, 1)})
guardar("lesion_a_los_29", filas)
print("\nHecho. Tablas en", OUT)
