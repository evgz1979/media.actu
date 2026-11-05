# Нативные определения

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

Разбор языков, владения ресурсами, протокола и UI приведён в [подробном руководстве](../development/native.md).

## Оглавление

- [media_manager.video_frame.m.DescriptorLoader](#symbol-media_manager.video_frame.m.DescriptorLoader) — Передаёт AVFoundation диапазоны уже проверенного файлового дескриптора.
- [media_manager.video_frame.m.DescriptorLoader.resourceLoader:shouldWaitForLoadingOfRequestedResource:](#symbol-media_manager.video_frame.m.DescriptorLoader.resourceLoader%3AshouldWaitForLoadingOfRequestedResource%3A) — Отвечает на запрос диапазона байтов через pread без изменения позиции дескриптора.
- [media_manager.video_frame.m.main](#symbol-media_manager.video_frame.m.main) — Извлекает первый кадр видео и возвращает JPEG через stdout.
- [paired_tree.js.beforeUnmount](#symbol-paired_tree.js.beforeUnmount) — Освобождает ResizeObserver при удалении компонента дерева.
- [paired_tree.js.computed.start](#symbol-paired_tree.js.computed.start) — Вычисляет индекс первой отображаемой строки с запасом перед видимой областью.
- [paired_tree.js.computed.visible](#symbol-paired_tree.js.computed.visible) — Выбирает небольшой срез строк вокруг текущей прокрутки.
- [paired_tree.js.data](#symbol-paired_tree.js.data) — Создаёт локальное состояние видимой области, выбора и подписей решений.
- [paired_tree.js.methods.keyDown](#symbol-paired_tree.js.methods.keyDown) — Перемещает выделение стрелками вверх и вниз и удерживает строку в viewport.
- [paired_tree.js.methods.pick](#symbol-paired_tree.js.methods.pick) — Выбирает строку мышью и передаёт path/side серверному обработчику.
- [paired_tree.js.methods.resetScroll](#symbol-paired_tree.js.methods.resetScroll) — Возвращает список к верхней строке и согласует вторую сторону пары.
- [paired_tree.js.methods.scrolled](#symbol-paired_tree.js.methods.scrolled) — Сохраняет положение viewport и синхронизирует вертикальную прокрутку пары.
- [paired_tree.js.methods.setSelection](#symbol-paired_tree.js.methods.setSelection) — Обновляет локальное выделение по команде Python-обёртки.
- [paired_tree.js.methods.status](#symbol-paired_tree.js.methods.status) — Выбирает пользовательскую подпись статуса строки для данной стороны пары.
- [paired_tree.js.mounted](#symbol-paired_tree.js.mounted) — Подписывает viewport на изменение размера и прокручивает длинный путь к концу.
- [paired_tree.js.watch.rows](#symbol-paired_tree.js.watch.rows) — Сбрасывает клавиатурную позицию при замене списка строк.
- [paired_tree.js.watch.selected](#symbol-paired_tree.js.watch.selected) — Принимает выбранный сервером путь и согласует локальное выделение.
- [photos_adapter.export.applescript.run](#symbol-photos_adapter.export.applescript.run) — Сохраняет прежний сценарий экспорта производной версии объекта Photos.
- [photos_adapter.main.m.LibraryState](#symbol-photos_adapter.main.m.LibraryState) — Хранит сигнал недоступности текущей медиатеки для одного клиента службы.
- [photos_adapter.main.m.LibraryState.photoLibraryDidBecomeUnavailable:](#symbol-photos_adapter.main.m.LibraryState.photoLibraryDidBecomeUnavailable%3A) — Помечает текущую медиатеку недоступной после уведомления PhotoKit.
- [photos_adapter.main.m.assetName](#symbol-photos_adapter.main.m.assetName) — Выбирает исходное имя фото или видео из ресурсов объекта Photos.
- [photos_adapter.main.m.assetVersion](#symbol-photos_adapter.main.m.assetVersion) — Получает версию объекта по modificationDate либо creationDate.
- [photos_adapter.main.m.authorization](#symbol-photos_adapter.main.m.authorization) — Читает разрешение PhotoKit и при запросе показывает системный диалог.
- [photos_adapter.main.m.canRead](#symbol-photos_adapter.main.m.canRead) — Проверяет, допускает ли статус чтение объектов Photos.
- [photos_adapter.main.m.cancelled](#symbol-photos_adapter.main.m.cancelled) — Без блокировки проверяет входной канал на quit, cancel или закрытие клиента.
- [photos_adapter.main.m.handleRequest](#symbol-photos_adapter.main.m.handleRequest) — Проверяет доступ и якоря, затем выполняет короткий запрос PhotoKit.
- [photos_adapter.main.m.main](#symbol-photos_adapter.main.m.main) — Выбирает режим запуска PhotoKit-helper и инициализирует GUI-сеанс AppKit.
- [photos_adapter.main.m.originalRequest](#symbol-photos_adapter.main.m.originalRequest) — Передаёт манифест или один оригинальный ресурс событиями протокола v2.
- [photos_adapter.main.m.originalResources](#symbol-photos_adapter.main.m.originalResources) — Выбирает исходные фото, видео, звук, RAW-вариант и движение Live Photo.
- [photos_adapter.main.m.resourceID](#symbol-photos_adapter.main.m.resourceID) — Кодирует ID ресурса как тип и порядковый номер среди ресурсов того же типа.
- [photos_adapter.main.m.scanCommand](#symbol-photos_adapter.main.m.scanCommand) — Сохраняет одноразовую CLI-команду перечисления медиаобъектов Photos.
- [photos_adapter.main.m.serve](#symbol-photos_adapter.main.m.serve) — Обслуживает последовательные JSON-запросы одного клиентского соединения.
- [photos_adapter.main.m.serveDefaultSocket](#symbol-photos_adapter.main.m.serveDefaultSocket) — Создаёт приватный endpoint пользователя и удерживает единственную блокировку службы.
- [photos_adapter.main.m.serveSocket](#symbol-photos_adapter.main.m.serveSocket) — Принимает несколько локальных клиентов Unix-сокета и обслуживает их независимо.
- [photos_adapter.main.m.statusCommand](#symbol-photos_adapter.main.m.statusCommand) — Обслуживает одноразовую команду проверки или запроса разрешения.
- [photos_adapter.main.m.statusName](#symbol-photos_adapter.main.m.statusName) — Преобразует PHAuthorizationStatus в строковый статус протокола.
- [photos_adapter.main.m.thumbnailCommand](#symbol-photos_adapter.main.m.thumbnailCommand) — Сохраняет CLI-режим создания миниатюры в заданный выходной путь.
- [photos_adapter.main.m.writeJSON](#symbol-photos_adapter.main.m.writeJSON) — Отправляет один JSON-объект с переводом строки и немедленным fflush.
- [photos_adapter.open.applescript.run](#symbol-photos_adapter.open.applescript.run) — Выделяет объект по ID в системном приложении Photos без экспорта.
- [photos_adapter.scan.js.module](#symbol-photos_adapter.scan.js.module) — Прежний JXA-скрипт собирает метаданные всех объектов через scripting API Photos.

<a id="symbol-media_manager.video_frame.m.DescriptorLoader"></a>

## `media_manager.video_frame.m.DescriptorLoader`

[media_manager/video_frame.m](../../media_manager/video_frame.m)

Передаёт AVFoundation диапазоны уже проверенного файлового дескриптора. Декодер не открывает исходный путь повторно и не следует заменённым ссылкам.

```text
@ interface DescriptorLoader : NSObject < AVAssetResourceLoaderDelegate >
```


<a id="symbol-media_manager.video_frame.m.DescriptorLoader.resourceLoader:shouldWaitForLoadingOfRequestedResource:"></a>

## `media_manager.video_frame.m.DescriptorLoader.resourceLoader:shouldWaitForLoadingOfRequestedResource:`

[media_manager/video_frame.m](../../media_manager/video_frame.m)

Отвечает на запрос диапазона байтов через pread без изменения позиции дескриптора. Ограничивает чтение длиной файла и завершает запрос ошибкой при неполном чтении.

```text
- ( BOOL ) resourceLoader : ( AVAssetResourceLoader * ) loader shouldWaitForLoadingOfRequestedResource : ( AVAssetResourceLoadingRequest * ) request
```


<a id="symbol-media_manager.video_frame.m.main"></a>

## `media_manager.video_frame.m.main`

[media_manager/video_frame.m](../../media_manager/video_frame.m)

Извлекает первый кадр видео и возвращает JPEG через stdout. Получает FD, ширину, высоту и расширение; сохраняет ориентацию и пределы размера.

```text
int main ( int argc , const char * argv [ ] )
```


<a id="symbol-paired_tree.js.beforeUnmount"></a>

## `paired_tree.js.beforeUnmount`

[paired_tree.js](../../paired_tree.js)

Освобождает ResizeObserver при удалении компонента дерева. Не оставляет наблюдатель привязанным к удалённому DOM-элементу.

```text
beforeUnmount ( )
```


<a id="symbol-paired_tree.js.computed.start"></a>

## `paired_tree.js.computed.start`

[paired_tree.js](../../paired_tree.js)

Вычисляет индекс первой отображаемой строки с запасом перед видимой областью. Высота строки 28 px, запас составляет восемь строк.

```text
start ( )
```


<a id="symbol-paired_tree.js.computed.visible"></a>

## `paired_tree.js.computed.visible`

[paired_tree.js](../../paired_tree.js)

Выбирает небольшой срез строк вокруг текущей прокрутки. К высоте viewport добавляет 16 строк запаса для плавного перемещения.

```text
visible ( )
```


<a id="symbol-paired_tree.js.data"></a>

## `paired_tree.js.data`

[paired_tree.js](../../paired_tree.js)

Создаёт локальное состояние видимой области, выбора и подписей решений. Серверные строки поступают через props; локальный курсор отвечает за клавиатуру.

```text
data ( )
```


<a id="symbol-paired_tree.js.methods.keyDown"></a>

## `paired_tree.js.methods.keyDown`

[paired_tree.js](../../paired_tree.js)

Перемещает выделение стрелками вверх и вниз и удерживает строку в viewport. Игнорирует модификаторы, ввод текста, IME и открытые меню; отправляет keyboard=true.

```text
keyDown ( event )
```


<a id="symbol-paired_tree.js.methods.pick"></a>

## `paired_tree.js.methods.pick`

[paired_tree.js](../../paired_tree.js)

Выбирает строку мышью и передаёт path/side серверному обработчику. Сбрасывает отдельный клавиатурный курсор, сохраняя локальное выделение.

```text
pick ( row )
```


<a id="symbol-paired_tree.js.methods.resetScroll"></a>

## `paired_tree.js.methods.resetScroll`

[paired_tree.js](../../paired_tree.js)

Возвращает список к верхней строке и согласует вторую сторону пары. Повторно вычисляет top через общий обработчик scrolled.

```text
resetScroll ( )
```


<a id="symbol-paired_tree.js.methods.scrolled"></a>

## `paired_tree.js.methods.scrolled`

[paired_tree.js](../../paired_tree.js)

Сохраняет положение viewport и синхронизирует вертикальную прокрутку пары. Обновляет соседний список только при расхождении более одного пикселя.

```text
scrolled ( )
```


<a id="symbol-paired_tree.js.methods.setSelection"></a>

## `paired_tree.js.methods.setSelection`

[paired_tree.js](../../paired_tree.js)

Обновляет локальное выделение по команде Python-обёртки. Путь должен соответствовать строке; функция сама не отправляет select.

```text
setSelection ( path )
```


<a id="symbol-paired_tree.js.methods.status"></a>

## `paired_tree.js.methods.status`

[paired_tree.js](../../paired_tree.js)

Выбирает пользовательскую подпись статуса строки для данной стороны пары. Отсутствующая сторона и непрочитанные элементы различаются явно.

```text
status ( row )
```


<a id="symbol-paired_tree.js.mounted"></a>

## `paired_tree.js.mounted`

[paired_tree.js](../../paired_tree.js)

Подписывает viewport на изменение размера и прокручивает длинный путь к концу. ResizeObserver поддерживает актуальную высоту среза без полной отрисовки списка.

```text
mounted ( )
```


<a id="symbol-paired_tree.js.watch.rows"></a>

## `paired_tree.js.watch.rows`

[paired_tree.js](../../paired_tree.js)

Сбрасывает клавиатурную позицию при замене списка строк. Новая выборка должна повторно найти текущий путь перед перемещением.

```text
rows ( )
```


<a id="symbol-paired_tree.js.watch.selected"></a>

## `paired_tree.js.watch.selected`

[paired_tree.js](../../paired_tree.js)

Принимает выбранный сервером путь и согласует локальное выделение. Сбрасывает курсор только при отсутствии фокуса внутри viewport.

```text
selected ( value )
```


<a id="symbol-photos_adapter.export.applescript.run"></a>

## `photos_adapter.export.applescript.run`

[photos_adapter/export.applescript](../../photos_adapter/export.applescript)

Сохраняет прежний сценарий экспорта производной версии объекта Photos. Текущих вызовов в проекте не найдено; скрипт сохранён для описания старой реализации.

```text
on run arguments
```


<a id="symbol-photos_adapter.main.m.LibraryState"></a>

## `photos_adapter.main.m.LibraryState`

[photos_adapter/main.m](../../photos_adapter/main.m)

Хранит сигнал недоступности текущей медиатеки для одного клиента службы. Реализует PHPhotoLibraryAvailabilityObserver; флаг читается между шагами запросов.

```text
@ interface LibraryState : NSObject < PHPhotoLibraryAvailabilityObserver >
```


<a id="symbol-photos_adapter.main.m.LibraryState.photoLibraryDidBecomeUnavailable:"></a>

## `photos_adapter.main.m.LibraryState.photoLibraryDidBecomeUnavailable:`

[photos_adapter/main.m](../../photos_adapter/main.m)

Помечает текущую медиатеку недоступной после уведомления PhotoKit. Последующие проверки прерывают запрос с явным статусом unavailable.

```text
- ( void ) photoLibraryDidBecomeUnavailable : ( PHPhotoLibrary * ) library
```


<a id="symbol-photos_adapter.main.m.assetName"></a>

## `photos_adapter.main.m.assetName`

[photos_adapter/main.m](../../photos_adapter/main.m)

Выбирает исходное имя фото или видео из ресурсов объекта Photos. При отсутствии подходящего ресурса использует первый ресурс или localIdentifier.

```text
static NSString * assetName ( PHAsset * asset )
```


<a id="symbol-photos_adapter.main.m.assetVersion"></a>

## `photos_adapter.main.m.assetVersion`

[photos_adapter/main.m](../../photos_adapter/main.m)

Получает версию объекта по modificationDate либо creationDate. Возвращает время с шестью знаками после точки для квитанций ресурсов Core.

```text
static NSString * assetVersion ( PHAsset * asset )
```


<a id="symbol-photos_adapter.main.m.authorization"></a>

## `photos_adapter.main.m.authorization`

[photos_adapter/main.m](../../photos_adapter/main.m)

Читает разрешение PhotoKit и при запросе показывает системный диалог. Во время ожидания поддерживает главный NSRunLoop для ответа macOS.

```text
static PHAuthorizationStatus authorization ( BOOL request )
```


<a id="symbol-photos_adapter.main.m.canRead"></a>

## `photos_adapter.main.m.canRead`

[photos_adapter/main.m](../../photos_adapter/main.m)

Проверяет, допускает ли статус чтение объектов Photos. Принимает только authorized и limited; остальные состояния отклоняются.

```text
static BOOL canRead ( PHAuthorizationStatus status )
```


<a id="symbol-photos_adapter.main.m.cancelled"></a>

## `photos_adapter.main.m.cancelled`

[photos_adapter/main.m](../../photos_adapter/main.m)

Без блокировки проверяет входной канал на quit, cancel или закрытие клиента. Отмена принимается для token текущего потока; прочая строка не останавливает передачу.

```text
static BOOL cancelled ( FILE * input , NSString * token )
```


<a id="symbol-photos_adapter.main.m.handleRequest"></a>

## `photos_adapter.main.m.handleRequest`

[photos_adapter/main.m](../../photos_adapter/main.m)

Проверяет доступ и якоря, затем выполняет короткий запрос PhotoKit. Обслуживает authorize, probe, scan, guard и локальное JPEG-превью thumbnail.

```text
static NSDictionary * handleRequest ( NSDictionary * request , LibraryState * state )
```


<a id="symbol-photos_adapter.main.m.main"></a>

## `photos_adapter.main.m.main`

[photos_adapter/main.m](../../photos_adapter/main.m)

Выбирает режим запуска PhotoKit-helper и инициализирует GUI-сеанс AppKit. Без аргументов запускает службу; SIGPIPE отключён для безопасного закрытия клиента.

```text
int main ( int argc , const char * argv [ ] )
```


<a id="symbol-photos_adapter.main.m.originalRequest"></a>

## `photos_adapter.main.m.originalRequest`

[photos_adapter/main.m](../../photos_adapter/main.m)

Передаёт манифест или один оригинальный ресурс событиями протокола v2. Данные идут блоками до 256 КиБ; helper не получает путей назначения и не пишет оригиналы.

```text
static void originalRequest ( NSDictionary * request , LibraryState * state , FILE * input , FILE * output )
```


<a id="symbol-photos_adapter.main.m.originalResources"></a>

## `photos_adapter.main.m.originalResources`

[photos_adapter/main.m](../../photos_adapter/main.m)

Выбирает исходные фото, видео, звук, RAW-вариант и движение Live Photo. Сортирует ресурсы по типу, исходному имени и UTI для устойчивых ID.

```text
static NSArray < PHAssetResource * > * originalResources ( PHAsset * asset )
```


<a id="symbol-photos_adapter.main.m.resourceID"></a>

## `photos_adapter.main.m.resourceID`

[photos_adapter/main.m](../../photos_adapter/main.m)

Кодирует ID ресурса как тип и порядковый номер среди ресурсов того же типа. Нумерация зависит от предварительной устойчивой сортировки originalResources.

```text
static NSString * resourceID ( PHAssetResource * resource , NSArray * resources , NSUInteger index )
```


<a id="symbol-photos_adapter.main.m.scanCommand"></a>

## `photos_adapter.main.m.scanCommand`

[photos_adapter/main.m](../../photos_adapter/main.m)

Сохраняет одноразовую CLI-команду перечисления медиаобъектов Photos. Текущий Python-клиент использует op=scan постоянной службы вместо этого режима.

```text
static int scanCommand ( void )
```


<a id="symbol-photos_adapter.main.m.serve"></a>

## `photos_adapter.main.m.serve`

[photos_adapter/main.m](../../photos_adapter/main.m)

Обслуживает последовательные JSON-запросы одного клиентского соединения. Регистрирует наблюдатель доступности Photos и снимает его после закрытия канала.

```text
static int serve ( FILE * input , FILE * output )
```


<a id="symbol-photos_adapter.main.m.serveDefaultSocket"></a>

## `photos_adapter.main.m.serveDefaultSocket`

[photos_adapter/main.m](../../photos_adapter/main.m)

Создаёт приватный endpoint пользователя и удерживает единственную блокировку службы. Только владелец service.lock удаляет устаревший photos.sock перед запуском.

```text
static int serveDefaultSocket ( void )
```


<a id="symbol-photos_adapter.main.m.serveSocket"></a>

## `photos_adapter.main.m.serveSocket`

[photos_adapter/main.m](../../photos_adapter/main.m)

Принимает несколько локальных клиентов Unix-сокета и обслуживает их независимо. Проверяет UID клиента; без подключений завершает службу после 30 секунд простоя.

```text
static int serveSocket ( NSString * path )
```


<a id="symbol-photos_adapter.main.m.statusCommand"></a>

## `photos_adapter.main.m.statusCommand`

[photos_adapter/main.m](../../photos_adapter/main.m)

Обслуживает одноразовую команду проверки или запроса разрешения. Печатает JSON количества объектов; отказ после запроса возвращает код 2.

```text
static int statusCommand ( BOOL request )
```


<a id="symbol-photos_adapter.main.m.statusName"></a>

## `photos_adapter.main.m.statusName`

[photos_adapter/main.m](../../photos_adapter/main.m)

Преобразует PHAuthorizationStatus в строковый статус протокола. Не запрашивает разрешение и не читает объекты медиатеки.

```text
static NSString * statusName ( PHAuthorizationStatus status )
```


<a id="symbol-photos_adapter.main.m.thumbnailCommand"></a>

## `photos_adapter.main.m.thumbnailCommand`

[photos_adapter/main.m](../../photos_adapter/main.m)

Сохраняет CLI-режим создания миниатюры в заданный выходной путь. Текущий UI получает JPEG через протокол службы; это отдельный доступный режим CLI.

```text
static int thumbnailCommand ( NSArray < NSString * > * arguments )
```


<a id="symbol-photos_adapter.main.m.writeJSON"></a>

## `photos_adapter.main.m.writeJSON`

[photos_adapter/main.m](../../photos_adapter/main.m)

Отправляет один JSON-объект с переводом строки и немедленным fflush. Блокирует FILE на время записи, чтобы события разных callback не смешивались.

```text
static BOOL writeJSON ( id value , FILE * stream )
```


<a id="symbol-photos_adapter.open.applescript.run"></a>

## `photos_adapter.open.applescript.run`

[photos_adapter/open.applescript](../../photos_adapter/open.applescript)

Выделяет объект по ID в системном приложении Photos без экспорта. Используется SystemPhotosAdapter.open_asset; принимает один assetIdentifier.

```text
on run arguments
```


<a id="symbol-photos_adapter.scan.js.module"></a>

## `photos_adapter.scan.js.module`

[photos_adapter/scan.js](../../photos_adapter/scan.js)

Прежний JXA-скрипт собирает метаданные всех объектов через scripting API Photos. Вызывается только сохранённым _applescript_scan, до которого текущих вызовов не найдено.

```text
const photos = Application ( 'Photos' ) ;
```
