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


# ─── Tests formato Martinez Estrada (hoja única plana) ───────────────────────

MARTINEZ_PATH = Path(__file__).parent.parent / "excel" / "MARTINEZ ESTRADA TODOSdrive.xlsx"


@pytest.fixture(scope="module")
def df_martinez():
    return cargar_excel(MARTINEZ_PATH)


def test_martinez_total_rows(df_martinez):
    """157 filas de datos (fila Total filtrada)."""
    assert len(df_martinez) == 157, f"Se esperaban 157 filas, se encontraron {len(df_martinez)}"


def test_martinez_columns_present(df_martinez):
    """Debe tener las columnas estándar más LEGAJO."""
    for col in EXPECTED_COLUMNS:
        assert col in df_martinez.columns, f"Columna ausente: {col}"
    assert "LEGAJO" in df_martinez.columns


def test_martinez_manzana_values(df_martinez):
    """MANZANA debe tener exactamente 5 valores: Manzana A a Manzana E."""
    manzanas = sorted(df_martinez["MANZANA"].unique())
    assert manzanas == ["Manzana A", "Manzana B", "Manzana C", "Manzana D", "Manzana E"]


def test_martinez_estado_values(df_martinez):
    """ESTADO solo debe contener ESCRITURADO y NO ESCRITURADO."""
    estados = set(df_martinez["ESTADO"].dropna().unique())
    assert estados == {"ESCRITURADO", "NO ESCRITURADO"}


def test_martinez_estado_normalized(df_martinez):
    """Los valores de ESTADO deben estar en mayúsculas y sin espacios."""
    for estado in df_martinez["ESTADO"].dropna():
        assert estado == estado.strip().upper(), f"ESTADO no normalizado: {estado!r}"


def test_martinez_titular_split(df_martinez):
    """Rows con ' - ' en TITULARES deben tener COTITULAR poblado."""
    has_cotitular = df_martinez["COTITULAR"].notna().sum()
    assert has_cotitular > 0, "Se esperaba al menos una fila con COTITULAR"


def test_martinez_total_row_filtered(df_martinez):
    """La fila 'Total' no debe aparecer en los datos."""
    titulares_lower = df_martinez["TITULAR"].astype(str).str.strip().str.lower()
    assert not (titulares_lower == "total").any()


def test_martinez_manzana_column_populated(df_martinez):
    """Todas las filas deben tener MANZANA poblado."""
    assert df_martinez["MANZANA"].notna().all()
