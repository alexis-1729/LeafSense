from pydantic import BaseModel

class TokenData(BaseModel):
    sub : str | None = None
    exp : str | None = None
    rol :  str | None = None