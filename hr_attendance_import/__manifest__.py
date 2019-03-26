# coding: utf-8
{
    'name': 'hr_attendance_import',
    'summary': '''
    .
    ''',
    'author': 'Ingenieria Aplicaciones y Software',
    'website': 'https://www.ias.com.co',
    'license': 'AGPL-3',
    'category': 'Installer',
    'version': '11.0.0.0.1',
    'depends': [
        'hr_attendance'
    ],
    'test': [
    ],
    'data': [
        'views/assets.xml',
        'wizards/views/wizard_hr_attendance_import.xml'
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/tree_view_buttons.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
