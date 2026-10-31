#import <AppKit/AppKit.h>
#import <Foundation/Foundation.h>
#import <Photos/Photos.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <sys/file.h>
#include <fcntl.h>
#include <poll.h>
#include <errno.h>
#include <unistd.h>

static NSString *statusName(PHAuthorizationStatus status) {
    switch (status) {
        case PHAuthorizationStatusAuthorized: return @"authorized";
        case PHAuthorizationStatusDenied: return @"denied";
        case PHAuthorizationStatusLimited: return @"limited";
        case PHAuthorizationStatusNotDetermined: return @"not_determined";
        case PHAuthorizationStatusRestricted: return @"restricted";
    }
    return @"unknown";
}

static PHAuthorizationStatus authorization(BOOL request) {
    __block PHAuthorizationStatus status =
        [PHPhotoLibrary authorizationStatusForAccessLevel:PHAccessLevelReadWrite];
    if (request && status == PHAuthorizationStatusNotDetermined) {
        __block BOOL finished = NO;
        [NSApp activateIgnoringOtherApps:YES];
        [PHPhotoLibrary requestAuthorizationForAccessLevel:PHAccessLevelReadWrite
                                                   handler:^(PHAuthorizationStatus newStatus) {
            status = newStatus;
            finished = YES;
        }];
        while (!finished) {
            [[NSRunLoop currentRunLoop] runMode:NSDefaultRunLoopMode
                                     beforeDate:[NSDate dateWithTimeIntervalSinceNow:0.1]];
        }
    }
    return status;
}

static BOOL canRead(PHAuthorizationStatus status) {
    return status == PHAuthorizationStatusAuthorized ||
           status == PHAuthorizationStatusLimited;
}

static void writeJSON(id value, FILE *stream) {
    NSData *data = [NSJSONSerialization dataWithJSONObject:value options:0 error:nil];
    fwrite(data.bytes, 1, data.length, stream);
    fputc('\n', stream);
    fflush(stream);
}

@interface LibraryState : NSObject <PHPhotoLibraryAvailabilityObserver>
@property (atomic) BOOL unavailable;
@end
@implementation LibraryState
- (void)photoLibraryDidBecomeUnavailable:(PHPhotoLibrary *)library { self.unavailable = YES; }
@end

static NSString *assetName(PHAsset *asset) {
    NSArray<PHAssetResource *> *resources = [PHAssetResource assetResourcesForAsset:asset];
    for (PHAssetResource *resource in resources) {
        if (resource.type == PHAssetResourceTypePhoto ||
            resource.type == PHAssetResourceTypeVideo ||
            resource.type == PHAssetResourceTypeFullSizePhoto ||
            resource.type == PHAssetResourceTypeFullSizeVideo) {
            return resource.originalFilename;
        }
    }
    return resources.firstObject.originalFilename ?: asset.localIdentifier;
}

static int statusCommand(BOOL request) {
    PHAuthorizationStatus status = authorization(request);
    NSUInteger count = canRead(status) ? [PHAsset fetchAssetsWithOptions:nil].count : 0;
    writeJSON(@{ @"status": statusName(status), @"count": @(count) }, stdout);
    return request && !canRead(status) ? 2 : 0;
}

static int scanCommand(void) {
    PHAuthorizationStatus status = authorization(NO);
    if (!canRead(status)) {
        writeJSON(@{ @"status": statusName(status), @"assets": @[] }, stdout);
        return 2;
    }

    PHFetchOptions *options = [[PHFetchOptions alloc] init];
    options.sortDescriptors = @[[NSSortDescriptor sortDescriptorWithKey:@"creationDate"
                                                               ascending:YES]];
    PHFetchResult<PHAsset *> *result = [PHAsset fetchAssetsWithOptions:options];
    NSMutableArray *assets = [NSMutableArray arrayWithCapacity:result.count];
    NSISO8601DateFormatter *formatter = [[NSISO8601DateFormatter alloc] init];
    formatter.formatOptions = NSISO8601DateFormatWithInternetDateTime |
                              NSISO8601DateFormatWithFractionalSeconds;

    [result enumerateObjectsUsingBlock:^(PHAsset *asset, NSUInteger index, BOOL *stop) {
        NSString *kind = nil;
        if (asset.mediaType == PHAssetMediaTypeImage) kind = @"photo";
        if (asset.mediaType == PHAssetMediaTypeVideo) kind = @"video";
        if (kind == nil) return;
        NSString *created = asset.creationDate
            ? [formatter stringFromDate:asset.creationDate]
            : @"";
        [assets addObject:@{
            @"id": asset.localIdentifier,
            @"name": assetName(asset),
            @"kind": kind,
            @"created_at": created,
            @"width": @(asset.pixelWidth),
            @"height": @(asset.pixelHeight),
            @"favorite": @(asset.favorite),
            @"hidden": @(asset.hidden),
        }];
    }];

    writeJSON(@{ @"status": @"authorized", @"assets": assets }, stdout);
    return 0;
}

static int thumbnailCommand(NSArray<NSString *> *arguments) {
    if (arguments.count != 6) {
        writeJSON(@{ @"error": @"thumbnail requires asset, output, width, height" }, stderr);
        return 64;
    }
    if (!canRead(authorization(NO))) {
        writeJSON(@{ @"error": @"Photos access is not authorized" }, stderr);
        return 2;
    }

    NSString *identifier = arguments[2];
    NSString *outputPath = arguments[3];
    CGFloat width = arguments[4].doubleValue;
    CGFloat height = arguments[5].doubleValue;
    PHAsset *asset = [PHAsset fetchAssetsWithLocalIdentifiers:@[identifier]
                                                     options:nil].firstObject;
    if (asset == nil || asset.mediaType != PHAssetMediaTypeImage) {
        writeJSON(@{ @"error": @"Photo asset not found" }, stderr);
        return 3;
    }

    PHImageRequestOptions *options = [[PHImageRequestOptions alloc] init];
    options.synchronous = YES;
    options.networkAccessAllowed = NO;
    options.deliveryMode = PHImageRequestOptionsDeliveryModeHighQualityFormat;
    options.resizeMode = PHImageRequestOptionsResizeModeFast;
    options.version = PHImageRequestOptionsVersionCurrent;
    __block NSImage *image = nil;
    [[PHImageManager defaultManager] requestImageForAsset:asset
                                                targetSize:NSMakeSize(width, height)
                                               contentMode:PHImageContentModeAspectFit
                                                   options:options
                                             resultHandler:^(NSImage *result, NSDictionary *info) {
        image = result;
    }];
    if (image == nil) {
        writeJSON(@{ @"error": @"PhotoKit did not return an image" }, stderr);
        return 4;
    }

    NSData *tiff = image.TIFFRepresentation;
    NSBitmapImageRep *bitmap = [NSBitmapImageRep imageRepWithData:tiff];
    NSData *jpeg = [bitmap representationUsingType:NSBitmapImageFileTypeJPEG
                                        properties:@{NSImageCompressionFactor: @0.86}];
    if (![jpeg writeToFile:outputPath atomically:YES]) {
        writeJSON(@{ @"error": @"Could not write thumbnail" }, stderr);
        return 5;
    }
    writeJSON(@{ @"path": outputPath }, stdout);
    return 0;
}

static NSDictionary *handleRequest(NSDictionary *request, LibraryState *state) {
    NSString *operation = request[@"op"];
    PHAuthorizationStatus access = authorization([operation isEqualToString:@"authorize"]);
    if (!canRead(access)) return @{ @"status": statusName(access) };
    if ([operation isEqualToString:@"authorize"]) return @{ @"status": statusName(access) };
    if (state.unavailable || [PHPhotoLibrary sharedPhotoLibrary].unavailabilityReason)
        return @{ @"status": @"unavailable" };
    NSArray *anchors = request[@"anchors"] ?: @[];
    if (anchors.count && [PHAsset fetchAssetsWithLocalIdentifiers:anchors options:nil].count < MIN(3, anchors.count))
        return @{ @"status": @"library_mismatch" };
    if ([operation isEqualToString:@"probe"]) {
        PHFetchResult<PHAsset *> *assets = [PHAsset fetchAssetsWithOptions:nil];
        NSMutableArray *sample = [NSMutableArray array];
        NSUInteger count = MIN(12, assets.count);
        for (NSUInteger i = 0; i < count; i++)
            [sample addObject:[assets objectAtIndex:(i * assets.count / count)].localIdentifier];
        NSMutableArray *matched = [NSMutableArray array];
        PHFetchResult *found = [PHAsset fetchAssetsWithLocalIdentifiers:request[@"identifiers"] ?: @[] options:nil];
        for (PHAsset *asset in found) [matched addObject:asset.localIdentifier];
        return @{ @"status": @"authorized", @"count": @(assets.count), @"sample": sample, @"matched": matched };
    }
    if ([operation isEqualToString:@"scan"]) {
        PHFetchOptions *options = [PHFetchOptions new];
        options.sortDescriptors = @[[NSSortDescriptor sortDescriptorWithKey:@"creationDate" ascending:YES]];
        NSMutableArray *result = [NSMutableArray array];
        NSISO8601DateFormatter *formatter = [NSISO8601DateFormatter new];
        formatter.formatOptions = NSISO8601DateFormatWithInternetDateTime | NSISO8601DateFormatWithFractionalSeconds;
        for (PHAsset *asset in [PHAsset fetchAssetsWithOptions:options]) {
            if (asset.mediaType != PHAssetMediaTypeImage && asset.mediaType != PHAssetMediaTypeVideo) continue;
            [result addObject:@{ @"id": asset.localIdentifier, @"name": assetName(asset),
                @"kind": asset.mediaType == PHAssetMediaTypeImage ? @"photo" : @"video",
                @"created_at": asset.creationDate ? [formatter stringFromDate:asset.creationDate] : @"" }];
        }
        if (state.unavailable || [PHPhotoLibrary sharedPhotoLibrary].unavailabilityReason)
            return @{ @"status": @"unavailable" };
        return @{ @"status": @"authorized", @"assets": result };
    }
    if (![operation isEqualToString:@"thumbnail"]) return @{ @"error": @"Unknown request" };
    PHAsset *asset = [PHAsset fetchAssetsWithLocalIdentifiers:@[request[@"identifier"]] options:nil].firstObject;
    if (!asset) return @{ @"error": @"Объект отсутствует в текущей медиатеке" };
    CGFloat width = MAX(1, MIN(1600, [request[@"width"] doubleValue]));
    CGFloat height = MAX(1, MIN(1200, [request[@"height"] doubleValue]));
    PHImageRequestOptions *options = [PHImageRequestOptions new];
    options.synchronous = YES;
    // A preview must never trigger a full iCloud original download. Originals
    // will be streamed into a bound copy by a separate, explicit operation.
    options.networkAccessAllowed = NO;
    options.deliveryMode = PHImageRequestOptionsDeliveryModeHighQualityFormat;
    options.resizeMode = PHImageRequestOptionsResizeModeFast;
    options.version = PHImageRequestOptionsVersionCurrent;
    __block NSImage *image = nil;
    __block NSDictionary *details = nil;
    [[PHImageManager defaultManager] requestImageForAsset:asset targetSize:NSMakeSize(width, height)
        contentMode:PHImageContentModeAspectFit options:options resultHandler:^(NSImage *result, NSDictionary *info) {
            image = result; details = info;
        }];
    if (!image) {
        if ([details[PHImageResultIsInCloudKey] boolValue]) return @{ @"status": @"cloud" };
        NSError *error = details[PHImageErrorKey];
        return @{ @"error": error.localizedDescription ?: @"Локальная миниатюра недоступна" };
    }
    if (state.unavailable) return @{ @"status": @"unavailable" };
    CGFloat scale = MIN(1, MIN(width / MAX(1, image.size.width), height / MAX(1, image.size.height)));
    NSInteger w = MAX(1, (NSInteger)(image.size.width * scale));
    NSInteger h = MAX(1, (NSInteger)(image.size.height * scale));
    NSBitmapImageRep *bitmap = [[NSBitmapImageRep alloc] initWithBitmapDataPlanes:NULL pixelsWide:w pixelsHigh:h
        bitsPerSample:8 samplesPerPixel:4 hasAlpha:YES isPlanar:NO colorSpaceName:NSDeviceRGBColorSpace bytesPerRow:0 bitsPerPixel:0];
    NSGraphicsContext *context = [NSGraphicsContext graphicsContextWithBitmapImageRep:bitmap];
    if (!context) return @{ @"error": @"Не удалось создать изображение превью" };
    [NSGraphicsContext saveGraphicsState];
    [NSGraphicsContext setCurrentContext:context];
    [[NSColor whiteColor] setFill]; NSRectFill(NSMakeRect(0, 0, w, h));
    [image drawInRect:NSMakeRect(0, 0, w, h) fromRect:NSZeroRect operation:NSCompositingOperationSourceOver fraction:1];
    [NSGraphicsContext restoreGraphicsState];
    NSData *jpeg = [bitmap representationUsingType:NSBitmapImageFileTypeJPEG properties:@{NSImageCompressionFactor:@0.82}];
    if (!jpeg) return @{ @"error": @"Не удалось сформировать миниатюру" };
    return @{ @"status": @"ready", @"jpeg": [jpeg base64EncodedStringWithOptions:0] };
}

static int serve(void) {
    LibraryState *state = [LibraryState new];
    BOOL watching = canRead(authorization(NO));
    if (watching) [[PHPhotoLibrary sharedPhotoLibrary] registerAvailabilityObserver:state];
    char *line = NULL;
    size_t capacity = 0;
    while (getline(&line, &capacity, stdin) > 0) {
        @autoreleasepool {
            NSData *data = [[NSString stringWithUTF8String:line] dataUsingEncoding:NSUTF8StringEncoding];
            NSDictionary *request = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
            if (![request isKindOfClass:NSDictionary.class]) { writeJSON(@{ @"error": @"Invalid JSON request" }, stdout); continue; }
            if ([request[@"op"] isEqualToString:@"quit"]) break;
            @try {
                NSMutableDictionary *response = [handleRequest(request, state) mutableCopy];
                response[@"pid"] = @(getpid());
                writeJSON(response, stdout);
            }
            @catch (NSException *error) { writeJSON(@{ @"error": error.reason ?: @"PhotoKit exception" }, stdout); }
        }
    }
    free(line);
    if (watching) [[PHPhotoLibrary sharedPhotoLibrary] unregisterAvailabilityObserver:state];
    return 0;
}

static int serveSocket(NSString *path) {
    struct sockaddr_un address = {0};
    address.sun_family = AF_UNIX;
    if (strlen(path.fileSystemRepresentation) >= sizeof(address.sun_path)) return 65;
    strlcpy(address.sun_path, path.fileSystemRepresentation, sizeof(address.sun_path));
    umask(0077);
    int listener = socket(AF_UNIX, SOCK_STREAM, 0);
    if (listener < 0) return 66;
    if (bind(listener, (struct sockaddr *)&address, sizeof(address)) || listen(listener, 1)) {
        close(listener); return 67;
    }
    struct pollfd incoming = { .fd = listener, .events = POLLIN };
    if (poll(&incoming, 1, 30000) <= 0) {
        close(listener); unlink(address.sun_path); return 68;
    }
    int client = accept(listener, NULL, NULL);
    close(listener);
    if (client < 0) { unlink(address.sun_path); return 68; }
    uid_t peerUID;
    gid_t peerGID;
    if (getpeereid(client, &peerUID, &peerGID) || peerUID != getuid()) {
        close(client); unlink(address.sun_path); return 69;
    }
    dup2(client, STDIN_FILENO);
    dup2(client, STDOUT_FILENO);
    close(client);
    int result = serve();
    unlink(address.sun_path);
    return result;
}

static int serveDefaultSocket(void) {
    NSString *directory = [NSString stringWithFormat:@"/private/tmp/media-actu-photos-v1-%u", getuid()];
    umask(0077);
    if (mkdir(directory.fileSystemRepresentation, 0700) && errno != EEXIST) return 70;
    struct stat info;
    if (lstat(directory.fileSystemRepresentation, &info) || !S_ISDIR(info.st_mode) ||
        info.st_uid != getuid() || (info.st_mode & 0777) != 0700) return 71;
    NSString *lockPath = [directory stringByAppendingPathComponent:@"service.lock"];
    int lock = open(lockPath.fileSystemRepresentation, O_CREAT | O_RDWR | O_NOFOLLOW, 0600);
    if (lock < 0) return 72;
    if (flock(lock, LOCK_EX | LOCK_NB)) { close(lock); return 73; }
    NSString *path = [directory stringByAppendingPathComponent:@"photos.sock"];
    // Only the service holding this user's lock can remove a stale endpoint.
    unlink(path.fileSystemRepresentation);
    int result = serveSocket(path);
    close(lock);
    return result;
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyAccessory];
        NSArray<NSString *> *arguments = [[NSProcessInfo processInfo] arguments];
        NSString *command = arguments.count > 1 ? arguments[1] : @"service";
        if ([command isEqualToString:@"service"]) return serveDefaultSocket();
        if ([command isEqualToString:@"check"]) return statusCommand(NO);
        if ([command isEqualToString:@"status"]) return statusCommand(YES);
        if ([command isEqualToString:@"scan"]) return scanCommand();
        if ([command isEqualToString:@"serve"]) return serve();
        if ([command isEqualToString:@"serve-socket"] && arguments.count >= 3) return serveSocket(arguments[2]);
        if ([command isEqualToString:@"thumbnail"]) return thumbnailCommand(arguments);
        writeJSON(@{ @"error": @"Unknown command" }, stderr);
        return 64;
    }
}
