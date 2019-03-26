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


class HrCurriculum(models.Model):
    _name = 'hr.curriculum'
    _description = "Employee's Curriculum"

    @api.onchange('employee_id')
    def get_employee_data(self):
        if self.employee_id:
            self.phone = self.employee_id.mobile_phone
            self.identification = self.employee_id.identification_id

    name = fields.Char('Name', required=True,)
    end_job = fields.Char('Job position end')
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    description = fields.Text('Description')
    partner_id = fields.Char(
        'Partner', help="Employer, School, University, "
                        "Certification Authority")
    identification = fields.Char('Identification')
    phone = fields.Char('Phone number')
    location = fields.Char('Location', help="Location")
    expire = fields.Boolean('Expire', help="Expire", default=True)
    wage_init = fields.Float('Initial wage')
    wage_end = fields.Float('Last wage')
    reason_leaving = fields.Boolean('Reason for leaving')
    info_performance = fields.Boolean('Performance information')
    leaving_selection = fields.Selection([
        ('v_resignation', 'Voluntary resignation'),
        ('m_agreement', 'Mutual agreement'),
        ('o_restructuring', 'Organizational Restructuring'),
        ('dismissal', 'Dismissal'),
        ('c_completion_internship', 'Contract Completion - Internship'),
        ('others', 'Others reasons'),], 'Leaving reason')
    leaving_description = fields.Text('Leaving description')
    job_knowledge = fields.Selection([
        ('excelent', 'Excelent'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('deficient', 'Deficient')], 'Job knowledge')
    interest_in_work = fields.Selection([
        ('excelent', 'Excelent'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('deficient', 'Deficient')], 'Interest in Work')
    performance = fields.Selection([
        ('excelent', 'Excelent'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('deficient', 'Deficient')], 'Performance')
    responsability = fields.Selection([
        ('excelent', 'Excelent'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('deficient', 'Deficient')], 'Responsability')
    discipline = fields.Selection([
        ('excelent', 'Excelent'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('deficient', 'Deficient')], 'Discipline')
    relationships = fields.Selection([
        ('excelent', 'Excelent'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('deficient', 'Deficient')], 'Relationships')
    supervisory_skill = fields.Selection([
        ('excelent', 'Excelent'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('deficient', 'Deficient')], 'Supervisory Skill')
    teamwork = fields.Selection([
        ('excelent', 'Excelent'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('deficient', 'Deficient')], 'Teamwork')
    work_under_pressure = fields.Selection([
        ('excelent', 'Excelent'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('deficient', 'Deficient')], 'Work under pressure')
    performance_description = fields.Text('Performance description')
    concerns_union_act = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], 'Concerns and / or Union Activities')
    company_hire_again = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], 'I would hire him again')
    company_description = fields.Text('Company comments')
    informant = fields.Char('Informant')
    informant_position = fields.Char('Informant job position')
    survey_date = fields.Date('Survey date')
