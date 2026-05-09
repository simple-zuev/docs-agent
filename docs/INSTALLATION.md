# Installation

## 1. Предпосылки

Нужны:
- macOS/Linux shell
- Python 3.12
- git
- доступ к Google APIs, используемым проектом

## 2. Локальная структура

Ожидаемый локальный путь:
~/AI/docs-agent

## 3. Создание виртуального окружения

Если окружение еще не создано:

python3.12 -m venv venv312
source venv312/bin/activate
pip install --upgrade pip
pip install -r requirements-py312.txt

## 4. Конфигурация

Локальный чувствительный контур:
- config/config.yml
- config/client_secret.json
- config/token.json

Эти файлы:
- обязательны для полноценной работы;
- не должны попадать в git;
- считаются локальными секретами.

## 5. Проверка установки

cd ~/AI/docs-agent
source venv312/bin/activate
bash scripts/operator_start.sh

Ожидаемый результат:
- doctor-lite возвращает healthy

## 6. Минимальная проверка

bash scripts/preflight_check.sh
python agent_cli.py status
python agent_cli.py f "DOC-0001"

## 7. Если что-то пошло не так

Смотри:
- docs/TROUBLESHOOTING.md
