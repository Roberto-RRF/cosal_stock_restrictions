# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class ReturnPickingInherit(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.constrains('product_return_moves')
    def _check_return_quantities(self):
        """
        Valida que en cada línea de devolución la cantidad ingresada no sea mayor que la cantidad
        disponible del movimiento original (cantidad original menos la cantidad ya devuelta).
        """
        for wizard in self:
            for return_line in wizard.product_return_moves:
                if return_line.move_id:
                    # Cantidad disponible inicialmente es la cantidad original del movimiento
                    allowed_qty = return_line.move_id.quantity
                    # Restamos la cantidad ya devuelta en movimientos de retorno asociados
                    for move in return_line.move_id.move_dest_ids:
                        if move.origin_returned_move_id and move.origin_returned_move_id == return_line.move_id:
                            allowed_qty -= move.quantity
                    allowed_qty = float_round(
                        allowed_qty, precision_rounding=return_line.move_id.product_id.uom_id.rounding
                    )
                    if return_line.quantity > allowed_qty:
                        raise UserError(_(
                            "The return quantity for product '%s' is greater than the available quantity (%s)."
                        ) % (return_line.product_id.display_name, allowed_qty))
