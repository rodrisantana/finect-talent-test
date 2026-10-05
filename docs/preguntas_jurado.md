# Preguntas probables del jurado y cifras que las respaldan

Cada respuesta indica de dónde sale el número, para poder enseñarlo si lo piden.

## ¿En base a qué esos porcentajes y no otros? ¿Habéis hecho simulaciones?

Respuesta honesta y sólida: "Partimos de criterios: liquidez para cubrir una lesión, poca renta variable porque sus ingresos ya son muy arriesgados, diversificadores con poco peso y productos baratos. Después los contrastamos con simulaciones: comparamos la propuesta con doce alternativas, desde un 30 % hasta un 100 % de renta variable, en una simulación del plan completo y con datos históricos desde 2006. El gasto sostenible casi no cambia entre un 30 % y un 60 % de renta variable, entre 588.000 y 595.000 € al año, pero la caída máxima histórica pasa del 12 % al 30 %. Por eso elegimos la cartera más estable sin perder gasto."

Evitar decir: "las simulaciones nos dieron estos porcentajes" o "es la cartera óptima". No es verdad, y si preguntan por el óptimo hay respuesta: ver más abajo. Cifras: `resultados/alternativas/comparacion_carteras.csv`.

## ¿Por qué no más renta variable, si es joven?

Con las hipótesis de J.P. Morgan, una 60/40 permitiría gastar unos 50.000 € más al año en el escenario central, pero a un 85 % de confianza sale algo peor, y su caída histórica es del 28,5 % frente al 18,5 % de la propuesta (2007-09). Su ingreso, además, ya se comporta como una acción muy volátil. Cifras: `alternativas_cartera.py` y `backtest_historico.py`.

## ¿Y por qué no menos?

Con un 30 % de renta variable el gasto al 90 % sale prácticamente igual (588.000 € frente a 594.000 €) con menos caída (-12 % frente a -18,5 %), pero el escenario central baja unos 40.000 € y la cartera crece menos por si juega más años. El 40 % es una elección de preferencia por el riesgo, no una verdad matemática; reconocerlo suena mejor que defenderla como única.

## ¿Habéis optimizado la cartera? ¿Dónde está en la frontera eficiente?

No hemos optimizado. Con las hipótesis de J.P. Morgan, la mejor combinación para el mismo riesgo y con un 15 % de liquidez daría unos 0,25 puntos más de rentabilidad (5,4 % frente a 5,2 %), pero con un 26 % en infraestructuras y un 20 % en oro. Esa concentración depende de estimaciones inciertas y de activos poco líquidos, así que no la recomendaríamos. Nuestra propuesta queda por encima de cualquier mezcla clásica de renta variable y renta fija. Cifras: `resultados/alternativas/frontera_pesos.csv`.

## ¿Para qué el 15 % de monetario? ¿Y el oro?

El monetario cuesta unos 16.000 € al año de gasto sostenible, pero sin él la cartera cae un 11,6 % en 2022 en lugar de un 9,4 %. El oro aporta unos 19.000 € de gasto sostenible y también amortigua 2008 y 2022 (sin oro: -21 % en la peor caída histórica). Cifras: `comparacion_carteras.csv`.

## ¿Cuánto gasta al año y cómo lo habéis calculado?

Unos 550.000 € al año en euros de hoy desde los 33. Con 20.000 escenarios, ese gasto llega a los 95 años en el 92 % (84 % sin vender nunca los inmuebles). Con 1 M€ al año, en menos de 1 de cada 10. El escenario central, sin azar, da unos 750.000 €. Cifras: `resultados/plan/probabilidad_por_gasto.csv`.

## ¿Qué pasa si se lesiona?

Si una lesión le retira a los 29, el gasto sostenible baja en torno a un 43 % (de unos 594.000 a 336.000 € al 85 %). Por eso hay un colchón de liquidez y un seguro de invalidez: ninguna cartera diversifica ese riesgo. Cifras: `resultados/sensibilidades/lesion_a_los_29.csv`.

## ¿Y si juega más allá de los 33? Estáis siendo muy conservadores

Es una hipótesis prudente a propósito. Si juega hasta los 35 con un sueldo menor (2 M€ netos), el gasto sostenible sube un 8 % (611.000 €), y un 12 % si llega a los 36. Cualquier alargamiento mejora el plan; la lesión es lo que lo empeora. Tener en cuenta que el régimen francés de impatriados dura ocho años, de los 26 a los 33, así que los años siguientes tributarían sin la exención. Cifras: `resultados/sensibilidades/edad_retirada.csv`.

## ¿Por qué usáis un 5,2 % si históricamente salió un 6 %?

El 6 % histórico sale por encima de las hipótesis a largo plazo (5,2 % de J.P. Morgan), sobre todo por el oro, que rindió un 11 % anual en estos años, y por una década muy buena de renta variable. Planificar con el pasado sería optimista, y por eso usamos la cifra prospectiva. Cifras: `resultados/backtest/contribucion.csv`.

## ¿Por qué una volatilidad del 7,6 % si J.P. Morgan da 6,6 %?

Para ser prudentes: con 6,6 % el gasto sostenible al 90 % sube de unos 566.000 a 593.000 €, un 5 % más. Cifras: `resultados/sensibilidades/mercado.csv`.

## En el informe pusisteis una caída del 19,7 % y del 11,1 %, y ahora decís 18,5 % y 9,4 %

En el informe eran estimaciones. Después las comprobamos con datos históricos reales en euros desde 2006 y la caída real habría sido algo menor, el 18,5 % en 2007-09 y el 9,4 % en 2022. Cifras: `resultados/backtest/crisis.csv`.

## ¿Qué pasa con los costes?

El 0,9 % anual (fondos 0,22 %, contrato y custodia unos 0,4 %, asesoramiento 0,3 %) cuesta unos 100.000 € de gasto sostenible al año frente a no tener costes. Con costes del 0,6 % sube un 5 %. Cifras: `resultados/sensibilidades/costes.csv`.

## ¿Dónde vive tras retirarse?

Es una hipótesis de cálculo, no una predicción: mantenemos la residencia francesa para que la fiscalidad del modelo sea coherente. Si volviera a España, la cartera no cambia, porque el contrato se mantiene, pero pagaría el Impuesto sobre el Patrimonio (unos 170.000 € al año según nuestro cálculo) y el contrato tendría que cumplir los requisitos fiscales españoles para seguir difiriendo el impuesto. Este último punto está pendiente de verificar con un especialista.

## Frases que conviene evitar

* "Las simulaciones nos dieron los porcentajes" (no es cierto).
* "Es la cartera óptima" (no lo es en sentido matemático).
* "Garantiza..." o "seguro que...": todo son probabilidades e hipótesis.
