# menu_catalog.py
from typing import List
from ElementoMenu import CrearMenu
from Ingrediente import Ingrediente
from IMenu import IMenu

def get_default_menus() -> List[IMenu]:
    return [
        CrearMenu(
            "Papas Fritas",
            [ Ingrediente("Papas", "unid", 5)],
            precio=500,
            icono_path="IMG/icono_papas_fritas_64x64.png",
        ),
        CrearMenu(
            "Completo",
            [
            Ingrediente("Vienesa","unid", 1),
            Ingrediente("Pan de completo","unid", 1),
            Ingrediente("Palta","kg",0.5),
            Ingrediente("Tomate","kg",0.2),
            ],
            precio=1800,
            icono_path="IMG/icono_hotdog_sin_texto_64x64.png",
        ),
        CrearMenu(
            "Hamburguesa",
            [ 
            Ingrediente("Pan de hamburguesa", "unid", 1),
            Ingrediente("Lamina de queso", "unid", 1),
            Ingrediente("Churrasco de carne", "unid", 1),
            ],
            precio=3500,
            icono_path="IMG/icono_hamburguesa_negra_64x64.png",
        ),
        CrearMenu(
            "Chorrillana",
            [
            Ingrediente("papas", "unid", 1),
            Ingrediente("carne de vacuno", "unid", 1),
            Ingrediente("Huevos", "unid", 1),
            Ingrediente("cebolla", "unid", 1),
            ],
            precio=4500,
            icono_path="IMG/icono_chorrillana_64x64.png",
        ),
        CrearMenu(
            "Pepsi",
            [ Ingrediente("Pepsi", "unid", 1)],
            precio=1000,
            icono_path="IMG/icono_cola_64x64.png",
        ),
        CrearMenu(
            "Coca Cola",
            [ Ingrediente("Coca Cola", "unid", 1)],
            precio=1200,
            icono_path="IMG/icono_cola_lata_64x64.png",
        ),
        CrearMenu(
            "Empanada de queso",
            [ 
            Ingrediente("Masa de empanada", "unid", 1),
            Ingrediente("Queso", "unid", 1)
            ],
            precio=800,
            icono_path="IMG/icono_empanada_queso_64x64.png",
        ),
    ]