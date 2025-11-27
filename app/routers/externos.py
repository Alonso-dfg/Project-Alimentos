from fastapi import APIRouter, HTTPException, Depends
import requests
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(prefix="/externos", tags=["Externos"])

@router.get("/productos_ext")
def obtener_productos_externos(limit: int = 10, db: Session = Depends(get_db)):
    
    #Consulta productos desde la API pública de Open Food Facts
    #y los guarda en la base de datos local si no existen.
    
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit
    }

    headers = {
        "User-Agent": "ProyectoIntegradorFastAPI/1.0 (https://openai.com)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        productos = []
        for p in data.get("products", []):
            nombre = p.get("product_name", "Desconocido")
            categoria = p.get("categories", "Sin categoría")
            ciudad = (
                p.get("countries_tags", ["desconocido"])[0].replace("en:", "").capitalize()
                if p.get("countries_tags")
                else "Desconocido"
            )
            fuente = "Open Food Facts"
            precio = p.get("price", 0.0)

            # Verificar si el producto ya existe en la BD
            existe = db.query(models.Producto).filter_by(nombre=nombre).first()
            if not existe and nombre != "Desconocido":
                nuevo_producto = models.Producto(
                    nombre=nombre,
                    ciudad=ciudad,
                    fuente=fuente,
                    precio=precio
                )
                db.add(nuevo_producto)
                db.commit()
                db.refresh(nuevo_producto)

            productos.append({
                "nombre": nombre,
                "categoria": categoria,
                "ciudad": ciudad,
                "fuente": fuente,
                "precio": precio
            })

        return {
            "cantidad": len(productos),
            "mensaje": "Datos externos obtenidos y almacenados correctamente",
            "datos": productos
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error al consultar API externa: {e}")
