"""
Armado de la narrativa del informe municipal.

Reúne los textos e indicadores calculados por los analizadores
en un único diccionario listo para ser consumido por los exportadores.
"""
from __future__ import annotations

import pandas as pd

from src.data.analyzer import (
    agrupar_estados_para_informe,
    detectar_patrones_observaciones,
    estado_por_manzana,
    extraer_montos_deuda,
    totales_por_manzana,
)


def armar_narrativa(df: pd.DataFrame, nombre_barrio: str, fecha: str) -> dict:
    """
    Construye el diccionario de narrativa para el informe.

    Parámetros
    ----------
    df:
        DataFrame unificado con columnas TITULAR, COTITULAR, LOTE,
        DIRECCION, ESTADO, OBSERVACIONES, MANZANA.
    nombre_barrio:
        Nombre del barrio para encabezados y textos.
    fecha:
        Fecha del informe en formato libre (ej. "18 de mayo de 2026").

    Retorna
    -------
    dict
        {
            "titulo": str,
            "fecha": str,
            "introduccion": str,
            "total_lotes": int,
            "por_manzana": pd.DataFrame,
            "estado_general": dict,
            "estado_por_manzana": pd.DataFrame,
            "patrones_obs": dict,
            "montos_deuda": dict | None,
        }
    """
    return {
        "titulo": (
            f"Informe de Estado de Lotes y Escrituraciones – Barrio {nombre_barrio}"
        ),
        "fecha": fecha,
        "introduccion": (
            f"El presente informe detalla el estado actual de los lotes del "
            f"Barrio {nombre_barrio} y el avance en sus procesos de escrituración, "
            f"conforme a los registros del Servicio Público de la Vivienda y Hábitat "
            f"(SPVH) de la Municipalidad de Rosario."
        ),
        "total_lotes": len(df),
        "por_manzana": totales_por_manzana(df),
        "estado_general": agrupar_estados_para_informe(df),
        "estado_por_manzana": estado_por_manzana(df),
        "patrones_obs": detectar_patrones_observaciones(df),
        "montos_deuda": extraer_montos_deuda(df),
    }
