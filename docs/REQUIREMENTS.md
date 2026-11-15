# Матрица требований

Статус «реализовано» означает наличие кода; подтверждение последней версии — только результаты финальных прогонов в STATUS.md. Исторические успешные прогоны не подменяют новую проверку.

| Требование ТЗ / UPD | Реализация | Проверка / ограничение |
|---|---|---|
| Аудит tests.zip и Compose | docs/AUDIT.md | Исходный архив сохранён, исправлены импорты |
| Задание 1: Hub + Chrome + Firefox, 4.25.0 | docker-compose.yml | Официальные образы, shm 2gb, Event Bus; без ненужных изменений |
| Python, venv, зависимости | .venv, requirements.txt | Python 3.13 вместо отсутствующего 3.11; отдельная tools/clean-venv успешно установлена |
| Конфигурация и приоритет CLI | src/config/settings.py, conftest.py | --browser, --url, --grid-url, --mode, --local, --remote; конфликт local/remote отклоняется |
| function-scoped WebDriver, quit, implicit=0 | conftest.py | Все UI-тесты; local smoke Chrome/Firefox проверены ранее |
| Задание 2: маркеры, логирование, xdist | pytest.ini, conftest.py | Групповые прогоны и финальный параллельный прогон |
| Задания 3 и 5: BasePage и наследование | src/pages/*.py | Все страницы непосредственно наследуют BasePage; общие modal/table операции в components.py |
| find/find_all, presence/visible/clickable | BasePage | Используются UI-сценариями |
| click, input, text, attributes, scroll, hover | BasePage | Используются страницами; значения ввода не декорируются Allure |
| script, current URL, URL wait | BasePage | Валидация форм и переходы |
| Fluent Interface и локальные импорты | src/pages | Переходы возвращают целевые страницы |
| Главная, навигация, подписка | MainPage, BasePage.subscribe | smoke, TC10, TC11 |
| Вход, регистрация, ошибки | LoginPage | TC1–5 |
| Полная регистрационная форма | SignupPage | TC1/14/15, безопасные поля; Mr/Mrs и адрес доступны через user |
| ACCOUNT CREATED / DELETED, Continue | AccountCreatedPage, AccountDeletedPage | Точные сообщения и ожидание главной страницы |
| Каталог, названия/цены, hover, add | ProductsPage | TC12; цены берутся из DOM |
| Открытие карточки из каталога | ProductsPage.open_product | Метод реализован; отдельный сценарий проверяет цепочку |
| Карточка, цена, количество | ProductDetailPage | TC13 |
| Корзина: товары, цены, qty, total | CartPage.items | TC12/13 и сравнение заказа |
| Удаление и продолжение покупок | CartPage | test_remove_and_continue |
| Checkout: адреса, заказ, комментарий | CheckoutPage | TC14/15; фиксированный демонстрационный адрес |
| Payment: поля и подтверждение | PaymentPage | TC14/15; фактический текст отличается от старого ТЗ |
| Задание 4: TC1–5 | tests/test_auth.py | Независимые пользователи, очистка |
| Задание 6: TC12–15 | tests/test_cart_order.py | Разная последовательность регистрации TC14/15 |
| Дополнительные TC10/11 | tests/test_subscription.py | Подписка главной и корзины |
| Задание 7: Allure labels/steps/attachments | conftest.py, pages | HTML ранее сформирован и открыт в Firefox |
| Скриншоты и доступные логи | conftest.py, diagnostics.py | Реальные падения; Firefox get_log имеет явный fallback |
| Безопасность диагностики | secrets.py, diagnostics.py | test_reporting: setup/call/teardown с контрольным паролем; test_diagnostics: секреты в HTTP-данных |
| Изоляция пользователей и артефактов | UUID, function driver, Metrics | xdist; нет общих изменяемых файлов метрик |
| Очистка после сбоя регистрации | driver finalizer, pending_account | test_cleanup_after_registration_check_failure; сеть может сделать очистку невозможной |
| Метрики perf_counter и CSV/JSON | src/metrics.py | Реальные операции и статусы; без порогов; вложенные интервалы не суммируются |
| Границы операций включают ожидания | MainPage, LoginPage, CheckoutPage и др. | Целевые элементы ожидаются до возврата объекта |
| Время отклика регистрационной формы | SignupPage.register_user | Отдельная метрика registration_response: от click CREATE до ACCOUNT CREATED |
| Диалог privacy | BasePage.dismiss_consent | Manage options → Confirm choices, без удаления DOM; smoke проверен |
| Новый кейс: неверный email | LoginPage.verify_invalid_signup | test_registration_validation, HTML validity и сообщение |
| Безопасные обязательные поля | SignupPage.verify_required_fields | test_password_field |
| Спецсимволы и границы имени | test_name_roundtrip | Апостроф, дефис, 1 и 100 символов; без атакующих payload |
| README Windows, Git, .env | README.md, .gitignore, .env.example | Команды соответствуют CLI; публичной публикации нет |
| Итоговая передача | STATUS.md, REQUIREMENTS.md | Файлы проекта и реальные артефакты в рабочей папке |

## Обоснованные ограничения

- Firefox browser/performance get_log не поддерживается используемым драйвером: записывается unavailable, данные не имитируются.
- Произвольный текст консоли не сохраняется: он может содержать неизвестные секреты. Для диагностики доступны source/level/time и сетевые метаданные Chrome.
- Проверки UI не доказывают серверную защищённость. Проверяется штатная валидация браузера и отсутствие технических ошибок в ожидаемых сценариях.
- Очистка аккаунта требует доступного сайта и сессии. Неудача очистки отмечается ошибкой teardown.
- Поле email полной формы заполняется первым шагом регистрации; не обходится read-only состояние поля.
- CLI Allure локален (tools), а не установлен глобально; просмотр привязан к 127.0.0.1.
