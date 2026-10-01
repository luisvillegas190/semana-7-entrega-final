"""
test_persistencia.py
====================

Pruebas unitarias para la capa de persistencia de datos en archivos JSON:
- Serialización y deserialización de entidades del modelo (Categoria, Producto, PedidoDespacho).
- Persistencia integral en ProductoRepositoryJSON (Guardado, actualización, eliminación y recarga desde disco).
- Persistencia de estructuras lineales en DespachoColaRepository (Cola FIFO y Pila LIFO sincronizadas en disco).

Autor: Luis Alberto Villegas Merchan
Actividad: Examen Final - Presentación y Explicación del Proyecto (Semanas 5, 6 y 7)
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from modelo import Categoria, PedidoDespacho, Producto
from repositorio import DespachoColaRepository, ProductoRepositoryJSON


class TestSerializacionModelo:
    """Pruebas de serialización to_dict y deserialización from_dict."""

    def test_categoria_serializacion(self):
        cat = Categoria("CAT-RED", "Redes y Telecomunicaciones")
        d = cat.to_dict()
        assert d == {"codigo": "CAT-RED", "nombre": "Redes y Telecomunicaciones"}

        recuperada = Categoria.from_dict(d)
        assert recuperada.get_codigo() == "CAT-RED"
        assert recuperada.get_nombre() == "Redes y Telecomunicaciones"

    def test_producto_serializacion(self):
        cat = Categoria("CAT-ALM", "Almacenamiento")
        prod = Producto("PRD-999", "Disco Duro 4TB", 120.50, 15, cat)
        d = prod.to_dict()

        assert d["codigo"] == "PRD-999"
        assert d["nombre"] == "Disco Duro 4TB"
        assert d["precio"] == 120.50
        assert d["stock"] == 15
        assert d["categoria"]["codigo"] == "CAT-ALM"

        recuperado = Producto.from_dict(d)
        assert recuperado.get_codigo() == "PRD-999"
        assert recuperado.get_nombre() == "Disco Duro 4TB"
        assert recuperado.get_precio() == 120.50
        assert recuperado.get_stock() == 15
        assert recuperado.get_categoria().get_nombre() == "Almacenamiento"

    def test_pedido_despacho_serializacion(self):
        pedido = PedidoDespacho(
            id_pedido="ORD-501",
            cliente="Logística Express",
            codigo_producto="PRD-999",
            nombre_producto="Disco Duro 4TB",
            cantidad=4,
        )
        d = pedido.to_dict()
        assert d["id_pedido"] == "ORD-501"
        assert d["cliente"] == "Logística Express"
        assert d["codigo_producto"] == "PRD-999"
        assert d["cantidad"] == 4
        assert d["estado"] == "PENDIENTE"

        recuperado = PedidoDespacho.from_dict(d)
        assert recuperado.get_id_pedido() == "ORD-501"
        assert recuperado.get_estado() == "PENDIENTE"

        # Probar serialización cuando está despachado
        pedido.marcar_despachado()
        d_desp = pedido.to_dict()
        assert d_desp["estado"] == "DESPACHADO"
        recuperado_desp = PedidoDespacho.from_dict(d_desp)
        assert recuperado_desp.get_estado() == "DESPACHADO"


class TestPersistenciaProductoRepositoryJSON:
    """Pruebas de persistencia en disco de ProductoRepositoryJSON."""

    def test_creacion_archivo_y_guardado_persistente(self, tmp_path: Path):
        ruta_json = tmp_path / "datos" / "productos.json"
        repo = ProductoRepositoryJSON(ruta_archivo=ruta_json, inicializar_demo=False)

        assert ruta_json.exists()
        assert repo.contar() == 0

        cat = Categoria("CAT-LOG", "Logística")
        p1 = Producto("PRD-201", "Cinta de Embalaje 50m", 3.50, 100, cat)
        p2 = Producto("PRD-202", "Dispensador Manual", 18.00, 20, cat)

        repo.guardar(p1)
        repo.guardar(p2)

        # Validar que el archivo físico contiene los datos
        with open(ruta_json, "r", encoding="utf-8") as f:
            contenido = json.load(f)
        assert len(contenido) == 2
        assert contenido[0]["codigo"] == "PRD-201"
        assert contenido[1]["codigo"] == "PRD-202"

        # Simular reinicio de la aplicación instanciando un nuevo repositorio desde el mismo archivo
        repo_reinicio = ProductoRepositoryJSON(ruta_archivo=ruta_json, inicializar_demo=False)
        assert repo_reinicio.contar() == 2
        recuperado1 = repo_reinicio.obtener_por_codigo("PRD-201")
        assert recuperado1 is not None
        assert recuperado1.get_nombre() == "Cinta de Embalaje 50m"
        assert recuperado1.get_stock() == 100

    def test_actualizacion_y_eliminacion_persistente(self, tmp_path: Path):
        ruta_json = tmp_path / "productos_crud.json"
        repo = ProductoRepositoryJSON(ruta_archivo=ruta_json, inicializar_demo=False)

        cat = Categoria("CAT-IND", "Industrial")
        p = Producto("PRD-301", "Casco de Seguridad", 25.00, 50, cat)
        repo.guardar(p)

        # Actualizar producto
        repo.actualizar(
            codigo="PRD-301",
            nombre="Casco de Seguridad Pro",
            precio=29.99,
            stock=45,
            categoria=cat,
        )

        # Verificar persistencia en nueva instancia
        repo2 = ProductoRepositoryJSON(ruta_archivo=ruta_json, inicializar_demo=False)
        p_actualizado = repo2.obtener_por_codigo("PRD-301")
        assert p_actualizado is not None
        assert p_actualizado.get_nombre() == "Casco de Seguridad Pro"
        assert p_actualizado.get_precio() == 29.99
        assert p_actualizado.get_stock() == 45

        # Eliminar producto
        repo2.eliminar("PRD-301")
        assert repo2.contar() == 0

        # Verificar en tercera instancia
        repo3 = ProductoRepositoryJSON(ruta_archivo=ruta_json, inicializar_demo=False)
        assert repo3.contar() == 0
        assert repo3.obtener_por_codigo("PRD-301") is None


class TestPersistenciaDespachoColaRepository:
    """Pruebas de persistencia en disco de DespachoColaRepository (Cola FIFO y Pila LIFO)."""

    def test_persistencia_cola_e_historial(self, tmp_path: Path):
        ruta_prod = tmp_path / "productos.json"
        ruta_desp = tmp_path / "despachos.json"

        repo_prod = ProductoRepositoryJSON(ruta_archivo=ruta_prod, inicializar_demo=False)
        cat = Categoria("CAT-TEST", "General")
        prod = Producto("PRD-501", "Monitor Industrial 24", 250.00, 10, cat)
        repo_prod.guardar(prod)

        repo_desp = DespachoColaRepository(
            producto_repo=repo_prod,
            ruta_archivo=ruta_desp,
            inicializar_demo=False,
        )

        ord1 = PedidoDespacho("ORD-1", "Cliente Alfa", "PRD-501", "Monitor Industrial 24", 2)
        ord2 = PedidoDespacho("ORD-2", "Cliente Beta", "PRD-501", "Monitor Industrial 24", 3)

        repo_desp.encolar_despacho(ord1)
        repo_desp.encolar_despacho(ord2)
        assert repo_desp.total_pendientes() == 2

        # Validar persistencia al reiniciar
        repo_desp_reinicio = DespachoColaRepository(
            producto_repo=repo_prod,
            ruta_archivo=ruta_desp,
            inicializar_demo=False,
        )
        assert repo_desp_reinicio.total_pendientes() == 2
        proximo = repo_desp_reinicio.consultar_proximo()
        assert proximo.get_id_pedido() == "ORD-1"

        # Procesar primer despacho (FIFO)
        atendido = repo_desp_reinicio.despachar_siguiente()
        assert atendido.get_id_pedido() == "ORD-1"
        assert repo_desp_reinicio.total_pendientes() == 1
        assert len(repo_desp_reinicio.listar_historial()) == 1

        # Verificar descuento de existencias en el inventario persistente
        repo_prod_check = ProductoRepositoryJSON(ruta_archivo=ruta_prod, inicializar_demo=False)
        assert repo_prod_check.obtener_por_codigo("PRD-501").get_stock() == 8

        # Validar en una tercera instancia que la cola tiene ORD-2 y el historial ORD-1
        repo_desp_final = DespachoColaRepository(
            producto_repo=repo_prod,
            ruta_archivo=ruta_desp,
            inicializar_demo=False,
        )
        assert repo_desp_final.total_pendientes() == 1
        assert repo_desp_final.consultar_proximo().get_id_pedido() == "ORD-2"
        historial = repo_desp_final.listar_historial()
        assert len(historial) == 1
        assert historial[0].get_id_pedido() == "ORD-1"
        assert historial[0].get_estado() == "DESPACHADO"
