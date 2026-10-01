"""
main.py
=======

Punto de entrada principal del Sistema de Gestión de Bodega e Inventario.

Actividad: Semana 7 — Patrones de Diseño, Testing Unitario y TDAs Lineales.
Materia: Programación Estructurada / Programación Orientada a Objetos
Estudiante: Luis Alberto Villegas Merchan

Modos de uso:
1. Interfaz Gráfica de Usuario (Flet):
   python main.py

2. Demostración técnica completa en consola (CLI):
   python main.py --cli
"""

from __future__ import annotations

import sys
import flet as ft

from app import crear_aplicacion
from estructuras_lineales import ColaLineal, PilaLineal
from modelo import Categoria, PedidoDespacho, Producto
from repositorio import (
    DespachoColaRepository,
    ProductoRepositoryJSON,
    ProductoRepositoryMemoria,
)


def ejecutar_demostracion_consola() -> None:
    """Ejecuta una demostración interactiva en terminal de todas las características de Semana 7."""
    print("=" * 80)
    print("  SISTEMA DE GESTIÓN DE BODEGA | SEMANA 7: TDA LINEALES & REPOSITORY")
    print("  Estudiante: Luis Alberto Villegas Merchan")
    print("  Carrera:    Programación Estructurada")
    print("=" * 80)

    # -------------------------------------------------------------
    # PARTE 1: DEMOSTRACIÓN DE LA ESTRUCTURA LINEAL MANUAL (COLA FIFO)
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print(">>> 1. DEMOSTRACIÓN DEL TDA LINEAL: COLA (QUEUE - FIFO)")
    print("    Implementada manualmente con Nodos Enlazados (sin colecciones nativas)")
    print("-" * 75)

    cola_manual: ColaLineal[str] = ColaLineal()
    print(f"[*] ¿Cola recién creada está vacía?: {cola_manual.esta_vacia()} (Tamaño: {cola_manual.tamano()})")

    print("[*] Encolando elementos de prueba (A -> B -> C)...")
    cola_manual.encolar("Ticket-001 (Cliente Alfa)")
    cola_manual.encolar("Ticket-002 (Cliente Beta)")
    cola_manual.encolar("Ticket-003 (Cliente Gamma)")

    print(f"[OK] Total elementos en cola: {cola_manual.tamano()}")
    print(f"[OK] Consultar frente sin eliminar (Peek): {cola_manual.ver_frente()}")
    print(f"[OK] Representación secuencial: {cola_manual.a_lista()}")

    print("\n[*] Desencolando elementos en orden FIFO (Primero en entrar, primero en salir):")
    turno = 1
    while not cola_manual.esta_vacia():
        atendido = cola_manual.desencolar()
        print(f"    - Turno #{turno} atendido: {atendido} | Quedan en cola: {cola_manual.tamano()}")
        turno += 1

    print(f"[*] Estado final de la cola: ¿Está vacía? {cola_manual.esta_vacia()}")

    # -------------------------------------------------------------
    # PARTE 2: DEMOSTRACIÓN DE LA ESTRUCTURA LINEAL MANUAL (PILA LIFO)
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print(">>> 2. DEMOSTRACIÓN DEL TDA LINEAL: PILA (STACK - LIFO)")
    print("    Implementada manualmente con Nodos Enlazados (Historial de Auditoría)")
    print("-" * 75)

    pila_manual: PilaLineal[str] = PilaLineal()
    print("[*] Apilando registros (Acción 1 -> Acción 2 -> Acción 3)...")
    pila_manual.apilar("Registro: Login de Usuario")
    pila_manual.apilar("Registro: Creación de Producto PRD-001")
    pila_manual.apilar("Registro: Modificación de Stock PRD-001")

    print(f"[OK] Elemento en el tope (Peek): {pila_manual.ver_tope()}")
    print("[*] Desapilando en orden LIFO (Último en entrar, primero en salir):")
    while not pila_manual.esta_vacia():
        reg = pila_manual.desapilar()
        print(f"    - Deshecho/Auditoría: {reg}")

    # -------------------------------------------------------------
    # PARTE 3: PATRÓN DE DISEÑO REPOSITORY INTEGRADO CON LA COLA MANUAL
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print(">>> 3. DEMOSTRACIÓN DEL PATRÓN DE DISEÑO REPOSITORY")
    print("    - IProductoRepository: Persistencia desacoplada del inventario")
    print("    - IDespachoRepository: Administra órdenes usando la ColaLineal manual")
    print("-" * 75)

    # 3.1 Inicializar Repositorio de Productos
    repo_prod = ProductoRepositoryMemoria()
    cat_her = Categoria("CAT-HER", "Herramientas")
    cat_ele = Categoria("CAT-ELE", "Electrónica")

    prod1 = Producto("PRD-101", "Lector Óptico Láser RF", 145.00, 10, cat_her)
    prod2 = Producto("PRD-102", "Terminal Portátil Android", 380.00, 5, cat_ele)
    repo_prod.guardar(prod1)
    repo_prod.guardar(prod2)

    print(f"[OK] Productos registrados en ProductoRepository: {repo_prod.contar()}")
    print(f"[OK] Total unidades en stock físico: {repo_prod.total_unidades()} uds.")
    print(f"[OK] Valor total de inventario: ${repo_prod.valor_total():,.2f}")

    # 3.2 Repositorio de Despachos respaldado por ColaLineal
    repo_desp = DespachoColaRepository(producto_repo=repo_prod)

    print("\n[*] Encolando órdenes de salida de bodega en DespachoColaRepository...")
    ord1 = PedidoDespacho("DSP-001", "Sucursal Central", "PRD-101", "Lector Láser", 3)
    ord2 = PedidoDespacho("DSP-002", "Logística Norte", "PRD-101", "Lector Láser", 4)
    ord3 = PedidoDespacho("DSP-003", "Distribuidora Sur", "PRD-102", "Terminal Android", 2)

    repo_desp.encolar_despacho(ord1)
    repo_desp.encolar_despacho(ord2)
    repo_desp.encolar_despacho(ord3)

    print(f"[OK] Total órdenes en espera en la Cola FIFO: {repo_desp.total_pendientes()}")
    proximo = repo_desp.consultar_proximo()
    print(f"[OK] Próximo en turno (Frente): {proximo.get_id_pedido()} para {proximo.get_cliente()}")

    print("\n[*] Validación de reglas de negocio en Repositorio:")
    try:
        # Intentar encolar un pedido que supere el stock disponible de PRD-102 (hay 5, se piden 10)
        pedido_excesivo = PedidoDespacho("DSP-004", "Cliente X", "PRD-102", "Terminal Android", 10)
        repo_desp.encolar_despacho(pedido_excesivo)
    except ValueError as e:
        print(f"[OK] El Repositorio rechazó la solicitud por stock insuficiente:")
        print(f"     Mensaje: {e}")

    print("\n[*] Procesando despachos en orden FIFO y descontando existencias:")
    while not repo_desp.esta_vacio():
        desp = repo_desp.despachar_siguiente()
        p = repo_prod.obtener_por_codigo(desp.get_codigo_producto())
        stock_restante = p.get_stock() if p else 0
        print(
            f"    [DESPACHADO] {desp.get_id_pedido()} | Cliente: {desp.get_cliente()} | "
            f"Cant: {desp.get_cantidad()} uds. | Stock restante de {desp.get_codigo_producto()}: {stock_restante} uds."
        )

    print(f"\n[*] Estado final de inventario:")
    print(f"    - Unidades restantes en stock: {repo_prod.total_unidades()} uds.")
    print(f"    - Valor restante: ${repo_prod.valor_total():,.2f}")
    print(f"    - Historial de despachos archivados en la Pila LIFO: {len(repo_desp.listar_historial())} pedidos.")

    # -------------------------------------------------------------
    # PARTE 4: DEMOSTRACIÓN DE PERSISTENCIA DE DATOS (ARCHIVOS JSON)
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print(">>> 4. DEMOSTRACIÓN DE PERSISTENCIA DE DATOS EN ARCHIVOS JSON")
    print("    Requisito Obligatorio del Examen: Almacenar y recuperar información")
    print("-" * 75)

    repo_json = ProductoRepositoryJSON(ruta_archivo="data/productos.json", inicializar_demo=True)
    print(f"[*] Repositorio de productos persistente: {repo_json.obtener_ruta_archivo()}")
    print(f"[OK] Total de productos sincronizados en disco: {repo_json.contar()}")
    print(f"[OK] Unidades físicas en catálogo persistente: {repo_json.total_unidades()} uds.")
    print(f"[OK] Valor total de inventario persistente: ${repo_json.valor_total():,.2f}")

    repo_desp_json = DespachoColaRepository(
        producto_repo=repo_json,
        ruta_archivo="data/despachos.json",
        inicializar_demo=True,
    )
    print(f"[*] Repositorio de despachos persistente: {repo_desp_json.obtener_ruta_archivo()}")
    print(f"[OK] Órdenes activas en Cola FIFO persistente: {repo_desp_json.total_pendientes()}")
    print(f"[OK] Despachos históricos en Pila LIFO persistente: {len(repo_desp_json.listar_historial())}")

    print("\n" + "=" * 80)
    print("  DEMOSTRACIÓN EN CONSOLA FINALIZADA EXITOSAMENTE")
    print("  Para ejecutar las pruebas unitarias: python -m pytest -v")
    print("  Para ejecutar la interfaz gráfica:  python main.py")
    print("=" * 80 + "\n")


def main() -> None:
    """Punto de entrada: CLI o GUI según argumentos."""
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--cli", "-c", "--test", "cli"):
        ejecutar_demostracion_consola()
    else:
        if hasattr(ft, "run"):
            ft.run(crear_aplicacion)
        else:
            ft.app(target=crear_aplicacion)


if __name__ == "__main__":
    main()
