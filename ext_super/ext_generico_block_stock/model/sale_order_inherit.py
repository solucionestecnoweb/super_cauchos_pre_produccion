# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api,_
import datetime
from odoo.exceptions import UserError, ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    stock=fields.Float(compute='_compute_stock_mano')

    @api.onchange('product_id')
    def _compute_stock_mano(self):
        for selff in self:
            selff.stock=selff.product_id.qty_available

    @api.onchange('product_id','product_uom_qty')
    #@api.depends('product_id')
    def valida(self):
        #raise UserError(_("Prueba"))
        # ESTE CAMPO is_transit_merch  ES DEL MODULO DE TRANSITO DE OLIVER, QUITAR SI NO SE VA A USAR EL MODULO DE TRANSITO DE MERCANCIA
        if self.order_id.is_transit_merch==False:
            if not self.product_id.id:
                pass
            else:
                if self.product_id.qty_available>0:
                    if self.product_id.qty_available>=self.product_uom_qty:
                        if self.product_uom_qty>0:
                            pass
                        else:
                            raise UserError(_("La cantidad seleccionada no debe ser igual a cero"))
                    else:
                        raise UserError(_("La cantidad a vender del producto %s no puede ser mayor al stock actual")%self.product_id.name)
                else:
                    raise UserError(_("El producto %s no puede ser vendido con stock cero o negativo")%self.product_id.name)

#class SaleOrder(models.Model):
    #_inherit = 'sale.order'


    """def action_confirm(self):
        super().action_confirm()
        for det in self.order_line:
            if det.product_id.qty_available>0:
                if det.product_id.qty_available>=det.product_uom_qty:
                    if det.product_uom_qty>0:
                        pass
                    else:
                        raise UserError(_("La cantidad seleccionada no debe ser igual a cero"))
                else:
                    raise UserError(_("La cantidad a vender del producto %s no puede ser mayor al stock actual")%det.product_id.name)
            else:
                raise UserError(_("El producto %s no puede ser vendido con stock cero")%det.product_id.name)"""
