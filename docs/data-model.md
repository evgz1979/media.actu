# Схема данных

Снято 2026-11-03 с двух пустых временных баз после создания служб Core. `lifespan` FastAPI не запускался: наблюдатели, сканирование и PhotoKit не работали. Это итоговая схема текущего кода после его миграций, а не выгрузка пользовательских данных.

В базе `catalog.sqlite3` 17 таблиц, в `storage.sqlite3` — 32. Базы независимы: `volume_id` в копиях Photos ссылается на каталог хранилищ логически, внешнего ключа между файлами SQLite нет. Отдельные службы также держат очереди и блокировки в памяти; наличие результата в таблице не означает, что соответствующий поток сейчас работает.

Связанные объяснения: [архитектура](architecture.md), [транзакции и ресурсы](development/data-and-files.md), [совместимость старых полей](legacy.md).

## Владение и транзакции

`Catalog.connect` включает `foreign_keys=ON`, `journal_mode=WAL` и `sqlite3.Row`, тайм-аут 30 секунд. `StorageCatalog.connect` — контекстный менеджер: включает внешние ключи, фиксирует успешный блок либо откатывает исключение и всегда закрывает соединение. WAL для storage этим методом явно не включается. Записи медиаиндекса используют `Catalog._write_lock`, многие изменения связей — `StorageCatalog._lock` и `BEGIN IMMEDIATE`; это локальные блокировки процесса, а не распределённая транзакция двух баз.

## Оглавление таблиц

### `catalog.sqlite3`

- [media_files](#table-media-files)
- [metadata](#table-metadata)
- [photos_copy_files](#table-photos-copy-files)
- [photos_copy_links](#table-photos-copy-links)
- [photos_copy_sources](#table-photos-copy-sources)
- [photos_libraries](#table-photos-libraries)
- [photos_original_inventory](#table-photos-original-inventory)
- [photos_original_jobs](#table-photos-original-jobs)
- [photos_original_log](#table-photos-original-log)
- [photos_original_resources](#table-photos-original-resources)
- [photos_original_staging](#table-photos-original-staging)
- [photos_original_versions](#table-photos-original-versions)
- [photos_sync_requests](#table-photos-sync-requests)
- [photos_sync_settings](#table-photos-sync-settings)
- [sources](#table-sources)
- [thumbnail_jobs](#table-thumbnail-jobs)
- [thumbnail_waits](#table-thumbnail-waits)

### `storage.sqlite3`

- [annotations](#table-annotations)
- [comparison_entries](#table-comparison-entries)
- [comparison_events](#table-comparison-events)
- [comparison_hashes](#table-comparison-hashes)
- [comparison_jobs](#table-comparison-jobs)
- [comparison_results](#table-comparison-results)
- [comparison_scans](#table-comparison-scans)
- [copy_group_settings](#table-copy-group-settings)
- [copy_groups](#table-copy-groups)
- [copy_locations](#table-copy-locations)
- [copy_operation_items](#table-copy-operation-items)
- [copy_operations](#table-copy-operations)
- [copy_sources](#table-copy-sources)
- [directories](#table-directories)
- [directory_sizes](#table-directory-sizes)
- [directory_tags](#table-directory-tags)
- [disconnected_copy_groups](#table-disconnected-copy-groups)
- [disconnected_copy_locations](#table-disconnected-copy-locations)
- [folder_marker_jobs](#table-folder-marker-jobs)
- [network_servers](#table-network-servers)
- [network_shares](#table-network-shares)
- [network_volume_links](#table-network-volume-links)
- [paired_decisions](#table-paired-decisions)
- [paired_entries](#table-paired-entries)
- [paired_jobs](#table-paired-jobs)
- [paired_rows](#table-paired-rows)
- [released_copy_locations](#table-released-copy-locations)
- [volume_aliases](#table-volume-aliases)
- [volume_capacity](#table-volume-capacity)
- [volume_details](#table-volume-details)
- [volume_origins](#table-volume-origins)
- [volumes](#table-volumes)

<a id="table-media-files"></a>

## `media_files`

База: `catalog.sqlite3`. Определение: [media_manager/catalog.py:28](../media_manager/catalog.py#L28).

Одна строка на объект источника. В обычной папке relative_path — путь файла, у Photos — ID объекта; parent_path задаёт виртуальный год/месяц. seen_token позволяет удалять исчезнувшие записи после полного успешного скана. В Photos modified_at сейчас формируется из created_at скана (либо времени скана при отсутствии даты), а не из assetVersion манифеста оригиналов; это разные версии для разных сценариев.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | False | не задано | 1 |
| `source_id` | `INTEGER` | True | не задано | 0 |
| `relative_path` | `TEXT` | True | не задано | 0 |
| `parent_path` | `TEXT` | True | не задано | 0 |
| `name` | `TEXT` | True | не задано | 0 |
| `kind` | `TEXT` | True | не задано | 0 |
| `size` | `INTEGER` | True | не задано | 0 |
| `modified_at` | `TEXT` | True | не задано | 0 |
| `seen_token` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE media_files (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    relative_path TEXT NOT NULL,
    parent_path TEXT NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('photo', 'video')),
    size INTEGER NOT NULL,
    modified_at TEXT NOT NULL,
    seen_token TEXT NOT NULL,
    UNIQUE(source_id, relative_path)
);
```

Внешние ключи:

- `source_id` → `sources.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `media_files_source_parent` (unique=False, partial=False), `sqlite_autoindex_media_files_1` (unique=True, partial=False).

<a id="table-metadata"></a>

## `metadata`

База: `catalog.sqlite3`. Определение: [media_manager/catalog.py:44](../media_manager/catalog.py#L44).

Служебные ключи медиаиндекса: catalog_revision и общая пауза превью. Это не EXIF и не пользовательские теги файлов.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `key` | `TEXT` | False | не задано | 1 |
| `value` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

Индексы: `sqlite_autoindex_metadata_1` (unique=True, partial=False).

<a id="table-photos-copy-files"></a>

## `photos_copy_files`

База: `catalog.sqlite3`. Определение: [media_manager/catalog.py:92](../media_manager/catalog.py#L92).

Квитанции готовых ресурсов: link, asset ID, resource ID, путь, размер и время проверки. Поле sha256 оставлено для совместимости и сейчас заполняется пустой строкой.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `link_id` | `TEXT` | True | не задано | 1 |
| `asset_identifier` | `TEXT` | True | не задано | 2 |
| `resource_id` | `TEXT` | True | не задано | 3 |
| `path` | `TEXT` | True | не задано | 0 |
| `size` | `INTEGER` | False | не задано | 0 |
| `sha256` | `TEXT` | False | не задано | 0 |
| `verified_at` | `TEXT` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_copy_files (
    link_id TEXT NOT NULL REFERENCES photos_copy_links(id) ON DELETE CASCADE,
    asset_identifier TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    path TEXT NOT NULL,
    size INTEGER,
    sha256 TEXT,
    verified_at TEXT,
    PRIMARY KEY(link_id,asset_identifier,resource_id)
);
```

Внешние ключи:

- `link_id` → `photos_copy_links.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_photos_copy_files_1` (unique=True, partial=False).

<a id="table-photos-copy-links"></a>

## `photos_copy_links`

База: `catalog.sqlite3`. Определение: [media_manager/catalog.py:81](../media_manager/catalog.py#L81).

Привязанные папки назначения Photos. Связь отключается через connected, чтобы сохранить квитанции и историю; номер уникален внутри медиатеки.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `source_id` | `INTEGER` | True | не задано | 0 |
| `volume_id` | `TEXT` | True | не задано | 0 |
| `path` | `TEXT` | True | не задано | 0 |
| `number` | `INTEGER` | True | не задано | 0 |
| `created_at` | `TEXT` | True | не задано | 0 |
| `connected` | `INTEGER` | True | `1` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_copy_links (
    id TEXT PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES photos_libraries(source_id),
    volume_id TEXT NOT NULL,
    path TEXT NOT NULL,
    number INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    connected INTEGER NOT NULL DEFAULT 1,
    UNIQUE(volume_id,path),
    UNIQUE(source_id,number)
);
```

Внешние ключи:

- `source_id` → `photos_libraries.source_id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_photos_copy_links_3` (unique=True, partial=False), `sqlite_autoindex_photos_copy_links_2` (unique=True, partial=False), `sqlite_autoindex_photos_copy_links_1` (unique=True, partial=False).

<a id="table-photos-copy-sources"></a>

## `photos_copy_sources`

База: `catalog.sqlite3`. Определение: [media_manager/photo_libraries.py:60](../media_manager/photo_libraries.py#L60).

Явное ребро от назначения к копии-источнику. Отсутствие строки означает прямой источник Photos. При изменении проверяются принадлежность медиатеке и отсутствие цикла.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `link_id` | `TEXT` | False | не задано | 1 |
| `source_link_id` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_copy_sources (
                link_id TEXT PRIMARY KEY REFERENCES photos_copy_links(id) ON DELETE CASCADE,
                source_link_id TEXT NOT NULL);
```

Внешние ключи:

- `link_id` → `photos_copy_links.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_photos_copy_sources_1` (unique=True, partial=False).

<a id="table-photos-libraries"></a>

## `photos_libraries`

База: `catalog.sqlite3`. Определение: [media_manager/catalog.py:65](../media_manager/catalog.py#L65).

Идентичность и доступность медиатеки, якорные ID в JSON, ручная пауза. Частичный уникальный индекс допускает только одну активную запись.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `source_id` | `INTEGER` | False | не задано | 1 |
| `library_id` | `TEXT` | True | не задано | 0 |
| `anchors` | `TEXT` | True | `'[]'` | 0 |
| `active` | `INTEGER` | True | `0` | 0 |
| `paused` | `INTEGER` | True | `0` | 0 |
| `state` | `TEXT` | True | `'unknown'` | 0 |
| `error` | `TEXT` | False | не задано | 0 |
| `checked_at` | `TEXT` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_libraries (
    source_id INTEGER PRIMARY KEY REFERENCES sources(id) ON DELETE CASCADE,
    library_id TEXT NOT NULL UNIQUE,
    anchors TEXT NOT NULL DEFAULT '[]',
    active INTEGER NOT NULL DEFAULT 0,
    paused INTEGER NOT NULL DEFAULT 0,
    state TEXT NOT NULL DEFAULT 'unknown',
    error TEXT,
    checked_at TEXT
);
```

Внешние ключи:

- `source_id` → `sources.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `photos_one_active` (unique=True, partial=True), `sqlite_autoindex_photos_libraries_1` (unique=True, partial=False).

<a id="table-photos-original-inventory"></a>

## `photos_original_inventory`

База: `catalog.sqlite3`. Определение: [media_manager/photos_originals.py:88](../media_manager/photos_originals.py#L88).

Индекс файлов папки назначения по пути, stat-fingerprint и поколению обхода. Поле sha256 историческое; текущий обход читает метаданные.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `link_id` | `TEXT` | True | не задано | 1 |
| `path` | `TEXT` | True | не задано | 2 |
| `fingerprint` | `TEXT` | True | не задано | 0 |
| `size` | `INTEGER` | True | не задано | 0 |
| `sha256` | `TEXT` | True | не задано | 0 |
| `seen` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_original_inventory (
                    link_id TEXT NOT NULL, path TEXT NOT NULL, fingerprint TEXT NOT NULL,
                    size INTEGER NOT NULL, sha256 TEXT NOT NULL, seen TEXT NOT NULL,
                    PRIMARY KEY(link_id,path));
```

Индексы: `sqlite_autoindex_photos_original_inventory_1` (unique=True, partial=False).

<a id="table-photos-original-jobs"></a>

## `photos_original_jobs`

База: `catalog.sqlite3`. Определение: [media_manager/photos_originals.py:76](../media_manager/photos_originals.py#L76).

Состояние задания оригиналов и JSON прогресса, включая идентичность корня, счётчики, текущий ресурс и буфер. Для продолжения используется последняя запись копии.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `link_id` | `TEXT` | True | не задано | 0 |
| `state` | `TEXT` | True | не задано | 0 |
| `updated_at` | `TEXT` | True | не задано | 0 |
| `data` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_original_jobs (
                    id TEXT PRIMARY KEY, link_id TEXT NOT NULL REFERENCES photos_copy_links(id),
                    state TEXT NOT NULL, updated_at TEXT NOT NULL, data TEXT NOT NULL);
```

Внешние ключи:

- `link_id` → `photos_copy_links.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.

Индексы: `photos_original_jobs_link` (unique=False, partial=False), `sqlite_autoindex_photos_original_jobs_1` (unique=True, partial=False).

<a id="table-photos-original-log"></a>

## `photos_original_log`

База: `catalog.sqlite3`. Определение: [media_manager/photos_originals.py:95](../media_manager/photos_originals.py#L95).

События сохранения оригиналов, ошибки и причины ожидания. API показывает последние 200 записей текущего задания и отдельно незавершённые пути.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | False | не задано | 1 |
| `job_id` | `TEXT` | True | не задано | 0 |
| `created_at` | `TEXT` | True | не задано | 0 |
| `level` | `TEXT` | True | не задано | 0 |
| `path` | `TEXT` | True | не задано | 0 |
| `message` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_original_log (
                    id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, created_at TEXT NOT NULL,
                    level TEXT NOT NULL, path TEXT NOT NULL, message TEXT NOT NULL);
```

Индексы: нет.

<a id="table-photos-original-resources"></a>

## `photos_original_resources`

База: `catalog.sqlite3`. Определение: [media_manager/photos_originals.py:80](../media_manager/photos_originals.py#L80).

Рабочий манифест конкретного задания: объект, ресурс, JSON версии и параметров, состояние pending/saved/reused/error и поколение seen.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `job_id` | `TEXT` | True | не задано | 1 |
| `asset` | `TEXT` | True | не задано | 2 |
| `resource` | `TEXT` | True | не задано | 3 |
| `data` | `TEXT` | True | не задано | 0 |
| `state` | `TEXT` | True | `'pending'` | 0 |
| `seen` | `TEXT` | True | `''` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_original_resources (
                    job_id TEXT NOT NULL REFERENCES photos_original_jobs(id), asset TEXT NOT NULL,
                    resource TEXT NOT NULL, data TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending', seen TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY(job_id,asset,resource));
```

Внешние ключи:

- `job_id` → `photos_original_jobs.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_photos_original_resources_1` (unique=True, partial=False).

<a id="table-photos-original-staging"></a>

## `photos_original_staging`

База: `catalog.sqlite3`. Определение: [media_manager/photos_originals.py:92](../media_manager/photos_originals.py#L92).

Намерения записи и идентичность созданных файлов. JSON final=true означает конечный путь, который нельзя удалять или повторно принимать после незавершённой записи.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `job_id` | `TEXT` | True | не задано | 1 |
| `path` | `TEXT` | True | не задано | 2 |
| `data` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_original_staging (
                    job_id TEXT NOT NULL, path TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(job_id,path));
```

Индексы: `sqlite_autoindex_photos_original_staging_1` (unique=True, partial=False).

<a id="table-photos-original-versions"></a>

## `photos_original_versions`

База: `catalog.sqlite3`. Определение: [media_manager/photos_originals.py:84](../media_manager/photos_originals.py#L84).

Ожидаемая версия ресурса Photos и stat-fingerprint готового файла по link/asset/resource. Используется совместно с квитанцией без повторного хеширования содержимого.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `link_id` | `TEXT` | True | не задано | 1 |
| `asset` | `TEXT` | True | не задано | 2 |
| `resource` | `TEXT` | True | не задано | 3 |
| `version` | `TEXT` | True | не задано | 0 |
| `fingerprint` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_original_versions (
                    link_id TEXT NOT NULL, asset TEXT NOT NULL, resource TEXT NOT NULL,
                    version TEXT NOT NULL, fingerprint TEXT NOT NULL,
                    PRIMARY KEY(link_id,asset,resource));
```

Индексы: `sqlite_autoindex_photos_original_versions_1` (unique=True, partial=False).

<a id="table-photos-sync-requests"></a>

## `photos_sync_requests`

База: `catalog.sqlite3`. Определение: [media_manager/photos_schedule.py:48](../media_manager/photos_schedule.py#L48).

Постоянные запросы расписания по корневой копии, дата обработанного окна, версия замеченного результата, отложенный повтор и текст ошибки.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `link_id` | `TEXT` | False | не задано | 1 |
| `enabled` | `INTEGER` | True | `1` | 0 |
| `last_window` | `TEXT` | False | не задано | 0 |
| `seen_result` | `TEXT` | False | не задано | 0 |
| `retry_after` | `REAL` | True | `0` | 0 |
| `error` | `TEXT` | True | `''` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_sync_requests (
                    link_id TEXT PRIMARY KEY REFERENCES photos_copy_links(id) ON DELETE CASCADE,
                    enabled INTEGER NOT NULL DEFAULT 1, last_window TEXT,
                    seen_result TEXT, retry_after REAL NOT NULL DEFAULT 0,
                    error TEXT NOT NULL DEFAULT '');
```

Внешние ключи:

- `link_id` → `photos_copy_links.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_photos_sync_requests_1` (unique=True, partial=False).

<a id="table-photos-sync-settings"></a>

## `photos_sync_settings`

База: `catalog.sqlite3`. Определение: [media_manager/photos_schedule.py:44](../media_manager/photos_schedule.py#L44).

Настройки окна работы по медиатеке: night_only, часы и Europe/Moscow. Они не совпадают с ручной паузой.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `source_id` | `INTEGER` | False | не задано | 1 |
| `night_only` | `INTEGER` | True | не задано | 0 |
| `start_hour` | `INTEGER` | True | не задано | 0 |
| `end_hour` | `INTEGER` | True | не задано | 0 |
| `timezone` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE photos_sync_settings (
                    source_id INTEGER PRIMARY KEY REFERENCES photos_libraries(source_id) ON DELETE CASCADE,
                    night_only INTEGER NOT NULL, start_hour INTEGER NOT NULL,
                    end_hour INTEGER NOT NULL, timezone TEXT NOT NULL);
```

Внешние ключи:

- `source_id` → `photos_libraries.source_id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: нет.

<a id="table-sources"></a>

## `sources`

База: `catalog.sqlite3`. Определение: [media_manager/catalog.py:15](../media_manager/catalog.py#L15).

Зарегистрированные источники медиаиндекса. kind различает folder и photos; role — прежнее назначение source/storage. path уникален, у Photos это виртуальный URI.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | False | не задано | 1 |
| `path` | `TEXT` | True | не задано | 0 |
| `kind` | `TEXT` | True | `'folder'` | 0 |
| `role` | `TEXT` | True | `'source'` | 0 |
| `label` | `TEXT` | False | не задано | 0 |
| `comment` | `TEXT` | False | не задано | 0 |
| `created_at` | `TEXT` | True | не задано | 0 |
| `last_scan_at` | `TEXT` | False | не задано | 0 |
| `status` | `TEXT` | True | `'idle'` | 0 |
| `error` | `TEXT` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE sources (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL DEFAULT 'folder',
    role TEXT NOT NULL DEFAULT 'source',
    label TEXT,
    comment TEXT,
    created_at TEXT NOT NULL,
    last_scan_at TEXT,
    status TEXT NOT NULL DEFAULT 'idle',
    error TEXT
);
```

Индексы: `sqlite_autoindex_sources_1` (unique=True, partial=False).

<a id="table-thumbnail-jobs"></a>

## `thumbnail_jobs`

База: `catalog.sqlite3`. Определение: [media_manager/catalog.py:49](../media_manager/catalog.py#L49).

Постоянная очередь JPEG-превью, одна строка на media_id и ожидаемую media_version. Состояния pending/running/done/error, приоритет и число попыток.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `media_id` | `INTEGER` | False | не задано | 1 |
| `media_version` | `TEXT` | True | не задано | 0 |
| `status` | `TEXT` | True | `'pending'` | 0 |
| `priority` | `INTEGER` | True | `0` | 0 |
| `attempts` | `INTEGER` | True | `0` | 0 |
| `error` | `TEXT` | False | не задано | 0 |
| `queued_at` | `TEXT` | True | не задано | 0 |
| `started_at` | `TEXT` | False | не задано | 0 |
| `finished_at` | `TEXT` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE thumbnail_jobs (
    media_id INTEGER PRIMARY KEY REFERENCES media_files(id) ON DELETE CASCADE,
    media_version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'done', 'error')),
    priority INTEGER NOT NULL DEFAULT 0,
    attempts INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    queued_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT
);
```

Внешние ключи:

- `media_id` → `media_files.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `thumbnail_jobs_status_priority` (unique=False, partial=False).

<a id="table-thumbnail-waits"></a>

## `thumbnail_waits`

База: `catalog.sqlite3`. Определение: [media_manager/catalog.py:76](../media_manager/catalog.py#L76).

Срок и причина временной отсрочки задания превью. Отличается от окончательной ошибки и ручной паузы.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `media_id` | `INTEGER` | False | не задано | 1 |
| `retry_at` | `REAL` | True | не задано | 0 |
| `reason` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE thumbnail_waits (
    media_id INTEGER PRIMARY KEY REFERENCES media_files(id) ON DELETE CASCADE,
    retry_at REAL NOT NULL,
    reason TEXT NOT NULL
);
```

Внешние ключи:

- `media_id` → `media_files.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: нет.

<a id="table-annotations"></a>

## `annotations`

База: `storage.sqlite3`. Определение: [media_manager/storage.py:180](../media_manager/storage.py#L180).

Прежние назначения и роли, пользовательские флаги и комментарии. При отображении часть полей наследуется от ближайшего предка; современный учёт копий хранится отдельно.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `volume_id` | `TEXT` | True | не задано | 1 |
| `path` | `TEXT` | True | не задано | 2 |
| `purpose` | `TEXT` | False | не задано | 0 |
| `role` | `TEXT` | False | не задано | 0 |
| `no_duplicate` | `INTEGER` | False | не задано | 0 |
| `planned_move` | `INTEGER` | False | не задано | 0 |
| `comment` | `TEXT` | True | `''` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE annotations (
                    volume_id TEXT NOT NULL, path TEXT NOT NULL, purpose TEXT, role TEXT,
                    no_duplicate INTEGER, planned_move INTEGER, comment TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY(volume_id, path)
                );
```

Индексы: `sqlite_autoindex_annotations_1` (unique=True, partial=False).

<a id="table-comparison-entries"></a>

## `comparison_entries`

База: `storage.sqlite3`. Определение: [media_manager/comparison.py:125](../media_manager/comparison.py#L125).

Сохранённые элементы области: пути, имена, тип, stat-параметры, ошибки, прежние хеши и нормализованные ключи поиска.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | False | не задано | 1 |
| `scan_id` | `INTEGER` | True | не задано | 0 |
| `path` | `TEXT` | True | не задано | 0 |
| `parent` | `TEXT` | False | не задано | 0 |
| `name` | `TEXT` | True | не задано | 0 |
| `kind` | `TEXT` | True | не задано | 0 |
| `size` | `INTEGER` | False | не задано | 0 |
| `mtime_ns` | `INTEGER` | False | не задано | 0 |
| `ctime_ns` | `INTEGER` | False | не задано | 0 |
| `inode` | `INTEGER` | False | не задано | 0 |
| `device` | `INTEGER` | False | не задано | 0 |
| `error` | `TEXT` | False | не задано | 0 |
| `digest` | `TEXT` | False | не задано | 0 |
| `hashed_at` | `TEXT` | False | не задано | 0 |
| `cached` | `INTEGER` | True | `0` | 0 |
| `name_key` | `TEXT` | True | `''` | 0 |
| `parent_key` | `TEXT` | True | `''` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE comparison_entries (
                    id INTEGER PRIMARY KEY, scan_id INTEGER NOT NULL, path TEXT NOT NULL,
                    parent TEXT, name TEXT NOT NULL, kind TEXT NOT NULL, size INTEGER,
                    mtime_ns INTEGER, ctime_ns INTEGER, inode INTEGER, device INTEGER,
                    error TEXT, digest TEXT, hashed_at TEXT, cached INTEGER NOT NULL DEFAULT 0, name_key TEXT NOT NULL DEFAULT '', parent_key TEXT NOT NULL DEFAULT '',
                    UNIQUE(scan_id,path)
                );
```

Индексы: `comparison_names` (unique=False, partial=False), `comparison_content` (unique=False, partial=False), `comparison_parent` (unique=False, partial=False), `sqlite_autoindex_comparison_entries_1` (unique=True, partial=False).

<a id="table-comparison-events"></a>

## `comparison_events`

База: `storage.sqlite3`. Определение: [media_manager/comparison.py:144](../media_manager/comparison.py#L144).

Постоянный журнал общей сверки с монотонным ID для обратной пагинации.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | False | не задано | 1 |
| `job_id` | `TEXT` | True | не задано | 0 |
| `at` | `TEXT` | True | не задано | 0 |
| `level` | `TEXT` | True | не задано | 0 |
| `message` | `TEXT` | True | не задано | 0 |
| `path` | `TEXT` | True | `''` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE comparison_events (
                    id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, at TEXT NOT NULL,
                    level TEXT NOT NULL, message TEXT NOT NULL, path TEXT NOT NULL DEFAULT ''
                );
```

Индексы: `comparison_event_job` (unique=False, partial=False).

<a id="table-comparison-hashes"></a>

## `comparison_hashes`

База: `storage.sqlite3`. Определение: [media_manager/comparison.py:138](../media_manager/comparison.py#L138).

Исторический кэш хешей прежней общей сверки содержимого. В текущем Python-коде найдено создание таблицы, но новых чтений/записей этого кэша нет; SHA-256 пар использует paired_entries.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `volume_id` | `TEXT` | True | не задано | 1 |
| `path` | `TEXT` | True | не задано | 2 |
| `size` | `INTEGER` | True | не задано | 0 |
| `mtime_ns` | `INTEGER` | True | не задано | 0 |
| `ctime_ns` | `INTEGER` | True | не задано | 0 |
| `inode` | `INTEGER` | True | не задано | 0 |
| `device` | `INTEGER` | True | не задано | 0 |
| `digest` | `TEXT` | True | не задано | 0 |
| `hashed_at` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE comparison_hashes (
                    volume_id TEXT NOT NULL, path TEXT NOT NULL, size INTEGER NOT NULL,
                    mtime_ns INTEGER NOT NULL, ctime_ns INTEGER NOT NULL, inode INTEGER NOT NULL,
                    device INTEGER NOT NULL, digest TEXT NOT NULL, hashed_at TEXT NOT NULL,
                    PRIMARY KEY(volume_id,path)
                );
```

Индексы: `sqlite_autoindex_comparison_hashes_1` (unique=True, partial=False).

<a id="table-comparison-jobs"></a>

## `comparison_jobs`

База: `storage.sqlite3`. Определение: [media_manager/comparison.py:114](../media_manager/comparison.py#L114).

Задания общей сверки. Новые задания имеют mode=names; content остаётся для чтения старых отчётов. reread и поля хеширования сохранены для совместимости.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `created_at` | `TEXT` | True | не задано | 0 |
| `updated_at` | `TEXT` | True | не задано | 0 |
| `state` | `TEXT` | True | не задано | 0 |
| `phase` | `TEXT` | True | не задано | 0 |
| `reread` | `INTEGER` | True | не задано | 0 |
| `current_path` | `TEXT` | True | `''` | 0 |
| `message` | `TEXT` | True | `''` | 0 |
| `hashed_bytes` | `INTEGER` | True | `0` | 0 |
| `total_bytes` | `INTEGER` | True | `0` | 0 |
| `mode` | `TEXT` | True | `'content'` | 0 |
| `reuse_index` | `INTEGER` | True | `1` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE comparison_jobs (
                    id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    state TEXT NOT NULL, phase TEXT NOT NULL, reread INTEGER NOT NULL,
                    current_path TEXT NOT NULL DEFAULT '', message TEXT NOT NULL DEFAULT '',
                    hashed_bytes INTEGER NOT NULL DEFAULT 0, total_bytes INTEGER NOT NULL DEFAULT 0
                , mode TEXT NOT NULL DEFAULT 'content', reuse_index INTEGER NOT NULL DEFAULT 1);
```

Индексы: `sqlite_autoindex_comparison_jobs_1` (unique=True, partial=False).

<a id="table-comparison-results"></a>

## `comparison_results`

База: `storage.sqlite3`. Определение: [media_manager/comparison.py:135](../media_manager/comparison.py#L135).

Классификация исходных элементов общей сверки по entry_id. Смысл статуса зависит от mode отчёта.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `entry_id` | `INTEGER` | False | не задано | 1 |
| `status` | `TEXT` | True | не задано | 0 |
| `reason` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE comparison_results (
                    entry_id INTEGER PRIMARY KEY, status TEXT NOT NULL, reason TEXT NOT NULL
                );
```

Индексы: нет.

<a id="table-comparison-scans"></a>

## `comparison_scans`

База: `storage.sqlite3`. Определение: [media_manager/comparison.py:120](../media_manager/comparison.py#L120).

Выбранные области общей сверки, сторона source/target, состояние полноты индекса и reused_from для повторно использованных списков.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | False | не задано | 1 |
| `job_id` | `TEXT` | True | не задано | 0 |
| `side` | `TEXT` | True | не задано | 0 |
| `volume_id` | `TEXT` | True | не задано | 0 |
| `root_path` | `TEXT` | True | не задано | 0 |
| `state` | `TEXT` | True | не задано | 0 |
| `started_at` | `TEXT` | False | не задано | 0 |
| `finished_at` | `TEXT` | False | не задано | 0 |
| `error` | `TEXT` | False | не задано | 0 |
| `reused_from` | `INTEGER` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE comparison_scans (
                    id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, side TEXT NOT NULL,
                    volume_id TEXT NOT NULL, root_path TEXT NOT NULL, state TEXT NOT NULL,
                    started_at TEXT, finished_at TEXT, error TEXT
                , reused_from INTEGER);
```

Индексы: `comparison_scan_job` (unique=False, partial=False).

<a id="table-copy-group-settings"></a>

## `copy_group_settings`

База: `storage.sqlite3`. Определение: [media_manager/copies.py:34](../media_manager/copies.py#L34).

Отслеживание основной папки, её метка temporary/inbox/archive и время обнаруженного изменения.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `group_id` | `TEXT` | False | не задано | 1 |
| `tracking` | `INTEGER` | True | `0` | 0 |
| `label` | `TEXT` | True | `''` | 0 |
| `changed_at` | `TEXT` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE copy_group_settings (
    group_id TEXT PRIMARY KEY REFERENCES copy_groups(id) ON DELETE CASCADE,
    tracking INTEGER NOT NULL DEFAULT 0 CHECK(tracking IN (0,1)),
    label TEXT NOT NULL DEFAULT '' CHECK(label IN ('','temporary','inbox','archive')),
    changed_at TEXT
);
```

Внешние ключи:

- `group_id` → `copy_groups.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_copy_group_settings_1` (unique=True, partial=False).

<a id="table-copy-groups"></a>

## `copy_groups`

База: `storage.sqlite3`. Определение: [media_manager/copies.py:16](../media_manager/copies.py#L16).

Наборы одной основной папки и её копий. next_number — сохранённое историческое поле; текущая выдача номера вычисляется из связей и освобождённых номеров.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `next_number` | `INTEGER` | True | `1` | 0 |
| `created_at` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE copy_groups (
    id TEXT PRIMARY KEY, next_number INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
```

Индексы: `sqlite_autoindex_copy_groups_1` (unique=True, partial=False).

<a id="table-copy-locations"></a>

## `copy_locations`

База: `storage.sqlite3`. Определение: [media_manager/copies.py:20](../media_manager/copies.py#L20).

Зарегистрированные области обычных наборов: main имеет номер 0, остальные — положительный номер и copy/cold/cloud. Пересечения областей проверяются кодом.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `group_id` | `TEXT` | True | не задано | 0 |
| `volume_id` | `TEXT` | True | не задано | 0 |
| `path` | `TEXT` | True | не задано | 0 |
| `kind` | `TEXT` | True | не задано | 0 |
| `number` | `INTEGER` | True | не задано | 0 |
| `created_at` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE copy_locations (
    id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL REFERENCES copy_groups(id) ON DELETE CASCADE,
    volume_id TEXT NOT NULL REFERENCES volumes(id),
    path TEXT NOT NULL, kind TEXT NOT NULL, number INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(group_id,number), UNIQUE(volume_id,path),
    CHECK ((kind='main' AND number=0) OR (kind IN ('copy','cold','cloud') AND number>0))
);
```

Внешние ключи:

- `volume_id` → `volumes.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.
- `group_id` → `copy_groups.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `copy_locations_volume` (unique=False, partial=False), `sqlite_autoindex_copy_locations_3` (unique=True, partial=False), `sqlite_autoindex_copy_locations_2` (unique=True, partial=False), `sqlite_autoindex_copy_locations_1` (unique=True, partial=False).

<a id="table-copy-operation-items"></a>

## `copy_operation_items`

База: `storage.sqlite3`. Определение: [media_manager/copy_files.py:109](../media_manager/copy_files.py#L109).

Каждый элемент зафиксированного плана: порядок, тип, JSON data с ожидаемыми параметрами источника, state/message. JSON staging хранит имя и identity созданного файла; final=true помечает конечную незавершённую запись.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `operation_id` | `TEXT` | True | не задано | 1 |
| `position` | `INTEGER` | True | не задано | 0 |
| `path` | `TEXT` | True | не задано | 2 |
| `kind` | `TEXT` | True | не задано | 0 |
| `data` | `TEXT` | True | не задано | 0 |
| `state` | `TEXT` | True | `'pending'` | 0 |
| `message` | `TEXT` | True | `''` | 0 |
| `staging` | `TEXT` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE copy_operation_items (
                    operation_id TEXT NOT NULL REFERENCES copy_operations(id), position INTEGER NOT NULL,
                    path TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'pending', message TEXT NOT NULL DEFAULT '', staging TEXT,
                    PRIMARY KEY(operation_id,path), UNIQUE(operation_id,position)
                );
```

Внешние ключи:

- `operation_id` → `copy_operations.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_copy_operation_items_2` (unique=True, partial=False), `sqlite_autoindex_copy_operation_items_1` (unique=True, partial=False).

<a id="table-copy-operations"></a>

## `copy_operations`

База: `storage.sqlite3`. Определение: [media_manager/copy_files.py:97](../media_manager/copy_files.py#L97).

Сохранённый план и прогресс копирования отсутствующего, снимок областей и корней, счётчики и ссылка на итоговую пересверку.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `report_id` | `TEXT` | True | не задано | 0 |
| `copy_id` | `TEXT` | True | не задано | 0 |
| `state` | `TEXT` | True | не задано | 0 |
| `created_at` | `TEXT` | True | не задано | 0 |
| `updated_at` | `TEXT` | True | не задано | 0 |
| `data` | `TEXT` | True | не задано | 0 |
| `message` | `TEXT` | True | `''` | 0 |
| `current_path` | `TEXT` | True | `''` | 0 |
| `total_files` | `INTEGER` | True | не задано | 0 |
| `total_directories` | `INTEGER` | True | не задано | 0 |
| `total_bytes` | `INTEGER` | True | не задано | 0 |
| `copied_files` | `INTEGER` | True | `0` | 0 |
| `copied_directories` | `INTEGER` | True | `0` | 0 |
| `copied_bytes` | `INTEGER` | True | `0` | 0 |
| `checked_items` | `INTEGER` | True | `0` | 0 |
| `skipped` | `INTEGER` | True | `0` | 0 |
| `errors` | `INTEGER` | True | `0` | 0 |
| `verification_id` | `TEXT` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE copy_operations (
                    id TEXT PRIMARY KEY, report_id TEXT NOT NULL REFERENCES paired_jobs(id),
                    copy_id TEXT NOT NULL, state TEXT NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, data TEXT NOT NULL, message TEXT NOT NULL DEFAULT '',
                    current_path TEXT NOT NULL DEFAULT '', total_files INTEGER NOT NULL,
                    total_directories INTEGER NOT NULL, total_bytes INTEGER NOT NULL,
                    copied_files INTEGER NOT NULL DEFAULT 0, copied_directories INTEGER NOT NULL DEFAULT 0,
                    copied_bytes INTEGER NOT NULL DEFAULT 0, checked_items INTEGER NOT NULL DEFAULT 0,
                    skipped INTEGER NOT NULL DEFAULT 0, errors INTEGER NOT NULL DEFAULT 0,
                    verification_id TEXT REFERENCES paired_jobs(id)
                );
```

Внешние ключи:

- `verification_id` → `paired_jobs.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.
- `report_id` → `paired_jobs.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.

Индексы: `copy_operations_report` (unique=False, partial=False), `sqlite_autoindex_copy_operations_1` (unique=True, partial=False).

<a id="table-copy-sources"></a>

## `copy_sources`

База: `storage.sqlite3`. Определение: [media_manager/copies.py:30](../media_manager/copies.py#L30).

Явные источники обычных копий внутри набора. Нет строки — источник 00-main; направленный цикл запрещён кодом.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `location_id` | `TEXT` | False | не задано | 1 |
| `source_id` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE copy_sources (
    location_id TEXT PRIMARY KEY REFERENCES copy_locations(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL
);
```

Внешние ключи:

- `location_id` → `copy_locations.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_copy_sources_1` (unique=True, partial=False).

<a id="table-directories"></a>

## `directories`

База: `storage.sqlite3`. Определение: [media_manager/storage.py:176](../media_manager/storage.py#L176).

Снимок непосредственных entries папки в JSON. Сохранённый список доступен при отключённом носителе и помечается как cached.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `volume_id` | `TEXT` | True | не задано | 1 |
| `path` | `TEXT` | True | не задано | 2 |
| `scanned_at` | `TEXT` | True | не задано | 0 |
| `entries` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE directories (
                    volume_id TEXT NOT NULL, path TEXT NOT NULL, scanned_at TEXT NOT NULL,
                    entries TEXT NOT NULL, PRIMARY KEY(volume_id, path)
                );
```

Индексы: `sqlite_autoindex_directories_1` (unique=True, partial=False).

<a id="table-directory-sizes"></a>

## `directory_sizes`

База: `storage.sqlite3`. Определение: [media_manager/directory_sizes.py:35](../media_manager/directory_sizes.py#L35).

Сохранённые логические размеры папок, количество файлов, полнота, ошибка, время расчёта и stale. Очередь пересчёта живёт отдельно в памяти.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `volume_id` | `TEXT` | True | не задано | 1 |
| `path` | `TEXT` | True | не задано | 2 |
| `bytes` | `INTEGER` | False | не задано | 0 |
| `files` | `INTEGER` | True | не задано | 0 |
| `calculated_at` | `TEXT` | True | не задано | 0 |
| `complete` | `INTEGER` | True | не задано | 0 |
| `error` | `TEXT` | False | не задано | 0 |
| `stale` | `INTEGER` | True | `0` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE directory_sizes (
                volume_id TEXT NOT NULL, path TEXT NOT NULL, bytes INTEGER,
                files INTEGER NOT NULL, calculated_at TEXT NOT NULL,
                complete INTEGER NOT NULL, error TEXT, stale INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(volume_id,path));
```

Индексы: `sqlite_autoindex_directory_sizes_1` (unique=True, partial=False).

<a id="table-directory-tags"></a>

## `directory_tags`

База: `storage.sqlite3`. Определение: [media_manager/storage.py:185](../media_manager/storage.py#L185).

Пользовательские метки old_copy/sort/check конкретной папки, сохранённые списком JSON.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `volume_id` | `TEXT` | True | не задано | 1 |
| `path` | `TEXT` | True | не задано | 2 |
| `tags` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE directory_tags (
                    volume_id TEXT NOT NULL REFERENCES volumes(id), path TEXT NOT NULL,
                    tags TEXT NOT NULL, PRIMARY KEY(volume_id,path)
                );
```

Внешние ключи:

- `volume_id` → `volumes.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_directory_tags_1` (unique=True, partial=False).

<a id="table-disconnected-copy-groups"></a>

## `disconnected_copy_groups`

База: `storage.sqlite3`. Определение: [media_manager/copies.py:40](../media_manager/copies.py#L40).

Логическое отключение набора без удаления связей, данных и истории.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `group_id` | `TEXT` | False | не задано | 1 |
| `disconnected_at` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE disconnected_copy_groups (
    group_id TEXT PRIMARY KEY REFERENCES copy_groups(id) ON DELETE CASCADE,
    disconnected_at TEXT NOT NULL
);
```

Внешние ключи:

- `group_id` → `copy_groups.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_disconnected_copy_groups_1` (unique=True, partial=False).

<a id="table-disconnected-copy-locations"></a>

## `disconnected_copy_locations`

База: `storage.sqlite3`. Определение: [media_manager/copies.py:44](../media_manager/copies.py#L44).

Логическое отключение конкретной копии без освобождения её номера.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `location_id` | `TEXT` | False | не задано | 1 |
| `disconnected_at` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE disconnected_copy_locations (
    location_id TEXT PRIMARY KEY REFERENCES copy_locations(id) ON DELETE CASCADE,
    disconnected_at TEXT NOT NULL
);
```

Внешние ключи:

- `location_id` → `copy_locations.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_disconnected_copy_locations_1` (unique=True, partial=False).

<a id="table-folder-marker-jobs"></a>

## `folder_marker_jobs`

База: `storage.sqlite3`. Определение: [media_manager/folder_markers.py:19](../media_manager/folder_markers.py#L19).

Постоянная очередь записи .media-actu-folder.json с JSON payload, ревизией, состоянием, ошибкой и сроком следующей попытки.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `location_id` | `TEXT` | False | не задано | 1 |
| `group_id` | `TEXT` | True | не задано | 0 |
| `volume_id` | `TEXT` | True | не задано | 0 |
| `path` | `TEXT` | True | не задано | 0 |
| `payload` | `TEXT` | True | не задано | 0 |
| `revision` | `INTEGER` | True | `1` | 0 |
| `state` | `TEXT` | True | `'pending'` | 0 |
| `error` | `TEXT` | False | не задано | 0 |
| `synced_at` | `TEXT` | False | не задано | 0 |
| `next_check` | `REAL` | True | `0` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE folder_marker_jobs (
    location_id TEXT PRIMARY KEY, group_id TEXT NOT NULL, volume_id TEXT NOT NULL,
    path TEXT NOT NULL, payload TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1,
    state TEXT NOT NULL DEFAULT 'pending', error TEXT, synced_at TEXT,
    next_check REAL NOT NULL DEFAULT 0
);
```

Индексы: `sqlite_autoindex_folder_marker_jobs_1` (unique=True, partial=False).

<a id="table-network-servers"></a>

## `network_servers`

База: `storage.sqlite3`. Определение: [media_manager/network.py:165](../media_manager/network.py#L165).

Запомненные серверы Bonjour/SMB, адреса, доступность и ошибки последней проверки.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `name` | `TEXT` | True | не задано | 0 |
| `host` | `TEXT` | True | не задано | 0 |
| `port` | `INTEGER` | True | не задано | 0 |
| `aliases` | `TEXT` | True | не задано | 0 |
| `last_seen` | `TEXT` | True | не задано | 0 |
| `discovered` | `INTEGER` | True | `1` | 0 |
| `shares_at` | `TEXT` | False | не задано | 0 |
| `error` | `TEXT` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE network_servers (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, host TEXT NOT NULL,
                    port INTEGER NOT NULL, aliases TEXT NOT NULL, last_seen TEXT NOT NULL,
                    discovered INTEGER NOT NULL DEFAULT 1, shares_at TEXT, error TEXT
                );
```

Индексы: `sqlite_autoindex_network_servers_1` (unique=True, partial=False).

<a id="table-network-shares"></a>

## `network_shares`

База: `storage.sqlite3`. Определение: [media_manager/network.py:170](../media_manager/network.py#L170).

Кэш ресурсов сервера с их видом и примечанием; используется при недоступности сети.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `server_id` | `TEXT` | True | не задано | 1 |
| `name` | `TEXT` | True | не задано | 2 |
| `comment` | `TEXT` | True | не задано | 0 |
| `last_seen` | `TEXT` | True | не задано | 0 |
| `present` | `INTEGER` | True | `1` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE network_shares (
                    server_id TEXT NOT NULL, name TEXT NOT NULL, comment TEXT NOT NULL,
                    last_seen TEXT NOT NULL, present INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY(server_id, name)
                );
```

Индексы: `sqlite_autoindex_network_shares_1` (unique=True, partial=False).

<a id="table-network-volume-links"></a>

## `network_volume_links`

База: `storage.sqlite3`. Определение: [media_manager/storage.py:190](../media_manager/storage.py#L190).

Сохранённый URL SMB-ресурса для подключения Finder. Пароли в эту таблицу не записываются.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `volume_id` | `TEXT` | False | не задано | 1 |
| `url` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE network_volume_links (volume_id TEXT PRIMARY KEY, url TEXT NOT NULL);
```

Индексы: `sqlite_autoindex_network_volume_links_1` (unique=True, partial=False).

<a id="table-paired-decisions"></a>

## `paired_decisions`

База: `storage.sqlite3`. Определение: [media_manager/paired_comparison.py:69](../media_manager/paired_comparison.py#L69).

Плановые решения keep/add_main/move/remove для extra_copy. Они наследуются вложенными элементами и сами не запускают файловые операции.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `job_id` | `TEXT` | True | не задано | 1 |
| `path` | `TEXT` | True | не задано | 2 |
| `action` | `TEXT` | True | не задано | 0 |
| `updated_at` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE paired_decisions (
                    job_id TEXT NOT NULL REFERENCES paired_jobs(id), path TEXT NOT NULL,
                    action TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(job_id,path)
                );
```

Внешние ключи:

- `job_id` → `paired_jobs.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_paired_decisions_1` (unique=True, partial=False).

<a id="table-paired-entries"></a>

## `paired_entries`

База: `storage.sqlite3`. Определение: [media_manager/paired_comparison.py:60](../media_manager/paired_comparison.py#L60).

Сохранённые метаданные и дополнительные digest одной стороны пары по относительному пути.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `job_id` | `TEXT` | True | не задано | 1 |
| `side` | `TEXT` | True | не задано | 2 |
| `path` | `TEXT` | True | не задано | 3 |
| `data` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE paired_entries (
                    job_id TEXT NOT NULL REFERENCES paired_jobs(id), side TEXT NOT NULL,
                    path TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY(job_id,side,path)
                );
```

Внешние ключи:

- `job_id` → `paired_jobs.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_paired_entries_1` (unique=True, partial=False).

<a id="table-paired-jobs"></a>

## `paired_jobs`

База: `storage.sqlite3`. Определение: [media_manager/paired_comparison.py:48](../media_manager/paired_comparison.py#L48).

Задания парной сверки: выбранные области в JSON, режим folders/files, метод size/sha256, полнота сторон, счётчики и состояние.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `copy_id` | `TEXT` | True | не задано | 0 |
| `mode` | `TEXT` | True | не задано | 0 |
| `state` | `TEXT` | True | не задано | 0 |
| `phase` | `TEXT` | True | не задано | 0 |
| `created_at` | `TEXT` | True | не задано | 0 |
| `updated_at` | `TEXT` | True | не задано | 0 |
| `scopes` | `TEXT` | True | не задано | 0 |
| `base_job_id` | `TEXT` | False | не задано | 0 |
| `left_complete` | `INTEGER` | True | `0` | 0 |
| `right_complete` | `INTEGER` | True | `0` | 0 |
| `current_path` | `TEXT` | True | `''` | 0 |
| `message` | `TEXT` | True | `''` | 0 |
| `hashed_bytes` | `INTEGER` | True | `0` | 0 |
| `total_bytes` | `INTEGER` | True | `0` | 0 |
| `checked_files` | `INTEGER` | True | `0` | 0 |
| `total_files` | `INTEGER` | True | `0` | 0 |
| `indexed_directories` | `INTEGER` | True | `0` | 0 |
| `errors` | `INTEGER` | True | `0` | 0 |
| `method` | `TEXT` | True | `'sha256'` | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE paired_jobs (
                    id TEXT PRIMARY KEY, copy_id TEXT NOT NULL, mode TEXT NOT NULL,
                    state TEXT NOT NULL, phase TEXT NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, scopes TEXT NOT NULL, base_job_id TEXT,
                    left_complete INTEGER NOT NULL DEFAULT 0, right_complete INTEGER NOT NULL DEFAULT 0,
                    current_path TEXT NOT NULL DEFAULT '', message TEXT NOT NULL DEFAULT '',
                    hashed_bytes INTEGER NOT NULL DEFAULT 0, total_bytes INTEGER NOT NULL DEFAULT 0,
                    checked_files INTEGER NOT NULL DEFAULT 0, total_files INTEGER NOT NULL DEFAULT 0,
                    indexed_directories INTEGER NOT NULL DEFAULT 0,
                    errors INTEGER NOT NULL DEFAULT 0
                , method TEXT NOT NULL DEFAULT 'sha256');
```

Индексы: `paired_jobs_copy` (unique=False, partial=False), `sqlite_autoindex_paired_jobs_1` (unique=True, partial=False).

<a id="table-paired-rows"></a>

## `paired_rows`

База: `storage.sqlite3`. Определение: [media_manager/paired_comparison.py:64](../media_manager/paired_comparison.py#L64).

Выровненные строки результата с устойчивым порядком position, статусом и JSON обеих сторон.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `job_id` | `TEXT` | True | не задано | 1 |
| `position` | `INTEGER` | True | не задано | 0 |
| `path` | `TEXT` | True | не задано | 2 |
| `kind` | `TEXT` | True | не задано | 0 |
| `status` | `TEXT` | True | не задано | 0 |
| `data` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE paired_rows (
                    job_id TEXT NOT NULL REFERENCES paired_jobs(id), position INTEGER NOT NULL,
                    path TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(job_id,path), UNIQUE(job_id,position)
                );
```

Внешние ключи:

- `job_id` → `paired_jobs.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.

Индексы: `sqlite_autoindex_paired_rows_2` (unique=True, partial=False), `sqlite_autoindex_paired_rows_1` (unique=True, partial=False).

<a id="table-released-copy-locations"></a>

## `released_copy_locations`

База: `storage.sqlite3`. Определение: [media_manager/copies.py:48](../media_manager/copies.py#L48).

Архив прежних отключённых привязок с освобождённым номером. Их история остаётся, но новые сверки и копирование запрещены.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `group_id` | `TEXT` | True | не задано | 0 |
| `volume_id` | `TEXT` | True | не задано | 0 |
| `path` | `TEXT` | True | не задано | 0 |
| `kind` | `TEXT` | True | не задано | 0 |
| `number` | `INTEGER` | True | не задано | 0 |
| `created_at` | `TEXT` | True | не задано | 0 |
| `disconnected_at` | `TEXT` | True | не задано | 0 |
| `released_at` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE released_copy_locations (
    id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL REFERENCES copy_groups(id) ON DELETE CASCADE,
    volume_id TEXT NOT NULL REFERENCES volumes(id),
    path TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('copy','cold','cloud')),
    number INTEGER NOT NULL CHECK(number>0), created_at TEXT NOT NULL,
    disconnected_at TEXT NOT NULL, released_at TEXT NOT NULL
);
```

Внешние ключи:

- `volume_id` → `volumes.id`, ON DELETE `NO ACTION`, ON UPDATE `NO ACTION`.
- `group_id` → `copy_groups.id`, ON DELETE `CASCADE`, ON UPDATE `NO ACTION`.

Индексы: `released_copy_locations_group` (unique=False, partial=False), `sqlite_autoindex_released_copy_locations_1` (unique=True, partial=False).

<a id="table-volume-aliases"></a>

## `volume_aliases`

База: `storage.sqlite3`. Определение: [media_manager/storage.py:191](../media_manager/storage.py#L191).

Сопоставление прежних ID сетевого ресурса с устойчивой записью тома при изменении адреса сервера.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `alias_id` | `TEXT` | False | не задано | 1 |
| `volume_id` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE volume_aliases (alias_id TEXT PRIMARY KEY, volume_id TEXT NOT NULL);
```

Индексы: `sqlite_autoindex_volume_aliases_1` (unique=True, partial=False).

<a id="table-volume-capacity"></a>

## `volume_capacity`

База: `storage.sqlite3`. Определение: [media_manager/storage.py:196](../media_manager/storage.py#L196).

Последний успешный замер ёмкости: полный, занятый, свободный и доступный объём плюс checked_at. Сохраняется после отключения.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `volume_id` | `TEXT` | False | не задано | 1 |
| `total_bytes` | `INTEGER` | True | не задано | 0 |
| `used_bytes` | `INTEGER` | True | не задано | 0 |
| `free_bytes` | `INTEGER` | True | не задано | 0 |
| `available_bytes` | `INTEGER` | True | не задано | 0 |
| `checked_at` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE volume_capacity (
                volume_id TEXT PRIMARY KEY, total_bytes INTEGER NOT NULL, used_bytes INTEGER NOT NULL,
                free_bytes INTEGER NOT NULL, available_bytes INTEGER NOT NULL, checked_at TEXT NOT NULL);
```

Индексы: `sqlite_autoindex_volume_capacity_1` (unique=True, partial=False).

<a id="table-volume-details"></a>

## `volume_details`

База: `storage.sqlite3`. Определение: [media_manager/storage.py:193](../media_manager/storage.py#L193).

Идентичность носителя: removable, verified/resource/unverified/legacy, marker_id, имя ресурса и ошибка подтверждения.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `volume_id` | `TEXT` | False | не задано | 1 |
| `removable` | `INTEGER` | True | не задано | 0 |
| `identity_status` | `TEXT` | True | не задано | 0 |
| `marker_id` | `TEXT` | False | не задано | 0 |
| `share_name` | `TEXT` | False | не задано | 0 |
| `identity_error` | `TEXT` | False | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE volume_details (
                volume_id TEXT PRIMARY KEY, removable INTEGER NOT NULL, identity_status TEXT NOT NULL,
                marker_id TEXT, share_name TEXT, identity_error TEXT);
```

Индексы: `sqlite_autoindex_volume_details_1` (unique=True, partial=False).

<a id="table-volume-origins"></a>

## `volume_origins`

База: `storage.sqlite3`. Определение: [media_manager/storage.py:192](../media_manager/storage.py#L192).

Запомненный сервер происхождения сетевого тома для группировки после отключения.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `volume_id` | `TEXT` | False | не задано | 1 |
| `host` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE volume_origins (volume_id TEXT PRIMARY KEY, host TEXT NOT NULL);
```

Индексы: `sqlite_autoindex_volume_origins_1` (unique=True, partial=False).

<a id="table-volumes"></a>

## `volumes`

База: `storage.sqlite3`. Определение: [media_manager/storage.py:172](../media_manager/storage.py#L172).

Устойчивые записи обнаруженных и запомненных томов. last_seen — время обнаружения, а не доказательство текущей доступности.

| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |
| --- | --- | --- | --- | --- |
| `id` | `TEXT` | False | не задано | 1 |
| `name` | `TEXT` | True | не задано | 0 |
| `mount_path` | `TEXT` | True | не задано | 0 |
| `kind` | `TEXT` | True | не задано | 0 |
| `first_seen` | `TEXT` | True | не задано | 0 |
| `last_seen` | `TEXT` | True | не задано | 0 |

Полное DDL (включает действующие CHECK, UNIQUE и добавленные поля):

```sql
CREATE TABLE volumes (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, mount_path TEXT NOT NULL,
                    kind TEXT NOT NULL, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL
                );
```

Индексы: `sqlite_autoindex_volumes_1` (unique=True, partial=False).
