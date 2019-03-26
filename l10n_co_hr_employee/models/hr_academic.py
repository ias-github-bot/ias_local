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


class HrAcademic(models.Model):
    _name = 'hr.academic'
    _inherit = 'hr.curriculum'

    diploma = fields.Char(
        string='Diploma', translate=True)
    study_field = fields.Char(
        string='Field of study', translate=True,)
    activities = fields.Text(
        string='Activities and associations', translate=True)