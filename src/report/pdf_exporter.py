"""
Conversión de documentos Word a PDF para el informe municipal.

En Windows usa ``docx2pdf`` (requiere Microsoft Word).
En Linux usa LibreOffice headless (disponible en Railway vía nixpacks.toml).
"""
from __future__ import annotations

import io
import subprocess
import sys
import tempfile
from pathlib import Path


def generar_pdf(docx_bytes: io.BytesIO) -> io.BytesIO | None:
    """
    Convierte un documento Word en memoria a PDF.

    Parámetros
    ----------
    docx_bytes:
        BytesIO con el contenido del .docx (salida de ``generar_word``).

    Retorna
    -------
    io.BytesIO | None
        Buffer con el PDF generado, o None si la conversión no está disponible.
    """
    docx_bytes.seek(0)
    raw = docx_bytes.read()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        docx_path = tmp / "informe.docx"
        docx_path.write_bytes(raw)

        if sys.platform == "win32":
            return _convertir_con_word(docx_path, tmp / "informe.pdf")
        else:
            return _convertir_con_libreoffice(docx_path, tmp)


def _convertir_con_word(docx_path: Path, pdf_path: Path) -> io.BytesIO | None:
    try:
        from docx2pdf import convert
        convert(str(docx_path), str(pdf_path))
        buf = io.BytesIO(pdf_path.read_bytes())
        buf.seek(0)
        return buf
    except Exception:
        return None


def _convertir_con_libreoffice(docx_path: Path, out_dir: Path) -> io.BytesIO | None:
    try:
        result = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf",
             "--outdir", str(out_dir), str(docx_path)],
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0:
            return None
        pdf_path = out_dir / "informe.pdf"
        if not pdf_path.exists():
            return None
        buf = io.BytesIO(pdf_path.read_bytes())
        buf.seek(0)
        return buf
    except Exception:
        return None
