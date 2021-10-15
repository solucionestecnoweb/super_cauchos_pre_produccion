from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import logging

import io
from io import BytesIO

import xlsxwriter
import shutil
import base64
import csv
import xlwt

_logger = logging.getLogger(__name__)

class SaleMerchandiseTransit(models.TransientModel):
    _inherit = 'wizard.merchandise.transit'

    def print_pdf(self):
        return {'type': 'ir.actions.report','report_name': 'sales_merchandise_in_transit.sales_merchandise_in_transit','report_type':"qweb-pdf"}

    def show_merchandise(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "temp.merchandise.transit",
            "views": [[self.env.ref('sales_merchandise_in_transit.sales_merchandise_transit_view_tree').id, "tree"],[False, "form"]],
            "name": "Mercancía en Tránsito",
        }

    def date_fix(self):
        new_date = self.date_now - timedelta(hours=4)
        return new_date