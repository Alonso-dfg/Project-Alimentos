from fastapi import APIRouter, HTTPException, Depends, Query, Request, Form
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
from app.database import get_db
from app import models
from typing import Optional

router = APIRouter(prefix="/externos", tags=["Externos"])
templates = Jinja2Templates(directory="app/templates")

# ========== RUTAS HTML ==========

@router.get("/opciones", response_class=HTMLResponse)
async def opciones_externos(request: Request):
    return templates.TemplateResponse("externos/opciones.html", {"request": request})

@router.get("/buscar_form", response_class=HTMLResponse)
async def buscar_externo_form(request: Request):
    return templates.TemplateResponse("externos/buscar_externo.html", {"request": request})

@router.post("/buscar_form", response_class=HTMLResponse)
async def buscar_externo_post(
    request: Request,
    busqueda: str = Form(""),  # Término de búsqueda
    limite: int = Form(10),    # Límite de resultados
    db: Session = Depends(get_db)
):
    productos = obtener_productos_externos_api(busqueda, limite, db)
    
    return templates.TemplateResponse("externos/buscar_externo.html", {
        "request": request,
        "productos": productos.get("datos", []),
        "mensaje": productos.get("mensaje", ""),
        "busqueda": busqueda
    })

# ========== RUTAS API MEJORADAS ==========

@router.get("/productos_ext")
def obtener_productos_externos(
    busqueda: Optional[str] = Query(None, description="Término de búsqueda"),
    limite: int = Query(10, description="Número máximo de resultados"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    pais: Optional[str] = Query(None, description="Filtrar por país"),
    db: Session = Depends(get_db)
):
    """
    Consulta productos desde Open Food Facts.
    Parámetros:
    - busqueda: Término para buscar (ej: "chocolate")
    - limite: Número máximo de resultados (default: 10)
    - categoria: Filtrar por categoría (ej: "snacks")
    - pais: Filtrar por país (ej: "france")
    """
    
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": busqueda if busqueda else "",
        "json": 1,
        "page_size": limite,
        "action": "process"
    }
    
    # Agregar filtros si existen
    if categoria:
        params["tag_0"] = f"categories:{categoria}"
    if pais:
        params["tag_1"] = f"countries:{pais}"

    headers = {
        "User-Agent": "ProyectoIntegradorFastAPI/1.0 (https://openai.com)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        productos_procesados = []
        productos_guardados = 0
        
        for p in data.get("products", []):
            # Extraer datos con validaciones
            nombre = p.get("product_name", p.get("product_name_es", "Desconocido"))
            if nombre == "Desconocido" or not nombre:
                continue  # Saltar productos sin nombre
            
            # Extraer categorías
            categorias = p.get("categories", "").split(",") if p.get("categories") else []
            categoria_principal = categorias[0].strip() if categorias else "Sin categoría"
            
            # Extraer país
            paises = p.get("countries", "").split(",") if p.get("countries") else []
            pais_principal = paises[0].strip() if paises else "Desconocido"
            
            # Extraer imagen
            imagen_url = p.get("image_url", p.get("image_small_url", ""))
            
            # Extraer precio
            precio = p.get("price", p.get("product_price", 0.0))
            if precio and isinstance(precio, str):
                try:
                    precio = float(precio.replace(",", "."))
                except:
                    precio = 0.0
            
            # Verificar si el producto ya existe
            existe = db.query(models.Producto).filter(
                models.Producto.nombre.ilike(f"%{nombre[:50]}%")
            ).first()
            
            # Guardar en BD si no existe
            if not existe:
                try:
                    nuevo_producto = models.Producto(
                        nombre=nombre[:100],  # Limitar longitud
                        precio=precio,
                        ciudad=pais_principal[:50],
                        fuente="Open Food Facts",
                        imagen=imagen_url[:200] if imagen_url else None,
                        categoria_externa=categoria_principal[:100],
                        estado="activo"
                    )
                    db.add(nuevo_producto)
                    productos_guardados += 1
                except Exception as e:
                    print(f"Error guardando producto {nombre}: {e}")
                    continue

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

# Función auxiliar para HTML
def obtener_productos_externos_api(busqueda: str = "", limite: int = 10, db: Session = None):
    """Versión simplificada para HTML"""
    try:
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": busqueda,
            "json": 1,
            "page_size": limite,
            "action": "process"
        }
        
        headers = {"User-Agent": "ProyectoIntegradorFastAPI/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        productos = []
        for p in data.get("products", []):
            nombre = p.get("product_name", p.get("product_name_es", "Desconocido"))
            if nombre == "Desconocido":
                continue
                
            productos.append({
                "nombre": nombre[:50],
                "categoria": p.get("categories", "Sin categoría").split(",")[0].strip()[:50],
                "pais": p.get("countries", "Desconocido").split(",")[0].strip()[:50],
                "precio": p.get("price", 0.0),
                "marca": p.get("brands", "Desconocido")[:50],
                "imagen": p.get("image_small_url", "")
            })
        
        return {
            "mensaje": f"Se encontraron {len(productos)} productos",
            "datos": productos
        }
        
    except Exception as e:
        return {"mensaje": f"Error: {str(e)}", "datos": []}

# Nueva ruta: Buscar productos por código de barras
@router.get("/producto/{codigo_barras}")
def obtener_producto_por_codigo(codigo_barras: str):
    """
    Obtiene un producto específico por código de barras desde Open Food Facts
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{codigo_barras}.json"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
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