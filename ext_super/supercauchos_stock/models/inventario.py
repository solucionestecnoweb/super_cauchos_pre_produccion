# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import json
from datetime import datetime, timedelta
import base64
from io import StringIO
from odoo import api, fields, models
from datetime import date
from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning

import time

class InventarioProductos(models.Model):
	_inherit = "product.product"

	@api.constrains('product_tmpl_id')
	def _default_campos(self):
		self.modelo = self.product_tmpl_id.modelo
		self.iva = self.product_tmpl_id.iva
		self.type_cauchos = self.product_tmpl_id.type_cauchos
		self.tarps = self.product_tmpl_id.tarps
		self.load_speed = self.product_tmpl_id.load_speed
		self.service_in = self.product_tmpl_id.service_in
		self.filler = self.product_tmpl_id.filler
		self.brand_id = self.product_tmpl_id.brand_id
		self.group_id = self.product_tmpl_id.group_id
		self.qty_hq = self.product_tmpl_id.qty_hq
		self.deote = self.product_tmpl_id.deote
		self.physical_count = self.product_tmpl_id.physical_count

	modelo = fields.Char(string='Modelo')
	iva = fields.Char(string='I.V.A.')
	type_cauchos = fields.Char(string='Tipo de Caucho')
	tarps = fields.Char(string='Lonas')
	load_speed = fields.Char(string='Load/Speed')
	service_in = fields.Char(string='Service Index')
	filler = fields.Float(string='Nro. Filler')
	brand_id = fields.Many2one('product.brand', string='Marca')
	group_id = fields.Many2one('product.group', string='Grupo')
	qty_hq = fields.Char(string='Qty Of 40HQ')
	deote = fields.Date(string='Fecha de Fabricación')
	physical_count = fields.Float(string='Conteo Físico')
	
class InventarioProductos(models.Model):
	_inherit = "product.template"

	modelo = fields.Char(string='Modelo')
	iva = fields.Char(string='I.V.A.')
	type_cauchos = fields.Char(string='Tipo de Caucho')
	tarps = fields.Char(string='Lonas')
	load_speed = fields.Char(string='Load/Speed')
	service_in = fields.Char(string='Service Index')
	filler = fields.Float(string='Nro. Filler')
	brand_id = fields.Many2one('product.brand', string='Marca')
	group_id = fields.Many2one('product.group', string='Grupo')
	qty_hq = fields.Char(string='Qty Of 40HQ')
	deote = fields.Date(string='Fecha de Fabricación')
	physical_count = fields.Float(string='Conteo Físico')
	

class MarcasProductos(models.Model):
	_name = 'product.brand'

	name = fields.Char(string='Nombre')

class GruposProductos(models.Model):
	_name = 'product.group'

	name = fields.Char(string='Nombre')

class InventarioProductos(models.Model):
	_inherit = "stock.picking"

	filler_per = fields.Float(string='Filler Facturado (%)', compute='_compute_filler_per')

	def _compute_filler_per(self):
		for item in self:
			item.filler_per = 0
			filler = 0
			for line in item.move_ids_without_package:
				filler += (line.quantity_done * line.product_id.filler)
				item.filler_per = filler

class AutomaticLot(models.Model):
	_inherit = 'stock.quant'

	@api.onchange('location_id','inventory_quantity')
	def _onchange_location_id(self):
		if not self.lot_id and self.inventory_quantity > 0:
			value = {
				'product_id': self.product_id.id,
				'company_id': self.env['res.company']._company_default_get('stock.quant').id,
				'product_qty': self.inventory_quantity
			}
			self.lot_id = self.env['stock.production.lot'].create(value)