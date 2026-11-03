# Core API и жизненный цикл: `app.py`

Композиционный корень Core: создаёт сервисы, определяет Pydantic-контракты и маршруты FastAPI, связывает фоновые службы и переводит ошибки домена в HTTP.

[Исходный модуль](../../app.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/catalog.py](media_manager--catalog.md), [media_manager/comparison.py](media_manager--comparison.md), [media_manager/copies.py](media_manager--copies.md), [media_manager/copy_files.py](media_manager--copy_files.md), [media_manager/directory_sizes.py](media_manager--directory_sizes.md), [media_manager/folder_markers.py](media_manager--folder_markers.md), [media_manager/folder_tracking.py](media_manager--folder_tracking.md), [media_manager/network.py](media_manager--network.md), [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [media_manager/photo_libraries.py](media_manager--photo_libraries.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md), [media_manager/photos_browser.py](media_manager--photos_browser.md), [media_manager/photos_originals.py](media_manager--photos_originals.md), [media_manager/photos_schedule.py](media_manager--photos_schedule.md), [media_manager/scanner.py](media_manager--scanner.md), [media_manager/storage.py](media_manager--storage.md), [media_manager/storage_previews.py](media_manager--storage_previews.md), [media_manager/thumbnail_workers.py](media_manager--thumbnail_workers.md), [media_manager/thumbnails.py](media_manager--thumbnails.md), [media_manager/watcher.py](media_manager--watcher.md).
Импортируется модулями: нет прямых импортов; см. запуск через `-m`, пакет или внешнюю конфигурацию.
Тестовые модули с прямым импортом: [tests/test_copy_connections.py](../../tests/test_copy_connections.py#L140), [tests/test_copy_files.py](../../tests/test_copy_files.py#L316), [tests/test_copy_number_release.py](../../tests/test_copy_number_release.py#L187), [tests/test_folder_tags.py](../../tests/test_folder_tags.py#L85), [tests/test_folder_tracking.py](../../tests/test_folder_tracking.py#L135), [tests/test_photos_schedule.py](../../tests/test_photos_schedule.py#L224), [tests/test_volume_identity.py](../../tests/test_volume_identity.py#L195).

## Оглавление определений

- [local_thumbnail_cache_directory](#symbol-local-thumbnail-cache-directory) — Выбирает каталог превью из config.local.json либо MEDIA_ACTU_DATA_DIR.
- [scan_source](#symbol-scan-source) — Сканирует один источник под отдельной блокировкой и обновляет его состояние.
- [schedule_scan](#symbol-schedule-scan) — Ставит сканирование источника в пул из двух потоков Core.
- [lifespan](#symbol-lifespan) — Запускает фоновые службы FastAPI и закрывает их при завершении Core.
- [lifespan.monitor_libraries](#symbol-lifespan-monitor-libraries) — Проверяет подключение Photos каждые 30 секунд и пробуждает очередь превью.
- [SourceRequest](#symbol-sourcerequest) — Определяет Pydantic-контракт регистрации обычного источника.
- [FolderChoiceRequest](#symbol-folderchoicerequest) — Определяет Pydantic-контракт выбора папок macOS.
- [SourceMetadataRequest](#symbol-sourcemetadatarequest) — Определяет Pydantic-контракт изменения метаданных источника.
- [FolderRequest](#symbol-folderrequest) — Определяет Pydantic-контракт открытия папки источника.
- [choose_folders_macos](#symbol-choose-folders-macos) — Открывает системный диалог выбора нескольких папок на машине Core.
- [health](#symbol-health) — Возвращает готовность HTTP-процесса и текущую ревизию каталога.
- [StorageMetadataRequest](#symbol-storagemetadatarequest) — Определяет Pydantic-контракт отметок файлового расположения.
- [FolderTagsRequest](#symbol-foldertagsrequest) — Определяет Pydantic-контракт меток папки.
- [storage_volumes](#symbol-storage-volumes) — Возвращает обнаруженные и сохранённые тома через API Core.
- [VolumeNameRequest](#symbol-volumenamerequest) — Определяет Pydantic-контракт названия сменного носителя.
- [register_removable](#symbol-register-removable) — Регистрирует сменный носитель с выбранным названием.
- [rename_removable](#symbol-rename-removable) — Меняет название подтверждённого сменного носителя.
- [NetworkShareRequest](#symbol-networksharerequest) — Определяет Pydantic-контракт запоминания SMB-ресурса.
- [remembered_nas](#symbol-remembered-nas) — Возвращает список сохранённых серверов NAS.
- [discover_nas](#symbol-discover-nas) — Запускает обнаружение NAS через Bonjour на машине Core.
- [nas_shares](#symbol-nas-shares) — Возвращает сохранённые либо обновлённые ресурсы выбранного NAS.
- [remember_nas_share](#symbol-remember-nas-share) — Сохраняет выбранный SMB-ресурс без подключения.
- [connect_network_volume](#symbol-connect-network-volume) — Открывает подключение сетевого тома в Finder на машине Core.
- [storage_directory](#symbol-storage-directory) — Возвращает список выбранной папки тома с признаками снимка и ошибок.
- [storage_preview](#symbol-storage-preview) — Возвращает JPEG-превью обычного файла выбранного тома.
- [StoragePathRequest](#symbol-storagepathrequest) — Определяет Pydantic-контракт открытия пути тома.
- [DirectorySizesRequest](#symbol-directorysizesrequest) — Определяет Pydantic-контракт подсчёта размеров папок.
- [storage_directory_sizes](#symbol-storage-directory-sizes) — Возвращает размеры папок и при разрешении ставит их в очередь подсчёта.
- [open_storage_path_in_finder](#symbol-open-storage-path-in-finder) — Передаёт Finder проверенный путь выбранного тома.
- [storage_metadata](#symbol-storage-metadata) — Сохраняет пользовательские отметки расположения в каталоге.
- [storage_folder_tags](#symbol-storage-folder-tags) — Сохраняет смысловые метки выбранной папки.
- [ComparisonScope](#symbol-comparisonscope) — Определяет Pydantic-контракт области сверки на файловом томе.
- [CopyLocationRequest](#symbol-copylocationrequest) — Определяет Pydantic-контракт привязки папки-копии.
- [CopyKindRequest](#symbol-copykindrequest) — Определяет Pydantic-контракт типа копии.
- [CopyNumberSnapshot](#symbol-copynumbersnapshot) — Определяет Pydantic-контракт снимка текущего номера копии.
- [CopyNumberReleaseRequest](#symbol-copynumberreleaserequest) — Определяет Pydantic-контракт освобождения номера копии.
- [CopyRenumberRequest](#symbol-copyrenumberrequest) — Определяет Pydantic-контракт перенумерации копий.
- [CopyGroupSettingsRequest](#symbol-copygroupsettingsrequest) — Определяет Pydantic-контракт настроек основной папки.
- [CopyGroupAcknowledgeRequest](#symbol-copygroupacknowledgerequest) — Определяет Pydantic-контракт подтверждения версии изменения.
- [CopyConnectionRequest](#symbol-copyconnectionrequest) — Определяет Pydantic-контракт подключения или отключения связи.
- [CopySourceRequest](#symbol-copysourcerequest) — Определяет Pydantic-контракт выбора источника копирования.
- [set_folder_copy_source](#symbol-set-folder-copy-source) — Меняет источник копии под общей блокировкой запуска сверок.
- [storage_copy_source](#symbol-storage-copy-source) — Обрабатывает изменение источника копирования обычной папки.
- [set_copy_connection](#symbol-set-copy-connection) — Меняет подключение связи с защитой от конфликтующего копирования.
- [copy_catalog_action](#symbol-copy-catalog-action) — Выполняет команду каталога копий в потоке и пробуждает запись маркеров.
- [storage_copy_groups](#symbol-storage-copy-groups) — Возвращает наборы папок с типами, метками и состоянием наблюдателей.
- [storage_folder_markers](#symbol-storage-folder-markers) — Возвращает состояние очереди служебных описаний папок.
- [storage_main_folder](#symbol-storage-main-folder) — Регистрирует выбранную папку как основную область набора.
- [storage_copy_group_settings](#symbol-storage-copy-group-settings) — Обновляет настройки набора и пробуждает отслеживание изменений.
- [storage_acknowledge_folder_changes](#symbol-storage-acknowledge-folder-changes) — Подтверждает конкретную версию уведомления об изменении папки.
- [storage_copy_group_connection](#symbol-storage-copy-group-connection) — Меняет подключение всего набора папок.
- [storage_copy_location_connection](#symbol-storage-copy-location-connection) — Меняет подключение одной обычной копии.
- [storage_copy_location](#symbol-storage-copy-location) — Добавляет папку копии к существующему набору.
- [release_copy_number](#symbol-release-copy-number) — Освобождает подтверждённый номер под блокировкой запуска сверок.
- [storage_release_copy_number](#symbol-storage-release-copy-number) — Архивирует прежнюю привязку и освобождает её номер.
- [storage_copy_kind](#symbol-storage-copy-kind) — Меняет тип зарегистрированной копии.
- [storage_renumber_copies](#symbol-storage-renumber-copies) — Применяет подтверждённую нумерацию по снимку текущих связей.
- [storage_remove_copy](#symbol-storage-remove-copy) — Удаляет связь копии из каталога без удаления пользовательских файлов.
- [storage_remove_copy_group](#symbol-storage-remove-copy-group) — Удаляет набор папок из каталога без удаления пользовательских файлов.
- [ComparisonRequest](#symbol-comparisonrequest) — Определяет Pydantic-контракт общей сверки имён.
- [comparison_call](#symbol-comparison-call) — Выполняет команду сверки в потоке и преобразует доменные ошибки в HTTP.
- [start_comparison_exclusive](#symbol-start-comparison-exclusive) — Проверяет отсутствие конфликтующей работы под общей блокировкой запуска.
- [PairedComparisonRequest](#symbol-pairedcomparisonrequest) — Определяет Pydantic-контракт сверки связанной пары.
- [PairedDecisionRequest](#symbol-paireddecisionrequest) — Определяет Pydantic-контракт планового решения для лишнего элемента.
- [paired_jobs](#symbol-paired-jobs) — Возвращает историю парных сверок и допустимые решения для лишних элементов.
- [start_paired_comparison](#symbol-start-paired-comparison) — Создаёт и запускает сверку зарегистрированной пары папок.
- [paired_job](#symbol-paired-job) — Возвращает состояние одной парной сверки.
- [paired_rows](#symbol-paired-rows) — Возвращает страницу выровненных строк парной сверки.
- [pause_paired_job](#symbol-pause-paired-job) — Запрашивает паузу парной сверки.
- [resume_paired_job](#symbol-resume-paired-job) — Продолжает парную сверку после проверки конфликтующих операций.
- [paired_decision](#symbol-paired-decision) — Сохраняет плановое решение для элемента только в копии.
- [comparison_jobs](#symbol-comparison-jobs) — Возвращает историю общей сверки имён и старых отчётов.
- [missing_copy_plan](#symbol-missing-copy-plan) — Создаёт сохранённый план копирования по завершённому файловому отчёту.
- [missing_copy_job](#symbol-missing-copy-job) — Возвращает состояние операции копирования отсутствующих элементов.
- [missing_copy_items](#symbol-missing-copy-items) — Возвращает страницу элементов сохранённого плана копирования.
- [start_missing_copy](#symbol-start-missing-copy) — Запускает подтверждённую операцию создания отсутствующих копий.
- [stop_missing_copy](#symbol-stop-missing-copy) — Запрашивает остановку операции копирования.
- [start_comparison](#symbol-start-comparison) — Создаёт общую сверку имён исходной области и выбранных целей.
- [comparison_job](#symbol-comparison-job) — Возвращает состояние и области общей сверки.
- [pause_comparison](#symbol-pause-comparison) — Запрашивает паузу общей сверки имён.
- [resume_comparison](#symbol-resume-comparison) — Продолжает сверку имён либо создаёт новую вместо старой проверки содержимого.
- [comparison_tree](#symbol-comparison-tree) — Возвращает страницу исходного дерева общей сверки с фильтром статуса.
- [comparison_target_tree](#symbol-comparison-target-tree) — Возвращает страницу сохранённого дерева выбранной цели общей сверки.
- [comparison_detail](#symbol-comparison-detail) — Возвращает найденные совпадения и подробности элемента отчёта.
- [comparison_events](#symbol-comparison-events) — Возвращает события общей сверки с обратной пагинацией.
- [list_sources](#symbol-list-sources) — Возвращает сохранённые источники медиаиндекса.
- [create_source](#symbol-create-source) — Регистрирует обычный источник, устанавливает наблюдение и запускает сканирование.
- [choose_sources](#symbol-choose-sources) — Регистрирует выбранные системным диалогом папки и запускает их сканирование.
- [update_source](#symbol-update-source) — Обновляет роль, название и комментарий обычного источника.
- [delete_source](#symbol-delete-source) — Снимает наблюдение и удаляет источник из медиаиндекса.
- [scan_one_source](#symbol-scan-one-source) — Проверяет источник и выполняет его ручное сканирование.
- [scan_all_sources](#symbol-scan-all-sources) — Запускает сканирование зарегистрированных источников.
- [authorize_system_photos](#symbol-authorize-system-photos) — Запрашивает разрешение Photos и возвращает состояние доступа.
- [library_call](#symbol-library-call) — Выполняет команду Photos в потоке с переводом ошибок доступа в HTTP.
- [LibraryNameRequest](#symbol-librarynamerequest) — Определяет Pydantic-контракт названия медиатеки.
- [LibraryCopyRequest](#symbol-librarycopyrequest) — Определяет Pydantic-контракт папки-копии медиатеки.
- [PhotosSyncScheduleRequest](#symbol-photossyncschedulerequest) — Определяет Pydantic-контракт временного окна Photos.
- [set_photos_sync_schedule](#symbol-set-photos-sync-schedule) — Сохраняет часы синхронизации выбранной медиатеки.
- [list_photo_libraries](#symbol-list-photo-libraries) — Возвращает медиатеки, состояние подключения, превью и привязанные копии.
- [connect_photo_library](#symbol-connect-photo-library) — Повторяет сопоставление системной медиатеки и пробуждает превью.
- [browse_photo_library](#symbol-browse-photo-library) — Возвращает виртуальную папку Photos и повышает приоритет её превью.
- [photo_preview_status](#symbol-photo-preview-status) — Возвращает готовые превью выбранных объектов медиатеки.
- [register_photo_library](#symbol-register-photo-library) — Регистрирует текущую медиатеку и ставит её первый скан в очередь.
- [rename_photo_library](#symbol-rename-photo-library) — Меняет название медиатеки и возвращает обновлённый список.
- [pause_photo_library](#symbol-pause-photo-library) — Включает ручную паузу выбранной медиатеки.
- [resume_photo_library](#symbol-resume-photo-library) — Снимает ручную паузу медиатеки и пробуждает очередь превью.
- [bind_photo_library_copy](#symbol-bind-photo-library-copy) — Привязывает выбранную папку как копию медиатеки.
- [unbind_photo_library_copy](#symbol-unbind-photo-library-copy) — Отключает привязку копии медиатеки и возвращает обновлённый список.
- [photo_copy_source](#symbol-photo-copy-source) — Меняет источник привязанной копии Photos.
- [photo_copy_first](#symbol-photo-copy-first) — Ставит выбранную копию Photos первой по номеру без изменения маршрутов.
- [start_photo_originals](#symbol-start-photo-originals) — Запускает или планирует сохранение оригиналов в цепочку копий Photos.
- [pause_photo_originals](#symbol-pause-photo-originals) — Запрашивает паузу сохранения оригиналов выбранной медиатеки.
- [photo_originals_status](#symbol-photo-originals-status) — Возвращает состояние оригиналов после проверки принадлежности копии медиатеке.
- [photo_originals_journal](#symbol-photo-originals-journal) — Возвращает журнал оригиналов и пути незавершённых записей.
- [catalog_summary](#symbol-catalog-summary) — Возвращает суммарные показатели сохранённого медиаиндекса.
- [source_tree](#symbol-source-tree) — Возвращает дерево виртуальных папок зарегистрированного источника.
- [source_files](#symbol-source-files) — Возвращает файлы папки источника и повышает приоритет их превью.
- [thumbnail_status](#symbol-thumbnail-status) — Возвращает очередь превью и диагностическое состояние её воркеров.
- [pause_thumbnails](#symbol-pause-thumbnails) — Сохраняет общую ручную паузу фоновой очереди превью.
- [resume_thumbnails](#symbol-resume-thumbnails) — Снимает общую паузу превью и пробуждает воркеры.
- [open_source_folder_in_finder](#symbol-open-source-folder-in-finder) — Открывает проверенную папку обычного источника в Finder.
- [media_thumbnail](#symbol-media-thumbnail) — Отдаёт только готовый JPEG из кэша медиаиндекса.
- [open_media_in_default_app](#symbol-open-media-in-default-app) — Открывает обычный файл системной командой или выделяет объект Photos.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [ROOT](../../app.py#L44) | `Path(__file__).parent` |
| [DATA_DIR](../../app.py#L45) | `Path(os.environ.get('MEDIA_ACTU_DATA_DIR', str(ROOT / 'data'))).expanduser()` |

<a id="symbol-local-thumbnail-cache-directory"></a>

## `local_thumbnail_cache_directory`

[app.py:50](../../app.py#L50)

Выбирает каталог превью из config.local.json либо MEDIA_ACTU_DATA_DIR. Использует Path, Path(str(configured)).expanduser, config_path.is_file, config_path.read_text, json.loads.

```python
def local_thumbnail_cache_directory() -> Path
```

Прямые выражения вызова: `Path`, `Path(str(configured)).expanduser`, `config_path.is_file`, `config_path.read_text`, `json.loads`, `settings.get`, `str`.

Выражения возврата (ветви, без исполнения):

- `DATA_DIR / 'thumbnails'`
- `Path(str(configured)).expanduser() if configured else DATA_DIR / 'thumbnails'`


<a id="symbol-scan-source"></a>

## `scan_source`

[app.py:86](../../app.py#L86)

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


<a id="symbol-schedule-scan"></a>

## `schedule_scan`

[app.py:120](../../app.py#L120)

Ставит сканирование источника в пул из двух потоков Core. Использует catalog.set_source_status, executor.submit.

```python
def schedule_scan(source_id: int) -> None
```

Прямые выражения вызова: `catalog.set_source_status`, `executor.submit`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-lifespan"></a>

## `lifespan`

[app.py:131](../../app.py#L131)

Запускает фоновые службы FastAPI и закрывает их при завершении Core. Асинхронно ожидает: asyncio.to_thread.

```python
async def lifespan(_: FastAPI)
```

Декораторы: `asynccontextmanager`.

Прямые выражения вызова: `Path`, `asyncio.create_task`, `asyncio.to_thread`, `catalog.list_sources`, `catalog.reset_stale_source_scans`, `comparison.close`, `directory_sizes.close`, `executor.shutdown`, `folder_markers.close`, `folder_markers.start`, `folder_tracking.close`, `folder_tracking.start`, `int`, `missing_copies.close`, [monitor_libraries](../../app.py#L155), `paired_comparison.close`, `photo_libraries.profile`, `photos_adapter.close`, `photos_monitor.cancel`, `photos_originals.close`, `photos_schedule.close`, `photos_schedule.start`, [schedule_scan](../../app.py#L120), `source.get`, `source_path.is_dir`, `str`, `thumbnail_workers.start`, `thumbnail_workers.stop`, `watcher.start`, `watcher.stop`, `watcher.watch`.

Передаёт управление через `yield`; ресурс и освобождение см. в теле контекстного менеджера.


<a id="symbol-lifespan-monitor-libraries"></a>

## `lifespan.monitor_libraries`

[app.py:155](../../app.py#L155)

Проверяет подключение Photos каждые 30 секунд и пробуждает очередь превью. Асинхронно ожидает: asyncio.sleep, asyncio.to_thread.

```python
async def monitor_libraries()
```

Прямые выражения вызова: `asyncio.sleep`, `asyncio.to_thread`, `photo_libraries.connection.get`, `thumbnail_workers.wake`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-sourcerequest"></a>

## `SourceRequest`

[app.py:190](../../app.py#L190)

Определяет Pydantic-контракт регистрации обычного источника. Поля: path, role, label, comment.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `обязательное поле` |
| `role` | `Literal['source', 'storage']` | `'source'` |
| `label` | `str` | `''` |
| `comment` | `str` | `''` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-folderchoicerequest"></a>

## `FolderChoiceRequest`

[app.py:199](../../app.py#L199)

Определяет Pydantic-контракт выбора папок macOS. Поля: role, label, comment.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `role` | `Literal['source', 'storage']` | `'source'` |
| `label` | `str` | `''` |
| `comment` | `str` | `''` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-sourcemetadatarequest"></a>

## `SourceMetadataRequest`

[app.py:207](../../app.py#L207)

Определяет Pydantic-контракт изменения метаданных источника. Поля: role, label, comment.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `role` | `Literal['source', 'storage']` | `обязательное поле` |
| `label` | `str` | `''` |
| `comment` | `str` | `''` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-folderrequest"></a>

## `FolderRequest`

[app.py:215](../../app.py#L215)

Определяет Pydantic-контракт открытия папки источника. Поля: folder.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `folder` | `str` | `''` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-choose-folders-macos"></a>

## `choose_folders_macos`

[app.py:221](../../app.py#L221)

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


<a id="symbol-health"></a>

## `health`

[app.py:247](../../app.py#L247)

Возвращает готовность HTTP-процесса и текущую ревизию каталога. Поля результата: status, revision.

```python
async def health() -> dict[str, object]
```

Декораторы: `app.get('/health')`.

Прямые выражения вызова: `catalog.revision`.

Выражения возврата (ветви, без исполнения):

- `{'status': 'ok', 'revision': catalog.revision()}`


<a id="symbol-storagemetadatarequest"></a>

## `StorageMetadataRequest`

[app.py:253](../../app.py#L253)

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

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-foldertagsrequest"></a>

## `FolderTagsRequest`

[app.py:265](../../app.py#L265)

Определяет Pydantic-контракт меток папки. Поля: path, tags.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `Field(default='', max_length=4096)` |
| `tags` | `list[Literal['old_copy', 'sort', 'check']]` | `Field(max_length=3)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-storage-volumes"></a>

## `storage_volumes`

[app.py:274](../../app.py#L274)

Возвращает обнаруженные и сохранённые тома через API Core. Асинхронно ожидает: asyncio.to_thread.

```python
async def storage_volumes(refresh: bool=False) -> dict
```

Декораторы: `app.get('/api/storage/volumes')`.

Прямые выражения вызова: `asyncio.to_thread`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(storage.refresh, refresh)`


<a id="symbol-volumenamerequest"></a>

## `VolumeNameRequest`

[app.py:280](../../app.py#L280)

Определяет Pydantic-контракт названия сменного носителя. Поля: name.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `name` | `str` | `Field(min_length=1, max_length=120)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-register-removable"></a>

## `register_removable`

[app.py:288](../../app.py#L288)

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


<a id="symbol-rename-removable"></a>

## `rename_removable`

[app.py:298](../../app.py#L298)

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


<a id="symbol-networksharerequest"></a>

## `NetworkShareRequest`

[app.py:307](../../app.py#L307)

Определяет Pydantic-контракт запоминания SMB-ресурса. Поля: share.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `share` | `str` | `Field(min_length=1, max_length=255)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-remembered-nas"></a>

## `remembered_nas`

[app.py:315](../../app.py#L315)

Возвращает список сохранённых серверов NAS. Асинхронно ожидает: asyncio.to_thread.

```python
async def remembered_nas() -> dict
```

Декораторы: `app.get('/api/storage/nas')`.

Прямые выражения вызова: `asyncio.to_thread`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(network.servers)`


<a id="symbol-discover-nas"></a>

## `discover_nas`

[app.py:322](../../app.py#L322)

Запускает обнаружение NAS через Bonjour на машине Core. Асинхронно ожидает: asyncio.to_thread.

```python
async def discover_nas() -> dict
```

Декораторы: `app.post('/api/storage/nas/discover')`.

Прямые выражения вызова: `asyncio.to_thread`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(network.scan)`


<a id="symbol-nas-shares"></a>

## `nas_shares`

[app.py:329](../../app.py#L329)

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


<a id="symbol-remember-nas-share"></a>

## `remember_nas_share`

[app.py:339](../../app.py#L339)

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


<a id="symbol-connect-network-volume"></a>

## `connect_network_volume`

[app.py:351](../../app.py#L351)

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


<a id="symbol-storage-directory"></a>

## `storage_directory`

[app.py:363](../../app.py#L363)

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


<a id="symbol-storage-preview"></a>

## `storage_preview`

[app.py:375](../../app.py#L375)

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


<a id="symbol-storagepathrequest"></a>

## `StoragePathRequest`

[app.py:389](../../app.py#L389)

Определяет Pydantic-контракт открытия пути тома. Поля: path.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `Field(default='', max_length=4096)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-directorysizesrequest"></a>

## `DirectorySizesRequest`

[app.py:396](../../app.py#L396)

Определяет Pydantic-контракт подсчёта размеров папок. Поля: paths, start, refresh.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `paths` | `list[str]` | `Field(min_length=1, max_length=500)` |
| `start` | `bool` | `True` |
| `refresh` | `bool` | `False` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-storage-directory-sizes"></a>

## `storage_directory_sizes`

[app.py:406](../../app.py#L406)

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


<a id="symbol-open-storage-path-in-finder"></a>

## `open_storage_path_in_finder`

[app.py:419](../../app.py#L419)

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


<a id="symbol-storage-metadata"></a>

## `storage_metadata`

[app.py:431](../../app.py#L431)

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


<a id="symbol-storage-folder-tags"></a>

## `storage_folder_tags`

[app.py:443](../../app.py#L443)

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


<a id="symbol-comparisonscope"></a>

## `ComparisonScope`

[app.py:454](../../app.py#L454)

Определяет Pydantic-контракт области сверки на файловом томе. Поля: volume_id, path.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `volume_id` | `str` | `Field(min_length=1, max_length=128)` |
| `path` | `str` | `Field(default='', max_length=4096)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-copylocationrequest"></a>

## `CopyLocationRequest`

[app.py:462](../../app.py#L462)

Определяет Pydantic-контракт привязки папки-копии. Поля: kind.

Базовые классы: `ComparisonScope`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `kind` | `Literal['copy', 'cold', 'cloud']` | `'copy'` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-copykindrequest"></a>

## `CopyKindRequest`

[app.py:468](../../app.py#L468)

Определяет Pydantic-контракт типа копии. Поля: kind.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `kind` | `Literal['copy', 'cold', 'cloud']` | `обязательное поле` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-copynumbersnapshot"></a>

## `CopyNumberSnapshot`

[app.py:475](../../app.py#L475)

Определяет Pydantic-контракт снимка текущего номера копии. Поля: id, number.

Базовые классы: `CopyKindRequest`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `id` | `str` | `Field(min_length=1, max_length=128)` |
| `number` | `int` | `Field(gt=0)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-copynumberreleaserequest"></a>

## `CopyNumberReleaseRequest`

[app.py:482](../../app.py#L482)

Определяет Pydantic-контракт освобождения номера копии. Поля: number.

Базовые классы: `CopyKindRequest`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `number` | `int` | `Field(gt=0, strict=True)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-copyrenumberrequest"></a>

## `CopyRenumberRequest`

[app.py:488](../../app.py#L488)

Определяет Pydantic-контракт перенумерации копий. Поля: copies.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `copies` | `list[CopyNumberSnapshot]` | `обязательное поле` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-copygroupsettingsrequest"></a>

## `CopyGroupSettingsRequest`

[app.py:495](../../app.py#L495)

Определяет Pydantic-контракт настроек основной папки. Поля: tracking, label.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `tracking` | `bool &#124; None` | `Field(default=None, strict=True)` |
| `label` | `Literal['', 'temporary', 'inbox', 'archive'] &#124; None` | `None` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-copygroupacknowledgerequest"></a>

## `CopyGroupAcknowledgeRequest`

[app.py:503](../../app.py#L503)

Определяет Pydantic-контракт подтверждения версии изменения. Поля: changed_at.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `changed_at` | `str` | `Field(min_length=1, max_length=64)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-copyconnectionrequest"></a>

## `CopyConnectionRequest`

[app.py:510](../../app.py#L510)

Определяет Pydantic-контракт подключения или отключения связи. Поля: connected.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `connected` | `bool` | `Field(strict=True)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-copysourcerequest"></a>

## `CopySourceRequest`

[app.py:517](../../app.py#L517)

Определяет Pydantic-контракт выбора источника копирования. Поля: source_id.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `source_id` | `str &#124; None` | `Field(default=None, min_length=1, max_length=128)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-set-folder-copy-source"></a>

## `set_folder_copy_source`

[app.py:524](../../app.py#L524)

Меняет источник копии под общей блокировкой запуска сверок. Явно отклоняет недопустимое состояние через ValueError.

```python
def set_folder_copy_source(location_id, source_id)
```

Прямые выражения вызова: `ValueError`, `copies.set_copy_source`, `paired_comparison.busy`.

Явные `raise`:

- `ValueError('Сначала приостанови сверку или дождись завершения копирования')`

Выражения возврата (ветви, без исполнения):

- `copies.set_copy_source(location_id, source_id)`


<a id="symbol-storage-copy-source"></a>

## `storage_copy_source`

[app.py:534](../../app.py#L534)

Обрабатывает изменение источника копирования обычной папки. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_source(location_id: str, request: CopySourceRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-locations/{location_id}/source')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(set_folder_copy_source, location_id, request.source_id)`


<a id="symbol-set-copy-connection"></a>

## `set_copy_connection`

[app.py:540](../../app.py#L540)

Меняет подключение связи с защитой от конфликтующего копирования. Явно отклоняет недопустимое состояние через ValueError.

```python
def set_copy_connection(action, identifier, connected)
```

Прямые выражения вызова: `ValueError`, `action`, `missing_copies.busy`.

Явные `raise`:

- `ValueError('Сначала дождись завершения копирования.')`

Выражения возврата (ветви, без исполнения):

- `action(identifier, connected)`


<a id="symbol-copy-catalog-action"></a>

## `copy_catalog_action`

[app.py:549](../../app.py#L549)

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


<a id="symbol-storage-copy-groups"></a>

## `storage_copy_groups`

[app.py:563](../../app.py#L563)

Возвращает наборы папок с типами, метками и состоянием наблюдателей. Поля результата: groups, kinds, labels.

```python
async def storage_copy_groups() -> dict
```

Декораторы: `app.get('/api/storage/copy-groups')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549), `dict`, `folder_tracking.status`.

Выражения возврата (ветви, без исполнения):

- `{'groups': [dict(group, **folder_tracking.status(group['id'])) for group in groups], 'kinds': COPY_KINDS, 'labels': FOLDER_LABELS}`


<a id="symbol-storage-folder-markers"></a>

## `storage_folder_markers`

[app.py:572](../../app.py#L572)

Возвращает состояние очереди служебных описаний папок. Асинхронно ожидает: asyncio.to_thread.

```python
async def storage_folder_markers() -> dict
```

Декораторы: `app.get('/api/storage/folder-markers')`.

Прямые выражения вызова: `asyncio.to_thread`.

Выражения возврата (ветви, без исполнения):

- `await asyncio.to_thread(folder_markers.status)`


<a id="symbol-storage-main-folder"></a>

## `storage_main_folder`

[app.py:579](../../app.py#L579)

Регистрирует выбранную папку как основную область набора. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_main_folder(request: ComparisonScope) -> dict
```

Декораторы: `app.post('/api/storage/copy-groups')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.create_main, request.volume_id, request.path)`


<a id="symbol-storage-copy-group-settings"></a>

## `storage_copy_group_settings`

[app.py:586](../../app.py#L586)

Обновляет настройки набора и пробуждает отслеживание изменений. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_group_settings(group_id: str, request: CopyGroupSettingsRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-groups/{group_id}')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549), `folder_tracking.wake`, `request.model_dump`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-storage-acknowledge-folder-changes"></a>

## `storage_acknowledge_folder_changes`

[app.py:595](../../app.py#L595)

Подтверждает конкретную версию уведомления об изменении папки. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_acknowledge_folder_changes(group_id: str, request: CopyGroupAcknowledgeRequest) -> dict
```

Декораторы: `app.post('/api/storage/copy-groups/{group_id}/acknowledge')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.acknowledge_changes, group_id, request.changed_at)`


<a id="symbol-storage-copy-group-connection"></a>

## `storage_copy_group_connection`

[app.py:602](../../app.py#L602)

Меняет подключение всего набора папок. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_group_connection(group_id: str, request: CopyConnectionRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-groups/{group_id}/connection')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549), `folder_tracking.wake`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-storage-copy-location-connection"></a>

## `storage_copy_location_connection`

[app.py:611](../../app.py#L611)

Меняет подключение одной обычной копии. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_location_connection(location_id: str, request: CopyConnectionRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-locations/{location_id}/connection')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(set_copy_connection, copies.set_copy_connected, location_id, request.connected)`


<a id="symbol-storage-copy-location"></a>

## `storage_copy_location`

[app.py:618](../../app.py#L618)

Добавляет папку копии к существующему набору. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_location(group_id: str, request: CopyLocationRequest) -> dict
```

Декораторы: `app.post('/api/storage/copy-groups/{group_id}/copies')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.add_copy, group_id, request.volume_id, request.path, request.kind)`


<a id="symbol-release-copy-number"></a>

## `release_copy_number`

[app.py:624](../../app.py#L624)

Освобождает подтверждённый номер под блокировкой запуска сверок. Явно отклоняет недопустимое состояние через ValueError.

```python
def release_copy_number(location_id, number, kind)
```

Прямые выражения вызова: `ValueError`, `copies.release_copy_number`, `paired_comparison.busy`.

Явные `raise`:

- `ValueError('Сначала дождись завершения сверки и копирования.')`

Выражения возврата (ветви, без исполнения):

- `copies.release_copy_number(location_id, number, kind)`


<a id="symbol-storage-release-copy-number"></a>

## `storage_release_copy_number`

[app.py:634](../../app.py#L634)

Архивирует прежнюю привязку и освобождает её номер. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_release_copy_number(location_id: str, request: CopyNumberReleaseRequest) -> dict
```

Декораторы: `app.post('/api/storage/copy-locations/{location_id}/release-number')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(release_copy_number, location_id, request.number, request.kind)`


<a id="symbol-storage-copy-kind"></a>

## `storage_copy_kind`

[app.py:641](../../app.py#L641)

Меняет тип зарегистрированной копии. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_copy_kind(location_id: str, request: CopyKindRequest) -> dict
```

Декораторы: `app.patch('/api/storage/copy-locations/{location_id}')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.change_kind, location_id, request.kind)`


<a id="symbol-storage-renumber-copies"></a>

## `storage_renumber_copies`

[app.py:648](../../app.py#L648)

Применяет подтверждённую нумерацию по снимку текущих связей. Асинхронно ожидает: copy_catalog_action.

```python
async def storage_renumber_copies(group_id: str, request: CopyRenumberRequest) -> dict
```

Декораторы: `app.post('/api/storage/copy-groups/{group_id}/renumber')`.

Прямые выражения вызова: `copy.model_dump`, [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `await copy_catalog_action(copies.renumber_copies, group_id, [copy.model_dump() for copy in request.copies])`


<a id="symbol-storage-remove-copy"></a>

## `storage_remove_copy`

[app.py:655](../../app.py#L655)

Удаляет связь копии из каталога без удаления пользовательских файлов. Поля результата: removed.

```python
async def storage_remove_copy(location_id: str) -> dict
```

Декораторы: `app.delete('/api/storage/copy-locations/{location_id}')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `{'removed': True}`


<a id="symbol-storage-remove-copy-group"></a>

## `storage_remove_copy_group`

[app.py:663](../../app.py#L663)

Удаляет набор папок из каталога без удаления пользовательских файлов. Поля результата: removed.

```python
async def storage_remove_copy_group(group_id: str) -> dict
```

Декораторы: `app.delete('/api/storage/copy-groups/{group_id}')`.

Прямые выражения вызова: [copy_catalog_action](../../app.py#L549).

Выражения возврата (ветви, без исполнения):

- `{'removed': True}`


<a id="symbol-comparisonrequest"></a>

## `ComparisonRequest`

[app.py:670](../../app.py#L670)

Определяет Pydantic-контракт общей сверки имён. Поля: source, targets, reread, reuse_index.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `source` | `ComparisonScope` | `обязательное поле` |
| `targets` | `list[ComparisonScope]` | `Field(min_length=1, max_length=16)` |
| `reread` | `bool` | `False` |
| `reuse_index` | `bool` | `True` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-comparison-call"></a>

## `comparison_call`

[app.py:680](../../app.py#L680)

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


<a id="symbol-start-comparison-exclusive"></a>

## `start_comparison_exclusive`

[app.py:691](../../app.py#L691)

Проверяет отсутствие конфликтующей работы под общей блокировкой запуска. Явно отклоняет недопустимое состояние через ValueError.

```python
def start_comparison_exclusive(action, *args, **kwargs)
```

Прямые выражения вызова: `ValueError`, `action`, `paired_comparison.busy`.

Явные `raise`:

- `ValueError('Сверка пары ещё выполняется. Сначала останови её.')`

Выражения возврата (ветви, без исполнения):

- `action(*args, **kwargs)`


<a id="symbol-pairedcomparisonrequest"></a>

## `PairedComparisonRequest`

[app.py:700](../../app.py#L700)

Определяет Pydantic-контракт сверки связанной пары. Поля: copy_id, mode, base_job_id, method.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `copy_id` | `str` | `Field(min_length=1, max_length=128)` |
| `mode` | `Literal['folders', 'files']` | `'folders'` |
| `base_job_id` | `str &#124; None` | `None` |
| `method` | `Literal['size', 'sha256']` | `'size'` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-paireddecisionrequest"></a>

## `PairedDecisionRequest`

[app.py:710](../../app.py#L710)

Определяет Pydantic-контракт планового решения для лишнего элемента. Поля: path, action.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `Field(max_length=4096)` |
| `action` | `Literal['keep', 'add_main', 'move', 'remove'] &#124; None` | `обязательное поле` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-paired-jobs"></a>

## `paired_jobs`

[app.py:719](../../app.py#L719)

Возвращает историю парных сверок и допустимые решения для лишних элементов. Поля результата: jobs, decisions.

```python
async def paired_jobs(copy_id: str | None=None) -> dict
```

Декораторы: `app.get('/api/storage/paired-comparisons')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `{'jobs': await comparison_call(paired_comparison.jobs, copy_id), 'decisions': DECISIONS}`


<a id="symbol-start-paired-comparison"></a>

## `start_paired_comparison`

[app.py:726](../../app.py#L726)

Создаёт и запускает сверку зарегистрированной пары папок. Асинхронно ожидает: comparison_call.

```python
async def start_paired_comparison(request: PairedComparisonRequest) -> dict
```

Декораторы: `app.post('/api/storage/paired-comparisons', status_code=201)`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, paired_comparison.create, request.copy_id, request.mode, request.base_job_id, method=request.method)`


<a id="symbol-paired-job"></a>

## `paired_job`

[app.py:734](../../app.py#L734)

Возвращает состояние одной парной сверки. Асинхронно ожидает: comparison_call.

```python
async def paired_job(job_id: str) -> dict
```

Декораторы: `app.get('/api/storage/paired-comparisons/{job_id}')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(paired_comparison.job, job_id)`


<a id="symbol-paired-rows"></a>

## `paired_rows`

[app.py:741](../../app.py#L741)

Возвращает страницу выровненных строк парной сверки. Асинхронно ожидает: comparison_call.

```python
async def paired_rows(job_id: str, offset: int=Query(0, ge=0), limit: int=Query(1000, ge=1, le=5000), differences_only: bool=False) -> dict
```

Декораторы: `app.get('/api/storage/paired-comparisons/{job_id}/rows')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(paired_comparison.rows, job_id, offset, limit, differences_only)`


<a id="symbol-pause-paired-job"></a>

## `pause_paired_job`

[app.py:749](../../app.py#L749)

Запрашивает паузу парной сверки. Асинхронно ожидает: comparison_call.

```python
async def pause_paired_job(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/paired-comparisons/{job_id}/pause')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(paired_comparison.pause, job_id)`


<a id="symbol-resume-paired-job"></a>

## `resume_paired_job`

[app.py:756](../../app.py#L756)

Продолжает парную сверку после проверки конфликтующих операций. Асинхронно ожидает: comparison_call.

```python
async def resume_paired_job(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/paired-comparisons/{job_id}/resume')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, paired_comparison.resume, job_id)`


<a id="symbol-paired-decision"></a>

## `paired_decision`

[app.py:763](../../app.py#L763)

Сохраняет плановое решение для элемента только в копии. Асинхронно ожидает: comparison_call.

```python
async def paired_decision(job_id: str, request: PairedDecisionRequest) -> dict
```

Декораторы: `app.patch('/api/storage/paired-comparisons/{job_id}/decision')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(paired_comparison.decide, job_id, request.path, request.action)`


<a id="symbol-comparison-jobs"></a>

## `comparison_jobs`

[app.py:770](../../app.py#L770)

Возвращает историю общей сверки имён и старых отчётов. Поля результата: jobs.

```python
async def comparison_jobs() -> dict
```

Декораторы: `app.get('/api/storage/comparisons')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `{'jobs': await comparison_call(comparison.jobs)}`


<a id="symbol-missing-copy-plan"></a>

## `missing_copy_plan`

[app.py:777](../../app.py#L777)

Создаёт сохранённый план копирования по завершённому файловому отчёту. Асинхронно ожидает: comparison_call.

```python
async def missing_copy_plan(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/paired-comparisons/{job_id}/copy-plan', status_code=201)`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(missing_copies.plan, job_id)`


<a id="symbol-missing-copy-job"></a>

## `missing_copy_job`

[app.py:784](../../app.py#L784)

Возвращает состояние операции копирования отсутствующих элементов. Асинхронно ожидает: comparison_call.

```python
async def missing_copy_job(operation_id: str) -> dict
```

Декораторы: `app.get('/api/storage/copy-operations/{operation_id}')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(missing_copies.job, operation_id)`


<a id="symbol-missing-copy-items"></a>

## `missing_copy_items`

[app.py:791](../../app.py#L791)

Возвращает страницу элементов сохранённого плана копирования. Асинхронно ожидает: comparison_call.

```python
async def missing_copy_items(operation_id: str, offset: int=Query(0, ge=0), limit: int=Query(200, ge=1, le=1000)) -> dict
```

Декораторы: `app.get('/api/storage/copy-operations/{operation_id}/items')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(missing_copies.items, operation_id, offset, limit)`


<a id="symbol-start-missing-copy"></a>

## `start_missing_copy`

[app.py:799](../../app.py#L799)

Запускает подтверждённую операцию создания отсутствующих копий. Асинхронно ожидает: comparison_call.

```python
async def start_missing_copy(operation_id: str) -> dict
```

Декораторы: `app.post('/api/storage/copy-operations/{operation_id}/start')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, missing_copies.start, operation_id)`


<a id="symbol-stop-missing-copy"></a>

## `stop_missing_copy`

[app.py:806](../../app.py#L806)

Запрашивает остановку операции копирования. Асинхронно ожидает: comparison_call.

```python
async def stop_missing_copy(operation_id: str) -> dict
```

Декораторы: `app.post('/api/storage/copy-operations/{operation_id}/stop')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(missing_copies.stop, operation_id)`


<a id="symbol-start-comparison"></a>

## `start_comparison`

[app.py:813](../../app.py#L813)

Создаёт общую сверку имён исходной области и выбранных целей. Асинхронно ожидает: comparison_call.

```python
async def start_comparison(request: ComparisonRequest) -> dict
```

Декораторы: `app.post('/api/storage/comparisons', status_code=201)`.

Прямые выражения вызова: [comparison_call](../../app.py#L680), `request.source.model_dump`, `t.model_dump`.

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, comparison.create, request.source.model_dump(), [t.model_dump() for t in request.targets], reuse_index=request.reuse_index)`


<a id="symbol-comparison-job"></a>

## `comparison_job`

[app.py:821](../../app.py#L821)

Возвращает состояние и области общей сверки. Асинхронно ожидает: comparison_call.

```python
async def comparison_job(job_id: str) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.job, job_id)`


<a id="symbol-pause-comparison"></a>

## `pause_comparison`

[app.py:828](../../app.py#L828)

Запрашивает паузу общей сверки имён. Асинхронно ожидает: comparison_call.

```python
async def pause_comparison(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/comparisons/{job_id}/pause')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.pause, job_id)`


<a id="symbol-resume-comparison"></a>

## `resume_comparison`

[app.py:835](../../app.py#L835)

Продолжает сверку имён либо создаёт новую вместо старой проверки содержимого. Асинхронно ожидает: comparison_call.

```python
async def resume_comparison(job_id: str) -> dict
```

Декораторы: `app.post('/api/storage/comparisons/{job_id}/resume')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(start_comparison_exclusive, comparison.resume, job_id)`


<a id="symbol-comparison-tree"></a>

## `comparison_tree`

[app.py:842](../../app.py#L842)

Возвращает страницу исходного дерева общей сверки с фильтром статуса. Асинхронно ожидает: comparison_call.

```python
async def comparison_tree(job_id: str, path: str | None=None, status: str='', offset: int=Query(0, ge=0), limit: int=Query(200, ge=1, le=500)) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}/tree')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.tree, job_id, path, status, offset, limit)`


<a id="symbol-comparison-target-tree"></a>

## `comparison_target_tree`

[app.py:850](../../app.py#L850)

Возвращает страницу сохранённого дерева выбранной цели общей сверки. Асинхронно ожидает: comparison_call.

```python
async def comparison_target_tree(job_id: str, scan_id: int=Query(..., ge=1), path: str | None=None, offset: int=Query(0, ge=0), limit: int=Query(200, ge=1, le=500)) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}/target-tree')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.target_tree, job_id, scan_id, path, offset, limit)`


<a id="symbol-comparison-detail"></a>

## `comparison_detail`

[app.py:858](../../app.py#L858)

Возвращает найденные совпадения и подробности элемента отчёта. Асинхронно ожидает: comparison_call.

```python
async def comparison_detail(job_id: str, path: str | None=None) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}/detail')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `await comparison_call(comparison.detail, job_id, path)`


<a id="symbol-comparison-events"></a>

## `comparison_events`

[app.py:865](../../app.py#L865)

Возвращает события общей сверки с обратной пагинацией. Поля результата: events.

```python
async def comparison_events(job_id: str, before: int | None=Query(None, ge=1)) -> dict
```

Декораторы: `app.get('/api/storage/comparisons/{job_id}/events')`.

Прямые выражения вызова: [comparison_call](../../app.py#L680).

Выражения возврата (ветви, без исполнения):

- `{'events': await comparison_call(comparison.events, job_id, before)}`


<a id="symbol-list-sources"></a>

## `list_sources`

[app.py:872](../../app.py#L872)

Возвращает сохранённые источники медиаиндекса. Поля результата: sources, revision.

```python
async def list_sources() -> dict[str, object]
```

Декораторы: `app.get('/api/sources')`.

Прямые выражения вызова: `catalog.list_sources`, `catalog.revision`.

Выражения возврата (ветви, без исполнения):

- `{'sources': catalog.list_sources(), 'revision': catalog.revision()}`


<a id="symbol-create-source"></a>

## `create_source`

[app.py:879](../../app.py#L879)

Регистрирует обычный источник, устанавливает наблюдение и запускает сканирование. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def create_source(request: SourceRequest) -> dict[str, object]
```

Декораторы: `app.post('/api/sources')`.

Прямые выражения вызова: `HTTPException`, `catalog.add_source`, `catalog.list_sources`, `int`, [schedule_scan](../../app.py#L120), `str`, `watcher.watch`.

Явные `raise`:

- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `(FileNotFoundError, NotADirectoryError, PermissionError)`.

Выражения возврата (ветви, без исполнения):

- `{'sources': catalog.list_sources()}`


<a id="symbol-choose-sources"></a>

## `choose_sources`

[app.py:897](../../app.py#L897)

Регистрирует выбранные системным диалогом папки и запускает их сканирование. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def choose_sources(request: FolderChoiceRequest) -> dict[str, object]
```

Декораторы: `app.post('/api/sources/choose')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `catalog.add_source`, `catalog.list_sources`, `int`, [schedule_scan](../../app.py#L120), `str`, `watcher.watch`.

Явные `raise`:

- `HTTPException(status_code=400, detail=str(error))`

Перехватываемые типы: `(RuntimeError, FileNotFoundError, NotADirectoryError, PermissionError)`.

Выражения возврата (ветви, без исполнения):

- `{'cancelled': not selected, 'sources': catalog.list_sources()}`


<a id="symbol-update-source"></a>

## `update_source`

[app.py:922](../../app.py#L922)

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


<a id="symbol-delete-source"></a>

## `delete_source`

[app.py:940](../../app.py#L940)

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


<a id="symbol-scan-one-source"></a>

## `scan_one_source`

[app.py:957](../../app.py#L957)

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


<a id="symbol-scan-all-sources"></a>

## `scan_all_sources`

[app.py:971](../../app.py#L971)

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


<a id="symbol-authorize-system-photos"></a>

## `authorize_system_photos`

[app.py:992](../../app.py#L992)

Запрашивает разрешение Photos и возвращает состояние доступа. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def authorize_system_photos() -> dict[str, object]
```

Декораторы: `app.post('/api/photos/authorize')`.

Прямые выражения вызова: `HTTPException`, `asyncio.to_thread`, `catalog.get_source`, [schedule_scan](../../app.py#L120), `source.get`, `status.get`, `str`, `thumbnail_workers.wake`.

Явные `raise`:

- `HTTPException(status_code=403, detail='Разреши доступ в настройках macOS: Конфиденциальность → Фото')`
- `HTTPException(status_code=500, detail=str(error))`

Перехватываемые типы: `PhotosAccessDenied`, `PhotosAdapterError`.

Выражения возврата (ветви, без исполнения):

- `{'status': status}`


<a id="symbol-library-call"></a>

## `library_call`

[app.py:1012](../../app.py#L1012)

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


<a id="symbol-librarynamerequest"></a>

## `LibraryNameRequest`

[app.py:1027](../../app.py#L1027)

Определяет Pydantic-контракт названия медиатеки. Поля: label.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `label` | `str` | `Field(min_length=1, max_length=120)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-librarycopyrequest"></a>

## `LibraryCopyRequest`

[app.py:1034](../../app.py#L1034)

Определяет Pydantic-контракт папки-копии медиатеки. Поля: volume_id, path.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `volume_id` | `str` | `Field(min_length=1, max_length=128)` |
| `path` | `str` | `Field(min_length=1, max_length=4096)` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-photossyncschedulerequest"></a>

## `PhotosSyncScheduleRequest`

[app.py:1042](../../app.py#L1042)

Определяет Pydantic-контракт временного окна Photos. Поля: night_only, start_hour, end_hour, timezone.

Базовые классы: `BaseModel`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `night_only` | `bool` | `Field(strict=True)` |
| `start_hour` | `int` | `Field(default=0, ge=0, le=23, strict=True)` |
| `end_hour` | `int` | `Field(default=7, ge=0, le=23, strict=True)` |
| `timezone` | `Literal['Europe/Moscow']` | `'Europe/Moscow'` |

Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-set-photos-sync-schedule"></a>

## `set_photos_sync_schedule`

[app.py:1053](../../app.py#L1053)

Сохраняет часы синхронизации выбранной медиатеки. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def set_photos_sync_schedule(source_id: int, request: PhotosSyncScheduleRequest) -> dict
```

Декораторы: `app.patch('/api/photos/libraries/{source_id}/sync-schedule')`.

Прямые выражения вызова: [library_call](../../app.py#L1012), [list_photo_libraries](../../app.py#L1062), `request.model_dump`, `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-list-photo-libraries"></a>

## `list_photo_libraries`

[app.py:1062](../../app.py#L1062)

Возвращает медиатеки, состояние подключения, превью и привязанные копии. Асинхронно ожидает: library_call.

```python
async def list_photo_libraries() -> dict
```

Декораторы: `app.get('/api/photos/libraries')`.

Прямые выражения вызова: [library_call](../../app.py#L1012).

Выражения возврата (ветви, без исполнения):

- `await library_call(photo_libraries.list)`


<a id="symbol-connect-photo-library"></a>

## `connect_photo_library`

[app.py:1069](../../app.py#L1069)

Повторяет сопоставление системной медиатеки и пробуждает превью. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def connect_photo_library() -> dict
```

Декораторы: `app.post('/api/photos/libraries/connect')`.

Прямые выражения вызова: [library_call](../../app.py#L1012), [list_photo_libraries](../../app.py#L1062), `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-browse-photo-library"></a>

## `browse_photo_library`

[app.py:1078](../../app.py#L1078)

Возвращает виртуальную папку Photos и повышает приоритет её превью. Асинхронно ожидает: library_call.

```python
async def browse_photo_library(source_id: int, path: str='', offset: int=Query(default=0, ge=0), limit: int=Query(default=150, ge=1, le=1000)) -> dict
```

Декораторы: `app.get('/api/photos/libraries/{source_id}/browse')`.

Прямые выражения вызова: [library_call](../../app.py#L1012), `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-photo-preview-status"></a>

## `photo_preview_status`

[app.py:1089](../../app.py#L1089)

Возвращает готовые превью выбранных объектов медиатеки. Явно отклоняет недопустимое состояние через HTTPException.

```python
async def photo_preview_status(source_id: int, ids: list[int]=Query(default=[])) -> dict
```

Декораторы: `app.get('/api/photos/libraries/{source_id}/preview-status')`.

Прямые выражения вызова: `HTTPException`, `len`, [library_call](../../app.py#L1012).

Явные `raise`:

- `HTTPException(status_code=400, detail='Слишком много объектов')`

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_browser.preview_status, source_id, ids)`


<a id="symbol-register-photo-library"></a>

## `register_photo_library`

[app.py:1098](../../app.py#L1098)

Регистрирует текущую медиатеку и ставит её первый скан в очередь. Асинхронно ожидает: library_call.

```python
async def register_photo_library(request: LibraryNameRequest) -> dict
```

Декораторы: `app.post('/api/photos/libraries', status_code=201)`.

Прямые выражения вызова: [library_call](../../app.py#L1012), [schedule_scan](../../app.py#L120).

Выражения возврата (ветви, без исполнения):

- `profile`


<a id="symbol-rename-photo-library"></a>

## `rename_photo_library`

[app.py:1107](../../app.py#L1107)

Меняет название медиатеки и возвращает обновлённый список. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def rename_photo_library(source_id: int, request: LibraryNameRequest) -> dict
```

Декораторы: `app.patch('/api/photos/libraries/{source_id}')`.

Прямые выражения вызова: [library_call](../../app.py#L1012), [list_photo_libraries](../../app.py#L1062).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-pause-photo-library"></a>

## `pause_photo_library`

[app.py:1115](../../app.py#L1115)

Включает ручную паузу выбранной медиатеки. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def pause_photo_library(source_id: int) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/pause')`.

Прямые выражения вызова: [library_call](../../app.py#L1012), [list_photo_libraries](../../app.py#L1062).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-resume-photo-library"></a>

## `resume_photo_library`

[app.py:1123](../../app.py#L1123)

Снимает ручную паузу медиатеки и пробуждает очередь превью. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def resume_photo_library(source_id: int) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/resume')`.

Прямые выражения вызова: [library_call](../../app.py#L1012), [list_photo_libraries](../../app.py#L1062), `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-bind-photo-library-copy"></a>

## `bind_photo_library_copy`

[app.py:1132](../../app.py#L1132)

Привязывает выбранную папку как копию медиатеки. Асинхронно ожидает: library_call.

```python
async def bind_photo_library_copy(source_id: int, request: LibraryCopyRequest) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/copies', status_code=201)`.

Прямые выражения вызова: [library_call](../../app.py#L1012).

Выражения возврата (ветви, без исполнения):

- `await library_call(photo_libraries.bind_copy, source_id, request.volume_id, request.path)`


<a id="symbol-unbind-photo-library-copy"></a>

## `unbind_photo_library_copy`

[app.py:1139](../../app.py#L1139)

Отключает привязку копии медиатеки и возвращает обновлённый список. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def unbind_photo_library_copy(source_id: int, link_id: str) -> dict
```

Декораторы: `app.delete('/api/photos/libraries/{source_id}/copies/{link_id}')`.

Прямые выражения вызова: [library_call](../../app.py#L1012), [list_photo_libraries](../../app.py#L1062).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-photo-copy-source"></a>

## `photo_copy_source`

[app.py:1147](../../app.py#L1147)

Меняет источник привязанной копии Photos. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def photo_copy_source(source_id: int, link_id: str, request: CopySourceRequest) -> dict
```

Декораторы: `app.patch('/api/photos/libraries/{source_id}/copies/{link_id}/source')`.

Прямые выражения вызова: [library_call](../../app.py#L1012), [list_photo_libraries](../../app.py#L1062).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-photo-copy-first"></a>

## `photo_copy_first`

[app.py:1155](../../app.py#L1155)

Ставит выбранную копию Photos первой по номеру без изменения маршрутов. Асинхронно ожидает: library_call, list_photo_libraries.

```python
async def photo_copy_first(source_id: int, link_id: str) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/copies/{link_id}/make-first')`.

Прямые выражения вызова: [library_call](../../app.py#L1012), [list_photo_libraries](../../app.py#L1062).

Выражения возврата (ветви, без исполнения):

- `await list_photo_libraries()`


<a id="symbol-start-photo-originals"></a>

## `start_photo_originals`

[app.py:1163](../../app.py#L1163)

Запускает или планирует сохранение оригиналов в цепочку копий Photos. Асинхронно ожидает: library_call.

```python
async def start_photo_originals(source_id: int, link_id: str) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/copies/{link_id}/originals/start')`.

Прямые выражения вызова: [library_call](../../app.py#L1012).

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_originals.start, link_id, source_id)`


<a id="symbol-pause-photo-originals"></a>

## `pause_photo_originals`

[app.py:1170](../../app.py#L1170)

Запрашивает паузу сохранения оригиналов выбранной медиатеки. Асинхронно ожидает: library_call.

```python
async def pause_photo_originals(source_id: int, link_id: str) -> dict
```

Декораторы: `app.post('/api/photos/libraries/{source_id}/copies/{link_id}/originals/pause')`.

Прямые выражения вызова: [library_call](../../app.py#L1012).

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_originals.pause, link_id, source_id)`


<a id="symbol-photo-originals-status"></a>

## `photo_originals_status`

[app.py:1177](../../app.py#L1177)

Возвращает состояние оригиналов после проверки принадлежности копии медиатеке. Асинхронно ожидает: library_call.

```python
async def photo_originals_status(source_id: int, link_id: str) -> dict
```

Декораторы: `app.get('/api/photos/libraries/{source_id}/copies/{link_id}/originals')`.

Прямые выражения вызова: [library_call](../../app.py#L1012).

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_originals.summary, link_id)`


<a id="symbol-photo-originals-journal"></a>

## `photo_originals_journal`

[app.py:1185](../../app.py#L1185)

Возвращает журнал оригиналов и пути незавершённых записей. Асинхронно ожидает: library_call.

```python
async def photo_originals_journal(source_id: int, link_id: str) -> dict
```

Декораторы: `app.get('/api/photos/libraries/{source_id}/copies/{link_id}/originals/journal')`.

Прямые выражения вызова: [library_call](../../app.py#L1012).

Выражения возврата (ветви, без исполнения):

- `await library_call(photos_originals.journal, link_id, source_id)`


<a id="symbol-catalog-summary"></a>

## `catalog_summary`

[app.py:1192](../../app.py#L1192)

Возвращает суммарные показатели сохранённого медиаиндекса. Использует catalog.summary.

```python
async def catalog_summary() -> dict[str, int]
```

Декораторы: `app.get('/api/catalog/summary')`.

Прямые выражения вызова: `catalog.summary`.

Выражения возврата (ветви, без исполнения):

- `catalog.summary()`


<a id="symbol-source-tree"></a>

## `source_tree`

[app.py:1199](../../app.py#L1199)

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


<a id="symbol-source-files"></a>

## `source_files`

[app.py:1208](../../app.py#L1208)

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


<a id="symbol-thumbnail-status"></a>

## `thumbnail_status`

[app.py:1227](../../app.py#L1227)

Возвращает очередь превью и диагностическое состояние её воркеров. Использует thumbnail_workers.status.

```python
async def thumbnail_status() -> dict[str, object]
```

Декораторы: `app.get('/api/thumbnails/status')`.

Прямые выражения вызова: `thumbnail_workers.status`.

Выражения возврата (ветви, без исполнения):

- `thumbnail_workers.status()`


<a id="symbol-pause-thumbnails"></a>

## `pause_thumbnails`

[app.py:1234](../../app.py#L1234)

Сохраняет общую ручную паузу фоновой очереди превью. Использует catalog.set_thumbnail_queue_paused, thumbnail_workers.status.

```python
async def pause_thumbnails() -> dict[str, object]
```

Декораторы: `app.post('/api/thumbnails/pause')`.

Прямые выражения вызова: `catalog.set_thumbnail_queue_paused`, `thumbnail_workers.status`.

Выражения возврата (ветви, без исполнения):

- `thumbnail_workers.status()`


<a id="symbol-resume-thumbnails"></a>

## `resume_thumbnails`

[app.py:1242](../../app.py#L1242)

Снимает общую паузу превью и пробуждает воркеры. Использует catalog.set_thumbnail_queue_paused, thumbnail_workers.status, thumbnail_workers.wake.

```python
async def resume_thumbnails() -> dict[str, object]
```

Декораторы: `app.post('/api/thumbnails/resume')`.

Прямые выражения вызова: `catalog.set_thumbnail_queue_paused`, `thumbnail_workers.status`, `thumbnail_workers.wake`.

Выражения возврата (ветви, без исполнения):

- `thumbnail_workers.status()`


<a id="symbol-open-source-folder-in-finder"></a>

## `open_source_folder_in_finder`

[app.py:1251](../../app.py#L1251)

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


<a id="symbol-media-thumbnail"></a>

## `media_thumbnail`

[app.py:1280](../../app.py#L1280)

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


<a id="symbol-open-media-in-default-app"></a>

## `open_media_in_default_app`

[app.py:1299](../../app.py#L1299)

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
