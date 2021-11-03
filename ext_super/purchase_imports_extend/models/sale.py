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

class SaleOrderImport(models.Model):
    _inherit = 'sale.order'

    is_transit_merch = fields.Boolean(string='Use Merchandise in Transit?')

class SaleOrderLineImport(models.Model):
    _inherit = 'sale.order.line'

    is_transit_merch = fields.Boolean(related='order_id.is_transit_merch')
    
