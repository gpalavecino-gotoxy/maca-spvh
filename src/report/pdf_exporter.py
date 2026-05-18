"""
Conversión de documentos Word a PDF para el informe municipal.

Intenta usar ``docx2pdf`` (requiere Microsoft Word instalado en Windows/macOS).
Si falla por cualquier motivo, devuelve None en lugar de propagar la excepción.
"""
from __future__ import annotations

import io
import os
import tempfile


def generar_pdf(docx_bytes: io.BytesIO) -> io.BytesIO | None:
    """
    Convierte un documento Word en memoria a PDF.

    Parámetros
    ----------
    docx_bytes:
        BytesIO con el contenido del .docx (salida de ``generar_word``).
        El puntero puede estar en cualquier posición; la función lo reposiciona.

    Retorna
    -------
    io.BytesIO | None
        Buffer con el PDF generado, o None si la conversión no está disponible
        (Word no instalado, plataforma no soportada, etc.).
    """
    try:
        from docx2pdf import convert  # importación diferida para no fallar en import

        docx_bytes.seek(0)
        raw = docx_bytes.read()

        # docx2pdf opera sobre archivos en disco, no sobre BytesIO
        with tempfile.TemporaryDirectory() as tmp_dir:
            docx_path = os.path.join(tmp_dir, "informe.docx")
            pdf_path = os.path.join(tmp_dir, "informe.pdf")

            with open(docx_path, "wb") as f:
                f.write(raw)

            convert(docx_path, pdf_path)

            with open(pdf_path, "rb") as f:
                pdf_data = f.read()

        buf = io.BytesIO(pdf_data)
        buf.seek(0)
        return buf

    except Exception:
        return None
