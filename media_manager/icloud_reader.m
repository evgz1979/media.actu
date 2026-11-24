#import <Foundation/Foundation.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>

//: Сопоставляет версии файла по идентичности, размеру и времени.
//: Принимает два снимка stat до и после передачи.
static BOOL sameVersion(struct stat first, struct stat second) {
    return first.st_dev == second.st_dev && first.st_ino == second.st_ino
        && first.st_size == second.st_size
        && first.st_mtimespec.tv_sec == second.st_mtimespec.tv_sec
        && first.st_mtimespec.tv_nsec == second.st_mtimespec.tv_nsec
        && first.st_ctimespec.tv_sec == second.st_ctimespec.tv_sec
        && first.st_ctimespec.tv_nsec == second.st_ctimespec.tv_nsec;
}

//: Сравнивает файл с сохранёнными метаданными передачи, не открывая его содержимое.
//: Гидратация и выгрузка могут менять ctime, поэтому здесь сравнивается mtime.
static BOOL expectedVersion(struct stat current, const char *argv[]) {
    return current.st_dev == strtoll(argv[4], NULL, 10)
        && current.st_ino == strtoull(argv[5], NULL, 10)
        && current.st_size == strtoll(argv[6], NULL, 10)
        && current.st_mtimespec.tv_sec == strtoll(argv[7], NULL, 10)
        && current.st_mtimespec.tv_nsec == strtol(argv[8], NULL, 10);
}

//: Запрашивает загрузку или освобождение подтверждённого файла через FileManager.
//: Код 76 сохраняет файл при наличии другого запроса или запрете выгрузки macOS.
static int changeResidency(int parent, const char *name, BOOL download, BOOL retry, const char *argv[]) {
    char directory[MAXPATHLEN];
    if (fcntl(parent, F_GETPATH, directory) < 0) {
        fputs("Не удалось получить путь iCloud Drive", stderr);
        return 75;
    }
    NSURL *folder = [NSURL fileURLWithFileSystemRepresentation:directory isDirectory:YES relativeToURL:nil];
    NSURL *url = [NSURL fileURLWithFileSystemRepresentation:name isDirectory:NO relativeToURL:folder];
    NSFileManager *manager = NSFileManager.defaultManager;
    NSArray *keys = download ? @[NSURLUbiquitousItemIsDownloadingKey, NSURLUbiquitousItemDownloadRequestedKey,
            NSURLUbiquitousItemDownloadingErrorKey]
        : @[NSURLIsUbiquitousItemKey, NSURLIsPurgeableKey, NSURLUbiquitousItemIsUploadedKey,
            NSURLUbiquitousItemIsUploadingKey, NSURLUbiquitousItemHasUnresolvedConflictsKey];
    NSError *error = nil;
    NSDictionary *values = [url resourceValuesForKeys:keys error:&error];
    struct stat current;
    if (fstatat(parent, name, &current, AT_SYMLINK_NOFOLLOW) || !S_ISREG(current.st_mode)
            || !expectedVersion(current, argv)) {
        fputs("Версия файла iCloud изменилась", stderr);
        return 76;
    }
    if (download) {
        if (!(current.st_flags & SF_DATALESS)) {
            fputs("Файл уже загружен на M4", stderr);
            return 76;
        }
        if ([values[NSURLUbiquitousItemIsDownloadingKey] boolValue]) {
            fputs("macOS загружает файл", stderr);
            return 76;
        }
        NSError *downloadError = values[NSURLUbiquitousItemDownloadingErrorKey];
        if (!retry && [values[NSURLUbiquitousItemDownloadRequestedKey] boolValue]) {
            if (downloadError) {
                fprintf(stderr, "macOS ожидает загрузки после ошибки (%s %ld): %s", downloadError.domain.UTF8String,
                    (long)downloadError.code, downloadError.localizedDescription.UTF8String);
            } else {
                fputs("Запрос на загрузку уже в очереди macOS", stderr);
            }
            return 76;
        }
        if ([manager startDownloadingUbiquitousItemAtURL:url error:&error]) {
            if (downloadError) {
                fprintf(stderr, "Повтор после ошибки macOS (%s %ld): %s", downloadError.domain.UTF8String,
                    (long)downloadError.code, downloadError.localizedDescription.UTF8String);
            }
            return 0;
        }
        error = error ?: downloadError;
    } else {
        if (current.st_flags & SF_DATALESS) return 0;
        if (![values[NSURLIsUbiquitousItemKey] boolValue] || ![values[NSURLIsPurgeableKey] boolValue]
                || ![values[NSURLUbiquitousItemIsUploadedKey] boolValue]
                || ![values[NSURLUbiquitousItemIsUploadingKey] isEqual:@NO]
                || ![values[NSURLUbiquitousItemHasUnresolvedConflictsKey] isEqual:@NO]) {
            fputs("macOS не подтвердила, что локальную загрузку можно освободить", stderr);
            return 76;
        }
        if ([manager evictUbiquitousItemAtURL:url error:&error]) {
            if (!fstatat(parent, name, &current, AT_SYMLINK_NOFOLLOW) && (current.st_flags & SF_DATALESS)) return 0;
            fputs("macOS ещё освобождает локальную загрузку", stderr);
            return 75;
        }
    }
    if (error) {
        fprintf(stderr, "%s (%s %ld)", error.localizedDescription.UTF8String, error.domain.UTF8String, (long)error.code);
    } else {
        fputs("macOS отклонила действие iCloud", stderr);
    }
    return 75;
}

//: Передаёт локальное содержимое в stdout или явно меняет состояние облачного файла.
//: Чтение заполнителя оставляет его в очереди без скрытого запроса на скачивание.
int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 3 && argc != 9) return 64;
        int parent = atoi(argv[1]);
        const char *name = argv[2];
        if (!*name || strchr(name, '/') || !strcmp(name, ".") || !strcmp(name, "..")) return 64;
        if (argc == 9) {
            if (!strcmp(argv[3], "download")) return changeResidency(parent, name, YES, NO, argv);
            if (!strcmp(argv[3], "retry")) return changeResidency(parent, name, YES, YES, argv);
            if (!strcmp(argv[3], "evict")) return changeResidency(parent, name, NO, NO, argv);
            return 64;
        }
        struct stat expected;
        if (fstatat(parent, name, &expected, AT_SYMLINK_NOFOLLOW) || !S_ISREG(expected.st_mode)) {
            fputs("Исходный файл недоступен", stderr);
            return 75;
        }
        if (expected.st_flags & SF_DATALESS) {
            fputs("Ожидание загрузки из iCloud", stderr);
            return 75;
        }
        int source = openat(parent, name, O_RDONLY | O_NOFOLLOW | O_NONBLOCK);
        struct stat current;
        if (source < 0 || fstat(source, &current) || !sameVersion(expected, current)) {
            fputs("Исходный файл изменился или недоступен", stderr);
            return 75;
        }
        char buffer[128 * 1024];
        ssize_t length;
        while ((length = read(source, buffer, sizeof(buffer))) > 0) {
            if (fwrite(buffer, 1, (size_t)length, stdout) != (size_t)length) return 74;
        }
        if (length < 0 || fstat(source, &current) || !sameVersion(expected, current)) {
            fputs("Не удалось дочитать исходный файл", stderr);
            return 75;
        }
        close(source);
        return fflush(stdout) == 0 ? 0 : 74;
    }
}
