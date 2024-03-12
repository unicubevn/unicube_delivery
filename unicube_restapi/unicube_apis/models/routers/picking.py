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
from ..schemas.order import OrderSchema
from ..schemas.receipt import ReceiptSchema
from .handlerespon import make_response

router = APIRouter()
