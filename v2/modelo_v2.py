"""
MODELO v2 DEL PLAN (caso actualizado tras la primera mentoría)

Todo en millones de euros NOMINALES (los que verá en su cuenta) salvo que se diga lo contrario.
El gasto se fija en euros de hoy y sube cada año con la inflación.

Cliente (hipótesis del equipo, diapositiva de perfil):
  26 años en 2026, Ligue 1, residente fiscal en Francia, 13,6 M€ brutos al año, contrato hasta 2031
  (5 temporadas, 26-30), 2 temporadas más de "segunda experiencia" (31-32) y retirada a los 33.
  Patrimonio hoy 20 M€: 14 M€ en pisos en España (70 %) y 6 M€ líquidos.
  Gasto actual 1,5 M€ al año.

Estructura del plan:
  * Colchón de 3 M€ desde el primer día (cuenta remunerada + monetario), fuera de la cartera.
  * Seguro de fin de carrera decreciente (27 M€ el primer año, hasta 0 en 2031).
  * Cartera financiera dentro de un contrato de capitalización, en tres etapas:
      Carrera (26-30), Puente (31-39) y Rentas (40 en adelante).
  * Pisos: un piso de 1 M€ al año mientras juega (27-32, siendo no residente) y, al volver a España (33),
    los necesarios para que los inmuebles (pisos + inmobiliario cotizado) sean el 45 % del patrimonio.
  * Agencia: hasta 3,5 M€ (como en la versión 1), invertidos en la cartera hasta que se usan por fases:
    1,5 M€ a los 33 (licencia FIFA y equipo), 1 M€ a los 34 y 1 M€ a los 35 (primeros representados), a rentabilidad 0 %.
"""
import numpy as np
import ltcma_v2 as L

INFL = 0.02
EDADES = np.arange(26, 96)

# ---------------- carteras por etapa (pesos de la cartera financiera)
CARTERAS = {
    "Carrera": {"dev": .37, "euro": .10, "em": .10, "reits": .15, "multi": .15, "ig": .05, "gold": .06, "cash": .02},
    "Puente":  {"dev": .27, "euro": .08, "em": .08, "reits": .15, "ig": .20, "multi": .12, "gold": .06, "cash": .04},
    "Rentas":  {"dev": .25, "euro": .08, "em": .07, "reits": .15, "ig": .15, "ilb": .10, "multi": .10, "gold": .06, "cash": .04},
}


def cartera_por_edad(edad):
    return "Carrera" if edad <= 30 else ("Puente" if edad <= 39 else "Rentas")


# ---------------- fiscalidad
def itsgf(base):
    """Impuesto de Solidaridad de las Grandes Fortunas (escala estatal), base = patrimonio neto en M€."""
    b = np.maximum(base - 0.7, 0)                       # mínimo exento de 700.000 €
    t = np.zeros_like(b)
    tramos = [(3.0, 5.347998, .017), (5.347998, 10.695996, .021), (10.695996, 1e9, .035)]
    for lo, hi, r in tramos:
        t += np.clip(b - lo, 0, hi - lo) * r
    return t


def neto_francia(bruto):
    """Del bruto al neto en Francia con el régimen de impatriados (art. 155 B), calibrado con el caso anterior:
    8 M€ brutos -> 0,85 M€ de cotizaciones y 2,6 M€ de impuesto."""
    return bruto * (1 - 0.85 / 8 - 2.6 / 8)


SUPUESTOS = dict(
    bruto_contrato=13.6, bruto_segunda=6.0, gasto_hoy=1.5,
    pisos0=14.0, liquido0=6.0, colchon=3.0,
    rent_bruta_pisos=0.05, gastos_pisos=0.25, irnr=0.19, irpf_alquiler=0.22,
    revalorizacion_pisos=0.025, vol_pisos=0.08, coste_compra_pisos=0.07,
    coste_cartera=0.009, impuesto_rescate=0.28, prima_seguro=0.0125,
    objetivo_inmuebles=0.45, agencia=((33, 1.5), (34, 1.0), (35, 1.0)),
    compras_pisos=((27, 1.0), (28, 1.0), (29, 1.0), (30, 1.0), (31, 1.0), (32, 1.0)),
    rent_colchon=0.022, haircut_venta_pisos=0.10, indexar_itsgf=True,
)


def simular(gasto_retiro_hoy, n=10000, semilla=11, lesion_edad=None, con_seguro=True, con_colchon=True,
            deterministico=False, carteras=None, compra_pisos=True, regla_flexible=False, residencia_retiro='ES', compra_ya=0.0, **cambios):
    """Simula n escenarios. gasto_retiro_hoy: gasto anual desde la retirada, en M€ de hoy.
    lesion_edad: si se da, deja de cobrar a esa edad y se retira (vuelve a España)."""
    S = dict(SUPUESTOS); S.update(cambios)
    carteras = carteras or CARTERAS
    rng = np.random.default_rng(semilla)
    T = len(EDADES); K = len(L.ORDEN)
    mu = np.log(1 + L.COMP)
    if deterministico:
        n = 1
        z = np.zeros((n, T, K))
    else:
        Lc = np.linalg.cholesky(L.R)
        z = rng.standard_normal((n, T, K)) @ Lc.T
    logr = mu + z * L.VOL                                   # rentabilidades logarítmicas por activo
    rend = np.exp(logr) - 1
    i_core = L.ORDEN.index("corere")
    aprec = np.exp(np.log(1 + S["revalorizacion_pisos"]) + z[:, :, i_core] * S["vol_pisos"]) - 1

    retiro = 33 if lesion_edad is None else lesion_edad
    F = np.full(n, S["liquido0"] - (S["colchon"] if con_colchon else 0.0))   # cartera financiera
    B = F.copy()                                            # base de coste (lo aportado)
    C = np.full(n, S["colchon"] if con_colchon else 0.0)    # colchón
    P = np.full(n, S["pisos0"])                             # pisos
    A = np.zeros(n)                                         # agencia (a coste)
    vivo = np.ones(n, bool)
    pend_seguro = np.zeros(n)                                # cobro del seguro pendiente (llega 12 meses después)
    tray = {k: np.zeros((n, T)) for k in ("F", "P", "C", "A", "W", "gasto", "impuesto_patr")}
    asegurado = [27.0, 21.6, 16.2, 10.8, 5.4]               # seguro decreciente, edades 26-30

    def retirar(F, B, neto, tipo):
        """Saca 'neto' de la cartera pagando impuesto sobre la parte de ganancia."""
        g = np.clip((F - B) / np.maximum(F, 1e-9), 0, 1)
        bruto = neto / (1 - tipo * g)
        frac = np.minimum(bruto / np.maximum(F, 1e-9), 1)
        return F - bruto, B * (1 - frac), bruto

    for j, edad in enumerate(EDADES):
        idx = (1 + INFL) ** (edad - 26)                     # índice de precios (26 = hoy)
        w = np.array([carteras[cartera_por_edad(edad)].get(k, 0) for k in L.ORDEN])
        r_cart = rend[:, j, :] @ w - S["coste_cartera"]
        residente_es = edad >= retiro

        # --- ingresos y gastos del año
        if edad < retiro:
            bruto = S["bruto_contrato"] if edad <= 30 else S["bruto_segunda"]
            ingreso = neto_francia(bruto)
            gasto = S["gasto_hoy"] * idx
            prima = S["prima_seguro"] * asegurado[edad - 26] if (con_seguro and edad <= 30) else 0.0
            ix = idx if S['indexar_itsgf'] else 1.0
            imp_patr = itsgf(P / ix) * ix                    # Solidaridad sobre los pisos como no residente
            alquiler = P * S["rent_bruta_pisos"] * (1 - S["gastos_pisos"]) * (1 - S["irnr"])
            flujo = ingreso - gasto - prima - imp_patr + alquiler
            for e_c, imp_c in S.get("compras_pisos", ()):
                if edad == e_c:
                    # compra de pisos en España siendo no residente (con sus costes de compra)
                    F = F - imp_c * (1 + S["coste_compra_pisos"]); B = B - imp_c * (1 + S["coste_compra_pisos"]); P = P + imp_c
            if compra_ya and edad == 27:
                # compra de pisos en España siendo no residente (variante para comparar)
                F = F - compra_ya * (1 + S["coste_compra_pisos"]); B = B - compra_ya * (1 + S["coste_compra_pisos"]); P = P + compra_ya
            # el colchón cubre si hiciera falta; el resto va a la cartera
            F = F + np.maximum(flujo, 0); B = B + np.maximum(flujo, 0)
            falta = np.maximum(-flujo, 0)
            F, B, _ = retirar(F, B, falta, 0.30)
        else:
            if edad == retiro:
                # vuelve a España: el colchón pasa a la cartera Puente
                F = F + C; B = B + C; C = C * 0
                if compra_pisos and residencia_retiro == 'ES':
                    W0 = F + P + A
                    w_reits = carteras[cartera_por_edad(edad)].get("reits", 0)
                    # compra X en pisos para que pisos + REITs = 40 % del patrimonio
                    X = (S["objetivo_inmuebles"] * W0 - P - w_reits * F) / (1 - w_reits * (1 + S["coste_compra_pisos"]))
                    X = np.clip(X, 0, 0.5 * F)
                    F, B, _ = retirar(F, B, X * (1 + S["coste_compra_pisos"]), S["impuesto_rescate"])
                    P = P + X
            for e_ag, imp in S["agencia"]:
                if edad == e_ag:
                    F, B, _ = retirar(F, B, np.full(n, imp), S["impuesto_rescate"]); A = A + imp
            gasto = gasto_retiro_hoy * idx
            if edad == retiro:
                F_ref = (F + P) / idx                        # patrimonio real al retirarse (referencia de la regla)
            if regla_flexible and edad > retiro:
                # regla de gasto: si el patrimonio real cae por debajo del 80 % del de la retirada, ese año gasta un 15 % menos
                gasto = np.where((F + P) / idx < 0.8 * F_ref, 0.85 * gasto, gasto)
            alquiler = P * S["rent_bruta_pisos"] * (1 - S["gastos_pisos"]) * (1 - S["irpf_alquiler"])
            Wt = F + P + A
            ix = idx if S['indexar_itsgf'] else 1.0
            if residencia_retiro == 'FR':
                # sigue en Francia: en España solo tributan los pisos (Solidaridad como no residente)
                alquiler = P * S["rent_bruta_pisos"] * (1 - S["gastos_pisos"]) * (1 - S["irnr"])
                imp_patr = itsgf(P / ix) * ix
                necesidad = np.maximum(gasto + imp_patr - alquiler, 0)
                F, B, _ = retirar(F, B, necesidad, 0.30)
                formula = None
            else:
                formula = itsgf(Wt / ix) * ix                   # tramos actualizados con la inflación
            if formula is not None:
              # límite conjunto: IRPF + patrimonio <= 60 % de la base, con un mínimo del 20 % de la cuota
              base = P * S["rent_bruta_pisos"] * (1 - S["gastos_pisos"]) + 0.5 * np.maximum(gasto - alquiler, 0)
              irpf = P * S["rent_bruta_pisos"] * (1 - S["gastos_pisos"]) * S["irpf_alquiler"] + 0.5 * np.maximum(gasto - alquiler, 0) * S["impuesto_rescate"]
              imp_patr = np.maximum(0.2 * formula, np.minimum(formula, np.maximum(0.6 * base - irpf, 0)))
              necesidad = np.maximum(gasto + imp_patr - alquiler, 0)
              F, B, _ = retirar(F, B, necesidad, S["impuesto_rescate"])

        # seguro por lesión
        if lesion_edad is not None and con_seguro and edad == lesion_edad + 1 and lesion_edad <= 30:
            F = F + asegurado[lesion_edad - 26]; B = B + asegurado[lesion_edad - 26]

        # si la cartera se agota, se venden pisos
        agot = (F < 0) & (P > 0)
        F = np.where(agot, F + P * (1 - S["haircut_venta_pisos"]), F); B = np.where(agot, np.maximum(F, 0), B)
        P = np.where(agot, 0, P)
        vivo &= F > -1e-9
        # rentabilidades del año
        F = np.where(vivo, F * (1 + r_cart), 0)
        C = C * (1 + S["rent_colchon"])
        P = P * (1 + aprec[:, j])
        W = F + P + C + A
        for k, v in (("F", F), ("P", P), ("C", C), ("A", A), ("W", W), ("gasto", np.full(n, gasto) if np.ndim(gasto) == 0 else gasto),
                     ("impuesto_patr", imp_patr)):
            tray[k][:, j] = v
    tray["vivo"] = vivo
    return tray


def gasto_sostenible(confianza=0.90, n=10000, **kw):
    """Mayor gasto anual (M€ de hoy) con el que la cartera llega a los 95 en el % de escenarios indicado."""
    lo, hi = 0.2, 6.0
    for _ in range(26):
        m = (lo + hi) / 2
        ok = np.mean(simular(m, n=n, **kw)["vivo"]) >= confianza
        lo, hi = (m, hi) if ok else (lo, m)
    return lo


if __name__ == "__main__":
    for nombre, w in CARTERAS.items():
        c, v = L.stats(w); print(f"{nombre:8s} rentabilidad {c*100:.2f} % · volatilidad {v*100:.2f} %")
    print("Neto anual en Francia con 13,6 M€ brutos:", round(neto_francia(13.6), 2))
    t = simular(1.2, deterministico=True)
    i33 = list(EDADES).index(33)
    print("Determinista: patrimonio a los 33 (antes de compras) ~", round(float(t["W"][0, i33 - 1]), 1),
          "| cartera", round(float(t["F"][0, i33 - 1]), 1), "| pisos", round(float(t["P"][0, i33 - 1]), 1))
