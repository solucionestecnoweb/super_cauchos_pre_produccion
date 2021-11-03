# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from itertools import accumulate
import json
from datetime import datetime, timedelta
import base64
from io import StringIO
from odoo import api, fields, models
from datetime import date
from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning

import time

class PurchaseOrderImports(models.Model):
	_inherit = "purchase.order"

	load_plan = fields.Binary(string='Load Plan')
	package_list = fields.Binary(string='Package List')
	landed_date = fields.Date(string='Landed Date')
	merchandise_available_load = fields.Binary(string='Merchandise Available for Load')

	aduana_agency_id = fields.Many2one(comodel_name='purchase.order.imports.aduana', string='Aduana Agency')
	aduana_costs = fields.Float(string='Aduana Estimated Costs')
	aduana_date = fields.Date(string='Aduana Estimated Date')
	aduana_doc = fields.Binary(string='Attach Document')

	aduana_payment_ids = fields.One2many(comodel_name='purchase.order.imports.aduana.payment', inverse_name='purchase_order_id', string=' Aduana Payment')

class PurchaseOrderLineImports(models.Model):
	_inherit = "purchase.order.line"

	pr = fields.Char(string='PR')
	pronto_pago = fields.Char(string='Pronto Pago Promotion')
	super_promo = fields.Char(string='Super Promo Promotion')
	apart_to_seller = fields.Integer(string='Set Apart to Seller', compute="compute_seller")
	apart_qty_available = fields.Integer(string='Set Apart Quantity Available', compute='compute_available')
	
	def compute_seller(self):
		for item in self:
			xfind = self.env['sale.order.line'].search([
				('state', 'in', ('draft', 'sent')),
				('product_id', '=', item.product_id.id),
				('is_transit_merch', '=', True),
			])
			item.apart_to_seller = 0
			for line in xfind:
				item.apart_to_seller += line.product_uom_qty

	def compute_available(self):
		for item in self:
			item.apart_qty_available = item.product_qty - item.apart_to_seller
