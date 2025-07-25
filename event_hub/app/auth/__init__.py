"""
Модуль авторизации Event Hub
"""

from .jwt_auth import (
    get_current_user,
    require_writer_role,
    require_reader_role,
    GRPCAuthInterceptor,
    require_graphql_auth,
    JWTAuthError
)

__all__ = [
    'get_current_user',
    'require_writer_role', 
    'require_reader_role',
    'GRPCAuthInterceptor',
    'require_graphql_auth',
    'JWTAuthError'
] 