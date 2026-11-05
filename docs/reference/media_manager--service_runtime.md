# Запуск сервисов и журналы: `media_manager/service_runtime.py`

Обёртка Launcher для stdout/stderr, ротации журналов и диагностических стеков. Поддерживает запуск Python-модуля и строки команды с исходными аргументами.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/service_runtime.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: вход может выполняться через CLI или внешнюю конфигурацию.
Тестовые модули с прямым импортом: [tests/test_service_runtime.py](tests.md#module-tests.test_service_runtime).

## Оглавление определений

- [ServiceFileHandler](#symbol-ServiceFileHandler) — Останавливает рекурсивное журналирование при ошибке записи файла журнала.
- [ServiceFileHandler.handleError](#symbol-ServiceFileHandler.handleError) — Фиксирует отказ обработчика без повторного вывода в перенаправленный stderr.
- [ServiceLogStream](#symbol-ServiceLogStream) — Перенаправляет текстовый вывод сервиса в ограниченный ротируемый журнал.
- [ServiceLogStream.__init__](#symbol-ServiceLogStream.__init__) — Инициализирует ServiceLogStream и его рабочее состояние.
- [ServiceLogStream.encoding](#symbol-ServiceLogStream.encoding) — Объявляет UTF-8 как кодировку текстового потока журнала.
- [ServiceLogStream.flush](#symbol-ServiceLogStream.flush) — Сбрасывает буфер файлового обработчика журнала.
- [ServiceLogStream.writable](#symbol-ServiceLogStream.writable) — Сообщает, что поток принимает текст для записи в журнал.
- [ServiceLogStream.write](#symbol-ServiceLogStream.write) — Разбивает текст на ограниченные блоки и передаёт файловому обработчику.
- [configure_logging](#symbol-configure_logging) — Настраивает журналы stdout/stderr и диагностические стеки выбранного сервиса.
- [main](#symbol-main) — Запускает модуль или команду Python после настройки журналирования Launcher.

<a id="symbol-ServiceFileHandler"></a>

## `ServiceFileHandler`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `ServiceFileHandler`

Останавливает рекурсивное журналирование при ошибке записи файла журнала. Базовые типы: RotatingFileHandler.

Базовые классы: `RotatingFileHandler`.


Именованные методы: `handleError`.

<a id="symbol-ServiceFileHandler.handleError"></a>

## `ServiceFileHandler.handleError`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `ServiceFileHandler.handleError`

Фиксирует отказ обработчика без повторного вывода в перенаправленный stderr. Обновляет состояние объекта: failed.

```python
def handleError(self, record)
```

Присваивания полям `self`: `failed`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ServiceLogStream"></a>

## `ServiceLogStream`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `ServiceLogStream`

Перенаправляет текстовый вывод сервиса в ограниченный ротируемый журнал. Зависимости конструктора: path.

Базовые классы: `io.TextIOBase`.


Состояние, присваиваемое конструктором: `chunk_size`, `handler`.

Именованные методы: `__init__`, `encoding`, `writable`, `write`, `flush`.

<a id="symbol-ServiceLogStream.__init__"></a>

## `ServiceLogStream.__init__`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `ServiceLogStream.__init__`

Инициализирует ServiceLogStream и его рабочее состояние. Обновляет состояние объекта: chunk_size, handler.

```python
def __init__(self, path, *, max_bytes=2 * 1024 * 1024, backups=3)
```

Присваивания полям `self`: `chunk_size`, `handler`.

Прямые выражения вызова: [ServiceFileHandler](media_manager--service_runtime.md#symbol-ServiceFileHandler), `logging.Formatter`, `max`, `min`, `self.handler.setFormatter`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ServiceLogStream.encoding"></a>

## `ServiceLogStream.encoding`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `ServiceLogStream.encoding`

Объявляет UTF-8 как кодировку текстового потока журнала. Возвращает локальное значение без обращения к файловой системе.

```python
def encoding(self)
```

Декораторы: `property`.

Выражения возврата (ветви, без исполнения):

- `'utf-8'`


<a id="symbol-ServiceLogStream.flush"></a>

## `ServiceLogStream.flush`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `ServiceLogStream.flush`

Сбрасывает буфер файлового обработчика журнала. Использует self.handler.flush.

```python
def flush(self)
```

Прямые выражения вызова: `self.handler.flush`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ServiceLogStream.writable"></a>

## `ServiceLogStream.writable`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `ServiceLogStream.writable`

Сообщает, что поток принимает текст для записи в журнал. Возвращает локальное значение без обращения к файловой системе.

```python
def writable(self)
```

Выражения возврата (ветви, без исполнения):

- `True`


<a id="symbol-ServiceLogStream.write"></a>

## `ServiceLogStream.write`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `ServiceLogStream.write`

Разбивает текст на ограниченные блоки и передаёт файловому обработчику. Использует logging.LogRecord, self.handler.handle.

```python
def write(self, text)
```

Прямые выражения вызова: `len`, `logging.LogRecord`, `range`, `self.handler.handle`.

Выражения возврата (ветви, без исполнения):

- `len(text)`


<a id="symbol-configure_logging"></a>

## `configure_logging`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `configure_logging`

Настраивает журналы stdout/stderr и диагностические стеки выбранного сервиса. Явно отклоняет недопустимое состояние через ValueError.

```python
def configure_logging(service)
```

Прямые выражения вызова: `Path`, `Path(__file__).resolve`, `Path(os.environ.get('MEDIA_ACTU_DATA_DIR', str(default))).expanduser`, [ServiceLogStream](media_manager--service_runtime.md#symbol-ServiceLogStream), `ValueError`, `_diagnostic_files.append`, `directory.mkdir`, `faulthandler.enable`, `faulthandler.register`, `hasattr`, `os.environ.get`, `stacks.exists`, `stacks.open`, `stacks.replace`, `stacks.stat`, `stacks.with_suffix`, `str`.

Явные `raise`:

- `ValueError('Expected core or ui service')`

Выражения возврата (ветви, без исполнения):

- `stream`


<a id="symbol-main"></a>

## `main`

[media_manager/service_runtime.py](../../media_manager/service_runtime.py) · `main`

Запускает модуль или команду Python после настройки журналирования Launcher. Явно отклоняет недопустимое состояние через SystemExit.

```python
def main()
```

Прямые выражения вызова: `SystemExit`, `compile`, [configure_logging](media_manager--service_runtime.md#symbol-configure_logging), `exec`, `len`, `runpy.run_module`.

Явные `raise`:

- `SystemExit('Usage: service_runtime core&#124;ui -m MODULE [ARGS] &#124; -c CODE [ARGS]')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
