"""
Carga y normalización de datos desde archivos Excel municipales.
"""
from __future__ import annotations

import re
from pathlib import Path

import openpyxl
import pandas as pd

# Columnas esperadas en cada hoja Manzana
_EXPECTED_COLUMNS = ["TITULAR", "COTITULAR", "LOTE", "DIRECCION", "ESTADO", "OBSERVACIONES"]

# Patrón para identificar hojas válidas
_SHEET_PATTERN = re.compile(r"^Manzana\s+\d+$", re.IGNORECASE)


def cargar_excel(path: str | Path) -> pd.DataFrame:
    """
    Lee un archivo Excel con hojas tipo 'Manzana N' y devuelve un DataFrame unificado.

    Parámetros
    ----------
    path : str | Path
        Ruta al archivo Excel.

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas: TITULAR, COTITULAR, LOTE, DIRECCION, ESTADO,
        OBSERVACIONES, MANZANA.

    Lanza
    -----
    ValueError
        Si el archivo no puede leerse, no tiene hojas 'Manzana N', o alguna
        hoja no tiene las columnas requeridas.
    """
    path = Path(path)

    # Intentar abrir el workbook
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as exc:
        raise ValueError(
            f"No se pudo leer el archivo '{path}': {exc}"
        ) from exc

    # Filtrar hojas que coincidan con "Manzana N"
    manzana_sheets = [name for name in wb.sheetnames if _SHEET_PATTERN.match(name)]

    if not manzana_sheets:
        raise ValueError(
            f"No se encontraron hojas con formato 'Manzana N' en '{path}'. "
            f"Hojas disponibles: {wb.sheetnames}"
        )

    frames: list[pd.DataFrame] = []

    for sheet_name in manzana_sheets:
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))

        if not rows:
            raise ValueError(
                f"La hoja '{sheet_name}' está vacía y no tiene fila de encabezado."
            )

        # La primera fila es el encabezado; las demás son datos
        header_row = rows[0]
        data_rows = rows[1:]

        # Construir DataFrame con las columnas del encabezado
        header = [str(c).strip() if c is not None else "" for c in header_row]

        # Verificar columnas requeridas
        missing = [col for col in _EXPECTED_COLUMNS if col not in header]
        if missing:
            raise ValueError(
                f"La hoja '{sheet_name}' no tiene las columnas requeridas: {missing}. "
                f"Columnas encontradas: {header}"
            )

        # Construir filas usando las posiciones de las columnas esperadas
        col_idx = {col: header.index(col) for col in _EXPECTED_COLUMNS}

        records = []
        for row in data_rows:
            titular = row[col_idx["TITULAR"]]

            # Filtrar filas sin titular
            if titular is None or str(titular).strip() == "":
                continue

            # Filtrar filas de total
            if str(titular).strip().lower() == "total":
                continue

            estado = row[col_idx["ESTADO"]]
            if estado is not None:
                estado = str(estado).strip().upper()

            records.append({
                "TITULAR": titular,
                "COTITULAR": row[col_idx["COTITULAR"]],
                "LOTE": row[col_idx["LOTE"]],
                "DIRECCION": row[col_idx["DIRECCION"]],
                "ESTADO": estado,
                "OBSERVACIONES": row[col_idx["OBSERVACIONES"]],
                "MANZANA": sheet_name,
            })

        frames.append(pd.DataFrame(records, columns=_EXPECTED_COLUMNS + ["MANZANA"]))

    if not frames:
        raise ValueError(
            "No se encontraron datos válidos en ninguna hoja 'Manzana N'."
        )

    return pd.concat(frames, ignore_index=True)
