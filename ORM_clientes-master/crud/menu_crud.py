from sqlalchemy.orm import Session
from models import Menu, Ingrediente, menu_ingrediente

class MenuCRUD:
    @staticmethod
    def crear_menu(db: Session, nombre: str, precio: int):
        nuevo = Menu(nombre=nombre, precio=precio)
        db.add(nuevo)
        db.commit()
        return nuevo

    @staticmethod
    def verificar_disponibilidad(db: Session, menu_id: int):
        menu = db.query(Menu).get(menu_id)
        if not menu: return False
        return True