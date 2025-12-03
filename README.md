# Mi Tienda - Sistema de Gestión Comercial

**Sistema completo de gestión comercial para administración de inventario, proveedores, usuarios y productos**

![Version](https://img.shields.io/badge/version-1.0.0-blue)

## Características Principales

---

### Gestión de Productos
- Crear, leer, actualizar y eliminar productos
- Búsqueda de producto por ID
- Listar todos los productos activos 
- Modificar información del producto
- Eliminar marcar producto como inactivo
- Ver y reactivar productos eliminados

### Gestión de Usuarios
- Crear, leer, actualizar y eliminar usuarios
- Búsqueda de usuario por ID
- Listar todos los usuarios activos 
- Modificar información del usuario
- Eliminar marcar usuario como inactivo
- Ver y reactivar usuario eliminados

### Gestión de Proveedores
- Crear, leer, actualizar y eliminar proveedor
- Búsqueda de proveedor por ID
- Listar todos los proveedores activos 
- Modificar información del proveedor
- Eliminar marcar proveedor como inactivo
- Ver y reactivar proveedor eliminados

### Gestión de Categorias
- Crear, leer, actualizar y eliminar categoria
- Búsqueda de categoria por ID
- Listar todos las categorias activos 
- Modificar información de la categoria
- Eliminar marcar categoria como inactivo
- Ver y reactivar categoria eliminados

### API Externa - Open Food Facts
- Busqueda de productos en Open Food Facts API
- Datos de la API

### Reportes y Estadísticas
- Dashboard con métricas clave
- Alertas y notificaciones

## Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Python 3.9+** - Lenguaje principal
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos principal (Clever Cloud)
- **Jinja2** - Motor de plantillas HTML

### Frontend
- **HTML** - Estructura de páginas
- **CSS** - Estilos y diseño responsivo

### Despliegue
- **Clever Cloud** - Hosting y base de datos
- **PostgreSQL Add-on** - Base de datos gestionada
- **Git** - Control de versiones
- **Render** - Hosting donde esta desplegada 

---

## Instalación y Configuración

### 1. Clonar el repositorio
```python 
git clone https://github.com/tuusuario/mi-tienda.git
cd mi-tienda
```
### 2. Crear entorno virtual
```python
python -m venv venv
venv/scripts/activate  #Para windows
source venv/bin/activate #Para Linux/Mac
```
### 3. Instalar dependencias
```python
pip install -r requirements.txt
```
### 4. Ejecutar la aplicación
```python
uvicorn app.main:app --reload 
```
---

### Estructura del proyecto
```bash
mi-tienda/
├── app/   # Aplicación principal
│ ├── pycache/   # Archivos caché de Python
│ └── models/   # Modelos de base de datos
│ ├── pycache/
│ ├── init.py   # Inicializador del módulo
│ ├── categoria.py   # Modelo de categorías
│ ├── producto.py   # Modelo de productos
│ ├── provedor.py   # Modelo de proveedores
│ └── usuario.py   # Modelo de usuarios
│
├── routers/   # Routers/Controladores de la API
│ ├── pycache/
│ ├── categorias.py   # Endpoints para categorías
│ ├── externos.py   # API externa (Open Food Facts)
│ ├── productos.py   # Endpoints para productos
│ ├── proveedores.py   # Endpoints para proveedores
│ └── usuarios.py   # Endpoints para usuarios
│
├── schemas/   # Esquemas Pydantic para validación
│ ├── pycache/
│ ├── categoria_schema.py   # Esquemas de categorías
│ ├── producto_schema.py   # Esquemas de productos
│ ├── provedor_schema.py   # Esquemas de proveedores
│ └── usuario_schema.py   # Esquemas de usuarios
│
├── static/   # Archivos estáticos (CSS, JS, imágenes)
│ └── css/
│ └── styles.css   # Estilos CSS principales
│
├── templates/   # Plantillas HTML/Jinja2
│ ├── index.html   # Página principal
│ ├── productos/   # Templates de productos
│ ├── usuarios/   # Templates de usuarios
│ ├── proveedores/   # Templates de proveedores
│ └── externos/   # Templates de API externa
│
│
├── .gitignore   # Archivos ignorados por Git
├── database.py   # Configuración y conexión a base de datos
├── main.py   # Punto de entrada de la aplicación FastAPI
├── requirements.txt   # Dependencias de Python
└── README.md   # Documentación del proyecto
```

---

## Despliegue en Clever Cloud
### 1. Crear cuenta en Clever Cloud
<clever-cloud.com> 

