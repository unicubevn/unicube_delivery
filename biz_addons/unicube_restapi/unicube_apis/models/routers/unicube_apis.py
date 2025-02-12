#   Copyright (c) by The UniCube, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.

from datetime import datetime, timedelta, timezone
from http.client import HTTPException
import logging
import statistics
from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import requests
from odoo.fields import Datetime
from pydantic import BaseModel
from jose import JWTError, jwt
import json
from odoo.addons.unicube_apis.const import RECIEPT_STATE, DO_STATE

from odoo import tools
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.api import Environment
from .decorators import auth_user, get_current_active_user, convert_timestamp_to_datetime, remove_token
from .unicube_redis import redis_single, gen_auth_key
from ..schemas.order import OrderSchema, ConfirmPickingSchema
from ..schemas.receipt import ReceiptSchema
from ..schemas.address import CountrySchema
from ..schemas.contact import ContactSchema
from ..schemas.user import LogoutSchema
from ..schemas.report import ReportResponse

from .handlerespon import make_response
from .address import get_country_state, get_country_district, get_country_ward
from .contact import handle_create_conract, handle_get_contact, handle_get_contact_by_store


_logger = logging.getLogger(__name__)

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

class UnicubeModel(BaseModel):
    error_code: str | None = ""
    errors: str | None = ""
    msg: str | None = ""
    status: int | None = 1
    time: float | None = ""
    version: str | None = "v1"
    

class Token(BaseModel):
    token: str
    token_type: str

class Token1(UnicubeModel):
    data: Token



router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# -> list[PartnerInfo]:

product_list = [
        {
            'id': 2,
            'name': 'Fast Delivery Pack'
        },
        {
            'id': 1,
            'name': 'Normal Delivery Pack'
        }
    ]

@router.get("/partners", response_model=list[PartnerInfo])
def get_partners(current_user: Annotated[dict, Depends(get_current_active_user)], env: Annotated[Environment, Depends(odoo_env)]): 
    
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
    # to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    _key = gen_auth_key(obj_type='user_account', payload=payload)

    redis_single.set(_key, encoded_jwt)
    return encoded_jwt


@router.post("/login")
async def login_for_access_token(env: Annotated[Environment, Depends(odoo_env)], token_data: TokenData ):

    url = env['ir.config_parameter'].sudo().get_param('web.base.url')

    session_url = f'{url}/web/session/authenticate'
    data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'db': tools.config.get('db_name'),
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
    
    res_partner = env["res.partner"].sudo().search([('id', '=', user.get('partner_id'))])

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        payload={
            'phone': user.get('username'),
            'email': res_partner.email,
            'store_id': res_partner.store_id.id,
            'account_type': res_partner.account_type,
            'address': res_partner.contact_address_complete,
            'name': user.get('name')
        },
        expires_delta=access_token_expires
    )

    return Token1(data=Token(token=access_token, token_type="bearer"))


@router.post("/logout")
async def logout(
        env: Annotated[Environment, Depends(odoo_env)],
        current_user: Annotated[dict, Depends(get_current_active_user)],
        logout_schema: LogoutSchema
    ):

    _token = logout_schema.model_dump()
    if not _token:
        return make_response(msg='logout fail', status=0)
    
    res = remove_token(_token)
    if res:
        return make_response(msg='success', status=1)
    return make_response(msg='false', status=0)


@router.post("/create-receipt")
async def create_receipt(
        env: Annotated[Environment, Depends(odoo_env)],
        current_user: Annotated[dict, Depends(get_current_active_user)],
        receipt_schema:ReceiptSchema
    ):

    _data = receipt_schema.model_dump()
    print('----_data------', _data)

    _time_data = convert_timestamp_to_datetime(_data.get('scheduled_date'))

    match _data.get('type'):
        case 0:
            _attibute_value = 'normal'
            # _product_id = 2
            _product_id = 8
        case 1:
            _attibute_value = 'fast'
            # _product_id = 3
            _product_id = 7

    new_picking = env["stock.picking"].sudo().create({
        'partner_id': _data.get('store_id'),
        'owner_id': _data.get('contact_id'),
        'contact_phone': _data.get('contact_phone'),
        'contact_name': _data.get('contact_name'),
        'contact_address': _data.get('contact_address'),
        'company_id': 1,
        'type': _data.get('type'),

        'user_id': 2,
        'location_id': 4,
        'location_dest_id': 8,
        'picking_type_id': 1,
        'scheduled_date': _time_data
    })

    if not new_picking.id:
        return make_response(msg="create receipt failed", status=0)    

    new_stock_move = env['stock.move'].sudo().create({
        'partner_id': _data.get('store_id'),
        'product_id': _product_id,
        'picking_id': new_picking.id,
        'company_id': 1,

        'location_id': 4,
        'location_dest_id': 8,
        'picking_type_id': 1,
        'name': f'Delivery Pack {_attibute_value}',
        'description_picking': f'Delivery Pack {_attibute_value}'
    })
    if not new_stock_move:
        return make_response(msg="create stock move failed", status=0)

    return make_response(
        data={
            'name': new_picking.name,
            'picking_id': new_picking.id,
            'type': new_picking.type,
            'owner_id': new_picking.owner_id.id,
            'contact_phone': new_picking.contact_phone,
            'contact_address': new_picking.contact_address,
            'partner_id': new_picking.partner_id.id,
            'scheduled_date': new_picking.scheduled_date
        },
        msg='success'
    )

@router.post("/create-order")
async def create_order(
        env: Annotated[Environment, Depends(odoo_env)],
        current_user: Annotated[dict, Depends(get_current_active_user)],
        order_schema: OrderSchema
    ):
    
    _model_dump = order_schema.model_dump()
    _package_items = _model_dump.get('package_items')
    _sum_item = len(_package_items)

    _total_package_price = 0
    _total_price = 0

    match _model_dump.get('type'):
        case 0:
            _attibute_value = 'normal'
            # _product_id = 2
            _product_id = 8
        case 1:
            _attibute_value = 'fast'
            # _product_id = 3
            _product_id = 7
    
    for item in _package_items:
       
        _total_package_price += item.get('package_price')
        _total_price += item.get('price')

        _stock_lot = env["stock.lot"].sudo().create({
            'store_id': _model_dump.get('store_id'),
            'product_id': _product_id,
            'last_delivery_partner_id': _model_dump.get('contact_id'),
            'package_price': item.get('package_price'),

            'price': item.get('price'),
            'picking_id': _model_dump.get('picking_id'),
            'type': _model_dump.get('type'),
            'description': item.get('desc')
        })

        if not _stock_lot:
            return 'add order to receipt failed'
        
        _stock_move_id = env['stock.move'].sudo().search([
            ('picking_id','=',_model_dump.get('picking_id')), ('product_id','=',_product_id)
        ])

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
    _result = await update_stock_move(
            env,
            picking_id=_model_dump.get('picking_id'),
            product_id=_product_id,
            total_price=_total_price,
            total_package_price=_total_package_price
        )
    
    env['stock.picking'].sudo().search([('id','=',_model_dump.get('picking_id'))]).write({
        # 'owner_id': _model_dump.get('contact_id'),
        'total_order': _sum_item,
        'total_package_price': _total_package_price,
        'total_price': _total_price
    })
    
    return make_response(msg='success')


async def update_stock_move(
        env,
        picking_id,
        product_id,
        total_price,
        total_package_price
    ):

    _stock_move = env['stock.move'].sudo().search([
        ('picking_id','=',picking_id), ('product_id','=',product_id)
    ]).write({
        'product_value': total_price,
        'total_package_price': total_package_price
    })

    return True


@router.post("/confirm-picking")
async def confirm_picking(
        env: Annotated[Environment, Depends(odoo_env)],
        current_user: Annotated[dict, Depends(get_current_active_user)],
        confirm_picking_schema: ConfirmPickingSchema,
    ):

    _data = confirm_picking_schema.model_dump()
    try:
        _stock_picking = env['stock.picking'].sudo().search([('id','=',_data.get('picking_id')), ('partner_id','=',_data.get('store_id'))])
        _stock_picking.action_confirm()
        
    except Exception as e:
        make_response(
            msg=e,
            status=0
        )

    return make_response(
        msg='success',
    )


@router.get("/get-orders")
async def get_order_by_store(env: Annotated[Environment, Depends(odoo_env)],page: int = 1):
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
async def get_receipt(
        env: Annotated[Environment, Depends(odoo_env)], 
        current_user: Annotated[dict, Depends(get_current_active_user)],
        store_id: int,
        state_picking:str = 'draft',
        code: str = '',
        phone: str = '',
        pageIndex: int = 1,
        pageSize: int = 10
    ):
    

    addons_filter = ()
    if code:
        addons_filter = ('name','=',code)
    if phone:
        addons_filter = ('contact_phone','=', phone)

    _store_id = current_user.get('store_id')
    # _store_id = 7
    try:
        if state_picking in RECIEPT_STATE:
            match state_picking:
                case 'draft':
                    _state = 'draft'
                case 'waiting':
                    _state = 'assigned'
                case 'receiving':
                    _state = 'done'
                case 'cancelled':
                    _state = 'cancel'

            _filter = [('partner_id', '=', _store_id), ('state', '=', _state)]
            if addons_filter:
                _filter.append(addons_filter)


            picking_model = env['stock.picking'].sudo().search(
                _filter,
                offset=(pageIndex - 1) * pageSize,
                limit=pageSize,
                order="id desc"
            )
            total = picking_model.sudo().search_count(_filter)

        else:
            match state_picking:
                case 'sorting':
                    _state = 'draft'
                case 'delivering':
                    _state = 'assigned'
                case 'delivered':
                    _state = 'done'

            _filter = [('partner_id','=',_store_id), ('DO_state','=',_state)]
            if addons_filter:
                _filter.append(addons_filter)

            picking_model = env['stock.picking'].sudo().search(
                _filter,
                offset=(pageIndex - 1) * pageSize,
                limit=pageSize,
                order="id desc"
            )
            total = picking_model.sudo().search_count(_filter)

        picking_data = []
        for item in picking_model:
            _stock_lot_data = []
            _stock_lot = env['stock.lot'].sudo().search([('picking_id','=',item.id)])
            
            for stock_item in _stock_lot:
                _stock_lot_data.append({
                    'serial_number': stock_item.name,
                    'desc': stock_item.description,
                    'price': stock_item.price,
                    'package_price': stock_item.package_price,
                })

            picking_data.append({
                'id': item.id,
                'name': item.name,
                'location_id': item.location_id.id,
                'location': item.location_id.name,

                'type': item.type,
                'location_dest_id': item.location_dest_id.id,
                'location_dest': item.location_dest_id.name,
                'scheduled_date': item.scheduled_date,

                'total_price': item.total_price,
                'total_package_price': item.total_package_price,
                'total_order': item.total_order,
                'state': item.state,

                'store_phone': item.partner_id.id,
                'store_name': item.partner_id.name,
                'phone': item.owner_id.phone,
                'contact_name': item.contact_name,
                'address': item.owner_id.contact_address_complete,

                'item': _stock_lot_data,
                'create_date': item.create_date.timestamp(),
            })

    except Exception as e:
        return make_response(
            msg=e,
            status=0
        )
    
    return make_response(
        data=picking_data,
        extend={
            'total': total
        },
        msg='success'
    )

@router.get("/get-picking-by-id")
async def get_receipt_by_id(
        env: Annotated[Environment, Depends(odoo_env)],
        current_user: Annotated[dict, Depends(get_current_active_user)],
        store_id: int,
        id: int
    ):
    try:
        picking_model = env['stock.picking'].sudo().search([('id','=',id), ('partner_id','=',store_id)],limit=1)

        for item in picking_model:
            _stock_lot_data = []
            _stock_lot = env['stock.lot'].sudo().search([('picking_id','=',item.id)])
            
            for stock_item in _stock_lot:
                _stock_lot_data.append({
                    'stock_lot_id': stock_item.id,
                    'serial_number': stock_item.name,
                    'desc': stock_item.description,
                    'price': stock_item.price,
                    'package_price': stock_item.package_price,
                })

            picking_data = {
                'id': item.id,
                'name': item.name,
                'location_id': item.location_id.id,
                'location': item.location_id.name,
                'location_dest_id': item.location_dest_id.id,
                'location_dest': item.location_dest_id.name,
                'scheduled_date': item.scheduled_date,

                'total_price': item.total_price,
                'total_package_price': item.total_package_price,
                'total_order': item.total_order,
                'state': item.state,

                # 'store_phone': item.partner_id.id,
                'store_name': item.partner_id.name,
                'store_id': item.partner_id.id,
                'type': item.type,

                'phone': item.contact_phone,
                'name': item.contact_name,
                'address': item.contact_address,
                'owner_id': item.owner_id.id,

                'item': _stock_lot_data,
                'create_date': item.create_date.timestamp(),
            }

    except Exception as e:
        _logger(e)
    
    return make_response(
        data=picking_data,
        msg='success'
    )


@router.get("/get-country-state")
async def country_state(
        env: Annotated[Environment, Depends(odoo_env)],
        current_user: Annotated[dict, Depends(get_current_active_user)],
        country_id: int = 241
    ):

    _result = get_country_state(env=env, country_id=country_id )

    return make_response(
        data=_result
    )
    

@router.get("/get-country-district")
async def country_district(
        env: Annotated[Environment, Depends(odoo_env)], 
        current_user: Annotated[dict, Depends(get_current_active_user)],
        state_id: int
    ):

    _result = get_country_district(env=env, state_id=state_id )

    return make_response(
        data=_result
    )

@router.get("/get-country-ward")
async def country_ward(
        env: Annotated[Environment, Depends(odoo_env)], 
        current_user: Annotated[dict, Depends(get_current_active_user)],
        district_id: int
    ):

    _result = get_country_ward(env=env, district_id=district_id )
    return make_response(
        data=_result
    )


@router.get("/get-contact-by-phone")
async def get_contact(
        env: Annotated[Environment, Depends(odoo_env)],
        current_user: Annotated[dict, Depends(get_current_active_user)],
        store_id: int, phone: str
    ):
    _contact_data = handle_get_contact(env, store_id=store_id, phone=phone)
    
    return make_response(
        data=_contact_data
    )

@router.post("/create-contact")
async def create_contact(
        env: Annotated[Environment, Depends(odoo_env)], contact_schema:ContactSchema,
        current_user: Annotated[dict, Depends(get_current_active_user)],
    ):
    
    _data = contact_schema.model_dump()
    result = handle_create_conract(env=env, contact_info=_data)
    if result == False:
        return make_response(msg='create customer failure!', status=0)

    return make_response(msg='success')

@router.post("/create-store-user")
async def create_store_user(
        env: Annotated[Environment, Depends(odoo_env)],
        contact_schema:ContactSchema
    ):

    return 'hello create user'

@router.get("/get-contact-by-store")
async def get_contact_by_store(
        env: Annotated[Environment, Depends(odoo_env)],
        current_user: Annotated[dict, Depends(get_current_active_user)],
        store_id: int, pageIndex: int = 1, pageSize: int = 10
    ):
    contact_data, total = handle_get_contact_by_store(env, store_id, pageIndex, pageSize)

    return make_response(
        data=contact_data,
        extend={
            'total': total
        },
        msg='success'
    )

def get_status_by_state_and_picking_type(state, picking_type_id):
    cases = {
        ("draft", 1): "Nháp",
        ("assigned", 1): "Chờ lấy hàng",
        ("done", 1): "Đã nhận hàng",
        ("draft", 2): "Hàng tới kho giao",
        ("assigned", 2): "Hàng đang giao",
        ("done", 2): "Giao thành công",
        ("cancel", 2): "Huỷ",
    }
    return cases.get((state, picking_type_id), "Khác")
@router.get("/report")
async def get_report(
        env: Annotated[Environment, Depends(odoo_env)],
        store_id : int,start_date : str , end_date : str
):
    try:
        print('get_report', store_id)
        print('data', start_date)
        print('date', end_date)
        query = """
            SELECT picking_type_id, state, COUNT(*) AS count, 
                   SUM(total_package_price) AS total_price,
                   SUM(total_price) AS total_ship
            FROM stock_picking 
            WHERE partner_id = %s  
                AND scheduled_date::date BETWEEN %s AND %s 
            GROUP BY picking_type_id, state
            ORDER BY picking_type_id;
        """
        print(query)
        env.cr.execute(query,(store_id,start_date,end_date))
        rows = env.cr.dictfetchall()
        reports = []
        for row in rows:
            _status = get_status_by_state_and_picking_type(
            row['state'],
            row['picking_type_id']
            )
            report_instance = ReportResponse(
                total_order =row['count'],
                total_price=row['total_price'],
                total_ship=row['total_ship'],
                status = _status
             )
            reports.append(report_instance)

        print('-----_response----', reports)
        if not reports:
            return make_response(
                msg="Khong co data",
                status=0
            )
    except Exception as e:
        print('-----_response----', e)
        make_response(
            msg=e,
            status=0
        )

    return make_response(
        msg="Aloooo",
        data=reports
    )

# dummy variables
# _name = 'stock.lot'
# picking_type_code = self.env.context.get('restricted_picking_type_code')   --- keywork find stock.picking

# _name = 'account.move' search account move