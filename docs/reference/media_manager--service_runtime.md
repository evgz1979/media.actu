# Запуск сервисов и журналы: `media_manager/service_runtime.py`

Обёртка Launcher для stdout/stderr, ротации журналов и диагностических стеков. Поддерживает запуск Python-модуля и строки команды с исходными аргументами.

[Исходный модуль](../../media_manager/service_runtime.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: нет прямых импортов; см. запуск через `-m`, пакет или внешнюю конфигурацию.
Тестовые модули с прямым импортом: [tests/test_service_runtime.py](../../tests/test_service_runtime.py#L9).

## Оглавление определений

- [ServiceFileHandler](#symbol-servicefilehandler) — Останавливает рекурсивное журналирование при ошибке записи файла журнала.
- [ServiceFileHandler.handleError](#symbol-servicefilehandler-handleerror) — Фиксирует отказ обработчика без повторного вывода в перенаправленный stderr.
- [ServiceLogStream](#symbol-servicelogstream) — Перенаправляет текстовый вывод сервиса в ограниченный ротируемый журнал.
- [ServiceLogStream.__init__](#symbol-servicelogstream---init--) — Инициализирует ServiceLogStream и его рабочее состояние.
- [ServiceLogStream.encoding](#symbol-servicelogstream-encoding) — Объявляет UTF-8 как кодировку текстового потока журнала.
- [ServiceLogStream.writable](#symbol-servicelogstream-writable) — Сообщает, что поток принимает текст для записи в журнал.
- [ServiceLogStream.write](#symbol-servicelogstream-write) — Разбивает текст на ограниченные блоки и передаёт файловому обработчику.
- [ServiceLogStream.flush](#symbol-servicelogstream-flush) — Сбрасывает буфер файлового обработчика журнала.
- [configure_logging](#symbol-configure-logging) — Настраивает журналы stdout/stderr и диагностические стеки выбранного сервиса.
- [main](#symbol-main) — Запускает модуль или команду Python после настройки журналирования Launcher.

<a id="symbol-servicefilehandler"></a>

## `ServiceFileHandler`

[media_manager/service_runtime.py:17](../../media_manager/service_runtime.py#L17)

Останавливает рекурсивное журналирование при ошибке записи файла журнала. Базовые типы: RotatingFileHandler.

Базовые классы: `RotatingFileHandler`.


Именованные методы: `handleError`.

<a id="symbol-servicefilehandler-handleerror"></a>

## `ServiceFileHandler.handleError`

[media_manager/service_runtime.py:20](../../media_manager/service_runtime.py#L20)

Фиксирует отказ обработчика без повторного вывода в перенаправленный stderr. Обновляет состояние объекта: failed.

```python
def handleError(self, record)
```

Присваивания полям `self`: `failed`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-servicelogstream"></a>

## `ServiceLogStream`

[media_manager/service_runtime.py:28](../../media_manager/service_runtime.py#L28)

Перенаправляет текстовый вывод сервиса в ограниченный ротируемый журнал. Зависимости конструктора: path.

Базовые классы: `io.TextIOBase`.


Состояние, присваиваемое конструктором: `chunk_size`, `handler`.

Именованные методы: `__init__`, `encoding`, `writable`, `write`, `flush`.

<a id="symbol-servicelogstream---init--"></a>

## `ServiceLogStream.__init__`

[media_manager/service_runtime.py:31](../../media_manager/service_runtime.py#L31)

Инициализирует ServiceLogStream и его рабочее состояние. Обновляет состояние объекта: chunk_size, handler.

```python
def __init__(self, path, *, max_bytes=2 * 1024 * 1024, backups=3)
```

Присваивания полям `self`: `chunk_size`, `handler`.

Прямые выражения вызова: [ServiceFileHandler](../../media_manager/service_runtime.py#L17), `logging.Formatter`, `max`, `min`, `self.handler.setFormatter`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-servicelogstream-encoding"></a>

## `ServiceLogStream.encoding`

[media_manager/service_runtime.py:41](../../media_manager/service_runtime.py#L41)

Объявляет UTF-8 как кодировку текстового потока журнала. Возвращает локальное значение без обращения к файловой системе.

```python
def encoding(self)
```

Декораторы: `property`.

Выражения возврата (ветви, без исполнения):

- `'utf-8'`


<a id="symbol-servicelogstream-writable"></a>

## `ServiceLogStream.writable`

[media_manager/service_runtime.py:46](../../media_manager/service_runtime.py#L46)

Сообщает, что поток принимает текст для записи в журнал. Возвращает локальное значение без обращения к файловой системе.

```python
def writable(self)
```

Выражения возврата (ветви, без исполнения):

- `True`


<a id="symbol-servicelogstream-write"></a>

## `ServiceLogStream.write`

[media_manager/service_runtime.py:51](../../media_manager/service_runtime.py#L51)

Разбивает текст на ограниченные блоки и передаёт файловому обработчику. Использует logging.LogRecord, self.handler.handle.

```python
def write(self, text)
```

Прямые выражения вызова: `len`, `logging.LogRecord`, `range`, `self.handler.handle`.

Выражения возврата (ветви, без исполнения):

- `len(text)`


<a id="symbol-servicelogstream-flush"></a>

## `ServiceLogStream.flush`

[media_manager/service_runtime.py:61](../../media_manager/service_runtime.py#L61)

Сбрасывает буфер файлового обработчика журнала. Использует self.handler.flush.

```python
def flush(self)
```

Прямые выражения вызова: `self.handler.flush`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-configure-logging"></a>

## `configure_logging`

[media_manager/service_runtime.py:70](../../media_manager/service_runtime.py#L70)

Настраивает журналы stdout/stderr и диагностические стеки выбранного сервиса. Явно отклоняет недопустимое состояние через ValueError.

```python
def configure_logging(service)
```

Прямые выражения вызова: `Path`, `Path(__file__).resolve`, `Path(os.environ.get('MEDIA_ACTU_DATA_DIR', str(default))).expanduser`, [ServiceLogStream](../../media_manager/service_runtime.py#L28), `ValueError`, `_diagnostic_files.append`, `directory.mkdir`, `faulthandler.enable`, `faulthandler.register`, `hasattr`, `os.environ.get`, `stacks.exists`, `stacks.open`, `stacks.replace`, `stacks.stat`, `stacks.with_suffix`, `str`.

Явные `raise`:

- `ValueError('Expected core or ui service')`

Выражения возврата (ветви, без исполнения):

- `stream`


<a id="symbol-main"></a>

## `main`

[media_manager/service_runtime.py:91](../../media_manager/service_runtime.py#L91)

Запускает модуль или команду Python после настройки журналирования Launcher. Явно отклоняет недопустимое состояние через SystemExit.

```python
def main()
```

Прямые выражения вызова: `SystemExit`, `compile`, [configure_logging](../../media_manager/service_runtime.py#L70), `exec`, `len`, `runpy.run_module`.

Явные `raise`:

- `SystemExit('Usage: service_runtime core&#124;ui -m MODULE [ARGS] &#124; -c CODE [ARGS]')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
