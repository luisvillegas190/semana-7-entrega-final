# 🏭 Sistema de Gestión de Bodega — Despachos FIFO, Patrón Repository, Persistencia JSON y Pytest

![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-38_Passed-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Flet](https://img.shields.io/badge/GUI-Flet_1.0-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2.10+-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Persistencia](https://img.shields.io/badge/Persistencia-Archivos_JSON-F7DF1E?style=for-the-badge&logo=json&logoColor=black)
![Actividad](https://img.shields.io/badge/Examen_Final-Presentación_y_Explicación-1B365D?style=for-the-badge)

---

## 📌 Datos del Estudiante y Actividad Académica

* **Estudiante:** Luis Alberto Villegas Merchan
* **Carrera:** Programación Estructurada
* **Materia:** Programación Orientada a Objetos / Programación Estructurada
* **Actividad:** Examen Final — Presentación y Explicación del Proyecto (Semanas 5, 6 y 7)
* **Lenguaje:** Python 3.14+
* **Framework Gráfico:** Flet (GUI Desktop)
* **Framework de Testing:** Pytest 9.1+

---

## 📑 Tabla de Contenidos

1. [Descripción General del Proyecto](#-descripción-general-del-proyecto)
2. [Objetivo del Proyecto](#-objetivo-del-proyecto)
3. [Principales Funcionalidades](#-principales-funcionalidades)
4. [Persistencia de Datos (Archivos JSON)](#-persistencia-de-datos-archivos-json)
5. [Estructura de Datos Lineal Manual (Cola FIFO y Pila LIFO)](#-estructura-de-datos-lineal-manual-cola-fifo-y-pila-lifo)
6. [Patrón de Diseño Repository](#%EF%B8%8F-patrón-de-diseño-repository)
7. [Interfaz Gráfica de Usuario (Flet)](#-interfaz-gráfica-de-usuario-flet)
8. [Pruebas Unitarias con Pytest](#-pruebas-unitarias-con-pytest)
9. [Estructura del Proyecto](#-estructura-del-proyecto)
10. [Instrucciones de Instalación y Ejecución](#-instrucciones-de-instalación-y-ejecución)

---

## 📦 Descripción General del Proyecto

Este proyecto implementa un **Sistema de Gestión de Bodega e Inventario** completo, desarrollado en Python, que simula el flujo logístico de un centro de distribución: desde el registro de productos en catálogo, hasta la gestión de órdenes de despacho procesadas en estricto orden de llegada (**FIFO**), con almacenamiento **persistente en archivos JSON** y una **interfaz gráfica desktop** moderna e interactiva.

El sistema integra y demuestra de forma práctica los conocimientos adquiridos durante las **Semanas 5, 6 y 7** de la asignatura:

| Semana | Tema | Implementación en el Proyecto |
| :---: | :--- | :--- |
| **5** | Colecciones Nativas y Encapsulación | Modelo de dominio (`Categoria`, `Producto`, `PedidoDespacho`) con `set`, `dict`, `list` y atributos privados `__`. Validación con Pydantic. |
| **6** | Interfaz Gráfica de Usuario (GUI) | Aplicación de escritorio completa con Flet: CRUD de productos, filtros, métricas en tiempo real y navegación por pestañas. |
| **7** | Patrones de Diseño, TDAs Lineales y Testing | Patrón Repository (ABC), Cola FIFO y Pila LIFO manuales con nodos enlazados, y suite de 38 pruebas automatizadas con Pytest. |
| **Examen** | Persistencia de Datos + Presentación | `ProductoRepositoryJSON` y `DespachoColaRepository` con persistencia atómica en archivos JSON (`data/productos.json`, `data/despachos.json`). |

---

## 🎯 Objetivo del Proyecto

Diseñar y desarrollar un sistema funcional que demuestre la aplicación práctica de:

1. **Programación Orientada a Objetos**: Clases encapsuladas, herencia mediante clases abstractas (ABC), polimorfismo en el patrón Repository y validación de datos con Pydantic.
2. **Tipos de Datos Abstractos Lineales**: Implementación manual de una Cola (FIFO) y una Pila (LIFO) con nodos enlazados, sin utilizar bibliotecas nativas como `deque` o `Queue`.
3. **Patrones de Diseño**: Patrón Repository que desacopla la lógica de acceso a datos de la interfaz gráfica, permitiendo intercambiar la implementación en memoria por una persistente en JSON sin modificar la GUI.
4. **Persistencia de Datos**: Almacenamiento y recuperación automática de información desde archivos JSON en disco, garantizando que los datos sobrevivan al reinicio del programa.
5. **Interfaz Gráfica**: Aplicación desktop interactiva con Flet que visualiza en tiempo real las estructuras de datos, las métricas del inventario y el flujo de despachos.
6. **Testing Unitario**: Suite completa de 38 pruebas automatizadas con Pytest que cubren modelos, estructuras lineales, repositorios y persistencia.

---

## ⚙️ Principales Funcionalidades

### Catálogo de Productos (Inventario)
- **CRUD completo**: Crear, consultar, actualizar y eliminar productos del inventario.
- **Búsqueda y filtros**: Por nombre, código y/o categoría en tiempo real.
- **Métricas globales**: Productos distintos, total de unidades en stock y valor monetario del inventario.
- **Validación de datos**: Pydantic garantiza tipos, rangos y longitudes correctas.

### Centro de Despachos (Cola FIFO)
- **Encolar solicitudes**: Registrar órdenes de salida verificando existencias físicas.
- **Despachar en orden FIFO**: El primer pedido en llegar es el primero en ser atendido.
- **Descuento automático de stock**: Al despachar, se descuentan las unidades del inventario y se sincroniza en disco.
- **Historial de auditoría (Pila LIFO)**: Registro cronológico inverso de todos los despachos completados.
- **Visualización interactiva**: Tarjetas con turno, estado (frente/en espera) y datos del pedido.

### Persistencia de Datos
- **Almacenamiento en JSON**: Productos en `data/productos.json` y despachos en `data/despachos.json`.
- **Recuperación automática**: Al reiniciar la aplicación, los datos se restauran íntegramente desde disco.
- **Escritura atómica**: Se usa un archivo temporal `.tmp` antes de reemplazar el archivo final para evitar corrupción.
- **Sincronización en cada operación**: Guardar, actualizar, eliminar y despachar persisten los cambios inmediatamente.

---

## 💾 Persistencia de Datos (Archivos JSON)

El proyecto cumple con el **requisito obligatorio del examen** de almacenar y recuperar información de forma persistente. La persistencia se implementa mediante archivos JSON en el directorio `data/`:

```
data/
├── productos.json      ← Catálogo completo del inventario (se crea automáticamente)
└── despachos.json      ← Órdenes pendientes en Cola FIFO + historial en Pila LIFO
```

### Flujo de Persistencia

```
                    ┌───────────────────────────────────────┐
                    │         Interfaz Gráfica (Flet)       │
                    │  Guardar │ Actualizar │ Eliminar │ Despachar
                    └─────┬────┴─────┬──────┴────┬─────┴───┘
                          │          │           │
                          ▼          ▼           ▼
                    ┌─────────────────────────────────────┐
                    │     Patrón Repository (Contratos)    │
                    │  IProductoRepository  IDespachoRepo  │
                    └────────┬───────────────────┬────────┘
                             │                   │
              ┌──────────────▼───┐     ┌─────────▼─────────┐
              │ ProductoRepo     │     │ DespachoColaRepo   │
              │ JSON             │     │ (ColaLineal FIFO)  │
              │ guardar_en_disco │     │ guardar_en_disco   │
              └────────┬─────────┘     └─────────┬─────────┘
                       │                         │
                       ▼                         ▼
              ┌────────────────┐      ┌──────────────────┐
              │ productos.json │      │ despachos.json   │
              │ (Archivo Disco)│      │ (Archivo Disco)  │
              └────────────────┘      └──────────────────┘
```

### Clases Clave de Persistencia

| Clase | Archivo | Descripción |
| :--- | :--- | :--- |
| `ProductoRepositoryJSON` | `repositorio.py` | Implementa `IProductoRepository` con lectura/escritura automática a `data/productos.json`. |
| `DespachoColaRepository` | `repositorio.py` | Implementa `IDespachoRepository` con persistencia opcional en `data/despachos.json`. |
| `Producto.to_dict()` / `from_dict()` | `modelo.py` | Serialización y deserialización de productos a/desde diccionarios JSON. |
| `PedidoDespacho.to_dict()` / `from_dict()` | `modelo.py` | Serialización y deserialización de órdenes de despacho. |
| `Categoria.to_dict()` / `from_dict()` | `modelo.py` | Serialización y deserialización de categorías. |

### Ejemplo de `data/productos.json`

```json
[
  {
    "codigo": "PRD-001",
    "nombre": "Lector de Código de Barras Láser RF",
    "precio": 145.0,
    "stock": 25,
    "categoria": {
      "codigo": "CAT-ACC",
      "nombre": "Accesorios"
    }
  }
]
```

### Ejemplo de `data/despachos.json`

```json
{
  "pendientes": [
    {
      "id_pedido": "ORD-101",
      "cliente": "Sucursal Guayaquil Centro",
      "codigo_producto": "PRD-001",
      "nombre_producto": "Lector Láser",
      "cantidad": 3,
      "fecha_registro": "2026-10-01 18:46:04",
      "estado": "PENDIENTE"
    }
  ],
  "historial": []
}
```

---

## 🧩 Estructura de Datos Lineal Manual (Cola FIFO y Pila LIFO)

Las estructuras fueron desarrolladas en `estructuras_lineales.py` utilizando una **Lista Simplemente Enlazada de Nodos (`Nodo[T]`)**, garantizando tiempo constante **O(1)** en todas las operaciones críticas:

### 1. Cola Lineal (`ColaLineal[T]`) — FIFO
Administra las solicitudes de despacho pendientes en orden de llegada:

| Operación | Método | Complejidad | Descripción |
| :--- | :--- | :---: | :--- |
| **Agregar** | `encolar(elemento)` | O(1) | Inserta un nodo al final ajustando el puntero `__final`. |
| **Eliminar** | `desencolar()` | O(1) | Extrae y retorna el elemento al frente (`__frente`). |
| **Consultar** | `ver_frente()` | O(1) | Retorna el dato al frente sin removerlo (Peek). |
| **Verificar vacía** | `esta_vacia()` | O(1) | Comprueba si `__frente is None`. |
| **Tamaño** | `tamano()` / `len()` | O(1) | Retorna el contador interno `__longitud`. |
| **Exportar** | `a_lista()` | O(n) | Genera una lista secuencial para renderizado. |

> **Excepciones personalizadas:** Si se intenta `desencolar()` o consultar `ver_frente()` en una cola vacía, se lanza `ColaVaciaError`.

### 2. Pila Lineal (`PilaLineal[T]`) — LIFO
Administra el historial de auditoría de despachos completados:
* `apilar(elemento)` (O(1)): Inserta en el tope.
* `desapilar()` (O(1)): Extrae del tope.
* `ver_tope()` (O(1)): Consulta el último despacho realizado.
* `esta_vacia()` y `tamano()` (O(1)).

---

## 🏛️ Patrón de Diseño Repository

El patrón Repository centraliza la lógica de acceso a datos, aislando el dominio y la interfaz de usuario de los mecanismos de almacenamiento.

```
+-----------------------------------------------------------+
|               Capa de Presentación / GUI                  |
|          (Flet Desktop en app.py / CLI en main.py)        |
+-----------------------------+-----------------------------+
                              | (Usa abstracciones)
                              v
+-----------------------------------------------------------+
|                 Contratos Abstractos (ABC)                |
|           IProductoRepository    IDespachoRepository       |
+-----------------------------+-----------------------------+
                              | (Implementan interfaces)
                              v
+-----------------------------------------------------------+
|                Implementaciones Concretas                 |
|  ProductoRepositoryMemoria      ProductoRepositoryJSON    |
|   (set/dict/list en memoria)    (JSON persistente disco)  |
|                                                           |
|  DespachoColaRepository                                   |
|   (ColaLineal Manual + Pila LIFO + JSON persistente)      |
+-----------------------------------------------------------+
```

### Componentes Clave en `repositorio.py`:

| Componente | Tipo | Responsabilidad |
| :--- | :--- | :--- |
| `IProductoRepository` | ABC (Interfaz) | Contrato abstracto para CRUD de productos. |
| `IDespachoRepository` | ABC (Interfaz) | Contrato abstracto para operaciones de despacho FIFO. |
| `ProductoRepositoryMemoria` | Implementación | Repositorio de productos en memoria (retrocompatible). |
| `ProductoRepositoryJSON` | Implementación | Repositorio de productos con persistencia en `data/productos.json`. |
| `DespachoColaRepository` | Implementación | Repositorio de despachos con `ColaLineal` FIFO, `PilaLineal` LIFO y persistencia opcional en JSON. |

**Ventaja del desacoplamiento:** La GUI en `app.py` funciona igual con `ProductoRepositoryMemoria` (en memoria) o con `ProductoRepositoryJSON` (persistente en disco), ya que ambas implementan el mismo contrato `IProductoRepository`. Solo se cambia la línea de instanciación.

---

## 🖥️ Interfaz Gráfica de Usuario (Flet)

La interfaz está implementada en `app.py` con **Flet 1.0** y ofrece dos pestañas principales:

### Pestaña 1: Catálogo de Productos (Inventario)
- Formulario de registro con validación Pydantic.
- Tabla interactiva con acciones de editar y eliminar por fila.
- Barra de búsqueda y filtro por categoría.
- Tarjetas métricas: Productos distintos, unidades en stock, valor total.

### Pestaña 2: Centro de Despachos (Cola FIFO)
- Formulario para encolar nuevas órdenes de salida.
- Visualización en tiempo real de la Cola Lineal con turno, frente y estado.
- Botón de despacho FIFO que procesa el pedido al frente y descuenta stock.
- Historial de auditoría respaldado por la PilaLineal (LIFO).

### Características Adicionales
- **Badge de Persistencia Activa (JSON)**: Indicador visual en el encabezado.
- **Botón "Restablecer Demo"**: Restaura el catálogo y las órdenes de demostración.
- **Modo Claro / Oscuro**: Alternancia de tema con un botón.
- **Notificaciones (SnackBar)**: Confirmación visual de cada operación.

---

## 🧪 Pruebas Unitarias con Pytest

Se implementaron **38 pruebas automatizadas** organizadas en 4 archivos de tests:

| Archivo | Pruebas | Cobertura |
| :--- | :---: | :--- |
| `test_estructuras_lineales.py` | 12 | Cola FIFO (encolar, desencolar, peek, vacía, iteración) y Pila LIFO (apilar, desapilar, tope). |
| `test_modelo.py` | 8 | Validación Pydantic, creación de entidades, stock, estados de pedido. |
| `test_repositorio.py` | 12 | CRUD en `ProductoRepositoryMemoria`, integración `DespachoColaRepository` con ColaLineal y control de stock. |
| `test_persistencia.py` | 6 | Serialización `to_dict`/`from_dict`, persistencia en disco de `ProductoRepositoryJSON`, recarga de `DespachoColaRepository` desde archivo JSON. |

### Ejecutar las pruebas:

```bash
python -m pytest -v
```

Resultado esperado:
```
============================= test session starts =============================
collected 38 items

tests/test_estructuras_lineales.py   ............                        [ 31%]
tests/test_modelo.py                 ........                            [ 52%]
tests/test_persistencia.py           ......                              [ 68%]
tests/test_repositorio.py            ............                        [100%]

============================= 38 passed ======================================
```

---

## 📁 Estructura del Proyecto

```
semana-7-entrega-final/
│
├── main.py                         # Punto de entrada principal (GUI o CLI con --cli)
├── app.py                          # Interfaz gráfica Flet con persistencia JSON
├── modelo.py                       # Modelo de dominio: Categoria, Producto, PedidoDespacho
│                                   #   + Validación Pydantic (DatosCategoria, DatosProducto, etc.)
│                                   #   + Serialización to_dict() / from_dict() para JSON
├── estructuras_lineales.py         # TDAs Lineales manuales: Nodo, ColaLineal (FIFO), PilaLineal (LIFO)
├── repositorio.py                  # Patrón Repository:
│                                   #   IProductoRepository (ABC), IDespachoRepository (ABC)
│                                   #   ProductoRepositoryMemoria (en memoria)
│                                   #   ProductoRepositoryJSON (persistente en disco)
│                                   #   DespachoColaRepository (Cola + Pila + JSON)
│
├── data/                           # Directorio de datos persistentes (creado automáticamente)
│   ├── productos.json              #   Catálogo de productos serializado
│   └── despachos.json              #   Órdenes pendientes + historial de despachos
│
├── tests/                          # Suite de pruebas unitarias
│   ├── __init__.py
│   ├── test_estructuras_lineales.py  # 12 tests: Cola FIFO y Pila LIFO
│   ├── test_modelo.py                # 8 tests: Validación y entidades del dominio
│   ├── test_repositorio.py           # 12 tests: CRUD Repository e integración ColaLineal
│   └── test_persistencia.py          # 6 tests: Serialización y persistencia JSON en disco
│
├── requirements.txt                # Dependencias: flet, pydantic, pytest, ruff, reportlab
├── Villegas_Luis_Semana7.pdf       # Documentación PDF de la entrega
├── .gitignore                      # Archivos excluidos del repositorio
└── README.md                       # Este archivo
```

---

## 🚀 Instrucciones de Instalación y Ejecución

### Requisitos Previos
- **Python 3.10** o superior instalado.
- **pip** (gestor de paquetes de Python).

### 1. Clonar el Repositorio

```bash
git clone https://github.com/luisvillegas190/semana-7-entrega-final.git
cd semana-7-entrega-final
```

### 2. Crear y Activar un Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Interfaz Gráfica (GUI)

```bash
python main.py
```

Se abrirá la ventana de escritorio con el sistema completo. Los datos se persisten automáticamente en `data/productos.json` y `data/despachos.json`.

### 5. Ejecutar la Demostración en Consola (CLI)

```bash
python main.py --cli
```

Muestra una demostración paso a paso de las 4 partes del proyecto: Cola FIFO, Pila LIFO, Patrón Repository y Persistencia JSON.

### 6. Ejecutar las Pruebas Unitarias

```bash
python -m pytest -v
```

---

## 📜 Licencia

Proyecto académico desarrollado para la materia de Programación Estructurada / Programación Orientada a Objetos.

**Estudiante:** Luis Alberto Villegas Merchan
