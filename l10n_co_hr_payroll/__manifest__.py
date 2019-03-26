# coding: utf-8
{
    'name': 'l10n_co_hr_payroll',
    'summary': '''
    .
    ''',
    'author': 'Ingenieria Aplicaciones y Software',
    'website': 'https://www.ias.com.co',
    'license': 'AGPL-3',
    'category': 'Installer',
    'version': '11.0.0.0.1',
    'depends': [
        'base', 'hr', 'hr_payroll', 'hr_contract', 'hr_attendance', 'account', 'mail',
    ],
    'test': [
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/hr_ov_structure_rule_type.xml',
        'data/hr_contribution_register.xml',
        'data/hr_salary_rule_category.xml',
        'data/hr_salary_rule.xml',
        'data/hr_payroll_structure.xml',
        'data/ir_sequence.xml',
        'data/hr_payroll_structure.xml',
        'reports/report_view.xml',
        'reports/hr_attendance_analysis_report.xml',
        'views/hr_employee.xml',
        'views/hr_employee_accumulated.xml',
        'views/hr_contract.xml',
        'views/hr_payslip.xml',
        'views/hr_overtime.xml',
        'views/res_partner.xml',
        'views/hr_loan.xml',
        'views/hr_social_contribution.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
