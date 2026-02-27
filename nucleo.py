"""
VIGÍA
Herramienta ligera destinada al cotejo estadístico de variabilidad
en las series numéricas.

Bajo este módulo se articula un sistema práctico de detección de anomalías
para el seguimiento de métricas operativas (por ejemplo:
volumen de ingestas, registros diarios o cambios porcentuales).

VIGÍA estima los límites inferiores y superiores de la serie
partiendo de su comportamiento histórico, para lo cual selecciona
el método estadístico más idóneo según la naturaleza de la distribución.

Aunque podría aplicarse a cualquier serie numérica transformada,
su uso principal yace en el monitoreo de la volatilidad en los 
procesos de datos.
En un principio fue diseñada como herramienta de gobierno de datos.

Componentes principales:
- Vigia: motor principal de evaluación.
- ResultadoVigia: estructura de salida.
- Estrategias de límite: métodos estadísticos intercambiables.
"""

from .funciones import determinar_rango, estimar_comportamiento, determinar_limite, filtrar_extremos
import pandas as pd
from scipy.stats import skew, kurtosis
from scipy.signal import find_peaks
import numpy as np

class _EstrategiaLimite:
    def calcular(self, serie, superior: bool): pass

class _MetodoTresSigmas(_EstrategiaLimite):
    """
    Realiza arbitrio estadístico basado en dispersión clásica. Determina el
    umbral partiendo de la media y la desviación, suponiendo que los datos
    guardan una compostura de normalidad.
    """
    def calcular(auto, serie: pd.Series, superior: bool = True):
        desv, media = estimar_comportamiento(serie)
        limite = determinar_limite(media, desv, superior=superior)
        return limite
    
class _MetodoRangoAjustado(_EstrategiaLimite):
    """
    Destinado a series de comportamiento errático. Amalgama el límite de
    tres sigmas con el rango intercuartílico para ofrecer un umbral más
    tolerante ante distribuciones que poseen colas pesadas.
    """
    def calcular(auto, serie: pd.Series, superior: bool = True):
        desv, media = estimar_comportamiento(serie)
        limite_3s = determinar_limite(media, desv, superior=superior)
        rango_aj = determinar_rango(serie)
        cuan = np.nan_to_num(serie.quantile(0.9 if superior else 0.1))
        ajuste = abs((rango_aj + limite_3s) / 2)
        limite_aj = (cuan + ajuste) if superior else (cuan - ajuste)
        return limite_aj

class Vigia:
    """
    Detector adaptativo de anomalías para series numéricas históricas.

    A partir de una serie de referencia, estima un rango esperado
    (límite inferior y superior) y evalúa si un valor actual se
    encuentra dentro de dicho rango.

    El método de estimación se selecciona automáticamente según la
    curtosis de la distribución histórica, alternando entre:
    - Método Tres Sigmas (distribuciones regulares)
    - Método Rango Ajustado (distribuciones pesadas o multimodales)

    Fue concebido el motor para operar sobre series con previa transformación
    (por ejemplo: variación porcentual diaria), sin suponer el significado
    específico de la métrica que analiza.

    Adviértase que no es cometido de esta clase realizar agregaciones
    ni transformaciones internas. Estas tareas deben prepararse antes
    de invocar el método `evaluar()`.
    """
    def __init__(
            auto,
            registrador = None,
            umbral_curtosis: int = 100
    ):
        auto.registrador = registrador
        auto.umbral_curtosis = umbral_curtosis

    def __hallar_picos(
            auto,
            serie: pd.Series,
            interv: int = 40
    ):
        if len(serie) < 40:
            interv = max(1, min(40, len(serie) // 2))
        hist, _ = np.histogram(serie, bins=interv)
        total = sum(hist)
        picos, _ = find_peaks(
            np.concatenate(([0], hist, [0])),
            height=total * 0.1,
            distance=4)
        return picos

    def __diagnosticar_modalidad(
            auto,
            serie: pd.Series,
            limite: float,
    ):
        picos = auto.__hallar_picos(serie)
        sesgo = np.nan_to_num(skew(serie))
        modalidad = len(picos)
        if limite < -99:
            if sesgo > 1.5 or modalidad > 1:
                limite = -99
            else:
                limite = -90
        return limite

    def __seleccionar_metodo(
            auto,
            serie: pd.Series
    ):
        curtosis = kurtosis(serie)
        if curtosis > auto.umbral_curtosis:
            return _MetodoRangoAjustado()
        return _MetodoTresSigmas()

    def evaluar(
            auto,
            serie: pd.Series,
            valor_actual: float,
    ):
        """
        Evalúa si un valor actual se encuentra dentro del rango normal
        estimado a partir de la serie histórica.
        """
        serie = filtrar_extremos(serie)
        if len(serie) < 5:
            return ResultadoVigia(
                limite_inferior=np.nan, 
                limite_superior=np.nan, 
                valor_actual=valor_actual,
                es_anomalia=False, 
                metodo_utilizado="muestra_insuficiente"
            )
        estrategia = auto.__seleccionar_metodo(serie)
        limite_superior = estrategia.calcular(serie, superior=True)
        limite_inferior = estrategia.calcular(serie, superior=False)
        limite_inferior = auto.__diagnosticar_modalidad(serie, limite_inferior)
        anomalia = not (limite_inferior <= valor_actual <= limite_superior)
        return ResultadoVigia(
            limite_inferior=limite_inferior,
            limite_superior=limite_superior,
            valor_actual=valor_actual,
            es_anomalia=anomalia,
            metodo_utilizado=estrategia.__class__.__name__,
            actual=valor_actual
        )

class ResultadoVigia:
    """
    Contenedor de los productos del análisis.
    Preserva tanto el veredicto de anomalía como los hitos estadísticos que
    lo justifican.
    """
    __slots__ = ["limite_inferior", "limite_superior", "valor_actual",
                 "es_anomalia", "metodo_utilizado", "tendencia"]

    def __init__(
            auto,
            limite_inferior: float,
            limite_superior: float,
            valor_actual: float,
            es_anomalia: bool,
            metodo_utilizado: str,
            actual: float
    ):
        auto.limite_inferior = limite_inferior
        auto.limite_superior = limite_superior
        auto.valor_actual = valor_actual
        auto.es_anomalia = es_anomalia
        auto.metodo_utilizado = metodo_utilizado
        auto.tendencia = "INCREMENTO" if actual >= 0 else "DECREMENTO"
        
    def __repr__(auto):
        estado = " [ANOMALÍA - ROJO] " if auto.es_anomalia else " [OK - VERDE] "
        limite_relevante = auto.limite_superior if auto.valor_actual >= 0 else auto.limite_inferior
        return (
            f"{estado}\n"
            f"ResultadoVigia(limite={limite_relevante}, "
            f"actual={auto.valor_actual}, "
            f"tendencia={auto.tendencia}"
            f"metodo='{auto.metodo_utilizado}')"
        )
    
    def a_dicc(auto):
        """Convierte el resultado en un diccionario (útil para JSON o bases de datos)"""
        return {attr: getattr(auto, attr) for attr in auto.__slots__}
