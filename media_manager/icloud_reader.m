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

//: Запрашивает загрузку облачного файла либо передаёт локальное содержимое в stdout.
//: Код 75 оставляет файл в очереди; передача использует дескриптор проверенного родителя.
int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 3) return 64;
        int parent = atoi(argv[1]);
        const char *name = argv[2];
        if (!*name || strchr(name, '/') || !strcmp(name, ".") || !strcmp(name, "..")) return 64;
        struct stat expected;
        if (fstatat(parent, name, &expected, AT_SYMLINK_NOFOLLOW) || !S_ISREG(expected.st_mode)) {
            fputs("Исходный файл недоступен", stderr);
            return 75;
        }
        if (expected.st_flags & SF_DATALESS) {
            char directory[MAXPATHLEN];
            if (fcntl(parent, F_GETPATH, directory) < 0) {
                fputs("Не удалось получить путь iCloud Drive", stderr);
                return 75;
            }
            NSFileManager *manager = NSFileManager.defaultManager;
            NSURL *folder = [NSURL fileURLWithFileSystemRepresentation:directory isDirectory:YES relativeToURL:nil];
            NSURL *url = [NSURL fileURLWithFileSystemRepresentation:name isDirectory:NO relativeToURL:folder];
            NSError *error = nil;
            if (![manager startDownloadingUbiquitousItemAtURL:url error:&error]) {
                fprintf(stderr, "%s", error.localizedDescription.UTF8String ?: "iCloud не принял запрос загрузки");
            } else {
                fputs("Ожидание загрузки из iCloud", stderr);
            }
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
