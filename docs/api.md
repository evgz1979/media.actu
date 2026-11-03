# HTTP API Core

Проверено 2026-11-03. Ниже перечислены все 84 маршрута Core по фактическому OpenAPI текущего приложения и 26 схем запросов. Сервисы доступны на loopback; базовый адрес Core — `http://127.0.0.1:18765`. Интерактивный OpenAPI — `/docs`. NiceGUI обслуживается другим процессом на 8090.

Не все ошибки задекларированы в OpenAPI: для каждого обработчика дана ссылка на реализацию, а точные перехваты и выражения HTTPException перечислены в [справочнике app.py](reference/app.md). `422` означает отказ Pydantic/Query; `400` — ошибку параметров или состояния, когда она переведена обработчиком; `404` — отсутствие записи/ресурса; Photos также использует `403`, `409`, `503` в зависимости от маршрута. Не следует ожидать одинаковый набор кодов от всех методов.

GET-методы могут пополнять снимки, приоритеты превью или кэш: HTTP-метод сам по себе не является обещанием отсутствия производных записей. Удаление связи или источника из каталога не является удалением пользовательских файлов. Запуск копирования — отдельная команда; обычная сверка не запускает копирование.

## Все маршруты

| Метод | Путь | Назначение и обработчик |
| --- | --- | --- |
| `GET` | `/health` | [health](../app.py#L247) — Возвращает готовность HTTP-процесса и текущую ревизию каталога. |
| `GET` | `/api/storage/volumes` | [storage_volumes](../app.py#L274) — Возвращает обнаруженные и сохранённые тома через API Core. |
| `POST` | `/api/storage/volumes/{volume_id}/register-removable` | [register_removable](../app.py#L288) — Регистрирует сменный носитель с выбранным названием. |
| `PATCH` | `/api/storage/volumes/{volume_id}/name` | [rename_removable](../app.py#L298) — Меняет название подтверждённого сменного носителя. |
| `GET` | `/api/storage/nas` | [remembered_nas](../app.py#L315) — Возвращает список сохранённых серверов NAS. |
| `POST` | `/api/storage/nas/discover` | [discover_nas](../app.py#L322) — Запускает обнаружение NAS через Bonjour на машине Core. |
| `GET` | `/api/storage/nas/{server_id}/shares` | [nas_shares](../app.py#L329) — Возвращает сохранённые либо обновлённые ресурсы выбранного NAS. |
| `POST` | `/api/storage/nas/{server_id}/remember` | [remember_nas_share](../app.py#L339) — Сохраняет выбранный SMB-ресурс без подключения. |
| `POST` | `/api/storage/volumes/{volume_id}/connect` | [connect_network_volume](../app.py#L351) — Открывает подключение сетевого тома в Finder на машине Core. |
| `GET` | `/api/storage/volumes/{volume_id}/directory` | [storage_directory](../app.py#L363) — Возвращает список выбранной папки тома с признаками снимка и ошибок. |
| `GET` | `/api/storage/volumes/{volume_id}/preview` | [storage_preview](../app.py#L375) — Возвращает JPEG-превью обычного файла выбранного тома. |
| `POST` | `/api/storage/volumes/{volume_id}/directory-sizes` | [storage_directory_sizes](../app.py#L406) — Возвращает размеры папок и при разрешении ставит их в очередь подсчёта. |
| `POST` | `/api/storage/volumes/{volume_id}/open-in-finder` | [open_storage_path_in_finder](../app.py#L419) — Передаёт Finder проверенный путь выбранного тома. |
| `PATCH` | `/api/storage/volumes/{volume_id}/metadata` | [storage_metadata](../app.py#L431) — Сохраняет пользовательские отметки расположения в каталоге. |
| `PATCH` | `/api/storage/volumes/{volume_id}/folder-tags` | [storage_folder_tags](../app.py#L443) — Сохраняет смысловые метки выбранной папки. |
| `PATCH` | `/api/storage/copy-locations/{location_id}/source` | [storage_copy_source](../app.py#L534) — Обрабатывает изменение источника копирования обычной папки. |
| `GET` | `/api/storage/copy-groups` | [storage_copy_groups](../app.py#L563) — Возвращает наборы папок с типами, метками и состоянием наблюдателей. |
| `POST` | `/api/storage/copy-groups` | [storage_main_folder](../app.py#L579) — Регистрирует выбранную папку как основную область набора. |
| `GET` | `/api/storage/folder-markers` | [storage_folder_markers](../app.py#L572) — Возвращает состояние очереди служебных описаний папок. |
| `PATCH` | `/api/storage/copy-groups/{group_id}` | [storage_copy_group_settings](../app.py#L586) — Обновляет настройки набора и пробуждает отслеживание изменений. |
| `DELETE` | `/api/storage/copy-groups/{group_id}` | [storage_remove_copy_group](../app.py#L663) — Удаляет набор папок из каталога без удаления пользовательских файлов. |
| `POST` | `/api/storage/copy-groups/{group_id}/acknowledge` | [storage_acknowledge_folder_changes](../app.py#L595) — Подтверждает конкретную версию уведомления об изменении папки. |
| `PATCH` | `/api/storage/copy-groups/{group_id}/connection` | [storage_copy_group_connection](../app.py#L602) — Меняет подключение всего набора папок. |
| `PATCH` | `/api/storage/copy-locations/{location_id}/connection` | [storage_copy_location_connection](../app.py#L611) — Меняет подключение одной обычной копии. |
| `POST` | `/api/storage/copy-groups/{group_id}/copies` | [storage_copy_location](../app.py#L618) — Добавляет папку копии к существующему набору. |
| `POST` | `/api/storage/copy-locations/{location_id}/release-number` | [storage_release_copy_number](../app.py#L634) — Архивирует прежнюю привязку и освобождает её номер. |
| `PATCH` | `/api/storage/copy-locations/{location_id}` | [storage_copy_kind](../app.py#L641) — Меняет тип зарегистрированной копии. |
| `DELETE` | `/api/storage/copy-locations/{location_id}` | [storage_remove_copy](../app.py#L655) — Удаляет связь копии из каталога без удаления пользовательских файлов. |
| `POST` | `/api/storage/copy-groups/{group_id}/renumber` | [storage_renumber_copies](../app.py#L648) — Применяет подтверждённую нумерацию по снимку текущих связей. |
| `GET` | `/api/storage/paired-comparisons` | [paired_jobs](../app.py#L719) — Возвращает историю парных сверок и допустимые решения для лишних элементов. |
| `POST` | `/api/storage/paired-comparisons` | [start_paired_comparison](../app.py#L726) — Создаёт и запускает сверку зарегистрированной пары папок. |
| `GET` | `/api/storage/paired-comparisons/{job_id}` | [paired_job](../app.py#L734) — Возвращает состояние одной парной сверки. |
| `GET` | `/api/storage/paired-comparisons/{job_id}/rows` | [paired_rows](../app.py#L741) — Возвращает страницу выровненных строк парной сверки. |
| `POST` | `/api/storage/paired-comparisons/{job_id}/pause` | [pause_paired_job](../app.py#L749) — Запрашивает паузу парной сверки. |
| `POST` | `/api/storage/paired-comparisons/{job_id}/resume` | [resume_paired_job](../app.py#L756) — Продолжает парную сверку после проверки конфликтующих операций. |
| `PATCH` | `/api/storage/paired-comparisons/{job_id}/decision` | [paired_decision](../app.py#L763) — Сохраняет плановое решение для элемента только в копии. |
| `GET` | `/api/storage/comparisons` | [comparison_jobs](../app.py#L770) — Возвращает историю общей сверки имён и старых отчётов. |
| `POST` | `/api/storage/comparisons` | [start_comparison](../app.py#L813) — Создаёт общую сверку имён исходной области и выбранных целей. |
| `POST` | `/api/storage/paired-comparisons/{job_id}/copy-plan` | [missing_copy_plan](../app.py#L777) — Создаёт сохранённый план копирования по завершённому файловому отчёту. |
| `GET` | `/api/storage/copy-operations/{operation_id}` | [missing_copy_job](../app.py#L784) — Возвращает состояние операции копирования отсутствующих элементов. |
| `GET` | `/api/storage/copy-operations/{operation_id}/items` | [missing_copy_items](../app.py#L791) — Возвращает страницу элементов сохранённого плана копирования. |
| `POST` | `/api/storage/copy-operations/{operation_id}/start` | [start_missing_copy](../app.py#L799) — Запускает подтверждённую операцию создания отсутствующих копий. |
| `POST` | `/api/storage/copy-operations/{operation_id}/stop` | [stop_missing_copy](../app.py#L806) — Запрашивает остановку операции копирования. |
| `GET` | `/api/storage/comparisons/{job_id}` | [comparison_job](../app.py#L821) — Возвращает состояние и области общей сверки. |
| `POST` | `/api/storage/comparisons/{job_id}/pause` | [pause_comparison](../app.py#L828) — Запрашивает паузу общей сверки имён. |
| `POST` | `/api/storage/comparisons/{job_id}/resume` | [resume_comparison](../app.py#L835) — Продолжает сверку имён либо создаёт новую вместо старой проверки содержимого. |
| `GET` | `/api/storage/comparisons/{job_id}/tree` | [comparison_tree](../app.py#L842) — Возвращает страницу исходного дерева общей сверки с фильтром статуса. |
| `GET` | `/api/storage/comparisons/{job_id}/target-tree` | [comparison_target_tree](../app.py#L850) — Возвращает страницу сохранённого дерева выбранной цели общей сверки. |
| `GET` | `/api/storage/comparisons/{job_id}/detail` | [comparison_detail](../app.py#L858) — Возвращает найденные совпадения и подробности элемента отчёта. |
| `GET` | `/api/storage/comparisons/{job_id}/events` | [comparison_events](../app.py#L865) — Возвращает события общей сверки с обратной пагинацией. |
| `GET` | `/api/sources` | [list_sources](../app.py#L872) — Возвращает сохранённые источники медиаиндекса. |
| `POST` | `/api/sources` | [create_source](../app.py#L879) — Регистрирует обычный источник, устанавливает наблюдение и запускает сканирование. |
| `POST` | `/api/sources/choose` | [choose_sources](../app.py#L897) — Регистрирует выбранные системным диалогом папки и запускает их сканирование. |
| `PATCH` | `/api/sources/{source_id}` | [update_source](../app.py#L922) — Обновляет роль, название и комментарий обычного источника. |
| `DELETE` | `/api/sources/{source_id}` | [delete_source](../app.py#L940) — Снимает наблюдение и удаляет источник из медиаиндекса. |
| `POST` | `/api/sources/{source_id}/scan` | [scan_one_source](../app.py#L957) — Проверяет источник и выполняет его ручное сканирование. |
| `POST` | `/api/scan` | [scan_all_sources](../app.py#L971) — Запускает сканирование зарегистрированных источников. |
| `POST` | `/api/photos/authorize` | [authorize_system_photos](../app.py#L992) — Запрашивает разрешение Photos и возвращает состояние доступа. |
| `PATCH` | `/api/photos/libraries/{source_id}/sync-schedule` | [set_photos_sync_schedule](../app.py#L1053) — Сохраняет часы синхронизации выбранной медиатеки. |
| `GET` | `/api/photos/libraries` | [list_photo_libraries](../app.py#L1062) — Возвращает медиатеки, состояние подключения, превью и привязанные копии. |
| `POST` | `/api/photos/libraries` | [register_photo_library](../app.py#L1098) — Регистрирует текущую медиатеку и ставит её первый скан в очередь. |
| `POST` | `/api/photos/libraries/connect` | [connect_photo_library](../app.py#L1069) — Повторяет сопоставление системной медиатеки и пробуждает превью. |
| `GET` | `/api/photos/libraries/{source_id}/browse` | [browse_photo_library](../app.py#L1078) — Возвращает виртуальную папку Photos и повышает приоритет её превью. |
| `GET` | `/api/photos/libraries/{source_id}/preview-status` | [photo_preview_status](../app.py#L1089) — Возвращает готовые превью выбранных объектов медиатеки. |
| `PATCH` | `/api/photos/libraries/{source_id}` | [rename_photo_library](../app.py#L1107) — Меняет название медиатеки и возвращает обновлённый список. |
| `POST` | `/api/photos/libraries/{source_id}/pause` | [pause_photo_library](../app.py#L1115) — Включает ручную паузу выбранной медиатеки. |
| `POST` | `/api/photos/libraries/{source_id}/resume` | [resume_photo_library](../app.py#L1123) — Снимает ручную паузу медиатеки и пробуждает очередь превью. |
| `POST` | `/api/photos/libraries/{source_id}/copies` | [bind_photo_library_copy](../app.py#L1132) — Привязывает выбранную папку как копию медиатеки. |
| `DELETE` | `/api/photos/libraries/{source_id}/copies/{link_id}` | [unbind_photo_library_copy](../app.py#L1139) — Отключает привязку копии медиатеки и возвращает обновлённый список. |
| `PATCH` | `/api/photos/libraries/{source_id}/copies/{link_id}/source` | [photo_copy_source](../app.py#L1147) — Меняет источник привязанной копии Photos. |
| `POST` | `/api/photos/libraries/{source_id}/copies/{link_id}/make-first` | [photo_copy_first](../app.py#L1155) — Ставит выбранную копию Photos первой по номеру без изменения маршрутов. |
| `POST` | `/api/photos/libraries/{source_id}/copies/{link_id}/originals/start` | [start_photo_originals](../app.py#L1163) — Запускает или планирует сохранение оригиналов в цепочку копий Photos. |
| `POST` | `/api/photos/libraries/{source_id}/copies/{link_id}/originals/pause` | [pause_photo_originals](../app.py#L1170) — Запрашивает паузу сохранения оригиналов выбранной медиатеки. |
| `GET` | `/api/photos/libraries/{source_id}/copies/{link_id}/originals` | [photo_originals_status](../app.py#L1177) — Возвращает состояние оригиналов после проверки принадлежности копии медиатеке. |
| `GET` | `/api/photos/libraries/{source_id}/copies/{link_id}/originals/journal` | [photo_originals_journal](../app.py#L1185) — Возвращает журнал оригиналов и пути незавершённых записей. |
| `GET` | `/api/catalog/summary` | [catalog_summary](../app.py#L1192) — Возвращает суммарные показатели сохранённого медиаиндекса. |
| `GET` | `/api/sources/{source_id}/tree` | [source_tree](../app.py#L1199) — Возвращает дерево виртуальных папок зарегистрированного источника. |
| `GET` | `/api/sources/{source_id}/files` | [source_files](../app.py#L1208) — Возвращает файлы папки источника и повышает приоритет их превью. |
| `GET` | `/api/thumbnails/status` | [thumbnail_status](../app.py#L1227) — Возвращает очередь превью и диагностическое состояние её воркеров. |
| `POST` | `/api/thumbnails/pause` | [pause_thumbnails](../app.py#L1234) — Сохраняет общую ручную паузу фоновой очереди превью. |
| `POST` | `/api/thumbnails/resume` | [resume_thumbnails](../app.py#L1242) — Снимает общую паузу превью и пробуждает воркеры. |
| `POST` | `/api/sources/{source_id}/open-in-finder` | [open_source_folder_in_finder](../app.py#L1251) — Открывает проверенную папку обычного источника в Finder. |
| `GET` | `/api/media/{media_id}/thumbnail` | [media_thumbnail](../app.py#L1280) — Отдаёт только готовый JPEG из кэша медиаиндекса. |
| `POST` | `/api/media/{media_id}/open` | [open_media_in_default_app](../app.py#L1299) — Открывает обычный файл системной командой или выделяет объект Photos. |

## Параметры и ответы по маршрутам

### `GET /health`

[health](../app.py#L247). Возвращает готовность HTTP-процесса и текущую ревизию каталога.

Декларированные ответы: `200` Successful Response.

### `GET /api/storage/volumes`

[storage_volumes](../app.py#L274). Возвращает обнаруженные и сохранённые тома через API Core.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `refresh` | `query` | False | `{"type": "boolean", "default": false, "title": "Refresh"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/volumes/{volume_id}/register-removable`

[register_removable](../app.py#L288). Регистрирует сменный носитель с выбранным названием.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"type": "string", "title": "Volume Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/VolumeNameRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/volumes/{volume_id}/name`

[rename_removable](../app.py#L298). Меняет название подтверждённого сменного носителя.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"type": "string", "title": "Volume Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/VolumeNameRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/nas`

[remembered_nas](../app.py#L315). Возвращает список сохранённых серверов NAS.

Декларированные ответы: `200` Successful Response.

### `POST /api/storage/nas/discover`

[discover_nas](../app.py#L322). Запускает обнаружение NAS через Bonjour на машине Core.

Декларированные ответы: `200` Successful Response.

### `GET /api/storage/nas/{server_id}/shares`

[nas_shares](../app.py#L329). Возвращает сохранённые либо обновлённые ресурсы выбранного NAS.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `server_id` | `path` | True | `{"type": "string", "title": "Server Id"}` |
| `refresh` | `query` | False | `{"type": "boolean", "default": false, "title": "Refresh"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/nas/{server_id}/remember`

[remember_nas_share](../app.py#L339). Сохраняет выбранный SMB-ресурс без подключения.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `server_id` | `path` | True | `{"type": "string", "title": "Server Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/NetworkShareRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/volumes/{volume_id}/connect`

[connect_network_volume](../app.py#L351). Открывает подключение сетевого тома в Finder на машине Core.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"type": "string", "title": "Volume Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/volumes/{volume_id}/directory`

[storage_directory](../app.py#L363). Возвращает список выбранной папки тома с признаками снимка и ошибок.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"type": "string", "title": "Volume Id"}` |
| `path` | `query` | False | `{"type": "string", "default": "", "title": "Path"}` |
| `refresh` | `query` | False | `{"type": "boolean", "default": true, "title": "Refresh"}` |
| `discover` | `query` | False | `{"type": "boolean", "default": true, "title": "Discover"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/volumes/{volume_id}/preview`

[storage_preview](../app.py#L375). Возвращает JPEG-превью обычного файла выбранного тома.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"type": "string", "title": "Volume Id"}` |
| `path` | `query` | True | `{"type": "string", "title": "Path"}` |
| `large` | `query` | False | `{"type": "boolean", "default": false, "title": "Large"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/volumes/{volume_id}/directory-sizes`

[storage_directory_sizes](../app.py#L406). Возвращает размеры папок и при разрешении ставит их в очередь подсчёта.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"type": "string", "title": "Volume Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/DirectorySizesRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/volumes/{volume_id}/open-in-finder`

[open_storage_path_in_finder](../app.py#L419). Передаёт Finder проверенный путь выбранного тома.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"type": "string", "title": "Volume Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/StoragePathRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/volumes/{volume_id}/metadata`

[storage_metadata](../app.py#L431). Сохраняет пользовательские отметки расположения в каталоге.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"type": "string", "title": "Volume Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/StorageMetadataRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/volumes/{volume_id}/folder-tags`

[storage_folder_tags](../app.py#L443). Сохраняет смысловые метки выбранной папки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `volume_id` | `path` | True | `{"type": "string", "title": "Volume Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/FolderTagsRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/copy-locations/{location_id}/source`

[storage_copy_source](../app.py#L534). Обрабатывает изменение источника копирования обычной папки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"type": "string", "title": "Location Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopySourceRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/copy-groups`

[storage_copy_groups](../app.py#L563). Возвращает наборы папок с типами, метками и состоянием наблюдателей.

Декларированные ответы: `200` Successful Response.

### `POST /api/storage/copy-groups`

[storage_main_folder](../app.py#L579). Регистрирует выбранную папку как основную область набора.

Тело JSON: `{"$ref": "#/components/schemas/ComparisonScope"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/folder-markers`

[storage_folder_markers](../app.py#L572). Возвращает состояние очереди служебных описаний папок.

Декларированные ответы: `200` Successful Response.

### `PATCH /api/storage/copy-groups/{group_id}`

[storage_copy_group_settings](../app.py#L586). Обновляет настройки набора и пробуждает отслеживание изменений.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"type": "string", "title": "Group Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyGroupSettingsRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `DELETE /api/storage/copy-groups/{group_id}`

[storage_remove_copy_group](../app.py#L663). Удаляет набор папок из каталога без удаления пользовательских файлов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"type": "string", "title": "Group Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-groups/{group_id}/acknowledge`

[storage_acknowledge_folder_changes](../app.py#L595). Подтверждает конкретную версию уведомления об изменении папки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"type": "string", "title": "Group Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyGroupAcknowledgeRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/copy-groups/{group_id}/connection`

[storage_copy_group_connection](../app.py#L602). Меняет подключение всего набора папок.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"type": "string", "title": "Group Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyConnectionRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/copy-locations/{location_id}/connection`

[storage_copy_location_connection](../app.py#L611). Меняет подключение одной обычной копии.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"type": "string", "title": "Location Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyConnectionRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-groups/{group_id}/copies`

[storage_copy_location](../app.py#L618). Добавляет папку копии к существующему набору.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"type": "string", "title": "Group Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyLocationRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-locations/{location_id}/release-number`

[storage_release_copy_number](../app.py#L634). Архивирует прежнюю привязку и освобождает её номер.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"type": "string", "title": "Location Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyNumberReleaseRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/copy-locations/{location_id}`

[storage_copy_kind](../app.py#L641). Меняет тип зарегистрированной копии.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"type": "string", "title": "Location Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyKindRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `DELETE /api/storage/copy-locations/{location_id}`

[storage_remove_copy](../app.py#L655). Удаляет связь копии из каталога без удаления пользовательских файлов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `location_id` | `path` | True | `{"type": "string", "title": "Location Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-groups/{group_id}/renumber`

[storage_renumber_copies](../app.py#L648). Применяет подтверждённую нумерацию по снимку текущих связей.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `group_id` | `path` | True | `{"type": "string", "title": "Group Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopyRenumberRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/paired-comparisons`

[paired_jobs](../app.py#L719). Возвращает историю парных сверок и допустимые решения для лишних элементов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `copy_id` | `query` | False | `{"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Copy Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/paired-comparisons`

[start_paired_comparison](../app.py#L726). Создаёт и запускает сверку зарегистрированной пары папок.

Тело JSON: `{"$ref": "#/components/schemas/PairedComparisonRequest"}`; обязательное: True.

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `GET /api/storage/paired-comparisons/{job_id}`

[paired_job](../app.py#L734). Возвращает состояние одной парной сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/paired-comparisons/{job_id}/rows`

[paired_rows](../app.py#L741). Возвращает страницу выровненных строк парной сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |
| `offset` | `query` | False | `{"type": "integer", "minimum": 0, "default": 0, "title": "Offset"}` |
| `limit` | `query` | False | `{"type": "integer", "maximum": 5000, "minimum": 1, "default": 1000, "title": "Limit"}` |
| `differences_only` | `query` | False | `{"type": "boolean", "default": false, "title": "Differences Only"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/paired-comparisons/{job_id}/pause`

[pause_paired_job](../app.py#L749). Запрашивает паузу парной сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/paired-comparisons/{job_id}/resume`

[resume_paired_job](../app.py#L756). Продолжает парную сверку после проверки конфликтующих операций.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/storage/paired-comparisons/{job_id}/decision`

[paired_decision](../app.py#L763). Сохраняет плановое решение для элемента только в копии.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/PairedDecisionRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons`

[comparison_jobs](../app.py#L770). Возвращает историю общей сверки имён и старых отчётов.

Декларированные ответы: `200` Successful Response.

### `POST /api/storage/comparisons`

[start_comparison](../app.py#L813). Создаёт общую сверку имён исходной области и выбранных целей.

Тело JSON: `{"$ref": "#/components/schemas/ComparisonRequest"}`; обязательное: True.

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `POST /api/storage/paired-comparisons/{job_id}/copy-plan`

[missing_copy_plan](../app.py#L777). Создаёт сохранённый план копирования по завершённому файловому отчёту.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `GET /api/storage/copy-operations/{operation_id}`

[missing_copy_job](../app.py#L784). Возвращает состояние операции копирования отсутствующих элементов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `operation_id` | `path` | True | `{"type": "string", "title": "Operation Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/copy-operations/{operation_id}/items`

[missing_copy_items](../app.py#L791). Возвращает страницу элементов сохранённого плана копирования.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `operation_id` | `path` | True | `{"type": "string", "title": "Operation Id"}` |
| `offset` | `query` | False | `{"type": "integer", "minimum": 0, "default": 0, "title": "Offset"}` |
| `limit` | `query` | False | `{"type": "integer", "maximum": 1000, "minimum": 1, "default": 200, "title": "Limit"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-operations/{operation_id}/start`

[start_missing_copy](../app.py#L799). Запускает подтверждённую операцию создания отсутствующих копий.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `operation_id` | `path` | True | `{"type": "string", "title": "Operation Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/copy-operations/{operation_id}/stop`

[stop_missing_copy](../app.py#L806). Запрашивает остановку операции копирования.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `operation_id` | `path` | True | `{"type": "string", "title": "Operation Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}`

[comparison_job](../app.py#L821). Возвращает состояние и области общей сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/comparisons/{job_id}/pause`

[pause_comparison](../app.py#L828). Запрашивает паузу общей сверки имён.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/storage/comparisons/{job_id}/resume`

[resume_comparison](../app.py#L835). Продолжает сверку имён либо создаёт новую вместо старой проверки содержимого.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}/tree`

[comparison_tree](../app.py#L842). Возвращает страницу исходного дерева общей сверки с фильтром статуса.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |
| `path` | `query` | False | `{"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Path"}` |
| `status` | `query` | False | `{"type": "string", "default": "", "title": "Status"}` |
| `offset` | `query` | False | `{"type": "integer", "minimum": 0, "default": 0, "title": "Offset"}` |
| `limit` | `query` | False | `{"type": "integer", "maximum": 500, "minimum": 1, "default": 200, "title": "Limit"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}/target-tree`

[comparison_target_tree](../app.py#L850). Возвращает страницу сохранённого дерева выбранной цели общей сверки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |
| `scan_id` | `query` | True | `{"type": "integer", "minimum": 1, "title": "Scan Id"}` |
| `path` | `query` | False | `{"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Path"}` |
| `offset` | `query` | False | `{"type": "integer", "minimum": 0, "default": 0, "title": "Offset"}` |
| `limit` | `query` | False | `{"type": "integer", "maximum": 500, "minimum": 1, "default": 200, "title": "Limit"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}/detail`

[comparison_detail](../app.py#L858). Возвращает найденные совпадения и подробности элемента отчёта.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |
| `path` | `query` | False | `{"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Path"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/storage/comparisons/{job_id}/events`

[comparison_events](../app.py#L865). Возвращает события общей сверки с обратной пагинацией.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `job_id` | `path` | True | `{"type": "string", "title": "Job Id"}` |
| `before` | `query` | False | `{"anyOf": [{"type": "integer", "minimum": 1}, {"type": "null"}], "title": "Before"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/sources`

[list_sources](../app.py#L872). Возвращает сохранённые источники медиаиндекса.

Декларированные ответы: `200` Successful Response.

### `POST /api/sources`

[create_source](../app.py#L879). Регистрирует обычный источник, устанавливает наблюдение и запускает сканирование.

Тело JSON: `{"$ref": "#/components/schemas/SourceRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/sources/choose`

[choose_sources](../app.py#L897). Регистрирует выбранные системным диалогом папки и запускает их сканирование.

Тело JSON: `{"$ref": "#/components/schemas/FolderChoiceRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/sources/{source_id}`

[update_source](../app.py#L922). Обновляет роль, название и комментарий обычного источника.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/SourceMetadataRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `DELETE /api/sources/{source_id}`

[delete_source](../app.py#L940). Снимает наблюдение и удаляет источник из медиаиндекса.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/sources/{source_id}/scan`

[scan_one_source](../app.py#L957). Проверяет источник и выполняет его ручное сканирование.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/scan`

[scan_all_sources](../app.py#L971). Запускает сканирование зарегистрированных источников.

Декларированные ответы: `200` Successful Response.

### `POST /api/photos/authorize`

[authorize_system_photos](../app.py#L992). Запрашивает разрешение Photos и возвращает состояние доступа.

Декларированные ответы: `200` Successful Response.

### `PATCH /api/photos/libraries/{source_id}/sync-schedule`

[set_photos_sync_schedule](../app.py#L1053). Сохраняет часы синхронизации выбранной медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/PhotosSyncScheduleRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/photos/libraries`

[list_photo_libraries](../app.py#L1062). Возвращает медиатеки, состояние подключения, превью и привязанные копии.

Декларированные ответы: `200` Successful Response.

### `POST /api/photos/libraries`

[register_photo_library](../app.py#L1098). Регистрирует текущую медиатеку и ставит её первый скан в очередь.

Тело JSON: `{"$ref": "#/components/schemas/LibraryNameRequest"}`; обязательное: True.

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/connect`

[connect_photo_library](../app.py#L1069). Повторяет сопоставление системной медиатеки и пробуждает превью.

Декларированные ответы: `200` Successful Response.

### `GET /api/photos/libraries/{source_id}/browse`

[browse_photo_library](../app.py#L1078). Возвращает виртуальную папку Photos и повышает приоритет её превью.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `path` | `query` | False | `{"type": "string", "default": "", "title": "Path"}` |
| `offset` | `query` | False | `{"type": "integer", "minimum": 0, "default": 0, "title": "Offset"}` |
| `limit` | `query` | False | `{"type": "integer", "maximum": 1000, "minimum": 1, "default": 150, "title": "Limit"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/photos/libraries/{source_id}/preview-status`

[photo_preview_status](../app.py#L1089). Возвращает готовые превью выбранных объектов медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `ids` | `query` | False | `{"type": "array", "items": {"type": "integer"}, "default": [], "title": "Ids"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/photos/libraries/{source_id}`

[rename_photo_library](../app.py#L1107). Меняет название медиатеки и возвращает обновлённый список.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/LibraryNameRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/pause`

[pause_photo_library](../app.py#L1115). Включает ручную паузу выбранной медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/resume`

[resume_photo_library](../app.py#L1123). Снимает ручную паузу медиатеки и пробуждает очередь превью.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/copies`

[bind_photo_library_copy](../app.py#L1132). Привязывает выбранную папку как копию медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/LibraryCopyRequest"}`; обязательное: True.

Декларированные ответы: `201` Successful Response, `422` Validation Error.

### `DELETE /api/photos/libraries/{source_id}/copies/{link_id}`

[unbind_photo_library_copy](../app.py#L1139). Отключает привязку копии медиатеки и возвращает обновлённый список.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `link_id` | `path` | True | `{"type": "string", "title": "Link Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `PATCH /api/photos/libraries/{source_id}/copies/{link_id}/source`

[photo_copy_source](../app.py#L1147). Меняет источник привязанной копии Photos.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `link_id` | `path` | True | `{"type": "string", "title": "Link Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/CopySourceRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/copies/{link_id}/make-first`

[photo_copy_first](../app.py#L1155). Ставит выбранную копию Photos первой по номеру без изменения маршрутов.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `link_id` | `path` | True | `{"type": "string", "title": "Link Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/copies/{link_id}/originals/start`

[start_photo_originals](../app.py#L1163). Запускает или планирует сохранение оригиналов в цепочку копий Photos.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `link_id` | `path` | True | `{"type": "string", "title": "Link Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/photos/libraries/{source_id}/copies/{link_id}/originals/pause`

[pause_photo_originals](../app.py#L1170). Запрашивает паузу сохранения оригиналов выбранной медиатеки.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `link_id` | `path` | True | `{"type": "string", "title": "Link Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/photos/libraries/{source_id}/copies/{link_id}/originals`

[photo_originals_status](../app.py#L1177). Возвращает состояние оригиналов после проверки принадлежности копии медиатеке.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `link_id` | `path` | True | `{"type": "string", "title": "Link Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/photos/libraries/{source_id}/copies/{link_id}/originals/journal`

[photo_originals_journal](../app.py#L1185). Возвращает журнал оригиналов и пути незавершённых записей.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `link_id` | `path` | True | `{"type": "string", "title": "Link Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/catalog/summary`

[catalog_summary](../app.py#L1192). Возвращает суммарные показатели сохранённого медиаиндекса.

Декларированные ответы: `200` Successful Response.

### `GET /api/sources/{source_id}/tree`

[source_tree](../app.py#L1199). Возвращает дерево виртуальных папок зарегистрированного источника.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/sources/{source_id}/files`

[source_files](../app.py#L1208). Возвращает файлы папки источника и повышает приоритет их превью.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |
| `folder` | `query` | False | `{"type": "string", "default": "", "title": "Folder"}` |
| `limit` | `query` | False | `{"type": "integer", "maximum": 1000, "minimum": 1, "default": 300, "title": "Limit"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/thumbnails/status`

[thumbnail_status](../app.py#L1227). Возвращает очередь превью и диагностическое состояние её воркеров.

Декларированные ответы: `200` Successful Response.

### `POST /api/thumbnails/pause`

[pause_thumbnails](../app.py#L1234). Сохраняет общую ручную паузу фоновой очереди превью.

Декларированные ответы: `200` Successful Response.

### `POST /api/thumbnails/resume`

[resume_thumbnails](../app.py#L1242). Снимает общую паузу превью и пробуждает воркеры.

Декларированные ответы: `200` Successful Response.

### `POST /api/sources/{source_id}/open-in-finder`

[open_source_folder_in_finder](../app.py#L1251). Открывает проверенную папку обычного источника в Finder.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `source_id` | `path` | True | `{"type": "integer", "title": "Source Id"}` |

Тело JSON: `{"$ref": "#/components/schemas/FolderRequest"}`; обязательное: True.

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `GET /api/media/{media_id}/thumbnail`

[media_thumbnail](../app.py#L1280). Отдаёт только готовый JPEG из кэша медиаиндекса.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `media_id` | `path` | True | `{"type": "integer", "title": "Media Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

### `POST /api/media/{media_id}/open`

[open_media_in_default_app](../app.py#L1299). Открывает обычный файл системной командой или выделяет объект Photos.

| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |
| --- | --- | --- | --- |
| `media_id` | `path` | True | `{"type": "integer", "title": "Media Id"}` |

Декларированные ответы: `200` Successful Response, `422` Validation Error.

## Схемы Pydantic и валидации

Поля с отсутствующим `default` и входящие в `required` обязательны. `anyOf` с `null` допускает `None`, но само по себе не делает поле необязательным. `additionalProperties=false` запрещает лишние поля. Унаследованные поля уже раскрыты в схеме.

### `ComparisonRequest`

```json
{
  "properties": {
    "source": {
      "$ref": "#/components/schemas/ComparisonScope"
    },
    "targets": {
      "items": {
        "$ref": "#/components/schemas/ComparisonScope"
      },
      "type": "array",
      "maxItems": 16,
      "minItems": 1,
      "title": "Targets"
    },
    "reread": {
      "type": "boolean",
      "title": "Reread",
      "default": false
    },
    "reuse_index": {
      "type": "boolean",
      "title": "Reuse Index",
      "default": true
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "source",
    "targets"
  ],
  "title": "ComparisonRequest"
}
```

### `ComparisonScope`

```json
{
  "properties": {
    "volume_id": {
      "type": "string",
      "maxLength": 128,
      "minLength": 1,
      "title": "Volume Id"
    },
    "path": {
      "type": "string",
      "maxLength": 4096,
      "title": "Path",
      "default": ""
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "volume_id"
  ],
  "title": "ComparisonScope"
}
```

### `CopyConnectionRequest`

```json
{
  "properties": {
    "connected": {
      "type": "boolean",
      "title": "Connected"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "connected"
  ],
  "title": "CopyConnectionRequest"
}
```

### `CopyGroupAcknowledgeRequest`

```json
{
  "properties": {
    "changed_at": {
      "type": "string",
      "maxLength": 64,
      "minLength": 1,
      "title": "Changed At"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "changed_at"
  ],
  "title": "CopyGroupAcknowledgeRequest"
}
```

### `CopyGroupSettingsRequest`

```json
{
  "properties": {
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
    },
    "label": {
      "anyOf": [
        {
          "type": "string",
          "enum": [
            "",
            "temporary",
            "inbox",
            "archive"
          ]
        },
        {
          "type": "null"
        }
      ],
      "title": "Label"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "title": "CopyGroupSettingsRequest"
}
```

### `CopyKindRequest`

```json
{
  "properties": {
    "kind": {
      "type": "string",
      "enum": [
        "copy",
        "cold",
        "cloud"
      ],
      "title": "Kind"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "kind"
  ],
  "title": "CopyKindRequest"
}
```

### `CopyLocationRequest`

```json
{
  "properties": {
    "volume_id": {
      "type": "string",
      "maxLength": 128,
      "minLength": 1,
      "title": "Volume Id"
    },
    "path": {
      "type": "string",
      "maxLength": 4096,
      "title": "Path",
      "default": ""
    },
    "kind": {
      "type": "string",
      "enum": [
        "copy",
        "cold",
        "cloud"
      ],
      "title": "Kind",
      "default": "copy"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "volume_id"
  ],
  "title": "CopyLocationRequest"
}
```

### `CopyNumberReleaseRequest`

```json
{
  "properties": {
    "kind": {
      "type": "string",
      "enum": [
        "copy",
        "cold",
        "cloud"
      ],
      "title": "Kind"
    },
    "number": {
      "type": "integer",
      "exclusiveMinimum": 0.0,
      "title": "Number"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "kind",
    "number"
  ],
  "title": "CopyNumberReleaseRequest"
}
```

### `CopyNumberSnapshot`

```json
{
  "properties": {
    "kind": {
      "type": "string",
      "enum": [
        "copy",
        "cold",
        "cloud"
      ],
      "title": "Kind"
    },
    "id": {
      "type": "string",
      "maxLength": 128,
      "minLength": 1,
      "title": "Id"
    },
    "number": {
      "type": "integer",
      "exclusiveMinimum": 0.0,
      "title": "Number"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "kind",
    "id",
    "number"
  ],
  "title": "CopyNumberSnapshot"
}
```

### `CopyRenumberRequest`

```json
{
  "properties": {
    "copies": {
      "items": {
        "$ref": "#/components/schemas/CopyNumberSnapshot"
      },
      "type": "array",
      "title": "Copies"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "copies"
  ],
  "title": "CopyRenumberRequest"
}
```

### `CopySourceRequest`

```json
{
  "properties": {
    "source_id": {
      "anyOf": [
        {
          "type": "string",
          "maxLength": 128,
          "minLength": 1
        },
        {
          "type": "null"
        }
      ],
      "title": "Source Id"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "title": "CopySourceRequest"
}
```

### `DirectorySizesRequest`

```json
{
  "properties": {
    "paths": {
      "items": {
        "type": "string"
      },
      "type": "array",
      "maxItems": 500,
      "minItems": 1,
      "title": "Paths"
    },
    "start": {
      "type": "boolean",
      "title": "Start",
      "default": true
    },
    "refresh": {
      "type": "boolean",
      "title": "Refresh",
      "default": false
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "paths"
  ],
  "title": "DirectorySizesRequest"
}
```

### `FolderChoiceRequest`

```json
{
  "properties": {
    "role": {
      "type": "string",
      "enum": [
        "source",
        "storage"
      ],
      "title": "Role",
      "default": "source"
    },
    "label": {
      "type": "string",
      "title": "Label",
      "default": ""
    },
    "comment": {
      "type": "string",
      "title": "Comment",
      "default": ""
    }
  },
  "type": "object",
  "title": "FolderChoiceRequest"
}
```

### `FolderRequest`

```json
{
  "properties": {
    "folder": {
      "type": "string",
      "title": "Folder",
      "default": ""
    }
  },
  "type": "object",
  "title": "FolderRequest"
}
```

### `FolderTagsRequest`

```json
{
  "properties": {
    "path": {
      "type": "string",
      "maxLength": 4096,
      "title": "Path",
      "default": ""
    },
    "tags": {
      "items": {
        "type": "string",
        "enum": [
          "old_copy",
          "sort",
          "check"
        ]
      },
      "type": "array",
      "maxItems": 3,
      "title": "Tags"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "tags"
  ],
  "title": "FolderTagsRequest"
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
      "type": "array",
      "title": "Detail"
    }
  },
  "type": "object",
  "title": "HTTPValidationError"
}
```

### `LibraryCopyRequest`

```json
{
  "properties": {
    "volume_id": {
      "type": "string",
      "maxLength": 128,
      "minLength": 1,
      "title": "Volume Id"
    },
    "path": {
      "type": "string",
      "maxLength": 4096,
      "minLength": 1,
      "title": "Path"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "volume_id",
    "path"
  ],
  "title": "LibraryCopyRequest"
}
```

### `LibraryNameRequest`

```json
{
  "properties": {
    "label": {
      "type": "string",
      "maxLength": 120,
      "minLength": 1,
      "title": "Label"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "label"
  ],
  "title": "LibraryNameRequest"
}
```

### `NetworkShareRequest`

```json
{
  "properties": {
    "share": {
      "type": "string",
      "maxLength": 255,
      "minLength": 1,
      "title": "Share"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "share"
  ],
  "title": "NetworkShareRequest"
}
```

### `PairedComparisonRequest`

```json
{
  "properties": {
    "copy_id": {
      "type": "string",
      "maxLength": 128,
      "minLength": 1,
      "title": "Copy Id"
    },
    "mode": {
      "type": "string",
      "enum": [
        "folders",
        "files"
      ],
      "title": "Mode",
      "default": "folders"
    },
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
    "method": {
      "type": "string",
      "enum": [
        "size",
        "sha256"
      ],
      "title": "Method",
      "default": "size"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "copy_id"
  ],
  "title": "PairedComparisonRequest"
}
```

### `PairedDecisionRequest`

```json
{
  "properties": {
    "path": {
      "type": "string",
      "maxLength": 4096,
      "title": "Path"
    },
    "action": {
      "anyOf": [
        {
          "type": "string",
          "enum": [
            "keep",
            "add_main",
            "move",
            "remove"
          ]
        },
        {
          "type": "null"
        }
      ],
      "title": "Action"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "path",
    "action"
  ],
  "title": "PairedDecisionRequest"
}
```

### `PhotosSyncScheduleRequest`

```json
{
  "properties": {
    "night_only": {
      "type": "boolean",
      "title": "Night Only"
    },
    "start_hour": {
      "type": "integer",
      "maximum": 23.0,
      "minimum": 0.0,
      "title": "Start Hour",
      "default": 0
    },
    "end_hour": {
      "type": "integer",
      "maximum": 23.0,
      "minimum": 0.0,
      "title": "End Hour",
      "default": 7
    },
    "timezone": {
      "type": "string",
      "const": "Europe/Moscow",
      "title": "Timezone",
      "default": "Europe/Moscow"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "night_only"
  ],
  "title": "PhotosSyncScheduleRequest"
}
```

### `SourceMetadataRequest`

```json
{
  "properties": {
    "role": {
      "type": "string",
      "enum": [
        "source",
        "storage"
      ],
      "title": "Role"
    },
    "label": {
      "type": "string",
      "title": "Label",
      "default": ""
    },
    "comment": {
      "type": "string",
      "title": "Comment",
      "default": ""
    }
  },
  "type": "object",
  "required": [
    "role"
  ],
  "title": "SourceMetadataRequest"
}
```

### `SourceRequest`

```json
{
  "properties": {
    "path": {
      "type": "string",
      "title": "Path"
    },
    "role": {
      "type": "string",
      "enum": [
        "source",
        "storage"
      ],
      "title": "Role",
      "default": "source"
    },
    "label": {
      "type": "string",
      "title": "Label",
      "default": ""
    },
    "comment": {
      "type": "string",
      "title": "Comment",
      "default": ""
    }
  },
  "type": "object",
  "required": [
    "path"
  ],
  "title": "SourceRequest"
}
```

### `StorageMetadataRequest`

```json
{
  "properties": {
    "path": {
      "type": "string",
      "title": "Path",
      "default": ""
    },
    "purpose": {
      "anyOf": [
        {
          "type": "string",
          "enum": [
            "",
            "media",
            "documents",
            "projects",
            "mixed"
          ]
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
          "type": "string",
          "enum": [
            "",
            "primary",
            "copy",
            "archive",
            "temporary"
          ]
        },
        {
          "type": "null"
        }
      ],
      "title": "Role"
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
    "comment": {
      "type": "string",
      "maxLength": 4000,
      "title": "Comment",
      "default": ""
    }
  },
  "additionalProperties": false,
  "type": "object",
  "title": "StorageMetadataRequest"
}
```

### `StoragePathRequest`

```json
{
  "properties": {
    "path": {
      "type": "string",
      "maxLength": 4096,
      "title": "Path",
      "default": ""
    }
  },
  "additionalProperties": false,
  "type": "object",
  "title": "StoragePathRequest"
}
```

### `ValidationError`

```json
{
  "properties": {
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
      "type": "array",
      "title": "Location"
    },
    "msg": {
      "type": "string",
      "title": "Message"
    },
    "type": {
      "type": "string",
      "title": "Error Type"
    },
    "input": {
      "title": "Input"
    },
    "ctx": {
      "type": "object",
      "title": "Context"
    }
  },
  "type": "object",
  "required": [
    "loc",
    "msg",
    "type"
  ],
  "title": "ValidationError"
}
```

### `VolumeNameRequest`

```json
{
  "properties": {
    "name": {
      "type": "string",
      "maxLength": 120,
      "minLength": 1,
      "title": "Name"
    }
  },
  "additionalProperties": false,
  "type": "object",
  "required": [
    "name"
  ],
  "title": "VolumeNameRequest"
}
```
