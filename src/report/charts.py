"""
Generación de gráficos para el informe municipal.

Provee dos sabores de cada gráfico:
- Plotly  → para el dashboard interactivo de Streamlit.
- Matplotlib → para insertar en documentos Word/PDF (devuelve BytesIO PNG).
"""
from __future__ import annotations

import io

import matplotlib
matplotlib.use("Agg")  # backend sin pantalla, necesario en servidor
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

# ─── Paleta de colores compartida ────────────────────────────────────────────

# Grupos de informe (salida de agrupar_estados_para_informe)
_COLOR_GRUPO: dict[str, str] = {
    "Escriturados": "#2E86AB",
    "Cancelados":   "#A8DADC",
    "Con Deuda":    "#E63946",
    "Con Mejoras":  "#F4A261",
    "Sin Datos":    "#ADB5BD",
    "Otros":        "#6C757D",
}

# Estados crudos del DataFrame (salida de estado_por_manzana)
_COLOR_ESTADO: dict[str, str] = {
    "ESCRITURADO":  "#2E86AB",
    "CANCELADO":    "#A8DADC",
    "CANCELADO-PP": "#85C1E9",
    "DEUDA":        "#E63946",
    "MEJORAS":      "#F4A261",
    "SIN DATOS":    "#ADB5BD",
}
_COLOR_ESTADO_DEFAULT = "#6C757D"


def _color_estado(estado: str) -> str:
    """Devuelve el color hex para un ESTADO crudo, con fallback a gris oscuro."""
    return _COLOR_ESTADO.get(str(estado).strip().upper(), _COLOR_ESTADO_DEFAULT)


# ─── Gráficos Plotly ─────────────────────────────────────────────────────────


def grafico_torta_estados_plotly(
    datos: dict,
    titulo: str = "Estado General de Lotes",
) -> go.Figure:
    """
    Gráfico de torta (pie) con los grupos de estado del informe.

    Parámetros
    ----------
    datos:
        Salida de ``agrupar_estados_para_informe()``.
        Formato: ``{grupo: {'cantidad': int, 'porcentaje': float}}``.
    titulo:
        Título del gráfico.

    Retorna
    -------
    go.Figure
        Figura Plotly lista para mostrar en Streamlit.
    """
    labels = list(datos.keys())
    values = [v["cantidad"] for v in datos.values()]
    colors = [_COLOR_GRUPO.get(label, _COLOR_ESTADO_DEFAULT) for label in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=1.5)),
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>%{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            xanchor="center",
            font=dict(size=18, family="Arial", color="#333333"),
        ),
        legend=dict(orientation="v", x=1.02, y=0.5),
        margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
    )

    return fig


def grafico_barras_por_manzana_plotly(
    df_pivot: pd.DataFrame,
    titulo: str = "Estado de Lotes por Manzana",
) -> go.Figure:
    """
    Gráfico de barras apiladas por manzana.

    Parámetros
    ----------
    df_pivot:
        Salida de ``estado_por_manzana()``.
        Índice = MANZANA, columnas = ESTADO (valores crudos), valores = cantidad.
    titulo:
        Título del gráfico.

    Retorna
    -------
    go.Figure
        Figura Plotly lista para mostrar en Streamlit.
    """
    manzanas = df_pivot.index.tolist()
    estados = df_pivot.columns.tolist()

    traces = []
    for estado in estados:
        traces.append(
            go.Bar(
                name=str(estado),
                x=manzanas,
                y=df_pivot[estado].tolist(),
                marker_color=_color_estado(str(estado)),
                hovertemplate=f"<b>%{{x}}</b><br>{estado}: %{{y}}<extra></extra>",
            )
        )

    fig = go.Figure(data=traces)

    fig.update_layout(
        barmode="stack",
        title=dict(
            text=titulo,
            x=0.5,
            xanchor="center",
            font=dict(size=18, family="Arial", color="#333333"),
        ),
        xaxis=dict(title="Manzana", tickangle=-45),
        yaxis=dict(title="Cantidad de Lotes"),
        legend=dict(title="Estado", orientation="v", x=1.02, y=0.5),
        margin=dict(t=60, b=100, l=60, r=20),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8F9FA",
    )

    return fig


# ─── Gráficos Matplotlib (para Word/PDF) ─────────────────────────────────────


def grafico_torta_estados_matplotlib(
    datos: dict,
    titulo: str = "Estado General de Lotes",
) -> io.BytesIO:
    """
    Gráfico de torta (pie) con los grupos de estado, en formato PNG.

    Parámetros
    ----------
    datos:
        Salida de ``agrupar_estados_para_informe()``.
    titulo:
        Título del gráfico.

    Retorna
    -------
    io.BytesIO
        Buffer con el PNG listo para insertar en un documento Word/PDF.
    """
    labels = list(datos.keys())
    values = [v["cantidad"] for v in datos.values()]
    colors = [_COLOR_GRUPO.get(label, _COLOR_ESTADO_DEFAULT) for label in labels]

    fig, ax = plt.subplots(figsize=(7, 5))

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops=dict(edgecolor="white", linewidth=1.2),
    )

    for text in texts:
        text.set_fontsize(10)
        text.set_fontfamily("DejaVu Sans")

    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    ax.set_title(titulo, fontsize=14, fontweight="bold", pad=15, color="#333333")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def grafico_barras_por_manzana_matplotlib(
    df_pivot: pd.DataFrame,
    titulo: str = "Estado de Lotes por Manzana",
) -> io.BytesIO:
    """
    Gráfico de barras apiladas por manzana, en formato PNG.

    Parámetros
    ----------
    df_pivot:
        Salida de ``estado_por_manzana()``.
    titulo:
        Título del gráfico.

    Retorna
    -------
    io.BytesIO
        Buffer con el PNG listo para insertar en un documento Word/PDF.
    """
    manzanas = df_pivot.index.tolist()
    estados = df_pivot.columns.tolist()
    x = range(len(manzanas))

    fig, ax = plt.subplots(figsize=(10, 6))

    bottom = [0] * len(manzanas)
    for estado in estados:
        valores = df_pivot[estado].tolist()
        ax.bar(
            x,
            valores,
            bottom=bottom,
            color=_color_estado(str(estado)),
            label=str(estado),
            edgecolor="white",
            linewidth=0.5,
        )
        bottom = [b + v for b, v in zip(bottom, valores)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(manzanas, rotation=45, ha="right", fontsize=8)
    ax.set_xlabel("Manzana", fontsize=10)
    ax.set_ylabel("Cantidad de Lotes", fontsize=10)
    ax.set_title(titulo, fontsize=14, fontweight="bold", pad=15, color="#333333")
    ax.legend(title="Estado", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    ax.set_facecolor("#F8F9FA")
    ax.grid(axis="y", color="white", linewidth=0.8)

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf
