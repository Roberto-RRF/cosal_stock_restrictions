from odoo import models, api, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.constrains('move_ids_without_package')
    def _check_allowed_products(self):
        """
        Valida que todos los productos en las líneas del picking estén presentes en la
        orden original (venta o compra) cuyo nombre se encuentre en el campo 'origin'.
        Se aplica únicamente para pickings de tipo 'internal' o 'outgoing'.
        """
        for picking in self:
            # Se valida solo para traslados internos o entregas
            if picking.picking_type_code in ['internal', 'outgoing'] and picking.origin:
                allowed_products = []
                # Se busca primero la Orden de Venta cuyo nombre coincida con el origen
                sale_order = self.env['sale.order'].search([('name', '=', picking.origin)], limit=1)
                if sale_order:
                    allowed_products = sale_order.order_line.mapped('product_id').ids
                else:
                    # Si no se encontró la Orden de Venta, se busca la Orden de Compra
                    purchase_order = self.env['purchase.order'].search([('name', '=', picking.origin)], limit=1)
                    if purchase_order:
                        allowed_products = purchase_order.order_line.mapped('product_id').ids
                
                # Si se encontró la orden y se definen productos permitidos,
                # se valida cada línea del picking
                if allowed_products:
                    for move in picking.move_ids:
                        if move.product_id.id not in allowed_products:
                            raise ValidationError(_(
                                "No se permite agregar el producto '%s' ya que no estaba incluido en la orden original '%s'."
                            ) % (move.product_id.display_name, picking.origin))
