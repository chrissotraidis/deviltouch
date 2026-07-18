#import <UIKit/UIKit.h>

#import "game_data_import.h"

@interface DevilTouchGameDataImporter : NSObject <UIDocumentPickerDelegate>

@property(nonatomic, assign) BOOL finished;
@property(nonatomic, assign) NSInteger importedCount;
@property(nonatomic, strong) NSMutableArray<NSString *> *errors;

@end

static UIViewController *DevilTouchTopViewController(void)
{
	UIWindow *window = nil;
	for (UIWindow *candidate in UIApplication.sharedApplication.windows) {
		if (candidate.isKeyWindow) {
			window = candidate;
			break;
		}
	}
	if (window == nil)
		window = UIApplication.sharedApplication.windows.firstObject;

	UIViewController *controller = window.rootViewController;
	while (controller.presentedViewController != nil)
		controller = controller.presentedViewController;
	return controller;
}

static NSDictionary<NSString *, NSString *> *DevilTouchArchiveNames(void)
{
	return @{
		@"diabdat.mpq" : @"diabdat.mpq",
		@"spawn.mpq" : @"spawn.mpq",
		@"hellfire.mpq" : @"hellfire.mpq",
		@"hfmonk.mpq" : @"hfmonk.mpq",
		@"hfmusic.mpq" : @"hfmusic.mpq",
		@"hfvoice.mpq" : @"hfvoice.mpq",
		@"hfbard.mpq" : @"hfbard.mpq",
		@"hfbarb.mpq" : @"hfbarb.mpq",
	};
}

static BOOL DevilTouchHasMpqHeader(NSURL *url)
{
	NSFileHandle *handle = [NSFileHandle fileHandleForReadingFromURL:url error:nil];
	if (handle == nil)
		return NO;
	NSData *prefix = [handle readDataOfLength:1024 * 1024];
	[handle closeFile];

	const unsigned char *bytes = prefix.bytes;
	for (NSUInteger offset = 0; offset + 4 <= prefix.length; offset += 512) {
		if (bytes[offset] == 'M' && bytes[offset + 1] == 'P' && bytes[offset + 2] == 'Q'
		    && (bytes[offset + 3] == 0x1A || bytes[offset + 3] == 0x1B))
			return YES;
	}
	return NO;
}

@implementation DevilTouchGameDataImporter

- (instancetype)init
{
	self = [super init];
	if (self != nil)
		_errors = [NSMutableArray array];
	return self;
}

- (void)recordErrorForURL:(NSURL *)url reason:(NSString *)reason
{
	[self.errors addObject:[NSString stringWithFormat:@"%@: %@", url.lastPathComponent, reason]];
}

- (void)importURL:(NSURL *)url
{
	NSString *canonicalName = DevilTouchArchiveNames()[url.lastPathComponent.lowercaseString];
	if (canonicalName == nil) {
		[self recordErrorForURL:url reason:@"not a recognized Diablo archive"];
		return;
	}

	BOOL accessed = [url startAccessingSecurityScopedResource];
	if (!DevilTouchHasMpqHeader(url)) {
		[self recordErrorForURL:url reason:@"does not contain a valid MPQ header"];
		if (accessed)
			[url stopAccessingSecurityScopedResource];
		return;
	}

	NSURL *documents = [[[NSFileManager defaultManager] URLsForDirectory:NSDocumentDirectory
	                                                           inDomains:NSUserDomainMask] firstObject];
	NSURL *destination = [documents URLByAppendingPathComponent:canonicalName];
	if ([url.path.stringByStandardizingPath isEqualToString:destination.path.stringByStandardizingPath]) {
		self.importedCount++;
		if (accessed)
			[url stopAccessingSecurityScopedResource];
		return;
	}

	NSFileManager *manager = [NSFileManager defaultManager];
	NSURL *temporary = [documents URLByAppendingPathComponent:
	    [NSString stringWithFormat:@".%@.%@.importing", canonicalName, NSUUID.UUID.UUIDString]];
	NSError *error = nil;
	BOOL copied = [manager copyItemAtURL:url toURL:temporary error:&error];
	if (copied && [manager fileExistsAtPath:destination.path]) {
		copied = [manager replaceItemAtURL:destination
		                    withItemAtURL:temporary
		                   backupItemName:nil
		                          options:0
		                 resultingItemURL:nil
		                            error:&error];
	} else if (copied) {
		copied = [manager moveItemAtURL:temporary toURL:destination error:&error];
	}
	if (copied) {
		self.importedCount++;
	} else {
		[manager removeItemAtURL:temporary error:nil];
		[self recordErrorForURL:url reason:error.localizedDescription ?: @"could not be copied"];
	}

	if (accessed)
		[url stopAccessingSecurityScopedResource];
}

- (void)beginImportWithURLs:(NSArray<NSURL *> *)urls fromPicker:(UIDocumentPickerViewController *)picker
{
	UIViewController *presenter = picker.presentingViewController ?: DevilTouchTopViewController();
	[picker dismissViewControllerAnimated:YES completion:^{
		UIAlertController *progress = [UIAlertController alertControllerWithTitle:@"Importing Game Data"
		                                                               message:@"Copying the selected archives. Please keep DevilTouch open.\n\n"
		                                                        preferredStyle:UIAlertControllerStyleAlert];
		UIActivityIndicatorView *indicator = [[UIActivityIndicatorView alloc]
		    initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleLarge];
		indicator.translatesAutoresizingMaskIntoConstraints = NO;
		[progress.view addSubview:indicator];
		[NSLayoutConstraint activateConstraints:@[
			[indicator.centerXAnchor constraintEqualToAnchor:progress.view.centerXAnchor],
			[indicator.bottomAnchor constraintEqualToAnchor:progress.view.bottomAnchor constant:-18],
		]];
		[indicator startAnimating];

		[presenter presentViewController:progress animated:YES completion:^{
			dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
				for (NSURL *url in urls)
					[self importURL:url];
				dispatch_async(dispatch_get_main_queue(), ^{
					[progress dismissViewControllerAnimated:YES completion:^{ self.finished = YES; }];
				});
			});
		}];
	}];
}

- (void)documentPicker:(UIDocumentPickerViewController *)controller didPickDocumentsAtURLs:(NSArray<NSURL *> *)urls
{
	[self beginImportWithURLs:urls fromPicker:controller];
}

- (void)documentPicker:(UIDocumentPickerViewController *)controller didPickDocumentAtURL:(NSURL *)url
{
	[self beginImportWithURLs:@[ url ] fromPicker:controller];
}

- (void)documentPickerWasCancelled:(UIDocumentPickerViewController *)controller
{
	self.finished = YES;
}

@end

static void DevilTouchShowImportErrors(NSArray<NSString *> *errors)
{
	if (errors.count == 0)
		return;

	__block BOOL acknowledged = NO;
	UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Could Not Import Game Data"
	                                                               message:[errors componentsJoinedByString:@"\n"]
	                                                        preferredStyle:UIAlertControllerStyleAlert];
	[alert addAction:[UIAlertAction actionWithTitle:@"OK"
	                                       style:UIAlertActionStyleDefault
	                                     handler:^(UIAlertAction *action) { acknowledged = YES; }]];
	[DevilTouchTopViewController() presentViewController:alert animated:YES completion:nil];
	while (!acknowledged)
		[[NSRunLoop currentRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
}

int DevilTouchImportGameData(void)
{
	@autoreleasepool {
		if (![NSThread isMainThread])
			return 0;

		UIViewController *presenter = DevilTouchTopViewController();
		if (presenter == nil)
			return 0;

		DevilTouchGameDataImporter *importer = [[DevilTouchGameDataImporter alloc] init];
		UIDocumentPickerViewController *picker = [[UIDocumentPickerViewController alloc]
		    initWithDocumentTypes:@[ @"public.data" ]
		                  inMode:UIDocumentPickerModeImport];
		picker.delegate = importer;
		picker.allowsMultipleSelection = YES;
		picker.modalPresentationStyle = UIModalPresentationFormSheet;
		[presenter presentViewController:picker animated:YES completion:nil];

		while (!importer.finished)
			[[NSRunLoop currentRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
		while (picker.presentingViewController != nil)
			[[NSRunLoop currentRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];

		DevilTouchShowImportErrors(importer.errors);
		return (int)importer.importedCount;
	}
}
