import java.io.File;
import java.io.InputStream;
import java.io.PrintStream;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Vector;

import org.microemu.DisplayAccess;
import org.microemu.DisplayComponent;
import org.microemu.EmulatorContext;
import org.microemu.MIDletAccess;
import org.microemu.MIDletBridge;
import org.microemu.app.Common;
import org.microemu.app.ui.noui.NoUiDisplayComponent;
import org.microemu.device.DeviceDisplay;
import org.microemu.device.FontManager;
import org.microemu.device.InputMethod;
import org.microemu.device.j2se.J2SEDevice;
import org.microemu.device.j2se.J2SEDeviceDisplay;
import org.microemu.device.j2se.J2SEFontManager;
import org.microemu.device.j2se.J2SEInputMethod;

/**
 * Run the MIDlet headless under MicroEmulator, drive it from a script, and
 * print its state.
 *
 * Why MicroEmulator and not FreeJ2ME for this: it is built to be embedded.
 * Common is a plain object you construct, NoUiDisplayComponent is a display
 * that draws nothing, DisplayAccess.keyPressed takes a MIDP key code directly,
 * and org.microemu.cldc.http.Connection is a thin wrapper over
 * java.net.HttpURLConnection — so unlike FreeJ2ME it needs no networking shim
 * to reach the relay. FreeJ2ME stays the emulator we actually play on.
 *
 *   tools/harness/meh.sh run/EoE-ShiradsForge.jar "wait:4000,key:-6,state"
 *
 * Script steps, comma separated:
 *   wait:MS       let the game run
 *   key:CODE      press and release a MIDP key code
 *   hold:CODE:MS  hold one down (exploration movement is velocity based)
 *   type:TEXT     enter text a key at a time (hero names)
 *   state         print the current screen's fields
 *   quit          stop
 *
 * Reading state means reflecting over obfuscated single-letter fields, so the
 * names below come from decompiled-vf/ and hold only for these builds.
 */
public class MEHarness {

    /** d.java's fields, as recovered in decompiled-vf/d.java. */
    private static final String[][] MAP_FIELDS = {
        {"I", "location"}, {"Q", "heroX"}, {"R", "heroY"},
        {"T", "loaded"}, {"c", "inCombat"}, {"k", "needsTurn"},
        {"ab", "inputMode"}, {"ag", "turnClock"}, {"Y", "barSlot"},
    };

    static final DisplayComponent DISPLAY = new NoUiDisplayComponent();
    static DeviceDisplay deviceDisplay;
    static FontManager fontManager;
    static InputMethod inputMethod;

    static final EmulatorContext CONTEXT = new EmulatorContext() {
        public DisplayComponent getDisplayComponent() { return DISPLAY; }
        public InputMethod getDeviceInputMethod() { return inputMethod; }
        public DeviceDisplay getDeviceDisplay() { return deviceDisplay; }
        public FontManager getDeviceFontManager() { return fontManager; }
        public InputStream getResourceAsStream(String name) {
            return MEHarness.class.getResourceAsStream(name);
        }
        public boolean platformRequest(String url) { return false; }
    };

    /**
     * MicroEmulator replaces System.out with its own console sink, which
     * headless goes nowhere. Hold on to the real one.
     */
    static final PrintStream OUT = new PrintStream(
        new java.io.FileOutputStream(java.io.FileDescriptor.out), true);

    public static void main(String[] args) throws Exception {
        try {
            run(args);
        } catch (Throwable t) {
            OUT.println("MEH FAILED: " + t);
            t.printStackTrace(OUT);
        }
        OUT.flush();
        System.exit(0);
    }

    private static void run(String[] args) throws Exception {
        PrintStream out = OUT;
        if (args.length < 1) {
            out.println("usage: MEHarness <jar> [script]");
            return;
        }

        deviceDisplay = new J2SEDeviceDisplay(CONTEXT);
        fontManager = new J2SEFontManager();
        inputMethod = new J2SEInputMethod();

        File jar = new File(args[0]);
        if (!jar.isFile()) {
            out.println("MEH no such jar: " + jar);
            return;
        }

        out.println("MEH booting " + jar.getName());
        Common common = new Common(CONTEXT);
        // initParams parses the same arguments the command line takes; the
        // bare path is the jar to run. Records live in memory so every run
        // starts from a clean account rather than resuming yesterday's hero.
        List<String> params = new ArrayList<String>();
        Collections.addAll(params,
            // relaxed delegation lets classes the jar does not contain fall
            // through to our classpath, which is how the Nokia UI stub in
            // tools/harness/nokia gets found
            "--appclassloader", "relaxed",
            // MicroEmulator's own chatter is not what we are testing
            "--quiet",
            // the same 240x320 screen FreeJ2ME gives it, so coordinates and
            // layout bugs seen here are the ones seen when playing
            "--resizableDevice", "240", "320",
            "--rms", System.getProperty("meh.rms", "memory"),
            jar.getAbsolutePath());
        common.initParams(params, null, J2SEDevice.class);
        common.initMIDlet(true);
        out.println("MEH started " + jar.getName());

        String script = args.length > 1 ? args[1] : "wait:5000,state";
        for (String step : script.split(",")) {
            String[] p = step.trim().split(":");
            try {
                if ("wait".equals(p[0])) {
                    Thread.sleep(Long.parseLong(p[1]));
                } else if ("key".equals(p[0])) {
                    key(Integer.parseInt(p[1]), 60);
                } else if ("hold".equals(p[0])) {
                    key(Integer.parseInt(p[1]), Long.parseLong(p[2]));
                } else if ("type".equals(p[0])) {
                    type(p[1]);
                } else if ("await".equals(p[0])) {
                    await(out, p[1], p.length > 2 ? Long.parseLong(p[2]) : 10000);
                } else if ("boot".equals(p[0])) {
                    boot(out, p.length > 1 ? p[1] : "Tester");
                } else if ("set".equals(p[0])) {
                    setText(Integer.parseInt(p[1]), step.split(":", 3)[2]);
                } else if ("pick".equals(p[0])) {
                    pick(Integer.parseInt(p[1]), Integer.parseInt(p[2]));
                } else if ("choose".equals(p[0])) {
                    choose(out, step.split(":", 2)[1]);
                } else if ("fields".equals(p[0])) {
                    DisplayAccess da = access();
                    Object target = "screen".equals(p.length > 1 ? p[1] : "")
                        ? currentScreen()
                        : (da == null ? null : da.getCurrent());
                    describe(out, target);
                } else if ("probe".equals(p[0])) {
                    DisplayAccess da = access();
                    Object canvas = da == null ? null : da.getCurrent();
                    out.println("PROBE " + p[1] + "=" + field(canvas, p[1]));
                } else if ("state".equals(p[0])) {
                    dump(out);
                } else if ("quit".equals(p[0])) {
                    break;
                } else {
                    out.println("MEH unknown step: " + step);
                }
            } catch (Exception e) {
                out.println("MEH step " + step + " failed: " + e);
            }
        }
        out.println("MEH done");
    }

    private static DisplayAccess access() {
        MIDletAccess ma = MIDletBridge.getMIDletAccess();
        return ma == null ? null : ma.getDisplayAccess();
    }

    /**
     * MIDP key codes go straight to the Canvas. Display.keyPressed would
     * queue them on the emulator's event thread instead; calling the
     * Displayable directly is what that thread ends up doing anyway, and
     * doing it synchronously keeps a scripted run reproducible.
     */
    private static void key(int code, long holdMs) throws Exception {
        DisplayAccess da = access();
        javax.microedition.lcdui.Displayable d = da == null ? null : da.getCurrent();
        if (d == null) {
            OUT.println("MEH no display yet, dropping key " + code);
            return;
        }
        java.lang.reflect.Method press = keyMethod(d, "keyPressed");
        java.lang.reflect.Method release = keyMethod(d, "keyReleased");
        if (Boolean.getBoolean("meh.verbose")) {
            OUT.println("MEH key " + code + " -> "
                + press.getDeclaringClass().getName() + " on "
                + d.getClass().getName());
        }
        try {
            press.invoke(d, Integer.valueOf(code));
            Thread.sleep(holdMs);
            release.invoke(d, Integer.valueOf(code));
        } catch (java.lang.reflect.InvocationTargetException e) {
            OUT.println("MEH key " + code + " threw: " + e.getCause());
            e.getCause().printStackTrace(OUT);
        }
        Thread.sleep(150);
    }

    private static java.lang.reflect.Method keyMethod(Object o, String name)
            throws Exception {
        for (Class<?> c = o.getClass(); c != null; c = c.getSuperclass()) {
            try {
                java.lang.reflect.Method m =
                    c.getDeclaredMethod(name, Integer.TYPE);
                m.setAccessible(true);
                return m;
            } catch (NoSuchMethodException e) {
                // keep walking up
            }
        }
        throw new NoSuchMethodException(name);
    }

    /**
     * Text entry is the one thing the desktop emulator has never done well
     * here, so spell names out on the numeric keypad the way a phone would.
     */
    private static void type(String text) throws Exception {
        for (char ch : text.toCharArray()) {
            char c = Character.toLowerCase(ch);
            if (c == '_' || c == ' ') {
                key('0', 60);
                continue;
            }
            int key = keyFor(c);
            int presses = pressesFor(key, c);
            for (int i = 0; i < presses; i++) {
                key(key, 60);
            }
            // wait out the multi-tap timer so the next letter starts fresh
            Thread.sleep(1200);
        }
    }

    private static final String[] PAD = {
        "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz",
    };

    private static int keyFor(char c) {
        for (int d = 2; d <= 9; d++) {
            if (PAD[d].indexOf(c) >= 0) {
                return '0' + d;
            }
        }
        return '0' + (c - '0');
    }

    private static int pressesFor(int key, char c) {
        int d = key - '0';
        return d >= 2 && d <= 9 ? PAD[d].indexOf(c) + 1 : 1;
    }

    /**
     * Block until the screen is the one named, rather than sleeping for a
     * guessed number of milliseconds. Screens are identified by their id in
     * e.u: 0 splash, 6 hero creation, 8 the in-game menu, 10 the map.
     */
    private static boolean await(PrintStream out, String spec, long timeoutMs)
            throws Exception {
        long until = System.currentTimeMillis() + timeoutMs;
        int want = Integer.parseInt(spec);
        while (System.currentTimeMillis() < until) {
            Object screen = currentScreen();
            Object u = field(screen, "u");
            if (u instanceof Integer && ((Integer) u).intValue() == want) {
                return true;
            }
            Thread.sleep(50);
        }
        out.print("MEH timed out waiting for u=" + want + "; ");
        dump(out);
        return false;
    }

    /**
     * Splash to walkable map in one step: the preamble every scripted run
     * shares, with a fresh hero so a run never depends on what the last one
     * left in the record store.
     */
    private static void boot(PrintStream out, String name) throws Exception {
        if (!await(out, "0", 15000)) {
            return;
        }
        key(-6, 60);
        if (await(out, "6", 15000)) {
            setText(0, name);
            pick(1, 0);
            choose(out, "Create hero");
        }
        if (!await(out, "8", 15000)) {
            return;
        }
        choose(out, entriesHave("Resume game") ? "Resume game" : "Start game");
        await(out, "10", 20000);
    }

    private static boolean entriesHave(String label) {
        Vector<?> items = entries();
        if (items == null) {
            return false;
        }
        for (Object o : items) {
            if (label.equals(labelOf(o))) {
                return true;
            }
        }
        return false;
    }

    /** The entries of the list screen currently on show. */
    private static Vector<?> entries() {
        Object screen = currentScreen();
        Object b = field(screen, "b");
        return b instanceof Vector ? (Vector<?>) b : null;
    }

    private static String labelOf(Object entry) {
        return String.valueOf(entry instanceof String ? entry : field(entry, "a"));
    }

    /** Fill a text field (f.d) without multi-tapping a name in one key at a time. */
    private static void setText(int index, String text) {
        Object item = entries().elementAt(index);
        Object buf = field(item, "d");
        if (buf instanceof StringBuffer) {
            StringBuffer sb = (StringBuffer) buf;
            sb.setLength(0);
            sb.append(text);
        } else {
            OUT.println("MEH entry " + index + " is not a text field");
        }
    }

    /** Select one of a chooser's options (f.j indexes f.i). */
    private static void pick(int index, int option) throws Exception {
        Object item = entries().elementAt(index);
        Field j = item.getClass().getDeclaredField("j");
        j.setAccessible(true);
        j.setInt(item, option);
    }

    /**
     * Activate a menu entry by its label, the way the list screen does when
     * fire is pressed. Going through the canvas's own command handler rather
     * than steering a cursor with key events keeps scripts readable and
     * independent of how many rows a menu happens to have.
     */
    private static void choose(PrintStream out, String label) throws Exception {
        Object screen = currentScreen();
        Vector<?> items = entries();
        if (items == null) {
            out.println("MEH nothing to choose on " + screen.getClass().getSimpleName());
            return;
        }
        for (int i = 0; i < items.size(); i++) {
            Object entry = items.elementAt(i);
            if (!label.equals(labelOf(entry))) {
                continue;
            }
            DisplayAccess da = access();
            Object canvas = da.getCurrent();
            for (java.lang.reflect.Method m
                    : canvas.getClass().getDeclaredMethods()) {
                Class<?>[] sig = m.getParameterTypes();
                if (sig.length == 3 && sig[1] == Integer.TYPE
                        && sig[2] == Object.class
                        && sig[0].isInstance(screen)) {
                    m.setAccessible(true);
                    m.invoke(canvas, screen, Integer.valueOf(i), entry);
                    return;
                }
            }
            out.println("MEH no command handler on "
                + canvas.getClass().getName());
            return;
        }
        List<String> have = new ArrayList<String>();
        for (Object o : items) {
            have.add(labelOf(o));
        }
        out.println("MEH no entry \"" + label + "\" in " + have);
    }

    private static void dump(PrintStream out) {
        Object screen = currentScreen();
        if (screen == null) {
            out.println("STATE screen=none");
            return;
        }
        String cls = screen.getClass().getSimpleName();
        StringBuilder sb = new StringBuilder("STATE screen=" + cls);
        DisplayAccess da = access();
        Object shown = da == null ? null : da.getCurrent();
        if (shown != null && shown != screen) {
            sb.append(" on=").append(shown.getClass().getSimpleName());
            Object stack = field(shown, "a");
            if (stack instanceof java.util.Vector) {
                sb.append(" stack=").append(((java.util.Vector<?>) stack).size());
            }
        }

        // every screen extends e, which carries the screen id in u
        Object u = field(screen, "u");
        if (u instanceof Integer) {
            sb.append(" u=").append(u);
        }

        if ("d".equals(cls)) {
            for (String[] f : MAP_FIELDS) {
                Object v = field(screen, f[0]);
                if (v != null) {
                    sb.append(' ').append(f[1]).append('=').append(v);
                }
            }
            Object aF = field(screen, "aF");
            if (aF instanceof Vector) {
                sb.append(" entities=").append(((Vector<?>) aF).size());
            }
        } else if ("c".equals(cls)) {
            Object items = field(screen, "b");
            if (items instanceof Vector) {
                List<String> labels = new ArrayList<String>();
                for (Object o : (Vector<?>) items) {
                    labels.add(labelOf(o));
                }
                sb.append(" items=").append(labels);
            }
        } else if ("h".equals(cls)) {
            sb.append(" text=").append(field(screen, "b"));
        }
        out.println(sb);
    }

    /** Every field of an object and its superclasses, for finding one's way. */
    private static void describe(PrintStream out, Object o) {
        if (o == null) {
            out.println("FIELDS none");
            return;
        }
        out.println("FIELDS of " + o.getClass().getName());
        for (Class<?> c = o.getClass(); c != null && c != Object.class;
                c = c.getSuperclass()) {
            for (Field f : c.getDeclaredFields()) {
                try {
                    f.setAccessible(true);
                    Object v = f.get(o);
                    String shown = v instanceof java.util.Vector
                        ? "Vector(" + ((java.util.Vector<?>) v).size() + ")"
                        : String.valueOf(v);
                    if (shown.length() > 90) {
                        shown = shown.substring(0, 90) + "...";
                    }
                    out.println("  " + c.getSimpleName() + "." + f.getName()
                        + " : " + f.getType().getSimpleName() + " = " + shown);
                } catch (Exception e) {
                    // an inaccessible field tells us nothing; skip it
                }
            }
        }
    }

    private static Object currentScreen() {
        try {
            DisplayAccess da = access();
            Object d = da == null ? null : da.getCurrent();
            // The Displayable is always the game's single Canvas. g.h is the
            // screen actually on show (g.g is the one queued to replace it,
            // g.a the stack underneath). Not g.c(), which returns the bottom
            // of that stack; and not a plain field lookup for "h", because
            // the splash subclass declares a boolean of the same name and
            // shadows it.
            Object h = objectField(d, "h");
            return h != null ? h : d;
        } catch (Throwable t) {
            return null;
        }
    }

    /**
     * The first field of this name holding an object rather than a
     * primitive, walking up from the object's own class.
     */
    private static Object objectField(Object o, String name) {
        for (Class<?> c = o == null ? null : o.getClass(); c != null;
                c = c.getSuperclass()) {
            try {
                Field f = c.getDeclaredField(name);
                if (f.getType().isPrimitive()) {
                    continue;
                }
                f.setAccessible(true);
                return f.get(o);
            } catch (NoSuchFieldException e) {
                // keep walking up
            } catch (Exception e) {
                return null;
            }
        }
        return null;
    }

    private static java.lang.reflect.Method method(Object o, String name) {
        if (o == null) {
            return null;
        }
        for (Class<?> c = o.getClass(); c != null; c = c.getSuperclass()) {
            try {
                java.lang.reflect.Method m = c.getDeclaredMethod(name);
                m.setAccessible(true);
                return m;
            } catch (NoSuchMethodException e) {
                // keep walking up
            }
        }
        return null;
    }

    private static Object field(Object o, String name) {
        if (o == null) {
            return null;
        }
        for (Class<?> c = o.getClass(); c != null; c = c.getSuperclass()) {
            try {
                Field f = c.getDeclaredField(name);
                f.setAccessible(true);
                return f.get(o);
            } catch (NoSuchFieldException e) {
                // keep walking up
            } catch (Exception e) {
                return null;
            }
        }
        return null;
    }
}
