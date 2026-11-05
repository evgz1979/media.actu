# Виртуальное дерево Photos: `media_manager/photos_browser.py`

Строит годы, месяцы и страницы объектов из сохранённого каталога. Чтение дерева не обращается к PhotoKit и не экспортирует оригиналы.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/photos_browser.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_photos_browser.py](tests.md#module-tests.test_photos_browser).

## Оглавление определений

- [PhotosBrowser](#symbol-PhotosBrowser) — Предоставляет папки и объекты Photos поверх сохранённого медиаиндекса.
- [PhotosBrowser.__init__](#symbol-PhotosBrowser.__init__) — Инициализирует PhotosBrowser и его рабочее состояние.
- [PhotosBrowser.browse](#symbol-PhotosBrowser.browse) — Возвращает виртуальную папку или объект с пагинацией и приоритетом превью.
- [PhotosBrowser.preview_status](#symbol-PhotosBrowser.preview_status) — Возвращает готовые ID превью из запрошенного набора объектов медиатеки.
- [photo_entry](#symbol-photo_entry) — Преобразует строку медиаиндекса в виртуальный файловый элемент UI.

<a id="symbol-PhotosBrowser"></a>

## `PhotosBrowser`

[media_manager/photos_browser.py](../../media_manager/photos_browser.py) · `PhotosBrowser`

Предоставляет папки и объекты Photos поверх сохранённого медиаиндекса. Зависимости конструктора: libraries.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `catalog`, `libraries`.

Именованные методы: `__init__`, `browse`, `preview_status`.

<a id="symbol-PhotosBrowser.__init__"></a>

## `PhotosBrowser.__init__`

[media_manager/photos_browser.py](../../media_manager/photos_browser.py) · `PhotosBrowser.__init__`

Инициализирует PhotosBrowser и его рабочее состояние. Обновляет состояние объекта: catalog, libraries.

```python
def __init__(self, libraries)
```

Присваивания полям `self`: `catalog`, `libraries`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosBrowser.browse"></a>

## `PhotosBrowser.browse`

[media_manager/photos_browser.py](../../media_manager/photos_browser.py) · `PhotosBrowser.browse`

Возвращает виртуальную папку или объект с пагинацией и приоритетом превью. Явно отклоняет недопустимое состояние через KeyError.

```python
def browse(self, source_id, path='', *, offset=0, limit=150)
```

SQLite: чтение `media_files`, `thumbnail_jobs`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `PurePosixPath`, `bool`, `children.setdefault`, `children.values`, `db.execute`, `db.execute('SELECT COUNT(*) FROM media_files WHERE source_id=? AND parent_path=?', (source_id, path)).fetchone`, `db.execute('SELECT m.*,j.status AS thumbnail_status\n                    FROM media_files m LEFT JOIN thumbnail_jobs j ON j.media_id=m.id\n                    WHERE m.source_id=? AND m.id=?', (source_id, int(leaf))).fetchone`, `db.execute('SELECT m.*,j.status AS thumbnail_status\n                    FROM media_files m LEFT JOIN thumbnail_jobs j ON j.media_id=m.id\n                    WHERE m.source_id=? AND m.parent_path=?\n                    ORDER BY m.name COLLATE NOCASE,m.id LIMIT ? OFFSET ?', (source_id, path, remaining, max(0, offset - len(folders)))).fetchall`, `db.execute('SELECT parent_path,COUNT(*) AS count,SUM(size) AS size\n                FROM media_files WHERE source_id=? GROUP BY parent_path', (source_id,)).fetchall`, `dict`, `entries.extend`, `int`, `leaf.isascii`, `leaf.isdigit`, `len`, `max`, `min`, `parent.startswith`, `parent[len(prefix):].split`, [photo_entry](media_manager--photos_browser.md#symbol-photo_entry), `relative_path`, `self.catalog.connect`, `self.catalog.get_source`, `self.catalog.prioritize_folder_thumbnails`, `self.libraries.profile`, `sorted`, `source.get`.

Явные `raise`:

- `KeyError('Папка медиатеки не найдена')`

Выражения возврата (ветви, без исполнения):

- `dict(entry=photo_entry(row), kind='file')`
- `dict(path=path, kind='directory', entries=entries, total=total, has_more=offset + len(entries) < total, scanned_at=source.get('last_scan_at') or source['created_at'], cached=not bool(profile['active']), source_id=source_id)`


<a id="symbol-PhotosBrowser.preview_status"></a>

## `PhotosBrowser.preview_status`

[media_manager/photos_browser.py](../../media_manager/photos_browser.py) · `PhotosBrowser.preview_status`

Возвращает готовые ID превью из запрошенного набора объектов медиатеки. Поля результата: ready.

```python
def preview_status(self, source_id, ids)
```

SQLite: чтение `media_files`, `thumbnail_jobs`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `dict`, `dict.fromkeys`, `list`, `self.catalog.connect`, `self.libraries.profile`.

Выражения возврата (ветви, без исполнения):

- `dict(ready=[])`
- `dict(ready=ready)`


<a id="symbol-photo_entry"></a>

## `photo_entry`

[media_manager/photos_browser.py](../../media_manager/photos_browser.py) · `photo_entry`

Преобразует строку медиаиндекса в виртуальный файловый элемент UI. Поля результата: path, name, kind, media_kind, media_id, size, modified_at, preview_ready.

```python
def photo_entry(row)
```

Прямые выражения вызова: `'/'.join`, `dict`, `filter`, `str`.

Выражения возврата (ветви, без исполнения):

- `dict(path='/'.join(filter(None, (row['parent_path'], str(row['id'])))), name=row['name'], kind='file', media_kind=row['kind'], media_id=row['id'], size=row['size'] or None, modified_at=row['modified_at'], preview_ready=row['thumbnail_status'] == 'done')`
