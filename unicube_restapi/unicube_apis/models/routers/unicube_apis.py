#   Copyright (c) by The UniCube, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.

from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
import requests

from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi_auth_jwt.dependencies import AuthJwtPartner
from odoo.addons.base.models.res_partner import Partner
from jose import JWTError, jwt
from odoo.http import request, Controller, route
# import jwt
from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


class PartnerInfo(BaseModel):
    name: str
    email: str

class TestData(BaseModel):
    name: Union[str, None] = None
    email: Union[str, None] = None
    uid: int

class TokenData(BaseModel):
    username: str | None = None
    password: str | None = None

class Token(BaseModel):
    token: str
    token_type: str

class UnicubeModel(BaseModel):
    error_code: str | None = ""
    errors: str | None = ""
    msg: str | None = ""
    status: int | None = 1
    time: float | None = ""
    version: str | None = "v1"


def get_user( username: str):
    
    user = request.env['res.users'].sudo().search([('login', 'like', username)])
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def verify_password(plain_password, hashed_password):
    
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = get_user(username)

    if not user:
        return False
    if not verify_password(password, "$pbkdf2-sha512$600000$Z8z5/7/3/l/L2Rvj/L9Xyg$clzZjS06ylwJ0DCXVt9NIlj3aeMVZMR4oZxpCWc4wjjKBuhwI8AOcrchfZDgUep4qAbzZlq8xaruYFpnW4KTpw"):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/partners", response_model=list[PartnerInfo])
def get_partners(env: Annotated[Environment, Depends(odoo_env)]) -> list[PartnerInfo]:
    return [
        PartnerInfo(name=partner.name, email=partner.email if partner.email else "No email" )
        for partner in env["res.partner"].sudo().search([])
    ]


@router.post("/token")
async def login_for_access_token(env: Annotated[Environment, Depends(odoo_env)], token_data: TokenData ):
    
    # _payload = kw
   
    # user = env['res.users'].sudo().search([('login', 'like', token_data.username)])
    # user = authenticate_user(token_data.username, token_data.password)

    url = 'http://localhost:8070'
    session_url = f'{url}/web/session/authenticate'
    data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'db': 'delivery_db',
            'login': token_data.username,
            'password': token_data.password,
        }
    }
    session_response = requests.post(session_url, json=data)
    session_data = session_response.json()
    user = session_data.get('result')
    print('------user-----', user)

    # user = None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    res_partner = env["res.partner"].sudo().search([('id', 'like', user.get('partner_id'))])
    print('-------res_partber-------', res_partner)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            'payload': {
                'phone': user.get('username'),
                'email': res_partner.email,
                'store_id': user.get('user_companies').get('current_company'),
                'name': user.get('name')
            }
        },
        expires_delta=access_token_expires
    )

    # return Token(
    #     access_token=access_token, token_type="bearer"
    # )

    return {
        "data": Token(token=access_token, token_type="bearer"),
        "base": UnicubeModel()
    }


@router.get("/whoami", response_model=TestData)
def whoami(
        partner: Annotated[
            Partner,
            Depends(AuthJwtPartner(validator_name="demo")),
        ],
) -> TestData:
    return TestData(
        name=partner.name,
        email=partner.email,
        uid=partner.env.uid,
    )


@router.get("/whoami-public-or-jwt", response_model=TestData)
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


@router.get("/cookie/whoami", response_model=TestData)
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


@router.get("/cookie/whoami-public-or-jwt", response_model=TestData)
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


@router.get("/keycloak/whoami", response_model=TestData)
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


@router.get("/keycloak/whoami-public-or-jwt", response_model=TestData)
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
