import argparse
import pandas as pd
from .nucleo import Vigia

def prima():
    """
    Constituye el punto de entrada al sistema VIGÍA, donde se conciertan 
    los parámetros del usuario con la lógica de evaluación estadística.
    """
    expositor = argparse.ArgumentParser(
        description="VIGÍA - Monitor estadístico adaptativo de ingestas"
    )
    expositor.add_argument("archivo", help="Archivo CSV con histórico")
    expositor.add_argument("--columna", required=True, help="Nombre de la columna numérica")
    expositor.add_argument("--actual", type=float, required=True, help="Valor actual a evaluar")
    argumentos = expositor.parse_args()

    datos = pd.read_csv(argumentos.archivo)

    if argumentos.columna not in datos.columns:
        print(f"Error: la columna '{argumentos.columna}' no existe.")
        return

    serie = datos[argumentos.columna]

    vigia = Vigia()
    veredicto = vigia.evaluar(serie, argumentos.actual)

    print("------ VIGÍA ------")
    print(f"Procedimiento seguido: {veredicto.metodo_utilizado}")
    print(f"Umbral inferior: {veredicto.limite_inferior}")
    print(f"Umbral superior: {veredicto.limite_superior}")
    print(f"Valor actual: {veredicto.valor_actual}")
    print("Estado:", "ANOMALÍA" if veredicto.es_anomalia else "NORMAL")