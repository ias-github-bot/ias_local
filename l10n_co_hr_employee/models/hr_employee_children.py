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
from odoo import models, fields


GENDER_SELECTION = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')]


class HrEmployeeChildren(models.Model):
    _name = 'hr.employee.children'
    _description = 'HR Employee Children'

    name = fields.Char(
        "Name", required=True)
    date_of_birth = fields.Date(
        "Date of Birth", oldname='dob')
    employee_id = fields.Many2one(
        'hr.employee', "Employee")
    gender = fields.Selection(
        selection=GENDER_SELECTION, string='Gender')
