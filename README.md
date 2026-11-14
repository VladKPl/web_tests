# Automation Exercise UI

Проект Selenium + Pytest для Windows, Grid 4.25.0, Chrome/Firefox, Allure и xdist.
Запускайте команды из корня проекта в PowerShell.

## Подготовка Windows

1. Установите Python с https://www.python.org/downloads/windows/ (рекомендуется 3.11).
2. Проверьте версии: `py -0p`. В текущей среде использован установленный 3.13.
3. Установите Docker Desktop: https://www.docker.com/products/docker-desktop/ и запустите его.
4. Проверьте Engine: `docker version` и `docker info`.
5. Проверьте Compose: `docker compose version`.
6. Получите файлы проекта или клонируйте свой репозиторий; перейдите в его каталог.
7. Создайте окружение: `py -3.11 -m venv .venv`. Если 3.11 отсутствует, используйте установленную совместимую версию, например `py -3.13 -m venv .venv`. Существующее окружение не удаляйте.
8. Активируйте его: `.\.venv\Scripts\Activate.ps1`. Только при запрете выполнения: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, затем повторите активацию.
9. Установите зависимости:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
python -c "import sys,selenium,pytest; print(sys.executable, selenium.__version__, pytest.__version__)"
```

10. Подготовьте настройки: `Copy-Item .env.example .env` (не перезаписывайте существующий файл).
11. Изучите `docker-compose.yml`, выполните `docker compose config --quiet`. Используются только официальные образы Selenium 4.25.0.
12. Проверьте `docker compose ps -a`. Для существующих остановленных контейнеров используйте `docker compose start`; при первой установке — `docker compose up -d`. Работающие контейнеры не пересоздавайте. Остановка без удаления: `docker compose stop`; удаление контейнеров по необходимости: `docker compose down`.
13. Проверьте Hub и Nodes:

```powershell
docker compose ps
$status = Invoke-RestMethod http://localhost:4444/status
$status.value.ready
$status.value.nodes | ConvertTo-Json -Depth 8
Start-Process http://localhost:4444/ui
```

Ожидаются ready=true, два UP-узла со слотами chrome и firefox.
14. Chrome: `python -m pytest --browser chrome`.
15. Firefox: `python -m pytest --browser firefox`.
16. Группы:

```powershell
python -m pytest -m auth
python -m pytest -m cart
python -m pytest -m order
python -m pytest -m subscription
python -m pytest -m security
python -m pytest -m smoke
```

17. Параллельный запуск: `python -m pytest -n 2`. Каждый тест получает собственный браузер; Grid имеет один слот каждого браузера, поэтому два Chrome выполняются через очередь. UUID изолирует пользователей и файлы.
18. Allure: результаты сохраняются автоматически в `allure-results`. Установите Allure Commandline отдельно по https://allurereport.org/docs/install-for-windows/ (нужна Java). Проверьте `java -version` и `allure --version`.

```powershell
python -m pytest --alluredir=allure-results
allure serve allure-results
allure generate allure-results -o allure-report --clean
allure open allure-report
```

Для отдельных прогонов указывайте отдельный каталог, например `--alluredir=allure-results/chrome-final`, чтобы старые результаты не смешивались.
19. Реальные метрики операций автоматически сохраняются в `reports/metrics/*.csv` и `*.json`; JSON прикладывается к Allure. Поля: timestamp UTC, test_name, browser, operation, elapsed_ms, status, worker_id. Длительности вложенных операций не суммируются. Порогов производительности нет.
20. Диагностика падений: `reports/screenshots`, `reports/logs`, вложения Allure. В браузерных логах сохраняются только уровень и время, без тел запросов, заголовков и сообщений. Firefox может не поддерживать get_log — это отражено в файле. Консольные сообщения Pytest содержат результаты тестов.

## Браузеры и драйверы

В режиме `--mode remote` Chromium работает внутри selenium/node-chromium, Firefox — внутри selenium/node-firefox. Драйверы включены в образы, на Windows устанавливать ChromeDriver/GeckoDriver не нужно. Слоты и активные сессии видны в Dashboard.

Локальный режим:

1. Установите Chrome с https://www.google.com/chrome/ и Firefox с https://www.mozilla.org/firefox/new/.
2. Посмотрите версии в chrome://settings/help и about:support соответственно.
3. Активируйте .venv.
4. Выполните `python -m pytest tests/test_smoke.py --mode local --browser chrome` и аналогично с `--browser firefox`.
5. Selenium Manager подберёт драйвер; первый запуск требует сети. Глобальная установка драйверов не требуется. При ручной установке используйте совместимый драйвер в отдельном каталоге PATH текущего процесса.

Параметры: `--browser chrome|firefox`, `--mode remote|local`, `--url`, `--grid-url`, `--headless`. CLI имеет приоритет над .env. Неявное ожидание всегда 0; TIMEOUT задаёт явные ожидания.

## Архитектура

`src/config/settings.py` загружает .env. Корневой conftest создаёт function-scoped WebDriver и собирает диагностику. `src/pages` содержит Page Object; BasePage сохраняет явные ожидания из исходного архива, добавляет общие операции. Переходы возвращают объекты следующих страниц. SignupPage заполняет только демонстрационные данные. Методы страниц автоматически измеряются через perf_counter в src/metrics.py. Тесты сравнивают цены каталога с корзиной, без фиксированных цен. Каждый аккаунт имеет UUID-email; удаление выполняется после сценария.

## Git

Репозиторий локальный, GitHub не требуется. Установка Git: https://git-scm.com/downloads/win.

```powershell
git status
git add src tests conftest.py pytest.ini README.md requirements.txt .env.example docs
git commit -m "Update UI tests"
git log --oneline
```

.venv, .env и результаты исключены. Проект не публиковался.

## Частые ошибки

- Connection refused: проверьте Docker Desktop, compose ps и /status.
- Up без браузерных слотов: `docker compose logs chrome-node firefox-node selenium-hub`; проверьте Event Bus.
- PowerShell запрещает Activate: используйте Process ExecutionPolicy выше, не меняйте системную политику.
- No module named: проверьте sys.executable и установку через python -m pip.
- Session queue: один слот на браузер; уменьшите число работников или дождитесь освобождения.
- Firefox nssFailure2: соединение с публичным сайтом прервалось; сохраните диагностику и повторите конкретный тест. TLS-проверки не отключайте.
- Allure не найден: Python-плагин не устанавливает Commandline; установите CLI отдельно.
- Реклама или изменения DOM могут мешать взаимодействию; изучите скриншот и актуальную страницу. Тесты не скрывают элементы сайта для получения успешного результата.

См. docs/AUDIT.md и docs/STATUS.md для фактического состояния и ограничений.
