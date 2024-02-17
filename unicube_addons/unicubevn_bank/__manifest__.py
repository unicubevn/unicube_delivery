# -*- coding: utf-8 -*-
{
    'name': "Payment: Vietnamese Bank Base Module",

    'summary': """
        This module is the base module for generator VietQR module.(VietQR is the Vietnam's QR standard for payment)""",

    'description': """
        This module is the base module for generator VietQR module. 
        This module will provided:
        -   All the Vietnamese bank info and bankcode which announced by State Bank of Viet Nam.
        -   Add "default bank account" field to res.company model.
        -   Add VietQR for invoice view form.
    """,

    'author': "UniCube",
    "license": "LGPL-3",
    'category': 'UniCube/Localization',
    'version': '17.0.0.3',
    'website': "https://unicube.vn",
    'support': 'community@unicube.vn',
    "application": True,
    "installable": True,

    "images": ["static/description/image.png"],

    # any module necessary for this one to work correctly
    'depends': ['base', 'l10n_vn', 'account_qr_code_emv',"base_vat"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/res.bank.csv',
        'reports/paper_format.xml',
        'reports/invoice_receipt.xml',
        'views/account_move.xml',
        'views/ipn_log.xml',
        'views/res_bank_account.xml',
        'views/res_company_info.xml',
        'menus/bank_menu.xml',
        'data/res_partner_bank.xml',
        # 'data/account_journal.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            "unicubevn_bank/static/src/scss/report.scss"
        ],
        'web.assets_backend': [
            "unicubevn_bank/static/src/json_field/**/*",
        ],
    }

}
