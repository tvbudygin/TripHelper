"""Запуск бэкенда и фронтенда одной командой"""

import http.client
import os
import shutil
import subprocess
import sys
import time

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
LOGS_DIR = os.path.join(PROJECT_DIR, "logs")

BACKEND_PORT = 8000
FRONTEND_PORT = 5173
STARTUP_TIMEOUT_SECONDS = 30


def start_process(command, cwd, log_path):
    """Запускает процесс в фоне, весь вывод пишется в файле лога"""

    log_file = open(log_path, "w", encoding="utf-8")
    return subprocess.Popen(command, cwd=cwd, stdout=log_file, stderr=subprocess.STDOUT)


def wait_for_port(port, timeout_seconds):
    """Ждёт, пока сервер на порту начнёт отвечать"""

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            connection = http.client.HTTPConnection("localhost", port, timeout=1)
            connection.request("GET", "/")
            connection.close()
            return True
        except OSError:
            time.sleep(0.5)
    return False


def print_summary():
    """print ссылки на сайт и документацию"""

    print("\nTripHelper запущен")
    print(f"  Сайт (бэкенд + собранный фронтенд, если он собран): http://localhost:{BACKEND_PORT}")
    print(f"  Фронтенд для разработки (hot-reload):               http://localhost:{FRONTEND_PORT}")
    print(f"  Документация API:                                   http://localhost:{BACKEND_PORT}/docs")
    print(f"  Логи backend/frontend лежат в папке:                {LOGS_DIR}")
    print("\nCtrl+C — остановить\n", flush=True)


def main():
    os.makedirs(LOGS_DIR, exist_ok=True)
    npm_path = shutil.which("npm") or "npm"

    backend = start_process(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)],
        PROJECT_DIR,
        os.path.join(LOGS_DIR, "backend.log"),
    )
    frontend = start_process(
        [npm_path, "run", "dev"],
        FRONTEND_DIR,
        os.path.join(LOGS_DIR, "frontend.log"),
    )

    if not wait_for_port(BACKEND_PORT, STARTUP_TIMEOUT_SECONDS):
        print(f"Бэкенд не поднялся за {STARTUP_TIMEOUT_SECONDS} секунд", flush=True)
    if not wait_for_port(FRONTEND_PORT, STARTUP_TIMEOUT_SECONDS):
        print(f"Фронтенд не поднялся за {STARTUP_TIMEOUT_SECONDS} секунд", flush=True)

    print_summary()

    try:
        while backend.poll() is None and frontend.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        backend.terminate()
        frontend.terminate()


if __name__ == "__main__":
    main()
