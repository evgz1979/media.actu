# Правила sandbox: `media_manager/sandbox_rules.py`

Формирует текст исключений sandbox-exec для служебных маркеров и создания новых копий. Эти функции не устанавливают sandbox и не меняют конфигурацию Launcher сами.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/sandbox_rules.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: вход может выполняться через CLI или внешнюю конфигурацию.
Тестовые модули с прямым импортом: [tests/test_copy_sandbox.py](tests.md#module-tests.test_copy_sandbox).

## Оглавление определений

- [copy_write_rules](#symbol-copy_write_rules) — Формирует правила создания новых копий и собственных временных файлов.
- [folder_marker_write_rules](#symbol-folder_marker_write_rules) — Формирует правило записи служебного описания внутри зарегистрированной папки.
- [marker_write_rules](#symbol-marker_write_rules) — Формирует правило записи служебного маркера в корне носителя.

<a id="symbol-copy_write_rules"></a>

## `copy_write_rules`

[media_manager/sandbox_rules.py](../../media_manager/sandbox_rules.py) · `copy_write_rules`

Формирует правила создания новых копий и собственных временных файлов. Использует json.dumps, re.escape, re.escape(root).replace, root.rstrip.

```python
def copy_write_rules(root='/Volumes')
```

Прямые выражения вызова: `json.dumps`, `re.escape`, `re.escape(root).replace`, `root.rstrip`.

Выражения возврата (ветви, без исполнения):

- `'(allow file-write-create (subpath ' + json.dumps(root) + ')) (allow file-write* (regex #' + json.dumps(temporary) + '))'`


<a id="symbol-folder_marker_write_rules"></a>

## `folder_marker_write_rules`

[media_manager/sandbox_rules.py](../../media_manager/sandbox_rules.py) · `folder_marker_write_rules`

Формирует правило записи служебного описания внутри зарегистрированной папки. Использует json.dumps, re.escape, re.escape(root.rstrip('/')).replace, root.rstrip.

```python
def folder_marker_write_rules(root='/Volumes')
```

Прямые выражения вызова: `json.dumps`, `re.escape`, `re.escape(root.rstrip('/')).replace`, `root.rstrip`.

Выражения возврата (ветви, без исполнения):

- `'(allow file-write-create file-write-data file-write-unlink (regex #' + json.dumps(marker) + '))'`


<a id="symbol-marker_write_rules"></a>

## `marker_write_rules`

[media_manager/sandbox_rules.py](../../media_manager/sandbox_rules.py) · `marker_write_rules`

Формирует правило записи служебного маркера в корне носителя. Использует json.dumps, re.escape, re.escape(root.rstrip('/')).replace, root.rstrip.

```python
def marker_write_rules(root='/Volumes')
```

Прямые выражения вызова: `json.dumps`, `re.escape`, `re.escape(root.rstrip('/')).replace`, `root.rstrip`.

Выражения возврата (ветви, без исполнения):

- `'(allow file-write-create file-write-data file-write-unlink (regex #' + json.dumps(marker) + '))'`
