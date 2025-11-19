from sqlalchemy.orm import Session
from models import Ingrediente

class IngredienteCRUD:
    @staticmethod
    def crear_ingrediente(db: Session, nombre: str, unidad: str, cantidad: float):
        if cantidad < 0:
            print("Error: La cantidad no puede ser negativa.")
            return None

        if db.query(Ingrediente).filter_by(nombre=nombre).first():
            print(f"El ingrediente '{nombre}' ya existe.")
            return None

        nuevo = Ingrediente(nombre=nombre, unidad=unidad, cantidad=cantidad)
        db.add(nuevo)
        try:
            db.commit()
            db.refresh(nuevo)
            return nuevo
        except Exception as e:
            db.rollback()
            print(f"Error BD: {e}")
            return None

    @staticmethod
    def obtener_todos(db: Session):
        return db.query(Ingrediente).all()

    @staticmethod
    def actualizar_stock(db: Session, nombre: str, cantidad_agregar: float):
        ingrediente = db.query(Ingrediente).filter_by(nombre=nombre).first()
        if ingrediente:
            nueva_cantidad = ingrediente.cantidad + cantidad_agregar
            if nueva_cantidad < 0:
                print("Error: Stock resultante no puede ser negativo.")
                return None
            ingrediente.cantidad = nueva_cantidad
            db.commit()
            db.refresh(ingrediente)
            return ingrediente
        return None

    @staticmethod
    def eliminar_ingrediente(db: Session, nombre: str):
        ing = db.query(Ingrediente).filter_by(nombre=nombre).first()
        if ing:
            db.delete(ing)
            db.commit()
            return True
        return False