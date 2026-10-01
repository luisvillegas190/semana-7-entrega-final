"""
repositorio.py
==============

Implementación del Patrón de Diseño Repository (Repositorio).

Actividad: Semana 7 — Patrones de Diseño, Testing Unitario y TDAs Lineales.
Materia: Programación Estructurada / Programación Orientada a Objetos
Estudiante: Luis Alberto Villegas Merchan

PROPÓSITO DEL PATRÓN REPOSITORY:
Separar el acceso y persistencia de los datos de la lógica de negocio y de la
interfaz gráfica. Provee una interfaz limpia y desacoplada mediante clases base
abstractas (ABC) que define contratos estrictos.

INTEGRACIÓN REQUERIDA:
El repositorio de despachos ('DespachoColaRepository') integra directamente la
estructura de datos 'ColaLineal' implementada manualmente para gestionar las
solicitudes en estricto orden de llegada (FIFO). Adicionalmente integra 'PilaLineal'
para registrar el historial de auditoría de despachos completados (LIFO).
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from estructuras_lineales import ColaLineal, ColaVaciaError, PilaLineal
from modelo import Categoria, PedidoDespacho, Producto


# 1. INTERFAZ ABSTRACTA DEL REPOSITORIO DE PRODUCTOS

class IProductoRepository(ABC):
    """
    Contrato abstracto que define las operaciones de acceso y manipulación
    del inventario de productos.
    """

    @abstractmethod
    def guardar(self, producto: Producto) -> None:
        """Persiste un nuevo producto."""
        pass

    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> Optional[Producto]:
        """Obtiene un producto por su código único."""
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Producto]:
        """Retorna todos los productos registrados."""
        pass

    @abstractmethod
    def actualizar(
        self,
        codigo: str,
        nombre: str,
        precio: float,
        stock: int,
        categoria: Categoria,
    ) -> None:
        """Actualiza la información de un producto."""
        pass

    @abstractmethod
    def eliminar(self, codigo: str) -> None:
        """Elimina un producto por su código."""
        pass

    @abstractmethod
    def buscar_por_nombre(self, query: str) -> list[Producto]:
        """Busca productos por coincidencia en nombre o código."""
        pass

    @abstractmethod
    def filtrar_por_categoria(self, categoria: str) -> list[Producto]:
        """Filtra productos pertenecientes a una categoría."""
        pass

    @abstractmethod
    def contar(self) -> int:
        """Retorna la cantidad total de productos distintos."""
        pass

    @abstractmethod
    def total_unidades(self) -> int:
        """Retorna la cantidad acumulada de unidades en inventario."""
        pass

    @abstractmethod
    def valor_total(self) -> float:
        """Retorna el valor monetario global del inventario."""
        pass


# 2. IMPLEMENTACIÓN CONCRETA DEL REPOSITORIO DE PRODUCTOS

class ProductoRepositoryMemoria(IProductoRepository):
    """
    Implementación en memoria del repositorio de productos.
    Garantiza unicidad de códigos e indexación rápida.
    """

    def __init__(self) -> None:
        self.__codigos: set[str] = set()
        self.__productos_dict: dict[str, Producto] = {}
        self.__productos_list: list[Producto] = []

    def guardar(self, producto: Producto) -> None:
        codigo = producto.get_codigo()
        if codigo in self.__codigos:
            raise ValueError(f"El producto con código '{codigo}' ya está registrado.")
        self.__codigos.add(codigo)
        self.__productos_dict[codigo] = producto
        self.__productos_list.append(producto)

    def obtener_por_codigo(self, codigo: str) -> Optional[Producto]:
        return self.__productos_dict.get(codigo.strip().upper())

    def obtener_todos(self) -> list[Producto]:
        return list(self.__productos_list)

    def actualizar(
        self,
        codigo: str,
        nombre: str,
        precio: float,
        stock: int,
        categoria: Categoria,
    ) -> None:
        producto = self.obtener_por_codigo(codigo)
        if not producto:
            raise KeyError(f"No existe ningún producto con el código '{codigo}'.")
        producto.set_nombre(nombre)
        producto.set_precio(precio)
        producto.set_stock(stock)
        producto.set_categoria(categoria)

    def eliminar(self, codigo: str) -> None:
        codigo_norm = codigo.strip().upper()
        producto = self.obtener_por_codigo(codigo_norm)
        if not producto:
            raise KeyError(f"No se puede eliminar: el código '{codigo_norm}' no existe.")
        self.__codigos.remove(codigo_norm)
        del self.__productos_dict[codigo_norm]
        self.__productos_list.remove(producto)

    def buscar_por_nombre(self, query: str) -> list[Producto]:
        texto = query.strip().lower()
        if not texto:
            return self.obtener_todos()
        return [
            p for p in self.__productos_list
            if texto in p.get_nombre().lower() or texto in p.get_codigo().lower()
        ]

    def filtrar_por_categoria(self, categoria: str) -> list[Producto]:
        cat_filtro = categoria.strip().lower()
        if not cat_filtro or cat_filtro == "todas":
            return self.obtener_todos()
        return [
            p for p in self.__productos_list
            if p.get_categoria().get_nombre().lower() == cat_filtro
        ]

    def contar(self) -> int:
        return len(self.__codigos)

    def total_unidades(self) -> int:
        return sum(p.get_stock() for p in self.__productos_list)

    def valor_total(self) -> float:
        return sum(p.calcular_valor_inventario() for p in self.__productos_list)


# 2.1 IMPLEMENTACIÓN PERSISTENTE EN ARCHIVO JSON (REQUISITO EXAMEN FINAL)

class ProductoRepositoryJSON(IProductoRepository):
    """
    Implementación concreta de IProductoRepository con persistencia física en disco
    mediante archivos JSON.
    
    Garantiza el cumplimiento obligatorio del Examen Final:
    - Almacenamiento persistente de datos (archivos JSON).
    - Recuperación integral del inventario al reiniciar el programa.
    - Sincronización automática atómica tras operaciones de guardado, actualización y eliminación.
    """

    def __init__(
        self,
        ruta_archivo: str | Path = "data/productos.json",
        inicializar_demo: bool = True,
    ) -> None:
        self.__ruta_archivo: Path = Path(ruta_archivo)
        self.__codigos: set[str] = set()
        self.__productos_dict: dict[str, Producto] = {}
        self.__productos_list: list[Producto] = []

        # Asegurar creación del directorio contenedor si no existe
        self.__ruta_archivo.parent.mkdir(parents=True, exist_ok=True)

        if self.__ruta_archivo.exists() and self.__ruta_archivo.stat().st_size > 0:
            self.cargar_de_disco()
        elif inicializar_demo:
            self.restaurar_demo()
        else:
            self.guardar_en_disco()

    def obtener_ruta_archivo(self) -> str:
        """Retorna la ruta absoluta o relativa del archivo de datos."""
        return str(self.__ruta_archivo)

    def guardar_en_disco(self) -> None:
        """Serializa y persiste la lista completa de productos en el archivo JSON."""
        datos = [p.to_dict() for p in self.__productos_list]
        temp_file = self.__ruta_archivo.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        temp_file.replace(self.__ruta_archivo)

    def cargar_de_disco(self) -> None:
        """Recupera los productos almacenados en el archivo JSON."""
        if not self.__ruta_archivo.exists():
            return
        with open(self.__ruta_archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        self.__codigos.clear()
        self.__productos_dict.clear()
        self.__productos_list.clear()

        for item in datos:
            prod = Producto.from_dict(item)
            cod = prod.get_codigo()
            self.__codigos.add(cod)
            self.__productos_dict[cod] = prod
            self.__productos_list.append(prod)

    def restaurar_demo(self) -> None:
        """Reinicia el inventario con el catálogo predeterminado de demostración."""
        self.__codigos.clear()
        self.__productos_dict.clear()
        self.__productos_list.clear()

        cat_acc = Categoria("CAT-ACC", "Accesorios")
        cat_ele = Categoria("CAT-ELE", "Electrónica")
        cat_her = Categoria("CAT-HER", "Herramientas")
        cat_red = Categoria("CAT-RED", "Redes y Conectividad")
        cat_alm = Categoria("CAT-ALM", "Almacenamiento")

        demos = [
            Producto("PRD-001", "Lector de Código de Barras Láser RF", 145.00, 25, cat_acc),
            Producto("PRD-002", "Terminal Portátil de Inventario Android", 380.00, 12, cat_ele),
            Producto("PRD-003", "Impresora Térmica de Etiquetas 4x6", 210.00, 18, cat_ele),
            Producto("PRD-004", "Bobina de Cable UTP Cat6 305m", 85.50, 30, cat_red),
            Producto("PRD-005", "Transpaleta Hidráulica Manual 2.5 Ton", 450.00, 6, cat_her),
            Producto("PRD-006", "Switch Gigabit Gestionable 24 Puertos", 175.00, 15, cat_red),
            Producto("PRD-007", "Disco Sólido SSD NVMe 1TB Industrial", 115.00, 40, cat_alm),
        ]
        for p in demos:
            self.guardar(p)

    def guardar(self, producto: Producto) -> None:
        codigo = producto.get_codigo()
        if codigo in self.__codigos:
            raise ValueError(f"El producto con código '{codigo}' ya está registrado.")
        self.__codigos.add(codigo)
        self.__productos_dict[codigo] = producto
        self.__productos_list.append(producto)
        self.guardar_en_disco()

    def obtener_por_codigo(self, codigo: str) -> Optional[Producto]:
        return self.__productos_dict.get(codigo.strip().upper())

    def obtener_todos(self) -> list[Producto]:
        return list(self.__productos_list)

    def actualizar(
        self,
        codigo: str,
        nombre: str,
        precio: float,
        stock: int,
        categoria: Categoria,
    ) -> None:
        producto = self.obtener_por_codigo(codigo)
        if not producto:
            raise KeyError(f"No existe ningún producto con el código '{codigo}'.")
        producto.set_nombre(nombre)
        producto.set_precio(precio)
        producto.set_stock(stock)
        producto.set_categoria(categoria)
        self.guardar_en_disco()

    def eliminar(self, codigo: str) -> None:
        codigo_norm = codigo.strip().upper()
        producto = self.obtener_por_codigo(codigo_norm)
        if not producto:
            raise KeyError(f"No se puede eliminar: el código '{codigo_norm}' no existe.")
        self.__codigos.remove(codigo_norm)
        del self.__productos_dict[codigo_norm]
        self.__productos_list.remove(producto)
        self.guardar_en_disco()

    def buscar_por_nombre(self, query: str) -> list[Producto]:
        texto = query.strip().lower()
        if not texto:
            return self.obtener_todos()
        return [
            p for p in self.__productos_list
            if texto in p.get_nombre().lower() or texto in p.get_codigo().lower()
        ]

    def filtrar_por_categoria(self, categoria: str) -> list[Producto]:
        cat_filtro = categoria.strip().lower()
        if not cat_filtro or cat_filtro == "todas":
            return self.obtener_todos()
        return [
            p for p in self.__productos_list
            if p.get_categoria().get_nombre().lower() == cat_filtro
        ]

    def contar(self) -> int:
        return len(self.__codigos)

    def total_unidades(self) -> int:
        return sum(p.get_stock() for p in self.__productos_list)

    def valor_total(self) -> float:
        return sum(p.calcular_valor_inventario() for p in self.__productos_list)


# 3. INTERFAZ ABSTRACTA DEL REPOSITORIO DE DESPACHOS

class IDespachoRepository(ABC):
    """
    Contrato abstracto que define las operaciones para la administración
    de órdenes de despacho utilizando una estructura lineal (Cola/Pila).
    """

    @abstractmethod
    def encolar_despacho(self, pedido: PedidoDespacho) -> None:
        """Agrega una solicitud a la cola de atención."""
        pass

    @abstractmethod
    def despachar_siguiente(self) -> PedidoDespacho:
        """Atiende y remueve la siguiente solicitud en orden FIFO."""
        pass

    @abstractmethod
    def consultar_proximo(self) -> PedidoDespacho:
        """Consulta la próxima solicitud en cola sin removerla."""
        pass

    @abstractmethod
    def listar_pendientes(self) -> list[PedidoDespacho]:
        """Retorna la lista de todas las órdenes en espera."""
        pass

    @abstractmethod
    def total_pendientes(self) -> int:
        """Retorna la cantidad de órdenes pendientes."""
        pass

    @abstractmethod
    def esta_vacio(self) -> bool:
        """Indica si no hay pedidos pendientes en la cola."""
        pass

    @abstractmethod
    def listar_historial(self) -> list[PedidoDespacho]:
        """Retorna el historial de despachos completados (LIFO)."""
        pass


# 4. IMPLEMENTACIÓN CONCRETA CON COLA LINEAL MANUAL

class DespachoColaRepository(IDespachoRepository):
    """
    Implementación del repositorio de despachos respaldado por la
    estructura lineal 'ColaLineal' manual (FIFO) y 'PilaLineal' (LIFO),
    con soporte integral para persistencia en archivo JSON.
    
    Separa completamente el flujo logístico de la capa gráfica, conecta
    con el inventario para validar y descontar existencias físicas, y
    garantiza la persistencia de órdenes pendientes e historial.
    """

    def __init__(
        self,
        producto_repo: Optional[IProductoRepository] = None,
        ruta_archivo: Optional[str | Path] = None,
        inicializar_demo: bool = False,
    ) -> None:
        """
        Inicializa el repositorio integrando la ColaLineal manual y persistencia opcional.
        
        Args:
            producto_repo: Instancia opcional del repositorio de productos
                           para validar y sincronizar el stock disponible.
            ruta_archivo: Ruta opcional a un archivo JSON para persistir órdenes.
            inicializar_demo: Si es True y el archivo no existe, precarga pedidos de demo.
        """
        # Estructura manual LINEAL COLA (FIFO) para solicitudes en espera
        self.__cola_pendientes: ColaLineal[PedidoDespacho] = ColaLineal()
        # Estructura manual LINEAL PILA (LIFO) para historial de despachos
        self.__historial_despachos: PilaLineal[PedidoDespacho] = PilaLineal()
        self.__producto_repo: Optional[IProductoRepository] = producto_repo
        self.__ruta_archivo: Optional[Path] = Path(ruta_archivo) if ruta_archivo else None

        if self.__ruta_archivo:
            self.__ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
            if self.__ruta_archivo.exists() and self.__ruta_archivo.stat().st_size > 0:
                self.cargar_de_disco()
            elif inicializar_demo:
                self.restaurar_demo()
            else:
                self.guardar_en_disco()

    def obtener_ruta_archivo(self) -> Optional[str]:
        """Retorna la ruta del archivo de persistencia si está configurado."""
        return str(self.__ruta_archivo) if self.__ruta_archivo else None

    def guardar_en_disco(self) -> None:
        """Persiste las colas de pedidos pendientes e historial en archivo JSON."""
        if not self.__ruta_archivo:
            return
        datos = {
            "pendientes": [p.to_dict() for p in self.__cola_pendientes.a_lista()],
            "historial": [p.to_dict() for p in reversed(self.__historial_despachos.a_lista())],
        }
        temp_file = self.__ruta_archivo.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        temp_file.replace(self.__ruta_archivo)

    def cargar_de_disco(self) -> None:
        """Carga las órdenes pendientes en la ColaLineal y el historial en la PilaLineal."""
        if not self.__ruta_archivo or not self.__ruta_archivo.exists():
            return
        with open(self.__ruta_archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        self.__cola_pendientes = ColaLineal()
        self.__historial_despachos = PilaLineal()

        for item in datos.get("pendientes", []):
            self.__cola_pendientes.encolar(PedidoDespacho.from_dict(item))

        for item in datos.get("historial", []):
            self.__historial_despachos.apilar(PedidoDespacho.from_dict(item))

    def restaurar_demo(self) -> None:
        """Carga órdenes de demostración iniciales y las guarda en disco."""
        self.__cola_pendientes = ColaLineal()
        self.__historial_despachos = PilaLineal()

        ord1 = PedidoDespacho("ORD-101", "Sucursal Guayaquil Centro", "PRD-001", "Lector Láser", 3)
        ord2 = PedidoDespacho("ORD-102", "Logística Quito Norte", "PRD-003", "Impresora Térmica", 2)
        self.encolar_despacho(ord1)
        self.encolar_despacho(ord2)

    def encolar_despacho(self, pedido: PedidoDespacho) -> None:
        """
        Registra una nueva orden en la cola FIFO y persiste en disco.
        Si existe un repositorio de productos, valida que el producto exista
        y que haya stock suficiente para la solicitud.
        """
        if self.__producto_repo:
            producto = self.__producto_repo.obtener_por_codigo(pedido.get_codigo_producto())
            if not producto:
                raise KeyError(
                    f"No se puede encolar el pedido: El producto "
                    f"'{pedido.get_codigo_producto()}' no existe en el catálogo."
                )
            if producto.get_stock() < pedido.get_cantidad():
                raise ValueError(
                    f"Stock insuficiente en bodega para el producto '{producto.get_nombre()}'. "
                    f"Disponible: {producto.get_stock()} uds., "
                    f"Solicitado: {pedido.get_cantidad()} uds."
                )

        # Inserción en la cola manual O(1)
        self.__cola_pendientes.encolar(pedido)
        self.guardar_en_disco()

    def despachar_siguiente(self) -> PedidoDespacho:
        """
        Extrae y procesa el pedido al frente de la cola (FIFO).
        Descuenta el stock físico del producto, actualiza persistencia y
        guarda la orden en la pila de historial.
        
        Raises:
            ColaVaciaError: Si no hay despachos en espera.
            ValueError: Si el stock actual es insuficiente al momento del despacho.
        """
        if self.__cola_pendientes.esta_vacia():
            raise ColaVaciaError("No hay pedidos pendientes en la cola de despacho.")

        # Desencolar de la estructura lineal O(1)
        pedido = self.__cola_pendientes.desencolar()

        # Descontar stock del producto en el inventario si hay repositorio vinculado
        if self.__producto_repo:
            producto = self.__producto_repo.obtener_por_codigo(pedido.get_codigo_producto())
            if producto:
                if producto.get_stock() < pedido.get_cantidad():
                    raise ValueError(
                        f"Stock insuficiente al momento de despachar. "
                        f"Disponible: {producto.get_stock()}, "
                        f"Requerido: {pedido.get_cantidad()}."
                    )
                producto.disminuir_stock(pedido.get_cantidad())
                # Si el repositorio de productos es persistente, sincronizar en disco
                if hasattr(self.__producto_repo, "guardar_en_disco"):
                    self.__producto_repo.guardar_en_disco()

        # Marcar estado como completado y apilar en el historial de auditoría
        pedido.marcar_despachado()
        self.__historial_despachos.apilar(pedido)
        self.guardar_en_disco()

        return pedido

    def consultar_proximo(self) -> PedidoDespacho:
        """Consulta el siguiente pedido a despachar sin removerlo (Peek)."""
        return self.__cola_pendientes.ver_frente()

    def listar_pendientes(self) -> list[PedidoDespacho]:
        """Retorna todas las órdenes en espera en orden de turno."""
        return self.__cola_pendientes.a_lista()

    def total_pendientes(self) -> int:
        """Retorna el número de despachos pendientes."""
        return self.__cola_pendientes.tamano()

    def esta_vacio(self) -> bool:
        """Indica si la cola de despacho está vacía."""
        return self.__cola_pendientes.esta_vacia()

    def listar_historial(self) -> list[PedidoDespacho]:
        """Retorna las órdenes despachadas en orden cronológico inverso (LIFO)."""
        return self.__historial_despachos.a_lista()
