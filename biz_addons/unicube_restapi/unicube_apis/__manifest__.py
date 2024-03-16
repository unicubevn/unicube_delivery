# -*- coding: utf-8 -*-
{
    "name": "UniCube OpenApi",

    "summary": "UniCube OpenApi for Delivery System",

    "description": """
Long description of module's purpose
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
    "depends": ["base","fastapi", "auth_jwt"],

    # always loaded
    "data": [
        # "security/ir.model.access.csv",
        "data/auth_jwt_validator.xml",
        "views/views.xml",
        "views/templates.xml",
    ],
    # only loaded in demonstration mode
    # "demo": [
    #     "demo/demo.xml",
    # ],
}
