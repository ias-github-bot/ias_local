from odoo import api, fields, models, _
from datetime import datetime
import time


class HRContract(models.Model):
    _inherit = "hr.contract"

    is_prime = fields.Boolean(string="Got prime?")
    overtime_structure_id = fields.Many2one('hr.overtime.structure', string="Overtime Structure")

    wage_type = fields.Selection('_get_salary_type', string="Salary Type", default='30')

    @api.onchange('wage')
    def _do_primes(self):

        def push_data(self, prime):
            acumulatedLoan_obj = self.env['hr.employee.acumulated']
            self.employee_id.write({'prime': prime})
            acumulatedLoan_obj.create({
                'employee_id': self.employee_id.id,
                'date': time.strftime('%d/%m/%Y'),
                'year_name': time.strftime('%Y'),
                'last_month': time.strftime('%B'),
                'rule_name': 'Prima',
                'wage': self.wage,
                'prime': prime
            })

        length_data = 0
        suma = 0
        months_wages = []
        now = datetime.now()
        acumulatedLoan_obj = self.env['hr.employee.acumulated']
        if self.wage and self.is_prime and self.employee_id:
            acumulated = acumulatedLoan_obj.search(
                [('rule_name', '=', 'Prima'),
                 ('employee_id', '=', self.employee_id.id)])
            if acumulated:
                for a in acumulated:
                    year = u''.join((a.year_name)).encode('utf-8').strip()
                    date = datetime.strptime(
                        str(a.date), '%Y-%m-%d').strftime('%m')
                    months_wages.append((year, date, a.wage))
                for data in months_wages:
                    if str(now.year) == data[0]:
                        length_data = len(months_wages)
                        if length_data > 1:
                            suma += data[2]
                            if data[2] <= 3:
                                prime = self.wage / 2
                                return push_data(self, prime)
                            else:
                                prime = (suma / length_data) / 2
                                return push_data(self, prime)
                        else:
                            prime = self.wage / 2
                            return push_data(self, prime)
            else:
                prime = self.wage / 2
                return push_data(self, prime)

    def _get_salary_type(self):
        types = [('7', _('weekly')),
                 ('15', _('biweekly')),
                 ('30', _('monthly')),
                 ('60', _('bimonthly')),
                 ('90', _('quarterly')),
                 ('180', _('semi-annually')),
                 ('360', _('annually')),
                 ]
        return types
