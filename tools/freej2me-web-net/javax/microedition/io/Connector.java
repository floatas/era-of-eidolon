package javax.microedition.io;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import javax.wireless.messaging.impl.MessageConnectionImpl;

import org.recompile.mobile.Mobile;

/**
 * freej2me-web's Connector, with HTTP added.
 *
 * Upstream this class throws ConnectionNotFoundException for every scheme but
 * sms://, so no MIDlet that talks to a server can run in the web build. Only
 * the http/https branch below is new; everything else matches the original
 * behaviour (resource: streams, sms:, and the dummy streams).
 */
public class Connector {
    public static final int READ = 1;
    public static final int READ_WRITE = 3;
    public static final int WRITE = 2;

    public static InputStream openInputStream(String name) {
        if (name.startsWith("resource:")) {
            return Mobile.getPlatform().loader.getMIDletResourceAsSiemensStream(
                    name.substring(9).replaceAll("\\\\", "/"));
        }
        System.out.println("Faked InputStream for " + name);
        return new fakeIS();
    }

    public static DataInputStream openDataInputStream(String name) {
        System.out.println("Faked DataInputStream: " + name);
        return new DataInputStream(new fakeIS());
    }

    public static Connection open(String name) throws IOException {
        if (name != null && (name.startsWith("http://") || name.startsWith("https://"))) {
            return new HttpConnectionImpl(name);
        } else if (name != null && name.startsWith("sms://")) {
            return new MessageConnectionImpl(name);
        } else {
            throw new ConnectionNotFoundException();
        }
    }

    public static Connection open(String name, int mode) throws IOException {
        return open(name);
    }

    public static Connection open(String name, int mode, boolean timeouts) throws IOException {
        return open(name);
    }

    public static DataOutputStream openDataOutputStream(String name) {
        return new DataOutputStream(new DummyOutputStream());
    }

    public static OutputStream openOutputStream(String name) {
        return new DummyOutputStream();
    }

    static class fakeIS extends InputStream {
        fakeIS() {
        }

        public int avaliable() {
            return 0;
        }

        public void close() {
        }

        public void mark() {
        }

        public boolean markSupported() {
            return false;
        }

        public int read() {
            return 0;
        }

        public int read(byte[] b) {
            return 0;
        }

        public int read(byte[] b, int off, int len) {
            return 0;
        }

        public void reset() {
        }

        public long skip(long n) {
            return 0L;
        }
    }

    static class DummyOutputStream extends OutputStream {
        DummyOutputStream() {
        }

        public void write(int a) {
        }
    }
}
