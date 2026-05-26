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


def generar_pdf(docx_bytes: io.BytesIO) -> io.BytesIO:
    """
    Convierte un documento Word en memoria a PDF.

    Parámetros
    ----------
    docx_bytes:
        BytesIO con el contenido del .docx (salida de ``generar_word``).

    Retorna
    -------
    io.BytesIO
        Buffer con el PDF generado.

    Lanza
    -----
    RuntimeError
        Si la conversión falla, con el motivo detallado.
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


def _convertir_con_word(docx_path: Path, pdf_path: Path) -> io.BytesIO:
    try:
        from docx2pdf import convert
        convert(str(docx_path), str(pdf_path))
    except ImportError:
        raise RuntimeError(
            "El paquete 'docx2pdf' no está instalado. "
            "Ejecute: pip install docx2pdf"
        )
    except Exception as exc:
        raise RuntimeError(
            f"docx2pdf falló al convertir: {exc}"
        ) from exc

    if not pdf_path.exists():
        raise RuntimeError("docx2pdf no generó el archivo PDF.")

    buf = io.BytesIO(pdf_path.read_bytes())
    buf.seek(0)
    return buf


def _convertir_con_libreoffice(docx_path: Path, out_dir: Path) -> io.BytesIO:
    # Intentar con 'libreoffice' y como fallback 'soffice'
    for cmd in ("libreoffice", "soffice"):
        try:
            result = subprocess.run(
                [cmd, "--headless", "--convert-to", "pdf",
                 "--outdir", str(out_dir), str(docx_path)],
                capture_output=True,
                timeout=60,
            )
            break
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            raise RuntimeError("LibreOffice tardó más de 60 segundos y fue cancelado.")
    else:
        raise RuntimeError(
            "LibreOffice no está instalado o no se encuentra en el PATH. "
            "En Railway verifique que nixpacks.toml incluya 'libreoffice' en aptPkgs."
        )

    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace").strip()
        stdout = result.stdout.decode(errors="replace").strip()
        raise RuntimeError(
            f"LibreOffice terminó con error (código {result.returncode}).\n"
            f"stderr: {stderr or '(vacío)'}\n"
            f"stdout: {stdout or '(vacío)'}"
        )

    pdf_path = out_dir / "informe.pdf"
    if not pdf_path.exists():
        raise RuntimeError(
            "LibreOffice no generó el archivo PDF. "
            f"Archivos en directorio temporal: {list(out_dir.iterdir())}"
        )

    buf = io.BytesIO(pdf_path.read_bytes())
    buf.seek(0)
    return buf
