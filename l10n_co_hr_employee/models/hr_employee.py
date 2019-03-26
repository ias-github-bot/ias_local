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
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.exceptions import UserError
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Family and children
    fam_spouse = fields.Char("Name")
    fam_spouse_employer = fields.Char("Employer")
    fam_spouse_tel = fields.Char("Telephone.")
    fam_spouse_address = fields.Char("Address")
    fam_children_ids = fields.One2many(
        'hr.employee.children', 'employee_id', "Children")
    fam_father = fields.Char("Father's Name")
    fam_father_date_of_birth = fields.Date(
        "Date of Birth", oldname='fam_father_dob')
    fam_mother = fields.Char("Mother's Name")
    fam_mother_date_of_birth = fields.Date(
        "Date of Birth", oldname='fam_mother_dob')
    fam_parents_address = fields.Char('Parents Address')
    # Emergency contacts
    emergency_contact_ids = fields.Many2many(
        string='Emergency Contacts', comodel_name='res.partner',
        relation='rel_employee_emergency_contact',
        column1='employee_id', column2='partner_id',
        domain=[('is_company', '=', False)])    
    # Employee age
    age = fields.Integer(
        'Age', readonly=True, compute='_compute_age')
    # Employee work location
    wlocation_id = fields.Many2one(
        'res.partner', string="Actual work location")
    # Projects employee
    project_ids = fields.One2many(
        'project.project', 'employee_id', string="Projects")
    # Language
    language_ids = fields.One2many(
        'hr.language', 'employee_id', u"Languages")
    # Employee skills
    skill_ids = fields.Many2many(
        'hr.skill',
        'skill_employee_rel',
        'employee_id',
        'skill_id',
        'Skills',
        domain="[('child_ids', '=', False)]")
    # Employee experience
    academic_ids = fields.One2many(
        'hr.academic', 'employee_id',
        'Academic experiences', help="Academic experiences")
    certification_ids = fields.One2many(
        'hr.certification', 'employee_id',
        'Certifications', help="Certifications")
    experience_ids = fields.One2many(
        'hr.experience', 'employee_id', 'Professional Experiences',
        help='Professional Experiences')
    # Employee seniority
    initial_employment_date = fields.Date(
        string='Date of Employment')
    length_of_service = fields.Float(
        compute="_get_employed_months", type='float',
        method=True, groups=False, string='Length of Service')
    # Resume employee
    biography = fields.Text('Biography')
    # Employee infractions
    infraction_ids = fields.One2many(
        'hr.infraction', 'employee_id',
        'Infractions', readonly=True,)
    infraction_action_ids = fields.One2many(
        'hr.infraction.action', 'employee_id',
        'Disciplinary Actions', readonly=True,)
    # Employee Work contact
    contact_person = fields.Char(string="Work Contact Person")
    relationship = fields.Char(string="Work Relationship")
    telephone_contact = fields.Char(string="Work telephone contact")
    # Employee document
    document_type = fields.Selection(
        [('cc', 'C.C.'),
         ('ce', 'C.E'),
         ('passport', 'Passport'),
         ('visa', 'Visa')],
        string="document type")
    visa_type = fields.Many2one(
        'hr.visa', string='Visa Type')
    expedition_place = fields.Char(
        string="expedition place")
    expedition_date = fields.Date(
        string="Expedition date")

    eps_id = fields.Many2one('res.partner', string='Eps',
                          domain="[('eps','=',True)]")
    arl_id = fields.Many2one('res.partner', string='Arl',
                          domain="[('arl','=',True)]")
    compensation_box_id = fields.Many2one(
        'res.partner', string='Compensation_box',
        domain="[('compensation_box','=',True)]")
    pension_severance_fund_id = fields.Many2one(
        'res.partner', string='Pension severance fund',
        domain="[('pension_severance_fund','=',True)]")

    type_of_contributor = fields.Many2one('hr.type.of.contributor',
                                          string='Type of contributor')

    medical_exam_ids = fields.One2many('hr.medical.exam',
                                       'employee_id', 'Medical exam')

    survey_ids = fields.One2many('survey.user_input', 'employee_id', "Survey")

    email = fields.Char('Email', related='work_email',)

    survey_count = fields.Integer('Number of survey',
                                  compute='_compute_survey_count')

    is_pensioned = fields.Boolean('Pensioned', default=False)

    @api.one
    def _compute_age(self):
        if self.birthday:
            dBday = datetime.strptime(self.birthday, OE_DATEFORMAT).date()
            dToday = datetime.now().date()
            self.age = dToday.year - dBday.year - ((
                dToday.month, dToday.day) < (dBday.month, dBday.day))

    @api.multi
    def _get_contracts_list(self, employee):
        """Return list of contracts in chronological order"""
        contracts = []
        for contract in employee.contract_ids:
            lenght = len(contracts)
            if lenght == 0:
                contracts.append(contract)
            else:
                date_c_start = datetime.strptime(contract.date_start,
                                                 OE_DATEFORMAT).date()
                i = lenght - 1
                while i >= 0:
                    date_contract_start = datetime.strptime(
                        contracts[i].date_start, OE_DATEFORMAT).date()
                    if date_contract_start < date_c_start:
                        contracts = contracts[:i + 1]\
                                    + [contract] + contracts[i + 1:]
                        break
                    elif i == 0:
                        contracts = [contract] + contracts
                    i -= 1

        return contracts

    @api.multi
    def _get_days_in_month(self, date_initial):

        last_date = date_initial - timedelta(days=(date_initial.day - 1)) + \
                    relativedelta(months=+1) + relativedelta(days=-1)

        return last_date.day

    @api.multi
    def get_months_service_to_date(self, employee):
        """Returns a dictionary of floats. The key is the employee id,
        and the value is number of months of employment.
        """

        date_today = date.today()
        delta = relativedelta(date_today, date_today)
        contracts = self._get_contracts_list(employee)

        if len(contracts) == 0:
            return [0.0, False]
        else:
            date_initial = datetime.strptime(
                contracts[0].date_start, OE_DATEFORMAT).date()

            if contracts[0].employee_id.initial_employment_date:

                date_first_contract = date_initial
                date_initial = datetime.strptime(
                    contracts[0].employee_id.initial_employment_date,
                    OE_DATEFORMAT).date()
                if date_first_contract < date_initial:
                    raise UserError(_("Employment Date mismatch!"
                                      "The initial employment date cannot"
                                      " be after the first contract in "
                                      "the system.\n"))

                delta = relativedelta(date_first_contract, date_initial)

            for c in contracts:
                date_start = datetime.strptime(c.date_start, '%Y-%m-%d').date()
                if date_start >= date_today:
                    continue

                # If the contract doesn't have an end date, use today's date
                # If the contract has finished consider the entire duration of
                # the contract, otherwise consider only the months in the
                # contract until today.
                #
                if c.date_end:
                    date_end = datetime.strptime(c.date_end, '%Y-%m-%d').date()
                else:
                    date_end = date_today
                if date_end > date_today:
                    date_end = date_today

                delta += relativedelta(date_end, date_start)

            # Set the number of months the employee has worked
            date_part = float(delta.days) / float(self._get_days_in_month(
                date_initial))

            delt = float((delta.years * 12) + delta.months)
            employee.initial_employment_date = date_initial
            res = [(delt + date_part), date_initial]

        return res

    @api.multi
    def _get_employed_months(self):
        for employee in self:
            res = self.get_months_service_to_date(employee)
            employee.length_of_service = res[0]
            employee.write({'initial_employment_date': res[1]})

    @api.multi
    def action_view_survey_user_input(self):
        action_rec = self.env.ref('survey.action_survey_user_input')
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update({'employee_id': self.ids[0]})
        action['domain'] = [('employee_id', '=', self.ids[0])]
        action['context'] = ctx
        return action

    def _compute_survey_count(self):
        Survey = self.env['survey.user_input']
        can_read = Survey.check_access_rights('read', raise_exception=False)
        for employee in self:
            employee.survey_count = can_read and Survey.search_count([
                ('employee_id', '=', employee.id)]) or 0
