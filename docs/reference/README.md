# Справочник реализации

Проверено по исходникам 2026-11-03. Все ссылки ведут к строкам текущего дерева после добавления комментариев.

Справочник охватывает все 37 Python-модулей, 71 класс и 733 именованных определения функций и методов, включая вложенные обработчики. Наличие определения здесь не означает, что оно вызывается в текущем UI: статусы старых частей вынесены в [реестр](../legacy.md).

В каждом разделе указаны точная сигнатура, назначение, наблюдаемые операции, прямые вызовы и обработка исключений. Списки вызовов получены статическим разбором тела без тел вложенных функций; они не заменяют трассировку исполнения. Неаннотированные типы не угадываются. Исключения внешних библиотек могут проходить транзитом, поэтому список явных raise не является полным контрактом ошибок.

| Модуль | Назначение | Классы / функции |
| --- | --- | --- |
| [app.py](app.md) | Core API и жизненный цикл | 26 / 97 |
| [comparison_tree_ui.py](comparison_tree_ui.md) | UI найденных путей | 1 / 13 |
| [comparison_ui.py](comparison_ui.md) | Совместимость адреса /compare | 0 / 2 |
| [copy_groups_ui.py](copy_groups_ui.md) | UI наборов копий | 1 / 32 |
| [media_manager/__init__.py](media_manager--__init__.md) | Пакет Core | 0 / 0 |
| [media_manager/catalog.py](media_manager--catalog.md) | Медиаиндекс и очередь превью | 1 / 34 |
| [media_manager/comparison.py](media_manager--comparison.md) | Поиск совпадений по именам | 2 / 25 |
| [media_manager/copies.py](media_manager--copies.md) | Учёт основных папок и копий | 1 / 26 |
| [media_manager/copy_files.py](media_manager--copy_files.md) | Копирование отсутствующего | 3 / 25 |
| [media_manager/directory_sizes.py](media_manager--directory_sizes.md) | Размеры папок | 1 / 6 |
| [media_manager/folder_markers.py](media_manager--folder_markers.md) | Служебные описания папок | 1 / 15 |
| [media_manager/folder_tracking.py](media_manager--folder_tracking.md) | Отслеживание основных папок | 2 / 11 |
| [media_manager/network.py](media_manager--network.md) | Обнаружение NAS | 2 / 16 |
| [media_manager/paired_comparison.py](media_manager--paired_comparison.md) | Сверка связанных папок | 1 / 23 |
| [media_manager/photo_libraries.py](media_manager--photo_libraries.md) | Профили медиатек Photos | 1 / 24 |
| [media_manager/photos_adapter.py](media_manager--photos_adapter.md) | Python-клиент PhotoKit | 7 / 25 |
| [media_manager/photos_browser.py](media_manager--photos_browser.md) | Виртуальное дерево Photos | 1 / 4 |
| [media_manager/photos_originals.py](media_manager--photos_originals.md) | Сохранение оригиналов Photos | 1 / 40 |
| [media_manager/photos_schedule.py](media_manager--photos_schedule.md) | Окна синхронизации Photos | 1 / 20 |
| [media_manager/sandbox_rules.py](media_manager--sandbox_rules.md) | Правила sandbox | 0 / 3 |
| [media_manager/scanner.py](media_manager--scanner.md) | Сканирование обычных источников | 3 / 10 |
| [media_manager/service_runtime.py](media_manager--service_runtime.md) | Запуск сервисов и журналы | 2 / 8 |
| [media_manager/storage.py](media_manager--storage.md) | Тома и снимки каталогов | 1 / 25 |
| [media_manager/storage_previews.py](media_manager--storage_previews.md) | Превью файлов на томах | 1 / 4 |
| [media_manager/thumbnail_workers.py](media_manager--thumbnail_workers.md) | Фоновые воркеры превью | 1 / 8 |
| [media_manager/thumbnails.py](media_manager--thumbnails.md) | Кэш превью медиаиндекса | 2 / 6 |
| [media_manager/volume_identity.py](media_manager--volume_identity.md) | Идентичность носителей | 0 / 12 |
| [media_manager/watcher.py](media_manager--watcher.md) | Повторное сканирование источников | 2 / 8 |
| [network_ui.py](network_ui.md) | Диалог NAS | 0 / 8 |
| [paired_tree.py](paired_tree.md) | Python-обёртка Vue-дерева | 1 / 2 |
| [paired_workspace_ui.py](paired_workspace_ui.md) | UI связанных пар | 1 / 45 |
| [photo_libraries_ui.py](photo_libraries_ui.md) | UI медиатек Photos | 1 / 28 |
| [storage_preview_ui.py](storage_preview_ui.md) | UI превью и плиток | 1 / 13 |
| [storage_ui.py](storage_ui.md) | Общие элементы и регистрация UI | 0 / 2 |
| [ui.py](ui.md) | Вход в NiceGUI и HTTP-клиент | 0 / 6 |
| [workspace_state.py](workspace_state.md) | Состояние браузерной вкладки | 0 / 5 |
| [workspace_ui.py](workspace_ui.md) | Рабочее пространство и панели | 2 / 102 |

- [JavaScript, Objective-C и AppleScript](../development/native.md)
- [HTTP API и модели запросов](../api.md)
- [Таблицы, индексы и внешние ключи](../data-model.md)
