"""Запуск всего проекта — бэкенд и фронтенд"""

import subprocess
import sys
import os
import time


def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_dir, "frontend")

    print("Запускается TripHelper...")

    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    frontend = subprocess.Popen(
        ["/usr/local/bin/npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    time.sleep(3)

    print("\n" + "=" * 40)
    print("  TripHelper запущен!")
    print("=" * 40)
    print(f"  Фронтенд:  http://localhost:5173")
    print(f"  Бэкенд:   http://localhost:8000")
    print(f"  Документация API: http://localhost:8000/docs")
    print("=" * 40)
    print("\nНажми Ctrl+C чтобы остановить\n")

    while True:
        line = backend.stdout.readline().decode(errors="replace")
        if line:
            print(f"[backend] {line.strip()}")
        line2 = frontend.stdout.readline().decode(errors="replace")
        if line2:
            print(f"[frontend] {line2.strip()}")

        if backend.poll() is not None or frontend.poll() is not None:
            break

    backend.terminate()
    frontend.terminate()


if __name__ == "__main__":
    main()
