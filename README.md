# VIGÍA

**VIGÍA** es un instrumento de precisión destinado al cotejo estadístico y la detección de anomalías en series numéricas históricas.

Se concibe como herramienta práctica de monitoreo operativo. Puede emplearse para:

- Vigilar ingestas diarias.
- Controlar métricas internas.
- Detectar saltos inesperados en procesos automatizados.
- Servir de criterio preliminar antes de escalar una alerta.

Para diferenciarse de los sistemas de reglas rígidas, VIGÍA actúa como un centinela adaptativo: escruta la naturaleza de la distribución y selecciona, de forma autónoma, el arbitrio matemático que mejor se compagina con la realidad de los datos. No depende de modelos de aprendizaje automático, más bien se apoya en estadística descriptiva robusta.

> [!NOTE]
> An English localization will be included.

## Funcionamiento

Dada una serie histórica, el sistema:

1. Estima el comportamiento normal de la serie.
2. Calcula un límite inferior y un límite superior.
3. Evalúa si un valor actual cae dentro del rango calculado.
4. Indica la existencia de anomalía, si hubiere.

El sistema selecciona automáticamente el método de estimación según la forma de la distribución histórica.

## Capacidades Adaptativas

VIGÍA no juzga todas las métricas con el mismo rasero. Su motor interno alterna entre dos estrategias fundamentales según la curtosis de la muestra:

1. **Método de Tres Sigmas:** Aplicado cuando la serie guarda una compostura de normalidad y regularidad.
2. **Método de Rango Ajustado:** Invocado ante distribuciones de "cola pesada" o carácter multimodal, donde el rigor clásico resultaría insuficiente o erróneo.

## Instalación y Requisitos

El entorno debe contar con las siguientes librerías de cálculo:

```bash
pip install pandas scipy numpy
```

---

## Ejemplo de uso (Python)

```python
from vigia import Vigia
import pandas as pd

serie = pd.Series([100, 105, 102, 108, 110, 107]) # Serie de datos que será evaluada
vigia = Vigia()

# Analiza el histórico de la serie para modelar los límites
# y toma el valor más reciente para evaluar potenciales anomalías
resultado = vigia.evaluar(serie[:-1], serie.iloc[-1])

print(resultado)
```

## Intenciones

- Reducir o eliminar dependencias externas.
- Implementar versiones puramente basadas en la biblioteca estándar.
- Añadir interfaz de línea de comandos estable.
- Permitir salida estructurada en JSON.
- Incorporar pruebas estadísticas más formales cuando el tamaño muestral lo permita.
- Documentar criterios matemáticos con mayor detalle.
- Incluir una versión internacional (inglés).