"""Hipótesis de J.P. Morgan AM, Long-Term Capital Market Assumptions 2026, en euros.
Valores: rentabilidad compuesta 2026 (%), aritmética (%), volatilidad (%). Correlaciones de la matriz en euros."""
import numpy as np

ACTIVOS = {
    # clave: (nombre, compuesta, aritmética, volatilidad)
    "cash":   ("Liquidez euro", 2.30, 2.30, 0.64),
    "govt":   ("Deuda pública euro", 3.40, 3.54, 5.34),
    "ig":     ("Crédito euro grado de inversión", 4.00, 4.12, 4.93),
    "ilb":    ("Bonos ligados a la inflación euro", 3.60, 3.77, 5.98),
    "multi":  ("Renta fija global cubierta (Multiverse)", 3.80, 3.87, 3.88),
    "dev":    ("Renta variable desarrollada", 6.30, 7.29, 14.69),
    "em":     ("Renta variable emergente", 7.20, 8.48, 16.78),
    "euro":   ("Renta variable zona euro", 7.20, 8.53, 17.13),
    "reits":  ("Inmobiliario cotizado global (REITs)", 8.10, 8.95, 13.70),
    "corere": ("Inmobiliario directo europeo (core)", 6.30, 6.84, 10.83),
    "infra":  ("Infraestructura core", 5.90, 6.51, 11.48),
    "gold":   ("Oro", 4.90, 6.03, 15.63),
}
ORDEN = list(ACTIVOS)
_C = {
 ("cash","govt"):.20,("cash","ig"):.09,("cash","ilb"):.11,("cash","multi"):.21,("cash","dev"):-.16,("cash","em"):-.09,("cash","euro"):-.11,("cash","corere"):-.28,("cash","reits"):-.17,("cash","infra"):-.17,("cash","gold"):.10,
 ("govt","ig"):.72,("govt","ilb"):.74,("govt","multi"):.87,("govt","dev"):.21,("govt","em"):.12,("govt","euro"):.19,("govt","corere"):-.19,("govt","reits"):.31,("govt","infra"):-.13,("govt","gold"):.13,
 ("ig","ilb"):.73,("ig","multi"):.78,("ig","dev"):.54,("ig","em"):.51,("ig","euro"):.53,("ig","corere"):.06,("ig","reits"):.58,("ig","infra"):.07,("ig","gold"):.07,
 ("ilb","multi"):.68,("ilb","dev"):.41,("ilb","em"):.33,("ilb","euro"):.44,("ilb","corere"):.03,("ilb","reits"):.49,("ilb","infra"):.07,("ilb","gold"):.09,
 ("multi","dev"):.26,("multi","em"):.25,("multi","euro"):.30,("multi","corere"):-.18,("multi","reits"):.39,("multi","infra"):-.11,("multi","gold"):.19,
 ("dev","em"):.71,("dev","euro"):.84,("dev","corere"):.48,("dev","reits"):.84,("dev","infra"):.38,("dev","gold"):-.10,
 ("em","euro"):.71,("em","corere"):.49,("em","reits"):.65,("em","infra"):.31,("em","gold"):.01,
 ("euro","corere"):.33,("euro","reits"):.73,("euro","infra"):.21,("euro","gold"):-.21,
 ("corere","reits"):.37,("corere","infra"):.36,("corere","gold"):.04,
 ("reits","infra"):.40,("reits","gold"):-.04,("infra","gold"):.14,
}
def corr(a,b):
    if a==b: return 1.0
    return _C.get((a,b), _C.get((b,a)))
R = np.array([[corr(a,b) for b in ORDEN] for a in ORDEN])
VOL = np.array([ACTIVOS[k][3] for k in ORDEN])/100
ARIT = np.array([ACTIVOS[k][2] for k in ORDEN])/100
COMP = np.array([ACTIVOS[k][1] for k in ORDEN])/100
COV = np.outer(VOL,VOL)*R

def stats(pesos):
    w = np.array([pesos.get(k,0) for k in ORDEN]); assert abs(w.sum()-1)<1e-9, w.sum()
    var = w@COV@w
    return float(w@ARIT - var/2), float(np.sqrt(var))

if __name__=="__main__":
    print("autovalor mínimo", np.linalg.eigvalsh(R).min())
