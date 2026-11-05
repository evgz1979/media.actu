# Core API и жизненный цикл: `app.py`

Композиционный корень Core: создаёт сервисы, определяет Pydantic-контракты и маршруты FastAPI, связывает фоновые службы и переводит ошибки домена в HTTP.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../app.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/catalog.py](media_manager--catalog.md), [media_manager/comparison.py](media_manager--comparison.md), [media_manager/copies.py](media_manager--copies.md), [media_manager/copy_files.py](media_manager--copy_files.md), [media_manager/directory_sizes.py](media_manager--directory_sizes.md), [media_manager/folder_markers.py](media_manager--folder_markers.md), [media_manager/folder_tracking.py](media_manager--folder_tracking.md), [media_manager/network.py](media_manager--network.md), [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [media_manager/photo_libraries.py](media_manager--photo_libraries.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md), [media_manager/photos_browser.py](media_manager--photos_browser.md), [media_manager/photos_originals.py](media_manager--photos_originals.md), [media_manager/photos_schedule.py](media_manager--photos_schedule.md), [media_manager/scanner.py](media_manager--scanner.md), [media_manager/storage.py](media_manager--storage.md), [media_manager/storage_previews.py](media_manager--storage_previews.md), [media_manager/thumbnail_workers.py](media_manager--thumbnail_workers.md), [media_manager/thumbnails.py](media_manager--thumbnails.md), [media_manager/watcher.py](media_manager--watcher.md).
Импортируется модулями: [scripts/build_documentation.py](scripts--build_documentation.md).
Тестовые модули с прямым импортом: [tests/test_copy_connections.py](tests.md#module-tests.test_copy_connections), [tests/test_copy_files.py](tests.md#module-tests.test_copy_files), [tests/test_copy_number_release.py](tests.md#module-tests.test_copy_number_release), [tests/test_folder_tags.py](tests.md#module-tests.test_folder_tags), [tests/test_folder_tracking.py](tests.md#module-tests.test_folder_tracking), [tests/test_photos_schedule.py](tests.md#module-tests.test_photos_schedule), [tests/test_volume_identity.py](tests.md#module-tests.test_volume_identity).

## Оглавление определений

- [ComparisonRequest](#symbol-ComparisonRequest) — Определяет Pydantic-контракт общей сверки имён.
- [ComparisonScope](#symbol-ComparisonScope) — Определяет Pydantic-контракт области сверки на файловом томе.
- [CopyConnectionRequest](#symbol-CopyConnectionRequest) — Определяет Pydantic-контракт подключения или отключения связи.
- [CopyGroupAcknowledgeRequest](#symbol-CopyGroupAcknowledgeRequest) — Определяет Pydantic-контракт подтверждения версии изменения.
- [CopyGroupSettingsRequest](#symbol-CopyGroupSettingsRequest) — Определяет Pydantic-контракт настроек основной папки.
- [CopyKindRequest](#symbol-CopyKindRequest) — Определяет Pydantic-контракт типа копии.
- [CopyLocationRequest](#symbol-CopyLocationRequest) — Определяет Pydantic-контракт привязки папки-копии.
- [CopyNumberReleaseRequest](#symbol-CopyNumberReleaseRequest) — Определяет Pydantic-контракт освобождения номера копии.
- [CopyNumberSnapshot](#symbol-CopyNumberSnapshot) — Определяет Pydantic-контракт снимка текущего номера копии.
- [CopyRenumberRequest](#symbol-CopyRenumberRequest) — Определяет Pydantic-контракт перенумерации копий.
- [CopySourceRequest](#symbol-CopySourceRequest) — Определяет Pydantic-контракт выбора источника копирования.
- [DirectorySizesRequest](#symbol-DirectorySizesRequest) — Определяет Pydantic-контракт подсчёта размеров папок.
- [FolderChoiceRequest](#symbol-FolderChoiceRequest) — Определяет Pydantic-контракт выбора папок macOS.
- [FolderRequest](#symbol-FolderRequest) — Определяет Pydantic-контракт открытия папки источника.
- [FolderTagsRequest](#symbol-FolderTagsRequest) — Определяет Pydantic-контракт меток папки.
- [LibraryCopyRequest](#symbol-LibraryCopyRequest) — Определяет Pydantic-контракт папки-копии медиатеки.
- [LibraryNameRequest](#symbol-LibraryNameRequest) — Определяет Pydantic-контракт названия медиатеки.
- [NetworkShareRequest](#symbol-NetworkShareRequest) — Определяет Pydantic-контракт запоминания SMB-ресурса.
- [PairedComparisonRequest](#symbol-PairedComparisonRequest) — Определяет Pydantic-контракт сверки связанной пары.
- [PairedDecisionRequest](#symbol-PairedDecisionRequest) — Определяет Pydantic-контракт планового решения для лишнего элемента.
- [PhotosSyncScheduleRequest](#symbol-PhotosSyncScheduleRequest) — Определяет Pydantic-контракт временного окна Photos.
- [SourceMetadataRequest](#symbol-SourceMetadataRequest) — Определяет Pydantic-контракт изменения метаданных источника.
- [SourceRequest](#symbol-SourceRequest) — Определяет Pydantic-контракт регистрации обычного источника.
- [StorageMetadataRequest](#symbol-StorageMetadataRequest) — Определяет Pydantic-контракт отметок файлового расположения.
- [StoragePathRequest](#symbol-StoragePathRequest) — Определяет Pydantic-контракт открытия пути тома.
- [VolumeNameRequest](#symbol-VolumeNameRequest) — Определяет Pydantic-контракт названия сменного носителя.
- [authorize_system_photos](#symbol-authorize_system_photos) — Запрашивает разрешение Photos и возвращает состояние доступа.
- [bind_photo_library_copy](#symbol-bind_photo_library_copy) — Привязывает выбранную папку как копию медиатеки.
- [browse_photo_library](#symbol-browse_photo_library) — Возвращает виртуальную папку Photos и повышает приоритет её превью.
- [catalog_summary](#symbol-catalog_summary) — Возвращает суммарные показатели сохранённого медиаиндекса.
- [choose_folders_macos](#symbol-choose_folders_macos) — Открывает системный диалог выбора нескольких папок на машине Core.
- [choose_sources](#symbol-choose_sources) — Регистрирует выбранные системным диалогом папки и запускает их сканирование.
- [comparison_call](#symbol-comparison_call) — Выполняет команду сверки в потоке и преобразует доменные ошибки в HTTP.
- [comparison_detail](#symbol-comparison_detail) — Возвращает найденные совпадения и подробности элемента отчёта.
- [comparison_events](#symbol-comparison_events) — Возвращает события общей сверки с обратной пагинацией.
- [comparison_job](#symbol-comparison_job) — Возвращает состояние и области общей сверки.
- [comparison_jobs](#symbol-comparison_jobs) — Возвращает историю общей сверки имён и старых отчётов.
- [comparison_target_tree](#symbol-comparison_target_tree) — Возвращает страницу сохранённого дерева выбранной цели общей сверки.
- [comparison_tree](#symbol-comparison_tree) — Возвращает страницу исходного дерева общей сверки с фильтром статуса.
- [connect_network_volume](#symbol-connect_network_volume) — Открывает подключение сетевого тома в Finder на машине Core.
- [connect_photo_library](#symbol-connect_photo_library) — Повторяет сопоставление системной медиатеки и пробуждает превью.
- [copy_catalog_action](#symbol-copy_catalog_action) — Выполняет команду каталога копий в потоке и пробуждает запись маркеров.
- [create_source](#symbol-create_source) — Регистрирует обычный источник, устанавливает наблюдение и запускает сканирование.
- [delete_source](#symbol-delete_source) — Снимает наблюдение и удаляет источник из медиаиндекса.
- [discover_nas](#symbol-discover_nas) — Запускает обнаружение NAS через Bonjour на машине Core.
- [health](#symbol-health) — Возвращает готовность HTTP-процесса и текущую ревизию каталога.
- [library_call](#symbol-library_call) — Выполняет команду Photos в потоке с переводом ошибок доступа в HTTP.
- [lifespan](#symbol-lifespan) — Запускает фоновые службы FastAPI и закрывает их при завершении Core.
- [lifespan.monitor_libraries](#symbol-lifespan.monitor_libraries) — Проверяет подключение Photos каждые 30 секунд и пробуждает очередь превью.
- [list_photo_libraries](#symbol-list_photo_libraries) — Возвращает медиатеки, состояние подключения, превью и привязанные копии.
- [list_sources](#symbol-list_sources) — Возвращает сохранённые источники медиаиндекса.
- [local_thumbnail_cache_directory](#symbol-local_thumbnail_cache_directory) — Выбирает каталог превью из config.local.json либо MEDIA_ACTU_DATA_DIR.
- [media_thumbnail](#symbol-media_thumbnail) — Отдаёт только готовый JPEG из кэша медиаиндекса.
- [missing_copy_items](#symbol-missing_copy_items) — Возвращает страницу элементов сохранённого плана копирования.
- [missing_copy_job](#symbol-missing_copy_job) — Возвращает состояние операции копирования отсутствующих элементов.
- [missing_copy_plan](#symbol-missing_copy_plan) — Создаёт сохранённый план копирования по завершённому файловому отчёту.
- [nas_shares](#symbol-nas_shares) — Возвращает сохранённые либо обновлённые ресурсы выбранного NAS.
- [open_media_in_default_app](#symbol-open_media_in_default_app) — Открывает обычный файл системной командой или выделяет объект Photos.
- [open_source_folder_in_finder](#symbol-open_source_folder_in_finder) — Открывает проверенную папку обычного источника в Finder.
- [open_storage_path_in_finder](#symbol-open_storage_path_in_finder) — Передаёт Finder проверенный путь выбранного тома.
- [paired_decision](#symbol-paired_decision) — Сохраняет плановое решение для элемента только в копии.
- [paired_job](#symbol-paired_job) — Возвращает состояние одной парной сверки.
- [paired_jobs](#symbol-paired_jobs) — Возвращает историю парных сверок и допустимые решения для лишних элементов.
- [paired_rows](#symbol-paired_rows) — Возвращает страницу выровненных строк парной сверки.
- [pause_comparison](#symbol-pause_comparison) — Запрашивает паузу общей сверки имён.
- [pause_paired_job](#symbol-pause_paired_job) — Запрашивает паузу парной сверки.
- [pause_photo_library](#symbol-pause_photo_library) — Включает ручную паузу выбранной медиатеки.
- [pause_photo_originals](#symbol-pause_photo_originals) — Запрашивает паузу сохранения оригиналов выбранной медиатеки.
- [pause_thumbnails](#symbol-pause_thumbnails) — Сохраняет общую ручную паузу фоновой очереди превью.
- [photo_copy_first](#symbol-photo_copy_first) — Ставит выбранную копию Photos первой по номеру без изменения маршрутов.
- [photo_copy_source](#symbol-photo_copy_source) — Меняет источник привязанной копии Photos.
- [photo_originals_journal](#symbol-photo_originals_journal) — Возвращает журнал оригиналов и пути незавершённых записей.
- [photo_originals_status](#symbol-photo_originals_status) — Возвращает состояние оригиналов после проверки принадлежности копии медиатеке.
- [photo_preview_status](#symbol-photo_preview_status) — Возвращает готовые превью выбранных объектов медиатеки.
- [register_photo_library](#symbol-register_photo_library) — Регистрирует текущую медиатеку и ставит её первый скан в очередь.
- [register_removable](#symbol-register_removable) — Регистрирует сменный носитель с выбранным названием.
- [release_copy_number](#symbol-release_copy_number) — Освобождает подтверждённый номер под блокировкой запуска сверок.
- [remember_nas_share](#symbol-remember_nas_share) — Сохраняет выбранный SMB-ресурс без подключения.
- [remembered_nas](#symbol-remembered_nas) — Возвращает список сохранённых серверов NAS.
- [rename_photo_library](#symbol-rename_photo_library) — Меняет название медиатеки и возвращает обновлённый список.
- [rename_removable](#symbol-rename_removable) — Меняет название подтверждённого сменного носителя.
- [resume_comparison](#symbol-resume_comparison) — Продолжает сверку имён либо создаёт новую вместо старой проверки содержимого.
- [resume_paired_job](#symbol-resume_paired_job) — Продолжает парную сверку после проверки конфликтующих операций.
- [resume_photo_library](#symbol-resume_photo_library) — Снимает ручную паузу медиатеки и пробуждает очередь превью.
- [resume_thumbnails](#symbol-resume_thumbnails) — Снимает общую паузу превью и пробуждает воркеры.
- [scan_all_sources](#symbol-scan_all_sources) — Запускает сканирование зарегистрированных источников.
- [scan_one_source](#symbol-scan_one_source) — Проверяет источник и выполняет его ручное сканирование.
- [scan_source](#symbol-scan_source) — Сканирует один источник под отдельной блокировкой и обновляет его состояние.
- [schedule_scan](#symbol-schedule_scan) — Ставит сканирование источника в пул из двух потоков Core.
- [set_copy_connection](#symbol-set_copy_connection) — Меняет подключение связи с защитой от конфликтующего копирования.
- [set_folder_copy_source](#symbol-set_folder_copy_source) — Меняет источник копии под общей блокировкой запуска сверок.
- [set_photos_sync_schedule](#symbol-set_photos_sync_schedule) — Сохраняет часы синхронизации выбранной медиатеки.
- [source_files](#symbol-source_files) — Возвращает файлы папки источника и повышает приоритет их превью.
- [source_tree](#symbol-source_tree) — Возвращает дерево виртуальных папок зарегистрированного источника.
- [start_comparison](#symbol-start_comparison) — Создаёт общую сверку имён исходной области и выбранных целей.
- [start_comparison_exclusive](#symbol-start_comparison_exclusive) — Проверяет отсутствие конфликтующей работы под общей блокировкой запуска.
- [start_missing_copy](#symbol-start_missing_copy) — Запускает подтверждённую операцию создания отсутствующих копий.
- [start_paired_comparison](#symbol-start_paired_comparison) — Создаёт и запускает сверку зарегистрированной пары папок.
- [start_photo_originals](#symbol-start_photo_originals) — Запускает или планирует сохранение оригиналов в цепочку копий Photos.
- [stop_missing_copy](#symbol-stop_missing_copy) — Запрашивает остановку операции копирования.
- [storage_acknowledge_folder_changes](#symbol-storage_acknowledge_folder_changes) — Подтверждает конкретную версию уведомления об изменении папки.
- [storage_copy_group_connection](#symbol-storage_copy_group_connection) — Меняет подключение всего набора папок.
- [storage_copy_group_settings](#symbol-storage_copy_group_settings) — Обновляет настройки набора и пробуждает отслеживание изменений.
- [storage_copy_groups](#symbol-storage_copy_groups) — Возвращает наборы папок с типами, метками и состоянием наблюдателей.
- [storage_copy_kind](#symbol-storage_copy_kind) — Меняет тип зарегистрированной копии.
- [storage_copy_location](#symbol-storage_copy_location) — Добавляет папку копии к существующему набору.
- [storage_copy_location_connection](#symbol-storage_copy_location_connection) — Меняет подключение одной обычной копии.
- [storage_copy_source](#symbol-storage_copy_source) — Обрабатывает изменение источника копирования обычной папки.
- [storage_directory](#symbol-storage_directory) — Возвращает список выбранной папки тома с признаками снимка и ошибок.
- [storage_directory_sizes](#symbol-storage_directory_sizes) — Возвращает размеры папок и при разрешении ставит их в очередь подсчёта.
- [storage_folder_markers](#symbol-storage_folder_markers) — Возвращает состояние очереди служебных описаний папок.
- [storage_folder_tags](#symbol-storage_folder_tags) — Сохраняет смысловые метки выбранной папки.
- [storage_main_folder](#symbol-storage_main_folder) — Регистрирует выбранную папку как основную область набора.
- [storage_metadata](#symbol-storage_metadata) — Сохраняет пользовательские отметки расположения в каталоге.
- [storage_preview](#symbol-storage_preview) — Возвращает JPEG-превью обычного файла выбранного тома.
- [storage_release_copy_number](#symbol-storage_release_copy_number) — Архивирует прежнюю привязку и освобождает её номер.
- [storage_remove_copy](#symbol-storage_remove_copy) — Удаляет связь копии из каталога без удаления пользовательских файлов.
- [storage_remove_copy_group](#symbol-storage_remove_copy_group) — Удаляет набор папок из каталога без удаления пользовательских файлов.
- [storage_renumber_copies](#symbol-storage_renumber_copies) — Применяет подтверждённую нумерацию по снимку текущих связей.
- [storage_volumes](#symbol-storage_volumes) — Возвращает обнаруженные и сохранённые тома через API Core.
- [thumbnail_status](#symbol-thumbnail_status) — Возвращает очередь превью и диагностическое состояние её воркеров.
- [unbind_photo_library_copy](#symbol-unbind_photo_library_copy) — Отключает привязку копии медиатеки и возвращает обновлённый список.
- [update_source](#symbol-update_source) — Обновляет роль, название и комментарий обычного источника.

## Константы и значения по умолчанию

<a id="constant-DATA_DIR"></a>

### `DATA_DIR`

`Path(os.environ.get('MEDIA_ACTU_DATA_DIR', str(ROOT / 'data'))).expanduser()`

<a id="constant-ROOT"></a>

### `ROOT`

`Path(__file__).parent`


<a id="symbol-ComparisonRequest"></a>

## `ComparisonRequest`

[app.py](../../app.py) · `ComparisonRequest`

Определяет Pydantic-контракт общей сверки имён. Поля: source, targets, reread, reuse_index.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `source` | `ComparisonScope` | `обязательное поле` |
| `targets` | `list[ComparisonScope]` | `Field(min_length=1, max_length=16)` |
| `reread` | `bool` | `False` |
| `reuse_index` | `bool` | `True` |

Именованные методы: собственных методов нет.

<a id="symbol-ComparisonScope"></a>

## `ComparisonScope`

[app.py](../../app.py) · `ComparisonScope`

Определяет Pydantic-контракт области сверки на файловом томе. Поля: volume_id, path.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `volume_id` | `str` | `Field(min_length=1, max_length=128)` |
| `path` | `str` | `Field(default='', max_length=4096)` |

Именованные методы: собственных методов нет.

<a id="symbol-CopyConnectionRequest"></a>

## `CopyConnectionRequest`

[app.py](../../app.py) · `CopyConnectionRequest`

Определяет Pydantic-контракт подключения или отключения связи. Поля: connected.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `connected` | `bool` | `Field(strict=True)` |

Именованные методы: собственных методов нет.

<a id="symbol-CopyGroupAcknowledgeRequest"></a>

## `CopyGroupAcknowledgeRequest`

[app.py](../../app.py) · `CopyGroupAcknowledgeRequest`

Определяет Pydantic-контракт подтверждения версии изменения. Поля: changed_at.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `changed_at` | `str` | `Field(min_length=1, max_length=64)` |

Именованные методы: собственных методов нет.

<a id="symbol-CopyGroupSettingsRequest"></a>

## `CopyGroupSettingsRequest`

[app.py](../../app.py) · `CopyGroupSettingsRequest`

Определяет Pydantic-контракт настроек основной папки. Поля: tracking, label.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `tracking` | `bool &#124; None` | `Field(default=None, strict=True)` |
| `label` | `Literal['', 'temporary', 'inbox', 'archive'] &#124; None` | `None` |

Именованные методы: собственных методов нет.

<a id="symbol-CopyKindRequest"></a>

## `CopyKindRequest`

[app.py](../../app.py) · `CopyKindRequest`

Определяет Pydantic-контракт типа копии. Поля: kind.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `kind` | `Literal['copy', 'cold', 'cloud']` | `обязательное поле` |

Именованные методы: собственных методов нет.

<a id="symbol-CopyLocationRequest"></a>

## `CopyLocationRequest`

[app.py](../../app.py) · `CopyLocationRequest`

Определяет Pydantic-контракт привязки папки-копии. Поля: kind.

Базовые классы: `ComparisonScope`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `kind` | `Literal['copy', 'cold', 'cloud']` | `'copy'` |

Именованные методы: собственных методов нет.

<a id="symbol-CopyNumberReleaseRequest"></a>

## `CopyNumberReleaseRequest`

[app.py](../../app.py) · `CopyNumberReleaseRequest`

Определяет Pydantic-контракт освобождения номера копии. Поля: number.

Базовые классы: `CopyKindRequest`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `number` | `int` | `Field(gt=0, strict=True)` |

Именованные методы: собственных методов нет.

<a id="symbol-CopyNumberSnapshot"></a>

## `CopyNumberSnapshot`

[app.py](../../app.py) · `CopyNumberSnapshot`

Определяет Pydantic-контракт снимка текущего номера копии. Поля: id, number.

Базовые классы: `CopyKindRequest`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `id` | `str` | `Field(min_length=1, max_length=128)` |
| `number` | `int` | `Field(gt=0)` |

Именованные методы: собственных методов нет.

<a id="symbol-CopyRenumberRequest"></a>

## `CopyRenumberRequest`

[app.py](../../app.py) · `CopyRenumberRequest`

Определяет Pydantic-контракт перенумерации копий. Поля: copies.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `copies` | `list[CopyNumberSnapshot]` | `обязательное поле` |

Именованные методы: собственных методов нет.

<a id="symbol-CopySourceRequest"></a>

## `CopySourceRequest`

[app.py](../../app.py) · `CopySourceRequest`

Определяет Pydantic-контракт выбора источника копирования. Поля: source_id.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `source_id` | `str &#124; None` | `Field(default=None, min_length=1, max_length=128)` |

Именованные методы: собственных методов нет.

<a id="symbol-DirectorySizesRequest"></a>

## `DirectorySizesRequest`

[app.py](../../app.py) · `DirectorySizesRequest`

Определяет Pydantic-контракт подсчёта размеров папок. Поля: paths, start, refresh.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `paths` | `list[str]` | `Field(min_length=1, max_length=500)` |
| `start` | `bool` | `True` |
| `refresh` | `bool` | `False` |

Именованные методы: собственных методов нет.

<a id="symbol-FolderChoiceRequest"></a>

## `FolderChoiceRequest`

[app.py](../../app.py) · `FolderChoiceRequest`

Определяет Pydantic-контракт выбора папок macOS. Поля: role, label, comment.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `role` | `Literal['source', 'storage']` | `'source'` |
| `label` | `str` | `''` |
| `comment` | `str` | `''` |

Именованные методы: собственных методов нет.

<a id="symbol-FolderRequest"></a>

## `FolderRequest`

[app.py](../../app.py) · `FolderRequest`

Определяет Pydantic-контракт открытия папки источника. Поля: folder.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `folder` | `str` | `''` |

Именованные методы: собственных методов нет.

<a id="symbol-FolderTagsRequest"></a>

## `FolderTagsRequest`

[app.py](../../app.py) · `FolderTagsRequest`

Определяет Pydantic-контракт меток папки. Поля: path, tags.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `Field(default='', max_length=4096)` |
| `tags` | `list[Literal['old_copy', 'sort', 'check']]` | `Field(max_length=3)` |

Именованные методы: собственных методов нет.

<a id="symbol-LibraryCopyRequest"></a>

## `LibraryCopyRequest`

[app.py](../../app.py) · `LibraryCopyRequest`

Определяет Pydantic-контракт папки-копии медиатеки. Поля: volume_id, path.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `volume_id` | `str` | `Field(min_length=1, max_length=128)` |
| `path` | `str` | `Field(min_length=1, max_length=4096)` |

Именованные методы: собственных методов нет.

<a id="symbol-LibraryNameRequest"></a>

## `LibraryNameRequest`

[app.py](../../app.py) · `LibraryNameRequest`

Определяет Pydantic-контракт названия медиатеки. Поля: label.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `label` | `str` | `Field(min_length=1, max_length=120)` |

Именованные методы: собственных методов нет.

<a id="symbol-NetworkShareRequest"></a>

## `NetworkShareRequest`

[app.py](../../app.py) · `NetworkShareRequest`

Определяет Pydantic-контракт запоминания SMB-ресурса. Поля: share.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `share` | `str` | `Field(min_length=1, max_length=255)` |

Именованные методы: собственных методов нет.

<a id="symbol-PairedComparisonRequest"></a>

## `PairedComparisonRequest`

[app.py](../../app.py) · `PairedComparisonRequest`

Определяет Pydantic-контракт сверки связанной пары. Поля: copy_id, mode, base_job_id, method.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `copy_id` | `str` | `Field(min_length=1, max_length=128)` |
| `mode` | `Literal['folders', 'files']` | `'folders'` |
| `base_job_id` | `str &#124; None` | `None` |
| `method` | `Literal['size', 'sha256']` | `'size'` |

Именованные методы: собственных методов нет.

<a id="symbol-PairedDecisionRequest"></a>

## `PairedDecisionRequest`

[app.py](../../app.py) · `PairedDecisionRequest`

Определяет Pydantic-контракт планового решения для лишнего элемента. Поля: path, action.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `Field(max_length=4096)` |
| `action` | `Literal['keep', 'add_main', 'move', 'remove'] &#124; None` | `обязательное поле` |

Именованные методы: собственных методов нет.

<a id="symbol-PhotosSyncScheduleRequest"></a>

## `PhotosSyncScheduleRequest`

[app.py](../../app.py) · `PhotosSyncScheduleRequest`

Определяет Pydantic-контракт временного окна Photos. Поля: night_only, start_hour, end_hour, timezone.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `night_only` | `bool` | `Field(strict=True)` |
| `start_hour` | `int` | `Field(default=0, ge=0, le=23, strict=True)` |
| `end_hour` | `int` | `Field(default=7, ge=0, le=23, strict=True)` |
| `timezone` | `Literal['Europe/Moscow']` | `'Europe/Moscow'` |

Именованные методы: собственных методов нет.

<a id="symbol-SourceMetadataRequest"></a>

## `SourceMetadataRequest`

[app.py](../../app.py) · `SourceMetadataRequest`

Определяет Pydantic-контракт изменения метаданных источника. Поля: role, label, comment.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `role` | `Literal['source', 'storage']` | `обязательное поле` |
| `label` | `str` | `''` |
| `comment` | `str` | `''` |

Именованные методы: собственных методов нет.

<a id="symbol-SourceRequest"></a>

## `SourceRequest`

[app.py](../../app.py) · `SourceRequest`

Определяет Pydantic-контракт регистрации обычного источника. Поля: path, role, label, comment.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `обязательное поле` |
| `role` | `Literal['source', 'storage']` | `'source'` |
| `label` | `str` | `''` |
| `comment` | `str` | `''` |

Именованные методы: собственных методов нет.

<a id="symbol-StorageMetadataRequest"></a>

## `StorageMetadataRequest`

[app.py](../../app.py) · `StorageMetadataRequest`

Определяет Pydantic-контракт отметок файлового расположения. Поля: path, purpose, role, no_duplicate, planned_move, comment.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `''` |
| `purpose` | `Literal['', 'media', 'documents', 'projects', 'mixed'] &#124; None` | `None` |
| `role` | `Literal['', 'primary', 'copy', 'archive', 'temporary'] &#124; None` | `None` |
| `no_duplicate` | `bool &#124; None` | `None` |
| `planned_move` | `bool &#124; None` | `None` |
| `comment` | `str` | `Field(default='', max_length=4000)` |

Именованные методы: собственных методов нет.

<a id="symbol-StoragePathRequest"></a>

## `StoragePathRequest`

[app.py](../../app.py) · `StoragePathRequest`

Определяет Pydantic-контракт открытия пути тома. Поля: path.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `Field(default='', max_length=4096)` |

Именованные методы: собственных методов нет.

<a id="symbol-VolumeNameRequest"></a>

## `VolumeNameRequest`

[app.py](../../app.py) · `VolumeNameRequest`

Определяет Pydantic-контракт названия сменного носителя. Поля: name.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `name` | `str` | `Field(min_length=1, max_length=120)` |

Именованные методы: собственных методов нет.

<a id="symbol-authorize_system_photos"></a>

## `authorize_system_photos`

[app.py](../../app.py) · `authorize_system_photos`

Запрашивает разрешение Photos и возвращает состояние доступа. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def authorize_system_photos() -> dict[str, object]
```

Декораторы: `app.post('/api/photos/authorize')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `catalog.get_source`, [schedule_scan](app.md#symbol-schedule_scan), `source.get`, `status.get`, `str`, `thumbnail_workers.wake`.

Явные `raise`:

- `HTTPException(status_code=403, detail='Разреши доступ в настройках macOS: Конфиденциальность → Фото')`
- `HTTPException(status_code=500, detail=str(error))`

Перехватываемые типы: `PhotosAccessDenied`, `PhotosAdapterError`.

Выражения возврата (ветви, без исполнения):

- `{'status': status}`


<a id="symbol-bind_photo_library_copy"></a>

## `bind_photo_library_copy`

[app.py](../../app.py) · `bind_photo_library_copy`

Привязывает выбранную папку как копию медиатеки. Асинхронно ожидает: library_call.

```python
async def bind_photo_library_copy(source_id: int, request: LibraryCopyRequest) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/copies', status_code=201)`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call).

Выражения возврата (ветви, без исполнения):

- `await library_call(photo_libraries.bind_copy, source_id, request.volume_id, request.path)`


<a id="symbol-browse_photo_library"></a>

## `browse_photo_library`

[app.py](../../app.py) · `browse_photo_library`

Возвращает виртуальную папку Photos и повышает приоритет её превью. Асинхронно ожидает: library_call.

```python
async def browse_photo_library(source_id: int, path: str='', offset: int=Query(default=0, ge=0), limit: int=Query(default=150, ge=1, le=1000)) -> dict
```

Декораторы: `app.get('/api/photos/libraries/{source_id}/browse')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-catalog_summary"></a>

## `catalog_summary`

[app.py](../../app.py) · `catalog_summary`

Возвращает суммарные показатели сохранённого медиаиндекса. Использует catalog.summary.

```python
async def catalog_summary() -> dict[str, int]
```

Декораторы: `app.get('/api/catalog/summary')`.

Прямые выражения вызова: `catalog.summary`.

Выражения возврата (ветви, без исполнения):

- `catalog.summary()`


<a id="symbol-choose_folders_macos"></a>

## `choose_folders_macos`

[app.py](../../app.py) · `choose_folders_macos`

Открывает системный диалог выбора нескольких папок на машине Core. Явно отклоняет недопустимое состояние через RuntimeError.

```python
def choose_folders_macos(prompt: str) -> list[str]
```

Прямые выражения вызова: `RuntimeError`, `line.strip`, `result.stderr.strip`, `result.stdout.splitlines`, `subprocess.run`.

Явные `raise`:

- `RuntimeError(result.stderr.strip() or 'Не удалось открыть выбор папки')`

Выражения возврата (ветви, без исполнения):

- `[]`
- `[line.strip() for line in result.stdout.splitlines() if line.strip()]`


<a id="symbol-choose_sources"></a>

## `choose_sources`

[app.py](../../app.py) · `choose_sources`

Регистрирует выбранные системным диалогом папки и запускает их сканирование. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def choose_sources(request: FolderChoiceRequest) -> dict[str, object]
```

Декораторы: `app.post('/api/sources/choose')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `catalog.add_source`, `catalog.list_sources`, `int`, [schedule_scan](app.md#symbol-schedule_scan), `str`, `watcher.watch`.

Явные `raise`:

- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `(RuntimeError, FileNotFoundError, NotADirectoryError, PermissionError)`.

Выражения возврата (ветви, без исполнения):

- `{'cancelled': not selected, 'sources': catalog.list_sources()}`


<a id="symbol-comparison_call"></a>

## `comparison_call`

[app.py](../../app.py) · `comparison_call`

Выполняет команду сверки в потоке и преобразует доменные ошибки в HTTP. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def comparison_call(function, *args, **kwargs)
```

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail=str(error))`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `(ValueError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(function, *args, **kwargs)`


<a id="symbol-comparison_detail"></a>

## `comparison_detail`

[app.py](../../app.py) · `comparison_detail`

Возвращает найденные совпадения и подробности элемента отчёта. Асинхронно ожидает: comparison_call.

```python
async def comparison_detail(job_id: str, path: str | None=None) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}/detail')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.detail, job_id, path)`


<a id="symbol-comparison_events"></a>

## `comparison_events`

[app.py](../../app.py) · `comparison_events`

Возвращает события общей сверки с обратной пагинацией. Поля результата: events.

```python
async def comparison_events(job_id: str, before: int | None=Query(None, ge=1)) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}/events')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `{'events': await comparison_call(comparison.events, job_id, before)}`


<a id="symbol-comparison_job"></a>

## `comparison_job`

[app.py](../../app.py) · `comparison_job`

Возвращает состояние и области общей сверки. Асинхронно ожидает: comparison_call.

```python
async def comparison_job(job_id: str) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.job, job_id)`


<a id="symbol-comparison_jobs"></a>

## `comparison_jobs`

[app.py](../../app.py) · `comparison_jobs`

Возвращает историю общей сверки имён и старых отчётов. Поля результата: jobs.

```python
async def comparison_jobs() -> dict
```

Декораторы: `app.get('/api/storage/comparisons')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `{'jobs': await comparison_call(comparison.jobs)}`


<a id="symbol-comparison_target_tree"></a>

## `comparison_target_tree`

[app.py](../../app.py) · `comparison_target_tree`

Возвращает страницу сохранённого дерева выбранной цели общей сверки. Асинхронно ожидает: comparison_call.

```python
async def comparison_target_tree(job_id: str, scan_id: int=Query(..., ge=1), path: str | None=None, offset: int=Query(0, ge=0), limit: int=Query(200, ge=1, le=500)) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}/target-tree')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.target_tree, job_id, scan_id, path, offset, limit)`


<a id="symbol-comparison_tree"></a>

## `comparison_tree`

[app.py](../../app.py) · `comparison_tree`

Возвращает страницу исходного дерева общей сверки с фильтром статуса. Асинхронно ожидает: comparison_call.

```python
async def comparison_tree(job_id: str, path: str | None=None, status: str='', offset: int=Query(0, ge=0), limit: int=Query(200, ge=1, le=500)) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}/tree')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.tree, job_id, path, status, offset, limit)`


<a id="symbol-connect_network_volume"></a>

## `connect_network_volume`

[app.py](../../app.py) · `connect_network_volume`

Открывает подключение сетевого тома в Finder на машине Core. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def connect_network_volume(volume_id: str) -> dict
```

Декораторы: `app.post('/api/storage/volumes/{volume_id}/connect')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Том не найден')`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `NetworkError`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(network.open_in_finder, volume_id)`


<a id="symbol-connect_photo_library"></a>

## `connect_photo_library`

[app.py](../../app.py) · `connect_photo_library`

Повторяет сопоставление системной медиатеки и пробуждает превью. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def connect_photo_library() -> dict
```

Декораторы: `app.post('/api/photos/libraries/connect')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), [list_photo_libraries](app.md#symbol-list_photo_libraries), `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-copy_catalog_action"></a>

## `copy_catalog_action`

[app.py](../../app.py) · `copy_catalog_action`

Выполняет команду каталога копий в потоке и пробуждает запись маркеров. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def copy_catalog_action(action, *args)
```

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `folder_markers.wake`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail=str(error))`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `(ValueError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-create_source"></a>

## `create_source`

[app.py](../../app.py) · `create_source`

Регистрирует обычный источник, устанавливает наблюдение и запускает сканирование. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def create_source(request: SourceRequest) -> dict[str, object]
```

Декораторы: `app.post('/api/sources')`.

Прямые выражения вызова: `HTTPException`, `catalog.add_source`, `catalog.list_sources`, `int`, [schedule_scan](app.md#symbol-schedule_scan), `str`, `watcher.watch`.

Явные `raise`:

- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `(FileNotFoundError, NotADirectoryError, PermissionError)`.

Выражения возврата (ветви, без исполнения):

- `{'sources': catalog.list_sources()}`


<a id="symbol-delete_source"></a>

## `delete_source`

[app.py](../../app.py) · `delete_source`

Снимает наблюдение и удаляет источник из медиаиндекса. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def delete_source(source_id: int) -> dict[str, object]
```

Декораторы: `app.delete('/api/sources/{source_id}')`.

Прямые выражения вызова: `HTTPException`, `catalog.get_source`, `catalog.list_sources`, `catalog.remove_source`, `source.get`, `watcher.unwatch`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Источник не найден')`
- `HTTPException(status_code=400, detail='Предустановленный источник Photos нельзя удалить')`

Выражения возврата (ветви, без исполнения):

- `{'sources': catalog.list_sources()}`


<a id="symbol-discover_nas"></a>

## `discover_nas`

[app.py](../../app.py) · `discover_nas`

Запускает обнаружение NAS через Bonjour на машине Core. Асинхронно ожидает: asyncio.to_thread.

```python
async def discover_nas() -> dict
```

Декораторы: `app.post('/api/storage/nas/discover')`.

Прямые выражения вызова: `asyncio.to_thread`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(network.scan)`


<a id="symbol-health"></a>

## `health`

[app.py](../../app.py) · `health`

Возвращает готовность HTTP-процесса и текущую ревизию каталога. Поля результата: status, revision.

```python
async def health() -> dict[str, object]
```

Декораторы: `app.get('/health')`.

Прямые выражения вызова: `catalog.revision`.

Выражения возврата (ветви, без исполнения):

- `{'status': 'ok', 'revision': catalog.revision()}`


<a id="symbol-library_call"></a>

## `library_call`

[app.py](../../app.py) · `library_call`

Выполняет команду Photos в потоке с переводом ошибок доступа в HTTP. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def library_call(method, *args, **kwargs)
```

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=403, detail=str(error))`
- `HTTPException(status_code=409, detail=str(error))`
- `HTTPException(status_code=404, detail=str(error))`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `PhotosAccessDenied`, `PhotosLibraryUnavailable`, `KeyError`, `(ValueError, OSError, PhotosAdapterError)`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(method, *args, **kwargs)`


<a id="symbol-lifespan"></a>

## `lifespan`

[app.py](../../app.py) · `lifespan`

Запускает фоновые службы FastAPI и закрывает их при завершении Core. Асинхронно ожидает: asyncio.to_thread.

```python
async def lifespan(_: FastAPI)
```

Декораторы: `asynccontextmanager`.

Прямые выражения вызова: `Path`, `asyncio.create_task`, `asyncio.to_thread`, `catalog.list_sources`, `catalog.reset_stale_source_scans`, `comparison.close`, `directory_sizes.close`, `executor.shutdown`, `folder_markers.close`, `folder_markers.start`, `folder_tracking.close`, `folder_tracking.start`, `int`, `missing_copies.close`, `monitor_libraries`, `paired_comparison.close`, `photo_libraries.profile`, `photos_adapter.close`, `photos_monitor.cancel`, `photos_originals.close`, `photos_schedule.close`, `photos_schedule.start`, [schedule_scan](app.md#symbol-schedule_scan), `source.get`, `source_path.is_dir`, `str`, `thumbnail_workers.start`, `thumbnail_workers.stop`, `watcher.start`, `watcher.stop`, `watcher.watch`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-lifespan.monitor_libraries"></a>

## `lifespan.monitor_libraries`

[app.py](../../app.py) · `lifespan.monitor_libraries`

Проверяет подключение Photos каждые 30 секунд и пробуждает очередь превью. Асинхронно ожидает: asyncio.sleep, asyncio.to_thread.

```python
async def monitor_libraries()
```

Прямые выражения вызова: `asyncio.sleep`, `asyncio.to_thread`, `photo_libraries.connection.get`, `thumbnail_workers.wake`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-list_photo_libraries"></a>

## `list_photo_libraries`

[app.py](../../app.py) · `list_photo_libraries`

Возвращает медиатеки, состояние подключения, превью и привязанные копии. Асинхронно ожидает: library_call.

```python
async def list_photo_libraries() -> dict
```

Декораторы: `app.get('/api/photos/libraries')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call).

Выражения возврата (ветви, без исполнения):

- `await library_call(photo_libraries.list)`


<a id="symbol-list_sources"></a>

## `list_sources`

[app.py](../../app.py) · `list_sources`

Возвращает сохранённые источники медиаиндекса. Поля результата: sources, revision.

```python
async def list_sources() -> dict[str, object]
```

Декораторы: `app.get('/api/sources')`.

Прямые выражения вызова: `catalog.list_sources`, `catalog.revision`.

Выражения возврата (ветви, без исполнения):

- `{'sources': catalog.list_sources(), 'revision': catalog.revision()}`


<a id="symbol-local_thumbnail_cache_directory"></a>

## `local_thumbnail_cache_directory`

[app.py](../../app.py) · `local_thumbnail_cache_directory`

Выбирает каталог превью из config.local.json либо MEDIA_ACTU_DATA_DIR. Использует Path, Path(str(configured)).expanduser, config_path.is_file, config_path.read_text, json.loads.

```python
def local_thumbnail_cache_directory() -> Path
```

Прямые выражения вызова: `Path`, `Path(str(configured)).expanduser`, `config_path.is_file`, `config_path.read_text`, `json.loads`, `settings.get`, `str`.

Выражения возврата (ветви, без исполнения):

- `DATA_DIR / 'thumbnails'`
- `Path(str(configured)).expanduser() if configured else DATA_DIR / 'thumbnails'`


<a id="symbol-media_thumbnail"></a>

## `media_thumbnail`

[app.py](../../app.py) · `media_thumbnail`

Отдаёт только готовый JPEG из кэша медиаиндекса. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def media_thumbnail(media_id: int) -> FileResponse
```

Декораторы: `app.get('/api/media/{media_id}/thumbnail')`.

Прямые выражения вызова: `FileResponse`, `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=503, detail=str(error))`
- `HTTPException(status_code=404, detail=str(error))`
- `HTTPException(status_code=404, detail='Превью готовится')`

Перехватываемые типы: `ThumbnailCacheUnavailable`, `(FileNotFoundError, PermissionError, OSError, PhotosAdapterError)`.

Выражения возврата (ветви, без исполнения):

- `FileResponse(thumbnail, media_type='image/jpeg', headers={'Cache-Control': 'no-store'})`


<a id="symbol-missing_copy_items"></a>

## `missing_copy_items`

[app.py](../../app.py) · `missing_copy_items`

Возвращает страницу элементов сохранённого плана копирования. Асинхронно ожидает: comparison_call.

```python
async def missing_copy_items(operation_id: str, offset: int=Query(0, ge=0), limit: int=Query(200, ge=1, le=1000)) -> dict
```

Декораторы: `app.get('/api/storage/copy-operations/{operation_id}/items')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(missing_copies.items, operation_id, offset, limit)`


<a id="symbol-missing_copy_job"></a>

## `missing_copy_job`

[app.py](../../app.py) · `missing_copy_job`

Возвращает состояние операции копирования отсутствующих элементов. Асинхронно ожидает: comparison_call.

```python
async def missing_copy_job(operation_id: str) -> dict
```

Декораторы: `app.get('/api/storage/copy-operations/{operation_id}')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(missing_copies.job, operation_id)`


<a id="symbol-missing_copy_plan"></a>

## `missing_copy_plan`

[app.py](../../app.py) · `missing_copy_plan`

Создаёт сохранённый план копирования по завершённому файловому отчёту. Асинхронно ожидает: comparison_call.

```python
async def missing_copy_plan(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/paired-comparisons/{job_id}/copy-plan', status_code=201)`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(missing_copies.plan, job_id)`


<a id="symbol-nas_shares"></a>

## `nas_shares`

[app.py](../../app.py) · `nas_shares`

Возвращает сохранённые либо обновлённые ресурсы выбранного NAS. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def nas_shares(server_id: str, refresh: bool=False) -> dict
```

Декораторы: `app.get('/api/storage/nas/{server_id}/shares')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`.

Явные `raise`:

- `HTTPException(status_code=404, detail='NAS не найден')`

Перехватываемые типы: `KeyError`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(network.shares, server_id, refresh)`


<a id="symbol-open_media_in_default_app"></a>

## `open_media_in_default_app`

[app.py](../../app.py) · `open_media_in_default_app`

Открывает обычный файл системной командой или выделяет объект Photos. Явно отклоняет недопустимое состояние через HTTPException, KeyError.

```python
async def open_media_in_default_app(media_id: int) -> dict[str, str]
```

Декораторы: `app.post('/api/media/{media_id}/open')`.

Прямые выражения вызова: `HTTPException`, `KeyError`, `asyncio.to_thread`, `catalog.get_media`, `catalog.resolve_media_file`, `error.stderr.strip`, `int`, `media.get`, `str`.

Явные `raise`:

- `KeyError(media_id)`
- `HTTPException(status_code=404, detail='Файл не найден в каталоге')`
- `HTTPException(status_code=404, detail='Оригинал файла не найден')`
- `HTTPException(status_code=403, detail=str(error))`
- `HTTPException(status_code=409, detail=str(error))`
- `HTTPException(status_code=500, detail=str(error))`
- `HTTPException(status_code=500, detail=error.stderr.strip() or 'Не удалось открыть файл')`

Перехватываемые типы: `KeyError`, `FileNotFoundError`, `PermissionError`, `PhotosLibraryUnavailable`, `PhotosAccessDenied`, `PhotosAdapterError`, `subprocess.CalledProcessError`.

Выражения возврата (ветви, без исполнения):

- `{'path': f"{media['source_path']}/{media['relative_path']}"}`
- `{'path': str(original)}`


<a id="symbol-open_source_folder_in_finder"></a>

## `open_source_folder_in_finder`

[app.py](../../app.py) · `open_source_folder_in_finder`

Открывает проверенную папку обычного источника в Finder. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def open_source_folder_in_finder(source_id: int, request: FolderRequest) -> dict[str, str]
```

Декораторы: `app.post('/api/sources/{source_id}/open-in-finder')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `catalog.resolve_source_folder`, `error.stderr.strip`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Источник не найден')`
- `HTTPException(status_code=404, detail='Каталог не найден')`
- `HTTPException(status_code=403, detail=str(error))`
- `HTTPException(status_code=500, detail=error.stderr.strip() or 'Не удалось открыть Finder')`

Перехватываемые типы: `KeyError`, `FileNotFoundError`, `PermissionError`, `subprocess.CalledProcessError`.

Выражения возврата (ветви, без исполнения):

- `{'path': str(folder)}`


<a id="symbol-open_storage_path_in_finder"></a>

## `open_storage_path_in_finder`

[app.py](../../app.py) · `open_storage_path_in_finder`

Передаёт Finder проверенный путь выбранного тома. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def open_storage_path_in_finder(volume_id: str, request: StoragePathRequest) -> dict
```

Декораторы: `app.post('/api/storage/volumes/{volume_id}/open-in-finder')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Том не найден')`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `(ValueError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(storage.open_in_finder, volume_id, request.path)`


<a id="symbol-paired_decision"></a>

## `paired_decision`

[app.py](../../app.py) · `paired_decision`

Сохраняет плановое решение для элемента только в копии. Асинхронно ожидает: comparison_call.

```python
async def paired_decision(job_id: str, request: PairedDecisionRequest) -> dict
```

Декораторы: `app.patch('/api/storage/paired-comparisons/{job_id}/decision')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(paired_comparison.decide, job_id, request.path, request.action)`


<a id="symbol-paired_job"></a>

## `paired_job`

[app.py](../../app.py) · `paired_job`

Возвращает состояние одной парной сверки. Асинхронно ожидает: comparison_call.

```python
async def paired_job(job_id: str) -> dict
```

Декораторы: `app.get('/api/storage/paired-comparisons/{job_id}')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(paired_comparison.job, job_id)`


<a id="symbol-paired_jobs"></a>

## `paired_jobs`

[app.py](../../app.py) · `paired_jobs`

Возвращает историю парных сверок и допустимые решения для лишних элементов. Поля результата: jobs, decisions.

```python
async def paired_jobs(copy_id: str | None=None) -> dict
```

Декораторы: `app.get('/api/storage/paired-comparisons')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `{'jobs': await comparison_call(paired_comparison.jobs, copy_id), 'decisions': DECISIONS}`


<a id="symbol-paired_rows"></a>

## `paired_rows`

[app.py](../../app.py) · `paired_rows`

Возвращает страницу выровненных строк парной сверки. Асинхронно ожидает: comparison_call.

```python
async def paired_rows(job_id: str, offset: int=Query(0, ge=0), limit: int=Query(1000, ge=1, le=5000), differences_only: bool=False) -> dict
```

Декораторы: `app.get('/api/storage/paired-comparisons/{job_id}/rows')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(paired_comparison.rows, job_id, offset, limit, differences_only)`


<a id="symbol-pause_comparison"></a>

## `pause_comparison`

[app.py](../../app.py) · `pause_comparison`

Запрашивает паузу общей сверки имён. Асинхронно ожидает: comparison_call.

```python
async def pause_comparison(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/comparisons/{job_id}/pause')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.pause, job_id)`


<a id="symbol-pause_paired_job"></a>

## `pause_paired_job`

[app.py](../../app.py) · `pause_paired_job`

Запрашивает паузу парной сверки. Асинхронно ожидает: comparison_call.

```python
async def pause_paired_job(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/paired-comparisons/{job_id}/pause')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(paired_comparison.pause, job_id)`


<a id="symbol-pause_photo_library"></a>

## `pause_photo_library`

[app.py](../../app.py) · `pause_photo_library`

Включает ручную паузу выбранной медиатеки. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def pause_photo_library(source_id: int) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/pause')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), [list_photo_libraries](app.md#symbol-list_photo_libraries).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-pause_photo_originals"></a>

## `pause_photo_originals`

[app.py](../../app.py) · `pause_photo_originals`

Запрашивает паузу сохранения оригиналов выбранной медиатеки. Асинхронно ожидает: library_call.

```python
async def pause_photo_originals(source_id: int, link_id: str) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/copies/{link_id}/originals/pause')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call).

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_originals.pause, link_id, source_id)`


<a id="symbol-pause_thumbnails"></a>

## `pause_thumbnails`

[app.py](../../app.py) · `pause_thumbnails`

Сохраняет общую ручную паузу фоновой очереди превью. Использует catalog.set_thumbnail_queue_paused, thumbnail_workers.status.

```python
async def pause_thumbnails() -> dict[str, object]
```

Декораторы: `app.post('/api/thumbnails/pause')`.

Прямые выражения вызова: `catalog.set_thumbnail_queue_paused`, `thumbnail_workers.status`.

Выражения возврата (ветви, без исполнения):

- `thumbnail_workers.status()`


<a id="symbol-photo_copy_first"></a>

## `photo_copy_first`

[app.py](../../app.py) · `photo_copy_first`

Ставит выбранную копию Photos первой по номеру без изменения маршрутов. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def photo_copy_first(source_id: int, link_id: str) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/copies/{link_id}/make-first')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), [list_photo_libraries](app.md#symbol-list_photo_libraries).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-photo_copy_source"></a>

## `photo_copy_source`

[app.py](../../app.py) · `photo_copy_source`

Меняет источник привязанной копии Photos. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def photo_copy_source(source_id: int, link_id: str, request: CopySourceRequest) -> dict
```

Декораторы: `app.patch('/api/photos/libraries/{source_id}/copies/{link_id}/source')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), [list_photo_libraries](app.md#symbol-list_photo_libraries).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-photo_originals_journal"></a>

## `photo_originals_journal`

[app.py](../../app.py) · `photo_originals_journal`

Возвращает журнал оригиналов и пути незавершённых записей. Асинхронно ожидает: library_call.

```python
async def photo_originals_journal(source_id: int, link_id: str) -> dict
```

Декораторы: `app.get('/api/photos/libraries/{source_id}/copies/{link_id}/originals/journal')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call).

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_originals.journal, link_id, source_id)`


<a id="symbol-photo_originals_status"></a>

## `photo_originals_status`

[app.py](../../app.py) · `photo_originals_status`

Возвращает состояние оригиналов после проверки принадлежности копии медиатеке. Асинхронно ожидает: library_call.

```python
async def photo_originals_status(source_id: int, link_id: str) -> dict
```

Декораторы: `app.get('/api/photos/libraries/{source_id}/copies/{link_id}/originals')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call).

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_originals.summary, link_id)`


<a id="symbol-photo_preview_status"></a>

## `photo_preview_status`

[app.py](../../app.py) · `photo_preview_status`

Возвращает готовые превью выбранных объектов медиатеки. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def photo_preview_status(source_id: int, ids: list[int]=Query(default=[])) -> dict
```

Декораторы: `app.get('/api/photos/libraries/{source_id}/preview-status')`.

Прямые выражения вызова: `HTTPException`, `len`, [library_call](app.md#symbol-library_call).

Явные `raise`:

- `HTTPException(status_code=400, detail='Слишком много объектов')`

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_browser.preview_status, source_id, ids)`


<a id="symbol-register_photo_library"></a>

## `register_photo_library`

[app.py](../../app.py) · `register_photo_library`

Регистрирует текущую медиатеку и ставит её первый скан в очередь. Асинхронно ожидает: library_call.

```python
async def register_photo_library(request: LibraryNameRequest) -> dict
```

Декораторы: `app.post('/api/photos/libraries', status_code=201)`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), [schedule_scan](app.md#symbol-schedule_scan).

Выражения возврата (ветви, без исполнения):

- `profile`


<a id="symbol-register_removable"></a>

## `register_removable`

[app.py](../../app.py) · `register_removable`

Регистрирует сменный носитель с выбранным названием. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def register_removable(volume_id: str, request: VolumeNameRequest) -> dict
```

Декораторы: `app.post('/api/storage/volumes/{volume_id}/register-removable')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `(ValueError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(storage.register_removable, volume_id, request.name)`


<a id="symbol-release_copy_number"></a>

## `release_copy_number`

[app.py](../../app.py) · `release_copy_number`

Освобождает подтверждённый номер под блокировкой запуска сверок. Явно отклоняет недопустимое состояние через ValueError.

```python
def release_copy_number(location_id, number, kind)
```

Прямые выражения вызова: `ValueError`, `copies.release_copy_number`, `paired_comparison.busy`.

Явные `raise`:

- `ValueError('Сначала дождись завершения сверки и копирования.')`

Выражения возврата (ветви, без исполнения):

- `copies.release_copy_number(location_id, number, kind)`


<a id="symbol-remember_nas_share"></a>

## `remember_nas_share`

[app.py](../../app.py) · `remember_nas_share`

Сохраняет выбранный SMB-ресурс без подключения. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def remember_nas_share(server_id: str, request: NetworkShareRequest) -> dict
```

Декораторы: `app.post('/api/storage/nas/{server_id}/remember')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail=str(error))`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `NetworkError`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(network.remember, server_id, request.share)`


<a id="symbol-remembered_nas"></a>

## `remembered_nas`

[app.py](../../app.py) · `remembered_nas`

Возвращает список сохранённых серверов NAS. Асинхронно ожидает: asyncio.to_thread.

```python
async def remembered_nas() -> dict
```

Декораторы: `app.get('/api/storage/nas')`.

Прямые выражения вызова: `asyncio.to_thread`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(network.servers)`


<a id="symbol-rename_photo_library"></a>

## `rename_photo_library`

[app.py](../../app.py) · `rename_photo_library`

Меняет название медиатеки и возвращает обновлённый список. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def rename_photo_library(source_id: int, request: LibraryNameRequest) -> dict
```

Декораторы: `app.patch('/api/photos/libraries/{source_id}')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), [list_photo_libraries](app.md#symbol-list_photo_libraries).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-rename_removable"></a>

## `rename_removable`

[app.py](../../app.py) · `rename_removable`

Меняет название подтверждённого сменного носителя. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def rename_removable(volume_id: str, request: VolumeNameRequest) -> dict
```

Декораторы: `app.patch('/api/storage/volumes/{volume_id}/name')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `(ValueError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(storage.rename_removable, volume_id, request.name)`


<a id="symbol-resume_comparison"></a>

## `resume_comparison`

[app.py](../../app.py) · `resume_comparison`

Продолжает сверку имён либо создаёт новую вместо старой проверки содержимого. Асинхронно ожидает: comparison_call.

```python
async def resume_comparison(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/comparisons/{job_id}/resume')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, comparison.resume, job_id)`


<a id="symbol-resume_paired_job"></a>

## `resume_paired_job`

[app.py](../../app.py) · `resume_paired_job`

Продолжает парную сверку после проверки конфликтующих операций. Асинхронно ожидает: comparison_call.

```python
async def resume_paired_job(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/paired-comparisons/{job_id}/resume')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, paired_comparison.resume, job_id)`


<a id="symbol-resume_photo_library"></a>

## `resume_photo_library`

[app.py](../../app.py) · `resume_photo_library`

Снимает ручную паузу медиатеки и пробуждает очередь превью. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def resume_photo_library(source_id: int) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/resume')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), [list_photo_libraries](app.md#symbol-list_photo_libraries), `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-resume_thumbnails"></a>

## `resume_thumbnails`

[app.py](../../app.py) · `resume_thumbnails`

Снимает общую паузу превью и пробуждает воркеры. Использует catalog.set_thumbnail_queue_paused, thumbnail_workers.status, thumbnail_workers.wake.

```python
async def resume_thumbnails() -> dict[str, object]
```

Декораторы: `app.post('/api/thumbnails/resume')`.

Прямые выражения вызова: `catalog.set_thumbnail_queue_paused`, `thumbnail_workers.status`, `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `thumbnail_workers.status()`


<a id="symbol-scan_all_sources"></a>

## `scan_all_sources`

[app.py](../../app.py) · `scan_all_sources`

Запускает сканирование зарегистрированных источников. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def scan_all_sources() -> dict[str, object]
```

Декораторы: `app.post('/api/scan')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `catalog.list_sources`, `catalog.summary`, `int`, `photo_libraries.profile`, `results.append`, `source.get`.

Явные `raise`:

- `HTTPException(status_code=400, detail='Сначала добавь хотя бы один источник')`

Выражения возврата (ветви, без исполнения):

- `{'results': results, 'summary': catalog.summary()}`


<a id="symbol-scan_one_source"></a>

## `scan_one_source`

[app.py](../../app.py) · `scan_one_source`

Проверяет источник и выполняет его ручное сканирование. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def scan_one_source(source_id: int) -> dict[str, object]
```

Декораторы: `app.post('/api/sources/{source_id}/scan')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Источник не найден')`
- `HTTPException(status_code=409, detail=str(error))`
- `HTTPException(status_code=403, detail=str(error))`

Перехватываемые типы: `KeyError`, `PhotosLibraryUnavailable`, `PhotosAccessDenied`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(scan_source, source_id)`


<a id="symbol-scan_source"></a>

## `scan_source`

[app.py](../../app.py) · `scan_source`

Сканирует один источник под отдельной блокировкой и обновляет его состояние. Явно отклоняет недопустимое состояние через KeyError.

```python
def scan_source(source_id: int) -> dict[str, object]
```

Прямые выражения вызова: `'\n'.join`, `KeyError`, `catalog.enqueue_source_thumbnails`, `catalog.get_source`, `catalog.replace_source_scan`, `catalog.set_source_status`, `len`, `lock.acquire`, `lock.release`, `photo_libraries._require_active`, `photo_libraries.scan`, `report.to_dict`, `scan_locks.setdefault`, `scan_sources`, `source.get`, `str`, `threading.Lock`, `thumbnail_workers.wake`.

Явные `raise`:

- `KeyError(source_id)`

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `{'source_id': source_id, 'status': 'already_scanning'}`
- `{'source_id': source_id, 'total': len(assets)}`
- `{'source_id': source_id, **report.to_dict()['summary']}`


<a id="symbol-schedule_scan"></a>

## `schedule_scan`

[app.py](../../app.py) · `schedule_scan`

Ставит сканирование источника в пул из двух потоков Core. Использует catalog.set_source_status, executor.submit.

```python
def schedule_scan(source_id: int) -> None
```

Прямые выражения вызова: `catalog.set_source_status`, `executor.submit`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-set_copy_connection"></a>

## `set_copy_connection`

[app.py](../../app.py) · `set_copy_connection`

Меняет подключение связи с защитой от конфликтующего копирования. Явно отклоняет недопустимое состояние через ValueError.

```python
def set_copy_connection(action, identifier, connected)
```

Прямые выражения вызова: `ValueError`, `action`, `missing_copies.busy`.

Явные `raise`:

- `ValueError('Сначала дождись завершения копирования.')`

Выражения возврата (ветви, без исполнения):

- `action(identifier, connected)`


<a id="symbol-set_folder_copy_source"></a>

## `set_folder_copy_source`

[app.py](../../app.py) · `set_folder_copy_source`

Меняет источник копии под общей блокировкой запуска сверок. Явно отклоняет недопустимое состояние через ValueError.

```python
def set_folder_copy_source(location_id, source_id)
```

Прямые выражения вызова: `ValueError`, `copies.set_copy_source`, `paired_comparison.busy`.

Явные `raise`:

- `ValueError('Сначала приостанови сверку или дождись завершения копирования')`

Выражения возврата (ветви, без исполнения):

- `copies.set_copy_source(location_id, source_id)`


<a id="symbol-set_photos_sync_schedule"></a>

## `set_photos_sync_schedule`

[app.py](../../app.py) · `set_photos_sync_schedule`

Сохраняет часы синхронизации выбранной медиатеки. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def set_photos_sync_schedule(source_id: int, request: PhotosSyncScheduleRequest) -> dict
```

Декораторы: `app.patch('/api/photos/libraries/{source_id}/sync-schedule')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), [list_photo_libraries](app.md#symbol-list_photo_libraries), `request.model_dump`, `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-source_files"></a>

## `source_files`

[app.py](../../app.py) · `source_files`

Возвращает файлы папки источника и повышает приоритет их превью. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def source_files(source_id: int, folder: str='', limit: int=Query(default=300, ge=1, le=1000)) -> dict[str, object]
```

Декораторы: `app.get('/api/sources/{source_id}/files')`.

Прямые выражения вызова: `HTTPException`, `catalog.get_source`, `catalog.list_files`, `catalog.prioritize_folder_thumbnails`, `catalog.revision`, `thumbnail_workers.wake`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Источник не найден')`

Выражения возврата (ветви, без исполнения):

- `{'files': catalog.list_files(source_id, folder=folder, limit=limit), 'folder': folder, 'revision': catalog.revision()}`


<a id="symbol-source_tree"></a>

## `source_tree`

[app.py](../../app.py) · `source_tree`

Возвращает дерево виртуальных папок зарегистрированного источника. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def source_tree(source_id: int) -> dict[str, object]
```

Декораторы: `app.get('/api/sources/{source_id}/tree')`.

Прямые выражения вызова: `HTTPException`, `catalog.folder_tree`, `catalog.get_source`, `catalog.revision`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Источник не найден')`

Выражения возврата (ветви, без исполнения):

- `{'nodes': catalog.folder_tree(source_id), 'revision': catalog.revision()}`


<a id="symbol-start_comparison"></a>

## `start_comparison`

[app.py](../../app.py) · `start_comparison`

Создаёт общую сверку имён исходной области и выбранных целей. Асинхронно ожидает: comparison_call.

```python
async def start_comparison(request: ComparisonRequest) -> dict
```

Декораторы: `app.post('/api/storage/comparisons', status_code=201)`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call), `request.source.model_dump`, `t.model_dump`.

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, comparison.create, request.source.model_dump(), [t.model_dump() for t in request.targets], reuse_index=request.reuse_index)`


<a id="symbol-start_comparison_exclusive"></a>

## `start_comparison_exclusive`

[app.py](../../app.py) · `start_comparison_exclusive`

Проверяет отсутствие конфликтующей работы под общей блокировкой запуска. Явно отклоняет недопустимое состояние через ValueError.

```python
def start_comparison_exclusive(action, *args, **kwargs)
```

Прямые выражения вызова: `ValueError`, `action`, `paired_comparison.busy`.

Явные `raise`:

- `ValueError('Сверка пары ещё выполняется. Сначала останови её.')`

Выражения возврата (ветви, без исполнения):

- `action(*args, **kwargs)`


<a id="symbol-start_missing_copy"></a>

## `start_missing_copy`

[app.py](../../app.py) · `start_missing_copy`

Запускает подтверждённую операцию создания отсутствующих копий. Асинхронно ожидает: comparison_call.

```python
async def start_missing_copy(operation_id: str) -> dict
```

Декораторы: `app.post('/api/storage/copy-operations/{operation_id}/start')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, missing_copies.start, operation_id)`


<a id="symbol-start_paired_comparison"></a>

## `start_paired_comparison`

[app.py](../../app.py) · `start_paired_comparison`

Создаёт и запускает сверку зарегистрированной пары папок. Асинхронно ожидает: comparison_call.

```python
async def start_paired_comparison(request: PairedComparisonRequest) -> dict
```

Декораторы: `app.post('/api/storage/paired-comparisons', status_code=201)`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, paired_comparison.create, request.copy_id, request.mode, request.base_job_id, method=request.method)`


<a id="symbol-start_photo_originals"></a>

## `start_photo_originals`

[app.py](../../app.py) · `start_photo_originals`

Запускает или планирует сохранение оригиналов в цепочку копий Photos. Асинхронно ожидает: library_call.

```python
async def start_photo_originals(source_id: int, link_id: str) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/copies/{link_id}/originals/start')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call).

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_originals.start, link_id, source_id)`


<a id="symbol-stop_missing_copy"></a>

## `stop_missing_copy`

[app.py](../../app.py) · `stop_missing_copy`

Запрашивает остановку операции копирования. Асинхронно ожидает: comparison_call.

```python
async def stop_missing_copy(operation_id: str) -> dict
```

Декораторы: `app.post('/api/storage/copy-operations/{operation_id}/stop')`.

Прямые выражения вызова: [comparison_call](app.md#symbol-comparison_call).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(missing_copies.stop, operation_id)`


<a id="symbol-storage_acknowledge_folder_changes"></a>

## `storage_acknowledge_folder_changes`

[app.py](../../app.py) · `storage_acknowledge_folder_changes`

Подтверждает конкретную версию уведомления об изменении папки. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_acknowledge_folder_changes(group_id: str, request: CopyGroupAcknowledgeRequest) -> dict
```

Декораторы: `app.post('/api/storage/copy-groups/{group_id}/acknowledge')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.acknowledge_changes, group_id, request.changed_at)`


<a id="symbol-storage_copy_group_connection"></a>

## `storage_copy_group_connection`

[app.py](../../app.py) · `storage_copy_group_connection`

Меняет подключение всего набора папок. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_group_connection(group_id: str, request: CopyConnectionRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-groups/{group_id}/connection')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action), `folder_tracking.wake`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-storage_copy_group_settings"></a>

## `storage_copy_group_settings`

[app.py](../../app.py) · `storage_copy_group_settings`

Обновляет настройки набора и пробуждает отслеживание изменений. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_group_settings(group_id: str, request: CopyGroupSettingsRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-groups/{group_id}')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action), `folder_tracking.wake`, `request.model_dump`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-storage_copy_groups"></a>

## `storage_copy_groups`

[app.py](../../app.py) · `storage_copy_groups`

Возвращает наборы папок с типами, метками и состоянием наблюдателей. Поля результата: groups, kinds, labels.

```python
async def storage_copy_groups() -> dict
```

Декораторы: `app.get('/api/storage/copy-groups')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action), `dict`, `folder_tracking.status`.

Выражения возврата (ветви, без исполнения):

- `{'groups': [dict(group, **folder_tracking.status(group['id'])) for group in groups], 'kinds': COPY_KINDS, 'labels': FOLDER_LABELS}`


<a id="symbol-storage_copy_kind"></a>

## `storage_copy_kind`

[app.py](../../app.py) · `storage_copy_kind`

Меняет тип зарегистрированной копии. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_kind(location_id: str, request: CopyKindRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-locations/{location_id}')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.change_kind, location_id, request.kind)`


<a id="symbol-storage_copy_location"></a>

## `storage_copy_location`

[app.py](../../app.py) · `storage_copy_location`

Добавляет папку копии к существующему набору. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_location(group_id: str, request: CopyLocationRequest) -> dict
```

Декораторы: `app.post('/api/storage/copy-groups/{group_id}/copies')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.add_copy, group_id, request.volume_id, request.path, request.kind)`


<a id="symbol-storage_copy_location_connection"></a>

## `storage_copy_location_connection`

[app.py](../../app.py) · `storage_copy_location_connection`

Меняет подключение одной обычной копии. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_location_connection(location_id: str, request: CopyConnectionRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-locations/{location_id}/connection')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(set_copy_connection, copies.set_copy_connected, location_id, request.connected)`


<a id="symbol-storage_copy_source"></a>

## `storage_copy_source`

[app.py](../../app.py) · `storage_copy_source`

Обрабатывает изменение источника копирования обычной папки. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_source(location_id: str, request: CopySourceRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-locations/{location_id}/source')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(set_folder_copy_source, location_id, request.source_id)`


<a id="symbol-storage_directory"></a>

## `storage_directory`

[app.py](../../app.py) · `storage_directory`

Возвращает список выбранной папки тома с признаками снимка и ошибок. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def storage_directory(volume_id: str, path: str='', refresh: bool=True, discover: bool=True) -> dict
```

Декораторы: `app.get('/api/storage/volumes/{volume_id}/directory')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Том не найден')`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `ValueError`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(storage.directory, volume_id, path, refresh, discover=discover)`


<a id="symbol-storage_directory_sizes"></a>

## `storage_directory_sizes`

[app.py](../../app.py) · `storage_directory_sizes`

Возвращает размеры папок и при разрешении ставит их в очередь подсчёта. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def storage_directory_sizes(volume_id: str, request: DirectorySizesRequest) -> dict
```

Декораторы: `app.post('/api/storage/volumes/{volume_id}/directory-sizes')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Том не найден')`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `(ValueError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(directory_sizes.request, volume_id, request.paths, start=request.start, refresh=request.refresh)`


<a id="symbol-storage_folder_markers"></a>

## `storage_folder_markers`

[app.py](../../app.py) · `storage_folder_markers`

Возвращает состояние очереди служебных описаний папок. Асинхронно ожидает: asyncio.to_thread.

```python
async def storage_folder_markers() -> dict
```

Декораторы: `app.get('/api/storage/folder-markers')`.

Прямые выражения вызова: `asyncio.to_thread`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(folder_markers.status)`


<a id="symbol-storage_folder_tags"></a>

## `storage_folder_tags`

[app.py](../../app.py) · `storage_folder_tags`

Сохраняет смысловые метки выбранной папки. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def storage_folder_tags(volume_id: str, request: FolderTagsRequest) -> dict
```

Декораторы: `app.patch('/api/storage/volumes/{volume_id}/folder-tags')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Том не найден')`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `ValueError`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(storage.set_folder_tags, volume_id, request.path, request.tags)`


<a id="symbol-storage_main_folder"></a>

## `storage_main_folder`

[app.py](../../app.py) · `storage_main_folder`

Регистрирует выбранную папку как основную область набора. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_main_folder(request: ComparisonScope) -> dict
```

Декораторы: `app.post('/api/storage/copy-groups')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.create_main, request.volume_id, request.path)`


<a id="symbol-storage_metadata"></a>

## `storage_metadata`

[app.py](../../app.py) · `storage_metadata`

Сохраняет пользовательские отметки расположения в каталоге. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def storage_metadata(volume_id: str, request: StorageMetadataRequest) -> dict
```

Декораторы: `app.patch('/api/storage/volumes/{volume_id}/metadata')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `request.model_dump`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Том не найден')`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `ValueError`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(storage.annotate, volume_id, request.path, request.model_dump(exclude={'path'}))`


<a id="symbol-storage_preview"></a>

## `storage_preview`

[app.py](../../app.py) · `storage_preview`

Возвращает JPEG-превью обычного файла выбранного тома. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def storage_preview(volume_id: str, path: str, large: bool=False) -> FileResponse
```

Декораторы: `app.get('/api/storage/volumes/{volume_id}/preview')`.

Прямые выражения вызова: `FileResponse`, `HTTPException`, `asyncio.to_thread`, `str`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Том не найден')`
- `HTTPException(status_code=503, detail=str(error))`
- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `KeyError`, `ThumbnailCacheUnavailable`, `(ValueError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `FileResponse(target, media_type='image/jpeg', headers={'Cache-Control': 'no-cache'})`


<a id="symbol-storage_release_copy_number"></a>

## `storage_release_copy_number`

[app.py](../../app.py) · `storage_release_copy_number`

Архивирует прежнюю привязку и освобождает её номер. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_release_copy_number(location_id: str, request: CopyNumberReleaseRequest) -> dict
```

Декораторы: `app.post('/api/storage/copy-locations/{location_id}/release-number')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(release_copy_number, location_id, request.number, request.kind)`


<a id="symbol-storage_remove_copy"></a>

## `storage_remove_copy`

[app.py](../../app.py) · `storage_remove_copy`

Удаляет связь копии из каталога без удаления пользовательских файлов. Поля результата: removed.

```python
async def storage_remove_copy(location_id: str) -> dict
```

Декораторы: `app.delete('/api/storage/copy-locations/{location_id}')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `{'removed': True}`


<a id="symbol-storage_remove_copy_group"></a>

## `storage_remove_copy_group`

[app.py](../../app.py) · `storage_remove_copy_group`

Удаляет набор папок из каталога без удаления пользовательских файлов. Поля результата: removed.

```python
async def storage_remove_copy_group(group_id: str) -> dict
```

Декораторы: `app.delete('/api/storage/copy-groups/{group_id}')`.

Прямые выражения вызова: [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `{'removed': True}`


<a id="symbol-storage_renumber_copies"></a>

## `storage_renumber_copies`

[app.py](../../app.py) · `storage_renumber_copies`

Применяет подтверждённую нумерацию по снимку текущих связей. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_renumber_copies(group_id: str, request: CopyRenumberRequest) -> dict
```

Декораторы: `app.post('/api/storage/copy-groups/{group_id}/renumber')`.

Прямые выражения вызова: `copy.model_dump`, [copy_catalog_action](app.md#symbol-copy_catalog_action).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.renumber_copies, group_id, [copy.model_dump() for copy in request.copies])`


<a id="symbol-storage_volumes"></a>

## `storage_volumes`

[app.py](../../app.py) · `storage_volumes`

Возвращает обнаруженные и сохранённые тома через API Core. Асинхронно ожидает: asyncio.to_thread.

```python
async def storage_volumes(refresh: bool=False) -> dict
```

Декораторы: `app.get('/api/storage/volumes')`.

Прямые выражения вызова: `asyncio.to_thread`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(storage.refresh, refresh)`


<a id="symbol-thumbnail_status"></a>

## `thumbnail_status`

[app.py](../../app.py) · `thumbnail_status`

Возвращает очередь превью и диагностическое состояние её воркеров. Использует thumbnail_workers.status.

```python
async def thumbnail_status() -> dict[str, object]
```

Декораторы: `app.get('/api/thumbnails/status')`.

Прямые выражения вызова: `thumbnail_workers.status`.

Выражения возврата (ветви, без исполнения):

- `thumbnail_workers.status()`


<a id="symbol-unbind_photo_library_copy"></a>

## `unbind_photo_library_copy`

[app.py](../../app.py) · `unbind_photo_library_copy`

Отключает привязку копии медиатеки и возвращает обновлённый список. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def unbind_photo_library_copy(source_id: int, link_id: str) -> dict
```

Декораторы: `app.delete('/api/photos/libraries/{source_id}/copies/{link_id}')`.

Прямые выражения вызова: [library_call](app.md#symbol-library_call), [list_photo_libraries](app.md#symbol-list_photo_libraries).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-update_source"></a>

## `update_source`

[app.py](../../app.py) · `update_source`

Обновляет роль, название и комментарий обычного источника. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def update_source(source_id: int, request: SourceMetadataRequest) -> dict[str, object]
```

Декораторы: `app.patch('/api/sources/{source_id}')`.

Прямые выражения вызова: `HTTPException`, `catalog.list_sources`, `catalog.update_source_metadata`.

Явные `raise`:

- `HTTPException(status_code=404, detail='Папка не найдена')`

Перехватываемые типы: `KeyError`.

Выражения возврата (ветви, без исполнения):

- `{'source': source, 'sources': catalog.list_sources()}`
