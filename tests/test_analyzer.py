"""
Tests de src/data/analyzer.py usando el Excel real de HUMITOS.
"""
from pathlib import Path

import pytest

from src.data.loader import cargar_excel
from src.data.analyzer import (
    totales_por_estado,
    totales_por_manzana,
    estado_por_manzana,
    agrupar_estados_para_informe,
    detectar_patrones_observaciones,
    extraer_montos_deuda,
)

EXCEL_PATH = Path(__file__).parent.parent / "excel" / "HUMITOS TOTAL.xlsx"


@pytest.fixture(scope="module")
def df():
    return cargar_excel(EXCEL_PATH)


# ─── totales_por_estado ───────────────────────────────────────────────────────

def test_totales_por_estado_escriturado(df):
    """ESCRITURADO debe tener 136 lotes según el GRAFICO."""
    totales = totales_por_estado(df)
    assert "ESCRITURADO" in totales, "Falta la clave ESCRITURADO"
    assert totales["ESCRITURADO"]["cantidad"] == 136, (
        f"Se esperaban 136 escriturados, se encontraron {totales['ESCRITURADO']['cantidad']}"
    )


def test_totales_por_estado_keys(df):
    """El diccionario debe tener las claves 'cantidad' y 'porcentaje'."""
    totales = totales_por_estado(df)
    for estado, info in totales.items():
        assert "cantidad" in info, f"Falta 'cantidad' en {estado}"
        assert "porcentaje" in info, f"Falta 'porcentaje' en {estado}"


def test_totales_por_estado_porcentajes_suman_100(df):
    """Los porcentajes de todos los estados deben sumar ~100%."""
    totales = totales_por_estado(df)
    total_pct = sum(v["porcentaje"] for v in totales.values())
    assert abs(total_pct - 100.0) < 1.0, (
        f"Los porcentajes suman {total_pct}, se esperaba ~100"
    )


def test_totales_por_estado_deuda(df):
    """DEUDA debe tener 38 lotes."""
    totales = totales_por_estado(df)
    assert totales["DEUDA"]["cantidad"] == 38


# ─── agrupar_estados_para_informe ─────────────────────────────────────────────

def test_agrupar_cancelados(df):
    """Cancelados = CANCELADO (18) + CANCELADO-PP (8) = 26."""
    grupos = agrupar_estados_para_informe(df)
    assert "Cancelados" in grupos, "Falta el grupo 'Cancelados'"
    assert grupos["Cancelados"]["cantidad"] == 26, (
        f"Se esperaban 26 cancelados, se encontraron {grupos['Cancelados']['cantidad']}"
    )


def test_agrupar_escriturados(df):
    """Escriturados debe tener 136."""
    grupos = agrupar_estados_para_informe(df)
    assert grupos["Escriturados"]["cantidad"] == 136


def test_agrupar_con_deuda(df):
    """Con Deuda debe tener 38."""
    grupos = agrupar_estados_para_informe(df)
    assert grupos["Con Deuda"]["cantidad"] == 38


def test_agrupar_con_mejoras(df):
    """Con Mejoras debe tener 16."""
    grupos = agrupar_estados_para_informe(df)
    assert grupos["Con Mejoras"]["cantidad"] == 16


def test_agrupar_porcentajes_suman_100(df):
    """Los porcentajes agrupados deben sumar ~100%."""
    grupos = agrupar_estados_para_informe(df)
    total_pct = sum(v["porcentaje"] for v in grupos.values())
    assert abs(total_pct - 100.0) < 1.0


# ─── totales_por_manzana ──────────────────────────────────────────────────────

def test_totales_por_manzana_six_rows(df):
    """Debe haber exactamente 6 manzanas."""
    result = totales_por_manzana(df)
    assert len(result) == 6, f"Se esperaban 6 manzanas, se encontraron {len(result)}"


def test_totales_por_manzana_columns(df):
    """El DataFrame debe tener las columnas MANZANA y TOTAL."""
    result = totales_por_manzana(df)
    assert list(result.columns) == ["MANZANA", "TOTAL"]


def test_totales_por_manzana_manzana3_is_largest(df):
    """Manzana 3 debe tener la mayor cantidad de filas (59)."""
    result = totales_por_manzana(df)
    idx_max = result["TOTAL"].idxmax()
    assert result.loc[idx_max, "MANZANA"] == "Manzana 3", (
        f"Se esperaba 'Manzana 3' como la más grande, se encontró {result.loc[idx_max, 'MANZANA']}"
    )


def test_totales_por_manzana_sum_equals_total(df):
    """La suma de los totales por manzana debe igualar el total de filas del DataFrame."""
    result = totales_por_manzana(df)
    assert result["TOTAL"].sum() == len(df)


# ─── estado_por_manzana ───────────────────────────────────────────────────────

def test_estado_por_manzana_shape(df):
    """El pivot debe tener 6 filas (manzanas) y columnas por cada estado."""
    pivot = estado_por_manzana(df)
    assert pivot.shape[0] == 6
    assert "ESCRITURADO" in pivot.columns


def test_estado_por_manzana_no_nans(df):
    """No debe haber NaN en el pivot (se rellenan con 0)."""
    pivot = estado_por_manzana(df)
    assert not pivot.isnull().any().any()


# ─── detectar_patrones_observaciones ─────────────────────────────────────────

def test_detectar_plan_original(df):
    """Debe detectar observaciones con 'Plan original'."""
    patrones = detectar_patrones_observaciones(df)
    assert "Plan original" in patrones, "No se encontró el patrón 'Plan original'"
    assert patrones["Plan original"] > 0


def test_detectar_tanda(df):
    """Debe detectar observaciones con 'Tanda N'."""
    patrones = detectar_patrones_observaciones(df)
    assert "Tanda escrituración" in patrones, "No se encontró el patrón 'Tanda escrituración'"
    assert patrones["Tanda escrituración"] > 0


def test_detectar_copia_simple(df):
    """Debe detectar observaciones con 'copia simple'."""
    patrones = detectar_patrones_observaciones(df)
    assert "Copia simple" in patrones
    assert patrones["Copia simple"] > 0


def test_detectar_moratoria(df):
    """Debe detectar observaciones con 'Moratoria YYYY'."""
    patrones = detectar_patrones_observaciones(df)
    assert "Moratoria" in patrones
    assert patrones["Moratoria"] > 0


def test_detectar_solo_nonzero(df):
    """Solo se incluyen patrones con conteo > 0."""
    patrones = detectar_patrones_observaciones(df)
    for key, count in patrones.items():
        assert count > 0, f"El patrón '{key}' tiene conteo 0 pero fue incluido"


# ─── extraer_montos_deuda ─────────────────────────────────────────────────────

def test_extraer_montos_retorna_dict_o_none(df):
    """La función debe retornar un dict o None."""
    result = extraer_montos_deuda(df)
    assert result is None or isinstance(result, dict)


def test_extraer_montos_estructura_si_no_es_none(df):
    """Si retorna dict, debe tener las claves esperadas."""
    result = extraer_montos_deuda(df)
    if result is not None:
        assert "lotes_con_monto" in result
        assert "montos_detectados" in result
        assert "total_estimado" in result
        assert isinstance(result["montos_detectados"], list)
        assert isinstance(result["lotes_con_monto"], int)
        assert isinstance(result["total_estimado"], float)


def test_extraer_montos_total_coherente(df):
    """El total estimado debe ser la suma de los montos detectados."""
    result = extraer_montos_deuda(df)
    if result is not None:
        assert abs(result["total_estimado"] - sum(result["montos_detectados"])) < 0.01


# ─── Tests con datos Martinez Estrada ────────────────────────────────────────

MARTINEZ_PATH = Path(__file__).parent.parent / "excel" / "MARTINEZ ESTRADA TODOSdrive.xlsx"


@pytest.fixture(scope="module")
def df_martinez():
    return cargar_excel(MARTINEZ_PATH)


def test_martinez_totales_por_estado(df_martinez):
    """Debe tener exactamente dos estados: ESCRITURADO y NO ESCRITURADO."""
    totales = totales_por_estado(df_martinez)
    assert set(totales.keys()) == {"ESCRITURADO", "NO ESCRITURADO"}


def test_martinez_agrupar_estados(df_martinez):
    """Debe agrupar en Escriturados y No Escriturados, sin grupo Otros."""
    grupos = agrupar_estados_para_informe(df_martinez)
    assert "Escriturados" in grupos
    assert "No Escriturados" in grupos
    assert "Otros" not in grupos


def test_martinez_agrupar_porcentajes_suman_100(df_martinez):
    """Los porcentajes deben sumar ~100%."""
    grupos = agrupar_estados_para_informe(df_martinez)
    total_pct = sum(v["porcentaje"] for v in grupos.values())
    assert abs(total_pct - 100.0) < 1.0


def test_martinez_totales_por_manzana(df_martinez):
    """Debe haber 5 manzanas y sumar 157 lotes."""
    result = totales_por_manzana(df_martinez)
    assert len(result) == 5
    assert result["TOTAL"].sum() == 157


def test_martinez_estado_por_manzana(df_martinez):
    """Pivot debe tener 5 filas y columna ESCRITURADO."""
    pivot = estado_por_manzana(df_martinez)
    assert pivot.shape[0] == 5
    assert "ESCRITURADO" in pivot.columns
    assert not pivot.isnull().any().any()


def test_martinez_montos_deuda_none(df_martinez):
    """Sin estados DEUDA/CANCELADO, extraer_montos_deuda debe retornar None."""
    result = extraer_montos_deuda(df_martinez)
    assert result is None
