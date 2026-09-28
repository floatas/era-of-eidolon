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

    static final int WIDTH = 240;
    static final int HEIGHT = 320;

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
            "--resizableDevice", String.valueOf(WIDTH), String.valueOf(HEIGHT),
            "--rms", System.getProperty("meh.rms", "memory"),
            jar.getAbsolutePath());
        common.initParams(params, null, J2SEDevice.class);
        common.initMIDlet(true);
        out.println("MEH started " + jar.getName());

        String script = args.length > 1 ? args[1] : "wait:5000,state";
        if ("-".equals(script)) {
            // Interactive: one line of steps at a time from stdin, answered
            // with "MEH ready" when it is done, so a driver can look at what
            // happened before it decides what to do next.
            java.io.BufferedReader in = new java.io.BufferedReader(
                new java.io.InputStreamReader(System.in));
            out.println("MEH ready");
            out.flush();
            String line;
            while ((line = in.readLine()) != null) {
                if ("quit".equals(line.trim())) {
                    break;
                }
                runSteps(out, line);
                out.println("MEH ready");
                out.flush();
            }
            out.println("MEH done");
            return;
        }
        runSteps(out, script);
        out.println("MEH done");
    }

    private static void runSteps(PrintStream out, String script) {
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
                } else if ("shot".equals(p[0])) {
                    shot(out, step.split(":", 2)[1]);
                } else if ("film".equals(p[0])) {
                    film(out, p[1], p.length > 2 ? Integer.parseInt(p[2]) : 80);
                } else if ("stopfilm".equals(p[0])) {
                    stopFilm(out);
                } else if ("dismiss".equals(p[0])) {
                    dismiss(out);
                } else if ("tile".equals(p[0])) {
                    tile(out, Integer.parseInt(p[1]), Integer.parseInt(p[2]));
                } else if ("goto".equals(p[0])) {
                    walkTo(out, Integer.parseInt(p[1]), Integer.parseInt(p[2]),
                           p.length > 3 ? Long.parseLong(p[3]) : 15000);
                } else if ("path".equals(p[0])) {
                    pathTo(out, Integer.parseInt(p[1]), Integer.parseInt(p[2]),
                           p.length > 3 ? Long.parseLong(p[3]) : 60000);
                } else if ("states".equals(p[0])) {
                    Object ds = field(currentScreen(), "i");
                    StringBuilder sb = new StringBuilder("STATES");
                    for (String id : p[1].split("/")) {
                        int n = Integer.parseInt(id);
                        sb.append(" ").append(n).append("=")
                          .append(ds instanceof byte[] && n < ((byte[]) ds).length
                                  ? String.valueOf(((byte[]) ds)[n]) : "?");
                    }
                    Object near = field(currentScreen(), "S");
                    sb.append("  nearby-actions=").append(near instanceof Vector ? ((Vector<?>) near).size() : -1);
                    out.println(sb);
                } else if ("where".equals(p[0])) {
                    // live tiles of the drawn creatures: (h + 128) >> 8, as d.java
                    // reports them to the server
                    Object drawn = field(currentScreen(), "aF");
                    if (drawn instanceof Vector) {
                        for (Object e : (Vector<?>) drawn) {
                            Object b = field(e, "b"), h = field(e, "h"), i = field(e, "i");
                            if (b instanceof Integer && h instanceof Integer && i instanceof Integer) {
                                out.println("WHERE " + b + " " + (((Integer) h + 128) >> 8)
                                    + " " + (((Integer) i + 128) >> 8));
                            }
                        }
                    }
                } else if ("act".equals(p[0])) {
                    act(out, step.split(":", 2)[1]);
                } else if ("entities".equals(p[0])) {
                    entities(out);
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
                } else if ("item".equals(p[0])) {
                    Vector<?> items = entries();
                    int n = Integer.parseInt(p[1]);
                    if (items == null || n >= items.size()) {
                        out.println("MEH no item " + n);
                    } else {
                        activate(out, n, items.elementAt(n));
                    }
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
     * Paint the game into a PNG. Headless the emulator never draws anything,
     * but the Canvas will paint on demand into any Graphics, and half the
     * bugs in this project were things that looked right in a field dump and
     * wrong on screen: an empty health bar, townsfolk standing on a tile the
     * camera never showed.
     */
    // Filming: a daemon thread that keeps painting the live canvas into
    // numbered frames while the rest of the script plays. One shot at a time
    // would only ever catch the pauses between steps, and the walk cycles and
    // the turn clock are the parts worth seeing.
    private static volatile boolean filming = false;
    private static Thread camera = null;

    private static void film(final PrintStream out, final String dir,
                             final int everyMs) {
        if (filming) {
            return;
        }
        filming = true;
        final File folder = new File(dir);
        folder.mkdirs();
        camera = new Thread(new Runnable() {
            public void run() {
                int n = 0;
                while (filming) {
                    try {
                        capture(new File(folder,
                                String.format("f%05d.png", n++)).getPath());
                    } catch (Throwable t) {
                        // a frame mid-repaint is not worth stopping for
                    }
                    try {
                        Thread.sleep(everyMs);
                    } catch (InterruptedException e) {
                        return;
                    }
                }
            }
        });
        camera.setDaemon(true);
        camera.start();
        out.println("FILM started " + folder.getPath()
                    + " every " + everyMs + "ms");
    }

    private static void stopFilm(PrintStream out) throws Exception {
        filming = false;
        if (camera != null) {
            camera.join(2000);
            camera = null;
        }
        out.println("FILM stopped");
    }

    private static void shot(PrintStream out, String path) throws Exception {
        String where = capture(path);
        out.println(where == null ? "SHOT nothing to paint" : "SHOT " + where);
    }

    /** Paint the current canvas into a PNG. Returns where it landed. */
    private static String capture(String path) throws Exception {
        DisplayAccess da = access();
        Object canvas = da == null ? null : da.getCurrent();
        if (canvas == null) {
            return null;
        }
        javax.microedition.lcdui.Image buffer =
            javax.microedition.lcdui.Image.createImage(WIDTH, HEIGHT);
        java.lang.reflect.Method paint = canvas.getClass().getMethod(
            "paint", javax.microedition.lcdui.Graphics.class);
        paint.setAccessible(true);
        paint.invoke(canvas, buffer.getGraphics());

        Object impl = field(buffer, "image");
        if (impl == null) {
            impl = buffer;
        }
        java.lang.reflect.Method getImage =
            impl.getClass().getMethod("getImage");
        java.awt.Image awt = (java.awt.Image) getImage.invoke(impl);
        java.awt.image.BufferedImage png = new java.awt.image.BufferedImage(
            WIDTH, HEIGHT, java.awt.image.BufferedImage.TYPE_INT_RGB);
        java.awt.Graphics g = png.getGraphics();
        g.drawImage(awt, 0, 0, null);
        g.dispose();
        File file = new File(path);
        if (file.getParentFile() != null) {
            file.getParentFile().mkdirs();
        }
        javax.imageio.ImageIO.write(png, "png", file);
        return file.getPath();
    }

    /**
     * What the map screen is actually drawing, and why. d.j holds one row per
     * creature in the world and d.l its node state; a creature is loaded when
     * its row names this location, but only drawn when its state is 2, so a
     * creature that is present and missing from the draw list is a node-state
     * problem rather than a placement one.
     */
    private static void entities(PrintStream out) {
        Object screen = currentScreen();
        if (!"d".equals(screen.getClass().getSimpleName())) {
            out.println("ENTITIES not on the map");
            return;
        }
        Object here = field(screen, "I");
        Object rows = field(screen, "j");
        Object states = field(screen, "l");
        Object drawn = field(screen, "aF");

        java.util.Set<Integer> shown = new java.util.HashSet<Integer>();
        if (drawn instanceof Vector) {
            for (Object e : (Vector<?>) drawn) {
                Object b = field(e, "b");
                if (b instanceof Integer) {
                    shown.add((Integer) b);
                }
            }
        }

        out.println("ENTITIES location=" + here
            + " drawn=" + (drawn instanceof Vector ? ((Vector<?>) drawn).size() : -1));
        if (!(rows instanceof byte[][]) || !(states instanceof byte[])) {
            out.println("  no creature table");
            return;
        }
        for (byte[] row : (byte[][]) rows) {
            int id = row[0] & 255;
            int loc = row[1];
            int state = ((byte[]) states)[id];
            out.println("  node " + id + " loc=" + loc + " state=" + state
                + " sheet=" + (row[12] & 255)
                + " anim=" + (row[13] & 255)
                + (shown.contains(Integer.valueOf(id)) ? " DRAWN" : "")
                + "  " + hex(row));
        }
    }

    private static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) {
            sb.append(Character.forDigit((x >> 4) & 15, 16));
            sb.append(Character.forDigit(x & 15, 16));
        }
        return sb.toString();
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
     * Get back to the map. An entity can greet you the moment a location
     * loads, and on the map the soft key opens the action list rather than
     * closing anything, so a dialog has to be popped rather than keyed away.
     */
    private static void dismiss(PrintStream out) throws Exception {
        for (int i = 0; i < 6; i++) {
            Object screen = currentScreen();
            if (screen == null || "d".equals(screen.getClass().getSimpleName())) {
                return;
            }
            // "Entering fight" (screen 36) must be answered, never popped:
            // d.a(String, byte[]) sets d.aw when it opens, and only a fight's
            // end clears it, so a popped one blocks every later fight.
            if (isFightOffer(screen)) {
                out.println("FIGHT offered");
                return;
            }
            // say what is being closed: a stack of dialogs (the fight's
            // "X attacks", "Congratulations", the Battle report) goes in one
            // dismiss, and the script still has to read them
            if ("h".equals(screen.getClass().getSimpleName())) {
                Object text = field(screen, "a");
                if (text != null) {
                    out.println("SAID " + String.valueOf(text).replace('\n', '|'));
                }
            }
            DisplayAccess da = access();
            pop(da == null ? null : da.getCurrent(), screen);
            Thread.sleep(250);
        }
        out.print("MEH could not get back to the map; ");
        dump(out);
    }

    /**
     * Read a tile out of the client's LIVE map (d.aA, width d.ay), which is
     * the only way to see whether a kind 6 patch actually landed.
     */
    private static void tile(PrintStream out, int x, int y) {
        Object screen = currentScreen();
        Object tiles = field(screen, "aA");
        Object width = field(screen, "ay");
        if (!(tiles instanceof byte[]) || !(width instanceof Integer)) {
            out.println("TILE not on the map");
            return;
        }
        byte[] a = (byte[]) tiles;
        int w = (Integer) width;
        int i = y * w + x;
        if (i < 0 || i >= a.length) {
            out.println("TILE " + x + "," + y + " out of range");
            return;
        }
        int t = a[i] & 255;
        out.println("TILE " + x + "," + y + " = 0x"
            + Integer.toHexString(t) + "  ground " + (t & 15)
            + "  obstacle " + ((t & 240) >> 4));
    }

    /**
     * Walk to a tile. Movement is velocity based and the game advances on its
     * own thread, so a fixed hold moves an unpredictable distance; steering
     * by the hero's actual position each step is what makes a scripted walk
     * repeatable. Stops early if the location changes — crossing a doorway is
     * usually the point.
     */
    private static void walkTo(PrintStream out, int tx, int ty, long timeoutMs)
            throws Exception {
        long until = System.currentTimeMillis() + timeoutMs;
        Object start = field(currentScreen(), "I");
        int stalled = 0;
        int[] was = {-1, -1};
        while (System.currentTimeMillis() < until) {
            Object screen = currentScreen();
            if (screen != null
                    && !"d".equals(screen.getClass().getSimpleName())) {
                // something spoke to us on the way — Hrom calling for help
                // the moment you leave the Village. Read it and walk on;
                // but a creature that noticed us is a fight, not a message
                if (isFightOffer(screen)) {
                    out.println("FIGHT offered");
                    return;
                }
                dismiss(out);
                screen = currentScreen();
            }
            Object loc = field(screen, "I");
            if (loc != null && !loc.equals(start)) {
                return;                       // through a doorway
            }
            Object ox = field(screen, "Q"), oy = field(screen, "R");
            if (!(ox instanceof Integer) || !(oy instanceof Integer)) {
                return;
            }
            int x = (Integer) ox, y = (Integer) oy;
            if (x == tx && y == ty) {
                return;
            }
            stalled = (x == was[0] && y == was[1]) ? stalled + 1 : 0;
            if (stalled > 12) {
                out.println("MEH stuck at " + x + "," + y
                    + " heading for " + tx + "," + ty);
                return;
            }
            was[0] = x;
            was[1] = y;
            // One axis at a time. When that axis is blocked — a rock, the
            // water's edge — try the other for a while rather than pressing
            // into the obstacle forever.
            boolean useX = (x != tx) != (stalled >= 3 && y != ty);
            int code = useX ? (x < tx ? -4 : -3) : (y < ty ? -2 : -1);
            // ease off on the last tile, or a long hold overshoots and the
            // walk spends the rest of its time oscillating
            int left = Math.abs(useX ? tx - x : ty - y);
            key(code, left <= 1 ? 140 : 400);
        }
    }

    /**
     * Screens the walker and dismiss hand back to the script instead of
     * closing: "Entering fight" (36), and "Raises left" (14) with its "Add"
     * confirmation (15). Closing a raise screen banks the points unspent.
     */
    private static boolean isFightOffer(Object screen) {
        Object u = field(screen, "u");
        if (!(u instanceof Integer)) {
            return false;
        }
        int id = ((Integer) u).intValue();
        return id == 36 || id == 14 || id == 15;
    }

    /** The phone's own walk test, d.b(x, y), on its live map. */
    private static boolean walkable(Object screen, int x, int y) throws Exception {
        for (java.lang.reflect.Method m : screen.getClass().getDeclaredMethods()) {
            Class<?>[] sig = m.getParameterTypes();
            if ("b".equals(m.getName()) && sig.length == 2
                    && sig[0] == Integer.TYPE && sig[1] == Integer.TYPE
                    && m.getReturnType() == Boolean.TYPE) {
                m.setAccessible(true);
                return ((Boolean) m.invoke(screen, x, y)).booleanValue();
            }
        }
        return false;
    }

    /**
     * Breadth-first over the phone's live map, straight steps only, from the
     * hero to (tx, ty) or, if that tile cannot be stood on, to the nearest
     * one beside it. Returns the tiles to walk, first step first, or null.
     */
    private static List<int[]> route(Object screen, int sx, int sy, int tx, int ty)
            throws Exception {
        int w = (Integer) field(screen, "ay"), h = (Integer) field(screen, "az");
        boolean exact = walkable(screen, tx, ty);
        int[] prev = new int[w * h];
        java.util.Arrays.fill(prev, -2);
        java.util.ArrayDeque<Integer> q = new java.util.ArrayDeque<Integer>();
        prev[sy * w + sx] = -1;
        q.add(sy * w + sx);
        int goal = -1;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!q.isEmpty()) {
            int c = q.poll(), cx = c % w, cy = c / w;
            boolean there = exact ? (cx == tx && cy == ty)
                : Math.max(Math.abs(cx - tx), Math.abs(cy - ty)) <= 1;
            if (there) {
                goal = c;
                break;
            }
            for (int[] d : dirs) {
                int nx = cx + d[0], ny = cy + d[1];
                if (nx < 0 || ny < 0 || nx >= w || ny >= h) {
                    continue;
                }
                int n = ny * w + nx;
                if (prev[n] != -2 || !walkable(screen, nx, ny)) {
                    continue;
                }
                prev[n] = c;
                q.add(n);
            }
        }
        if (goal < 0) {
            return null;
        }
        java.util.LinkedList<int[]> path = new java.util.LinkedList<int[]>();
        for (int c = goal; prev[c] != -1; c = prev[c]) {
            path.addFirst(new int[] {c % w, c / w});
        }
        return path;
    }

    /**
     * Walk to a tile by the phone's own map, round walls and water, one step
     * at a time so a creature or a patch in the way is seen on the next plan.
     * Stops at a doorway, like goto.
     */
    private static void pathTo(PrintStream out, int tx, int ty, long timeoutMs)
            throws Exception {
        long until = System.currentTimeMillis() + timeoutMs;
        Object start = field(currentScreen(), "I");
        while (System.currentTimeMillis() < until) {
            Object screen = currentScreen();
            if (screen != null && !"d".equals(screen.getClass().getSimpleName())) {
                if (isFightOffer(screen)) {
                    out.println("PATH stopped: a fight is offered");
                    return;
                }
                dismiss(out);
                screen = currentScreen();
                if (screen != null && !"d".equals(screen.getClass().getSimpleName())) {
                    out.println("PATH stopped: a dialog is up");
                    return;
                }
            }
            Object loc = field(screen, "I");
            if (loc != null && !loc.equals(start)) {
                out.println("PATH through a doorway to " + loc);
                return;
            }
            int x = (Integer) field(screen, "Q"), y = (Integer) field(screen, "R");
            List<int[]> path = route(screen, x, y, tx, ty);
            if (path == null) {
                out.println("PATH none from " + x + "," + y + " to " + tx + "," + ty);
                return;
            }
            if (path.isEmpty()) {
                out.println("PATH arrived " + x + "," + y);
                return;
            }
            int[] next = path.get(0);
            walkTo(out, next[0], next[1], 4000);
        }
        out.println("PATH timed out heading for " + tx + "," + ty);
    }

    /** Open the phone's "Choose action" list (fire) and pick an entry. */
    private static void act(PrintStream out, String label) throws Exception {
        key(-5, 60);
        Thread.sleep(300);
        Object screen = currentScreen();
        Object u = field(screen, "u");
        if (!(u instanceof Integer) || ((Integer) u).intValue() != 32) {
            out.println("ACT no action list here (screen " + u + ")");
            return;
        }
        Vector<?> items = entries();
        List<String> have = new ArrayList<String>();
        for (Object o : items) {
            have.add(labelOf(o));
        }
        if (!have.contains(label)) {
            choose(out, "Cancel");
            out.println("ACT missing \"" + label + "\" in " + have);
            return;
        }
        choose(out, label);
        out.println("ACT " + label);
    }

    /** Wait for whichever of these screens turns up first; -1 if none does. */
    private static int awaitAny(PrintStream out, int[] want, long timeoutMs)
            throws Exception {
        long until = System.currentTimeMillis() + timeoutMs;
        while (System.currentTimeMillis() < until) {
            Object u = field(currentScreen(), "u");
            if (u instanceof Integer) {
                for (int w : want) {
                    if (((Integer) u).intValue() == w) {
                        return w;
                    }
                }
            }
            Thread.sleep(50);
        }
        out.print("MEH timed out waiting for a screen; ");
        dump(out);
        return -1;
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
        // With MEH_RMS=file the account token survives the run, so opcode 1
        // answers with "Select hero" (screen 5) rather than hero creation
        // (screen 6). Handle both, so the same script works cold or warm.
        int screen = awaitAny(out, new int[] {5, 6, 8}, 15000);
        if (screen == 6) {
            setText(0, name);
            pick(1, 0);
            choose(out, "Create hero");
        } else if (screen == 5) {
            choose(out, entriesHave(name) ? name : labelOf(entries().elementAt(0)));
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

    /**
     * What the current screen offers. A list screen keeps its rows in a
     * Vector; a dialog keeps its buttons in a String[].
     */
    private static Vector<?> entries() {
        Object screen = currentScreen();
        Object b = field(screen, "b");
        if (b instanceof Vector) {
            return (Vector<?>) b;
        }
        Object buttons = field(screen, "e");
        if (buttons instanceof String[]) {
            Vector<Object> v = new Vector<Object>();
            for (String s : (String[]) buttons) {
                v.addElement(s);
            }
            return v;
        }
        return null;
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
        DisplayAccess access = access();
        Object top = access == null ? null : access.getCurrent();
        // Back and Cancel are never passed to the command handler — the
        // screen pops itself on the key press — and a dialog with no buttons
        // still has to be dismissable.
        if ("Back".equals(label) || "Cancel".equals(label)) {
            pop(top, screen);
            return;
        }
        if (items == null) {
            out.println("MEH nothing to choose on "
                + screen.getClass().getSimpleName());
            return;
        }
        for (int i = 0; i < items.size(); i++) {
            Object entry = items.elementAt(i);
            if (!label.equals(labelOf(entry))) {
                continue;
            }
            Object canvas = top;
            for (java.lang.reflect.Method m
                    : canvas.getClass().getDeclaredMethods()) {
                Class<?>[] sig = m.getParameterTypes();
                if (sig.length == 3 && sig[1] == Integer.TYPE
                        && sig[2] == Object.class
                        && sig[0].isInstance(screen)) {
                    m.setAccessible(true);
                    m.invoke(canvas, screen, Integer.valueOf(i), entry);
                    // the handler only queues the next screen; g.keyPressed
                    // commits it with d(), and so must we
                    method(canvas, "d").invoke(canvas);
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

    /** Activate one entry of the current list by position (choose, by index). */
    private static void activate(PrintStream out, int i, Object entry) throws Exception {
        Object screen = currentScreen();
        // Put the list's cursor (c.c) on the row first, as the keys would.
        // Screens that act on "the selected row" later (Equip reads f(),
        // the row under the cursor) otherwise act on row 0.
        if (screen != null && "c".equals(screen.getClass().getSimpleName())) {
            setField(screen, "c", Integer.valueOf(i));
        }
        DisplayAccess access = access();
        Object canvas = access == null ? null : access.getCurrent();
        for (java.lang.reflect.Method m : canvas.getClass().getDeclaredMethods()) {
            Class<?>[] sig = m.getParameterTypes();
            if (sig.length == 3 && sig[1] == Integer.TYPE && sig[2] == Object.class
                    && sig[0].isInstance(screen)) {
                m.setAccessible(true);
                m.invoke(canvas, screen, Integer.valueOf(i), entry);
                method(canvas, "d").invoke(canvas);
                return;
            }
        }
        out.println("MEH no command handler on " + canvas.getClass().getName());
    }

    /** g.b(e) drops a screen; g.d() commits the swap, as keyPressed does. */
    private static void pop(Object canvas, Object screen) throws Exception {
        for (java.lang.reflect.Method m : canvas.getClass().getMethods()) {
            Class<?>[] sig = m.getParameterTypes();
            if ("b".equals(m.getName()) && sig.length == 1
                    && sig[0].isInstance(screen)) {
                m.setAccessible(true);
                m.invoke(canvas, screen);
                break;
            }
        }
        method(canvas, "d").invoke(canvas);
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
            // h.a is the body text; h.b is a layout counter, not the message
            String text = String.valueOf(field(screen, "a"));
            sb.append(" text=").append(text.replace('\n', '|'));
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

    private static void setField(Object o, String name, Object value) {
        for (Class<?> c = o.getClass(); c != null; c = c.getSuperclass()) {
            try {
                Field f = c.getDeclaredField(name);
                f.setAccessible(true);
                f.set(o, value);
                return;
            } catch (NoSuchFieldException e) {
                // keep walking up
            } catch (Exception e) {
                return;
            }
        }
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
