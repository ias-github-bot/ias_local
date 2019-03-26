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
from odoo import models, fields, api


class HrTypeOfContributor(models.Model):
    _name = 'hr.type.of.contributor'

    name = fields.Char(
        string='Name', translate=True)
    code = fields.Char(
        string='Code', translate=True,)
    description = fields.Char(
        string='Description', translate=True)

    employee_ids = fields.One2many('hr.employee', compute='_compute_employees_ids', store=False)

    @api.one
    def _compute_employees_ids(self):
        self.employee_ids = self.env['hr.employee'].search([('type_of_contributor', '=', self.id)])
