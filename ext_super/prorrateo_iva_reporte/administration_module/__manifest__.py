{
    'name': 'Administration',
    'description': 'Administration Module',
    'version': '13.0.1.0.0',
    'author': 'OasisConsultora',
    'maintainer': 'OasisConsultora',
    'website': 'oasisconsultora.com',
    'license': 'AGPL-3',
    'depends': ['account', 'stock', 'sale', 'isrl_retention', 'account_promotions'],
    'data': [
        'views/administration_menu_items.xml',
        'views/account_move_out_invoice.xml',
        'views/account_move_in_invoice.xml',
        'views/account_move_filters.xml',
        'views/wizard_out_invoice.xml',
        'views/wizard_in_invoice.xml',
        'report/out_invoice_report.xml',
        'report/in_invoice_report.xml',
        ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
