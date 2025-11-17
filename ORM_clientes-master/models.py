from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

menu_ingrediente = Table(
    'menu_ingrediente',
    Base.metadata,
    Column('menu_id', Integer, ForeignKey('menus.id')),
    Column('ingrediente_id', Integer, ForeignKey('ingredientes.id')),
    Column('cantidad_neesaria', Float)
)

pedido_menu = Table(
    'pedido_menu',
    Base.metadata,
    Column('pedido_id', Integer, ForeignKey('pedidos.id')),
    Column('menu_id', Integer, ForeignKey('menus.id')),
    Column('cantidad', Integer)
)


class Cliente(Base):
    __tablename__ = 'clientes'

    email = Column(String, primaty_key=True)
    nombre = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)

pedidos = relationship('Pedido', back_populates='cliente', cascade='all, delete-orphan')


class Ingrediente(Base):
    __tablename__ = 'ingredientes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=True)
    unidad = Column(String, nullable=False)
    cantidad = Column(Float, default=0.0)


class Menu(Base):
    __tablename__ = 'menus'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)
    precio = Column(Float, nullable=False)
    ingredientes = relationship('Ingrediente', secondary=menu_ingrediente, backref='menus')


class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String, nullable=True)
    fecha = Column(DateTime(timezone=True, server_default=func.now()))
    total = Column(Integer, default=0)


# FK usando email
cliente_email = Column(String, ForeignKey('clientes.email', onupdate='CASCADE'), nullable=False)
cliente = relationship('Menu', secondary=pedido_menu, backref='pedidos')

items_menu = relationship('Menu', secondary=pedido_menu, backref='pedidos')