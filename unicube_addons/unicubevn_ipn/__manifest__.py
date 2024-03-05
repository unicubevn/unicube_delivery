# -*- coding: utf-8 -*-
{
    'name': "VietQR with auto complete invoice for TIMO's personal current account (TIMO is a Vietnamese digital bank)",

    'summary': """
        This module will publish a IPN Url to receive the TIMO's (a Vietnamese digital bank) callback api which provide the data of 
        bank account changes""",

    'description': """
        This module will provided:
        -   IPN Url: '/cube/timo' to receive the TIMO (a digital bank) callback api which provide the data of 
        bank account changes..
        -   'Timo callback data handling function.
    """,

    'author': "UniCube",
    "license": 'OPL-1',
    'category': 'UniCube/Localization',
    "sequence": 200,
    'version': '17.0.0.2',
    'website': "https://unicube.vn",
    'support': 'community@unicube.vn',
    "application": True,
    "installable": True,
    'price': 50.00,
    'currency': 'USD',

    "images": ["static/description/image.gif"],

    # any module necessary for this one to work correctly
    'depends': ['base', 'unicubevn_bank','payment_custom'],
    'data': [
        'security/ir.model.access.csv',
        'data/payment.provider.csv',
        'data/res_config_settings.xml',
        'data/res_groups.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        'views/ipn_key_views.xml',
        'menus/bank_menu.xml',
    ],

}
