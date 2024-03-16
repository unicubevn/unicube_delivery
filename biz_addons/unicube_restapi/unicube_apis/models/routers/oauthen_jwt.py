#   Copyright (c) by The UniCube, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from datetime import datetime, timezone, timedelta, time
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext

from jose import jwt, JWTError
from odoo.addons.unicube_apis.models.routers.unicube_apis import router as app
from odoo.addons.fastapi.dependencies import odoo_env, Environment
from odoo.exceptions import AccessDenied
from odoo.addons.fastapi_auth_jwt.dependencies import auth_jwt_http_header_authorization

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "e6e9c4a1a7faeed02d5661eaa213e0a1ebe4c9246c4a8ef55a4f7b2dfdadd706"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ===== Define Oauthen2 data ======
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def auth_jwt_http_header_authorization_1(
        credentials: Annotated[
            Optional[HTTPAuthorizationCredentials],
            Depends(oauth2_scheme),
        ]
):
    print("overridden in auth_jwt_http_header_authorization_1 is running ")
    if credentials is None:
        return None
    return credentials.credentials


auth_jwt_http_header_authorization = auth_jwt_http_header_authorization_1

# ===== faked database =====
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


def fake_hash_password(password: str):
    return "fakehashed" + password


# ===== Token Area =====
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# ===== User Area =====
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


# ===== Authen functions =====
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

def authenticate_user(odooEnv, username: str, password: str):
    print(username)
    print(odooEnv.uid, ' - ', odooEnv.values())
    user = odooEnv['res.users'].sudo().search([('login', '=', username)], limit=1)
    try:
        user = user.with_user(user)
        print(user)
        user._check_credentials(password, {'interactive': True})

        # TODO: update the login time as Odoo default login
        # if tz in pytz.all_timezones and (not user.tz or not user.login_date):
        # first login or missing tz -> set tz to browser tz
        # user.tz = datetime.now().tzname()
        # user._update_last_login
    except AccessDenied:
        print("Login failed for login:%s ", username)
        raise

    print("Login successful for login:%s ", username)

    return user


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           env: Annotated[Environment, Depends(odoo_env)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(token)
        validator = env["auth.jwt.validator"].sudo().search([("name", "=", "unicube")])
        print("validator found", validator)
        # payload = jwt.decode(token, key=validator.secret_key, algorithms=validator.algorithm)
        payload = validator._decode(token)
        print("payload", payload)
        username: str = payload.get(f"{validator.partner_id_strategy}")
        print("username", username)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        print("token_data", username)
    except JWTError:
        raise credentials_exception
    # user = get_user(fake_users_db, username=token_data.username)
    user = env['res.users'].sudo().search([('login', '=', username)], limit=1)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# # ===== Create jwt token =====
# def create_access_token(data: dict, expires_delta: timedelta | None = None, odooEnv):
#     # Get validator, in this scope , we use 'unicude', you can change to your
#     validator = odooEnv["auth.jwt.validator"].sudo().search([("name", "=", "unicube")])
#
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# ===== Path =====
@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        env: Annotated[Environment, Depends(odoo_env)]
) -> Token:
    print("In token path: ", form_data.username, " - ", form_data.password)
    user = authenticate_user(env, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print("Found user: ", user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = create_access_token(
    #     data={"sub": user.login}, expires_delta=access_token_expires
    # )
    # Create access token based on the login user infos
    # Force get validator is 'unicube, TODO: change it later
    validator = env["auth.jwt.validator"].sudo().search([("name", "=", "unicube")])
    payload = {"aud": form_data.client_id or validator.audience, "iss": validator.issuer,
               "exp": datetime.now(timezone.utc) + access_token_expires, f"{validator.partner_id_strategy}": user.login}
    access_token = jwt.encode(
        payload, key=validator.secret_key, algorithm=validator.secret_algorithm
    )
    print(access_token)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User, tags=["Oauth2+JWT"])
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return User(username=current_user.login, email=current_user.partner_id.email, full_name=current_user.name, disabled= not current_user.active)


@app.get("/users/me/items/",tags=["Oauth2+JWT"])
async def read_own_items(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.login}]
