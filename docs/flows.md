# Сквозные сценарии: от действия до результата

Каждый сценарий описывает нынешнюю цепочку вызовов. Полные аргументы и ветви ошибок
есть в [справочнике модулей](reference/README.md), HTTP-контракты — в [API](api.md).

## 1. Запуск Core и подключение UI

1. Launcher запускает `service_runtime`, который перенаправляет журналы и исполняет
   команду uvicorn или NiceGUI.
2. Импорт `app.py` создаёт службы, базы и недостающие таблицы; lifespan запускает
   наблюдение, проверку Photos, расписание и превью.
3. UI регистрирует главную; новый клиент создаёт StorageWorkspace и две BrowserPane.
4. UI получает тома, медиатеки и связи HTTP-запросами, проверяет sessionStorage
   и восстанавливает допустимое состояние навигации.

Код: [`main`](reference/media_manager--service_runtime.md#symbol-main), [`lifespan`](reference/app.md#symbol-lifespan),
[`StorageWorkspace.load`](reference/workspace_ui.md#symbol-StorageWorkspace.load), [`StorageWorkspace.restore_workspace`](reference/workspace_ui.md#symbol-StorageWorkspace.restore_workspace).
Закрытие браузера не останавливает Core; перезапуск Core сохраняет базы и кэш.

## 2. Открытие папки и работа отключённого тома

BrowserPane.show_volume меняет поколение выбранной области, сначала загружает
сохранённый список, рисует его и при доступности запускает refresh_open_folder.
StorageWorkspace.read_directory отправляет GET directory. StorageCatalog.directory
проверяет путь, том и необходимость живого чтения; успешный список сохраняет в directories.

Если живое чтение недоступно, прежний успешный снимок остаётся с cached/error.
Медленный ответ предыдущей области отбрасывается по generation. Раскрытие папки
загружает следующий уровень; обычный просмотр не запускает сверку всего носителя.

Код: [`BrowserPane.show_volume`](reference/workspace_ui.md#symbol-BrowserPane.show_volume),
[`StorageCatalog.directory`](reference/media_manager--storage.md#symbol-StorageCatalog.directory),
[`StorageCatalog._read_directory`](reference/media_manager--storage.md#symbol-StorageCatalog._read_directory).

## 3. Регистрация сменного носителя

Пользователь выбирает неподтверждённый сменный том и название. Core открывает
корень, проверяет device и исключительно создаёт `.media-actu-volume.json` с UUID.
После повторного обнаружения ID строится по маркеру, а не по usbshare или mount_path.
Старая история ресурса не переносится на новый носитель автоматически.

Код: [`StorageWorkspace.register_disk`](reference/workspace_ui.md#symbol-StorageWorkspace.register_disk),
[`StorageCatalog.register_removable`](reference/media_manager--storage.md#symbol-StorageCatalog.register_removable),
[`create_marker`](reference/media_manager--volume_identity.md#symbol-create_marker).
Повреждение, чужой маркер или дублирующийся ID должны дать явный отказ/неподтверждённость.

## 4. Основная папка, копия и служебное описание

Команда регистрации вызывает CopyCatalog.create_main или add_copy. В транзакции
проверяются том, известность папки, пересечения и номер; сохраняются связи и marker-job.
FolderMarkerService позднее записывает `.media-actu-folder.json`, проверяя ревизию
задания и принадлежность папки. Отключённый диск оставляет задание ожидающим.

Сама регистрация не доказывает наличие копии содержимого и не копирует медиа.
Изменение типа/номера меняет служебную метку, а не имя пользовательской папки.

Код: [`CopyCatalog.create_main`](reference/media_manager--copies.md#symbol-CopyCatalog.create_main),
[`CopyCatalog.add_copy`](reference/media_manager--copies.md#symbol-CopyCatalog.add_copy),
[`FolderMarkerService.reconcile`](reference/media_manager--folder_markers.md#symbol-FolderMarkerService.reconcile).

## 5. Связанная структура и проверка файлов

1. Выбор ссылки копии разрешает её актуальный источник; PairedWorkspace связывает панели.
2. «Папки» вызывает создание folders-отчёта. Core обходит стороны, сохраняет entries
   и выравнивает по точному относительному пути.
3. Завершённая структура позволяет создать files-отчёт с base_job_id. Связь и области
   должны соответствовать базовой проверке.
4. Метод size сравнивает тип, наличие и размер без чтения содержимого. Метод sha256
   дополнительно читает кандидатов равного размера с проверкой fingerprint.
5. Строки и счётчики сохраняются; UI грузит страницы и показывает их виртуальным деревом.

Код: [`PairedWorkspace.start`](reference/paired_workspace_ui.md#symbol-PairedWorkspace.start),
[`PairedComparisonCatalog.create`](reference/media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.create),
[`PairedComparisonCatalog.run`](reference/media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.run),
[`PairedComparisonCatalog._hash_pairs`](reference/media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._hash_pairs).
Ошибка каталога делает отсутствие внутри него неподтверждённым. Новая независимая
проверка не должна автоматически принимать старые решения о лишних файлах.

## 6. Подтверждённое копирование отсутствующего

UI запрашивает copy-plan по завершённому files-отчёту. План фиксирует missing_copy,
источник, назначения и версии файлов; полный состав доступен страницами. После
просмотра пользователь отдельно запускает start.

Core перепроверяет связь и корни, исполняет элементы по порядку, не трогает
существующие цели. Изменившийся источник отклоняется; новая конкурентная цель
сохраняется как skipped. Остановка оставляет готовые файлы. Прямая незавершённая
запись сохраняется с отметкой и не становится same_size без учёта журнала.

После результата Core при допустимых условиях создаёт новую size-сверку и записывает
verification_id. Если пересверка не создалась, сообщение предлагает обновить её вручную.
Старые отчёты и планы не переписываются новым результатом.

Код: [`PairedWorkspace.prepare_copy`](reference/paired_workspace_ui.md#symbol-PairedWorkspace.prepare_copy),
[`MissingCopyCatalog.plan`](reference/media_manager--copy_files.md#symbol-MissingCopyCatalog.plan),
[`MissingCopyCatalog.run`](reference/media_manager--copy_files.md#symbol-MissingCopyCatalog.run).

## 7. Общий поиск имён и прежние отчёты

В диалоге прежних отчётов выбираются исходная область и цели. ComparisonCatalog
проверяет пересечения и создаёт mode=names. Подходящие завершённые списки могут
использоваться повторно; при отключённом reuse_index выполняется новый обход.
NFC/casefold объединяет регистр и формы Unicode; для файлов учитывается имя
непосредственного родителя, а не весь относительный путь пары.

Если найдено имя в другой папке, это отдельный статус other_folder. Отсутствие
можно подтвердить лишь при полном целевом индексе; иначе unverified. Исторический
mode=content читается как прежний отчёт. Нажатие продолжения создаёт новую
names-сверку, не переписывая смысл старых результатов.

Код: [`ComparisonCatalog.run`](reference/media_manager--comparison.md#symbol-ComparisonCatalog.run),
[`ComparisonCatalog._classify_names`](reference/media_manager--comparison.md#symbol-ComparisonCatalog._classify_names),
[`ComparisonCatalog.resume`](reference/media_manager--comparison.md#symbol-ComparisonCatalog.resume).

## 8. Открытие Photos и построение превью

При подключении PhotoLibraries собирает якоря профилей и выполняет probe.
Однозначно найденная медиатека становится active/ready. Её сохранённые годы/месяцы
показывает PhotosBrowser без вызова PhotoKit. Открытая папка повышает приоритет JPEG,
но HTTP не экспортирует оригинал и не создаёт превью синхронно.

Photos-воркер забирает допустимое задание, получает локальную миниатюру/постер
через отдельный клиент helper и сохраняет JPEG. Недоступная локальная миниатюра
откладывается, а не запускает полную загрузку оригинала. API отдаёт готовый кэш,
UI обновляет ожидавшие изображения по preview-status.

Код: [`PhotoLibraries.refresh_connection`](reference/media_manager--photo_libraries.md#symbol-PhotoLibraries.refresh_connection),
[`PhotosBrowser.browse`](reference/media_manager--photos_browser.md#symbol-PhotosBrowser.browse),
[`ThumbnailWorkerPool._work`](reference/media_manager--thumbnail_workers.md#symbol-ThumbnailWorkerPool._work),
[`StoragePreview.refresh_pending`](reference/storage_preview_ui.md#symbol-StoragePreview.refresh_pending).

## 9. Оригиналы Photos и продолжение

Команда start сначала разрешает корневую копию цепочки и расписание. После проверки
активной медиатеки и неизменности папки Core индексирует stat назначения и принимает
поток манифеста. Готовность восстанавливается по квитанциям; старые успешные файлы
не читаются целиком повторно. Новые ресурсы берутся из подходящих копий либо PhotoKit.

Поток накапливается в буфер до 64 МиБ, создаётся новое конечное имя, намерение
фиксируется до записи. После fsync, закрытия и проверки метаданных сохраняется
квитанция. Все ресурсы одного asset должны быть готовы, чтобы объект считался готовым.
Прерванный конечный файл остаётся в журнале, повтор выбирает свободное имя.

Код: [`PhotosOriginals.start`](reference/media_manager--photos_originals.md#symbol-PhotosOriginals.start),
[`PhotosOriginals.run`](reference/media_manager--photos_originals.md#symbol-PhotosOriginals.run),
[`PhotosOriginals._save`](reference/media_manager--photos_originals.md#symbol-PhotosOriginals._save),
[`PhotosOriginals._receipt`](reference/media_manager--photos_originals.md#symbol-PhotosOriginals._receipt).

## 10. Цепочка Photos → NVMe → HDD

Источники задаются отдельными рёбрами photos_copy_sources. Корневая копия получает
данные Photos, зависимая — только подтверждённые файлы выбранного upstream. Перед
новыми загрузками корень пытается восстановить уже известные ресурсы других копий.
Репликация обслуживает готовые партии до основного прохода, каждые 256 ресурсов и в конце.

Если зависимый диск недоступен, сохраняется waiting и ошибка, а маршруты не меняются
автоматически. Изменение источника требует остановленного сохранения и проверки цикла.
«Сделать первой» меняет порядок номеров, само по себе не задаёт эту цепочку.

Код: [`PhotoLibraries.set_copy_source`](reference/media_manager--photo_libraries.md#symbol-PhotoLibraries.set_copy_source),
[`PhotoLibraries.make_first_copy`](reference/media_manager--photo_libraries.md#symbol-PhotoLibraries.make_first_copy),
[`PhotosOriginals._replicate_all`](reference/media_manager--photos_originals.md#symbol-PhotosOriginals._replicate_all).

## 11. Ночное окно

По умолчанию ограничение выключено. При включении окно 00–07 либо выбранные часы
по Москве ограничивают выдачу превью, сканирование Photos и передачу оригиналов.
Ручной запрос оригиналов сохраняется как запрос расписания; таймер запускает
допустимый корень и ставит его на паузу при выходе из окна.

Ручная пауза оригиналов отменяет автоматический запрос, а пауза из-за конца окна
сохраняет его для продолжения. Готовые превью доступны в любое время.
Код: [`PhotosSyncSchedule.request`](reference/media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.request),
[`PhotosSyncSchedule.tick`](reference/media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.tick),
[`PhotosOriginals.pause`](reference/media_manager--photos_originals.md#symbol-PhotosOriginals.pause).

## 12. Размер папки и уведомление об изменениях

DirectorySizeService устраняет покрываемые одной областью запросы, помещает нужные
корни в очередь и считает сумму st_size обычных файлов без чтения содержимого.
Итоги сохраняются снизу вверх, ошибки дают частичность, изменение дочернего итога
помечает родителя stale. Опрос размеров не обязан повторно обнаруживать все диски.

Отслеживание основной папки — другой сценарий: Watchdog замечает изменение и
сохраняет changed_at. Подтверждение уведомления передаёт ожидаемое changed_at,
чтобы не снять более новое событие. Это не автоматическая сверка или копирование.

Код: [`DirectorySizeService.calculate`](reference/media_manager--directory_sizes.md#symbol-DirectorySizeService.calculate),
[`FolderTrackingService.reconcile`](reference/media_manager--folder_tracking.md#symbol-FolderTrackingService.reconcile),
[`CopyCatalog.acknowledge_changes`](reference/media_manager--copies.md#symbol-CopyCatalog.acknowledge_changes).
