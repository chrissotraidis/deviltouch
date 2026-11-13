#include "../upstream/DevilutionX/Source/controls/touch/visibility.hpp"

#include <cstdio>

using devilution::TouchOverlayLive;

int main()
{
	int failures = 0;
	auto expect = [&](bool ok, const char *step) {
		if (!ok) {
			std::fprintf(stderr, "FAIL: %s\n", step);
			++failures;
		}
	};
	const bool autoHideDefault = true; // the option's default when nothing is saved

	expect(!TouchOverlayLive(false, autoHideDefault, false, false, false), "overlay off by default stays off");
	expect(TouchOverlayLive(true, autoHideDefault, false, false, false), "overlay on without a controller");
	expect(TouchOverlayLive(true, autoHideDefault, true, false, false), "a connected but unused controller keeps the overlay");
	expect(!TouchOverlayLive(true, autoHideDefault, true, true, false), "playing with a controller hides the overlay");
	expect(TouchOverlayLive(true, autoHideDefault, false, true, false), "disconnecting the controller restores the overlay");
	expect(TouchOverlayLive(true, autoHideDefault, true, false, false), "touch or pointer input after a controller restores the overlay");
	expect(TouchOverlayLive(true, false, true, true, false), "auto-hide off keeps the overlay with a controller in use");
	expect(!TouchOverlayLive(true, true, true, true, false), "auto-hide back on hides it again");
	expect(!TouchOverlayLive(true, false, false, false, true), "a directly touchable side panel hides the overlay");
	// Show Touch Controls turns the overlay on and auto-hide off.
	expect(TouchOverlayLive(true, false, true, true, false), "Show works with the controller still connected");

	if (failures == 0) std::puts("touch overlay visibility: pass");
	return failures == 0 ? 0 : 1;
}
