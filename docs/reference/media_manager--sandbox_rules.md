# Правила sandbox: `media_manager/sandbox_rules.py`

Формирует текст исключений sandbox-exec для служебных маркеров и создания новых копий. Эти функции не устанавливают sandbox и не меняют конфигурацию Launcher сами.

[Исходный модуль](../../media_manager/sandbox_rules.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: нет прямых импортов; см. запуск через `-m`, пакет или внешнюю конфигурацию.
Тестовые модули с прямым импортом: [tests/test_copy_sandbox.py](../../tests/test_copy_sandbox.py#L8).

## Оглавление определений

- [marker_write_rules](#symbol-marker-write-rules) — Формирует правило записи служебного маркера в корне носителя.
- [folder_marker_write_rules](#symbol-folder-marker-write-rules) — Формирует правило записи служебного описания внутри зарегистрированной папки.
- [copy_write_rules](#symbol-copy-write-rules) — Формирует правила создания новых копий и собственных временных файлов.

<a id="symbol-marker-write-rules"></a>

## `marker_write_rules`

[media_manager/sandbox_rules.py:8](../../media_manager/sandbox_rules.py#L8)

Формирует правило записи служебного маркера в корне носителя. Использует json.dumps, re.escape, re.escape(root.rstrip('/')).replace, root.rstrip.

```python
def marker_write_rules(root='/Volumes')
```

Прямые выражения вызова: `json.dumps`, `re.escape`, `re.escape(root.rstrip('/')).replace`, `root.rstrip`.

Выражения возврата (ветви, без исполнения):

- `'(allow file-write-create file-write-data file-write-unlink (regex #' + json.dumps(marker) + '))'`


<a id="symbol-folder-marker-write-rules"></a>

## `folder_marker_write_rules`

[media_manager/sandbox_rules.py:16](../../media_manager/sandbox_rules.py#L16)

Формирует правило записи служебного описания внутри зарегистрированной папки. Использует json.dumps, re.escape, re.escape(root.rstrip('/')).replace, root.rstrip.

```python
def folder_marker_write_rules(root='/Volumes')
```

Прямые выражения вызова: `json.dumps`, `re.escape`, `re.escape(root.rstrip('/')).replace`, `root.rstrip`.

Выражения возврата (ветви, без исполнения):

- `'(allow file-write-create file-write-data file-write-unlink (regex #' + json.dumps(marker) + '))'`


<a id="symbol-copy-write-rules"></a>

## `copy_write_rules`

[media_manager/sandbox_rules.py:24](../../media_manager/sandbox_rules.py#L24)

Формирует правила создания новых копий и собственных временных файлов. Использует json.dumps, re.escape, re.escape(root).replace, root.rstrip.

```python
def copy_write_rules(root='/Volumes')
```

Прямые выражения вызова: `json.dumps`, `re.escape`, `re.escape(root).replace`, `root.rstrip`.

Выражения возврата (ветви, без исполнения):

- `'(allow file-write-create (subpath ' + json.dumps(root) + ')) (allow file-write* (regex #' + json.dumps(temporary) + '))'`
