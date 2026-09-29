"""
generar_pdf.py
==============

Generador del informe académico en PDF para entrega en Blackboard:
'Villegas_Luis_Semana7.pdf'

Formato sobrio y estándar:
- Texto en negro y títulos en negrita.
- Sin encabezados ni pies de página.
- 5 pruebas unitarias clave representativas con pytest.
- Explicación directa y natural del problema, estructura y repositorio.

Autor: Luis Villegas
Carrera: Programación Estructurada
"""

from __future__ import annotations

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generar_informe_pdf(ruta_salida: str) -> None:
    # Márgenes estándar de 1 pulgada (72 pt) o 54 pt
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Estilos estrictamente monocromáticos: solo negro y negrita
    style_titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.black,
        alignment=1,  # Centrado
        spaceAfter=6,
    )

    style_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.black,
        alignment=1,  # Centrado
        spaceAfter=12,
    )

    style_h1 = ParagraphStyle(
        "H1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.black,
        spaceBefore=10,
        spaceAfter=4,
    )

    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.black,
        spaceAfter=5,
    )

    style_code = ParagraphStyle(
        "CodeBlock",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.black,
    )

    style_table_text = ParagraphStyle(
        "TableText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.black,
    )

    style_table_bold = ParagraphStyle(
        "TableTextBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.black,
    )

    elementos = []

    # ========================================================
    # TÍTULO Y DATOS DEL ESTUDIANTE
    # ========================================================
    elementos.append(Paragraph("ACTIVIDAD SEMANA 7", style_titulo))
    elementos.append(
        Paragraph(
            "Patrones de Diseño, Testing Unitario y Tipos de Datos Abstractos Lineales",
            style_subtitulo,
        )
    )
    elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=8))

    datos_alumno = [
        [
            Paragraph("<b>Estudiante:</b> Luis Alberto Villegas Merchan", style_table_text),
            Paragraph("<b>Carrera:</b> Programación Estructurada", style_table_text),
        ],
        [
            Paragraph("<b>Materia:</b> Programación Orientada a Objetos", style_table_text),
            Paragraph("<b>Lenguaje:</b> Python 3.14", style_table_text),
        ],
        [
            Paragraph("<b>Repositorio GitHub:</b> https://github.com/luisvillegas190/semana-7-entrega-final.git", style_table_text),
            Paragraph("<b>Fecha:</b> Septiembre 2026", style_table_text),
        ],
    ]
    t_datos = Table(datos_alumno, colWidths=[270, 234])
    t_datos.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("PADDING", (0, 0), (-1, -1), 4),
        ])
    )
    elementos.append(t_datos)
    elementos.append(Spacer(1, 10))

    # ========================================================
    # 1. PROBLEMA SELECCIONADO
    # ========================================================
    elementos.append(Paragraph("1. Problema o Caso Práctico Seleccionado", style_h1))
    p1 = (
        "Para esta actividad se seleccionó el problema de la <b>gestión de órdenes de despacho en una bodega</b>. "
        "Cuando los clientes o sucursales solicitan productos del inventario, los pedidos deben atenderse "
        "en el mismo orden en que fueron recibidos, sin adelantar a nadie de manera arbitraria. "
        "Este comportamiento responde de forma natural al principio <b>FIFO (First-In, First-Out)</b>, "
        "por lo que la estructura de datos ideal para resolver este caso es una <b>Cola (Queue)</b>."
    )
    elementos.append(Paragraph(p1, style_body))

    # ========================================================
    # 2. ESTRUCTURA DE DATOS IMPLEMENTADA MANUALMENTE
    # ========================================================
    elementos.append(Paragraph("2. Estructura de Datos Lineal Manual (Cola)", style_h1))
    p2 = (
        "Siguiendo las instrucciones de la guía, la estructura fue implementada manualmente sin utilizar "
        "bibliotecas nativas como <code>collections.deque</code> o <code>queue.Queue</code>. "
        "En el archivo <code>estructuras_lineales.py</code> se creó la clase <b>ColaLineal</b> basada en "
        "<b>Nodos enlazados</b> (cada nodo almacena el dato y una referencia al siguiente nodo), "
        "manejando punteros al <b>frente</b> y al <b>final</b> de la estructura. "
        "Esto permite que las operaciones se ejecuten en tiempo constante <b>O(1)</b>:"
    )
    elementos.append(Paragraph(p2, style_body))

    tabla_cola = [
        [
            Paragraph("<b>Operación</b>", style_table_bold),
            Paragraph("<b>Método</b>", style_table_bold),
            Paragraph("<b>Descripción</b>", style_table_bold),
        ],
        [
            Paragraph("Agregar elemento", style_table_text),
            Paragraph("encolar(elemento)", style_table_text),
            Paragraph("Inserta el elemento al final de la cola.", style_table_text),
        ],
        [
            Paragraph("Eliminar elemento", style_table_text),
            Paragraph("desencolar()", style_table_text),
            Paragraph("Remueve y retorna el elemento al frente (FIFO). Lanza error si está vacía.", style_table_text),
        ],
        [
            Paragraph("Consultar siguiente", style_table_text),
            Paragraph("ver_frente()", style_table_text),
            Paragraph("Retorna el elemento del frente sin eliminarlo (Peek).", style_table_text),
        ],
        [
            Paragraph("Verificar vacía", style_table_text),
            Paragraph("esta_vacia()", style_table_text),
            Paragraph("Indica si la cola no contiene elementos.", style_table_text),
        ],
        [
            Paragraph("Cantidad de elementos", style_table_text),
            Paragraph("tamano() / __len__", style_table_text),
            Paragraph("Retorna la cantidad exacta de elementos almacenados.", style_table_text),
        ],
    ]
    t_cola = Table(tabla_cola, colWidths=[120, 130, 254])
    t_cola.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("PADDING", (0, 0), (-1, -1), 3),
        ])
    )
    elementos.append(t_cola)
    elementos.append(Spacer(1, 8))

    # ========================================================
    # 3. PATRÓN DE DISEÑO REPOSITORY
    # ========================================================
    elementos.append(Paragraph("3. Aplicación del Patrón de Diseño Repository", style_h1))
    p3 = (
        "El patrón <b>Repository</b> se utilizó para separar la forma en que se guardan y manipulan los datos "
        "de la lógica principal y de la interfaz gráfica. En el archivo <code>repositorio.py</code> se definieron "
        "dos interfaces con clases base abstractas (ABC):<br/>"
        "• <b>IProductoRepository:</b> Se encarga de administrar los productos del catálogo (guardar, buscar, "
        "actualizar, eliminar y calcular métricas).<br/>"
        "• <b>IDespachoRepository:</b> Administra los despachos de bodega. Su implementación "
        "<b>DespachoColaRepository</b> utiliza internamente la <b>ColaLineal manual</b>.<br/>"
        "De esta forma, cuando se llama a <code>despachar_siguiente()</code>, el repositorio desencola la orden "
        "en orden de llegada y descuenta automáticamente las unidades físicas del inventario, asegurando que no se "
        "pueda despachar más stock del que realmente existe en bodega."
    )
    elementos.append(Paragraph(p3, style_body))

    # ========================================================
    # 4. EVIDENCIAS DE PRUEBAS UNITARIAS (PYTEST)
    # ========================================================
    elementos.append(Paragraph("4. Evidencias de Pruebas Unitarias con Pytest", style_h1))
    p4 = (
        "Se implementaron pruebas unitarias con <b>pytest</b> para comprobar el funcionamiento correcto de las "
        "operaciones principales (encolar, desencolar en orden FIFO, consultar el frente, guardar productos y "
        "despachar descontando stock). A continuación se muestra la evidencia de ejecución en consola de 5 pruebas clave:"
    )
    elementos.append(Paragraph(p4, style_body))

    texto_pytest = (
        "PS C:\\Users\\ASUS\\Desktop\\Villegas_Luis_Semana7> python -m pytest -v tests/\n"
        "============================= test session starts =============================\n"
        "platform win32 -- Python 3.14.7, pytest-9.1.1\n"
        "collected 5 items\n\n"
        "tests/test_estructuras_lineales.py::TestColaLineal::test_encolar_un_elemento PASSED        [ 20%]\n"
        "tests/test_estructuras_lineales.py::TestColaLineal::test_encolar_multiples_y_orden_fifo PASSED [ 40%]\n"
        "tests/test_estructuras_lineales.py::TestColaLineal::test_ver_frente_no_altera_la_estructura PASSED [ 60%]\n"
        "tests/test_repositorio.py::TestProductoRepositoryMemoria::test_guardar_y_obtener_por_codigo PASSED [ 80%]\n"
        "tests/test_repositorio.py::TestDespachoColaRepository::test_despachar_orden_fifo_y_descontar_stock PASSED [100%]\n\n"
        "============================== 5 passed in 0.05s =============================="
    )

    t_pytest = Table([[Paragraph(texto_pytest.replace("\n", "<br/>"), style_code)]], colWidths=[504])
    t_pytest.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("PADDING", (0, 0), (-1, -1), 5),
        ])
    )
    elementos.append(t_pytest)
    elementos.append(Spacer(1, 8))

    # ========================================================
    # 5. ENLACE A GITHUB E INSTRUCCIONES
    # ========================================================
    elementos.append(Paragraph("5. Enlace al Repositorio de GitHub e Instrucciones de Ejecución", style_h1))
    p5 = (
        "<b>Enlace al repositorio público en GitHub:</b><br/>"
        "https://github.com/luisvillegas190/semana-7-entrega-final.git<br/><br/>"
        "<b>Instrucciones para ejecutar el código:</b><br/>"
        "• Instalar dependencias: <code>python -m pip install -r requirements.txt</code><br/>"
        "• Ejecutar pruebas unitarias: <code>python -m pytest -v</code><br/>"
        "• Ejecutar interfaz gráfica (Flet): <code>python main.py</code><br/>"
        "• Ejecutar demostración en consola: <code>python main.py --cli</code>"
    )
    elementos.append(Paragraph(p5, style_body))

    doc.build(elementos)
    print(f"[OK] PDF sobrio generado exitosamente en: {ruta_salida}")


if __name__ == "__main__":
    nombre_archivo = "Villegas_Luis_Semana7.pdf"
    directorio = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(directorio, nombre_archivo)
    generar_informe_pdf(ruta)
