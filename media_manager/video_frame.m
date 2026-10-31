#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <ImageIO/ImageIO.h>
#import <UniformTypeIdentifiers/UniformTypeIdentifiers.h>
#include <sys/stat.h>
#include <unistd.h>

@interface DescriptorLoader : NSObject <AVAssetResourceLoaderDelegate>
@property int descriptor;
@property long long length;
@property (nonatomic, copy) NSString *contentType;
@end

@implementation DescriptorLoader
- (BOOL)resourceLoader:(AVAssetResourceLoader *)loader shouldWaitForLoadingOfRequestedResource:(AVAssetResourceLoadingRequest *)request {
    AVAssetResourceLoadingContentInformationRequest *info = request.contentInformationRequest;
    info.contentType = self.contentType;
    info.contentLength = self.length;
    info.byteRangeAccessSupported = YES;
    AVAssetResourceLoadingDataRequest *data = request.dataRequest;
    if (data) {
        long long offset = data.currentOffset;
        long long end = data.requestsAllDataToEndOfResource ? self.length : MIN(self.length, data.requestedOffset + data.requestedLength);
        unsigned char buffer[65536];
        while (offset < end) {
            ssize_t count = pread(self.descriptor, buffer, (size_t)MIN(end - offset, sizeof(buffer)), offset);
            if (count <= 0) {
                [request finishLoadingWithError:[NSError errorWithDomain:NSPOSIXErrorDomain code:count < 0 ? errno : EIO userInfo:nil]];
                return YES;
            }
            [data respondWithData:[NSData dataWithBytes:buffer length:(NSUInteger)count]];
            offset += count;
        }
    }
    [request finishLoading];
    return YES;
}
@end

// The parent passes an already checked, read-only descriptor, never a pathname
// that a media decoder could follow through a substituted link.
int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 5) return 2;
        int descriptor = atoi(argv[1]);
        struct stat info;
        if (fstat(descriptor, &info) != 0) return 2;
        NSString *extension = [NSString stringWithUTF8String:argv[4]];
        NSURL *url = [NSURL URLWithString:[@"media-actu://preview/file." stringByAppendingString:extension]];
        AVURLAsset *asset = [AVURLAsset URLAssetWithURL:url options:nil];
        DescriptorLoader *loader = [DescriptorLoader new];
        loader.descriptor = descriptor;
        loader.length = info.st_size;
        loader.contentType = [UTType typeWithFilenameExtension:extension].identifier ?: @"public.movie";
        [asset.resourceLoader setDelegate:loader queue:dispatch_queue_create("media-actu.video", DISPATCH_QUEUE_SERIAL)];
        AVAssetImageGenerator *generator = [[AVAssetImageGenerator alloc] initWithAsset:asset];
        generator.appliesPreferredTrackTransform = YES;
        generator.maximumSize = CGSizeMake(atoi(argv[2]), atoi(argv[3]));
        NSError *error = nil;
        CGImageRef image = [generator copyCGImageAtTime:kCMTimeZero actualTime:NULL error:&error];
        if (!image) {
            fprintf(stderr, "%s\n", error.localizedDescription.UTF8String ?: "Video frame unavailable");
            return 3;
        }
        NSMutableData *data = [NSMutableData data];
        CGImageDestinationRef destination = CGImageDestinationCreateWithData((__bridge CFMutableDataRef)data, CFSTR("public.jpeg"), 1, NULL);
        if (!destination) { CGImageRelease(image); return 4; }
        CGImageDestinationAddImage(destination, image, NULL);
        BOOL ok = CGImageDestinationFinalize(destination);
        CFRelease(destination);
        CGImageRelease(image);
        if (!ok) return 5;
        return fwrite(data.bytes, 1, data.length, stdout) == data.length ? 0 : 6;
    }
}
