# Versión 2 del plan (tras la primera mentoría)

Caso actualizado: futbolista internacional de 26 años que ficha por un club de la Ligue 1 (residente fiscal en Francia, régimen de impatriados), 13,6 M€ brutos al año hasta 2031, dos temporadas más, retirada a los 33 y vuelta a España. Patrimonio de 20 M€, un 70 % en pisos en España.

## Qué cambia respecto a la versión 1

| Mentoría | Respuesta en la v2 |
|---|---|
| Una sola cartera para toda la vida no basta | Tres carteras por etapa: Carrera (26-30), Puente (31-39) y Rentas (40+) |
| Las infraestructuras son renta variable, no protección | Fuera. Entra más inmobiliario cotizado y oro |
| Gráficos demasiado simples, sin efecto compuesto | 20.000 escenarios: negativo, realista y optimista |
| «¿No voy a poder comprar más pisitos?» | Inmuebles en torno al 40 % del patrimonio y compra de pisos al volver a España |
| Explicar mejor el gasto sostenible | Probabilidad de que el dinero llegue a los 95 según lo que gaste |

## Archivos

| Archivo | Qué hace |
|---|---|
| `ltcma_v2.py` | Rentabilidades, volatilidades y correlaciones de J.P. Morgan AM (LTCMA 2026, euros) |
| `modelo_v2.py` | Simulación año a año: sueldo, impuestos, seguro, colchón, pisos, tres carteras, retirada y gasto |
| `resultados_v2.py` | Cifras de la presentación (`resultados/cifras_v2.json`) y gráficos |

```
cd v2
python resultados_v2.py      # unos 3 minutos
```

## Resultados principales

| | Cifra |
|---|---|
| Patrimonio a los 33 (negativo / realista / optimista) | 57 / 69 / 86 M€ |
| Gasto de por vida que llega a los 95 en 9 de cada 10 escenarios | 1,09 M€ al año de hoy (1,1 M€ llega en el 89 %) |
| Con su gasto actual (1,5 M€) | llega en 54 de cada 100 |
| Frente a la cartera de la v1 / una 60/40 | +70.000 € / +85.000 € de gasto seguro al año |
| Lesión a los 28, con y sin colchón y seguro | 0,85 M€ frente a 0,61 M€ al año |

| Cartera | Rentabilidad esperada | Volatilidad | Peor año (1 de cada 20) |
|---|---:|---:|---:|
| Carrera | 6,4 % | 10,3 % | -10 % |
| Puente | 6,0 % | 8,8 % | -8 % |
| Rentas | 5,9 % | 8,5 % | -8 % |

## Hipótesis que conviene conocer

- Neto en Francia calibrado con el caso anterior: 10,6 % de cotizaciones y 32,5 % de impuesto sobre el bruto con el régimen 155 B.
- Pisos: 5 % de rentabilidad bruta, 25 % de gastos, 19 % de impuesto como no residente (22 % como residente), 2,5 % de revalorización con volatilidad del 8 %.
- Impuesto de Solidaridad: escala estatal con tramos actualizados con la inflación. Como no residente, sobre los pisos sin límite conjunto. Como residente en España, sobre todo el patrimonio con el límite conjunto (mínimo del 20 % de la cuota).
- Costes de la cartera: 0,9 % al año (fondos 0,22 %, contrato y depositario 0,4 %, asesoramiento 0,3 %), como en la v1. Rescates: 28 % sobre la parte de ganancia.
- Agencia: hasta 3,5 M€, como en la v1: 1,5 M€ a los 33 y 1 M€ a los 34 y a los 35, a rentabilidad cero.
- Regla de gasto: si el patrimonio real cae por debajo del 80 % del que tenía al retirarse, ese año gasta un 15 % menos.
- Seguro: 27 M€ el primer año, decreciente hasta 2031, prima del 1,25 % (rango de mercado 0,5-2 %).

Pendiente de verificar con un especialista: la prima real del seguro, la aplicación del límite conjunto a no residentes (TEAC, diciembre de 2025) y la adaptación del contrato luxemburgués a la normativa española.

## Versión final (resultados_v5.py y graficos_v5.py)

Tras la mentoría: todas las cifras en **euros de hoy**, un piso de 1 M€ al año mientras juega (27-32) y, al volver, compra hasta que los inmuebles (pisos + inmobiliario cotizado) sean el 45 %.

```
python resultados_v5.py   # cifras (resultados/cifras_v5.json), unos 5 minutos
python graficos_v5.py     # gráficos h0-h4, segundos
```

| | Cifra (euros de hoy) |
|---|---|
| Patrimonio a los 33 (negativo / realista / optimista) | 49 / 59 / 73 M€ |
| Gasto de por vida en 9 de cada 10 escenarios | 1,08 M€ al año (1,1 M€ llega en el 89 %) |
| Con su gasto actual (1,5 M€) | llega en el 52 % |
| Pisos | de 14 a más de 20 M€; inmuebles ≈46 % a los 35 |
| Coste de las compras de pisos | menos de un 1 % del gasto |
| Frente a una 60/40 / la cartera de la v1 | +85.000 € / +75.000 € al año |
| Lesión a los 28, con y sin colchón y seguro | 0,85 frente a 0,60 M€ al año |
| Patrimonio a los 95, realista | ≈75 M€ |
