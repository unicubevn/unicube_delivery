from pydantic import BaseModel

class LogoutSchema(BaseModel):
    acces_token: str
