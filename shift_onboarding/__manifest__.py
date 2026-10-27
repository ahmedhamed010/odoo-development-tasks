{
    'name': "shift_onboarding",
    'author': "Ahmed",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': ['base', 'mail' , 'sale'],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/ir_cron.xml',
        'views/views.xml',
        'views/inherited_views.xml',
        'report/project_report.xml',
    ],
}

