from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class ContractType(models.Model):
    _inherit = 'hr.contract.type'

    training = fields.Boolean('Is Training')


class HrContract(models.Model):
    _inherit = 'hr.contract'

    training = fields.Boolean('Is Training', related="type_id.training")
    stage = fields.Selection([('elective', "Elective"),
                              ('practice', "Practice")],
                             string="Stage", track_visibility='onchange')
    date_start_practice_stage = fields.Date('Start Date Practice Stage')

    @api.onchange('type_id')
    def get_employee_data(self):
        if self.type_id:
            self.training = self.type_id.training

    @api.model
    def training_contract_practice_stage(self):
        self.search([
            ('training', '=', True),
            ('date_end', '=',
             fields.Date.to_string(date.today() +
                                   relativedelta(months=6)))]).write(
            {'stage': 'practice', 'date_start_practice_stage': date.today()})

        return True

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()

        if 'stage' in init_values and self.state == 'practice':
            return self.env.ref(
                'l10n_co_hr_employee.mt_training_contract_practice_stage')
        return super(HrContract, self)._track_subtype(init_values)
