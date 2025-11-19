import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import pandas as pd
import os
from datetime import datetime
from functools import reduce

# IMPORTACIONES BASE DE DATOS
from database import get_session, engine, Base
from models import Menu, Ingrediente, Pedido, Cliente, menu_ingrediente, pedido_menu
from sqlalchemy import insert 
from crud.ingrediente_crud import IngredienteCRUD
from crud.cliente_crud import ClienteCRUD
from crud.pedido_crud import PedidoCRUD
from crud.menu_crud import MenuCRUD

# UTILIDADES
from BoletaFacade import BoletaFacade
from ctk_pdf_viewer import CTkPDFViewer
from Menu_catalog import get_default_menus
from CTkMessagebox import CTkMessagebox
import graficos

Base.metadata.create_all(bind=engine)

class MenuTemp:
    def __init__(self, nombre, precio, cantidad=1):
        self.nombre = nombre; self.precio = precio; self.cantidad = cantidad

class PedidoAdapter:
    def __init__(self, items_carrito): self.menus = items_carrito
    def calcular_total(self): return sum(m.precio * m.cantidad for m in self.menus)

class Aplicacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Restaurante Final - Ev3")
        self.geometry("1200x800")
        ctk.set_appearance_mode("Dark")
        
        self.carrito = []
        
        # CONFIGURACIÓN TABS
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.tab_cli = self.tabview.add("Clientes")
        self.tab_inv = self.tabview.add("Inventario")
        self.tab_men = self.tabview.add("Gestión Menús")
        self.tab_ped = self.tabview.add("Realizar Pedido")
        self.tab_his = self.tabview.add("Historial")
        self.tab_est = self.tabview.add("Estadísticas")
        self.tab_bol = self.tabview.add("Boleta")
        
        self._init_db_semilla()
        self._setup_clientes()
        self._setup_inventario()
        self._setup_gestion_menus()
        self._setup_pedido()
        self._setup_historial()
        self._setup_estadisticas()
        self._setup_visor()
        self.actualizar_combos()

    def _init_db_semilla(self):
        db = next(get_session())
        if db.query(Menu).count() == 0:
            print("Cargando catálogo inicial...")
            for m in get_default_menus():
                MenuCRUD.crear_menu(db, m.nombre, m.precio, m.imagen_path)
        db.close()


    # 1. GESTIÓN CLIENTES

    def _setup_clientes(self):
        frame = ctk.CTkFrame(self.tab_cli)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        frm_in = ctk.CTkFrame(frame)
        frm_in.pack(fill="x", pady=5)
        
        self.cli_nom = ctk.CTkEntry(frm_in, placeholder_text="Nombre")
        self.cli_nom.pack(side="left", padx=5)
        self.cli_mail = ctk.CTkEntry(frm_in, placeholder_text="Email")
        self.cli_mail.pack(side="left", padx=5)
        self.cli_edad = ctk.CTkEntry(frm_in, placeholder_text="Edad", width=60)
        self.cli_edad.pack(side="left", padx=5)
        
        ctk.CTkButton(frm_in, text="Guardar", command=self.guardar_cliente).pack(side="left", padx=5)
        
        self.tree_cli = ttk.Treeview(frame, columns=("Email", "Nombre", "Edad"), show="headings")
        self.tree_cli.heading("Email", text="Email"); self.tree_cli.heading("Nombre", text="Nombre")
        self.tree_cli.pack(fill="both", expand=True, pady=10)
        self.cargar_clientes()

    def guardar_cliente(self):
        try: edad = int(self.cli_edad.get())
        except: CTkMessagebox(title="Error", message="Edad debe ser número", icon="cancel"); return
        
        db = next(get_session())
        if ClienteCRUD.crear_cliente(db, self.cli_nom.get(), self.cli_mail.get(), edad):
            self.cargar_clientes()
            self.actualizar_combos()
        else:
            CTkMessagebox(title="Error", message="Error al guardar (¿Email duplicado?)", icon="cancel")
        db.close()

    def cargar_clientes(self):
        for i in self.tree_cli.get_children(): self.tree_cli.delete(i)
        db = next(get_session())
        for c in ClienteCRUD.leer_clientes(db):
            self.tree_cli.insert("", "end", values=(c.email, c.nombre, c.edad))
        db.close()


    # 2. INVENTARIO Y CARGA

    def _setup_inventario(self):
        frame = ctk.CTkFrame(self.tab_inv)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Carga CSV Integrada
        ctk.CTkButton(frame, text="Importar CSV Masivo", command=self.importar_csv, fg_color="#00796B").pack(pady=5)
        
        # Agregar Manual
        frm_in = ctk.CTkFrame(frame)
        frm_in.pack(fill="x", pady=5)
        self.inv_nom = ctk.CTkEntry(frm_in, placeholder_text="Ingrediente")
        self.inv_nom.pack(side="left", padx=5)
        self.inv_uni = ctk.CTkComboBox(frm_in, values=["kg", "unid", "lt"], width=80)
        self.inv_uni.pack(side="left", padx=5)
        self.inv_cant = ctk.CTkEntry(frm_in, placeholder_text="Cant", width=80)
        self.inv_cant.pack(side="left", padx=5)
        ctk.CTkButton(frm_in, text="Agregar", command=self.agregar_stock).pack(side="left", padx=5)
        
        self.tree_inv = ttk.Treeview(frame, columns=("ID", "Nombre", "Stock"), show="headings")
        self.tree_inv.heading("ID", text="ID"); self.tree_inv.heading("Nombre", text="Nombre"); self.tree_inv.heading("Stock", text="Stock")
        self.tree_inv.pack(fill="both", expand=True)
        self.cargar_inventario()

    def importar_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path: return
        try:
            df = pd.read_csv(path)
            db = next(get_session())
            # Procesar datos antes de insertar
            datos_limpios = list(map(lambda x: (str(x[0]), str(x[1]), float(x[2])), df[['nombre', 'unidad', 'cantidad']].values))
            
            for nom, uni, cant in datos_limpios:
                IngredienteCRUD.crear_ingrediente(db, nom, uni, cant)
            db.close()
            self.cargar_inventario()
            CTkMessagebox(title="Éxito", message="CSV Cargado", icon="check")
        except Exception as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")

    def agregar_stock(self):
        try: cant = float(self.inv_cant.get())
        except: return
        db = next(get_session())
        if not IngredienteCRUD.crear_ingrediente(db, self.inv_nom.get(), self.inv_uni.get(), cant):
            IngredienteCRUD.actualizar_stock(db, self.inv_nom.get(), cant)
        db.close()
        self.cargar_inventario()

    def cargar_inventario(self):
        for i in self.tree_inv.get_children(): self.tree_inv.delete(i)
        db = next(get_session())
        for ing in IngredienteCRUD.obtener_todos(db):
            self.tree_inv.insert("", "end", values=(ing.id, ing.nombre, ing.cantidad))
        db.close()


    # 3. GESTIÓN MENÚS

    def _setup_gestion_menus(self):
        """Pestaña para crear recetas nuevas desde la GUI"""
        frame = ctk.CTkFrame(self.tab_men)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Datos del Menú
        frm_data = ctk.CTkFrame(frame)
        frm_data.pack(fill="x", pady=5)
        self.new_menu_nom = ctk.CTkEntry(frm_data, placeholder_text="Nombre Nuevo Plato")
        self.new_menu_nom.pack(side="left", fill="x", expand=True, padx=5)
        self.new_menu_pre = ctk.CTkEntry(frm_data, placeholder_text="Precio", width=100)
        self.new_menu_pre.pack(side="left", padx=5)
        
        # Selección de Ingredientes
        frm_ing = ctk.CTkFrame(frame)
        frm_ing.pack(fill="x", pady=5)
        ctk.CTkLabel(frm_ing, text="Ingrediente:").pack(side="left", padx=5)
        self.combo_ing_recipe = ctk.CTkComboBox(frm_ing, values=[])
        self.combo_ing_recipe.pack(side="left", padx=5)
        self.entry_cant_recipe = ctk.CTkEntry(frm_ing, placeholder_text="Cant", width=60)
        self.entry_cant_recipe.pack(side="left", padx=5)
        ctk.CTkButton(frm_ing, text="Añadir a Receta", command=self.add_ing_to_recipe).pack(side="left", padx=5)
        
        # Lista temporal de receta
        self.recipe_list = [] 
        self.tree_recipe = ttk.Treeview(frame, columns=("Ingrediente", "Cantidad"), show="headings", height=8)
        self.tree_recipe.heading("Ingrediente", text="Ingrediente")
        self.tree_recipe.heading("Cantidad", text="Cantidad")
        self.tree_recipe.pack(fill="x", padx=10)
        
        ctk.CTkButton(frame, text="GUARDAR MENÚ NUEVO", fg_color="green", command=self.guardar_nuevo_menu).pack(pady=10)

    def add_ing_to_recipe(self):
        nom = self.combo_ing_recipe.get()
        try: cant = float(self.entry_cant_recipe.get())
        except: return
        if not nom: return
        
        self.recipe_list.append({"nombre": nom, "cantidad": cant})
        self.tree_recipe.insert("", "end", values=(nom, cant))

    def guardar_nuevo_menu(self):
        nom = self.new_menu_nom.get()
        try: precio = float(self.new_menu_pre.get())
        except: CTkMessagebox(title="Error", message="Precio inválido", icon="cancel"); return
        
        if not self.recipe_list:
            CTkMessagebox(title="Error", message="Agrega ingredientes a la receta", icon="cancel"); return

        db = next(get_session())
        # 1. Crear Menu
        nuevo = MenuCRUD.crear_menu(db, nom, precio)
        # 2. Asociar Ingredientes
        # Usar Ingredientes Existentes
        for item in self.recipe_list:
            ing_db = db.query(Ingrediente).filter_by(nombre=item['nombre']).first()
            if ing_db:
                stmt = insert(menu_ingrediente).values(
                    menu_id=nuevo.id,
                    ingrediente_id=ing_db.id,
                    cantidad_necesaria=item['cantidad']
                )
                db.execute(stmt)
        db.commit()
        db.close()
        
        CTkMessagebox(title="Éxito", message="Menú Creado Exitosamente", icon="check")
        self.recipe_list = []
        for i in self.tree_recipe.get_children(): self.tree_recipe.delete(i)
        self.refrescar_menus_disponibles() # Para que aparezca en ventas


    # 4. REALIZAR PEDIDO

    def _setup_pedido(self):
        frm_cli = ctk.CTkFrame(self.tab_ped)
        frm_cli.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frm_cli, text="Cliente:").pack(side="left")
        self.combo_cli_ped = ctk.CTkComboBox(frm_cli, values=[])
        self.combo_cli_ped.pack(side="left", padx=5)
        
        self.scroll_menus = ctk.CTkScrollableFrame(self.tab_ped, height=280, orientation="horizontal", label_text="Catálogo")
        self.scroll_menus.pack(fill="x", padx=10)
        ctk.CTkButton(self.tab_ped, text="Actualizar Disponibilidad", command=self.refrescar_menus_disponibles).pack(pady=5)
        
        self.tree_cart = ttk.Treeview(self.tab_ped, columns=("Item", "Cant", "Subtotal"), show="headings", height=6)
        self.tree_cart.heading("Item", text="Item"); self.tree_cart.heading("Cant", text="Cant"); self.tree_cart.heading("Subtotal", text="Subtotal")
        self.tree_cart.pack(fill="x", padx=10)
        
        self.lbl_total = ctk.CTkLabel(self.tab_ped, text="Total: $0", font=("Arial", 16, "bold"))
        self.lbl_total.pack()
        
        ctk.CTkButton(self.tab_ped, text="FINALIZAR COMPRA", fg_color="green", command=self.finalizar_compra).pack(pady=10)
        
        self.refrescar_menus_disponibles()

    def refrescar_menus_disponibles(self):
        for w in self.scroll_menus.winfo_children(): w.destroy()
        db = next(get_session())
        menus_bd = db.query(Menu).all()
        stock_bd = {i.nombre.lower().strip(): i.cantidad for i in IngredienteCRUD.obtener_todos(db)}
        
        # Obtener recetas
        # Por simplicidad, cargamos la receta desde BD
        for menu in menus_bd:
            disponible = True
            btn_txt = "Agregar"
            
            receta = {}
            if menu.ingredientes:
                pass 
            
            # Fallback al catalogo default para items base
            menus_default = {m.nombre: m.ingredientes for m in get_default_menus()}
            receta = menus_default.get(menu.nombre, {})

            # SI ES UN MENU NUEVO (No esta en default), hay que sacarlo de BD
            if not receta and menu.ingredientes:
                 # Consulta manual rapida a tabla intermedia
                 stmt = db.query(menu_ingrediente).filter_by(menu_id=menu.id).all()
                 for row in stmt:
                     # obtener nombre ingrediente
                     ing_obj = db.query(Ingrediente).get(row.ingrediente_id)
                     receta[ing_obj.nombre] = row.cantidad_necesaria

            # REDUCE para calcular consumo actual del carrito
            consumo_actual = {}
            for item in self.carrito:
                receta_item = menus_default.get(item.nombre, {})
                if not receta_item and item.nombre not in menus_default: 
                     # Buscar receta de menu nuevo en BD para el carrito
                     m_db = db.query(Menu).filter_by(nombre=item.nombre).first()
                     if m_db:
                        stmt = db.query(menu_ingrediente).filter_by(menu_id=m_db.id).all()
                        receta_item = {}
                        for row in stmt:
                            i_obj = db.query(Ingrediente).get(row.ingrediente_id)
                            receta_item[i_obj.nombre] = row.cantidad_necesaria

                for i_nom, i_cant in receta_item.items():
                    consumo_actual[i_nom.lower()] = consumo_actual.get(i_nom.lower(), 0) + (i_cant * item.cantidad)


            # Validar Stock
            if not receta: disponible = False
            
            for r_nom, r_cant in receta.items():
                stock_real = stock_bd.get(r_nom.lower().strip(), 0) - consumo_actual.get(r_nom.lower().strip(), 0)
                if stock_real < r_cant:
                    disponible = False; btn_txt = "Sin Stock"; break

            color = "#2E7D32" if disponible else "#C62828"
            state = "normal" if disponible else "disabled"
            
            c = ctk.CTkFrame(self.scroll_menus, width=130, height=160, fg_color=color)
            c.pack(side="left", padx=5)
            if menu.imagen_path and os.path.exists(menu.imagen_path):
                try:
                    img = ctk.CTkImage(Image.open(menu.imagen_path), size=(60,60))
                    ctk.CTkLabel(c, image=img, text="").pack(pady=2)
                except: pass
            
            ctk.CTkLabel(c, text=menu.nombre, font=("Arial",11,"bold")).pack()
            ctk.CTkLabel(c, text=f"${menu.precio:.0f}").pack()
            ctk.CTkButton(c, text=btn_txt, state=state, width=70, fg_color="white", text_color="black",
                          command=lambda m=menu: self.add_cart(m)).pack(pady=5)
        db.close()

    def add_cart(self, menu):
        found = False
        for item in self.carrito:
            if item.nombre == menu.nombre:
                item.cantidad += 1; found = True; break
        if not found: self.carrito.append(MenuTemp(menu.nombre, menu.precio))
        
        self.render_cart()
        self.refrescar_menus_disponibles()

    def render_cart(self):
        for i in self.tree_cart.get_children(): self.tree_cart.delete(i)
        
        # REDUCE (Calcular Total)
        total = reduce(lambda acc, x: acc + (x.precio * x.cantidad), self.carrito, 0)
        
        for item in self.carrito:
            self.tree_cart.insert("", "end", values=(item.nombre, item.cantidad, f"${item.precio*item.cantidad:.0f}"))
        
        self.lbl_total.configure(text=f"Total: ${total:.0f}")

    def finalizar_compra(self):
        if not self.carrito: return
        email = self.combo_cli_ped.get()
        if not email: return
        
        db = next(get_session())
        pedido = PedidoCRUD.crear_pedido(db, email, "Venta App")
        
        # Descontar Stock
        menus_default = {m.nombre: m.ingredientes for m in get_default_menus()}
        
        total_final = 0
        for item in self.carrito:
            total_final += (item.precio * item.cantidad)
            
            # Guardar relacion Pedido-Menu
            m_db = db.query(Menu).filter_by(nombre=item.nombre).first()
            if m_db:
                stmt = insert(pedido_menu).values(pedido_id=pedido.id, menu_id=m_db.id, cantidad=item.cantidad)
                db.execute(stmt)
            
            # Descontar ingredientes
            receta = menus_default.get(item.nombre, {})
            # Si es custom, buscar en BD
            if not receta and m_db:
                 stmt_ing = db.query(menu_ingrediente).filter_by(menu_id=m_db.id).all()
                 for row in stmt_ing:
                     i_obj = db.query(Ingrediente).get(row.ingrediente_id)
                     receta[i_obj.nombre] = row.cantidad_necesaria

            for r_nom, r_cant in receta.items():
                IngredienteCRUD.actualizar_stock(db, r_nom, -(r_cant * item.cantidad))
        
        pedido.total = total_final
        db.commit()
        db.close()
        
        # Generar PDF
        try:
            path = BoletaFacade(PedidoAdapter(self.carrito)).generar_boleta()
            self.mostrar_pdf(path)
            self.carrito = []
            self.render_cart()
            self.refrescar_menus_disponibles()
            self.cargar_historial()
            CTkMessagebox(title="Exito", message="Compra realizada", icon="check")
        except Exception as e: print(e)


    # 5. HISTORIAL (FILTRAR POR CLIENTE)

    def _setup_historial(self):
        frm = ctk.CTkFrame(self.tab_his)
        frm.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frm, text="Filtrar por Cliente:").pack(side="left")
        self.combo_filtro_his = ctk.CTkComboBox(frm, values=["Todos"])
        self.combo_filtro_his.pack(side="left", padx=5)
        ctk.CTkButton(frm, text="Filtrar", command=self.cargar_historial).pack(side="left")
        
        self.tree_his = ttk.Treeview(self.tab_his, columns=("ID", "Fecha", "Cliente", "Total"), show="headings")
        self.tree_his.heading("ID", text="ID"); self.tree_his.heading("Fecha", text="Fecha")
        self.tree_his.heading("Cliente", text="Cliente"); self.tree_his.heading("Total", text="Total")
        self.tree_his.pack(fill="both", expand=True, padx=10)

    def cargar_historial(self):
        for i in self.tree_his.get_children(): self.tree_his.delete(i)
        filtro = self.combo_filtro_his.get()
        
        db = next(get_session())
        pedidos = PedidoCRUD.leer_pedidos(db)
        
        # FILTER
        if filtro != "Todos":
            pedidos = list(filter(lambda p: p.cliente_email == filtro, pedidos))
            
        for p in pedidos:
            self.tree_his.insert("", "end", values=(p.id, p.fecha.strftime("%Y-%m-%d %H:%M"), p.cliente_email, f"${p.total}"))
        db.close()


    # 6. ESTADÍSTICAS

    def _setup_estadisticas(self):
        ctk.CTkLabel(self.tab_est, text="Análisis de Ventas e Inventario", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.frame_graficos = ctk.CTkScrollableFrame(self.tab_est)
        self.frame_graficos.pack(fill="both", expand=True)
        
        ctk.CTkButton(self.tab_est, text="Generar Gráficos", command=self.mostrar_graficos).pack(pady=10)

    def mostrar_graficos(self):
        for w in self.frame_graficos.winfo_children(): w.destroy()
        
        # Frame Izq (Ventas)
        f1 = ctk.CTkFrame(self.frame_graficos)
        f1.pack(side="left", fill="both", expand=True, padx=5)
        if not graficos.generar_grafico_menus_mas_vendidos(f1):
            ctk.CTkLabel(f1, text="No hay datos de ventas").pack()
            
        # Frame Der (Stock)
        f2 = ctk.CTkFrame(self.frame_graficos)
        f2.pack(side="right", fill="both", expand=True, padx=5)
        if not graficos.generar_grafico_ingredientes(f2):
            ctk.CTkLabel(f2, text="No hay stock").pack()


    # COMPONENTES COMUNES

    def _setup_visor(self):
        self.pdf_frame = ctk.CTkFrame(self.tab_bol); self.pdf_frame.pack(fill="both", expand=True)
        self.visor = None
    
    def mostrar_pdf(self, path):
        self.tabview.set("Boleta")
        if self.visor: self.visor.destroy()
        self.visor = CTkPDFViewer(self.pdf_frame, file=os.path.abspath(path))
        self.visor.pack(fill="both", expand=True)

    def actualizar_combos(self):
        db = next(get_session())
        
        emails = list(map(lambda c: c.email, ClienteCRUD.leer_clientes(db)))
        
        self.combo_cli_ped.configure(values=emails)
        self.combo_filtro_his.configure(values=["Todos"] + emails)
        
        # Llenar combo ingredientes para recetas nuevas
        ings = list(map(lambda i: i.nombre, IngredienteCRUD.obtener_todos(db)))
        self.combo_ing_recipe.configure(values=ings)
        
        db.close()

if __name__ == "__main__":
    Aplicacion().mainloop()