#pragma once

#ifdef __cplusplus
extern "C" {
#endif

// Presents the iOS Files picker and copies recognized, valid MPQ archives into
// the app's Documents directory. Returns the number of accepted archives.
int DevilTouchImportGameData(void);

#ifdef __cplusplus
}
#endif
