"""
app.py
======

Interfaz Gráfica de Usuario (GUI) desarrollada con Flet para el Sistema de Bodega.

Actividad: Semana 7 — Patrones de Diseño, Testing Unitario y TDAs Lineales.
Materia: Programación Estructurada / Programación Orientada a Objetos
Estudiante: Luis Alberto Villegas Merchan

NUEVAS CARACTERÍSTICAS INTEGRADAS (SEMANA 7):
1. Arquitectura desacoplada basada en el Patrón Repository:
   - IProductoRepository (ProductoRepositoryMemoria) para gestión de inventario.
   - IDespachoRepository (DespachoColaRepository) que integra la 'ColaLineal' manual (FIFO).
2. Pestaña interactiva "Centro de Despachos (Cola FIFO)":
   - Encolar solicitudes de despacho verificando existencias físicas en tiempo real.
   - Visualización interactiva de la Cola Lineal manual (orden de turno, frente/peek).
   - Operación de Despacho FIFO con descuento automático de stock en bodega.
   - Historial de auditoría respaldado por la PilaLineal manual (LIFO).
3. Pestaña "Catálogo de Productos":
   - CRUD completo, filtros, validaciones con Pydantic y métricas globales.
"""

from __future__ import annotations

import flet as ft
from pydantic import ValidationError

from estructuras_lineales import ColaVaciaError
from modelo import Categoria, PedidoDespacho, Producto
from repositorio import (
    DespachoColaRepository,
    ProductoRepositoryJSON,
    ProductoRepositoryMemoria,
)


def crear_aplicacion(page: ft.Page) -> None:
    """Configura y orquesta la interfaz gráfica Flet con el patrón Repository y Persistencia JSON."""

    # 1. Configuración de la ventana principal
    page.title = "Sistema de Bodega — Patrones de Diseño, TDAs Lineales y Persistencia JSON (Examen Final)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 16
    page.window.width = 1250
    page.window.height = 840
    page.window.min_width = 950
    page.window.min_height = 700

    # 2. Inicialización de Repositorios con Persistencia JSON Física en Disco (Requisito Examen Final)
    repo_productos = ProductoRepositoryJSON("data/productos.json", inicializar_demo=True)
    repo_despachos = DespachoColaRepository(
        producto_repo=repo_productos,
        ruta_archivo="data/despachos.json",
        inicializar_demo=True,
    )

    # Categorías y configuración
    cat_acc = Categoria("CAT-ACC", "Accesorios")
    cat_elec = Categoria("CAT-ELE", "Electrónica")
    cat_her = Categoria("CAT-HER", "Herramientas")
    cat_red = Categoria("CAT-RED", "Redes y Conectividad")
    cat_alm = Categoria("CAT-ALM", "Almacenamiento")

    categorias_disponibles = [cat_acc, cat_elec, cat_her, cat_red, cat_alm]
    mapa_categorias = {cat.get_nombre(): cat for cat in categorias_disponibles}

    def calcular_siguiente_id() -> str:
        todos = repo_despachos.listar_pendientes() + repo_despachos.listar_historial()
        ids = []
        for ped in todos:
            pid = ped.get_id_pedido()
            if pid.startswith("ORD-"):
                try:
                    ids.append(int(pid.replace("ORD-", "")))
                except ValueError:
                    pass
        siguiente = (max(ids) + 1) if ids else 101
        return f"ORD-{siguiente}"

    # FUNCIÓN AUXILIAR DE NOTIFICACIÓN (SnackBar)
    def notificar(mensaje: str, es_error: bool = False) -> None:
        snack = ft.SnackBar(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.ERROR_OUTLINE if es_error else ft.Icons.CHECK_CIRCLE_OUTLINE,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(mensaje, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ]),
            bgcolor=ft.Colors.RED_700 if es_error else ft.Colors.GREEN_700,
            duration=3500,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # ========================================================
    # SECCIÓN 1: CONTROLES DEL CATÁLOGO DE PRODUCTOS
    # ========================================================

    txt_codigo = ft.TextField(
        label="Código del Producto",
        prefix_icon=ft.Icons.QR_CODE_2,
        hint_text="Ej: PRD-008",
        border_radius=8,
        dense=True,
    )
    txt_nombre = ft.TextField(
        label="Nombre del Producto",
        prefix_icon=ft.Icons.INVENTORY_2_OUTLINED,
        hint_text="Ej: Multímetro Digital Industrial",
        border_radius=8,
        dense=True,
    )
    txt_precio = ft.TextField(
        label="Precio Unitario ($)",
        prefix_icon=ft.Icons.ATTACH_MONEY,
        hint_text="Ej: 85.00",
        border_radius=8,
        dense=True,
    )
    txt_stock = ft.TextField(
        label="Cantidad en Stock",
        prefix_icon=ft.Icons.NUMBERS,
        hint_text="Ej: 15",
        border_radius=8,
        dense=True,
    )
    dd_categoria = ft.Dropdown(
        label="Categoría",
        leading_icon=ft.Icons.CATEGORY_OUTLINED,
        options=[ft.dropdown.Option(cat.get_nombre()) for cat in categorias_disponibles],
        border_radius=8,
        dense=True,
        value="Accesorios",
    )

    txt_buscar = ft.TextField(
        label="Buscar producto por código o nombre...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=8,
        dense=True,
        expand=True,
    )
    dd_filtro_cat = ft.Dropdown(
        label="Filtrar por Categoría",
        options=[ft.dropdown.Option("Todas")] + [
            ft.dropdown.Option(cat.get_nombre()) for cat in categorias_disponibles
        ],
        value="Todas",
        border_radius=8,
        dense=True,
        width=220,
    )

    # Tarjetas de Métricas del Inventario
    lbl_total_productos = ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    lbl_total_stock = ft.Text("0 uds.", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900)
    lbl_valor_inventario = ft.Text("$0.00", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_900)

    tabla_productos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Nombre del Producto", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Categoría", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Precio", weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Stock", weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Valor Total", weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=8,
        heading_row_color=ft.Colors.BLUE_50,
        show_bottom_border=True,
    )

    def actualizar_metricas_inventario() -> None:
        lbl_total_productos.value = str(repo_productos.contar())
        lbl_total_stock.value = f"{repo_productos.total_unidades()} uds."
        lbl_valor_inventario.value = f"${repo_productos.valor_total():,.2f}"

    def cargar_en_formulario(prod: Producto) -> None:
        txt_codigo.value = prod.get_codigo()
        txt_codigo.read_only = True
        txt_nombre.value = prod.get_nombre()
        txt_precio.value = f"{prod.get_precio():.2f}"
        txt_stock.value = str(prod.get_stock())
        dd_categoria.value = prod.get_categoria().get_nombre()
        btn_agregar_prod.disabled = True
        btn_actualizar_prod.disabled = False
        btn_eliminar_prod.disabled = False
        page.update()

    def recargar_tabla_productos(lista: list[Producto] | None = None) -> None:
        productos = lista if lista is not None else repo_productos.obtener_todos()
        filas = []

        for p in productos:
            codigo = p.get_codigo()

            def on_edit_click(e, item=p):
                cargar_en_formulario(item)

            def on_del_click(e, cod=codigo):
                try:
                    repo_productos.eliminar(cod)
                    notificar(f"🗑️ Producto '{cod}' eliminado del catálogo y persistido en disco.")
                    limpiar_formulario_producto()
                    recargar_todo()
                except KeyError as err:
                    notificar(str(err), es_error=True)

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p.get_codigo(), weight=ft.FontWeight.W_600)),
                        ft.DataCell(ft.Text(p.get_nombre())),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    p.get_categoria().get_nombre(),
                                    size=12,
                                    color=ft.Colors.BLUE_900,
                                ),
                                bgcolor=ft.Colors.BLUE_100,
                                border_radius=6,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                            )
                        ),
                        ft.DataCell(ft.Text(f"${p.get_precio():,.2f}")),
                        ft.DataCell(
                            ft.Text(
                                f"{p.get_stock()} uds.",
                                color=ft.Colors.RED_700 if p.get_stock() <= 5 else ft.Colors.BLACK,
                                weight=ft.FontWeight.BOLD if p.get_stock() <= 5 else ft.FontWeight.NORMAL,
                            )
                        ),
                        ft.DataCell(ft.Text(f"${p.calcular_valor_inventario():,.2f}")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_color=ft.Colors.BLUE_700,
                                    tooltip="Editar producto",
                                    on_click=on_edit_click,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_700,
                                    tooltip="Eliminar producto",
                                    on_click=on_del_click,
                                ),
                            ], spacing=0)
                        ),
                    ]
                )
            )

        tabla_productos.rows = filas
        actualizar_metricas_inventario()
        actualizar_dropdown_despachos()
        page.update()

    def limpiar_formulario_producto(e=None) -> None:
        txt_codigo.value = ""
        txt_codigo.read_only = False
        txt_nombre.value = ""
        txt_precio.value = ""
        txt_stock.value = ""
        dd_categoria.value = "Accesorios"
        btn_agregar_prod.disabled = False
        btn_actualizar_prod.disabled = True
        btn_eliminar_prod.disabled = True
        page.update()

    def handle_agregar_producto(e) -> None:
        cod = txt_codigo.value.strip()
        nom = txt_nombre.value.strip()
        prec_str = txt_precio.value.strip()
        stock_str = txt_stock.value.strip()
        cat_nom = dd_categoria.value

        if not cod or not nom or not prec_str or not stock_str or not cat_nom:
            notificar("Por favor, complete todos los campos.", es_error=True)
            return

        try:
            prec = float(prec_str)
            stk = int(stock_str)
            cat_obj = mapa_categorias[cat_nom]
            nuevo = Producto(codigo=cod, nombre=nom, precio=prec, stock=stk, categoria=cat_obj)
            repo_productos.guardar(nuevo)
            notificar(f"✅ Producto '{cod}' guardado y persistido en data/productos.json.")
            limpiar_formulario_producto()
            recargar_todo()
        except ValidationError as err:
            notificar(f"Validación: {err.errors()[0]['msg']}", es_error=True)
        except (ValueError, KeyError) as err:
            notificar(str(err), es_error=True)

    def handle_actualizar_producto(e) -> None:
        cod = txt_codigo.value.strip()
        nom = txt_nombre.value.strip()
        prec_str = txt_precio.value.strip()
        stock_str = txt_stock.value.strip()
        cat_nom = dd_categoria.value

        try:
            prec = float(prec_str)
            stk = int(stock_str)
            cat_obj = mapa_categorias[cat_nom]
            repo_productos.actualizar(
                codigo=cod,
                nombre=nom,
                precio=prec,
                stock=stk,
                categoria=cat_obj,
            )
            notificar(f"✏️ Producto '{cod}' actualizado y persistido en data/productos.json.")
            limpiar_formulario_producto()
            recargar_todo()
        except (ValidationError, ValueError, KeyError) as err:
            notificar(f"Error: {err}", es_error=True)

    def handle_filtrar_productos(e) -> None:
        query = txt_buscar.value.strip()
        cat = dd_filtro_cat.value
        resultados = repo_productos.buscar_por_nombre(query)
        if cat and cat != "Todas":
            resultados = [p for p in resultados if p.get_categoria().get_nombre().lower() == cat.lower()]
        recargar_tabla_productos(resultados)

    txt_buscar.on_change = handle_filtrar_productos
    dd_filtro_cat.on_change = handle_filtrar_productos

    btn_agregar_prod = ft.FilledButton(
        "Guardar Producto",
        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        height=40,
        on_click=handle_agregar_producto,
    )
    btn_actualizar_prod = ft.FilledButton(
        "Actualizar",
        icon=ft.Icons.EDIT_NOTE,
        bgcolor=ft.Colors.AMBER_800,
        color=ft.Colors.WHITE,
        height=40,
        disabled=True,
        on_click=handle_actualizar_producto,
    )
    btn_eliminar_prod = ft.FilledButton(
        "Eliminar",
        icon=ft.Icons.DELETE_FOREVER,
        bgcolor=ft.Colors.RED_700,
        color=ft.Colors.WHITE,
        height=40,
        disabled=True,
        on_click=lambda e: recargar_tabla_productos(),
    )
    btn_limpiar_prod = ft.OutlinedButton(
        "Limpiar",
        icon=ft.Icons.CLEANING_SERVICES_OUTLINED,
        height=40,
        on_click=limpiar_formulario_producto,
    )

    # ========================================================
    # SECCIÓN 2: CENTRO DE DESPACHOS (COLA FIFO MANUAL - SEMANA 7)
    # ========================================================

    txt_dsp_id = ft.TextField(
        label="ID de Orden",
        value=calcular_siguiente_id(),
        read_only=True,
        width=130,
        dense=True,
        border_radius=8,
    )
    txt_dsp_cliente = ft.TextField(
        label="Cliente / Sucursal Solicitante",
        hint_text="Ej: Distribuidora Central S.A.",
        prefix_icon=ft.Icons.BUSINESS_OUTLINED,
        dense=True,
        border_radius=8,
        expand=True,
    )
    dd_dsp_producto = ft.Dropdown(
        label="Producto a Despachar",
        leading_icon=ft.Icons.INVENTORY_OUTLINED,
        options=[],
        dense=True,
        border_radius=8,
        expand=True,
    )
    txt_dsp_cantidad = ft.TextField(
        label="Cantidad",
        hint_text="Ej: 5",
        prefix_icon=ft.Icons.NUMBERS,
        dense=True,
        border_radius=8,
        width=120,
    )

    lbl_cola_total = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_900)
    lbl_cola_frente = ft.Text("Cola Vacía", size=15, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_900)
    lbl_historial_total = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_900)

    lista_visual_cola = ft.ListView(
        spacing=8,
        padding=10,
        expand=True,
    )

    lista_visual_historial = ft.ListView(
        spacing=6,
        padding=10,
        expand=True,
    )

    def actualizar_dropdown_despachos() -> None:
        prods = repo_productos.obtener_todos()
        dd_dsp_producto.options = [
            ft.dropdown.Option(
                key=p.get_codigo(),
                text=f"[{p.get_codigo()}] {p.get_nombre()} (Stock: {p.get_stock()})",
            )
            for p in prods
        ]
        if prods and not dd_dsp_producto.value:
            dd_dsp_producto.value = prods[0].get_codigo()

    def recargar_vista_despachos() -> None:
        txt_dsp_id.value = calcular_siguiente_id()
        # Métricas de la cola
        total_p = repo_despachos.total_pendientes()
        lbl_cola_total.value = str(total_p)
        lbl_historial_total.value = str(len(repo_despachos.listar_historial()))

        if not repo_despachos.esta_vacio():
            proximo = repo_despachos.consultar_proximo()
            lbl_cola_frente.value = (
                f"[{proximo.get_id_pedido()}] {proximo.get_cliente()} "
                f"({proximo.get_nombre_producto()} x{proximo.get_cantidad()})"
            )
            btn_despachar_fifo.disabled = False
        else:
            lbl_cola_frente.value = "Ninguno (Cola Vacía)"
            btn_despachar_fifo.disabled = True

        # Renderizar elementos de la Cola FIFO
        pendientes = repo_despachos.listar_pendientes()
        tarjetas_cola = []

        if not pendientes:
            tarjetas_cola.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=28),
                        ft.Text("No hay órdenes pendientes en la cola. Todos los despachos están al día.", size=14, color=ft.Colors.GREY_700),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for idx, ped in enumerate(pendientes, start=1):
                es_frente = (idx == 1)
                tarjetas_cola.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "TURNO 1 (AL FRENTE)" if es_frente else f"TURNO {idx}",
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.Text(
                                        "PRÓXIMO EN SALIR" if es_frente else "EN ESPERA",
                                        size=9,
                                        color=ft.Colors.WHITE,
                                    ),
                                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                bgcolor=ft.Colors.GREEN_700 if es_frente else ft.Colors.BLUE_GREY_600,
                                border_radius=6,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                                width=130,
                            ),
                            ft.Column([
                                ft.Row([
                                    ft.Text(ped.get_id_pedido(), size=15, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"• {ped.get_cliente()}", size=14, weight=ft.FontWeight.W_500),
                                ]),
                                ft.Text(
                                    f"Producto: {ped.get_nombre_producto()} ({ped.get_codigo_producto()}) | Cantidad: {ped.get_cantidad()} uds.",
                                    size=13,
                                    color=ft.Colors.GREY_800,
                                ),
                                ft.Text(f"Fecha de ingreso: {ped.get_fecha_registro()}", size=11, color=ft.Colors.GREY_600),
                            ], spacing=2, expand=True),
                            ft.Icon(
                                ft.Icons.FAST_FORWARD if es_frente else ft.Icons.HOURGLASS_BOTTOM,
                                color=ft.Colors.GREEN_700 if es_frente else ft.Colors.GREY_500,
                                size=28,
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=ft.Colors.GREEN_50 if es_frente else ft.Colors.GREY_50,
                        border=ft.Border.all(1.5 if es_frente else 1, ft.Colors.GREEN_400 if es_frente else ft.Colors.GREY_300),
                        border_radius=8,
                        padding=10,
                    )
                )

        lista_visual_cola.controls = tarjetas_cola

        # Renderizar historial de la Pila LIFO
        historial = repo_despachos.listar_historial()
        tarjetas_hist = []
        for ped in historial:
            tarjetas_hist.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DONE_ALL, color=ft.Colors.TEAL_700, size=20),
                        ft.Text(f"{ped.get_id_pedido()}", weight=ft.FontWeight.BOLD, size=13),
                        ft.Text(f"{ped.get_cliente()}", size=12, expand=True),
                        ft.Text(f"{ped.get_codigo_producto()} x{ped.get_cantidad()} uds.", size=12, color=ft.Colors.BLUE_900),
                        ft.Container(
                            content=ft.Text("DESPACHADO", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=ft.Colors.TEAL_700,
                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                            border_radius=4,
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1, ft.Colors.GREY_200),
                    border_radius=6,
                    padding=8,
                )
            )
        lista_visual_historial.controls = tarjetas_hist
        page.update()

    def handle_encolar_despacho(e) -> None:
        cliente = txt_dsp_cliente.value.strip()
        cod_prod = dd_dsp_producto.value
        cant_str = txt_dsp_cantidad.value.strip()

        if not cliente or not cod_prod or not cant_str:
            notificar("Por favor complete todos los datos de la orden de despacho.", es_error=True)
            return

        try:
            cant = int(cant_str)
            prod = repo_productos.obtener_por_codigo(cod_prod)
            if not prod:
                notificar("El producto seleccionado no existe.", es_error=True)
                return

            nuevo_pedido = PedidoDespacho(
                id_pedido=txt_dsp_id.value,
                cliente=cliente,
                codigo_producto=prod.get_codigo(),
                nombre_producto=prod.get_nombre(),
                cantidad=cant,
            )

            # Inserción en la ColaLineal mediante el Repository y persistencia en disco
            repo_despachos.encolar_despacho(nuevo_pedido)
            notificar(f"📥 Orden '{nuevo_pedido.get_id_pedido()}' agregada a la Cola FIFO y guardada en disco.")

            txt_dsp_id.value = calcular_siguiente_id()
            txt_dsp_cliente.value = ""
            txt_dsp_cantidad.value = ""

            recargar_vista_despachos()
            page.update()

        except ValidationError as err:
            notificar(f"Validación: {err.errors()[0]['msg']}", es_error=True)
        except (ValueError, KeyError) as err:
            notificar(str(err), es_error=True)

    def handle_despachar_siguiente(e) -> None:
        try:
            despachado = repo_despachos.despachar_siguiente()
            notificar(
                f"🚀 Despacho Exitoso: Se atendió '{despachado.get_id_pedido()}' "
                f"para '{despachado.get_cliente()}'. Stock y estado persistidos en disco."
            )
            recargar_todo()
        except ColaVaciaError as err:
            notificar(str(err), es_error=True)
        except ValueError as err:
            notificar(f"Error de stock: {err}", es_error=True)

    def recargar_todo() -> None:
        recargar_tabla_productos()
        recargar_vista_despachos()

    btn_encolar = ft.FilledButton(
        "Encolar Pedido (Enqueue FIFO)",
        icon=ft.Icons.INPUT,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        height=40,
        on_click=handle_encolar_despacho,
    )

    btn_despachar_fifo = ft.FilledButton(
        "⚡ Despachar Siguiente Pedido (FIFO)",
        icon=ft.Icons.DELIVERY_DINING,
        bgcolor=ft.Colors.GREEN_700,
        color=ft.Colors.WHITE,
        height=44,
        on_click=handle_despachar_siguiente,
    )

    # ========================================================
    # ENSAMBLAJE DE VISTAS (PESTAÑAS)
    # ========================================================

    # Vista 1: Catálogo de Productos
    metricas_cards_catalogo = ft.Row([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INVENTORY, size=30, color=ft.Colors.BLUE_700),
                ft.Column([
                    ft.Text("Productos Distintos", size=11, color=ft.Colors.GREY_700),
                    lbl_total_productos,
                ], spacing=1),
            ]),
            bgcolor=ft.Colors.BLUE_50,
            border=ft.Border.all(1, ft.Colors.BLUE_200),
            border_radius=8,
            padding=12,
            expand=True,
        ),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.STORAGE, size=30, color=ft.Colors.GREEN_700),
                ft.Column([
                    ft.Text("Total Unidades en Stock", size=11, color=ft.Colors.GREY_700),
                    lbl_total_stock,
                ], spacing=1),
            ]),
            bgcolor=ft.Colors.GREEN_50,
            border=ft.Border.all(1, ft.Colors.GREEN_200),
            border_radius=8,
            padding=12,
            expand=True,
        ),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=30, color=ft.Colors.PURPLE_700),
                ft.Column([
                    ft.Text("Valor Total Inventario", size=11, color=ft.Colors.GREY_700),
                    lbl_valor_inventario,
                ], spacing=1),
            ]),
            bgcolor=ft.Colors.PURPLE_50,
            border=ft.Border.all(1, ft.Colors.PURPLE_200),
            border_radius=8,
            padding=12,
            expand=True,
        ),
    ], spacing=12)

    card_form_producto = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.APP_REGISTRATION, color=ft.Colors.BLUE_700),
                ft.Text("Registro de Producto", size=15, weight=ft.FontWeight.BOLD),
            ]),
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            txt_codigo,
            txt_nombre,
            ft.Row([txt_precio, txt_stock], spacing=8),
            dd_categoria,
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            ft.Column([
                ft.Row([btn_agregar_prod, btn_limpiar_prod], spacing=8),
                ft.Row([btn_actualizar_prod, btn_eliminar_prod], spacing=8),
            ], spacing=8),
        ], spacing=10),
        width=360,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=10,
        padding=16,
    )

    card_tabla_catalogo = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LIST_ALT, color=ft.Colors.BLUE_700),
                ft.Text("Catálogo de Productos en Bodega", size=15, weight=ft.FontWeight.BOLD),
            ]),
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            ft.Row([txt_buscar, dd_filtro_cat], spacing=8),
            ft.Container(
                content=ft.ListView(
                    controls=[tabla_productos],
                    expand=True,
                ),
                expand=True,
                border=ft.Border.all(1, ft.Colors.GREY_200),
                border_radius=8,
                padding=4,
            ),
        ], spacing=10),
        expand=True,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=10,
        padding=16,
    )

    vista_catalogo = ft.Column([
        metricas_cards_catalogo,
        ft.Row([card_form_producto, card_tabla_catalogo], expand=True, spacing=12),
    ], expand=True, spacing=10)

    # Vista 2: Centro de Despachos (Cola FIFO)
    metricas_cards_despacho = ft.Row([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.HOURGLASS_TOP, size=30, color=ft.Colors.ORANGE_700),
                ft.Column([
                    ft.Text("Órdenes en Espera (FIFO)", size=11, color=ft.Colors.GREY_700),
                    lbl_cola_total,
                ], spacing=1),
            ]),
            bgcolor=ft.Colors.ORANGE_50,
            border=ft.Border.all(1, ft.Colors.ORANGE_200),
            border_radius=8,
            padding=12,
            expand=1,
        ),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.RECORD_VOICE_OVER, size=30, color=ft.Colors.BLUE_700),
                ft.Column([
                    ft.Text("Próximo en Turno (Frente de Cola)", size=11, color=ft.Colors.GREY_700),
                    lbl_cola_frente,
                ], spacing=1),
            ]),
            bgcolor=ft.Colors.BLUE_50,
            border=ft.Border.all(1, ft.Colors.BLUE_200),
            border_radius=8,
            padding=12,
            expand=2,
        ),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.TASK_ALT, size=30, color=ft.Colors.TEAL_700),
                ft.Column([
                    ft.Text("Despachos Atendidos (Pila)", size=11, color=ft.Colors.GREY_700),
                    lbl_historial_total,
                ], spacing=1),
            ]),
            bgcolor=ft.Colors.TEAL_50,
            border=ft.Border.all(1, ft.Colors.TEAL_200),
            border_radius=8,
            padding=12,
            expand=1,
        ),
    ], spacing=12)

    card_form_despacho = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.POST_ADD, color=ft.Colors.BLUE_700),
                ft.Text("Solicitar Nueva Salida de Bodega", size=15, weight=ft.FontWeight.BOLD),
            ]),
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            ft.Row([txt_dsp_id, txt_dsp_cliente], spacing=8),
            dd_dsp_producto,
            txt_dsp_cantidad,
            btn_encolar,
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            ft.Text(
                "ℹ️ Los pedidos ingresados se forman en la Cola FIFO manual. "
                "Al despachar, se atiende estrictamente el pedido con mayor tiempo en espera.",
                size=12,
                color=ft.Colors.GREY_700,
            ),
        ], spacing=10),
        width=400,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=10,
        padding=16,
    )

    card_cola_visual = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.QUEUE, color=ft.Colors.GREEN_700),
                    ft.Text("Cola de Despacho en Tiempo Real (TDA ColaLineal - FIFO)", size=15, weight=ft.FontWeight.BOLD),
                ]),
                btn_despachar_fifo,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            ft.Container(
                content=lista_visual_cola,
                expand=True,
                bgcolor=ft.Colors.GREY_50,
                border_radius=8,
            ),
            ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=18, color=ft.Colors.TEAL_700),
                ft.Text("Historial de Salidas Procesadas (TDA PilaLineal - LIFO)", size=13, weight=ft.FontWeight.BOLD),
            ]),
            ft.Container(
                content=lista_visual_historial,
                height=140,
                border=ft.Border.all(1, ft.Colors.GREY_200),
                border_radius=8,
            ),
        ], spacing=8),
        expand=True,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=10,
        padding=16,
    )

    vista_despachos = ft.Column([
        metricas_cards_despacho,
        ft.Row([card_form_despacho, card_cola_visual], expand=True, spacing=12),
    ], expand=True, spacing=10)

    # Navegación por pestañas (Tabs)
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        tabs=[
            ft.Tab(
                text="Catálogo de Productos (Inventario)",
                icon=ft.Icons.INVENTORY_2,
                content=vista_catalogo,
            ),
            ft.Tab(
                text="Centro de Despachos (Cola FIFO)",
                icon=ft.Icons.LOCAL_SHIPPING,
                content=vista_despachos,
            ),
        ],
        expand=True,
    )

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        theme_btn.icon = (
            ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE
        )
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Modo Claro / Oscuro",
        on_click=toggle_theme,
    )

    def handle_restablecer_demo(e):
        repo_productos.restaurar_demo()
        repo_despachos.restaurar_demo()
        recargar_todo()
        notificar("🔄 Datos de catálogo y órdenes de demo restablecidos en archivos JSON.")

    btn_restaurar = ft.OutlinedButton(
        "Restablecer Demo",
        icon=ft.Icons.RESTORE,
        tooltip="Restaura catálogo y pedidos demo en disco",
        on_click=handle_restablecer_demo,
        height=36,
    )

    badge_persistencia = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.STORAGE, size=15, color=ft.Colors.GREEN_800),
            ft.Text("Persistencia Activa (JSON)", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_900),
        ], spacing=4),
        bgcolor=ft.Colors.GREEN_100,
        border=ft.Border.all(1, ft.Colors.GREEN_400),
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )

    header = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.WAREHOUSE, size=36, color=ft.Colors.BLUE_700),
                ft.Column([
                    ft.Text(
                        "Sistema de Gestión de Bodega — Patrones de Diseño, TDAs Lineales y Persistencia",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Examen Final: ColaLineal FIFO manual, Patrón Repository y Persistencia JSON | Luis Alberto Villegas Merchan",
                        size=12,
                        color=ft.Colors.GREY_700,
                    ),
                ], spacing=2),
            ]),
            ft.Row([
                badge_persistencia,
                btn_restaurar,
                theme_btn,
            ], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding.only(bottom=6),
    )

    page.add(
        ft.Column(
            [header, tabs],
            expand=True,
            spacing=8,
        )
    )

    # Carga inicial completa
    recargar_todo()


def main():
    """Ejecuta la interfaz Flet."""
    if hasattr(ft, "run"):
        ft.run(crear_aplicacion)
    else:
        ft.app(target=crear_aplicacion)


if __name__ == "__main__":
    main()
