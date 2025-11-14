from fpdf import FPDF
from datetime import datetime

class BoletaFacade:
    def __init__(self, pedido):
        self.pedido = pedido
        self.subtotal = self.pedido.calcular_total()
        self.iva = self.subtotal * 0.19
        self.total = self.subtotal + self.iva

    def crear_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Boleta Restaurante", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(80, 10, "Menu", border=1, align='C')
        pdf.cell(25, 10, "Cantidad", border=1, align='C')
        pdf.cell(40, 10, "Precio Unit.", border=1, align='C')
        pdf.cell(40, 10, "Subtotal", border=1, align='C'); pdf.ln()
        
        pdf.set_font("Arial", size=10)
        for item in self.pedido.menus:
            subtotal_item = item.precio * item.cantidad
            pdf.cell(80, 10, item.nombre, border=1)
            pdf.cell(25, 10, str(item.cantidad), border=1, align='C')
            pdf.cell(40, 10, f"${item.precio:,.0f}", border=1, align='R')
            pdf.cell(40, 10, f"${subtotal_item:,.0f}", border=1, align='R'); pdf.ln()

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(145, 10, "Subtotal:", 0, 0, 'R'); pdf.cell(40, 10, f"${self.subtotal:,.0f}", 0, 1, 'R')
        pdf.cell(145, 10, "IVA (19%):", 0, 0, 'R'); pdf.cell(40, 10, f"${self.iva:,.0f}", 0, 1, 'R')
        pdf.cell(145, 10, "Total:", 0, 0, 'R'); pdf.cell(40, 10, f"${self.total:,.0f}", 0, 1, 'R')
        pdf.ln(5)
        
        pdf.set_font("Arial", 'I', 9); pdf.cell(0, 10, "Gracias por su compra", 0, 1, 'C')
        
        pdf_filename = "boleta.pdf"
        pdf.output(pdf_filename)
        return pdf_filename

    def generar_boleta(self):
        """Coordina la generación de la boleta y la creación del PDF."""
        return self.crear_pdf()