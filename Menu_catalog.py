class MenuDTO:
    def __init__(self, nombre, precio, ingredientes_dict, imagen_path=None):
        self.nombre = nombre
        self.precio = precio
        self.ingredientes = ingredientes_dict
        self.imagen_path = imagen_path

def get_default_menus():
    return [
        # MODIFICADO
        MenuDTO("Papas Fritas", 2000, {"Papas": 5}, "IMG/icono_papas_fritas_64x64.png"),
        
        # MODIFICADO
        MenuDTO("Completo", 1800, {"Vienesa": 1, "Pan de completo": 1, "Palta": 0.2, "Tomate": 0.2}, "IMG/icono_hotdog_sin_texto_64x64.png"),
        
        # MODIFICADO
        MenuDTO("Hamburguesa", 3500, {"Pan de hamburguesa": 1, "Carne": 1, "Queso": 1}, "IMG/icono_hamburguesa_negra_64x64.png"),
        
        # MODIFICADO
        MenuDTO("Chorrillana", 4500, {"Papas": 5, "Carne": 1, "Huevos": 2, "Cebolla": 1}, "IMG/icono_chorrillana_64x64.png"),
        
        # MODIFICADO
        MenuDTO("Bebida", 1000, {"Pepsi": 1}, "IMG/icono_cola_lata_64x64.png"),
        
        # ESTE FUNCIONABA BIEN
        MenuDTO("Coca Cola", 1200, {"Coca cola": 1}, "IMG/icono_cola_64x64.png"),
        
        # MODIFICADO
        MenuDTO("Empanada", 1500, {"Queso": 1, "Masa de empanada": 1}, "IMG/icono_empanada_queso_64x64.png"),
    ]