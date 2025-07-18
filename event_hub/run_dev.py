#!/usr/bin/env python3
"""
Скрипт для запуска всех сервисов Event Hub в режиме разработки
"""
import asyncio
import subprocess
import sys
import os
import signal
import time
from typing import List

class DevRunner:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = True
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        print("\n🛑 Получен сигнал завершения, останавливаю сервисы...")
        self.running = False
        self.stop_all()
        sys.exit(0)
    
    def start_redis(self):
        """Запускает Redis"""
        print("🔴 Запуск Redis...")
        process = subprocess.Popen(
            ["docker", "run", "--rm", "-p", "6379:6379", "--name", "event-hub-redis", "redis:7"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.processes.append(process)
        time.sleep(2)  # Даем время Redis запуститься
        print("✅ Redis запущен на порту 6379")
    
    def start_mongo(self):
        """Запускает MongoDB"""
        print("🟢 Запуск MongoDB...")
        process = subprocess.Popen(
            ["docker", "run", "--rm", "-p", "27017:27017", "--name", "event-hub-mongo", "mongo:6"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.processes.append(process)
        time.sleep(3)  # Даем время MongoDB запуститься
        print("✅ MongoDB запущен на порту 27017")
    
    def start_fastapi(self):
        """Запускает FastAPI сервер"""
        print("🚀 Запуск FastAPI сервера...")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
        self.processes.append(process)
        print("✅ FastAPI запущен на порту 8000")
    
    def start_grpc(self):
        """Запускает gRPC сервер"""
        print("🔧 Запуск gRPC сервера...")
        process = subprocess.Popen([
            sys.executable, "-m", "app.grpc.server"
        ])
        self.processes.append(process)
        print("✅ gRPC сервер запущен на порту 50051")
    
    def start_consumer(self):
        """Запускает consumer метрик"""
        print("📊 Запуск consumer метрик...")
        process = subprocess.Popen([
            sys.executable, "-m", "consumer.metrics_consumer"
        ])
        self.processes.append(process)
        print("✅ Consumer метрик запущен")
    
    def generate_protos(self):
        """Генерирует protobuf файлы"""
        print("📝 Генерация protobuf файлов...")
        try:
            subprocess.run([sys.executable, "generate_protos.py"], check=True)
            print("✅ Protobuf файлы сгенерированы")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Ошибка генерации protobuf: {e}")
    
    def stop_all(self):
        """Останавливает все процессы"""
        print("🛑 Остановка всех сервисов...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Ошибка остановки процесса: {e}")
        
        # Останавливаем Docker контейнеры
        try:
            subprocess.run(["docker", "stop", "event-hub-redis"], check=False)
            subprocess.run(["docker", "stop", "event-hub-mongo"], check=False)
        except Exception as e:
            print(f"Ошибка остановки Docker контейнеров: {e}")
        
        print("✅ Все сервисы остановлены")
    
    def run(self):
        """Основной метод запуска"""
        print("🎯 Event Hub - Запуск в режиме разработки")
        print("=" * 50)
        
        # Регистрируем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Генерируем protobuf файлы
            self.generate_protos()
            
            # Запускаем инфраструктурные сервисы
            self.start_redis()
            self.start_mongo()
            
            # Даем время сервисам запуститься
            time.sleep(2)
            
            # Запускаем приложения
            self.start_fastapi()
            time.sleep(1)
            self.start_grpc()
            time.sleep(1)
            self.start_consumer()
            
            print("\n🎉 Все сервисы запущены!")
            print("📱 Доступные сервисы:")
            print("   • FastAPI + GraphQL: http://localhost:8000")
            print("   • GraphQL Playground: http://localhost:8000/graphql")
            print("   • API Docs: http://localhost:8000/docs")
            print("   • gRPC: localhost:50051")
            print("   • MongoDB: localhost:27017")
            print("   • Redis: localhost:6379")
            print("\n💡 Для остановки нажмите Ctrl+C")
            
            # Ждем завершения
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал прерывания")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            self.stop_all()

if __name__ == "__main__":
    runner = DevRunner()
    runner.run() 