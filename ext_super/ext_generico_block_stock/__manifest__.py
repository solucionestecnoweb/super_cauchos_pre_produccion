# -*- coding: utf-8 -*-
{
    'name': "X Bloqueo de stock cero en ventas, transferencias y entregas",

    'summary': """X Bloqueo de stock cero en ventas, transferencias y entregas""",

    'description': """
       X Bloqueo de stock cero en ventas, transferencias y entregas
       Colaborador: Ing. Darrell Sojo
    """,
    'version': '1.0',
    'author': 'INM&LDR Soluciones Tecnologicas',
    'category': 'X Bloqueo de stock cero en ventas, transferencias y entregas',

    # any module necessary for this one to work correctly
    'depends': ['product','base', 'account','sale','purchase','stock','product','purchase_imports_extend'],

    # always loaded
    'data': [
        'vista/sale_order_inherit.xml',
        'vista/stock_piking_inherit.xml',
        #'security/ir.model.access.csv',
    ],
    'application': True,
}
