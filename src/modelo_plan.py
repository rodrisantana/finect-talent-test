"""
MODELO DEL PLAN PATRIMONIAL (Finect Talent 2026, Caso A "El futbolista")

Este archivo es el "motor" de las simulaciones. El resto de scripts lo importan.

IDEA GENERAL
------------
Seguimos el patrimonio financiero del futbolista año a año, desde los 26 hasta los 95:

  * Mientras juega (26 a 32 años): cada año entra su renta disponible, sale su gasto
    de vida y la cartera crece con la rentabilidad del mercado.
  * Desde la retirada (33 años): ya no entra sueldo. Cada año retira de la cartera
    lo que necesita para vivir, pagando impuestos sobre la parte de ganancia.
  * Si la cartera se agota, el modelo puede vender los inmuebles (con un 15 % de coste).

La pregunta que contesta el modelo es: "¿cuánto puede gastar al año, en euros de hoy,
sin quedarse sin dinero antes de los 95 años?"

TODO ESTÁ EN MILLONES DE EUROS DE HOY (euros reales), salvo que se diga lo contrario.
Así, "0,55" significa 550.000 euros de poder adquisitivo actual cada año.

SUPUESTOS (son hipótesis de trabajo, no datos reales; están declarados en la presentación)
-----------------------------------------------------------------------------------------
  * Edad actual 26. Cobra 7 temporadas (26 a 32) y se retira a los 33.
  * Renta disponible: 4,55 M€ nominales fijos al año
      (8 M€ brutos, menos unos 0,85 M€ de cotizaciones, menos unos 2,6 M€ de impuestos).
  * Gasto mientras juega: 1 M€ de hoy al año (incluye seguros).
  * Patrimonio inicial: 9 M€. De ellos, 6,3 M€ son inmuebles (70 %) y 2,7 M€ son líquidos.
  * Inmuebles: valor real constante, renta neta del 2 % anual. Solo se venden si la cartera
    se agota (en ese caso se pierde un 15 % por impuestos y costes).
  * Agencia de representación: 3,5 M€ de hoy quedan invertidos en la cartera y salen a los
    33 años (se dan por gastados en montar la agencia).
  * Rentabilidad: 5,2 % anual compuesta antes de costes (J.P. Morgan LTCMA 2026, en euros).
  * Costes: 0,9 % anual (fondos 0,22 % + contrato y custodia 0,4 % + asesoramiento 0,3 %).
  * Inflación: 2 %.
  * Impuestos: 30 % sobre la parte de cada retirada que es ganancia (contrato de
    capitalización francés).
  * Incertidumbre: rentabilidades anuales aleatorias con volatilidad del 7,6 %
    (estimación prudente; la LTCMA da 6,6 % para la cartera propuesta).

SIMULACIÓN MONTE CARLO EN POCAS PALABRAS
----------------------------------------
Un "escenario" es una secuencia posible de rentabilidades anuales sacadas al azar. Se simulan
20.000 escenarios y se mira en cuántos el dinero llega a los 95. Ese porcentaje es la
"probabilidad de éxito" o "nivel de confianza". Si con 550.000 € al año llega en el 92 % de los
escenarios, decimos que ese gasto se sostiene con un 92 % de confianza.
"""
import numpy as np

# Constantes del plan
INFLACION = 0.02
COSTE_TOTAL = 0.009            # 0,9 % anual
RENT_COMPUESTA = 0.0522        # rentabilidad compuesta bruta de la mezcla propuesta (LTCMA 2026 EUR)
RENT_ARITMETICA = 0.0543       # rentabilidad aritmética bruta (la media simple de los años)
IMPUESTO_PLUSVALIA = 0.30      # impuesto sobre la parte de ganancia de cada retirada
VOL_PRUDENTE = 0.076           # volatilidad usada en las simulaciones

EDAD_INICIAL = 26
EDAD_FIN_SUELDO_ALTO = 33      # a partir de esta edad (si sigue jugando) puede cobrar menos


def simular(gasto, n=1, vol=0.0, bruto=None, edad_retirada=33,
            renta_disponible=4.55, renta_tardia=None,
            gasto_carrera=1.0, reserva_agencia=3.5,
            valor_inmuebles=6.3, renta_inmuebles=0.02,
            edad_final=95, semilla=7, cartera_inicial=2.7,
            vender_inmuebles=False, coste=COSTE_TOTAL,
            impuesto=IMPUESTO_PLUSVALIA, inflacion=INFLACION, rend_forzado=None):
    """Simula la cartera financiera del futbolista, año a año.

    Parámetros principales
    ----------------------
    gasto            gasto anual desde la retirada, en M€ de hoy (0,55 = 550.000 €)
    n                número de escenarios (1 = determinista, 20000 = Monte Carlo)
    vol              volatilidad anual de la cartera (0 = sin azar, rentabilidad fija)
    bruto            rentabilidad compuesta bruta; si no se da se usa la de la mezcla propuesta
    edad_retirada    edad a la que deja de cobrar (33 en el caso base, 29 en el caso de lesión)
    renta_tardia     renta disponible de las temporadas a partir de los 33 si juega más
                     (None = igual que antes)
    vender_inmuebles si es True, al agotarse la cartera se venden los inmuebles
    coste, impuesto  coste anual total y tipo sobre la ganancia de las retiradas
    rend_forzado     diccionario {edad: rentabilidad bruta nominal de ese año} para imponer un
                     año concreto (por ejemplo, una crisis justo al retirarse). El resto de años
                     siguen el modelo normal. Sirve para las pruebas de estrés.

    Devuelve (edades, trayectoria, edad_agotamiento):
      trayectoria      matriz n x edades con el valor real de la cartera cada año
      edad_agotamiento edad a la que se agota la cartera en cada escenario (nan = no se agota)
    """
    rng = np.random.default_rng(semilla)          # la semilla fija hace los resultados repetibles
    edades = np.arange(EDAD_INICIAL, edad_final + 1)

    # 1) Rentabilidad bruta. Con volatilidad usamos la fórmula media aritmética - vol^2/2,
    #    que da la rentabilidad compuesta (la "mediana") coherente con esa volatilidad.
    if bruto is None:
        bruto = (RENT_ARITMETICA - vol ** 2 / 2) if vol > 0 else RENT_COMPUESTA
    neto = bruto - coste                          # tras restar los costes

    # 2) Rentabilidades anuales: matriz n x edades con el azar de cada escenario
    if vol > 0:
        rend_nominal = np.exp(rng.normal(np.log(1 + neto), vol, (n, len(edades)))) - 1
    else:
        rend_nominal = np.full((n, len(edades)), neto)

    if rend_forzado:                              # prueba de estrés: años impuestos (restando costes)
        for edad_f, rent_f in rend_forzado.items():
            rend_nominal[:, edad_f - EDAD_INICIAL] = rent_f - coste

    cartera = np.full(n, cartera_inicial)         # valor de la cartera en euros de hoy
    base_coste = np.full(n, cartera_inicial)      # lo aportado (en euros nominales), para saber qué parte es ganancia
    vivo = np.ones(n, bool)                       # True mientras la cartera no se agote
    agotamiento = np.full(n, np.nan)
    trayectoria = np.zeros((n, len(edades)))
    renta_inm = valor_inmuebles * renta_inmuebles
    vendidos = np.zeros(n, bool)                  # True si ya se vendieron los inmuebles

    for j, edad in enumerate(edades):
        t = edad - EDAD_INICIAL
        deflactor = (1 + inflacion) ** t          # para pasar euros nominales a euros de hoy
        trayectoria[:, j] = np.where(vivo, cartera, 0)
        rend_real = (1 + rend_nominal[:, j]) / (1 + inflacion) - 1

        if edad < edad_retirada:
            # --- FASE DE CARRERA: entra sueldo, sale gasto, la cartera crece ---
            sueldo = renta_disponible if (edad < EDAD_FIN_SUELDO_ALTO or renta_tardia is None) else renta_tardia
            ahorro = sueldo / (deflactor * (1 + inflacion)) - gasto_carrera + renta_inm
            cartera = cartera * (1 + rend_real) + ahorro
            base_coste = base_coste + ahorro * deflactor * (1 + inflacion)
        else:
            # --- FASE DE RETIRADA ---
            if edad == edad_retirada and reserva_agencia > 0:
                # Sale el dinero de la agencia (se da por gastado). Tributa la parte de ganancia.
                cart_nom = cartera * deflactor
                parte_ganancia = np.clip((cart_nom - base_coste) / np.maximum(cart_nom, 1e-9), 0, 1)
                retirada_bruta = reserva_agencia / (1 - impuesto * parte_ganancia)
                base_coste = base_coste * (1 - np.minimum(retirada_bruta, cartera) / np.maximum(cartera, 1e-9))
                cartera = cartera - retirada_bruta
            # Necesidad de la cartera: el gasto menos la renta de los inmuebles (si aún se tienen)
            necesidad = np.maximum(0.0, gasto - np.where(vendidos, 0, renta_inm))
            cart_nom = cartera * deflactor
            parte_ganancia = np.clip((cart_nom - base_coste) / np.maximum(cart_nom, 1e-9), 0, 1)
            # Para recibir "necesidad" netos hay que retirar más, porque parte paga impuestos
            retirada_bruta = necesidad / (1 - impuesto * parte_ganancia)
            base_coste = base_coste * (1 - np.minimum(retirada_bruta, np.maximum(cartera, 0)) / np.maximum(cartera, 1e-9))
            cartera = (cartera - retirada_bruta) * (1 + rend_real)    # retirada a principio de año

        # --- ¿Se ha agotado la cartera este año? ---
        recien_agotado = vivo & (cartera <= 0)
        if vender_inmuebles:
            puede_vender = recien_agotado & (~vendidos)
            # Se vende el inmueble con un 15 % de coste e impuestos
            cartera = np.where(puede_vender, cartera + valor_inmuebles * 0.85, cartera)
            base_coste = np.where(puede_vender, cartera * (1 + inflacion) ** (t + 1), base_coste)
            vendidos = vendidos | puede_vender
            recien_agotado = vivo & (cartera <= 0)
        agotamiento[recien_agotado] = edad + 1
        vivo &= cartera > 0
        cartera = np.where(vivo, cartera, 0)

    return edades, trayectoria, agotamiento


def probabilidad_exito(gasto, n=20000, vol=VOL_PRUDENTE, edad_objetivo=95, **kw):
    """Proporción de escenarios en los que la cartera NO se agota antes de la edad objetivo."""
    _, _, agot = simular(gasto, n=n, vol=vol, edad_final=edad_objetivo, **kw)
    return float(np.mean(np.isnan(agot)))


def gasto_sostenible(confianza=None, edad_objetivo=95, n=20000, vol=VOL_PRUDENTE, **kw):
    """Gasto anual máximo (M€ de hoy) que llega a la edad objetivo.

    Se busca por bisección: se prueba un gasto, se mira si cumple, y se sube o baja
    hasta encontrar el máximo que cumple.

    confianza=None   escenario central determinista (rentabilidad fija, sin azar)
    confianza=0,90   el gasto con el que el dinero llega a los 95 en el 90 % de los escenarios
    """
    bajo, alto = 0.1, 3.0
    for _ in range(40):
        medio = (bajo + alto) / 2
        if confianza is None:
            _, _, agot = simular(medio, edad_final=edad_objetivo, **kw)
            cumple = bool(np.isnan(agot[0]))
        else:
            cumple = probabilidad_exito(medio, n=n, vol=vol, edad_objetivo=edad_objetivo, **kw) >= confianza
        bajo, alto = (medio, alto) if cumple else (bajo, medio)
    return bajo
