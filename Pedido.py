from ElementoMenu import CrearMenu 
class Pedido:
    def __init__(self):
        self.menus = []  

    def agregar_menu(self, menu: CrearMenu):
        # Busca si el menú ya está en el pedido para actualizar la cantidad
        for item in self.menus:
            if item.nombre == menu.nombre:
                item.cantidad += 1
                return
        # Esta en 1 porque es la primera vez que se agrega
        menu.cantidad = 1
        self.menus.append(menu)

    def eliminar_menu(self, nombre_menu: str):
        for index, item in enumerate(self.menus):
            if item.nombre == nombre_menu:
                return self.menus.pop(index)
        return None

    def mostrar_pedido(self):
        if not self.menus:

            return "El pedido está vacío."
        detallePedido = "Detalle del Pedido:\n"
        for item in self.menus:

            detallePedido += f"{item.nombre} x{item.cantidad}\n"
        return detallePedido        

    def calcular_total(self) -> float:
        return sum(menu.precio * menu.cantidad for menu in self.menus)
