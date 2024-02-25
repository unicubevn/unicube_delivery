{
    'name': "Utilities: Config PWA",

    'summary': """
        This is the custom module for configuring builtin Odoo PWA.
        """,

    'description': """
        This is the custom module for configuring builtin Odoo PWA, including:
            - Change PWA icon
            - Add custom path
    """,

    'author': "UniCube",
    "license": "LGPL-3",
    'category': 'UniCube/Localization',
    "sequence": 200,
    'version': '17.0.0.1',
    'website': "https://unicube.vn",
    'support': 'community@unicube.vn',
    "application": True,
    "installable": True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail'],
    "auto_install": True,

    "images": ["static/description/image.jpg"],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        'views/res_config.xml',
        'views/webclient_templates.xml',
        'views/push_notification.xml',
    ],
    'assets': {
        'web.assets_backend': [
            "unicubevn_pwa/static/src/js/firebase-app.js",
            "unicubevn_pwa/static/src/js/firebase-messaging.js",
            "unicubevn_pwa/static/src/js/backend_firebase.js",
        ],
        'web.assets_frontend': [
            "unicubevn_pwa/static/src/js/firebase-app.js",
            "unicubevn_pwa/static/src/js/firebase-messaging.js",
            "unicubevn_pwa/static/src/js/frontend_firebase.js",
        ]
    },
    "external_dependencies": {"python": ["pyfcm"]},
}
