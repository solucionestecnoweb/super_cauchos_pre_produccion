{
    'name': 'Reporte de Prorrateo de IVA',
    'description': 'Módulo para el reporte de prorrateo de IVA',
    'version': '13.0.1.0.0',
    'author': 'OasisConsultora',
    'maintainer': 'OasisConsultora',
    'website': 'oasisconsultora.com',
    'license': 'AGPL-3',
    'depends': ['account', 'administration_module'],
    'data': [
        'views/wizard_prorrateo_iva_reporte.xml',
        'reports/prorrateo_iva_reporte.xml',
        ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
