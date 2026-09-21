package com.nokia.mid.ui;

/**
 * The Nokia UI API, as far as this game uses it: one call to set the
 * backlight. FreeJ2ME provides the real thing; MicroEmulator does not, and
 * without it the game dies at startup with a NoClassDefFoundError inside its
 * own error dialog. Headless there is no backlight to set, so this does
 * nothing and lets the game get on with it.
 */
public final class DeviceControl {

    private DeviceControl() {
    }

    public static void setLights(int num, int level) {
    }

    public static void flashLights(long duration) {
    }

    public static void startVibra(int freq, long duration) {
    }

    public static void stopVibra() {
    }
}
