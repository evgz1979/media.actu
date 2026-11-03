# JavaScript, Objective-C, JXA и AppleScript

Этот документ дополняет Python-справочник всеми именованными функциями и методами
нативных исходников. Blocks Objective-C и анонимные arrow-callback описаны через
владельца и протокол, поскольку отдельного имени определения у них нет.

## PhotoKit-helper: типы и время жизни

Исходник [photos_adapter/main.m](../../photos_adapter/main.m) импортирует AppKit,
Foundation, Photos и POSIX IPC. `NSString *`, `NSDictionary *`, `NSArray *` — ссылки
на объекты; `@{...}` и `@[...]` создают коллекции, `@(number)` упаковывает число
в объект для JSON. ARC освобождает Objective-C-объекты, но файловые дескрипторы,
FILE*, сокеты и malloc/getline-буферы освобождаются явно через close/fclose/free.

`@autoreleasepool` ограничивает время жизни временных объектов больших обходов.
`__block` позволяет callback менять общий счётчик/флаг, но само не даёт взаимного
исключения. Для ожидаемого завершения PhotoKit-запроса используется dispatch_semaphore,
для полных JSON-строк — flockfile/funlockfile, для числа клиентов — NSLock.
Главный NSRunLoop продолжает работу, пока серверные соединения обслуживаются в
глобальных dispatch-очередях.

`LibraryState : NSObject<PHPhotoLibraryAvailabilityObserver>` содержит atomic BOOL
unavailable. Метод photoLibraryDidBecomeUnavailable переводит флаг в YES;
последующие запросы и проверки потока возвращают unavailable. Atomic-свойство
относится к флагу, а не делает весь протокол одной атомарной операцией.

## Все C-функции PhotoKit-helper

| Определение | Назначение и контракт |
| --- | --- |
| [`statusName`](../../photos_adapter/main.m#L16) | Преобразует PHAuthorizationStatus в строковый статус протокола. Не запрашивает разрешение и не читает объекты медиатеки. |
| [`authorization`](../../photos_adapter/main.m#L29) | Читает разрешение PhotoKit и при запросе показывает системный диалог. Во время ожидания поддерживает главный NSRunLoop для ответа macOS. |
| [`canRead`](../../photos_adapter/main.m#L50) | Проверяет, допускает ли статус чтение объектов Photos. Принимает только authorized и limited; остальные состояния отклоняются. |
| [`writeJSON`](../../photos_adapter/main.m#L57) | Отправляет один JSON-объект с переводом строки и немедленным fflush. Блокирует FILE на время записи, чтобы события разных callback не смешивались. |
| [`assetName`](../../photos_adapter/main.m#L79) | Выбирает исходное имя фото или видео из ресурсов объекта Photos. При отсутствии подходящего ресурса использует первый ресурс или localIdentifier. |
| [`statusCommand`](../../photos_adapter/main.m#L94) | Обслуживает одноразовую команду проверки или запроса разрешения. Печатает JSON количества объектов; отказ после запроса возвращает код 2. |
| [`scanCommand`](../../photos_adapter/main.m#L103) | Сохраняет одноразовую CLI-команду перечисления медиаобъектов Photos. Текущий Python-клиент использует op=scan постоянной службы вместо этого режима. |
| [`thumbnailCommand`](../../photos_adapter/main.m#L145) | Сохраняет CLI-режим создания миниатюры в заданный выходной путь. Текущий UI получает JPEG через протокол службы; это отдельный доступный режим CLI. |
| [`handleRequest`](../../photos_adapter/main.m#L199) | Проверяет доступ и якоря, затем выполняет короткий запрос PhotoKit. Обслуживает authorize, probe, scan, guard и локальное JPEG-превью thumbnail. |
| [`assetVersion`](../../photos_adapter/main.m#L281) | Получает версию объекта по modificationDate либо creationDate. Возвращает время с шестью знаками после точки для квитанций ресурсов Core. |
| [`originalResources`](../../photos_adapter/main.m#L287) | Выбирает исходные фото, видео, звук, RAW-вариант и движение Live Photo. Сортирует ресурсы по типу, исходному имени и UTI для устойчивых ID. |
| [`resourceID`](../../photos_adapter/main.m#L302) | Кодирует ID ресурса как тип и порядковый номер среди ресурсов того же типа. Нумерация зависит от предварительной устойчивой сортировки originalResources. |
| [`cancelled`](../../photos_adapter/main.m#L310) | Без блокировки проверяет входной канал на quit, cancel или закрытие клиента. Отмена принимается для token текущего потока; прочая строка не останавливает передачу. |
| [`originalRequest`](../../photos_adapter/main.m#L324) | Передаёт манифест или один оригинальный ресурс событиями протокола v2. Данные идут блоками до 256 КиБ; helper не получает путей назначения и не пишет оригиналы. |
| [`serve`](../../photos_adapter/main.m#L409) | Обслуживает последовательные JSON-запросы одного клиентского соединения. Регистрирует наблюдатель доступности Photos и снимает его после закрытия канала. |
| [`serveSocket`](../../photos_adapter/main.m#L442) | Принимает несколько локальных клиентов Unix-сокета и обслуживает их независимо. Проверяет UID клиента; без подключений завершает службу после 30 секунд простоя. |
| [`serveDefaultSocket`](../../photos_adapter/main.m#L489) | Создаёт приватный endpoint пользователя и удерживает единственную блокировку службы. Только владелец service.lock удаляет устаревший photos.sock перед запуском. |
| [`main`](../../photos_adapter/main.m#L510) | Выбирает режим запуска PhotoKit-helper и инициализирует GUI-сеанс AppKit. Без аргументов запускает службу; SIGPIPE отключён для безопасного закрытия клиента. |

Режим запуска без аргументов — service. Дополнительные CLI-команды: check/status,
scan, thumbnail, serve(stdin/stdout), serve-socket. Наличие команды в main делает
её явной точкой входа, даже если нынешний UI использует другой транспорт.
NDJSON-запросы, resource ID и отмена разобраны в [протоколе](photos-protocol.md).

Текущий SDK macOS 27 помечает используемый `PHAssetResource.originalFilename`
как deprecated и рекомендует `filename`. Синтаксическая проверка helper проходит
с пятью предупреждениями в местах выбора и сортировки имён ресурсов. Это действующий
код с устаревающим API, а не неиспользуемая функция; миграция API этой задачей не выполнялась.

## Нативный кадр видео

[media_manager/video_frame.m](../../media_manager/video_frame.m) использует AVFoundation,
ImageIO и UniformTypeIdentifiers. `DescriptorLoader` реализует
AVAssetResourceLoaderDelegate: отвечает на диапазоны байтов через pread проверенного
read-only FD, не открывая повторно исходный pathname. Буфер чтения — 65536 байт.
Ошибки чтения завершают resource request с NSPOSIXErrorDomain.

[`main`](../../media_manager/video_frame.m#L48) принимает четыре аргумента после имени процесса:
FD, максимальную ширину, максимальную высоту и расширение. Создаёт AVURLAsset со
служебной схемой media-actu, подключает loader, получает кадр kCMTimeZero,
учитывает preferredTrackTransform и возвращает JPEG в stdout. Коды отказа:
2 — аргументы/fstat, 3 — нет кадра, 4 — нет JPEG destination, 5 — finalize,
6 — неполная запись stdout. Helper не записывает оригинал.

Python строит имя бинарника по хешу исходника, компилирует его в кэше и передаёт FD
через subprocess pass_fds. FFmpeg, если доступен, используется первым. Размеры
storage-preview: 320×240 либо 1600×1200 с сохранением пропорций.
Код: [`StoragePreviewService._video_frame`](../../media_manager/storage_previews.py#L115).

## Vue-компонент связанных деревьев

[paired_tree.js](../../paired_tree.js) экспортирует объект компонента с template,
props, emits, data, watch, computed и lifecycle hooks. Props описывают серверные
rows/side/selected/empty_text/root_file_count/root_files_open/sizes. `$emit`
передаёт события Python через NiceGUI, а `$refs.viewport` указывает DOM-контейнер.
Optional chaining `?.` безопасно обрабатывает отсутствующий DOM-элемент;
nullish coalescing `??` выбирает клавиатурный курсор либо текущее выделение.

| Метод или hook | Назначение и контракт |
| --- | --- |
| [`data`](../../paired_tree.js#L49) | Создаёт локальное состояние видимой области, выбора и подписей решений. Серверные строки поступают через props; локальный курсор отвечает за клавиатуру. |
| [`start`](../../paired_tree.js#L63) | Вычисляет индекс первой отображаемой строки с запасом перед видимой областью. Высота строки 28 px, запас составляет восемь строк. |
| [`visible`](../../paired_tree.js#L66) | Выбирает небольшой срез строк вокруг текущей прокрутки. К высоте viewport добавляет 16 строк запаса для плавного перемещения. |
| [`mounted`](../../paired_tree.js#L70) | Подписывает viewport на изменение размера и прокручивает длинный путь к концу. ResizeObserver поддерживает актуальную высоту среза без полной отрисовки списка. |
| [`beforeUnmount`](../../paired_tree.js#L80) | Освобождает ResizeObserver при удалении компонента дерева. Не оставляет наблюдатель привязанным к удалённому DOM-элементу. |
| [`pick`](../../paired_tree.js#L15) | Выбирает строку мышью и передаёт path/side серверному обработчику. Сбрасывает отдельный клавиатурный курсор, сохраняя локальное выделение. |
| [`keyDown`](../../paired_tree.js#L91) | Перемещает выделение стрелками вверх и вниз и удерживает строку в viewport. Игнорирует модификаторы, ввод текста, IME и открытые меню; отправляет keyboard=true. |
| [`setSelection`](../../paired_tree.js#L110) | Обновляет локальное выделение по команде Python-обёртки. Путь должен соответствовать строке; функция сама не отправляет select. |
| [`resetScroll`](../../paired_tree.js#L113) | Возвращает список к верхней строке и согласует вторую сторону пары. Повторно вычисляет top через общий обработчик scrolled. |
| [`scrolled`](../../paired_tree.js#L105) | Сохраняет положение viewport и синхронизирует вертикальную прокрутку пары. Обновляет соседний список только при расхождении более одного пикселя. |
| [`status`](../../paired_tree.js#L41) | Выбирает пользовательскую подпись статуса строки для данной стороны пары. Отсутствующая сторона и непрочитанные элементы различаются явно. |

Дополнительные именованные watch-обработчики: `rows()` сбрасывает keyboardCursor
при новой выборке; `selected(value)` принимает серверный выбор и сбрасывает курсор
только когда фокус находится вне viewport. Анонимные callback ResizeObserver,
$nextTick, findIndex и обработчики template привязаны к этим владельцам.

Одна строка — 28 px. Computed-выборка добавляет запас вокруг viewport; виртуализация
уменьшает число DOM-узлов, но не размер уже полученного массива rows. Открытое
q-menu отправляет menu_state и удерживает сервер от нежелательной перерисовки.
Детали выбора и состояния: [документация UI](ui.md).

## JavaScript внутри Python-строк

В storage_ui.FOLDER_CLICK_JS хранится обработчик отличия одиночного/двойного клика:
DOM-элемент дерева переживает замену строк, предыдущий folder-key, время и координаты
удерживаются на tree. Порог — 500 мс и менее 6 px по каждой координате.
`emit` передаёт key/double серверу. Это действующий код, хотя он не отдельный `.js`.

workspace_ui содержит обработчики фокуса и клавиатуры обычного дерева, работу
sessionStorage и восстановление scroll через run_javascript. Парная версия этих
сценариев находится в Vue-компоненте. Для сравнения комментарий/код важно учитывать
строковые литералы: JavaScript внутри них является исполняемой частью приложения.

## AppleScript и JXA

| Файл | Вход | Поведение | Статус |
| --- | --- | --- | --- |
| [open.applescript](../../photos_adapter/open.applescript) | Один assetIdentifier | Находит объект, activate и spotlight в Photos | Действующий SystemPhotosAdapter.open_asset |
| [export.applescript](../../photos_adapter/export.applescript) | assetIdentifier и outputDirectory | export using originals false | Старый путь, текущих вызовов не найдено |
| [scan.js](../../photos_adapter/scan.js) | Запуск osascript -l JavaScript | Application('Photos'), массовое чтение метаданных, JSON | Вызывается только старым невызываемым _applescript_scan |

AppleScript получает список через `on run arguments`; ошибка отсутствующего объекта
переходит в ненулевой код osascript и затем PhotosAdapterError. JXA — JavaScript
for Automation, где Application — системный мост, а не браузерный глобальный объект.
Нельзя запускать его как обычный Node-скрипт ради проверки поведения.

Info.plist задаёт bundle ID и текст запроса разрешения; это конфигурация нативного
приложения, не Python-класс. Все старые файлы сохранены. Статусы совместимости:
[реестр старых частей](../legacy.md).
