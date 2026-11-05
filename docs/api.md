# HTTP API Core

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

OpenAPI получен из текущих контрактов FastAPI на временных данных. Core по умолчанию доступен на http://127.0.0.1:18765, UI на 8090, интерактивная схема на /docs.

Обработчики могут переводить доменные ошибки в HTTPException дополнительно к ответам OpenAPI. Точные raise и перехваты приведены в [справочнике app.py](reference/app.md). GET может пополнять кэш, снимки или приоритеты превью. План и старт копирования — отдельные действия.

`422` означает отказ валидации Pydantic/Query. Обработчики используют `400` для недопустимых параметров или состояния и `404` для отсутствующей записи либо ресурса. Photos дополнительно использует `403`, `409` и `503` по контракту конкретного маршрута.

## Все маршруты

| Метод | Путь | Назначение и обработчик |
| --- | --- | --- |
| `GET` | `/api/catalog/summary` | [catalog_summary](reference/app.md#symbol-catalog_summary) — Возвращает суммарные показатели сохранённого медиаиндекса. |
| `POST` | `/api/media/{media_id}/open` | [open_media_in_default_app](reference/app.md#symbol-open_media_in_default_app) — Открывает обычный файл системной командой или выделяет объект Photos. |
| `GET` | `/api/media/{media_id}/thumbnail` | [media_thumbnail](reference/app.md#symbol-media_thumbnail) — Отдаёт только готовый JPEG из кэша медиаиндекса. |
| `POST` | `/api/photos/authorize` | [authorize_system_photos](reference/app.md#symbol-authorize_system_photos) — Запрашивает разрешение Photos и возвращает состояние доступа. |
| `GET` | `/api/photos/libraries` | [list_photo_libraries](reference/app.md#symbol-list_photo_libraries) — Возвращает медиатеки, состояние подключения, превью и привязанные копии. |
| `POST` | `/api/photos/libraries` | [register_photo_library](reference/app.md#symbol-register_photo_library) — Регистрирует текущую медиатеку и ставит её первый скан в очередь. |
| `POST` | `/api/photos/libraries/connect` | [connect_photo_library](reference/app.md#symbol-connect_photo_library) — Повторяет сопоставление системной медиатеки и пробуждает превью. |
| `PATCH` | `/api/photos/libraries/{source_id}` | [rename_photo_library](reference/app.md#symbol-rename_photo_library) — Меняет название медиатеки и возвращает обновлённый список. |
| `GET` | `/api/photos/libraries/{source_id}/browse` | [browse_photo_library](reference/app.md#symbol-browse_photo_library) — Возвращает виртуальную папку Photos и повышает приоритет её превью. |
| `POST` | `/api/photos/libraries/{source_id}/copies` | [bind_photo_library_copy](reference/app.md#symbol-bind_photo_library_copy) — Привязывает выбранную папку как копию медиатеки. |
| `DELETE` | `/api/photos/libraries/{source_id}/copies/{link_id}` | [unbind_photo_library_copy](reference/app.md#symbol-unbind_photo_library_copy) — Отключает привязку копии медиатеки и возвращает обновлённый список. |
| `POST` | `/api/photos/libraries/{source_id}/copies/{link_id}/make-first` | [photo_copy_first](reference/app.md#symbol-photo_copy_first) — Ставит выбранную копию Photos первой по номеру без изменения маршрутов. |
| `GET` | `/api/photos/libraries/{source_id}/copies/{link_id}/originals` | [photo_originals_status](reference/app.md#symbol-photo_originals_status) — Возвращает состояние оригиналов после проверки принадлежности копии медиатеке. |
| `GET` | `/api/photos/libraries/{source_id}/copies/{link_id}/originals/journal` | [photo_originals_journal](reference/app.md#symbol-photo_originals_journal) — Возвращает журнал оригиналов и пути незавершённых записей. |
| `POST` | `/api/photos/libraries/{source_id}/copies/{link_id}/originals/pause` | [pause_photo_originals](reference/app.md#symbol-pause_photo_originals) — Запрашивает паузу сохранения оригиналов выбранной медиатеки. |
| `POST` | `/api/photos/libraries/{source_id}/copies/{link_id}/originals/start` | [start_photo_originals](reference/app.md#symbol-start_photo_originals) — Запускает или планирует сохранение оригиналов в цепочку копий Photos. |
| `PATCH` | `/api/photos/libraries/{source_id}/copies/{link_id}/source` | [photo_copy_source](reference/app.md#symbol-photo_copy_source) — Меняет источник привязанной копии Photos. |
| `POST` | `/api/photos/libraries/{source_id}/pause` | [pause_photo_library](reference/app.md#symbol-pause_photo_library) — Включает ручную паузу выбранной медиатеки. |
| `GET` | `/api/photos/libraries/{source_id}/preview-status` | [photo_preview_status](reference/app.md#symbol-photo_preview_status) — Возвращает готовые превью выбранных объектов медиатеки. |
| `POST` | `/api/photos/libraries/{source_id}/resume` | [resume_photo_library](reference/app.md#symbol-resume_photo_library) — Снимает ручную паузу медиатеки и пробуждает очередь превью. |
| `PATCH` | `/api/photos/libraries/{source_id}/sync-schedule` | [set_photos_sync_schedule](reference/app.md#symbol-set_photos_sync_schedule) — Сохраняет часы синхронизации выбранной медиатеки. |
| `POST` | `/api/scan` | [scan_all_sources](reference/app.md#symbol-scan_all_sources) — Запускает сканирование зарегистрированных источников. |
| `GET` | `/api/sources` | [list_sources](reference/app.md#symbol-list_sources) — Возвращает сохранённые источники медиаиндекса. |
| `POST` | `/api/sources` | [create_source](reference/app.md#symbol-create_source) — Регистрирует обычный источник, устанавливает наблюдение и запускает сканирование. |
| `POST` | `/api/sources/choose` | [choose_sources](reference/app.md#symbol-choose_sources) — Регистрирует выбранные системным диалогом папки и запускает их сканирование. |
| `DELETE` | `/api/sources/{source_id}` | [delete_source](reference/app.md#symbol-delete_source) — Снимает наблюдение и удаляет источник из медиаиндекса. |
| `PATCH` | `/api/sources/{source_id}` | [update_source](reference/app.md#symbol-update_source) — Обновляет роль, название и комментарий обычного источника. |
| `GET` | `/api/sources/{source_id}/files` | [source_files](reference/app.md#symbol-source_files) — Возвращает файлы папки источника и повышает приоритет их превью. |
| `POST` | `/api/sources/{source_id}/open-in-finder` | [open_source_folder_in_finder](reference/app.md#symbol-open_source_folder_in_finder) — Открывает проверенную папку обычного источника в Finder. |
| `POST` | `/api/sources/{source_id}/scan` | [scan_one_source](reference/app.md#symbol-scan_one_source) — Проверяет источник и выполняет его ручное сканирование. |
| `GET` | `/api/sources/{source_id}/tree` | [source_tree](reference/app.md#symbol-source_tree) — Возвращает дерево виртуальных папок зарегистрированного источника. |
| `GET` | `/api/storage/comparisons` | [comparison_jobs](reference/app.md#symbol-comparison_jobs) — Возвращает историю общей сверки имён и старых отчётов. |
| `POST` | `/api/storage/comparisons` | [start_comparison](reference/app.md#symbol-start_comparison) — Создаёт общую сверку имён исходной области и выбранных целей. |
| `GET` | `/api/storage/comparisons/{job_id}` | [comparison_job](reference/app.md#symbol-comparison_job) — Возвращает состояние и области общей сверки. |
| `GET` | `/api/storage/comparisons/{job_id}/detail` | [comparison_detail](reference/app.md#symbol-comparison_detail) — Возвращает найденные совпадения и подробности элемента отчёта. |
| `GET` | `/api/storage/comparisons/{job_id}/events` | [comparison_events](reference/app.md#symbol-comparison_events) — Возвращает события общей сверки с обратной пагинацией. |
| `POST` | `/api/storage/comparisons/{job_id}/pause` | [pause_comparison](reference/app.md#symbol-pause_comparison) — Запрашивает паузу общей сверки имён. |
| `POST` | `/api/storage/comparisons/{job_id}/resume` | [resume_comparison](reference/app.md#symbol-resume_comparison) — Продолжает сверку имён либо создаёт новую вместо старой проверки содержимого. |
| `GET` | `/api/storage/comparisons/{job_id}/target-tree` | [comparison_target_tree](reference/app.md#symbol-comparison_target_tree) — Возвращает страницу сохранённого дерева выбранной цели общей сверки. |
| `GET` | `/api/storage/comparisons/{job_id}/tree` | [comparison_tree](reference/app.md#symbol-comparison_tree) — Возвращает страницу исходного дерева общей сверки с фильтром статуса. |
| `GET` | `/api/storage/copy-groups` | [storage_copy_groups](reference/app.md#symbol-storage_copy_groups) — Возвращает наборы папок с типами, метками и состоянием наблюдателей. |
| `POST` | `/api/storage/copy-groups` | [storage_main_folder](reference/app.md#symbol-storage_main_folder) — Регистрирует выбранную папку как основную область набора. |
| `DELETE` | `/api/storage/copy-groups/{group_id}` | [storage_remove_copy_group](reference/app.md#symbol-storage_remove_copy_group) — Удаляет набор папок из каталога без удаления пользовательских файлов. |
| `PATCH` | `/api/storage/copy-groups/{group_id}` | [storage_copy_group_settings](reference/app.md#symbol-storage_copy_group_settings) — Обновляет настройки набора и пробуждает отслеживание изменений. |
| `POST` | `/api/storage/copy-groups/{group_id}/acknowledge` | [storage_acknowledge_folder_changes](reference/app.md#symbol-storage_acknowledge_folder_changes) — Подтверждает конкретную версию уведомления об изменении папки. |
| `PATCH` | `/api/storage/copy-groups/{group_id}/connection` | [storage_copy_group_connection](reference/app.md#symbol-storage_copy_group_connection) — Меняет подключение всего набора папок. |
| `POST` | `/api/storage/copy-groups/{group_id}/copies` | [storage_copy_location](reference/app.md#symbol-storage_copy_location) — Добавляет папку копии к существующему набору. |
| `POST` | `/api/storage/copy-groups/{group_id}/renumber` | [storage_renumber_copies](reference/app.md#symbol-storage_renumber_copies) — Применяет подтверждённую нумерацию по снимку текущих связей. |
| `DELETE` | `/api/storage/copy-locations/{location_id}` | [storage_remove_copy](reference/app.md#symbol-storage_remove_copy) — Удаляет связь копии из каталога без удаления пользовательских файлов. |
| `PATCH` | `/api/storage/copy-locations/{location_id}` | [storage_copy_kind](reference/app.md#symbol-storage_copy_kind) — Меняет тип зарегистрированной копии. |
| `PATCH` | `/api/storage/copy-locations/{location_id}/connection` | [storage_copy_location_connection](reference/app.md#symbol-storage_copy_location_connection) — Меняет подключение одной обычной копии. |
| `POST` | `/api/storage/copy-locations/{location_id}/release-number` | [storage_release_copy_number](reference/app.md#symbol-storage_release_copy_number) — Архивирует прежнюю привязку и освобождает её номер. |
| `PATCH` | `/api/storage/copy-locations/{location_id}/source` | [storage_copy_source](reference/app.md#symbol-storage_copy_source) — Обрабатывает изменение источника копирования обычной папки. |
| `GET` | `/api/storage/copy-operations/{operation_id}` | [missing_copy_job](reference/app.md#symbol-missing_copy_job) — Возвращает состояние операции копирования отсутствующих элементов. |
| `GET` | `/api/storage/copy-operations/{operation_id}/items` | [missing_copy_items](reference/app.md#symbol-missing_copy_items) — Возвращает страницу элементов сохранённого плана копирования. |
| `POST` | `/api/storage/copy-operations/{operation_id}/start` | [start_missing_copy](reference/app.md#symbol-start_missing_copy) — Запускает подтверждённую операцию создания отсутствующих копий. |
| `POST` | `/api/storage/copy-operations/{operation_id}/stop` | [stop_missing_copy](reference/app.md#symbol-stop_missing_copy) — Запрашивает остановку операции копирования. |
| `GET` | `/api/storage/folder-markers` | [storage_folder_markers](reference/app.md#symbol-storage_folder_markers) — Возвращает состояние очереди служебных описаний папок. |
| `GET` | `/api/storage/nas` | [remembered_nas](reference/app.md#symbol-remembered_nas) — Возвращает список сохранённых серверов NAS. |
| `POST` | `/api/storage/nas/discover` | [discover_nas](reference/app.md#symbol-discover_nas) — Запускает обнаружение NAS через Bonjour на машине Core. |
| `POST` | `/api/storage/nas/{server_id}/remember` | [remember_nas_share](reference/app.md#symbol-remember_nas_share) — Сохраняет выбранный SMB-ресурс без подключения. |
| `GET` | `/api/storage/nas/{server_id}/shares` | [nas_shares](reference/app.md#symbol-nas_shares) — Возвращает сохранённые либо обновлённые ресурсы выбранного NAS. |
| `GET` | `/api/storage/paired-comparisons` | [paired_jobs](reference/app.md#symbol-paired_jobs) — Возвращает историю парных сверок и допустимые решения для лишних элементов. |
| `POST` | `/api/storage/paired-comparisons` | [start_paired_comparison](reference/app.md#symbol-start_paired_comparison) — Создаёт и запускает сверку зарегистрированной пары папок. |
| `GET` | `/api/storage/paired-comparisons/{job_id}` | [paired_job](reference/app.md#symbol-paired_job) — Возвращает состояние одной парной сверки. |
| `POST` | `/api/storage/paired-comparisons/{job_id}/copy-plan` | [missing_copy_plan](reference/app.md#symbol-missing_copy_plan) — Создаёт сохранённый план копирования по завершённому файловому отчёту. |
| `PATCH` | `/api/storage/paired-comparisons/{job_id}/decision` | [paired_decision](reference/app.md#symbol-paired_decision) — Сохраняет плановое решение для элемента только в копии. |
| `POST` | `/api/storage/paired-comparisons/{job_id}/pause` | [pause_paired_job](reference/app.md#symbol-pause_paired_job) — Запрашивает паузу парной сверки. |
| `POST` | `/api/storage/paired-comparisons/{job_id}/resume` | [resume_paired_job](reference/app.md#symbol-resume_paired_job) — Продолжает парную сверку после проверки конфликтующих операций. |
| `GET` | `/api/storage/paired-comparisons/{job_id}/rows` | [paired_rows](reference/app.md#symbol-paired_rows) — Возвращает страницу выровненных строк парной сверки. |
| `GET` | `/api/storage/volumes` | [storage_volumes](reference/app.md#symbol-storage_volumes) — Возвращает обнаруженные и сохранённые тома через API Core. |
| `POST` | `/api/storage/volumes/{volume_id}/connect` | [connect_network_volume](reference/app.md#symbol-connect_network_volume) — Открывает подключение сетевого тома в Finder на машине Core. |
| `GET` | `/api/storage/volumes/{volume_id}/directory` | [storage_directory](reference/app.md#symbol-storage_directory) — Возвращает список выбранной папки тома с признаками снимка и ошибок. |
| `POST` | `/api/storage/volumes/{volume_id}/directory-sizes` | [storage_directory_sizes](reference/app.md#symbol-storage_directory_sizes) — Возвращает размеры папок и при разрешении ставит их в очередь подсчёта. |
| `PATCH` | `/api/storage/volumes/{volume_id}/folder-tags` | [storage_folder_tags](reference/app.md#symbol-storage_folder_tags) — Сохраняет смысловые метки выбранной папки. |
| `PATCH` | `/api/storage/volumes/{volume_id}/metadata` | [storage_metadata](reference/app.md#symbol-storage_metadata) — Сохраняет пользовательские отметки расположения в каталоге. |
| `PATCH` | `/api/storage/volumes/{volume_id}/name` | [rename_removable](reference/app.md#symbol-rename_removable) — Меняет название подтверждённого сменного носителя. |
| `POST` | `/api/storage/volumes/{volume_id}/open-in-finder` | [open_storage_path_in_finder](reference/app.md#symbol-open_storage_path_in_finder) — Передаёт Finder проверенный путь выбранного тома. |
| `GET` | `/api/storage/volumes/{volume_id}/preview` | [storage_preview](reference/app.md#symbol-storage_preview) — Возвращает JPEG-превью обычного файла выбранного тома. |
| `POST` | `/api/storage/volumes/{volume_id}/register-removable` | [register_removable](reference/app.md#symbol-register_removable) — Регистрирует сменный носитель с выбранным названием. |
| `POST` | `/api/thumbnails/pause` | [pause_thumbnails](reference/app.md#symbol-pause_thumbnails) — Сохраняет общую ручную паузу фоновой очереди превью. |
| `POST` | `/api/thumbnails/resume` | [resume_thumbnails](reference/app.md#symbol-resume_thumbnails) — Снимает общую паузу превью и пробуждает воркеры. |
| `GET` | `/api/thumbnails/status` | [thumbnail_status](reference/app.md#symbol-thumbnail_status) — Возвращает очередь превью и диагностическое состояние её воркеров. |
| `GET` | `/health` | [health](reference/app.md#symbol-health) — Возвращает готовность HTTP-процесса и текущую ревизию каталога. |

## Параметры и ответы по маршрутам

### `GET /api/catalog/summary`

[catalog_summary](reference/app.md#symbol-catalog_summary). Возвращает суммарные показатели сохранённого медиаиндекса.

Декларированные ответы: `200` Successful Response.

### `POST /api/media/{media_id}/open`

[open_media_in_default_app](reference/app.md#symbol-open_media_in_default_app). Открывает обычный файл системной командой или выделяет объект Photos.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `media_id` | `path` | True | `{"title": "Media Id", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/media/{media_id}/thumbnail`

[media_thumbnail](reference/app.md#symbol-media_thumbnail). Отдаёт только готовый JPEG из кэша медиаиндекса.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `media_id` | `path` | True | `{"title": "Media Id", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/authorize`

[authorize_system_photos](reference/app.md#symbol-authorize_system_photos). Запрашивает разрешение Photos и возвращает состояние доступа.

Декларированные ответы: `200` Successful Response.

### `GET /api/photos/libraries`

[list_photo_libraries](reference/app.md#symbol-list_photo_libraries). Возвращает медиатеки, состояние подключения, превью и привязанные копии.

Декларированные ответы: `200` Successful Response.

### `POST /api/photos/libraries`

[register_photo_library](reference/app.md#symbol-register_photo_library). Регистрирует текущую медиатеку и ставит её первый скан в очередь.

Тело JSON: `{"$ref": "#/components/schemas/LibraryNameRequest"}`; обязательное: True.

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/connect`

[connect_photo_library](reference/app.md#symbol-connect_photo_library). Повторяет сопоставление системной медиатеки и пробуждает превью.

Декларированные ответы: `200` Successful Response.

### `PATCH /api/photos/libraries/{source_id}`

[rename_photo_library](reference/app.md#symbol-rename_photo_library). Меняет название медиатеки и возвращает обновлённый список.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Тело JSON: `{"$ref": "#/components/schemas/LibraryNameRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/photos/libraries/{source_id}/browse`

[browse_photo_library](reference/app.md#symbol-browse_photo_library). Возвращает виртуальную папку Photos и повышает приоритет её превью.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `path` | `query` | False | `{"default": "", "title": "Path", "type": "string"}` |
| `offset` | `query` | False | `{"default": 0, "minimum": 0, "title": "Offset", "type": "integer"}` |
| `limit` | `query` | False | `{"default": 150, "maximum": 1000, "minimum": 1, "title": "Limit", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/copies`

[bind_photo_library_copy](reference/app.md#symbol-bind_photo_library_copy). Привязывает выбранную папку как копию медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Тело JSON: `{"$ref": "#/components/schemas/LibraryCopyRequest"}`; обязательное: True.

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `DELETE /api/photos/libraries/{source_id}/copies/{link_id}`

[unbind_photo_library_copy](reference/app.md#symbol-unbind_photo_library_copy). Отключает привязку копии медиатеки и возвращает обновлённый список.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `link_id` | `path` | True | `{"title": "Link Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/copies/{link_id}/make-first`

[photo_copy_first](reference/app.md#symbol-photo_copy_first). Ставит выбранную копию Photos первой по номеру без изменения маршрутов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `link_id` | `path` | True | `{"title": "Link Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/photos/libraries/{source_id}/copies/{link_id}/originals`

[photo_originals_status](reference/app.md#symbol-photo_originals_status). Возвращает состояние оригиналов после проверки принадлежности копии медиатеке.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `link_id` | `path` | True | `{"title": "Link Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/photos/libraries/{source_id}/copies/{link_id}/originals/journal`

[photo_originals_journal](reference/app.md#symbol-photo_originals_journal). Возвращает журнал оригиналов и пути незавершённых записей.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `link_id` | `path` | True | `{"title": "Link Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/copies/{link_id}/originals/pause`

[pause_photo_originals](reference/app.md#symbol-pause_photo_originals). Запрашивает паузу сохранения оригиналов выбранной медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `link_id` | `path` | True | `{"title": "Link Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/copies/{link_id}/originals/start`

[start_photo_originals](reference/app.md#symbol-start_photo_originals). Запускает или планирует сохранение оригиналов в цепочку копий Photos.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `link_id` | `path` | True | `{"title": "Link Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/photos/libraries/{source_id}/copies/{link_id}/source`

[photo_copy_source](reference/app.md#symbol-photo_copy_source). Меняет источник привязанной копии Photos.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `link_id` | `path` | True | `{"title": "Link Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopySourceRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/pause`

[pause_photo_library](reference/app.md#symbol-pause_photo_library). Включает ручную паузу выбранной медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/photos/libraries/{source_id}/preview-status`

[photo_preview_status](reference/app.md#symbol-photo_preview_status). Возвращает готовые превью выбранных объектов медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `ids` | `query` | False | `{"default": [], "items": {"type": "integer"}, "title": "Ids", "type": "array"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/resume`

[resume_photo_library](reference/app.md#symbol-resume_photo_library). Снимает ручную паузу медиатеки и пробуждает очередь превью.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/photos/libraries/{source_id}/sync-schedule`

[set_photos_sync_schedule](reference/app.md#symbol-set_photos_sync_schedule). Сохраняет часы синхронизации выбранной медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Тело JSON: `{"$ref": "#/components/schemas/PhotosSyncScheduleRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/scan`

[scan_all_sources](reference/app.md#symbol-scan_all_sources). Запускает сканирование зарегистрированных источников.

Декларированные ответы: `200` Successful Response.

### `GET /api/sources`

[list_sources](reference/app.md#symbol-list_sources). Возвращает сохранённые источники медиаиндекса.

Декларированные ответы: `200` Successful Response.

### `POST /api/sources`

[create_source](reference/app.md#symbol-create_source). Регистрирует обычный источник, устанавливает наблюдение и запускает сканирование.

Тело JSON: `{"$ref": "#/components/schemas/SourceRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/sources/choose`

[choose_sources](reference/app.md#symbol-choose_sources). Регистрирует выбранные системным диалогом папки и запускает их сканирование.

Тело JSON: `{"$ref": "#/components/schemas/FolderChoiceRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `DELETE /api/sources/{source_id}`

[delete_source](reference/app.md#symbol-delete_source). Снимает наблюдение и удаляет источник из медиаиндекса.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/sources/{source_id}`

[update_source](reference/app.md#symbol-update_source). Обновляет роль, название и комментарий обычного источника.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Тело JSON: `{"$ref": "#/components/schemas/SourceMetadataRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/sources/{source_id}/files`

[source_files](reference/app.md#symbol-source_files). Возвращает файлы папки источника и повышает приоритет их превью.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |
| `folder` | `query` | False | `{"default": "", "title": "Folder", "type": "string"}` |
| `limit` | `query` | False | `{"default": 300, "maximum": 1000, "minimum": 1, "title": "Limit", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/sources/{source_id}/open-in-finder`

[open_source_folder_in_finder](reference/app.md#symbol-open_source_folder_in_finder). Открывает проверенную папку обычного источника в Finder.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Тело JSON: `{"$ref": "#/components/schemas/FolderRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/sources/{source_id}/scan`

[scan_one_source](reference/app.md#symbol-scan_one_source). Проверяет источник и выполняет его ручное сканирование.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/sources/{source_id}/tree`

[source_tree](reference/app.md#symbol-source_tree). Возвращает дерево виртуальных папок зарегистрированного источника.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"title": "Source Id", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons`

[comparison_jobs](reference/app.md#symbol-comparison_jobs). Возвращает историю общей сверки имён и старых отчётов.

Декларированные ответы: `200` Successful Response.

### `POST /api/storage/comparisons`

[start_comparison](reference/app.md#symbol-start_comparison). Создаёт общую сверку имён исходной области и выбранных целей.

Тело JSON: `{"$ref": "#/components/schemas/ComparisonRequest"}`; обязательное: True.

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}`

[comparison_job](reference/app.md#symbol-comparison_job). Возвращает состояние и области общей сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}/detail`

[comparison_detail](reference/app.md#symbol-comparison_detail). Возвращает найденные совпадения и подробности элемента отчёта.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |
| `path` | `query` | False | `{"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Path"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}/events`

[comparison_events](reference/app.md#symbol-comparison_events). Возвращает события общей сверки с обратной пагинацией.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |
| `before` | `query` | False | `{"anyOf": [{"minimum": 1, "type": "integer"}, {"type": "null"}], "title": "Before"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/comparisons/{job_id}/pause`

[pause_comparison](reference/app.md#symbol-pause_comparison). Запрашивает паузу общей сверки имён.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/comparisons/{job_id}/resume`

[resume_comparison](reference/app.md#symbol-resume_comparison). Продолжает сверку имён либо создаёт новую вместо старой проверки содержимого.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}/target-tree`

[comparison_target_tree](reference/app.md#symbol-comparison_target_tree). Возвращает страницу сохранённого дерева выбранной цели общей сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |
| `scan_id` | `query` | True | `{"minimum": 1, "title": "Scan Id", "type": "integer"}` |
| `path` | `query` | False | `{"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Path"}` |
| `offset` | `query` | False | `{"default": 0, "minimum": 0, "title": "Offset", "type": "integer"}` |
| `limit` | `query` | False | `{"default": 200, "maximum": 500, "minimum": 1, "title": "Limit", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}/tree`

[comparison_tree](reference/app.md#symbol-comparison_tree). Возвращает страницу исходного дерева общей сверки с фильтром статуса.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |
| `path` | `query` | False | `{"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Path"}` |
| `status` | `query` | False | `{"default": "", "title": "Status", "type": "string"}` |
| `offset` | `query` | False | `{"default": 0, "minimum": 0, "title": "Offset", "type": "integer"}` |
| `limit` | `query` | False | `{"default": 200, "maximum": 500, "minimum": 1, "title": "Limit", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/copy-groups`

[storage_copy_groups](reference/app.md#symbol-storage_copy_groups). Возвращает наборы папок с типами, метками и состоянием наблюдателей.

Декларированные ответы: `200` Successful Response.

### `POST /api/storage/copy-groups`

[storage_main_folder](reference/app.md#symbol-storage_main_folder). Регистрирует выбранную папку как основную область набора.

Тело JSON: `{"$ref": "#/components/schemas/ComparisonScope"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `DELETE /api/storage/copy-groups/{group_id}`

[storage_remove_copy_group](reference/app.md#symbol-storage_remove_copy_group). Удаляет набор папок из каталога без удаления пользовательских файлов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"title": "Group Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/copy-groups/{group_id}`

[storage_copy_group_settings](reference/app.md#symbol-storage_copy_group_settings). Обновляет настройки набора и пробуждает отслеживание изменений.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"title": "Group Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyGroupSettingsRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-groups/{group_id}/acknowledge`

[storage_acknowledge_folder_changes](reference/app.md#symbol-storage_acknowledge_folder_changes). Подтверждает конкретную версию уведомления об изменении папки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"title": "Group Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyGroupAcknowledgeRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/copy-groups/{group_id}/connection`

[storage_copy_group_connection](reference/app.md#symbol-storage_copy_group_connection). Меняет подключение всего набора папок.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"title": "Group Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyConnectionRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-groups/{group_id}/copies`

[storage_copy_location](reference/app.md#symbol-storage_copy_location). Добавляет папку копии к существующему набору.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"title": "Group Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyLocationRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-groups/{group_id}/renumber`

[storage_renumber_copies](reference/app.md#symbol-storage_renumber_copies). Применяет подтверждённую нумерацию по снимку текущих связей.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"title": "Group Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyRenumberRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `DELETE /api/storage/copy-locations/{location_id}`

[storage_remove_copy](reference/app.md#symbol-storage_remove_copy). Удаляет связь копии из каталога без удаления пользовательских файлов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"title": "Location Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/copy-locations/{location_id}`

[storage_copy_kind](reference/app.md#symbol-storage_copy_kind). Меняет тип зарегистрированной копии.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"title": "Location Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyKindRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/copy-locations/{location_id}/connection`

[storage_copy_location_connection](reference/app.md#symbol-storage_copy_location_connection). Меняет подключение одной обычной копии.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"title": "Location Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyConnectionRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-locations/{location_id}/release-number`

[storage_release_copy_number](reference/app.md#symbol-storage_release_copy_number). Архивирует прежнюю привязку и освобождает её номер.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"title": "Location Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyNumberReleaseRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/copy-locations/{location_id}/source`

[storage_copy_source](reference/app.md#symbol-storage_copy_source). Обрабатывает изменение источника копирования обычной папки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"title": "Location Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopySourceRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/copy-operations/{operation_id}`

[missing_copy_job](reference/app.md#symbol-missing_copy_job). Возвращает состояние операции копирования отсутствующих элементов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `operation_id` | `path` | True | `{"title": "Operation Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/copy-operations/{operation_id}/items`

[missing_copy_items](reference/app.md#symbol-missing_copy_items). Возвращает страницу элементов сохранённого плана копирования.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `operation_id` | `path` | True | `{"title": "Operation Id", "type": "string"}` |
| `offset` | `query` | False | `{"default": 0, "minimum": 0, "title": "Offset", "type": "integer"}` |
| `limit` | `query` | False | `{"default": 200, "maximum": 1000, "minimum": 1, "title": "Limit", "type": "integer"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-operations/{operation_id}/start`

[start_missing_copy](reference/app.md#symbol-start_missing_copy). Запускает подтверждённую операцию создания отсутствующих копий.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `operation_id` | `path` | True | `{"title": "Operation Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-operations/{operation_id}/stop`

[stop_missing_copy](reference/app.md#symbol-stop_missing_copy). Запрашивает остановку операции копирования.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `operation_id` | `path` | True | `{"title": "Operation Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/folder-markers`

[storage_folder_markers](reference/app.md#symbol-storage_folder_markers). Возвращает состояние очереди служебных описаний папок.

Декларированные ответы: `200` Successful Response.

### `GET /api/storage/nas`

[remembered_nas](reference/app.md#symbol-remembered_nas). Возвращает список сохранённых серверов NAS.

Декларированные ответы: `200` Successful Response.

### `POST /api/storage/nas/discover`

[discover_nas](reference/app.md#symbol-discover_nas). Запускает обнаружение NAS через Bonjour на машине Core.

Декларированные ответы: `200` Successful Response.

### `POST /api/storage/nas/{server_id}/remember`

[remember_nas_share](reference/app.md#symbol-remember_nas_share). Сохраняет выбранный SMB-ресурс без подключения.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `server_id` | `path` | True | `{"title": "Server Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/NetworkShareRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/nas/{server_id}/shares`

[nas_shares](reference/app.md#symbol-nas_shares). Возвращает сохранённые либо обновлённые ресурсы выбранного NAS.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `server_id` | `path` | True | `{"title": "Server Id", "type": "string"}` |
| `refresh` | `query` | False | `{"default": false, "title": "Refresh", "type": "boolean"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/paired-comparisons`

[paired_jobs](reference/app.md#symbol-paired_jobs). Возвращает историю парных сверок и допустимые решения для лишних элементов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `copy_id` | `query` | False | `{"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Copy Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/paired-comparisons`

[start_paired_comparison](reference/app.md#symbol-start_paired_comparison). Создаёт и запускает сверку зарегистрированной пары папок.

Тело JSON: `{"$ref": "#/components/schemas/PairedComparisonRequest"}`; обязательное: True.

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `GET /api/storage/paired-comparisons/{job_id}`

[paired_job](reference/app.md#symbol-paired_job). Возвращает состояние одной парной сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/paired-comparisons/{job_id}/copy-plan`

[missing_copy_plan](reference/app.md#symbol-missing_copy_plan). Создаёт сохранённый план копирования по завершённому файловому отчёту.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `PATCH /api/storage/paired-comparisons/{job_id}/decision`

[paired_decision](reference/app.md#symbol-paired_decision). Сохраняет плановое решение для элемента только в копии.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/PairedDecisionRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/paired-comparisons/{job_id}/pause`

[pause_paired_job](reference/app.md#symbol-pause_paired_job). Запрашивает паузу парной сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/paired-comparisons/{job_id}/resume`

[resume_paired_job](reference/app.md#symbol-resume_paired_job). Продолжает парную сверку после проверки конфликтующих операций.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/paired-comparisons/{job_id}/rows`

[paired_rows](reference/app.md#symbol-paired_rows). Возвращает страницу выровненных строк парной сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"title": "Job Id", "type": "string"}` |
| `offset` | `query` | False | `{"default": 0, "minimum": 0, "title": "Offset", "type": "integer"}` |
| `limit` | `query` | False | `{"default": 1000, "maximum": 5000, "minimum": 1, "title": "Limit", "type": "integer"}` |
| `differences_only` | `query` | False | `{"default": false, "title": "Differences Only", "type": "boolean"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/volumes`

[storage_volumes](reference/app.md#symbol-storage_volumes). Возвращает обнаруженные и сохранённые тома через API Core.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `refresh` | `query` | False | `{"default": false, "title": "Refresh", "type": "boolean"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/volumes/{volume_id}/connect`

[connect_network_volume](reference/app.md#symbol-connect_network_volume). Открывает подключение сетевого тома в Finder на машине Core.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"title": "Volume Id", "type": "string"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/volumes/{volume_id}/directory`

[storage_directory](reference/app.md#symbol-storage_directory). Возвращает список выбранной папки тома с признаками снимка и ошибок.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"title": "Volume Id", "type": "string"}` |
| `path` | `query` | False | `{"default": "", "title": "Path", "type": "string"}` |
| `refresh` | `query` | False | `{"default": true, "title": "Refresh", "type": "boolean"}` |
| `discover` | `query` | False | `{"default": true, "title": "Discover", "type": "boolean"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/volumes/{volume_id}/directory-sizes`

[storage_directory_sizes](reference/app.md#symbol-storage_directory_sizes). Возвращает размеры папок и при разрешении ставит их в очередь подсчёта.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"title": "Volume Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/DirectorySizesRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/volumes/{volume_id}/folder-tags`

[storage_folder_tags](reference/app.md#symbol-storage_folder_tags). Сохраняет смысловые метки выбранной папки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"title": "Volume Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/FolderTagsRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/volumes/{volume_id}/metadata`

[storage_metadata](reference/app.md#symbol-storage_metadata). Сохраняет пользовательские отметки расположения в каталоге.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"title": "Volume Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/StorageMetadataRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/volumes/{volume_id}/name`

[rename_removable](reference/app.md#symbol-rename_removable). Меняет название подтверждённого сменного носителя.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"title": "Volume Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/VolumeNameRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/volumes/{volume_id}/open-in-finder`

[open_storage_path_in_finder](reference/app.md#symbol-open_storage_path_in_finder). Передаёт Finder проверенный путь выбранного тома.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"title": "Volume Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/StoragePathRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/volumes/{volume_id}/preview`

[storage_preview](reference/app.md#symbol-storage_preview). Возвращает JPEG-превью обычного файла выбранного тома.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"title": "Volume Id", "type": "string"}` |
| `path` | `query` | True | `{"title": "Path", "type": "string"}` |
| `large` | `query` | False | `{"default": false, "title": "Large", "type": "boolean"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/volumes/{volume_id}/register-removable`

[register_removable](reference/app.md#symbol-register_removable). Регистрирует сменный носитель с выбранным названием.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"title": "Volume Id", "type": "string"}` |

Тело JSON: `{"$ref": "#/components/schemas/VolumeNameRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/thumbnails/pause`

[pause_thumbnails](reference/app.md#symbol-pause_thumbnails). Сохраняет общую ручную паузу фоновой очереди превью.

Декларированные ответы: `200` Successful Response.

### `POST /api/thumbnails/resume`

[resume_thumbnails](reference/app.md#symbol-resume_thumbnails). Снимает общую паузу превью и пробуждает воркеры.

Декларированные ответы: `200` Successful Response.

### `GET /api/thumbnails/status`

[thumbnail_status](reference/app.md#symbol-thumbnail_status). Возвращает очередь превью и диагностическое состояние её воркеров.

Декларированные ответы: `200` Successful Response.

### `GET /health`

[health](reference/app.md#symbol-health). Возвращает готовность HTTP-процесса и текущую ревизию каталога.

Декларированные ответы: `200` Successful Response.

## Схемы Pydantic и валидации

required задаёт обязательность поля, null в anyOf допускает None, additionalProperties=false запрещает лишние поля. Унаследованные поля раскрыты в схеме.

### `ComparisonRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "reread": {
      "default": false,
      "title": "Reread",
      "type": "boolean"
    },
    "reuse_index": {
      "default": true,
      "title": "Reuse Index",
      "type": "boolean"
    },
    "source": {
      "$ref": "#/components/schemas/ComparisonScope"
    },
    "targets": {
      "items": {
        "$ref": "#/components/schemas/ComparisonScope"
      },
      "maxItems": 16,
      "minItems": 1,
      "title": "Targets",
      "type": "array"
    }
  },
  "required": [
    "source",
    "targets"
  ],
  "title": "ComparisonRequest",
  "type": "object"
}
```

### `ComparisonScope`

```json
{
  "additionalProperties": false,
  "properties": {
    "path": {
      "default": "",
      "maxLength": 4096,
      "title": "Path",
      "type": "string"
    },
    "volume_id": {
      "maxLength": 128,
      "minLength": 1,
      "title": "Volume Id",
      "type": "string"
    }
  },
  "required": [
    "volume_id"
  ],
  "title": "ComparisonScope",
  "type": "object"
}
```

### `CopyConnectionRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "connected": {
      "title": "Connected",
      "type": "boolean"
    }
  },
  "required": [
    "connected"
  ],
  "title": "CopyConnectionRequest",
  "type": "object"
}
```

### `CopyGroupAcknowledgeRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "changed_at": {
      "maxLength": 64,
      "minLength": 1,
      "title": "Changed At",
      "type": "string"
    }
  },
  "required": [
    "changed_at"
  ],
  "title": "CopyGroupAcknowledgeRequest",
  "type": "object"
}
```

### `CopyGroupSettingsRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "label": {
      "anyOf": [
        {
          "enum": [
            "",
            "temporary",
            "inbox",
            "archive"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Label"
    },
    "tracking": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "title": "Tracking"
    }
  },
  "title": "CopyGroupSettingsRequest",
  "type": "object"
}
```

### `CopyKindRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "kind": {
      "enum": [
        "copy",
        "cold",
        "cloud"
      ],
      "title": "Kind",
      "type": "string"
    }
  },
  "required": [
    "kind"
  ],
  "title": "CopyKindRequest",
  "type": "object"
}
```

### `CopyLocationRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "kind": {
      "default": "copy",
      "enum": [
        "copy",
        "cold",
        "cloud"
      ],
      "title": "Kind",
      "type": "string"
    },
    "path": {
      "default": "",
      "maxLength": 4096,
      "title": "Path",
      "type": "string"
    },
    "volume_id": {
      "maxLength": 128,
      "minLength": 1,
      "title": "Volume Id",
      "type": "string"
    }
  },
  "required": [
    "volume_id"
  ],
  "title": "CopyLocationRequest",
  "type": "object"
}
```

### `CopyNumberReleaseRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "kind": {
      "enum": [
        "copy",
        "cold",
        "cloud"
      ],
      "title": "Kind",
      "type": "string"
    },
    "number": {
      "exclusiveMinimum": 0.0,
      "title": "Number",
      "type": "integer"
    }
  },
  "required": [
    "kind",
    "number"
  ],
  "title": "CopyNumberReleaseRequest",
  "type": "object"
}
```

### `CopyNumberSnapshot`

```json
{
  "additionalProperties": false,
  "properties": {
    "id": {
      "maxLength": 128,
      "minLength": 1,
      "title": "Id",
      "type": "string"
    },
    "kind": {
      "enum": [
        "copy",
        "cold",
        "cloud"
      ],
      "title": "Kind",
      "type": "string"
    },
    "number": {
      "exclusiveMinimum": 0.0,
      "title": "Number",
      "type": "integer"
    }
  },
  "required": [
    "kind",
    "id",
    "number"
  ],
  "title": "CopyNumberSnapshot",
  "type": "object"
}
```

### `CopyRenumberRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "copies": {
      "items": {
        "$ref": "#/components/schemas/CopyNumberSnapshot"
      },
      "title": "Copies",
      "type": "array"
    }
  },
  "required": [
    "copies"
  ],
  "title": "CopyRenumberRequest",
  "type": "object"
}
```

### `CopySourceRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "source_id": {
      "anyOf": [
        {
          "maxLength": 128,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Source Id"
    }
  },
  "title": "CopySourceRequest",
  "type": "object"
}
```

### `DirectorySizesRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "paths": {
      "items": {
        "type": "string"
      },
      "maxItems": 500,
      "minItems": 1,
      "title": "Paths",
      "type": "array"
    },
    "refresh": {
      "default": false,
      "title": "Refresh",
      "type": "boolean"
    },
    "start": {
      "default": true,
      "title": "Start",
      "type": "boolean"
    }
  },
  "required": [
    "paths"
  ],
  "title": "DirectorySizesRequest",
  "type": "object"
}
```

### `FolderChoiceRequest`

```json
{
  "properties": {
    "comment": {
      "default": "",
      "title": "Comment",
      "type": "string"
    },
    "label": {
      "default": "",
      "title": "Label",
      "type": "string"
    },
    "role": {
      "default": "source",
      "enum": [
        "source",
        "storage"
      ],
      "title": "Role",
      "type": "string"
    }
  },
  "title": "FolderChoiceRequest",
  "type": "object"
}
```

### `FolderRequest`

```json
{
  "properties": {
    "folder": {
      "default": "",
      "title": "Folder",
      "type": "string"
    }
  },
  "title": "FolderRequest",
  "type": "object"
}
```

### `FolderTagsRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "path": {
      "default": "",
      "maxLength": 4096,
      "title": "Path",
      "type": "string"
    },
    "tags": {
      "items": {
        "enum": [
          "old_copy",
          "sort",
          "check"
        ],
        "type": "string"
      },
      "maxItems": 3,
      "title": "Tags",
      "type": "array"
    }
  },
  "required": [
    "tags"
  ],
  "title": "FolderTagsRequest",
  "type": "object"
}
```

### `HTTPValidationError`

```json
{
  "properties": {
    "detail": {
      "items": {
        "$ref": "#/components/schemas/ValidationError"
      },
      "title": "Detail",
      "type": "array"
    }
  },
  "title": "HTTPValidationError",
  "type": "object"
}
```

### `LibraryCopyRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "path": {
      "maxLength": 4096,
      "minLength": 1,
      "title": "Path",
      "type": "string"
    },
    "volume_id": {
      "maxLength": 128,
      "minLength": 1,
      "title": "Volume Id",
      "type": "string"
    }
  },
  "required": [
    "volume_id",
    "path"
  ],
  "title": "LibraryCopyRequest",
  "type": "object"
}
```

### `LibraryNameRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "label": {
      "maxLength": 120,
      "minLength": 1,
      "title": "Label",
      "type": "string"
    }
  },
  "required": [
    "label"
  ],
  "title": "LibraryNameRequest",
  "type": "object"
}
```

### `NetworkShareRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "share": {
      "maxLength": 255,
      "minLength": 1,
      "title": "Share",
      "type": "string"
    }
  },
  "required": [
    "share"
  ],
  "title": "NetworkShareRequest",
  "type": "object"
}
```

### `PairedComparisonRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "base_job_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Base Job Id"
    },
    "copy_id": {
      "maxLength": 128,
      "minLength": 1,
      "title": "Copy Id",
      "type": "string"
    },
    "method": {
      "default": "size",
      "enum": [
        "size",
        "sha256"
      ],
      "title": "Method",
      "type": "string"
    },
    "mode": {
      "default": "folders",
      "enum": [
        "folders",
        "files"
      ],
      "title": "Mode",
      "type": "string"
    }
  },
  "required": [
    "copy_id"
  ],
  "title": "PairedComparisonRequest",
  "type": "object"
}
```

### `PairedDecisionRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "action": {
      "anyOf": [
        {
          "enum": [
            "keep",
            "add_main",
            "move",
            "remove"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Action"
    },
    "path": {
      "maxLength": 4096,
      "title": "Path",
      "type": "string"
    }
  },
  "required": [
    "path",
    "action"
  ],
  "title": "PairedDecisionRequest",
  "type": "object"
}
```

### `PhotosSyncScheduleRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "end_hour": {
      "default": 7,
      "maximum": 23.0,
      "minimum": 0.0,
      "title": "End Hour",
      "type": "integer"
    },
    "night_only": {
      "title": "Night Only",
      "type": "boolean"
    },
    "start_hour": {
      "default": 0,
      "maximum": 23.0,
      "minimum": 0.0,
      "title": "Start Hour",
      "type": "integer"
    },
    "timezone": {
      "const": "Europe/Moscow",
      "default": "Europe/Moscow",
      "title": "Timezone",
      "type": "string"
    }
  },
  "required": [
    "night_only"
  ],
  "title": "PhotosSyncScheduleRequest",
  "type": "object"
}
```

### `SourceMetadataRequest`

```json
{
  "properties": {
    "comment": {
      "default": "",
      "title": "Comment",
      "type": "string"
    },
    "label": {
      "default": "",
      "title": "Label",
      "type": "string"
    },
    "role": {
      "enum": [
        "source",
        "storage"
      ],
      "title": "Role",
      "type": "string"
    }
  },
  "required": [
    "role"
  ],
  "title": "SourceMetadataRequest",
  "type": "object"
}
```

### `SourceRequest`

```json
{
  "properties": {
    "comment": {
      "default": "",
      "title": "Comment",
      "type": "string"
    },
    "label": {
      "default": "",
      "title": "Label",
      "type": "string"
    },
    "path": {
      "title": "Path",
      "type": "string"
    },
    "role": {
      "default": "source",
      "enum": [
        "source",
        "storage"
      ],
      "title": "Role",
      "type": "string"
    }
  },
  "required": [
    "path"
  ],
  "title": "SourceRequest",
  "type": "object"
}
```

### `StorageMetadataRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "comment": {
      "default": "",
      "maxLength": 4000,
      "title": "Comment",
      "type": "string"
    },
    "no_duplicate": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "title": "No Duplicate"
    },
    "path": {
      "default": "",
      "title": "Path",
      "type": "string"
    },
    "planned_move": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "title": "Planned Move"
    },
    "purpose": {
      "anyOf": [
        {
          "enum": [
            "",
            "media",
            "documents",
            "projects",
            "mixed"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Purpose"
    },
    "role": {
      "anyOf": [
        {
          "enum": [
            "",
            "primary",
            "copy",
            "archive",
            "temporary"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Role"
    }
  },
  "title": "StorageMetadataRequest",
  "type": "object"
}
```

### `StoragePathRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "path": {
      "default": "",
      "maxLength": 4096,
      "title": "Path",
      "type": "string"
    }
  },
  "title": "StoragePathRequest",
  "type": "object"
}
```

### `ValidationError`

```json
{
  "properties": {
    "ctx": {
      "title": "Context",
      "type": "object"
    },
    "input": {
      "title": "Input"
    },
    "loc": {
      "items": {
        "anyOf": [
          {
            "type": "string"
          },
          {
            "type": "integer"
          }
        ]
      },
      "title": "Location",
      "type": "array"
    },
    "msg": {
      "title": "Message",
      "type": "string"
    },
    "type": {
      "title": "Error Type",
      "type": "string"
    }
  },
  "required": [
    "loc",
    "msg",
    "type"
  ],
  "title": "ValidationError",
  "type": "object"
}
```

### `VolumeNameRequest`

```json
{
  "additionalProperties": false,
  "properties": {
    "name": {
      "maxLength": 120,
      "minLength": 1,
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "title": "VolumeNameRequest",
  "type": "object"
}
```
