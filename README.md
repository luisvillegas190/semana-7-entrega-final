# Sistema de Gestión de Bodega — Despachos con Cola FIFO, Patrón Repository y Pytest

![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-32_Passed-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Flet](https://img.shields.io/badge/GUI-Flet_1.0-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2.10+-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Actividad](https://img.shields.io/badge/Semana_7-Patrones_de_Diseño_&_TDAs-1B365D?style=for-the-badge)

---

## 📌 Datos del Estudiante y Actividad Académica

* **Estudiante:** Luis Alberto Villegas Merchan
* **Carrera:** Programación Estructurada
* **Materia:** Programación Orientada a Objetos / Programación Estructurada
* **Actividad:** Semana 7 — Patrones de Diseño, Testing Unitario y Tipos de Datos Abstractos Lineales
* **Lenguaje:** Python 3.14+
* **Framework Gráfico:** Flet (GUI Desktop)
* **Framework de Testing:** Pytest 9.1+

---

## 📑 Tabla de Contenidos

1. [Descripción General y Caso Práctico](#-descripción-general-y-caso-práctico)
2. [Estructura de Datos Lineal Manual (Cola FIFO y Pila LIFO)](#-estructura-de-datos-lineal-manual-cola-fifo-y-pila-lifo)
3. [Patrón de Diseño Repository](#-patrón-de-diseño-repository)
4. [Pruebas Unitarias con Pytest](#-pruebas-unitarias-con-pytest)
5. [Interfaz Gráfica de Usuario (Flet)](#-interfaz-gráfica-de-usuario-flet)
6. [Estructura del Proyecto](#-estructura-del-proyecto)
7. [Instrucciones de Instalación y Ejecución](#-instrucciones-de-instalación-y-ejecución)
8. [Instrucciones para Actualizar Repositorio en GitHub](#-instrucciones-para-actualizar-repositorio-en-github)

---

## 📦 Descripción General y Caso Práctico

En una bodega logística o centro de distribución, la salida de mercancía hacia clientes o sucursales debe procesarse de manera justa, ordenada y predecible: las órdenes deben ser despachadas en el **mismo orden cronológico en que fueron solicitadas**, bajo el principio **FIFO (First-In, First-Out)**.

Este proyecto resuelve este problema integrando:
1. **Un Tipo de Dato Abstracto (TDA) Lineal tipo Cola (`ColaLineal`)** implementado **manualmente desde cero** mediante nodos enlazados, sin utilizar bibliotecas nativas de colas (`deque` o `Queue`).
2. **El Patrón de Diseño Repository**, que desacopla el almacenamiento y la manipulación de datos de la lógica de negocio y de la interfaz visual. El repositorio de despachos (`DespachoColaRepository`) integra directamente la `ColaLineal` manual.
3. **Una Pila Lineal (`PilaLineal`)** para auditoría e historial cronológico inverso de órdenes despachadas (LIFO).
4. **Una suite completa de 32 pruebas unitarias automatizadas con `pytest`**, cubriendo todos los casos de uso, transiciones de estado, casos borde y excepciones.
5. **Una Interfaz Gráfica interactiva y moderna con Flet**, con navegación por pestañas entre el Catálogo de Productos y el Centro de Despachos en tiempo real.

---

## 🧩 Estructura de Datos Lineal Manual (Cola FIFO y Pila LIFO)

En cumplimiento de la consigna pedagógica, las estructuras fueron desarrolladas en `estructuras_lineales.py` utilizando una **Lista Simplemente Enlazada de Nodos (`Nodo[T]`)**, garantizando tiempo constante **$O(1)$** en todas las operaciones críticas:

### 1. Cola Lineal (`ColaLineal[T]`) — FIFO
Administra las solicitudes de despacho pendientes en orden de llegada:

| Operación | Método | Complejidad Temporal | Descripción |
| :--- | :--- | :---: | :--- |
| **Agregar elemento** | `encolar(elemento)` (Enqueue) | $O(1)$ | Inserta un nuevo nodo al final de la cola ajustando el puntero `__final`. |
| **Eliminar elemento** | `desencolar()` (Dequeue) | $O(1)$ | Extrae y retorna el elemento al frente (`__frente`), avanzando al siguiente. |
| **Consultar siguiente** | `ver_frente()` (Peek) | $O(1)$ | Retorna el dato al frente sin removerlo ni alterar la cola. |
| **Verificar si está vacía** | `esta_vacia()` (IsEmpty) | $O(1)$ | Comprueba si `__frente is None`. |
| **Consultar cantidad** | `tamano()` / `len()` (Size) | $O(1)$ | Retorna el contador interno `__longitud`. |
| **Exportar a lista** | `a_lista()` | $O(n)$ | Genera una lista secuencial para renderizado en la interfaz gráfica. |

> **Excepciones personalizadas:** Si se intenta `desencolar()` o consultar `ver_frente()` en una cola vacía, se lanza de forma controlada la excepción `ColaVaciaError`.

### 2. Pila Lineal (`PilaLineal[T]`) — LIFO
Administra el historial de auditoría de despachos completados:
* `apilar(elemento)` ($O(1)$): Inserta en el tope.
* `desapilar()` ($O(1)$): Extrae del tope.
* `ver_tope()` ($O(1)$): Consulta el último despacho realizado.
* `esta_vacia()` y `tamano()` ($O(1)$).

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
|  ProductoRepositoryMemoria        DespachoColaRepository  |
|   (set/dict/list en memoria)        (ColaLineal Manual)   |
+-----------------------------------------------------------+
```

### Componentes Clave en `repositorio.py`:
1. **`IProductoRepository` (ABC):** Define las firmas para `guardar`, `obtener_por_codigo`, `obtener_todos`, `actualizar`, `eliminar`, `buscar_por_nombre`, `filtrar_por_categoria`, `contar`, `total_unidades` y `valor_total`.
2. **`ProductoRepositoryMemoria`:** Implementa la interfaz para el catálogo de inventario.
3. **`IDespachoRepository` (ABC):** Define operaciones de cola: `encolar_despacho`, `despachar_siguiente`, `consultar_proximo`, `listar_pendientes`, `total_pendientes`, `esta_vacio` y `listar_historial`.
4. **`DespachoColaRepository`:** Integra **directamente la `ColaLineal` manual**. Al despachar (`despachar_siguiente`), atiende la orden en orden FIFO, valida y descuenta las existencias físicas del producto mediante el `IProductoRepository` de forma atómica y archiva la orden en la `PilaLineal` de auditoría.

---

## 🧪 Pruebas Unitarias con Pytest

Se implementaron **32 pruebas unitarias automatizadas** en el directorio `tests/`:

* **`tests/test_estructuras_lineales.py` (12 tests):**
  * Inicialización vacía, encolado individual y múltiple.
  * Verificación rigurosa del orden FIFO al desencolar.
  * Idempotencia de `ver_frente` (peek) sin remover elementos.
  * Manejo estricto de excepciones `ColaVaciaError` y `PilaVaciaError`.
  * Verificación de `PilaLineal` (orden LIFO, tope, tamaño).
* **`tests/test_repositorio.py` (12 tests):**
  * CRUD completo en `ProductoRepositoryMemoria`.
  * Prevención de códigos duplicados (`ValueError`).
  * Validación de existencia de producto al encolar en `DespachoColaRepository`.
  * Validación de stock insuficiente al momento de encolar y despachar.
  * Despacho FIFO con descuento automático de existencias físicas.
  * Verificación de cola vacía y archivo en historial de auditoría.
* **`tests/test_modelo.py` (8 tests):**
  * Validaciones de dominio con Pydantic (precios positivos, stock no negativo, cantidades mayores a cero).
  * Métodos de negocio `aumentar_stock` y `disminuir_stock`.

### Ejecución de Pruebas:
```powershell
python -m pytest -v
```

**Resultado de la Ejecución:**
```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
collected 32 items

tests/test_estructuras_lineales.py::TestColaLineal::test_inicializacion_cola_vacia PASSED
tests/test_estructuras_lineales.py::TestColaLineal::test_encolar_un_elemento PASSED
tests/test_estructuras_lineales.py::TestColaLineal::test_encolar_multiples_y_orden_fifo PASSED
tests/test_estructuras_lineales.py::TestColaLineal::test_ver_frente_no_altera_la_estructura PASSED
tests/test_estructuras_lineales.py::TestColaLineal::test_desencolar_en_cola_vacia_lanza_excepcion PASSED
tests/test_estructuras_lineales.py::TestColaLineal::test_ver_frente_en_cola_vacia_lanza_excepcion PASSED
tests/test_estructuras_lineales.py::TestColaLineal::test_limpiar_cola PASSED
tests/test_estructuras_lineales.py::TestColaLineal::test_iteracion_y_a_lista PASSED
tests/test_estructuras_lineales.py::TestPilaLineal::test_inicializacion_pila_vacia PASSED
tests/test_estructuras_lineales.py::TestPilaLineal::test_apilar_y_desapilar_orden_lifo PASSED
tests/test_estructuras_lineales.py::TestPilaLineal::test_desapilar_en_pila_vacia_lanza_excepcion PASSED
tests/test_estructuras_lineales.py::TestPilaLineal::test_ver_tope_en_pila_vacia_lanza_excepcion PASSED
tests/test_modelo.py::TestModeloDominio::test_creacion_categoria_valida PASSED
tests/test_modelo.py::TestModeloDominio::test_creacion_categoria_invalida PASSED
tests/test_modelo.py::TestModeloDominio::test_creacion_producto_valido PASSED
tests/test_modelo.py::TestModeloDominio::test_producto_precio_invalido PASSED
tests/test_modelo.py::TestModeloDominio::test_producto_stock_invalido PASSED
tests/test_modelo.py::TestModeloDominio::test_aumentar_y_disminuir_stock PASSED
tests/test_modelo.py::TestModeloDominio::test_pedido_despacho_valido PASSED
tests/test_modelo.py::TestModeloDominio::test_pedido_despacho_cantidad_invalida PASSED
tests/test_repositorio.py::TestProductoRepositoryMemoria::test_guardar_y_obtener_por_codigo PASSED
tests/test_repositorio.py::TestProductoRepositoryMemoria::test_evitar_codigo_duplicado PASSED
tests/test_repositorio.py::TestProductoRepositoryMemoria::test_actualizar_producto PASSED
tests/test_repositorio.py::TestProductoRepositoryMemoria::test_actualizar_inexistente_lanza_error PASSED
tests/test_repositorio.py::TestProductoRepositoryMemoria::test_eliminar_producto PASSED
tests/test_repositorio.py::TestProductoRepositoryMemoria::test_eliminar_inexistente_lanza_error PASSED
tests/test_repositorio.py::TestProductoRepositoryMemoria::test_metricas_globales PASSED
tests/test_repositorio.py::TestDespachoColaRepository::test_encolar_pedido_exitoso PASSED
tests/test_repositorio.py::TestDespachoColaRepository::test_encolar_producto_inexistente_falla PASSED
tests/test_repositorio.py::TestDespachoColaRepository::test_encolar_stock_insuficiente_falla PASSED
tests/test_repositorio.py::TestDespachoColaRepository::test_despachar_orden_fifo_y_descontar_stock PASSED
tests/test_repositorio.py::TestDespachoColaRepository::test_despachar_cola_vacia_lanza_error PASSED

============================= 32 passed in 0.19s ==============================
```

---

## 🖥️ Interfaz Gráfica de Usuario (Flet)

La aplicación implementa una interfaz moderna con navegación mediante pestañas:

1. **Pestaña "Catálogo de Productos":**
   * Formulario reactivo para Crear, Editar y Eliminar productos.
   * Tabla interactiva con búsqueda en tiempo real (`on_change`) y filtros por categoría.
   * Tarjetas de métricas calculadas automáticamente.
2. **Pestaña "Centro de Despachos (Cola FIFO)":**
   * Formulario para registrar órdenes de salida seleccionando el producto del inventario.
   * Verificación inmediata de disponibilidad física de existencias.
   * **Visualizador en vivo de la Cola FIFO:** Cada orden aparece con una tarjeta indicando su número de turno (`TURNO 1 - AL FRENTE`, `TURNO 2`, etc.).
   * **Botón "⚡ Despachar Siguiente Pedido (FIFO)":** Desencola la orden al frente, descuenta el stock del producto en el catálogo y notifica con `SnackBar`.
   * **Historial de Despachos Atendidos:** Respaldado por la estructura lineal `PilaLineal` (LIFO).
   * Modo Claro y Modo Oscuro dinámico.

---

## 📁 Estructura del Proyecto

```text
Villegas_Luis_Semana7/
│
├── estructuras_lineales.py   # Implementación manual de ColaLineal y PilaLineal con Nodos Enlazados
├── modelo.py                 # Entidades Categoria, Producto, PedidoDespacho y esquemas Pydantic
├── repositorio.py            # Interfaces IProductoRepository, IDespachoRepository e implementaciones
├── app.py                    # Interfaz Gráfica en Flet con pestañas de Inventario y Despachos FIFO
├── main.py                   # Punto de entrada principal (Modo GUI y Modo Demostración CLI)
├── requirements.txt          # Dependencias (flet, pydantic, pytest, ruff, reportlab)
├── .gitignore                # Exclusión de cachés y entornos virtuales
│
├── tests/                    # Suite de Pruebas Unitarias con Pytest
│   ├── __init__.py
│   ├── test_estructuras_lineales.py  # 12 tests para ColaLineal y PilaLineal
│   ├── test_repositorio.py           # 12 tests para patrón Repository y Cola
│   └── test_modelo.py                # 8 tests para modelos y validaciones Pydantic
│
└── Villegas_Luis_Semana7.pdf # Documento formal listo para entrega en Blackboard
```

---

## 🚀 Instrucciones de Instalación y Ejecución

### 1. Clonar o acceder a la carpeta del proyecto
```powershell
cd "C:\Users\ASUS\Desktop\Villegas_Luis_Semana7"
```

### 2. Instalar dependencias requeridas
```powershell
python -m pip install -r requirements.txt
```

### 3. Ejecutar las Pruebas Unitarias (Pytest)
```powershell
python -m pytest -v
```

### 4. Ejecutar la Aplicación Gráfica (Flet)
```powershell
python main.py
```

### 5. Ejecutar la Demostración en Consola (CLI)
```powershell
python main.py --cli
```

---

## 📤 Instrucciones para Actualizar Repositorio en GitHub

Para subir esta versión actualizada a tu repositorio público de GitHub:

```powershell
# 1. Situarse en la carpeta del proyecto
cd "C:\Users\ASUS\Desktop\Villegas_Luis_Semana7"

# 2. Inicializar o sincronizar el repositorio git
git init
git remote add origin https://github.com/luisvillegas190/semana-7-entrega-final.git
# (O si ya está configurado: git remote set-url origin https://github.com/luisvillegas190/semana-7-entrega-final.git)

# 3. Agregar los cambios y realizar el commit
git add .
git commit -m "Semana 7: Implementacion de ColaLineal manual, Patron Repository, Despachos FIFO y Suite de Pytest"

# 4. Enviar los cambios al repositorio remoto
git branch -M main
git push -u origin main --force
```

---

## 👨‍💻 Autor

**Luis Alberto Villegas Merchan**  
Estudiante de Programación Estructurada / Ingeniería de Software
