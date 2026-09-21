import java.io.File;
import java.io.PrintStream;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;
import java.util.Vector;

import org.recompile.mobile.Mobile;
import org.recompile.mobile.MobilePlatform;

/**
 * Run the MIDlet headless under FreeJ2ME, drive it from a script, and print
 * its state.
 *
 * Superseded by MEHarness, which does the same job under MicroEmulator and
 * actually reaches the game. This one stops at the front door: FreeJ2ME's
 * Display queues setCurrent on an event thread that, with no AWT frontend to
 * wake it, never runs, so MobilePlatform.displayable stays null and there is
 * nothing to drive. Kept because FreeJ2ME is still the emulator we play on,
 * and a fix there would be worth having.
 *
 * The emulator is a slow way to test a server: fifteen seconds to boot, then
 * synthetic keystrokes and screenshots to find out what happened. But
 * FreeJ2ME is a plain Java library implementing MIDP — the AWT window is only
 * one frontend — so the game can be run in-process with no window at all, and
 * its fields read directly.
 *
 *   java -Djava.awt.headless=true \
 *        -cp tools/harness:tools/freej2me-net:tools/freej2me/freej2me.jar \
 *        Harness run/EoE-ShiparsForge.jar "wait:3000,key:-6,wait:1500,state"
 *
 * Script steps, comma separated:
 *   wait:MS      let the game run
 *   key:CODE     press and release a MIDP key code
 *   hold:CODE:MS hold one down (exploration movement is velocity based)
 *   state        print the current screen's fields
 *   quit         stop
 *
 * Reading state means reflecting over obfuscated single-letter fields, so the
 * names below are from the decompiled source in decompiled-vf/ and are only
 * valid for these builds.
 */
public class Harness {

    /** d.java's fields, as recovered in decompiled-vf/d.java. */
    private static final String[][] MAP_FIELDS = {
        {"I", "location"}, {"Q", "heroX"}, {"R", "heroY"},
        {"T", "loaded"}, {"c", "inCombat"}, {"k", "needsTurn"},
        {"ab", "inputMode"}, {"ag", "turnClock"}, {"Y", "barSlot"},
    };

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.out.println("usage: Harness <jar> [script]");
            return;
        }
        PrintStream out = System.out;

        Mobile.lcdWidth = 240;
        Mobile.lcdHeight = 320;
        MobilePlatform platform = new MobilePlatform(240, 320);
        // The painter is what the AWT frontend uses to blit the backbuffer.
        // Headless, we simply never draw.
        Mobile.setPlatform(platform, new Runnable() { public void run() { } });
        platform.setPainter(new Runnable() { public void run() { } });

        // MobilePlatform.load() takes a URL, not a path
        File jar = new File(args[0]);
        if (!platform.load(jar.toURI().toURL().toString())) {
            out.println("HARNESS load failed: " + jar);
            return;
        }
        out.println("HARNESS loaded " + jar.getName());
        // runJar() swallows exceptions into a log we cannot see headless, so
        // start the loader ourselves and report anything it throws.
        try {
            Object loader = field(platform, "loader");
            out.println("HARNESS loader=" + loader);
            javax.microedition.media.Manager.prepareMediaEngine();
            out.println("HARNESS media ready");
            loader.getClass().getMethod("start").invoke(loader);
            Object midlet = field(loader, "midletInst");
            out.println("HARNESS midlet=" + midlet);
            if (midlet != null && MobilePlatform.displayable == null) {
                // start() reports success even when startApp never ran, so
                // call it directly and let anything it throws surface.
                java.lang.reflect.Method sa =
                    midlet.getClass().getDeclaredMethod("startApp");
                sa.setAccessible(true);
                sa.invoke(midlet);
                out.println("HARNESS startApp invoked");

                // FreeJ2ME's Display queues setCurrent but does not notify()
                // the event thread. With an AWT frontend a paint event wakes
                // it a moment later; headless nothing ever does, so the
                // request sits there and the game never gets a screen.
                // callSerially() does notify, so it acts as the poke.
                javax.microedition.lcdui.Display disp =
                    javax.microedition.lcdui.Display.getDisplay(
                        (javax.microedition.midlet.MIDlet) midlet);
                for (int i = 0; i < 20 && MobilePlatform.displayable == null; i++) {
                    disp.callSerially(new Runnable() { public void run() { } });
                    Thread.sleep(50);
                }
                out.println("HARNESS displayable=" + MobilePlatform.displayable);
            }
        } catch (Throwable t) {
            Throwable c = t.getCause() != null ? t.getCause() : t;
            out.println("HARNESS start FAILED: " + c);
            c.printStackTrace(out);
        }

        String script = args.length > 1 ? args[1] : "wait:4000,state";
        for (String step : script.split(",")) {
            String[] p = step.trim().split(":");
            String cmd = p[0];
            try {
                if ("wait".equals(cmd)) {
                    Thread.sleep(Long.parseLong(p[1]));
                } else if ("key".equals(cmd)) {
                    int code = Integer.parseInt(p[1]);
                    MobilePlatform.keyPressed(code);
                    Thread.sleep(60);
                    MobilePlatform.keyReleased(code);
                    Thread.sleep(200);
                } else if ("hold".equals(cmd)) {
                    int code = Integer.parseInt(p[1]);
                    MobilePlatform.keyPressed(code);
                    Thread.sleep(Long.parseLong(p[2]));
                    MobilePlatform.keyReleased(code);
                    Thread.sleep(200);
                } else if ("state".equals(cmd)) {
                    dumpState(out);
                } else if ("quit".equals(cmd)) {
                    break;
                } else {
                    out.println("HARNESS unknown step: " + step);
                }
            } catch (Exception e) {
                out.println("HARNESS step " + step + " failed: " + e);
            }
        }
        out.println("HARNESS done");
        System.exit(0);
    }

    /** Print whatever we can read off the screen the game is currently on. */
    private static void dumpState(PrintStream out) {
        Object screen = currentScreen();
        if (screen == null) {
            out.println("STATE screen=none");
            return;
        }
        String cls = screen.getClass().getSimpleName();
        StringBuilder sb = new StringBuilder("STATE screen=" + cls);

        // every screen extends e, which carries the screen id in u
        Integer u = intField(screen, "u");
        if (u != null) {
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
                    labels.add(String.valueOf(o instanceof String ? o
                            : field(o, "a")));
                }
                sb.append(" items=").append(labels);
            }
        } else if ("h".equals(cls)) {
            sb.append(" text=").append(field(screen, "b"));
        }
        out.println(sb);
    }

    private static Object currentScreen() {
        try {
            Object d = MobilePlatform.displayable;
            // the game's own canvas keeps the active screen in g.h
            Object h = field(d, "h");
            return h != null ? h : d;
        } catch (Throwable t) {
            return null;
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

    private static Integer intField(Object o, String name) {
        Object v = field(o, name);
        return v instanceof Integer ? (Integer) v : null;
    }
}
