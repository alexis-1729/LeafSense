from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.schemas.security import TokenData
from dotenv import load_dotenv
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
load_dotenv()

def verify_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms= os.getenv("ALGORITHM"))
        sub: str = payload.get("sub")
        exp: int = payload.get("exp")
        rol: str = payload.get("role")

        if sub is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Token invalido: falta subject",
                headers = {"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(sub = sub, exp = exp, rol = rol)
    
    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token invalido",
            headers = {"WWW-Authenticate": "Bearer"},
        )