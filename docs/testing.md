# Проверки и работа с тестами

Существующие тестовые модули unittest перечислены в [индексе сценариев](reference/tests.md), который
ссылается на каждую существующую тестовую функцию. Производственные определения
и тесты связаны также в [справочнике модулей](reference/README.md).

## Основной запуск

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Запускай из корня проекта существующим интерпретатором окружения с requirements.txt.
Тесты используют TemporaryDirectory и подменённые обнаружение, PhotoKit и HTTP;
они не должны направляться в рабочие каталоги. Импорт app создаёт базы, поэтому
API-fixture задают MEDIA_ACTU_DATA_DIR до импорта/перезагрузки.
`--lifespan off` не отменяет действия импорта.

Для одной проверки удобно добавить tests в PYTHONPATH:

```sh
PYTHONPATH=tests .venv/bin/python -m unittest -v test_copy_sources
```

## Карта покрытия

| Файл | Проверяемая область | Именованных test-методов |
| --- | --- | --- |
| [test_catalog.py](../tests/test_catalog.py) | Медиаиндекс, очередь и версии превью | 7 |
| [test_comparison.py](../tests/test_comparison.py) | Общая сверка имён и совместимость отчётов | 25 |
| [test_comparison_tree_ui.py](../tests/test_comparison_tree_ui.py) | Дерево найденных путей и пагинация | 4 |
| [test_copies.py](../tests/test_copies.py) | Наборы папок, нумерация и пересечения | 16 |
| [test_copy_connections.py](../tests/test_copy_connections.py) | Подключение и отключение связей | 12 |
| [test_copy_files.py](../tests/test_copy_files.py) | Планы, запись, гонки и незавершённые копии | 24 |
| [test_copy_number_release.py](../tests/test_copy_number_release.py) | Освобождение номеров и история привязок | 14 |
| [test_copy_sandbox.py](../tests/test_copy_sandbox.py) | Запрет записи существующих оригиналов в sandbox | 4 |
| [test_copy_sources.py](../tests/test_copy_sources.py) | Выбор источников и запрет циклов обычных копий | 5 |
| [test_directory_sizes.py](../tests/test_directory_sizes.py) | Размеры, частичность, stale и UI-подписи | 18 |
| [test_documentation.py](../tests/test_documentation.py) | Смысловая генерация, сдвиги строк, контракты и ссылки | 13 |
| [test_folder_markers.py](../tests/test_folder_markers.py) | Принадлежность, публикация и повтор маркеров папок | 15 |
| [test_folder_tags.py](../tests/test_folder_tags.py) | Пользовательские метки папок | 8 |
| [test_folder_tracking.py](../tests/test_folder_tracking.py) | Watchdog и подтверждение изменений | 7 |
| [test_network.py](../tests/test_network.py) | Bonjour, ресурсы SMB и ошибки | 16 |
| [test_paired_comparison.py](../tests/test_paired_comparison.py) | Выровненная структура, размеры и SHA-256 | 15 |
| [test_paired_workspace.py](../tests/test_paired_workspace.py) | Связанные панели, просмотр и история | 21 |
| [test_photo_copy_roles.py](../tests/test_photo_copy_roles.py) | Метки привязанных копий Photos | 4 |
| [test_photo_libraries.py](../tests/test_photo_libraries.py) | Идентичность и профили медиатек | 12 |
| [test_photos_adapter.py](../tests/test_photos_adapter.py) | NDJSON, Unix-сокет, отмена и границы блоков | 8 |
| [test_photos_browser.py](../tests/test_photos_browser.py) | Годы/месяцы, страницы и виртуальные ID | 4 |
| [test_photos_copy_chain.py](../tests/test_photos_copy_chain.py) | Источники Photos, квитанции и цепочки копий | 9 |
| [test_photos_originals.py](../tests/test_photos_originals.py) | Прямая запись, версии, продолжение и частичные ресурсы | 30 |
| [test_photos_schedule.py](../tests/test_photos_schedule.py) | Окна времени, повторные запросы и ручная пауза | 16 |
| [test_refresh_renamed_folder.py](../tests/test_refresh_renamed_folder.py) | Обновление переименованной области UI | 6 |
| [test_scanner.py](../tests/test_scanner.py) | Рекурсивный обход и ошибки обычного источника | 3 |
| [test_service_runtime.py](../tests/test_service_runtime.py) | Ротация журналов и отказ потока | 4 |
| [test_sidebar_state.py](../tests/test_sidebar_state.py) | Сохранение раскрытия боковых секций | 5 |
| [test_storage.py](../tests/test_storage.py) | Снимки, отключение и метаданные томов | 16 |
| [test_storage_previews.py](../tests/test_storage_previews.py) | Производные JPEG, видео и режим превью | 9 |
| [test_thumbnails.py](../tests/test_thumbnails.py) | Версии кэша, ориентация и генерация фото | 3 |
| [test_tree_keyboard.py](../tests/test_tree_keyboard.py) | Выделение, фокус и клавиатурная навигация | 7 |
| [test_ui_connection.py](../tests/test_ui_connection.py) | Повторное использование HTTP-пула | 1 |
| [test_volume_identity.py](../tests/test_volume_identity.py) | Маркеры, смена носителя и ёмкость | 18 |
| [test_workspace_photos.py](../tests/test_workspace_photos.py) | Виртуальные медиатеки в общих панелях | 2 |
| [test_workspace_refresh.py](../tests/test_workspace_refresh.py) | Обновление UI без потери дерева | 4 |
| [test_workspace_state.py](../tests/test_workspace_state.py) | Нормализация и восстановление состояния вкладки | 8 |

## Границы среды

Socket-тест GUI-адаптера запускает **поддельный локальный helper**, а не настоящую
системную медиатеку. Для него нужен разрешённый AF_UNIX bind/connect. Видеопроверка
строит временный fixture FFmpeg, затем проверяет нативный macOS fallback; ему нужен
работающий AVFoundation. Sandbox-тесты запускают sandbox-exec и проверяют реальные
ограничения файловых операций на временных файлах. В ограниченном окружении часть
таких проверок может пропускаться либо падать из-за системных прав.

Успешный unit-прогон не подтверждает выданное разрешение Photos на M4, текущий
Apple ID, наличие нужного носителя, целостность пользовательских оригиналов или
настройку Launcher на другой машине. Эти состояния не проверялись данной задачей.

## Проверка документационных изменений

1. Пересобрать `.venv/bin/python scripts/build_documentation.py` и запустить ту же
   команду с `--check` для сравнения смыслового результата и проверки устойчивых ссылок.
2. Проверить покрытие именованных определений двухстрочными помеченными пояснениями,
   включая сам генератор. Обычные комментарии не заменяют строки пояснения.
3. Проверить, что изменение Python оставляет AST неизменным; отдельно сравнить
   токены нативного кода и JavaScript после исключения комментариев.
4. Выполнить синтаксические проверки нативных исходников и полный unittest.
5. Проверить git diff --check, версии продукта/документации и отсутствие удаления старого кода.

Результат текущего прохода, особенности первого запуска в sandbox и итоговая
проверка: [протокол валидации](validation.md).
