#!/usr/bin/env python3
"""
Утилита для выпуска JWT токенов для тестирования авторизации
"""

import jwt
import datetime
import argparse
from typing import Dict, Any

# Секретный ключ для подписи токенов (в продакшене должен быть в переменных окружения)
SECRET_KEY = "your-secret-key-for-event-hub-jwt-signing"

def create_token(user_id: str, role: str, expires_in_hours: int = 24) -> str:
    """Создает JWT токен с указанной ролью"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours),
        'iat': datetime.datetime.utcnow(),
        'iss': 'event_hub'
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def create_expired_token(user_id: str, role: str) -> str:
    """Создает просроченный JWT токен"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow() - datetime.timedelta(hours=2),
        'iss': 'event_hub'
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def main():
    parser = argparse.ArgumentParser(description='Выпуск JWT токенов для тестирования')
    parser.add_argument('--user-id', default='test_user', help='ID пользователя')
    parser.add_argument('--role', choices=['reader', 'writer'], required=True, help='Роль пользователя')
    parser.add_argument('--expired', action='store_true', help='Создать просроченный токен')
    parser.add_argument('--hours', type=int, default=24, help='Время жизни токена в часах')
    
    args = parser.parse_args()
    
    if args.expired:
        token = create_expired_token(args.user_id, args.role)
        print(f"🔴 Просроченный токен для {args.role}:")
    else:
        token = create_token(args.user_id, args.role, args.hours)
        print(f"🟢 Валидный токен для {args.role}:")
    
    print(f"Authorization: Bearer {token}")
    print(f"\nДля тестирования:")
    print(f"curl -H 'Authorization: Bearer {token}' http://localhost:8000/api/events")

if __name__ == '__main__':
    main() 