# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api,_
import datetime
from odoo.exceptions import UserError, ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'stock.move'

    stock=fields.Float(compute='_compute_stock_mano')

    def _compute_stock_mano(self):
        for selff in self:
            cantidad=0
            #selff.stock=selff.location_id.id
            busca=selff.env['stock.quant'].search([('location_id','=',selff.location_id.id),('product_id','=',selff.product_id.id)])
            if busca:
                for det in busca:
                    cantidad=cantidad+det.quantity
            selff.stock=cantidad


class SaleOrder(models.Model):
    _inherit = 'stock.picking'

    def action_confirm(self):
        super().action_confirm()
        if self.picking_type_id.code!="incoming" and self.picking_type_id.code!="mrp_operation":
            for det in self.move_ids_without_package:
                if det.stock>0:
                    if det.stock>=det.quantity_done:
                        if det.quantity_done>0:
                            pass
                        else:
                            raise UserError(_("La cantidad a transferir no debe ser cero"))
                    else:
                        raise UserError(_("La cantidad a transferir del producto %s no puede ser mayor al stock actual del almacen de origen")%det.product_id.name)
                else:
                    raise UserError(_("El producto %s no puede ser movido con stock cero del almacen de origen")%det.product_id.name)

    def button_validate(self):
        super().button_validate()
        if self.picking_type_id.code!="incoming" and self.picking_type_id.code!="mrp_operation":
            for det in self.move_ids_without_package:
                if det.stock>0:
                    if det.stock>=det.quantity_done:
                        if det.quantity_done>0:
                            pass
                        else:
                            raise UserError(_("La cantidad a transferir no debe ser cero %s")%det.stock)
                    else:
                        raise UserError(_("La cantidad a transferir del producto %s no puede ser mayor al stock actual del almacen de origen")%det.product_id.name)
                else:
                    raise UserError(_("El producto %s no puede ser movido con stock cero del almacen de origen")%det.product_id.name)
