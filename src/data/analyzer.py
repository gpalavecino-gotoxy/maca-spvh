"""
Análisis y agrupación de datos del padrón municipal.
"""
from __future__ import annotations

import re

import pandas as pd


def totales_por_estado(df: pd.DataFrame) -> dict:
    """
    Cuenta y calcula el porcentaje de cada valor único de ESTADO.

    Retorna
    -------
    dict
        ``{estado: {'cantidad': int, 'porcentaje': float}}``
    """
    total = len(df)
    if total == 0:
        return {}

    result: dict = {}
    for estado, count in df["ESTADO"].value_counts().items():
        result[estado] = {
            "cantidad": int(count),
            "porcentaje": round(count / total * 100, 1),
        }
    return result


def totales_por_manzana(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cuenta las filas por manzana, ordenadas por nombre de manzana.

    Retorna
    -------
    pd.DataFrame
        Con columnas ``['MANZANA', 'TOTAL']``.
    """
    counts = (
        df.groupby("MANZANA", sort=False)
        .size()
        .reset_index(name="TOTAL")
    )
    counts = counts.sort_values("MANZANA").reset_index(drop=True)
    return counts


def estado_por_manzana(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabla pivote: índice=MANZANA, columnas=ESTADO, valores=cantidad de filas.

    Los NaN se rellenan con 0.
    """
    pivot = (
        df.pivot_table(
            index="MANZANA",
            columns="ESTADO",
            aggfunc="size",
            fill_value=0,
        )
    )
    pivot.columns.name = None
    return pivot


# ─── Mapeo de estados a grupos para el informe formal ───────────────────────

_ESTADO_A_GRUPO: dict[str, str] = {
    "ESCRITURADO": "Escriturados",
    "CANCELADO": "Cancelados",
    "CANCELADO-PP": "Cancelados",
    "DEUDA": "Con Deuda",
    "MEJORAS": "Con Mejoras",
    "SIN DATOS": "Sin Datos",
}


def agrupar_estados_para_informe(df: pd.DataFrame) -> dict:
    """
    Agrupa estados en categorías para el informe formal.

    Retorna
    -------
    dict
        ``{grupo: {'cantidad': int, 'porcentaje': float}}``
    """
    total = len(df)
    if total == 0:
        return {}

    grupos: dict[str, int] = {}
    for estado, count in df["ESTADO"].value_counts(dropna=False).items():
        grupo = _ESTADO_A_GRUPO.get(str(estado).strip().upper() if estado is not None else "", "Otros")
        grupos[grupo] = grupos.get(grupo, 0) + int(count)

    return {
        grupo: {
            "cantidad": cantidad,
            "porcentaje": round(cantidad / total * 100, 1),
        }
        for grupo, cantidad in grupos.items()
    }


# ─── Detección de patrones en OBSERVACIONES ──────────────────────────────────

_OBSERVATION_PATTERNS: list[tuple[str, str]] = [
    ("Moratoria", r"moratoria\s+\d{4}"),
    ("Plan original", r"plan\s+original"),
    ("Tanda escrituración", r"tanda\s+\d+"),
    ("Herederos/Fallecidos", r"falleci|heredero|sucesi"),
    ("Copia simple", r"copia\s+simple"),
    ("Cuotas pendientes", r"\d+\s+cuotas?\s+pendientes?"),
    ("Sin datos", r"sin\s+datos"),
    ("Titular a localizar", r"buscar|no\s+(?:la\s+)?encontr"),
]


def detectar_patrones_observaciones(df: pd.DataFrame) -> dict:
    """
    Cuenta cuántas observaciones coinciden con cada patrón predefinido.

    Solo analiza filas donde OBSERVACIONES no es nulo.

    Retorna
    -------
    dict
        ``{clave_patron: cantidad}`` — solo incluye patrones con conteo > 0.
    """
    obs_series = df["OBSERVACIONES"].dropna().astype(str)

    result: dict = {}
    for key, pattern in _OBSERVATION_PATTERNS:
        count = obs_series.str.contains(pattern, flags=re.IGNORECASE, regex=True).sum()
        if count > 0:
            result[key] = int(count)
    return result


# ─── Extracción de montos de deuda ───────────────────────────────────────────

_AMOUNT_PATTERNS = [
    re.compile(r"\$\s*([\d.,]+)"),
    re.compile(r"\b(\d{3,}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)\b"),
]


def _parse_amount(raw: str) -> float | None:
    """Convierte una cadena con formato de peso argentino a float."""
    raw = raw.replace("$", "").strip()

    # Heurística: si hay coma, la coma es decimal y los puntos son miles (ej. "1.234,56")
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    else:
        # Solo puntos — pueden ser miles o decimal
        # Si termina con ".XX" (1-2 dígitos), es decimal; sino es miles
        parts = raw.split(".")
        if len(parts) > 1 and len(parts[-1]) <= 2:
            raw = "".join(parts[:-1]) + "." + parts[-1]
        else:
            raw = raw.replace(".", "")

    try:
        return float(raw)
    except ValueError:
        return None


def extraer_montos_deuda(df: pd.DataFrame) -> dict | None:
    """
    Intenta extraer montos de deuda de las OBSERVACIONES de filas relevantes.

    Solo opera sobre filas con ESTADO en ``{"DEUDA", "CANCELADO", "CANCELADO-PP"}``.

    Retorna
    -------
    dict | None
        ``{'lotes_con_monto': int, 'montos_detectados': list[float], 'total_estimado': float}``
        o ``None`` si no se encuentran montos.
    """
    estados_relevantes = {"DEUDA", "CANCELADO", "CANCELADO-PP"}
    mask = df["ESTADO"].isin(estados_relevantes)
    subset = df[mask]

    montos: list[float] = []
    lotes_con_monto = 0

    for obs in subset["OBSERVACIONES"].dropna().astype(str):
        found_in_row: list[float] = []

        # Intentar primero el patrón con $
        for m in _AMOUNT_PATTERNS[0].finditer(obs):
            val = _parse_amount(m.group(1))
            if val is not None and val > 0:
                found_in_row.append(val)

        # Si no encontró con $, intentar números sueltos grandes
        # Excluir años (1900-2100) que no son montos
        if not found_in_row:
            for m in _AMOUNT_PATTERNS[1].finditer(obs):
                raw = m.group(1)
                val = _parse_amount(raw)
                if val is not None and val > 999 and not (1900 <= val <= 2100):
                    found_in_row.append(val)

        if found_in_row:
            lotes_con_monto += 1
            montos.extend(found_in_row)

    if not montos:
        return None

    return {
        "lotes_con_monto": lotes_con_monto,
        "montos_detectados": montos,
        "total_estimado": sum(montos),
    }
