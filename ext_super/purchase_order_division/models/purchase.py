from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
import base64
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools.float_utils import float_round

class PurchaseOrderDivision(models.Model):
    _inherit = 'purchase.order'

    purchase_type = fields.Selection(string='Purchase Type', selection=[('national', 'National'), ('international', 'International')], default='national')
    
