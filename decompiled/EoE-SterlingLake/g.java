/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Canvas
 *  javax.microedition.lcdui.Graphics
 *  javax.microedition.lcdui.Image
 *  javax.microedition.midlet.MIDlet
 */
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Hashtable;
import java.util.Stack;
import java.util.Vector;
import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.midlet.MIDlet;

public abstract class g
extends Canvas
implements Runnable {
    public final Stack a = new Stack();
    public static MIDlet b;
    private e g;
    private e h;
    private volatile boolean i = true;
    private final Thread j = new Thread(this);
    private final boolean k;
    private Image l;
    private Graphics m;
    public final byte[] c;
    public Hashtable d = new Hashtable();
    public Hashtable e = new Hashtable();
    public final Hashtable f = new Hashtable();

    public g(MIDlet mIDlet, e e2) {
        this.c = this.b(0, 0, null);
        b = mIDlet;
        this.h = this.g = e2;
        this.h.w = this;
        this.k = this.isDoubleBuffered();
        this.j.start();
    }

    public final void paint(Graphics graphics) {
        try {
            if (!this.k) {
                if (this.l == null) {
                    this.l = Image.createImage((int)this.getWidth(), (int)this.getHeight());
                    this.m = this.l.getGraphics();
                }
                this.a(this.m, this.h);
                graphics.drawImage(this.l, 0, 0, 20);
            } else {
                this.a(graphics, this.h);
            }
            return;
        }
        catch (Throwable throwable) {
            try {
                this.a(graphics, this.h);
                return;
            }
            catch (Throwable throwable2) {
                this.a("paint", this.h, null, throwable2, true);
                this.d();
                return;
            }
        }
    }

    public final void keyPressed(int n) {
        int n2 = 0;
        if (n == -6) {
            n2 = 3;
        } else if (n == -7) {
            n2 = 4;
        } else if (n == -11) {
            n2 = 4;
        } else if (n == -10) {
            n2 = -10;
        } else if (n == -8) {
            n2 = -8;
        } else {
            try {
                n2 = this.getGameAction(n);
            }
            catch (IllegalArgumentException illegalArgumentException) {}
        }
        try {
            if (this.h.a(n, n2)) {
                this.h.e();
            } else {
                try {
                    this.a(n, n2, this.h);
                }
                catch (Throwable throwable) {
                    this.a("key(" + n + ")", this.h, null, throwable, false);
                }
            }
        }
        catch (Throwable throwable) {
            this.a("key_s(" + n + ")", this.h, null, throwable, false);
        }
        this.d();
    }

    public final void keyReleased(int n) {
        int n2 = this.getGameAction(n);
        this.h.c(n, n2);
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    public final void run() {
        while (this.i) {
            long l;
            long l2;
            this.h.t = l2 = System.currentTimeMillis();
            try {
                this.h.a();
            }
            catch (Throwable throwable) {
                this.a("run_s", this.h, null, throwable, false);
                this.d();
            }
            try {
                int n = this.a(this.h);
                l = (long)Math.min(this.h.v, n) - System.currentTimeMillis() + l2;
            }
            catch (Throwable throwable) {
                this.a("run", this.h, null, throwable, false);
                this.d();
                l = 0L;
            }
            if (l > 0L) {
                try {
                    g g2 = this;
                    synchronized (g2) {
                        this.wait(l);
                        continue;
                    }
                }
                catch (InterruptedException interruptedException) {
                    continue;
                }
            }
            Thread.yield();
        }
    }

    public final void a() {
        this.i = false;
        this.b();
        b.notifyDestroyed();
    }

    public final synchronized void b() {
        this.notifyAll();
    }

    public final void a(e e2, b b2) {
        b2.w = this;
        this.a(e2, (e)b2, false);
        b2.b();
        this.d();
    }

    public final void b(e e2, b b2, Throwable throwable) {
        try {
            this.a(e2, b2, throwable);
        }
        catch (Throwable throwable2) {
            this.a("resp(" + b2.u + ")", e2, null, throwable2, false);
        }
        this.b(b2);
    }

    public final void b(e e2, int n, Object object) {
        try {
            this.a(e2, n, object);
            return;
        }
        catch (Throwable throwable) {
            this.a("menu", e2, null, throwable, false);
            return;
        }
    }

    public static final void a(boolean bl) {
        try {
            System.gc();
            Thread.sleep(300L);
            if (bl) {
                System.gc();
                Thread.sleep(500L);
            }
            return;
        }
        catch (InterruptedException interruptedException) {
            return;
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    public final void a(e e2, e e3, boolean bl) {
        Stack stack = this.a;
        synchronized (stack) {
            e3.w = this;
            if (e2 == null || e2 == this.g) {
                if (this.g != null) {
                    this.a.push(this.g);
                }
                this.g = e3;
                if (bl) {
                    this.a.removeAllElements();
                }
            } else {
                int n = this.a.indexOf(e2);
                if (n >= 0) {
                    this.a.insertElementAt(e3, n + 1);
                    while (bl && n-- >= 0) {
                        this.a.removeElementAt(0);
                    }
                } else {
                    if (this.g != null) {
                        this.a.push(this.g);
                    }
                    this.g = e3;
                }
            }
            return;
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    public final e b(e e2) {
        Stack stack = this.a;
        synchronized (stack) {
            if (e2 == this.g || e2 == null) {
                if (!this.a.isEmpty()) {
                    this.g = (e)this.a.pop();
                }
            } else {
                this.a.removeElement(e2);
            }
        }
        return this.g;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    public final void a(e e2, e e3) {
        Stack stack = this.a;
        synchronized (stack) {
            e3.w = this;
            if (e2 == this.g) {
                this.g = e3;
            } else {
                int n = this.a.indexOf(e2);
                if (n >= 0) {
                    this.a.setElementAt(e3, n);
                }
            }
            return;
        }
    }

    public final e c() {
        if (this.a.isEmpty()) {
            return this.h;
        }
        return (e)this.a.firstElement();
    }

    public final e c(e e2) {
        if (e2 == this.h && !this.a.isEmpty()) {
            return (e)this.a.peek();
        }
        int n = this.a.indexOf(e2);
        if (n > 0) {
            return (e)this.a.elementAt(n - 1);
        }
        return e2;
    }

    public final void d() {
        if (this.h != this.g && this.g != null) {
            this.h.d();
            this.h = this.g;
            this.h.c();
            this.b();
            this.repaint();
        }
    }

    public abstract void a(e var1, b var2, Throwable var3) throws IOException, Exception;

    public abstract void a(Graphics var1, e var2);

    public abstract void a(int var1, int var2, e var3) throws IOException, Exception;

    public abstract void a(e var1, int var2, Object var3) throws IOException;

    public abstract int a(e var1);

    public abstract void a(String var1, e var2, String var3, Throwable var4, boolean var5);

    public final Image a(String string) {
        try {
            return Image.createImage((String)string);
        }
        catch (IOException iOException) {
            throw new RuntimeException("Unable to read resource '" + string + "'");
        }
    }

    private Object a(int n, int n2) {
        Integer n3 = new Integer((n & 0xFF) << 8 | n2 & 0xFF);
        Object v = this.d.get(n3);
        if (v != null) {
            this.e.put(n3, v);
        }
        return v;
    }

    public final Image a(int n, int n2, Vector vector) {
        Object object = this.a(n, n2);
        if (object instanceof Image) {
            return (Image)object;
        }
        byte[] byArray = (byte[])object;
        if (byArray != null) {
            return Image.createImage((byte[])byArray, (int)0, (int)byArray.length);
        }
        try {
            Image image = Image.createImage((String)("/" + n + Integer.toHexString(n2)));
            this.a(n, n2, (Object)image);
            return image;
        }
        catch (IOException iOException) {
            g.d(n, n2, vector);
            return null;
        }
    }

    /*
     * Enabled aggressive block sorting
     * Enabled unnecessary exception pruning
     * Enabled aggressive exception aggregation
     */
    public final byte[] b(int n, int n2, Vector vector) {
        byte[] byArray2;
        byte[] byArray = (byte[])this.a(n, n2);
        if (byArray != null) {
            return byArray;
        }
        String string = "/" + n + Integer.toHexString(n2);
        InputStream inputStream = this.getClass().getResourceAsStream(string);
        if (inputStream == null) {
            g.d(n, n2, vector);
            return null;
        }
        try {
            int n3;
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            while ((n3 = inputStream.read()) >= 0) {
                byteArrayOutputStream.write(n3);
            }
            byArray = byteArrayOutputStream.toByteArray();
            this.a(n, n2, (Object)byArray);
            byArray2 = byArray;
        }
        catch (IOException iOException) {
            try {
                throw new RuntimeException("Unable to read resource '" + string + "'");
            }
            catch (Throwable throwable) {
                try {
                    inputStream.close();
                    throw throwable;
                }
                catch (IOException iOException2) {}
                throw throwable;
            }
        }
        try {
            inputStream.close();
            return byArray2;
        }
        catch (IOException iOException) {}
        return byArray2;
    }

    /*
     * Enabled aggressive block sorting
     * Enabled unnecessary exception pruning
     * Enabled aggressive exception aggregation
     */
    public final Hashtable a(int n, Vector vector) {
        Hashtable hashtable3;
        Hashtable hashtable = (Hashtable)this.a(11, n);
        if (hashtable != null) {
            return hashtable;
        }
        String string = "/11" + Integer.toHexString(n);
        InputStream inputStream = this.getClass().getResourceAsStream(string);
        if (inputStream == null) {
            g.d(11, n, vector);
            return null;
        }
        try {
            DataInputStream dataInputStream = new DataInputStream(inputStream);
            Hashtable hashtable2 = g.a(dataInputStream);
            this.a(11, n, (Object)hashtable2);
            hashtable3 = hashtable2;
        }
        catch (IOException iOException) {
            try {
                throw new RuntimeException("Unable to read resource '" + string + "'");
            }
            catch (Throwable throwable) {
                try {
                    inputStream.close();
                    throw throwable;
                }
                catch (IOException iOException2) {}
                throw throwable;
            }
        }
        try {
            inputStream.close();
            return hashtable3;
        }
        catch (IOException iOException) {}
        return hashtable3;
    }

    public final DataInputStream c(int n, int n2, Vector vector) {
        InputStream inputStream = this.getClass().getResourceAsStream("/" + n + Integer.toHexString(n2));
        if (inputStream == null) {
            byte[] byArray = this.b(n, n2, vector);
            if (byArray == null) {
                return null;
            }
            inputStream = new ByteArrayInputStream(byArray);
        }
        if (inputStream == null) {
            return null;
        }
        return new DataInputStream(inputStream);
    }

    public final Hashtable b(int n, Vector vector) {
        Hashtable hashtable = (Hashtable)this.a(3, n);
        if (hashtable != null) {
            return hashtable;
        }
        byte[] byArray = this.b(3, n, vector);
        if (byArray != null) {
            try {
                hashtable = this.a(new DataInputStream(new ByteArrayInputStream(byArray)), byArray.length, false);
                this.a(3, n, (Object)hashtable);
                return hashtable;
            }
            catch (IOException iOException) {}
        }
        return null;
    }

    public final void e() {
        byte[] byArray = this.b(10, 0, null);
        if (byArray != null) {
            try {
                this.a(new DataInputStream(new ByteArrayInputStream(byArray)), byArray.length, true);
                return;
            }
            catch (IOException iOException) {}
        }
    }

    public static final void d(int n, int n2, Vector vector) {
        Integer n3 = new Integer((n & 0xFF) << 8 | n2 & 0xFF);
        if (!vector.contains(n3)) {
            vector.addElement(n3);
        }
    }

    public final Hashtable a(DataInputStream dataInputStream, int n, boolean bl) throws IOException {
        Hashtable hashtable;
        Hashtable hashtable2 = hashtable = bl ? this.f : new Hashtable();
        while (n > 0) {
            Integer n2 = new Integer(dataInputStream.readUnsignedShort());
            int n3 = dataInputStream.readUnsignedShort();
            hashtable.put(n2, b.a(dataInputStream, n3));
            n -= n3 + 2 + 2;
        }
        return hashtable;
    }

    public static final Hashtable a(DataInputStream dataInputStream) throws IOException {
        Hashtable<Integer, byte[]> hashtable = new Hashtable<Integer, byte[]>();
        int n = dataInputStream.readUnsignedByte();
        while (n-- > 0) {
            int n2 = dataInputStream.readUnsignedByte();
            byte[] byArray = new byte[dataInputStream.readUnsignedByte()];
            dataInputStream.readFully(byArray);
            hashtable.put(new Integer(n2), byArray);
        }
        return hashtable;
    }

    public static final byte[][] b(DataInputStream dataInputStream) throws IOException {
        int n = dataInputStream.readUnsignedByte();
        byte[][] byArrayArray = new byte[n][];
        for (int k = 0; k < byArrayArray.length; ++k) {
            int n2 = dataInputStream.readUnsignedByte();
            byArrayArray[k] = new byte[n2];
            dataInputStream.readFully(byArrayArray[k]);
        }
        return byArrayArray;
    }

    public final void a(int n, int n2, Object object) {
        Integer n3 = new Integer((n & 0xFF) << 8 | n2 & 0xFF);
        this.d.put(n3, object);
        this.e.put(n3, object);
    }
}

