#import <AppKit/AppKit.h>
#import <Foundation/Foundation.h>
#import <Photos/Photos.h>

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
}

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
    options.networkAccessAllowed = YES;
    options.deliveryMode = PHImageRequestOptionsDeliveryModeHighQualityFormat;
    options.resizeMode = PHImageRequestOptionsResizeModeExact;
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

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyAccessory];
        NSArray<NSString *> *arguments = [[NSProcessInfo processInfo] arguments];
        NSString *command = arguments.count > 1 ? arguments[1] : @"status";
        if ([command isEqualToString:@"check"]) return statusCommand(NO);
        if ([command isEqualToString:@"status"]) return statusCommand(YES);
        if ([command isEqualToString:@"scan"]) return scanCommand();
        if ([command isEqualToString:@"thumbnail"]) return thumbnailCommand(arguments);
        writeJSON(@{ @"error": @"Unknown command" }, stderr);
        return 64;
    }
}
