import json
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import os

class InvoiceService:
    """Service for generating downloadable invoices"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Load company information from environment variables
        self.company_name = os.getenv("COMPANY_NAME", "Your Company Name")
        self.company_address = os.getenv("COMPANY_ADDRESS", "Your Company Address")
        self.product_name = os.getenv("PRODUCT_NAME", "Premium Access")
        
    def generate_invoice_pdf(self, transaction) -> BytesIO:
        """Generate PDF invoice for a completed transaction"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
        
        # Parse extra data
        extra_data = json.loads(transaction.extra_data or "{}")
        webhook_data = extra_data.get("webhook_data", {})
        payment_data = extra_data.get("payment_data", {})
        customer_data = extra_data.get("customer_data", {})
        
        # Build invoice content
        story = []
        
        # Header
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30
        )
        story.append(Paragraph(self.company_name, header_style))
        story.append(Paragraph(self.company_address, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Invoice title and number
        invoice_title = ParagraphStyle(
            'InvoiceTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.black
        )
        story.append(Paragraph(f"INVOICE #{transaction.id:06d}", invoice_title))
        story.append(Spacer(1, 20))
        
        # Invoice details table
        invoice_date = transaction.completed_at or transaction.created_at
        details_data = [
            ['Invoice Date:', invoice_date.strftime('%B %d, %Y')],
            ['Transaction ID:', str(transaction.id)],
            ['Payment ID:', extra_data.get("whop_payment_id", "N/A")],
            ['Status:', transaction.status.title()]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 30))
        
        # Bill to section
        story.append(Paragraph("BILL TO:", self.styles['Heading3']))
        customer_name = transaction.customer_name or customer_data.get("name", "Valued Customer")
        customer_email = transaction.customer_email or customer_data.get("email", "")
        
        story.append(Paragraph(customer_name, self.styles['Normal']))
        if customer_email:
            story.append(Paragraph(customer_email, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Items table
        story.append(Paragraph("ITEMS:", self.styles['Heading3']))
        
        items_data = [
            ['Description', 'Quantity', 'Unit Price', 'Total'],
            ['Cerebra Premium Access', '1', f'${transaction.amount:.2f}', f'${transaction.amount:.2f}']
        ]
        
        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(items_table)
        story.append(Spacer(1, 30))
        
        # Total section
        total_data = [
            ['Subtotal:', f'${transaction.amount:.2f}'],
            ['Tax:', '$0.00'],
            ['Total:', f'${transaction.amount:.2f}']
        ]
        
        total_table = Table(total_data, colWidths=[4*inch, 2*inch])
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(total_table)
        story.append(Spacer(1, 40))
        
        # Footer
        footer_text = """
        Thank you for your purchase! You now have lifetime access to Cerebra Premium.
        
        For support, please contact us at support@cerebra.com
        
        This invoice was generated automatically and is valid without signature.
        """
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def get_receipt_data(self, transaction) -> Dict[str, Any]:
        """Get structured receipt data for display"""
        extra_data = json.loads(transaction.extra_data or "{}")
        webhook_data = extra_data.get("webhook_data", {})
        payment_data = extra_data.get("payment_data", {})
        customer_data = extra_data.get("customer_data", {})
        
        return {
            "invoice_number": f"{transaction.id:06d}",
            "transaction_id": transaction.id,
            "payment_id": extra_data.get("whop_payment_id"),
            "invoice_date": (transaction.completed_at or transaction.created_at).strftime('%B %d, %Y'),
            "customer_name": transaction.customer_name or customer_data.get("name", "Valued Customer"),
            "customer_email": transaction.customer_email or customer_data.get("email", ""),
            "amount": transaction.amount,
            "status": transaction.status,
            "product_name": "Cerebra Premium Access",
            "company_name": self.company_name,
            "company_address": self.company_address
        }

# Global instance
invoice_service = InvoiceService()