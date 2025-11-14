from Ingrediente import Ingrediente

class Stock:
    def __init__(self):
        self.lista_ingredientes = []

    def agregar_ingrediente(self, ingrediente):
        for existente in self.lista_ingredientes:
            if (
                existente.nombre.lower() == ingrediente.nombre.lower()
                and existente.unidad == ingrediente.unidad
            ):
                existente.cantidad += ingrediente.cantidad
                return existente

        self.lista_ingredientes.append(ingrediente)
        return ingrediente

    def eliminar_ingrediente(self, nombre_ingrediente, unidad=None):
        nombre_ingrediente = nombre_ingrediente.lower()
        unidad = unidad if unidad else None

        for index, ingrediente in enumerate(self.lista_ingredientes):
            if ingrediente.nombre.lower() != nombre_ingrediente:
                continue

            if unidad is not None and ingrediente.unidad != unidad:
                continue

            del self.lista_ingredientes[index]
            return True

        return False

    def verificar_stock(self):
        return [
            (ing.nombre, ing.unidad, ing.cantidad) for ing in self.lista_ingredientes
        ]

    def actualizar_stock(self, nombre_ingrediente, nueva_cantidad):
        for ingrediente in self.lista_ingredientes:
            if ingrediente.nombre.lower() == nombre_ingrediente.lower():
                ingrediente.cantidad = float(nueva_cantidad)
                return ingrediente
        raise ValueError(f"Ingrediente '{nombre_ingrediente}' no encontrado en stock")

    def obtener_elementos_menu(self):
        return self.lista_ingredientes[:]
