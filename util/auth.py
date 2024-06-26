import secrets
from typing import Optional
import bcrypt
from fastapi import HTTPException, Request, status
from models.cliente_model import Cliente
from repositories.cliente_repo import ClienteRepo
from util.cookies import NOME_COOKIE_AUTH, adicionar_cookie_auth


async def obter_cliente_logado(request: Request) -> Optional[Cliente]:
    try:
        token = request.cookies[NOME_COOKIE_AUTH]
        print(f"Token: {token}")  # Debug statement
        if token.strip() == "":
            return None
        cliente = ClienteRepo.obter_por_token(token)
        print(f"Cliente from Token: {cliente}")  # Debug statement

        return cliente
    except KeyError:
        return None


async def middleware_autenticacao(request: Request, call_next):
    cliente = await obter_cliente_logado(request)
    print(f"Authenticated Cliente: {cliente}") 
    request.state.cliente = cliente
    response = await call_next(request)
    if response.status_code == status.HTTP_303_SEE_OTHER:
        return response
    if cliente:
        token = request.cookies[NOME_COOKIE_AUTH]
        adicionar_cookie_auth(response, token)
    return response


def obter_hash_senha(senha: str) -> str:
    try:
        hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
        return hashed.decode()
    except ValueError:
        return ""


def conferir_senha(senha: str, hash_senha: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), hash_senha.encode())
    except ValueError:
        return False


def gerar_token(length: int = 32) -> str:
    try:
        return secrets.token_hex(length)
    except ValueError:
        return ""


def checar_autorizacao(request: Request):
    if not request.state.cliente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
