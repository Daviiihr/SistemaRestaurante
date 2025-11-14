# IMenu.py
from typing import Protocol, List, Optional
from Ingrediente import Ingrediente
from Stock import Stock


class IMenu(Protocol):
    """debes rellenar la Interfaz para los elementos del menú."""

    nombre : str
    precio : float
    ingredientes : List[Ingrediente]
    icono_path : Optional[str]
    cantidad : int = 0

    def estaDisponible(self, stock: Stock) -> bool:
        """Verifica si el menú puede ser preparado con el stock disponible."""
        pass