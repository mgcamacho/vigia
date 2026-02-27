import argparse
import pandas as pd
from .nucleo import Vigia

def prima():
    parser = argparse.ArgumentParser(
        description="VIGÍA - Monitor estadístico adaptativo de ingestas"
    )
    parser.add_argument("archivo", help="Archivo CSV con histórico")
    parser.add_argument("--columna", required=True, help="Nombre de la columna numérica")
    parser.add_argument("--actual", type=float, required=True, help="Valor actual a evaluar")
    args = parser.parse_args()

    df = pd.read_csv(args.archivo)

    if args.columna not in df.columns:
        print(f"Error: la columna '{args.columna}' no existe.")
        return

    serie = df[args.columna]

    vigia = Vigia()
    resultado = vigia.evaluar(serie, args.actual)

    print("------ VIGÍA ------")
    print(f"Método: {resultado.metodo_utilizado}")
    print(f"Límite inferior: {resultado.limite_inferior}")
    print(f"Límite superior: {resultado.limite_superior}")
    print(f"Valor actual: {resultado.valor_actual}")
    print("Estado:", "ANOMALÍA" if resultado.es_anomalia else "NORMAL")