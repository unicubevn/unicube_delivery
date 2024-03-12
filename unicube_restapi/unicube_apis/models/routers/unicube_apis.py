#   Copyright (c) by The UniCube, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.

from datetime import datetime, timedelta, timezone
from http.client import HTTPException
import statistics
from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import requests
from odoo.fields import Datetime
from pydantic import BaseModel
from jose import JWTError, jwt

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.api import Environment
from .decorators import auth_user, get_current_active_user
from .unicube_redis import redis_single, gen_auth_key
from ..schemas.order import OrderSchema, ConfirmPickingSchema
from ..schemas.receipt import ReceiptSchema
from .handlerespon import make_response

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# app = FastAPI()

class PartnerInfo(BaseModel):
    name: str
    email: str

class TestData(BaseModel):
    name: Union[str, None] = None
    email: Union[str, None] = None
    uid: int

class TokenData(BaseModel):
    phone: str | None = None
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


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# -> list[PartnerInfo]:

@router.get("/partners", response_model=list[PartnerInfo])
def get_partners(current_user: Annotated[dict, Depends(get_current_active_user)], env: Annotated[Environment, Depends(odoo_env)]): 
    print('------current user------', current_user)
    
    return [
        PartnerInfo(name=str(partner.name), email=partner.email if partner.email else "No email" )
        for partner in env["res.partner"].sudo().search([])
    ]

def create_access_token(payload: dict, expires_delta: timedelta | None = None):

    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else: 
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    _key = gen_auth_key(obj_type='user_account', payload=payload)

    redis_single.set(_key, encoded_jwt)
    return encoded_jwt


@router.post("/token")
async def login_for_access_token(env: Annotated[Environment, Depends(odoo_env)], token_data: TokenData ):

    print('-----token data-----', token_data)
    url = 'http://localhost:8070'
    session_url = f'{url}/web/session/authenticate'
    data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'db': 'delivery_db',
            'login': token_data.phone,
            'password': token_data.password,
        }
    }
    session_response = requests.post(session_url, json=data)
    session_data = session_response.json()

    user = session_data.get('result')

    # user = None
    if not user:
        raise HTTPException(
            status_code=statistics.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    res_partner = env["res.partner"].sudo().search([('id', 'like', user.get('partner_id'))])

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        payload={
            'phone': user.get('username'),
            'email': res_partner.email,
            # 'store_id': user.get('user_companies').get('current_company'),
            'name': user.get('name')
        },
        expires_delta=access_token_expires
    )

    return {
        "data": Token(token=access_token, token_type="bearer"),
        "base": UnicubeModel()
    }

@router.post("/create-receipt")
async def create_receipt(env: Annotated[Environment, Depends(odoo_env)], receipt_schema:ReceiptSchema):

    _data = receipt_schema.model_dump()
    print('------data-------', _data)
    # print('---time now---', Datetime.now())
    new_picking = env["stock.picking"].sudo().create({

        'partner_id': _data.get('store_id'),
        'company_id': 1,
        'user_id': 2,
        'location_id': 4,
        'location_dest_id': 8,
        'picking_type_id': 1,
        'scheduled_date': _data.get('scheduled_date')
    })

    _product_list = [
        {
            'id': 2,
            'name': 'Fast Delivery Pack'
        },
        {
            'id': 3,
            'name': 'Normal Delivery Pack'
        }
    ]

    if not new_picking.id:
        return 'create receipt failed'

    for item in _product_list:
        new_stock_move = env['stock.move'].sudo().create({
            'partner_id': _data.get('store_id'),
            'product_id': item.get('id'),
            'picking_id': new_picking.id,
            'company_id': 1,

            'location_id': 4,
            'location_dest_id': 8,
            'picking_type_id': 1,
            'name': item.get('name'),
            'description_picking': item.get('name')
        })
        if not new_stock_move:
            return "create stock move failed"                

    return make_response(
        data={
            'picking_id': new_picking.id
        },
        msg='success'
    )

@router.post("/create-order")
async def create_order(env: Annotated[Environment, Depends(odoo_env)], order_schema: OrderSchema):
    
    _model_dump = order_schema.model_dump()
    print('-----_model_dump-----', _model_dump)
    print('---dummy prod----', _model_dump.get('product_items'))
    _product_list = _model_dump.get('product_items')
    _sum_item = len(_product_list)
    _total_amount = 0
    _total_fee = 0
    
    for item in _product_list:
        _product_id = 3 if item.get('type') == 0 else 2
        _total_amount += item.get('price')
        _total_fee += item.get('fee')

        _stock_lot = env["stock.lot"].sudo().create({
            'store_id': _model_dump.get('store_id'),
            'product_id': _product_id,
            'last_delivery_partner_id': item.get('contact_id'),
            'price': item.get('price'),

            'picking_id': _model_dump.get('picking_id'),
            'type': item.get('type'),
            'description': item.get('desc')
        })

        if not _stock_lot:
            return 'add order to receipt failed'
        
        _stock_move_id = env['stock.move'].sudo().search([
            ('picking_id','=',_model_dump.get('picking_id')), ('product_id','=',_product_id)
        ])
        print('---- _stock_move_id -----', _stock_move_id)

        try:
            _stock_move_line = env['stock.move.line'].sudo().create({
                'lot_name': _stock_lot.name,
                'picking_id': _model_dump.get('picking_id'),
                'product_id': _product_id,
                'move_id': _stock_move_id.id,
                'company_id': 1,
                'lot_id': _stock_lot.id,
                'location_id': 4,
                'location_dest_id': 8,
                'quantity': 1
            })

        except Exception as e:
            return make_response(msg='failed', status=0, error_code=e)

    # update Demand
    env['stock.picking'].sudo().search([('id','=',_model_dump.get('picking_id'))]).write({
        'total_order': _sum_item,
        'total_amount': _total_amount,
        'total_fee': _total_fee
    })
    
    return make_response(msg='success')


@router.post("/confirm-picking")
async def create_order(env: Annotated[Environment, Depends(odoo_env)], confirm_picking: ConfirmPickingSchema):
    _data = confirm_picking.model_dump
    print('----confirm---_data-----', _data)
    try:
        _result = env['stock.picking'].sudo().search([('id','=',_data.get('picking_id'))]).write({
            'state': _data.get('state')
        })
        if not _result:
            return make_response(msg='update state err', status=0)

    except Exception as e:
        make_response(
            msg=e,
            status=0
        )

    return make_response(
        msg='success',
    )


@router.get("/get-orders")
async def get_order_by_store(env: Annotated[Environment, Depends(odoo_env)], page: int = 1):
    _store_id = 7

    try:
        _order_data = env['stock.lot'].sudo().search([
            ('store_id','=',_store_id)
        ], offset=(page - 1) * 10, limit=10)

        total = _order_data.search_count([('store_id','=',_store_id)])

        data_order = []
        for item in _order_data:
            data_order.append({
                'name': item.name,
                'price': item.price,
                'desc': item.description,
                'type': item.type,

                'fee': item.fee,
                'delivery_order_id': item.delivery_order_id,
                'store_id': item.store_id,
                'picking_id': item.picking_id,
                'create_date': item.create_date
            })

    except Exception as e:
        return make_response(msg='failed', status=0, error_code=e)

    return make_response(
        data={
            'orders': data_order,
            'total': total,
            'limit': 10
        },
        msg='success'
    )

@router.get("/get-picking")
async def create_receipt(env: Annotated[Environment, Depends(odoo_env)], page: int = 1):
    _store_id = 7
    try:
        picking_model = env['stock.picking'].sudo().search([('partner_id','=',_store_id)], offset=(page - 1) * 10, limit=10)
        picking_data = []
        for item in picking_model:
            picking_data.append({
                'name': item.name,
                'location_id': item.location_id.id,
                'location': item.location_id.name,
                'location_dest_id': item.location_dest_id.id,
                'location_dest': item.location_dest_id.name,
                'scheduled_date': item.scheduled_date,

                'total_fee': item.total_fee,
                'total_amount': item.total_amount,
                'total_order': item.total_order,
                'state': item.state
            })
    except Exception as e:
        return make_response(msg=e, status=0)
    
    return make_response(
        data=picking_data,
        msg='success'
    )

# dummy variables
# _name = 'stock.lot'
# picking_type_code = self.env.context.get('restricted_picking_type_code')   --- keywork find stock.picking
