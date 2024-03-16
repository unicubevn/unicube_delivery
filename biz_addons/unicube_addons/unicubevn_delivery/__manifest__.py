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
    "depends": ["base", "sale", "stock", "account", "l10n_vn", "unicubevn_bank", "unicubevn_address", "unicubevn_ipn","unicubevn_pwa","unicube_apis"],
    "auto_install": ['base'],
    "data": [
        "views/res_partner.xml",
        "views/res_users.xml",
        'views/stock_picking_views.xml',
        'views/stock_lot.xml'
    ],
    "images": ["static/description/image.jpeg"],
    'installable': True,
    'application': True,
}
