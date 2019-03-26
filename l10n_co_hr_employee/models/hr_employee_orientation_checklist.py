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


class OrientationChecklist(models.Model):
    _name = 'hr.orientation.checklist'
    _description = "Checklist"
    _rec_name = 'checklist_name'
    _inherit = ['mail.thread']

    checklist_name = fields.Char(string='Name', required=True)
    checklist_department = fields.Many2one('hr.department',
                                           string='Department', required=True)
    active = fields.Boolean(
                            string='Active', default=True,
                            help="""Set active to false to hide the Orientation
                            Checklist without removing it."""
                            )
    checklist_line_id = fields.One2many('hr.orientation.check',
                                        'checklist', String="Checklist")


class OrientationChecklistNew(models.Model):
    _name = 'hr.orientation.check'

    checklist_line_name = fields.Many2one('hr.checklist.line', string='Name')
    checklist_line_user = fields.Many2one(
                                         'res.users',
                                         string='Responsible User',
                                         related=
                                         'checklist_line_name.responsible_user'
                                         )
    expected_date = fields.Date(string="Expected Date",
                                default=fields.Datetime.now)
    status = fields.Char(string='Status',
                         readonly=True, default=lambda self: _('New'))
    checklist = fields.Many2one('hr.orientation.checklist',
                                string="Checklist", ondelete='cascade')
    relative_field = fields.Many2one('hr.employee.orientation')