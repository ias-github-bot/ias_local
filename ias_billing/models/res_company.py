# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo.models import Model, api
from odoo import fields


class ResCompany(Model):
    _inherit = 'res.company'

    invoice_terms = fields.Text('Invoice Terms')
    resolution = fields.Char(string='Resolution')
    authorization_date = fields.Date('Date Authorization')
    from_res = fields.Char(string='Resolution (From)')
    to_res = fields.Char(string='Resolution (To)')
