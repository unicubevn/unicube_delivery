# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import time
from typing import Annotated, Union

import jwt

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi_auth_jwt.dependencies import AuthJwtPartner

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from odoo.addons.fastapi.dependencies import odoo_env, Environment

from .unicube_apis import router


class TestData(BaseModel):
    name: Union[str, None] = None
    email: Union[str, None] = None
    uid: int


# @router.post("/get_sample_token", tags=["HTTP[Bearer]+JWT"])
# def get_sample_token(env: Annotated[Environment, Depends(odoo_env)], aud: str, email: str, ) -> str:
#     validator = env["auth.jwt.validator"].sudo().search([("name", "=", "unicube")])
#     print("start time: ", time.time(), "to time:", time.time() + 600)
#     payload = {
#         "aud": aud or validator.audience,
#         "iss": validator.issuer,
#         "exp": time.time() + 600,
#     }
#     if email:
#         payload[validator.partner_id_strategy] = email
#     print("Start to encode...")
#     print("key: ", validator.secret_key)
#     print("[algorithm]: ", validator.secret_algorithm)
#     print("payload[validator.partner_id_strategy]",
#           f"{validator.partner_id_strategy}:{payload[validator.partner_id_strategy]}")
#     access_token = jwt.encode(
#         payload, key=validator.secret_key, algorithm=validator.secret_algorithm
#     )
#     return access_token


@router.get("/whoami", response_model=TestData, tags=["HTTP[Bearer]+JWT"])
def whoami(
        partner: Annotated[
            Partner,
            Depends(AuthJwtPartner(validator_name="unicube")),
        ],
) -> TestData:
    return TestData(
        name=partner.name,
        email=partner.email,
        uid=partner.env.uid,
    )


@router.get("/whoami-public-or-jwt", response_model=TestData, tags=["HTTP[Bearer]+JWT"])
def whoami_public_or_jwt(
        partner: Annotated[
            Partner,
            Depends(AuthJwtPartner(validator_name="demo", allow_unauthenticated=True)),
        ],
):
    if partner:
        return TestData(
            name=partner.name,
            email=partner.email,
            uid=partner.env.uid,
        )
    return TestData(uid=partner.env.uid)


@router.get("/cookie/whoami", response_model=TestData, tags=["HTTP[Bearer]+JWT"])
def whoami_cookie(
        partner: Annotated[
            Partner,
            Depends(AuthJwtPartner(validator_name="demo_cookie")),
        ],
):
    return TestData(
        name=partner.name,
        email=partner.email,
        uid=partner.env.uid,
    )


@router.get("/cookie/whoami-public-or-jwt", response_model=TestData, tags=["HTTP[Bearer]+JWT"])
def whoami_cookie_public_or_jwt(
        partner: Annotated[
            Partner,
            Depends(
                AuthJwtPartner(validator_name="demo_cookie", allow_unauthenticated=True)
            ),
        ],
):
    if partner:
        return TestData(
            name=partner.name,
            email=partner.email,
            uid=partner.env.uid,
        )
    return TestData(uid=partner.env.uid)


@router.get("/keycloak/whoami", response_model=TestData, tags=["HTTP[Bearer]+JWT"])
def whoami_keycloak(
        partner: Annotated[
            Partner, Depends(AuthJwtPartner(validator_name="demo_keycloak"))
        ],
):
    return TestData(
        name=partner.name,
        email=partner.email,
        uid=partner.env.uid,
    )


@router.get("/keycloak/whoami-public-or-jwt", response_model=TestData, tags=["HTTP[Bearer]+JWT"])
def whoami_keycloak_public_or_jwt(
        partner: Annotated[
            Partner,
            Depends(
                AuthJwtPartner(validator_name="demo_keycloak", allow_unauthenticated=True)
            ),
        ],
):
    if partner:
        return TestData(
            name=partner.name,
            email=partner.email,
            uid=partner.env.uid,
        )
    return TestData(uid=partner.env.uid)
