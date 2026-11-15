# Финальный аудит 15.11.2026

## Причина нестабильного добавления

DOM: `.product-image-wrapper > .single-products` содержит два соседних блока: `.productinfo` и `.product-overlay`. Ранее курсор наводился на `.productinfo`, которая перекрывается overlay, а кнопка хранилась как WebElement на всё время ожидания. Это приводило к потере hover и StaleElementReferenceException.

Исправление: выбор товара по `data-product-id`, наведение на `.single-products`, повторный поиск карточки и кнопки на каждом опросе. Проверяются видимость, enabled и доступность центра кнопки. Обновление DOM вызывает повтор наведения. Клик обычный WebDriver, после клика ожидается видимое модальное окно. Таймаут не увеличен, sleep и JS-click не используются.

## Остальные исправления

- ProductDetailPage и CheckoutPage непосредственно наследуют BasePage. Поведение модального окна и таблицы переиспользуется через mixin-компоненты `components.py`.
- Проверка Checkout ждёт фактический `h2` с текстом `Review Your Order`. Локатор проверен успешными TC14/15.
- Прямые клики навигации и удаления заменены на BasePage.click с явным ожиданием.
- Названия/цены каталога читаются из textContent: hover может скрыть базовую копию карточки, но её данные не меняются.
- Отложенный privacy-диалог обрабатывается в ожиданиях видимости/кликабельности и при наведении. Используются Manage options → Confirm choices.
- Общий клик повторно находит элемент, прокручивает в центр и наводит курсор перед настоящим нажатием. Это устраняет подтверждённое перекрытие кнопки создания аккаунта всплывающей панелью privacy. Неизвестное постоянное перекрытие не считается успешным кликом.
- Полноэкранная реклама воспроизведена: iframe содержит `#dismiss-button`, aria-label `Close ad`. При `#google_vignette` используется обычный клик этой кнопки.
- README нормализован в UTF-8, указана ссылка текущего GitHub-репозитория, описана локальная установка CLI. Повреждённых символов U+FFFD и фрагментов `???` в README не обнаружено.
- Allure CLI, .venv и .env уже не отслеживались Git. 242 ранее отслеживаемых файла метрик убраны только из индекса; локальные файлы сохранены. Дополнены правила .gitignore.

## Фактические проверки

- Три исходных проблемных сценария прошли: TC14 Chrome (27.28 s), remove_and_continue Chrome (12.59 s), TC15 Firefox (23.97 s).
- После обработки рекламы повтор remove_and_continue, catalog_detail и TC14 Chrome: 3 passed (57.62 s). Повтор TC15 Firefox: 1 passed (46.60 s).
- Отдельная регистрация Firefox после обработки отложенного диалога: 1 passed (29.90 s).
- collect-only: 25 экземпляров; импорты src, прямое наследование и pip check успешны.
- test_reporting и test_diagnostics: 2 passed. Контрольный пароль исключён из logging/traceback/Allure в setup, call, teardown.
- Реальные сбои аудита создали PNG и вложения browser/performance. Firefox сообщает unavailable для неподдерживаемого get_log. Проверены метрики CSV/JSON и шаги. Новые JSON проверены на отсутствие открытых параметров password.

Промежуточные неудачные прогоны сохранены отдельно и не объявляются успешными.

## Окончательные результаты

| Проверка | Фактический результат |
|---|---|
| Полный Chrome | **25 passed**, 381.99 s; exit 0 |
| Полный Firefox | **25 passed**, 404.04 s; exit 0 |
| Collect-only | 25 test instances |
| Импорты src и прямое наследование | Успешно |
| pip check / compileall / git diff --check | Успешно |
| Allure generate Chrome / Firefox | Оба HTML-отчёта успешно сформированы |
| Проверка result.json | По 25 passed, без broken/failed |
| Метрики в новых Allure | По 23 JSON-вложения для UI-тестов; unit-тесты не создают браузер |
| Чувствительные параметры | Открытых параметров password в новых JSON не найдено; тест очистки контрольного секрета прошёл |

Артефакты: `allure-results/final-verified-chrome`, `allure-results/final-verified-firefox`; HTML `allure-report` (Chrome) и `allure-report/firefox`.

Просмотр:

```powershell
.\tools\allure-2.32.0\bin\allure.bat open allure-report --host 127.0.0.1 --port 8765
```

Chrome: http://127.0.0.1:8765/ ; Firefox: http://127.0.0.1:8765/firefox/ .

## Подготовленные файлы

Изменены `.gitignore`, `README.md`, `docs/REQUIREMENTS.md`, `docs/STATUS.md`, `src/pages/BasePage.py`, `CartPage.py`, `CheckoutPage.py`, `MainPage.py`, `ProductDetailPage.py`, `ProductsPage.py`.
Добавлены `src/pages/components.py`, `docs/FINAL_AUDIT.md`.
Из индекса исключены 242 файла `reports/metrics/*`, но они сохранены локально. Архив и каталог Allure CLI уже отсутствовали в индексе; история Git не переписывалась.

Для просмотра: `git diff --cached` и `git diff`. Автоматические commit/push не выполнялись.

## Ограничения

Сторонние реклама и privacy-диалоги могут менять разметку. Неизвестные перекрытия приводят к диагностируемой ошибке. При недоступном сайте удаление аккаунта невозможно гарантировать; ошибка teardown видима. UI-проверки не являются полным аудитом безопасности.

Git push не выполнялся. Изменения подготовлены локально для просмотра пользователем. Удаление из индекса не переписывает историю Git.
