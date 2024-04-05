{
    "name": "UniCube Delivery System",
    "summary": """
        UniCube Delivery System """,
    'author': "UniCube",
    "license": "LGPL-3",
    'category': 'UniCube/Localization',
    'version': '17.0.0.1',
    'website': "https://unicube.vn",
    'support': 'community@unicube.vn',
    "depends": ["base", "sale", "stock", "account", "l10n_vn", "unicubevn_bank", "unicubevn_address", "unicubevn_ipn",
                "unicubevn_pwa", "unicube_apis", "bean_core"],
    "auto_install": ['base'],
    "data": [
        "views/res_config.xml",
        "views/res_partner.xml",
        "views/res_users.xml",
        'views/stock_picking_views.xml',
        'views/stock_picking_views_kaban.xml',
        'views/stock_lot.xml',
        'reports/paper_format.xml',
        'reports/delivery_receipt.xml',
    ],
    "images": ["static/description/image.jpeg"],
    'installable': True,
    'application': True,
    'assets': {
        'web.report_assets_common': [
            "unicubevn_delivery/static/src/scss/report.scss",
        ],
    }
}
