# Metodología explicada sin jerga

## 1. El modelo del plan (`src/modelo_plan.py`)

El modelo sigue el dinero del futbolista año a año, de los 26 a los 95. Todo está en **euros de hoy** (euros reales), así que 550.000 significa lo que hoy compraríamos con 550.000 €.

**Mientras juega (26 a 32 años).** Cada año la cartera hace tres cosas: crece con la rentabilidad del mercado, suma lo que ahorra (renta disponible menos gasto de vida, más el alquiler neto de los inmuebles) y paga costes.

**Desde la retirada (33 años).** Ya no entra sueldo. Cada año retira de la cartera lo que necesita para vivir. Como parte de lo retirado es ganancia y esa parte paga un 30 % de impuesto, hay que retirar más de lo que se gasta:

```
retirada bruta = necesidad / (1 - 0,30 x parte de ganancia de la cartera)
```

Ejemplo: si la mitad de la cartera es ganancia, para recibir 100 netos hay que retirar 100 / (1 - 0,30 x 0,5) = 117.

**La reserva de la agencia.** Los 3,5 M€ que se reservan para la agencia siguen invertidos hasta los 33, y entonces salen (tributando su parte de ganancia). El modelo los da por gastados.

**Los inmuebles.** Valen 6,3 M€ constantes en euros de hoy y dan un 2 % neto al año. Solo se venden si la cartera se agota, con un 15 % de coste e impuestos.

## 2. La rentabilidad y la volatilidad

* **Rentabilidad esperada:** 5,2 % anual compuesta antes de costes, de las hipótesis a largo plazo de J.P. Morgan para la mezcla propuesta.
* **Costes:** 0,9 % anual (fondos 0,22 %, contrato y custodia unos 0,4 %, asesoramiento 0,3 %), que se restan directamente de la rentabilidad. Quedan unos 4,3 % netos.
* **Media y rentabilidad compuesta.** Si una cartera sube de media un 5,4 % al año pero con vaivenes, lo que realmente se acumula es algo menos: la media aritmética menos la mitad de la varianza (`compuesta = media - volatilidad² / 2`). Por eso el modelo usa 5,2 % compuesto, no 5,4 %.

## 3. La simulación Monte Carlo

Un escenario es una secuencia de rentabilidades anuales sacadas al azar con la volatilidad indicada (7,6 % en la presentación, más prudente que el 6,6 % de J.P. Morgan). Se simulan 20.000 escenarios y se cuenta en cuántos el dinero llega a los 95. Ese porcentaje es la probabilidad de éxito.

**Gasto sostenible con un 90 % de confianza** es el mayor gasto con el que el dinero llega a los 95 en al menos el 90 % de los escenarios. Se encuentra por bisección: se prueba un gasto, se mira si cumple, y se sube o se baja hasta encontrar el límite.

La semilla del generador de números aleatorios es fija (`semilla=7`), así que los resultados son siempre los mismos.

## 4. El backtest (`src/backtest_historico.py`)

Se aplican los pesos de la cartera a los datos reales mensuales de los índices (en euros, con dividendos reinvertidos) de noviembre de 2006 a agosto de 2026. Se rebalancea cada diciembre y cualquier mes en que un activo se aleje más de 5 puntos de su peso objetivo.

* **Renta fija:** FTSE WGBI cubierto a euros hasta abril de 2019 y, desde mayo de 2019, el índice que replica el fondo de Vanguard (Bloomberg Global Aggregate Float Adjusted and Scaled, cubierto).
* **Costes:** la versión "neta" resta un 0,9 % anual.
* **Caída máxima:** la mayor caída desde un máximo hasta el mínimo posterior, con datos mensuales.

## 5. La comparación de carteras (`src/alternativas_cartera.py`)

Cada cartera se evalúa de tres formas independientes: hipótesis de J.P. Morgan (rentabilidad, volatilidad y correlaciones), simulación del plan completo y backtest histórico. También se compara con la **frontera eficiente**: se generan 300.000 repartos al azar entre cinco bloques y se busca el que más rentabilidad da para el mismo riesgo.

## 6. Qué no recoge el modelo

* Cambios de legislación ni de residencia fiscal.
* Rentabilidades relacionadas de un año al siguiente (en el mundo real hay rachas).
* Que el sueldo pueda ser distinto del supuesto, salvo en las sensibilidades.
* El diferimiento fiscal al cambiar de fondo dentro del contrato, ni su protección patrimonial.
* El error de seguimiento de los fondos respecto a sus índices.

## Glosario

| Término | Significa |
|---|---|
| Euros de hoy | Euros ajustados por inflación, para comparar poder adquisitivo |
| Volatilidad | Cuánto se mueve la rentabilidad de un año a otro; a más volatilidad, más riesgo |
| Caída máxima | La mayor pérdida desde un máximo hasta el mínimo siguiente |
| Backtest | Probar la cartera con datos reales del pasado |
| Monte Carlo | Probar la cartera con miles de futuros posibles generados al azar |
| Frontera eficiente | Las carteras que dan la máxima rentabilidad posible para cada nivel de riesgo |
| Sharpe | Rentabilidad por encima del monetario dividida entre la volatilidad |
| LTCMA | Hipótesis de rentabilidad a largo plazo que publica J.P. Morgan cada año |
