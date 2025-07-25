"""
JWT авторизация для Event Hub
"""

import jwt
import functools
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from grpc import RpcError, StatusCode
import grpc
from graphql import GraphQLError

# Публичный ключ для проверки токенов
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCgcy6eldO
Tm8kVRG5D9guHoZal6BUMVT7UdVGOAKlxotIYzOtTfIC7JgtYub/KCkL1+h4DAGJ
r9LXDDQuF8/Oluq4rVQFCbOKi0dUJQ++Z3WaBxLclAdI8OI3M06gVGW1yT1M+Sbk
I15YK19Xz/0p3YC/EELFs0XoTETwwOhFeX9iDtHqiEvIdz4LSFJamaid4DbNtAsb
8cCt7eQp7C7dozysjdcD0LxXf5k7Ch+GIWxOC2q4Nu/XTFZh17e2usM1bXFQIeE3
IMHPrgxxPqXEVbHZX1Cm/c+nqo+E60VJFPdqifZccpY2lUfUKmagdcBczwIDAQAB
-----END PUBLIC KEY-----"""

security = HTTPBearer()

class JWTAuthError(Exception):
    """Ошибка JWT авторизации"""
    pass

def verify_token(token: str) -> Dict[str, Any]:
    """Проверяет JWT токен и возвращает payload"""
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=['RS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise JWTAuthError("Токен истек")
    except jwt.InvalidTokenError:
        raise JWTAuthError("Недействительный токен")

def require_role(required_role: str):
    """Декоратор для проверки роли пользователя"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем токен из контекста
            token = kwargs.get('token')
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Токен не предоставлен"
                )
            
            try:
                payload = verify_token(token)
                user_role = payload.get('role')
                
                if user_role != required_role:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Недостаточно прав. Требуется роль: {required_role}"
                    )
                
                return await func(*args, **kwargs)
            except JWTAuthError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e)
                )
        
        return wrapper
    return decorator

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Получает текущего пользователя из JWT токена"""
    try:
        payload = verify_token(credentials.credentials)
        return payload
    except JWTAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

def require_writer_role():
    """Декоратор для проверки роли writer"""
    return require_role('writer')

def require_reader_role():
    """Декоратор для проверки роли reader"""
    return require_role('reader')

# gRPC авторизация
class GRPCAuthInterceptor(grpc.aio.ServicerContext):
    """gRPC интерцептор для авторизации"""
    
    def __init__(self, servicer_context: grpc.aio.ServicerContext):
        self._servicer_context = servicer_context
        self._metadata = servicer_context.invocation_metadata()
    
    def get_token(self) -> Optional[str]:
        """Извлекает токен из метаданных gRPC"""
        for key, value in self._metadata:
            if key == 'authorization':
                if value.startswith('Bearer '):
                    return value[7:]
        return None
    
    def verify_grpc_auth(self, required_role: str = None):
        """Проверяет авторизацию для gRPC"""
        token = self.get_token()
        if not token:
            raise RpcError(StatusCode.UNAUTHENTICATED, "Токен не предоставлен")
        
        try:
            payload = verify_token(token)
            if required_role and payload.get('role') != required_role:
                raise RpcError(StatusCode.PERMISSION_DENIED, f"Недостаточно прав. Требуется роль: {required_role}")
            return payload
        except JWTAuthError as e:
            raise RpcError(StatusCode.UNAUTHENTICATED, str(e))

# GraphQL авторизация
def get_graphql_user(info) -> Optional[Dict[str, Any]]:
    """Получает пользователя из GraphQL контекста"""
    request = info.context.get('request')
    if not request:
        return None
    
    auth_header = request.headers.get('authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header[7:]
    try:
        return verify_token(token)
    except JWTAuthError:
        return None

def require_graphql_auth(required_role: str = None):
    """Декоратор для GraphQL авторизации"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            info = kwargs.get('info') or args[-1] if args else None
            if not info:
                raise GraphQLError("Информация о запросе недоступна")
            
            user = get_graphql_user(info)
            if not user:
                raise GraphQLError("Требуется авторизация", extensions={'code': 'UNAUTHENTICATED'})
            
            if required_role and user.get('role') != required_role:
                raise GraphQLError("Недостаточно прав", extensions={'code': 'FORBIDDEN'})
            
            return func(*args, **kwargs)
        return wrapper
    return decorator 