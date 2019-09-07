from odoo import api, fields, models, _
import time
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError
import base64
import random
import string
import io

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    prime = fields.Float(
        string="Prime", compute='_get_prime', store=True)
    loan_ids = fields.One2many(
        'hr.loan.line', 'payroll_id',
        string="Loans", compute='_get_loan', store=True)
    total_order = fields.Float(
        string="Order", compute='_get_loan', store=True)
    total_loan = fields.Float(
        string="Loan", compute='_get_loan', store=True)
    total_savefunds = fields.Float(
        string="Save funds",  compute='_get_loan', store=True)
    total_socialc = fields.Float(
        string="Social contributions", compute='_get_loan', store=True)
    salary_hour = fields.Float(
        string="Salary Hour", compute="_get_salary_hour", store=True)
    txtbool = fields.Boolean(string='TXT Validator', default=False)
    txtfile = fields.Binary(string='TXT')
    txtfile_filename = fields.Char(string='TXT Filename')
    type_application = fields.Selection(
        [('I', 'Immediate'), ('M', 'Medium'), ('N', 'Night')],
        string="Application", default="I",
        track_visibility='onchange')

    @api.model
    def hr_verify_sheet(self):
        result = super(HrPayslip, self).hr_verify_sheet()
        # Acumulated amounts by payslip
        acumulatedLoan_obj = self.env['hr.employee.acumulated']
        payslip_line_obj = self.env['hr.payslip.line']
        for data in self.line_ids:
            # Acumulated
            payslip_lines = payslip_line_obj.search([('id', '=', data.id)])
            acumulatedLoan_obj.create({
                'employee_id': self.employee_id.id,
                'year_name': time.strftime('%Y'),
                'last_month': time.strftime('%B'),
                'date': time.strftime('%d/%m/%Y'),
                'rule_name': payslip_lines.name,
                'rule_amount': payslip_lines.total
            })
        return result

    @api.depends('employee_id', 'date_from')
    def _get_prime(self):
        day_from = fields.Date.from_string(self.date_from).strftime('%d')
        month = fields.Date.from_string(self.date_from).strftime('%m')
        if month == 6:
            if day_from >= 15:
                self.prime = self.employee_id.prime
        if month == 12:
            if day_from >= 15:
                self.prime = self.employee_id.prime

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(HrPayslip, self).get_worked_day_lines(
            contracts, date_from, date_to)
        # Objects definitions
        user_pool = self.env['res.users']
        contract_obj = self.env['hr.contract']
        # attendance_obj = self.env['hr.attendance']
        working_hours_obj = self.env['resource.calendar']
        # Common Variable
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        TIME_FORMAT = "%H:%M:%S"
        user = user_pool.browse(SUPERUSER_ID)
        # tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        sign_in_date = ""
        sign_in_attendance_time = timedelta(hours=00, minutes=00, seconds=00)
        sign_out_date = ""
        sign_out_attendance_time = timedelta(hours=00, minutes=00, seconds=00)

        def is_in_working_schedule(date_in, working_hours_id):
            found = False
            if type(date_in) is datetime:
                working_hours = working_hours_obj.browse(working_hours_id)
                for line in working_hours.attendance_ids:
                    if int(line.dayofweek) == date_in.weekday():
                        found = True
                        break
            return found

        def get_end_hour_of_the_day(date_in, working_hours_id):
            hour = 0.0
            if type(date_in) is datetime:
                working_hours = working_hours_obj.browse(working_hours_id)
                for line in working_hours.attendance_ids:
                    # First assign to hour
                    if \
                                            int(
                                                line.dayofweek
                                            ) == date_in.weekday() and hour == 0.0:
                        hour = line.hour_to
                    # Other assignments to hour
                    # No need for this part but it's a fail safe condition
                    elif \
                                                    int(
                                                        line.dayofweek
                                                    ) == date_in.weekday() and \
                                                    hour != 0.0 and line.hour_from < hour:
                        hour = line.hour_to
            return hour

        def get_time_from_float(float_time):
            str_time = str(float_time)
            str_hour = str_time.split('.')[0]
            str_minute = ("%2d" % int(
                str(
                    float(
                        "0." + str_time.split('.')[1]) * 60).split(
                    '.')[0])).replace(' ', '0')
            str_ret_time = str_hour + ":" + str_minute + ":00"
            str_ret_time = datetime.strptime(str_ret_time, TIME_FORMAT).time()
            return str_ret_time

        def get_float_from_time(time_type):
            signOnP = [int(n) for n in time_type.split(":")]
            signOnH = signOnP[0] + signOnP[1] / 60.0
            return signOnH

        for contract in contracts:
            val_overtime = 0.0
            # If work schedule not found skip this contract
            if not contract.resource_calendar_id:
                raise UserError(_(
                    'Working Schedule is not defined on this %s contract. %s.'
                ) % (contract.name))
                # continue

            for overtime_structure in self.env[
                    'hr.overtime.structure'].search(
                        [('overtime_required', '=', True)]):
                if overtime_structure:
                    if not contract.overtime_structure_id:
                        raise UserError(_(
                            'Overtime structure is not defined for '
                            'the employee %s on this %s contract.'
                            ) % (contract.employee_id.name, contract.name))
                        continue
            # By request
            else:
                hoe = contract.overtime_structure_id.hr_ov_structure_rule_ids
                hor = contract.overtime_structure_id.overtime_required
                if hoe:
                    for rule in hoe:
                        if rule.type_id and rule.type_detail_id:
                            for overtime in self.env[
                                'hr.overtime'].search(
                                [('employee_id', '=',
                                  contract.employee_id.id),
                                 ('from_date', '>=', date_from),
                                 ('to_date', '<=', date_to),
                                 ('state', '=', 'approve')]):
                                if \
                                                rule.type_detail_id.id == \
                                                overtime.type_detail_id.id:
                                    val_overtime = \
                                        overtime.total_time
                                    res.append({
                                        'name': 'Overtime ',
                                        'sequence': 11,
                                        'code':
                                            'OV' + overtime.type_detail_id.code,
                                        'number_of_days': val_overtime / 24,
                                        'number_of_hours': val_overtime,
                                        'rate': rule.rate,
                                        'contract_id': contract.id})
                        else:
                            raise Warning(_(
                                """
                                You need to define types and details
                                for the overtime structure %s
                                """) % (
                                              rule.hr_overtime_structure_id.name))
                else:
                    if hor:
                        raise Warning(_(
                            'You need to define overtime rules for %s'
                        ) % (contract.overtime_structure_id.name))
        return res

    @api.depends('employee_id', 'date_from', 'date_to')
    def _get_loan(self):
        array_order = []
        array_loan = []
        array_save = []
        array_savec = []
        total_order = 0
        total_loan = 0
        total_savefunds = 0
        total_socialc = 0
        # Order
        order_ids = self.env['hr.loan'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'approve'),
             ('type_loan', '=', 'order')])
        if order_ids:
            for order in order_ids:
                l_o = self.env['hr.loan.line'].search(
                    [('loan_id', '=', order.id), ('paid', '=', False)])
                total_order += l_o[0].amortization
                array_order.append(l_o[0].id)
        # Loan
        loan_ids = self.env['hr.loan'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'approve'),
             ('type_loan', '=', 'loan')])
        if loan_ids:
            for loan in loan_ids:
                l_l = self.env['hr.loan.line'].search(
                    [('loan_id', '=', loan.id), ('paid', '=', False)])
                total_loan += l_l[0].amortization
                array_loan.append(l_l[0].id)
        # Save funds
        save_funds_ids = self.env['hr.loan'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'approve'),
             ('type_loan', '=', 'save')])
        if save_funds_ids:
            for save in save_funds_ids:
                l_s = self.env['hr.loan.line'].search(
                    [('loan_id', '=', save.id), ('paid', '=', False)])
                total_savefunds += l_s[0].paid_amount
                array_save.append(l_s[0].id)
        # Social contributions
        # socialc_ids = self.env[
        #     'hr.social.contribution'].search(
        #         [('state', '=', 'active')])
        # if socialc_ids:
        #     for social in socialc_ids.social_contribution_ids:
        #
        #         if social.employee_id.id == self.employee_id.id:
        #             date_from = datetime.strptime(str(self.date_from + ' 00:00'), '%Y-%m-%d %H:%M')
        #             date_to = datetime.strptime(str(self.date_to + ' 00:00'), '%Y-%m-%d %H:%M')
        #             res = (date_to - date_from).days - 1
        #             if res < 17:
        #                 total_socialc += social.social_contribution / 2
        #             else:
        #                 total_socialc += social.social_contribution
        #
        # loan_data = array_order + array_loan + array_save + array_savec
        # self.total_order = total_order
        # self.total_loan = total_loan
        # self.total_savefunds = total_savefunds
        # self.total_socialc = total_socialc
        # self.loan_ids = loan_data

    @api.depends('employee_id', 'contract_id', 'date_from', 'date_to')
    def _get_salary_hour(self):
        from_date = fields.Date.from_string(self.date_from)
        to_date = fields.Date.from_string(self.date_to)
        total_days = (to_date - from_date).days + 1

        def addbusinessdays(origin_date, add_days):
            work_days = 0
            while add_days > 0:
                origin_date += timedelta(days=1)
                weekday = origin_date.weekday()
                if weekday >= 5:
                    pass
                else:
                    work_days += 1
                add_days -= 1
            return work_days

        if addbusinessdays(from_date, total_days) > 11:
            total_salary_days = None
            if self.contract_id.wage and self.contract_id.wage_type:
                total_salary_days = \
                    (self.contract_id.wage / float(self.contract_id.wage_type))
                total_salary_hours = total_salary_days / 8
                self.salary_hour = total_salary_hours
        else:
            if self.contract_id.wage and self.contract_id.wage_type:
                total_salary_days = \
                    (self.contract_id.wage / float(self.contract_id.wage_type))
                total_salary_hours = total_salary_days / 8
                self.salary_hour = total_salary_hours

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):

        res = super(HrPayslip, self).get_worked_day_lines(contract_ids, date_from, date_to)

        to_date = datetime.strptime(date_to, '%Y-%m-%d')

        contracts = self.env['hr.contract']

        for contract in contracts.browse(contract_ids):

            if to_date.month == 2:
                days_to_adjustment = 0
                hours_to_adjustment = 0

                if to_date.day == 28:
                    days_to_adjustment = 2
                    hours_to_adjustment = 16
                elif to_date.day == 29:
                    days_to_adjustment = 1
                    hours_to_adjustment = 8

                February_adjustment = {
                    'name': _('February Adjustment'),
                    'sequence': 13,
                    'code': 'WorkFeb',
                    'number_of_days': days_to_adjustment,
                    'number_of_hours': hours_to_adjustment,
                    'contract_id': contract.id}
                res += [February_adjustment]
        return res

    @api.multi
    def _timesheet_mapping(self, timesheet_sheets, payslip, date_from,
                           date_to):
        """This function takes timesheet objects imported from the timesheet
        module and creates a dict of worked days to be created in the payslip.
        """
        # Create one worked days record for each timesheet sheet
        wd_model = self.env['hr.payslip.worked_days']
        uom_obj = self.env['product.uom']
        uom_hours = self.env.ref('product.product_uom_hour')
        for ts_sheet in timesheet_sheets:
            # Get formated date from the timesheet sheet
            date_from_formated = fields.Date.to_string(
                fields.Datetime.from_string(ts_sheet.date_from))
            number_of_hours = 0
            for ts in ts_sheet.timesheet_ids:
                if date_from <= ts.date <= date_to:
                    # unit_amount = uom_obj._compute_qty_obj(
                    #     ts.product_uom_id,
                    #     ts.unit_amount, uom_hours)
                    # number_of_hours += unit_amount
                    number_of_hours = 8

            if number_of_hours > 0:
                wd_model.create({
                    'name': _('Timesheet %s') % date_from_formated,
                    'number_of_hours': number_of_hours,
                    'contract_id': payslip.contract_id.id,
                    'code': 'TS',
                    'imported_from_timesheet': True,
                    'timesheet_sheet_id': ts_sheet.id,
                    'payslip_id': payslip.id,
                })

    @api.multi
    def import_worked_days(self):
        """This method retreives the employee's timesheets for a payslip period
        and creates worked days records from the imported timesheets
        """
        for payslip in self:

            date_from = payslip.date_from
            date_to = payslip.date_to

            # Delete old imported worked_days
            # The reason to delete these records is that the user may make
            # corrections to his timesheets and then reimport these.
            wd_model = self.env['hr.payslip.worked_days']
            wd_model.search(
                [('payslip_id', '=', payslip.id),
                 ('imported_from_timesheet', '=', True)]).unlink()

            # get timesheet sheets of employee
            criteria = [
                ('date_from', '>=', date_from),
                ('date_to', '<=', date_to),
                ('state', '=', 'done'),
                ('employee_id', '=', payslip.employee_id.id),
            ]
            ts_model = self.env['hr_timesheet_sheet.sheet']
            timesheet_sheets = ts_model.search(criteria)

            if not timesheet_sheets:
                raise UserError(_("Sorry, but there is no approved Timesheets for the entire Payslip period"),)

            # The reason to call this method is for other modules to modify it.
            self._timesheet_mapping(timesheet_sheets, payslip, date_from, date_to)

    @api.onchange('name')
    def is_bank_account(self):
        if self.employee_id:
            if not self.employee_id.contract_id.resource_calendar_id:
                raise UserError(_(
                    'Please add a working hours (contract) for the employee:'
                    ' %s.') % (
                        self.employee_id.name))
            if not self.employee_id.contract_id.wage:
                raise UserError(_(
                    'Please add a salary (contract) for the employee: %s.') % (
                        self.employee_id.name))
            if not self.employee_id.bank_account_id:
                raise UserError(_(
                    'Please add bank account for the employee: %s.') % (
                        self.employee_id.name))
            if not self.employee_id.company_id.bank_account_id:
                raise UserError(_('Please add bank account for your company.'))
            if not self.employee_id.company_id.company_registry:
                raise UserError(_('Please add registry for your company.'))

    @api.multi
    def create_txt(self):
        # Header
        company_registry = (self.employee_id.company_id.company_registry
                            ).replace("-", "")
        c_deb = self.employee_id.company_id.bank_account_id.acc_number or ''
        t_c_de = self.employee_id.company_id.bank_account_id.account_type or ''
        type_payroll = str(225)
        type_app = self.type_application
        payroll_date = str(self.write_date).replace("-", "")[:8] or ''
        total_amounts = 0
        for data_amount in self.line_ids:
            if data_amount.name == 'TOTAL':
                total_amounts = data_amount.total
        t_c_de_new = ''
        if t_c_de == 'corriente':
            t_c_de_new = 'D'
        else:
            t_c_de_new = 'S'
        # Body
        ci = self.employee_id.identification_id or ''
        employee_name = self.employee_id.name
        employee_acc = self.employee_id.bank_account_id.acc_number or ''
        c_cre = self.employee_id.bank_account_id.account_type or ''
        t_c_cred_new = ''
        if c_cre == 'corriente':
            t_c_cred_new = '27'
        else:
            t_c_cred_new = '37'
        ent_c_cred = self.employee_id.bank_account_id.entity_code or ''
        ref = ''
        val = ''
        date_s = datetime.strptime(self.write_date, "%Y-%m-%d %H:%M:%S").date()

        sequence = self.env["hr.payslip.sequence"].generate_sequence(date_s,
                                                                     'single')
        content = base64.encodestring(u''.join((
            company_registry,
            type_payroll,
            type_app,
            sequence,
            c_deb,
            t_c_de_new,
            payroll_date,
            str(total_amounts).replace(".", ""), '\n',
            # Body
            ci,
            employee_name,
            t_c_cred_new,
            ent_c_cred,
            employee_acc,
            str(total_amounts).replace(".", ""),
            payroll_date)
        ).encode('utf-8').strip())

        self.write({'txtfile': content,
                    'txtfile_filename': 'Bancolombia.txt', 'txtbool': True})

    @api.multi
    def compute_sheet(self):
        result = super(HrPayslip, self).compute_sheet()
        for record in self:
            record.create_txt()
        return result


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    rate = fields.Float(string="Rate (%)", track_visibility='onchange')

    imported_from_timesheet = fields.Boolean(string='Imported From Timesheet', default=False)

    timesheet_sheet_id = fields.Many2one( string='Timesheet', comodel_name='hr_timesheet_sheet.sheet')


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    txtbool = fields.Boolean(string='TXT Validator', default=False)
    txtfile = fields.Binary(string='TXT',)
    txtfile_filename = fields.Char(string='TXT Filename')
    type_application = fields.Selection([
        ('I', 'Immediate'),
        ('M', 'Medium'),
        ('N', 'Night')],
        string="Application", default="I",
        track_visibility='onchange', required=True)


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.onchange('employee_ids')
    def is_bank_account(self):
        for d in self.employee_ids:
            if d.bank_account_id:
                pass
            else:
                raise UserError(_(
                    'Please add bank account for the employee: %s.') % (
                        d.name))
            if d.user_id.company_id.bank_account_id:
                pass
            else:
                raise UserError(_('Please add bank account for your company.'))
            if d.user_id.company_id.company_registry:
                pass
            else:
                raise UserError(_('Please add registry for your company.'))

    @api.multi
    def compute_sheet(self):

        result = super(HrPayslipEmployees, self).compute_sheet()
        active_id = self.env.context.get('active_id')
        content = ''
        output_h = io.StringIO()
        output_b = io.StringIO
        main_output = io.StringIO
        total = 0
        payslip_run_active = self.env['hr.payslip.run'].browse(active_id)
        type_application = payslip_run_active.type_application
        user = self.env['res.users'].browse(self._uid)
        payroll_date = str(self.write_date).replace("-", "")[:8]

        # Body
        for d in payslip_run_active.slip_ids:
            ci = d.employee_id.identification_id or ''
            employee_name = d.employee_id.name or ''
            employee_acc = d.employee_id.bank_account_id.acc_number or ''
            c_cre = d.employee_id.bank_account_id.account_type or ''
            total_amounts = 0
            for data_amount in d.line_ids:
                if data_amount.name == 'TOTAL':
                    total_amounts = data_amount.total
            total += total_amounts
            t_c_cred_new = ''
            if c_cre == 'corriente':
                t_c_cred_new = '27'
            else:
                t_c_cred_new = '37'
            ent_c_cred = d.employee_id.bank_account_id.entity_code or ''
            if content == '':
                output_b.write(u''.join((ci,
                             employee_name,
                             t_c_cred_new,
                             ent_c_cred,
                             employee_acc,
                             str(total_amounts).replace(".", ""),
                             payroll_date)).encode('utf-8').strip() + '\n')
            else:
                print >>output_b, (u''.join((
                    ci,
                    employee_name,
                    t_c_cred_new,
                    ent_c_cred,
                    employee_acc,
                    str(total_amounts).replace(".", ""),
                    payroll_date)).encode('utf-8').strip() + '\n')

                # Header
            type_payroll = str(225)
            company_registry = (user.company_id.company_registry
                                ).replace("-", "")
            c_deb = user.company_id.bank_account_id.acc_number or ''
            t_c_de = user.company_id.bank_account_id.account_type or ''
            t_c_de_new = ''
            if t_c_de == 'corriente':
                t_c_de_new = 'D'
            else:
                t_c_de_new = 'S'

        # Header
        date_s = datetime.strptime(self.write_date, "%Y-%m-%d %H:%M:%S").date()
        sequence = self.env["hr.payslip.sequence"].generate_sequence(date_s,
                                                                     'massive')

        output_h.write(u''.join((company_registry +
                       type_payroll +
                       type_application +
                       sequence +
                       c_deb +
                       t_c_de_new +
                       payroll_date +
                       str(total).replace(".", ""))).encode('utf-8'
                                                            ).strip() + '\n')

        main_output.write(output_h.getvalue())
        main_output.write(output_b.getvalue())
        content_body = base64.encodestring(main_output.getvalue())
        payslip_run_active.write({'txtfile': content_body,
                                  'txtfile_filename': 'Bancolombia.txt',
                                  'txtbool': True})
        return result


class HrPayslipSequence(models.Model):
    _name = 'hr.payslip.sequence'
    _description = 'hr payslip sequence '

    sequence = fields.Char(string='Sequence')
    date = fields.Date('Start date')

    @api.multi
    def generate_sequence(self, date, n_type):

        sequences = self.sequence_search(date)
        sequence = self.create_sequence(n_type)

        cont = 0

        while sequence in sequences:
            sequence = self.create_sequence(n_type)
            cont += 1

            if cont > 268:
                raise UserError(_('Sorry we have exhausted the sequence we'
                                  ' could use for this transaction for today'
                                  ' try again tomorrow.'))
        else:

            self.create({'sequence': sequence, 'date': date})
            return sequence

    @api.multi
    def sequence_search(self, date):
        sequences = []
        ids = self.env["hr.payslip.sequence"].search([('date', '=', date)])
        for id in ids:
            seq = id.sequence
            sequences.append(seq)

        return sequences

    @api.multi
    def create_sequence(self, n_type):
        letter = random.choice(string.ascii_letters)
        num = random.randint(0, 9)

        if n_type == 'massive':
            sequence = letter.upper() + str(num)
        else:
            sequence = str(num) + letter.upper()

        return sequence
