import pandas as pd
from scipy.stats import zscore
import numpy as np

def filtrar_extremos(
        serie: pd.Series,
        desv: int = 3
):
    puntaje_z = zscore(serie)
    serie = serie[(puntaje_z < desv) & (puntaje_z > -desv)]
    if len(serie) < 1:
        return pd.Series(dtype=float)
    return serie.dropna()

def estimar_comportamiento(
        serie: pd.Series
):
    desv = np.nan_to_num(np.std(serie))
    media = np.nan_to_num(serie.mean())
    return desv, media

def determinar_limite(
        media: float,
        desviacion: float,
        multi: int = 3,
        superior: bool = True
):
    multi = multi if superior else -multi
    limite = media + (multi * desviacion)
    return limite

def determinar_rango(
        serie: pd.Series
):
    rango_ajustado = np.nan_to_num(
        np.percentile(serie, 95) - np.percentile(serie, 5))
    return rango_ajustado