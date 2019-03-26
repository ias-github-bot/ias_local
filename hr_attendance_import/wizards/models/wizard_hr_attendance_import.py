from odoo import api, fields, models, _
from dateutil.parser import parse
from odoo.tools import pycompat
import base64
import logging
import psycopg2
import pandas as pd
import io
try:
    import xlrd
    try:
        from xlrd import xlsx # pylint: disable=W0611
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

_logger = logging.getLogger(__name__)


class WizardImportAttendance(models.TransientModel):
    _name = "wizard.import.attendance.xls"

    file_xls = fields.Binary("File XLS/XLSX", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('successful', 'Successful'),
        ('error', 'Error'),
    ], default="draft")
    error_message = fields.Text(readonly=True)

    def validate_length_columns(self, field):
        if not xlrd:
            raise ValueError(
                _("Unable to load xls file: requires Python module xlrd"))
        data = base64.b64decode(self.file_xls)
        book = xlrd.open_workbook(file_contents=data)
        ncols = book.sheet_by_index(0).ncols
        if ncols > len(field):
            message = _(
                "The number of columns indicated in xls is greater than"
                "the columns allowed, the format must be:"
                "Employee, check in, check Out")
            raise ValueError(message)
        if ncols < len(field)-2:
            message = _(
                "The number of columns indicated in xls is less than"
                "the columns allowed, the minimum allowed is 3")
            raise ValueError(message)
        if ncols >= len(field)-2 and ncols <= len(field):
            field = field[0: ncols]
        return field

    @api.multi
    def compose_html_error(self, messages):
        colors = {'error': 'red', 'warning': 'yellow', 'info': 'green'}
        html = ""
        for msg in messages:
            if msg['type'] in ['error', 'warning']:
                self.state = 'error'
            color = colors.get(msg['type'], 'green')
            msg['color'] = color
            html += (
                "<p style=color:{color}>{message}</p><br/>".format(
                    **msg))
        self.error_message = html
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'res_model': 'wizard.import.attendance.xls',
            'target': 'new',
        }

    @api.multi
    def load_file(self):
        self.ensure_one()
        self._cr.execute('SAVEPOINT import')
        import_fields = ['employee_id', 'check_in', 'check_out']
        try:
            data, import_fields = self._convert_import_data(
                import_fields, {})
            data = self._parse_import_data(data, import_fields)
        except ValueError as error:
            message = [{
                'type': 'error',
                'message': pycompat.text_type(error),
                'record': False}]
            return self.compose_html_error(message)
        model = self.env['hr.attendance'].with_context(
            import_file=True)
        defer_parent_store = self.env.context.get(
            'defer_parent_store_computation', True)
        if defer_parent_store and model._parent_store:
            model = model.with_context(defer_parent_store_computation=True)
        import_result = model.load(import_fields, data)
        _logger.info('done')
        try:
            self._cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass
        if not import_result['messages']:
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return self.compose_html_error(import_result['messages'])

    @api.model
    def _convert_import_data(self, fields_val, options):
        import_fields = [f for f in fields_val if f]
        data = self.get_tuple_data_xls()
        return data, import_fields

    @api.multi
    def _parse_import_data(self, data, fields_val):
        base_import = self.env['base_import.import']
        return base_import._parse_import_data_recursive(
            'hr.attendance', '', data, fields_val, {})

    @api.multi
    def _read_xls(self):
        """ Read file content, using xlrd lib """
        base_import = self.env['base_import.import']
        data = base64.b64decode(self.file_xls)
        book = xlrd.open_workbook(file_contents=data)
        return base_import._read_xls_book(book)

    def get_tuple_data_xls(self):
        result = []
        groups = {}
        datafile = base64.b64decode(self.file_xls)
        input_file = io.BytesIO(datafile)
        xml_obj = pd.read_excel(input_file)
        grouped_by_code = xml_obj.groupby("AC-No.")
        grouped_state = xml_obj.groupby(["AC-No.", "New State"])
        for code, group in grouped_by_code:
            time_in = grouped_state.get_group(
                (code, 'OverTime In'))['Time'].values[0]
            time_out = grouped_state.get_group(
                (code, 'OverTime Out'))['Time'].values[0]
            result += [[
                group['Name'].values[0].strip(),
                parse(time_in).strftime("%Y-%m-%d %H:%M:%S"),
                parse(time_out).strftime("%Y-%m-%d %H:%M:%S")]]
        return result
        
