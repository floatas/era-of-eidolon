/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Graphics
 */
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Random;
import java.util.Vector;
import javax.microedition.lcdui.Graphics;

public final class b
extends a
implements Runnable {
    public static String a = "prod";
    public Thread b;
    private int x;
    private static int y;
    private e z;
    private boolean A = true;
    private static byte[] B;
    private ByteArrayOutputStream C;
    private DataOutputStream D;
    public int c;
    public Hashtable d;
    private static int E;
    private static int F;
    private static int G;
    private static int H;
    private static int I;
    private static int J;
    private static int K;
    private static String L;
    private final int M;
    private int N = 0;
    private Random O = new Random();
    public static String e;
    public static String f;
    public static String g;
    public static int h;
    public boolean i;

    public b(int n, e e2) {
        super(n, "Loading...");
        this.z = e2;
        this.d(Math.min(236, 124));
        if (I == -1) {
            I = (this.m - 10) / 2;
        }
        this.d(65, 0);
        this.M = this.n - 3 - (this.n - 3 + 3 - 1) % 5;
        this.v = 150;
        this.b = new Thread(this);
        this.C = new ByteArrayOutputStream();
        this.D = new DataOutputStream(this.C);
        this.d = new Hashtable();
        this.b(255, y++);
    }

    public final void a(Graphics graphics, boolean bl) {
        this.a(graphics);
        graphics.setColor(0);
        graphics.fillRect(this.k, this.l, this.m, this.n);
        graphics.setColor(16173378);
        if (this.x == 0) {
            graphics.drawString("Data used:", this.k + (this.m >> 1), 0 + this.l + 2, 17);
        } else {
            graphics.drawString("Retry no: " + this.x, this.k + (this.m >> 1), 0 + this.l + 2, 17);
        }
        if (J / 10485 != K) {
            K = J / 10485;
            StringBuffer stringBuffer = new StringBuffer();
            stringBuffer.append(K);
            while (stringBuffer.length() < 3) {
                stringBuffer.insert(0, '0');
            }
            stringBuffer.insert(stringBuffer.length() - 2, '.');
            stringBuffer.append(" MB");
            L = stringBuffer.toString();
        }
        graphics.drawString(L, this.k + (this.m >> 1), 0 + this.l + 2 + e.s, 17);
        graphics.setColor(16645016);
        graphics.fillRect(this.k + E, this.l + F, 3, 3);
        graphics.setColor(16173378);
        graphics.drawLine(this.k + I, this.l + this.M, this.k + I + 10, this.l + this.M);
    }

    public final void a() {
        int n;
        I = Math.min(this.m - 10 - 1, Math.max(0, I + this.N));
        int n2 = E + G;
        int n3 = F + H;
        if (n2 <= 0) {
            G = -G;
            n2 = Math.max(1, Math.abs(n2));
        }
        if (n2 + 3 >= (n = this.m - 2)) {
            G = -G;
            n2 -= n2 + 3 - n;
        }
        if (n3 + 3 == this.M && n2 + 3 - 1 >= I && n2 - 1 <= I + 10) {
            H = -H;
            G += this.O.nextInt() % 2;
        }
        if (n3 >= this.n - 3 && H > 0) {
            n3 = 5;
        }
        if (n3 == 0) {
            H = -H;
        }
        F = n3;
        E = n2;
        this.e();
    }

    public final boolean a(int n, int n2) {
        if (n2 == 2) {
            this.N = -6;
        }
        if (n2 == 5) {
            this.N = 6;
        }
        return true;
    }

    /*
     * Exception decompiling
     */
    public final void run() {
        /*
         * This method has failed to decompile.  When submitting a bug report, please provide this stack trace, and (if you hold appropriate legal rights) the relevant class file.
         * 
         * org.benf.cfr.reader.util.ConfusedCFRException: Started 2 blocks at once
         *     at org.benf.cfr.reader.bytecode.analysis.opgraph.Op04StructuredStatement.getStartingBlocks(Op04StructuredStatement.java:412)
         *     at org.benf.cfr.reader.bytecode.analysis.opgraph.Op04StructuredStatement.buildNestedBlocks(Op04StructuredStatement.java:487)
         *     at org.benf.cfr.reader.bytecode.analysis.opgraph.Op03SimpleStatement.createInitialStructuredBlock(Op03SimpleStatement.java:736)
         *     at org.benf.cfr.reader.bytecode.CodeAnalyser.getAnalysisInner(CodeAnalyser.java:850)
         *     at org.benf.cfr.reader.bytecode.CodeAnalyser.getAnalysisOrWrapFail(CodeAnalyser.java:278)
         *     at org.benf.cfr.reader.bytecode.CodeAnalyser.getAnalysis(CodeAnalyser.java:201)
         *     at org.benf.cfr.reader.entities.attributes.AttributeCode.analyse(AttributeCode.java:94)
         *     at org.benf.cfr.reader.entities.Method.analyse(Method.java:531)
         *     at org.benf.cfr.reader.entities.ClassFile.analyseMid(ClassFile.java:1055)
         *     at org.benf.cfr.reader.entities.ClassFile.analyseTop(ClassFile.java:942)
         *     at org.benf.cfr.reader.Driver.doJarVersionTypes(Driver.java:257)
         *     at org.benf.cfr.reader.Driver.doJar(Driver.java:139)
         *     at org.benf.cfr.reader.CfrDriverImpl.analyse(CfrDriverImpl.java:76)
         *     at org.benf.cfr.reader.Main.main(Main.java:54)
         */
        throw new IllegalStateException("Decompilation failed");
    }

    public final void b() {
        this.D = null;
        this.b.start();
    }

    public final void b(int n, int n2) {
        try {
            this.D.writeByte(n);
            this.D.writeByte(1);
            if (n2 > -129 && n2 < 128) {
                this.D.writeShort(1);
                this.D.writeByte(n2);
            } else if (n2 > -32769 && n2 < 32768) {
                this.D.writeShort(2);
                this.D.writeShort(n2);
            } else {
                this.D.writeShort(4);
                this.D.writeInt(n2);
            }
            return;
        }
        catch (IOException iOException) {
            return;
        }
    }

    public final void a(int n, String string) {
        try {
            this.D.writeByte(n);
            this.D.writeByte(2);
            this.D.writeShort(b.a(string));
            b.a(this.D, string);
            return;
        }
        catch (IOException iOException) {
            return;
        }
    }

    public final void a(int n, byte[] byArray) {
        try {
            this.D.writeByte(n);
            this.D.writeByte(0);
            this.D.writeShort(byArray.length);
            ((OutputStream)this.D).write(byArray);
            return;
        }
        catch (IOException iOException) {
            return;
        }
    }

    public final void a(Hashtable hashtable) {
        try {
            this.D.writeByte(2);
            this.D.writeByte(0);
            this.D.writeShort(hashtable.size() << 1);
            Enumeration enumeration = hashtable.keys();
            while (enumeration.hasMoreElements()) {
                short s = ((Integer)enumeration.nextElement()).shortValue();
                this.D.writeShort(s);
            }
            return;
        }
        catch (IOException iOException) {
            return;
        }
    }

    public final Vector a(int n) {
        Object v = this.d.get(new Integer(n));
        if (v instanceof Vector) {
            return (Vector)v;
        }
        Vector vector = new Vector();
        if (v != null) {
            vector.addElement(v);
        }
        return vector;
    }

    public final int b(int n) {
        Object v = this.d.get(new Integer(n));
        if (v == null) {
            return 0;
        }
        return (Integer)v;
    }

    public final String c(int n) {
        return (String)this.d.get(new Integer(n));
    }

    public static final void a(OutputStream outputStream, String string) throws IOException {
        for (int k = 0; k < string.length(); ++k) {
            char c2 = string.charAt(k);
            if (c2 <= '\u007f') {
                outputStream.write(c2);
                continue;
            }
            if (c2 <= '\u07ff') {
                outputStream.write(0xC0 | c2 >> 6);
                outputStream.write(0x80 | c2 & 0x3F);
                continue;
            }
            outputStream.write(0xE0 | c2 >> 12);
            outputStream.write(0x80 | c2 >> 6 & 0x3F);
            outputStream.write(0x80 | c2 & 0x3F);
        }
    }

    public static final int a(String string) {
        int n = 0;
        for (int k = 0; k < string.length(); ++k) {
            char c2 = string.charAt(k);
            if (c2 <= '\u007f') {
                ++n;
                continue;
            }
            if (c2 <= '\u07ff') {
                n += 2;
                continue;
            }
            n += 3;
        }
        return n;
    }

    public static final String a(InputStream inputStream, int n) throws IOException {
        if (n == 0) {
            return null;
        }
        StringBuffer stringBuffer = new StringBuffer();
        int n2 = 0;
        int n3 = -1;
        for (int k = 0; k < n; ++k) {
            int n4 = inputStream.read();
            if (n4 == -1) {
                throw new EOFException();
            }
            if ((n4 & 0xC0) == 128) {
                n2 = n2 << 6 | n4 & 0x3F;
                if (--n3 != 0) continue;
                stringBuffer.append((char)n2);
                continue;
            }
            if ((n4 & 0x80) == 0) {
                stringBuffer.append((char)n4);
                continue;
            }
            if ((n4 & 0xE0) == 192) {
                n2 = n4 & 0x1F;
                n3 = 1;
                continue;
            }
            if ((n4 & 0xF0) == 224) {
                n2 = n4 & 0xF;
                n3 = 2;
                continue;
            }
            throw new IllegalArgumentException("utf8");
        }
        return stringBuffer.toString();
    }

    public static final String a(byte[] byArray, int n, int n2) {
        try {
            return b.a(new ByteArrayInputStream(byArray, n, n2), n2);
        }
        catch (IOException iOException) {
            return null;
        }
    }

    public final void c(int n, int n2) {
        this.N = 0;
    }

    static {
        G = 5;
        H = 5;
        I = -1;
        K = -1;
        e = "";
        f = "";
        g = "";
    }
}

