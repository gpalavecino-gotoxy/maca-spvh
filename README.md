# Generador de Informes de Lotes

Aplicación para generar informes de lotes de propiedades a partir de archivos Excel.

## Requisitos

- Windows 10 o superior
- Python 3.11 instalado (https://www.python.org/downloads/)

## Cómo usar la aplicación

### Primera vez

1. Hacer doble clic en `iniciar.bat`
2. El script va a crear automáticamente el entorno virtual e instalar todas las dependencias
3. Se abrirá el navegador con la aplicación

### Las veces siguientes

1. Hacer doble clic en `iniciar.bat`
2. Se abrirá el navegador con la aplicación

## Estructura del proyecto

```
maca/
├── app.py                   # Punto de entrada de la aplicación
├── iniciar.bat              # Script para iniciar la aplicación en Windows
├── requirements.txt         # Dependencias de Python
├── assets/
│   └── logos/               # Logos para los informes
│       ├── placeholder_municipalidad.png
│       └── placeholder_spvh.png
├── src/
│   ├── data/                # Módulos de lectura y procesamiento de datos
│   ├── report/              # Módulos de generación de informes
│   └── ui/                  # Componentes de la interfaz
└── tests/                   # Pruebas automatizadas
```

## Cómo reemplazar los logos

1. Preparar las imágenes en formato PNG (tamaño recomendado: 200x80 píxeles)
2. Reemplazar los archivos en la carpeta `assets/logos/`:
   - `placeholder_municipalidad.png` → logo de la municipalidad
   - `placeholder_spvh.png` → logo de SPVH

## Solución de problemas

- Si al hacer doble clic en `iniciar.bat` aparece un error de Python, asegurarse de tener Python 3.11 instalado y que esté en el PATH del sistema
- Si el navegador no se abre automáticamente, abrir manualmente `http://localhost:8501`
- Para cerrar la aplicación, cerrar la ventana de consola que se abrió con `iniciar.bat`
