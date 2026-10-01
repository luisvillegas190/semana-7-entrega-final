"""
modelo.py
=========

Modelo de dominio del Sistema de Gestión de Bodega e Inventario.

Actividad: Semana 7 — Patrones de Diseño, Testing Unitario y TDAs Lineales.
Materia: Programación Estructurada / Programación Orientada a Objetos
Estudiante: Luis Alberto Villegas Merchan

Este módulo define:
1. Modelos de validación de datos con Pydantic (DatosCategoria, DatosProducto, DatosPedidoDespacho).
2. Clases de entidad encapsuladas (Categoria, Producto, PedidoDespacho).
3. CatalogoProductos: Manejador de colecciones nativas (retrocompatibilidad Semanas 5 y 6).
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

# MODELOS DE VALIDACIÓN PYDANTIC

class DatosCategoria(BaseModel):
    """Valida los datos requeridos para una categoría de producto."""

    codigo: str = Field(min_length=2, max_length=20)
    nombre: str = Field(min_length=2, max_length=80)


class DatosProducto(BaseModel):
    """Valida los datos requeridos para un producto en bodega."""

    codigo: str = Field(min_length=2, max_length=20)
    nombre: str = Field(min_length=2, max_length=100)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)


class DatosPedidoDespacho(BaseModel):
    """Valida los datos de una solicitud u orden de despacho en bodega."""

    id_pedido: str = Field(min_length=2, max_length=30)
    cliente: str = Field(min_length=2, max_length=100)
    codigo_producto: str = Field(min_length=2, max_length=20)
    nombre_producto: str = Field(min_length=2, max_length=100)
    cantidad: int = Field(gt=0)


# CLASES DE DOMINIO (ENCAPSULADAS)

class Categoria:
    """Representa una categoría de productos en la bodega."""

    def __init__(self, codigo: str, nombre: str) -> None:
        datos = DatosCategoria(codigo=codigo, nombre=nombre)
        self.__codigo = datos.codigo.strip().upper()
        self.__nombre = datos.nombre.strip()

    def get_codigo(self) -> str:
        return self.__codigo

    def set_codigo(self, codigo: str) -> None:
        datos = DatosCategoria(codigo=codigo, nombre=self.__nombre)
        self.__codigo = datos.codigo.strip().upper()

    def get_nombre(self) -> str:
        return self.__nombre

    def set_nombre(self, nombre: str) -> None:
        datos = DatosCategoria(codigo=self.__codigo, nombre=nombre)
        self.__nombre = datos.nombre.strip()

    def __str__(self) -> str:
        return self.__nombre

    def __repr__(self) -> str:
        return f"Categoria(codigo='{self.__codigo}', nombre='{self.__nombre}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Categoria):
            return self.__codigo == other.get_codigo()
        return False

    def __hash__(self) -> int:
        return hash(self.__codigo)

    def to_dict(self) -> dict[str, str]:
        """Serializa la categoría a un diccionario serializable en JSON."""
        return {
            "codigo": self.__codigo,
            "nombre": self.__nombre,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Categoria:
        """Reconstruye una instancia de Categoria desde un diccionario."""
        return cls(
            codigo=data["codigo"],
            nombre=data["nombre"],
        )


class Producto:
    """
    Representa un producto almacenado en el inventario.
    Aplica encapsulación estricta mediante atributos privados (__).
    """

    def __init__(
        self,
        codigo: str,
        nombre: str,
        precio: float,
        stock: int,
        categoria: Categoria,
    ) -> None:
        datos = DatosProducto(
            codigo=codigo,
            nombre=nombre,
            precio=precio,
            stock=stock,
        )
        self.__codigo = datos.codigo.strip().upper()
        self.__nombre = datos.nombre.strip()
        self.__precio = datos.precio
        self.__stock = datos.stock
        self.__categoria = categoria

    def get_codigo(self) -> str:
        return self.__codigo

    def get_nombre(self) -> str:
        return self.__nombre

    def set_nombre(self, nombre: str) -> None:
        datos = DatosProducto(
            codigo=self.__codigo,
            nombre=nombre,
            precio=self.__precio,
            stock=self.__stock,
        )
        self.__nombre = datos.nombre.strip()

    def get_precio(self) -> float:
        return self.__precio

    def set_precio(self, precio: float) -> None:
        datos = DatosProducto(
            codigo=self.__codigo,
            nombre=self.__nombre,
            precio=precio,
            stock=self.__stock,
        )
        self.__precio = datos.precio

    def get_stock(self) -> int:
        return self.__stock

    def set_stock(self, stock: int) -> None:
        datos = DatosProducto(
            codigo=self.__codigo,
            nombre=self.__nombre,
            precio=self.__precio,
            stock=stock,
        )
        self.__stock = datos.stock

    def get_categoria(self) -> Categoria:
        return self.__categoria

    def set_categoria(self, categoria: Categoria) -> None:
        self.__categoria = categoria

    def aumentar_stock(self, cantidad: int) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad a reabastecer debe ser un número positivo.")
        self.set_stock(self.__stock + cantidad)

    def disminuir_stock(self, cantidad: int) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad a descontar debe ser un número positivo.")
        if cantidad > self.__stock:
            raise ValueError(
                f"Stock insuficiente para el producto {self.__codigo}. "
                f"Disponible: {self.__stock}, Solicitado: {cantidad}."
            )
        self.set_stock(self.__stock - cantidad)

    def calcular_valor_inventario(self) -> float:
        return self.__precio * self.__stock

    def mostrar_informacion(self) -> str:
        return (
            f"[{self.__codigo}] {self.__nombre} | "
            f"Categoría: {self.__categoria.get_nombre()} | "
            f"Precio: ${self.__precio:,.2f} | Stock: {self.__stock} uds."
        )

    def __str__(self) -> str:
        return self.mostrar_informacion()

    def __repr__(self) -> str:
        return (
            f"Producto(codigo='{self.__codigo}', nombre='{self.__nombre}', "
            f"precio={self.__precio}, stock={self.__stock})"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Producto):
            return self.__codigo == other.get_codigo()
        return False

    def __hash__(self) -> int:
        return hash(self.__codigo)

    def to_dict(self) -> dict:
        """Serializa el producto a un diccionario compatible con JSON."""
        return {
            "codigo": self.__codigo,
            "nombre": self.__nombre,
            "precio": self.__precio,
            "stock": self.__stock,
            "categoria": self.__categoria.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Producto:
        """Reconstruye una instancia de Producto desde un diccionario."""
        cat_data = data["categoria"]
        if isinstance(cat_data, dict):
            categoria_obj = Categoria.from_dict(cat_data)
        else:
            categoria_obj = Categoria("CAT-GEN", str(cat_data))

        return cls(
            codigo=data["codigo"],
            nombre=data["nombre"],
            precio=float(data["precio"]),
            stock=int(data["stock"]),
            categoria=categoria_obj,
        )


class PedidoDespacho:
    """
    Representa una solicitud de despacho u orden de salida de bodega.
    Se procesa típicamente en orden de llegada mediante una Cola FIFO.
    """

    def __init__(
        self,
        id_pedido: str,
        cliente: str,
        codigo_producto: str,
        nombre_producto: str,
        cantidad: int,
        fecha_registro: str | None = None,
    ) -> None:
        datos = DatosPedidoDespacho(
            id_pedido=id_pedido,
            cliente=cliente,
            codigo_producto=codigo_producto,
            nombre_producto=nombre_producto,
            cantidad=cantidad,
        )
        self.__id_pedido: str = datos.id_pedido.strip().upper()
        self.__cliente: str = datos.cliente.strip()
        self.__codigo_producto: str = datos.codigo_producto.strip().upper()
        self.__nombre_producto: str = datos.nombre_producto.strip()
        self.__cantidad: int = datos.cantidad
        self.__fecha_registro: str = (
            fecha_registro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.__estado: str = "PENDIENTE"  # PENDIENTE, DESPACHADO, CANCELADO

    def get_id_pedido(self) -> str:
        return self.__id_pedido

    def get_cliente(self) -> str:
        return self.__cliente

    def get_codigo_producto(self) -> str:
        return self.__codigo_producto

    def get_nombre_producto(self) -> str:
        return self.__nombre_producto

    def get_cantidad(self) -> int:
        return self.__cantidad

    def get_fecha_registro(self) -> str:
        return self.__fecha_registro

    def get_estado(self) -> str:
        return self.__estado

    def marcar_despachado(self) -> None:
        """Cambia el estado de la orden a DESPACHADO."""
        self.__estado = "DESPACHADO"

    def marcar_cancelado(self) -> None:
        """Cambia el estado de la orden a CANCELADO."""
        self.__estado = "CANCELADO"

    def __repr__(self) -> str:
        return (
            f"PedidoDespacho(id='{self.__id_pedido}', cliente='{self.__cliente}', "
            f"prod='{self.__codigo_producto}', cant={self.__cantidad}, estado='{self.__estado}')"
        )

    def __str__(self) -> str:
        return (
            f"[{self.__id_pedido}] Cliente: {self.__cliente} | "
            f"Producto: {self.__nombre_producto} ({self.__codigo_producto}) x{self.__cantidad} uds. | "
            f"Estado: {self.__estado}"
        )

    def to_dict(self) -> dict:
        """Serializa la orden de despacho a un formato almacenable en JSON."""
        return {
            "id_pedido": self.__id_pedido,
            "cliente": self.__cliente,
            "codigo_producto": self.__codigo_producto,
            "nombre_producto": self.__nombre_producto,
            "cantidad": self.__cantidad,
            "fecha_registro": self.__fecha_registro,
            "estado": self.__estado,
        }

    @classmethod
    def from_dict(cls, data: dict) -> PedidoDespacho:
        """Reconstruye una orden de despacho desde un diccionario."""
        pedido = cls(
            id_pedido=data["id_pedido"],
            cliente=data["cliente"],
            codigo_producto=data["codigo_producto"],
            nombre_producto=data["nombre_producto"],
            cantidad=int(data["cantidad"]),
            fecha_registro=data.get("fecha_registro"),
        )
        estado = data.get("estado", "PENDIENTE")
        if estado == "DESPACHADO":
            pedido.marcar_despachado()
        elif estado == "CANCELADO":
            pedido.marcar_cancelado()
        return pedido


# CLASE LEGACY PARA RETROCOMPATIBILIDAD CON SEMANA 5

class CatalogoProductos:
    """Mantiene compatibilidad con las semanas anteriores usando set, dict y list."""

    def __init__(self) -> None:
        self.__codigos_set: set[str] = set()
        self.__productos_dict: dict[str, Producto] = {}
        self.__productos_list: list[Producto] = []

    def agregar_producto(self, producto: Producto) -> None:
        codigo = producto.get_codigo()
        if codigo in self.__codigos_set:
            raise ValueError(f"El código '{codigo}' ya existe en el catálogo.")
        self.__codigos_set.add(codigo)
        self.__productos_dict[codigo] = producto
        self.__productos_list.append(producto)

    def buscar_por_codigo(self, codigo: str) -> Producto | None:
        return self.__productos_dict.get(codigo.strip().upper())

    def buscar_por_nombre(self, texto_busqueda: str) -> list[Producto]:
        query = texto_busqueda.strip().lower()
        if not query:
            return self.listar_todos()
        return [
            p for p in self.__productos_list
            if query in p.get_nombre().lower() or query in p.get_codigo().lower()
        ]

    def listar_todos(self) -> list[Producto]:
        return list(self.__productos_list)

    def listar_por_categoria(self, nombre_categoria: str) -> list[Producto]:
        cat_query = nombre_categoria.strip().lower()
        if not cat_query or cat_query == "todas":
            return self.listar_todos()
        return [
            p for p in self.__productos_list
            if p.get_categoria().get_nombre().lower() == cat_query
        ]

    def actualizar_producto(
        self,
        codigo: str,
        nuevo_nombre: str,
        nuevo_precio: float,
        nuevo_stock: int,
        nueva_categoria: Categoria,
    ) -> None:
        prod = self.buscar_por_codigo(codigo)
        if not prod:
            raise KeyError(f"No se encontró el producto con código '{codigo}'.")
        prod.set_nombre(nuevo_nombre)
        prod.set_precio(nuevo_precio)
        prod.set_stock(nuevo_stock)
        prod.set_categoria(nueva_categoria)

    def eliminar_producto(self, codigo: str) -> None:
        codigo_norm = codigo.strip().upper()
        prod = self.buscar_por_codigo(codigo_norm)
        if not prod:
            raise KeyError(f"No se puede eliminar: el código '{codigo_norm}' no existe.")
        self.__codigos_set.remove(codigo_norm)
        del self.__productos_dict[codigo_norm]
        self.__productos_list.remove(prod)

    def total_productos(self) -> int:
        return len(self.__codigos_set)

    def total_unidades_stock(self) -> int:
        return sum(p.get_stock() for p in self.__productos_list)

    def valor_total_inventario(self) -> float:
        return sum(p.calcular_valor_inventario() for p in self.__productos_list)

    def cargar_datos_iniciales(self) -> None:
        cat_acc = Categoria("CAT-ACC", "Accesorios")
        cat_elec = Categoria("CAT-ELE", "Electrónica")
        cat_her = Categoria("CAT-HER", "Herramientas")
        cat_red = Categoria("CAT-RED", "Redes y Conectividad")
        cat_alm = Categoria("CAT-ALM", "Almacenamiento")

        productos_demo = [
            Producto("PRD-001", "Lector de Código de Barras Láser RF", 145.00, 25, cat_acc),
            Producto("PRD-002", "Terminal Portátil de Inventario Android", 380.00, 12, cat_elec),
            Producto("PRD-003", "Impresora Térmica de Etiquetas 4x6", 210.00, 18, cat_elec),
            Producto("PRD-004", "Bobina de Cable UTP Cat6 305m", 85.50, 30, cat_red),
            Producto("PRD-005", "Transpaleta Hidráulica Manual 2.5 Ton", 450.00, 6, cat_her),
            Producto("PRD-006", "Switch Gigabit Gestionable 24 Puertos", 175.00, 15, cat_red),
            Producto("PRD-007", "Disco Sólido SSD NVMe 1TB Industrial", 115.00, 40, cat_alm),
        ]

        for p in productos_demo:
            if p.get_codigo() not in self.__codigos_set:
                self.agregar_producto(p)
