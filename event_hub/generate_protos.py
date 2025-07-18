#!/usr/bin/env python3
"""
Скрипт для генерации Python файлов из .proto файлов
"""
import subprocess
import sys
import os

def generate_protos():
    """Генерирует Python файлы из .proto файлов"""
    proto_dir = "protos"
    output_dir = "protos"
    
    # Создаем директорию если её нет
    os.makedirs(output_dir, exist_ok=True)
    
    # Находим все .proto файлы
    proto_files = []
    for file in os.listdir(proto_dir):
        if file.endswith('.proto'):
            proto_files.append(os.path.join(proto_dir, file))
    
    if not proto_files:
        print("No .proto files found in protos/ directory")
        return
    
    # Генерируем Python файлы
    for proto_file in proto_files:
        print(f"Generating Python files from {proto_file}...")
        
        try:
            cmd = [
                sys.executable, "-m", "grpc_tools.protoc",
                f"--python_out={output_dir}",
                f"--grpc_python_out={output_dir}",
                f"--proto_path={proto_dir}",
                proto_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Successfully generated Python files from {proto_file}")
            else:
                print(f"Error generating files from {proto_file}:")
                print(result.stderr)
                
        except Exception as e:
            print(f"Error processing {proto_file}: {e}")

if __name__ == "__main__":
    generate_protos() 