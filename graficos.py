import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy import func
from database import get_session
from models import Pedido, menu_ingrediente, Menu, pedido_menu, Ingrediente

def generar_grafico_menus_mas_vendidos(frame_destino):
    db = next(get_session())
    
    # Consulta compleja para contar ventas por menú
    resultados = db.query(Menu.nombre, func.sum(pedido_menu.c.cantidad))\
        .join(pedido_menu)\
        .group_by(Menu.nombre)\
        .all()
    db.close()

    if not resultados:
        return False # No hay datos para graficar

    nombres = [r[0] for r in resultados]
    cantidades = [r[1] for r in resultados]

    # Crear Figura
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    ax.bar(nombres, cantidades, color='#4CAF50')
    ax.set_title('Menús más Vendidos')
    ax.set_ylabel('Cantidad')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Incrustar en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame_destino)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return True

def generar_grafico_ingredientes(frame_destino):
    db = next(get_session())
    # Filtramos ingredientes que tengan stock > 0 para que el gráfico no se vea feo
    ingredientes = db.query(Ingrediente).filter(Ingrediente.cantidad > 0).all()
    db.close()

    if not ingredientes:
        return False

    nombres = [i.nombre for i in ingredientes]
    cantidades = [i.cantidad for i in ingredientes]

    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    ax.pie(cantidades, labels=nombres, autopct='%1.1f%%', startangle=140)
    ax.set_title('Distribución de Stock Actual')
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame_destino)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return True