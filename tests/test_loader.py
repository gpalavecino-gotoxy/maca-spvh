"""
Tests de integración para src/data/loader.py usando el Excel real.
"""
from pathlib import Path

import pytest

from src.data.loader import cargar_excel

EXCEL_PATH = Path(__file__).parent.parent / "excel" / "HUMITOS TOTAL.xlsx"

EXPECTED_COLUMNS = ["TITULAR", "COTITULAR", "LOTE", "DIRECCION", "ESTADO", "OBSERVACIONES", "MANZANA"]


@pytest.fixture(scope="module")
def df():
    return cargar_excel(EXCEL_PATH)


def test_total_rows(df):
    """Deben cargarse exactamente 220 filas (6 manzanas, sin encabezados ni totales)."""
    assert len(df) == 220, f"Se esperaban 220 filas, se encontraron {len(df)}"


def test_columns_present(df):
    """El DataFrame debe tener exactamente las columnas requeridas."""
    for col in EXPECTED_COLUMNS:
        assert col in df.columns, f"Columna ausente: {col}"


def test_manzana_column_populated(df):
    """La columna MANZANA debe estar completamente poblada y tener 6 valores únicos."""
    assert df["MANZANA"].notna().all(), "La columna MANZANA tiene valores nulos"
    manzanas = sorted(df["MANZANA"].unique())
    assert len(manzanas) == 6, f"Se esperaban 6 manzanas, se encontraron {len(manzanas)}"
    assert manzanas == ["Manzana 1", "Manzana 2", "Manzana 3", "Manzana 4", "Manzana 5", "Manzana 6"]


def test_grafico_sheet_excluded(df):
    """La hoja GRAFICO no debe aparecer en los datos."""
    assert "GRAFICO" not in df["MANZANA"].values
    # Tampoco como parte de un nombre
    assert not df["MANZANA"].str.upper().str.contains("GRAFICO").any()


def test_total_rows_filtered_out(df):
    """Las filas cuyo TITULAR sea 'Total' no deben estar presentes."""
    titulares_lower = df["TITULAR"].astype(str).str.strip().str.lower()
    assert not (titulares_lower == "total").any(), (
        "Se encontraron filas con TITULAR='Total' que debían ser filtradas"
    )


def test_estado_normalized(df):
    """Los valores de ESTADO deben estar en mayúsculas y sin espacios extremos."""
    estados_no_nulos = df["ESTADO"].dropna()
    for estado in estados_no_nulos:
        assert estado == estado.strip().upper(), (
            f"ESTADO no normalizado: {estado!r}"
        )


def test_raises_on_invalid_path():
    """Debe lanzar ValueError si el archivo no existe."""
    with pytest.raises(ValueError, match="No se pudo leer"):
        cargar_excel("archivo_que_no_existe.xlsx")


def test_six_manzanas_loaded(df):
    """Deben cargarse exactamente 6 manzanas."""
    assert df["MANZANA"].nunique() == 6
