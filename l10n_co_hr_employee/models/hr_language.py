# -*- coding: utf-8 -*-
##############################################################################
#
#    Ingeniería, Aplicaciones y Software S.A.S
#    Copyright (C) 2003-2018 Tiny SPRL (<http://www.ias.com.co>).
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
from odoo import tools
from odoo import models, fields


class HrLanguage(models.Model):
    _name = 'hr.language'

    name = fields.Selection(
        tools.scan_languages(),
        string="Language", required=True)
    description = fields.Char(
        string="Description", size=64, required=True)
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", required=True)
    can_read = fields.Boolean(
        string="Read", default=True)
    can_write = fields.Boolean(
        string="Write", default=True)
    can_speak = fields.Boolean(
        string="Speak", default=True)
