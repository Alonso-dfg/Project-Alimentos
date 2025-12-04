from fastapi import APIRouter, HTTPException, Depends, Query, Request, Form
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
from app.database import get_db
from app import models
from typing import Optional

# Rutas relacionadas con APIs o datos externos
router = APIRouter(prefix="/externos", tags=["Externos"])

# Carpeta donde están las plantillas HTML
templates = Jinja2Templates(directory="app/templates")


#                SECCIÓN DE PÁGINAS HTML


@router.get("/opciones", response_class=HTMLResponse)
async def opciones_externos(request: Request):
    """
    Página principal con las opciones relacionadas a productos externos.
    """
    return templates.TemplateResponse("externos/opciones.html", {"request": request})


@router.get("/buscar_form", response_class=HTMLResponse)
async def buscar_externo_form(request: Request):
    """
    Muestra un formulario donde el usuario escribe qué quiere buscar.
    """
    return templates.TemplateResponse("externos/buscar_externo.html", {"request": request})


@router.post("/buscar_form", response_class=HTMLResponse)
async def buscar_externo_post(
    request: Request,
    busqueda: str = Form(""),   # Palabra clave que escribe el usuario
    limite: int = Form(10),     # Cuántos resultados quiere ver
    db: Session = Depends(get_db)
):
    """
    Procesa el formulario de búsqueda y muestra los productos encontrados.
    """
    productos = obtener_productos_externos_api(busqueda, limite, db)

    return templates.TemplateResponse("externos/buscar_externo.html", {
        "request": request,
        "productos": productos.get("datos", []),
        "mensaje": productos.get("mensaje", ""),
        "busqueda": busqueda
    })


#                  RUTAS API (JSON) OPTIMIZADAS

@router.get("/productos_ext")
def obtener_productos_externos(
    busqueda: Optional[str] = Query(None),
    limite: int = Query(10),
    categoria: Optional[str] = Query(None),
    pais: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Consulta productos en la API de Open Food Facts con filtros opcionales.
    Permite buscar por nombre, categoría, país y limitar resultados.
    """

    # URL base de la API externa
    url = "https://world.openfoodfacts.org/cgi/search.pl"

    # Parámetros de búsqueda
    params = {
        "search_terms": busqueda or "",
        "json": 1,
        "page_size": limite,
        "action": "process"
    }

    # Filtros opcionales
    if categoria:
        params["tag_0"] = f"categories:{categoria}"
    if pais:
        params["tag_1"] = f"countries:{pais}"

    # Identificación de la app para la API
    headers = {
        "User-Agent": "ProyectoIntegradorFastAPI/1.0 (https://openai.com)"
    }

    try:
        # Llamado a la API externa
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        productos_procesados = []
        productos_guardados = 0

        # Recorremos cada producto devuelto por la API
        for p in data.get("products", []):

            # Nombre del producto válido
            nombre = p.get("product_name", p.get("product_name_es", "Desconocido"))
            if not nombre or nombre == "Desconocido":
                continue

            # Categoría principal (texto limpio)
            categorias = p.get("categories", "").split(",")
            categoria_principal = categorias[0].strip() if categorias else "Sin categoría"

            # País principal
            paises = p.get("countries", "").split(",")
            pais_principal = paises[0].strip() if paises else "Desconocido"

            # Imagen del producto
            imagen_url = p.get("image_url", p.get("image_small_url", ""))

            # Precio, si la API lo incluye
            precio = p.get("price", p.get("product_price", 0.0))
            if isinstance(precio, str):
                try:
                    precio = float(precio.replace(",", "."))
                except:
                    precio = 0.0

            # Verifica si ya existe en la base de datos
            existe = db.query(models.Producto).filter(
                models.Producto.nombre.ilike(f"%{nombre[:50]}%")
            ).first()

            # Si no existe, lo guarda
            if not existe:
                try:
                    nuevo_producto = models.Producto(
                        nombre=nombre[:100],
                        precio=precio,
                        ciudad=pais_principal[:50],
                        fuente="Open Food Facts",
                        imagen=imagen_url[:200],
                        categoria_externa=categoria_principal[:100],
                        estado="activo"
                    )
                    db.add(nuevo_producto)
                    productos_guardados += 1
                except Exception as e:
                    print(f"Error guardando producto {nombre}: {e}")
                    continue

            # Agregar a la lista de productos a mostrar
            productos_procesados.append({
                "id": len(productos_procesados) + 1,
                "nombre": nombre,
                "categoria": categoria_principal,
                "pais": pais_principal,
                "precio": precio,
                "imagen": imagen_url,
                "marca": p.get("brands", "Desconocido"),
                "url": p.get("url", "")
            })

        db.commit()

        return {
            "cantidad_total": data.get("count", 0),
            "cantidad_procesada": len(productos_procesados),
            "productos_guardados": productos_guardados,
            "datos": productos_procesados
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error al consultar API externa: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


#     FUNCIÓN AUXILIAR PARA USO INTERNO EN LAS PÁGINAS HTML


def obtener_productos_externos_api(busqueda: str = "", limite: int = 10, db: Session = None):
    """
    Versión simplificada para uso en las plantillas HTML.
    Devuelve solo datos necesarios para mostrarlos en la interfaz.
    """
    try:
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        response = requests.get(url, params={
            "search_terms": busqueda,
            "json": 1,
            "page_size": limite,
            "action": "process"
        }, timeout=10)

        data = response.json()
        productos = []

        for p in data.get("products", []):
            nombre = p.get("product_name", "Desconocido")
            if nombre == "Desconocido":
                continue

            productos.append({
                "nombre": nombre[:50],
                "categoria": p.get("categories", "Sin categoría").split(",")[0].strip(),
                "pais": p.get("countries", "Desconocido").split(",")[0].strip(),
                "precio": p.get("price", 0.0),
                "marca": p.get("brands", "Desconocido"),
                "imagen": p.get("image_small_url", "")
            })

        return {
            "mensaje": f"Se encontraron {len(productos)} productos",
            "datos": productos
        }

    except Exception as e:
        return {"mensaje": f"Error: {str(e)}", "datos": []}


#         CONSULTA DE PRODUCTOS POR CÓDIGO DE BARRAS


@router.get("/producto/{codigo_barras}")
def obtener_producto_por_codigo(codigo_barras: str):
    """
    Busca un producto específico utilizando su código de barras.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{codigo_barras}.json"

    try:
        response = requests.get(url, timeout=10)
        data = response.json().get("product", {})

        if not data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        return {
            "nombre": data.get("product_name", "Desconocido"),
            "marca": data.get("brands", "Desconocido"),
            "categorias": data.get("categories", ""),
            "ingredientes": data.get("ingredients_text", ""),
            "imagen": data.get("image_url", ""),
            "nutri_score": data.get("nutriscore_grade", "Desconocido"),
            "url": data.get("url", "")
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error al consultar: {str(e)}")
