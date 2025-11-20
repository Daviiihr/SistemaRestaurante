from sqlalchemy.orm import Session
from models import Pedido, Cliente, Menu

class PedidoCRUD:
    @staticmethod
    def crear_pedido(db: Session, cliente_email: str, descripcion: str):
        cliente = db.query(Cliente).filter_by(email=cliente_email).first()
        
        if not cliente:
            print(f"Error: No existe cliente con email {cliente_email}")
            return None

        nuevo_pedido = Pedido(descripcion=descripcion, cliente_email=cliente_email)
        db.add(nuevo_pedido)
        try:
            db.commit()
            db.refresh(nuevo_pedido)
            return nuevo_pedido
        except Exception as e:
            db.rollback()
            print(f"Error al crear pedido: {e}")
            return None

    @staticmethod
    def leer_pedidos(db: Session):
        return db.query(Pedido).order_by(Pedido.fecha.desc()).all()
        
    @staticmethod
    def agregar_menu_a_pedido(db: Session, pedido_id: int, menu_nombre: str, cantidad: int):
        pedido = db.query(Pedido).get(pedido_id)
        menu = db.query(Menu).filter_by(nombre=menu_nombre).first()
        
        if pedido and menu:
            pedido.items_menu.append(menu) 
            pedido.total += (menu.precio * cantidad)
            db.commit()
            return True
        return False