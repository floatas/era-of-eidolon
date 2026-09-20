/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Display
 *  javax.microedition.lcdui.Graphics
 *  javax.microedition.lcdui.Image
 *  javax.microedition.midlet.MIDlet
 */
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FilterInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Hashtable;
import java.util.Random;
import java.util.Stack;
import java.util.Vector;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.midlet.MIDlet;

public final class d
extends e {
    private final byte[][] h;
    private final byte[] i;
    private final byte[][] j;
    private boolean k;
    private byte[] l;
    private final byte[] m;
    private final j[] n;
    public j a;
    private int o;
    private b p;
    private Hashtable q;
    private static final Random x;
    private static final String[] y;
    private static final String[] z;
    private static final String[] A;
    public static final String[] b;
    private Image B;
    private Image C;
    private byte[] D;
    private final int E;
    private final int F;
    private int G;
    private int H;
    private int I;
    private int J;
    private int K;
    private int L;
    private long M;
    private Image N;
    private Image O;
    private long P;
    private int Q;
    private int R;
    private final Vector S;
    private boolean T;
    private boolean U;
    private long V;
    private int W;
    private int X;
    public boolean c;
    private int Y;
    private int Z;
    private int aa;
    private int ab;
    private j ac;
    private final c[] ad;
    private final Stack ae;
    private static final Object[] af;
    private int ag;
    private int ah;
    private final Stack ai;
    private Stack aj;
    private int ak;
    private byte[] al;
    private Vector am;
    private Vector an;
    private int ao;
    private int ap;
    private String aq;
    private int ar;
    public j d;
    private byte[] as;
    private int at;
    private b au;
    private Stack av;
    private boolean aw;
    private long ax;
    public byte[] e;
    public boolean f;
    private int ay;
    private int az;
    private byte[] aA;
    private int aB;
    private int aC;
    private int aD;
    private final Vector aE;
    private final Vector aF;
    public long g;
    private int aG;
    private byte[] aH;
    private byte[] aI;
    private c aJ;

    public d(int n, int n2, int n3, byte[][] byArray, byte[][] byArray2, b b2, boolean bl) {
        super(n);
        System.currentTimeMillis();
        this.S = new Vector();
        this.ad = new c[8];
        this.ae = new Stack();
        this.ai = new Stack();
        this.aj = new Stack();
        this.al = new byte[2];
        this.av = new Stack();
        this.f = true;
        this.aE = new Vector();
        this.aF = new Vector();
        this.E = n2;
        this.F = n3;
        this.h = byArray;
        this.j = byArray2;
        this.k = bl;
        this.i = (byte[])b2.d.get(new Integer(21));
        this.l = (byte[])b2.d.get(new Integer(25));
        this.n = new j[this.l.length];
        this.m = new byte[this.l.length];
        for (int k = 0; k < byArray2.length; ++k) {
            byte[] byArray3 = byArray2[k];
            int n4 = byArray3[0] & 0xFF;
            if (byArray3[11] == 0 || this.l[n4] != 3) continue;
            this.l[n4] = 2;
        }
        this.v = 50;
        this.G = n2 >> 1;
        this.H = (n3 >> 1) + 6;
        this.W = b2.b(26);
        this.X = b2.b(27);
        this.I = b2.b(22);
        this.J = b2.b(23) << 8;
        this.K = b2.b(24) << 8;
        this.ad[6] = new c(6, null, i.a(new Object[]{"End turn", "Try to flee"}), 9, 279);
        this.ad[7] = new c(7, "Target", i.a(new Object[]{"Change target"}), 9, 279);
    }

    /*
     * Enabled aggressive block sorting
     * Enabled unnecessary exception pruning
     * Enabled aggressive exception aggregation
     */
    private void k() {
        int n;
        Object object;
        Object object2;
        this.T = false;
        Vector vector = new Vector();
        if (this.p == null) {
            this.w.e = new Hashtable();
        }
        if (this.L != this.I) {
            this.Q = this.J + 128 >> 8;
            this.R = this.K + 128 >> 8;
        }
        if (!this.U) {
            object2 = this.w.a("/70");
            byte[] byArray = this.w.b(8, 0, vector);
            object = this.w.a(0, vector);
            byte[] byArray2 = new byte[19];
            byte[] byArray3 = byArray2;
            byArray2[15] = 1;
            this.a = new j(this, 0, byArray3);
            this.a.a((Image)object2, byArray, (Hashtable)object);
            this.n[0] = this.a;
            this.w.e();
        } else {
            this.W = this.Q;
            this.X = this.R;
        }
        this.a.h = this.J;
        this.a.i = this.K;
        object2 = this.w.c(2, this.I, vector);
        if (object2 != null) {
            try {
                ((DataInputStream)object2).readByte();
                ((DataInputStream)object2).readShort();
                this.aB = ((DataInputStream)object2).readUnsignedShort();
                this.aC = ((DataInputStream)object2).readUnsignedShort();
                this.aD = ((DataInputStream)object2).readUnsignedShort();
                this.ay = ((DataInputStream)object2).readShort();
                this.az = ((DataInputStream)object2).readShort();
                this.aA = new byte[this.ay * this.az];
                ((DataInputStream)object2).readFully(this.aA);
            }
            catch (Exception exception) {
                try {
                    throw new RuntimeException("Unable to read map '" + this.I + "'");
                }
                catch (Throwable throwable) {
                    try {
                        ((FilterInputStream)object2).close();
                        throw throwable;
                    }
                    catch (Exception exception2) {}
                    throw throwable;
                }
            }
            try {
                ((FilterInputStream)object2).close();
            }
            catch (Exception exception) {}
            for (int k = 0; k < this.h.length; ++k) {
                byte[] byArray = this.h[k];
                object = byArray;
                int n2 = byArray[0] & 0xFF;
                if (this.i[n2] != 3 || object[12] != 6 || this.I != object[14]) continue;
                this.b((byte[])object);
            }
        }
        this.q = this.w.b(this.I, vector);
        this.B = this.w.a(4, 0, vector);
        this.C = this.w.a(5, 2, vector);
        this.D = this.w.b(6, 2, vector);
        this.aF.removeAllElements();
        for (n = 0; n < this.j.length; ++n) {
            byte[] byArray = this.j[n];
            object = byArray;
            int n3 = byArray[0] & 0xFF;
            if (object[1] == this.I && (this.l[n3] == 1 || this.l[n3] == 2 || object[11] != false)) {
                Image image = this.w.a(7, (int)object[12], vector);
                byte[] byArray4 = this.w.b(8, (int)object[12], vector);
                Hashtable hashtable = this.w.a((int)object[12], vector);
                if (image == null || byArray4 == null || hashtable == null) continue;
                if (this.n[n3] == null) {
                    this.n[n3] = new j(this, n3, (byte[])object);
                }
                this.n[n3].a(image, byArray4, hashtable);
                this.n[n3].e = this.n[n3].a = object[13] & 0xFF;
                if (object[15] > 0) {
                    this.n[n3].a(14, true);
                } else {
                    this.n[n3].f = true;
                }
                if (this.l[n3] != 2) continue;
                this.aF.addElement(this.n[n3]);
                continue;
            }
            if (this.n[n3] == null) continue;
            this.n[n3].a();
        }
        if (vector.size() > 0) {
            if (this.p != null) {
                StringBuffer stringBuffer = new StringBuffer("Unable to get resources from server:");
                int k = 0;
                while (k < vector.size()) {
                    stringBuffer.append("\n").append(Integer.toHexString(((Integer)vector.elementAt(k)).shortValue()));
                    ++k;
                }
                throw new RuntimeException(stringBuffer.toString());
            }
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            object = new DataOutputStream(byteArrayOutputStream);
            try {
                for (int k = 0; k < vector.size(); ++k) {
                    ((DataOutputStream)object).writeShort(((Integer)vector.elementAt(k)).shortValue());
                }
            }
            catch (IOException iOException) {}
            this.p = new b(10, this);
            this.p.a(1, byteArrayOutputStream.toByteArray());
            this.p.a(this.w.d);
            this.p.a(3, this.w.c);
            if (this.U) {
                this.d(this.p);
            }
            this.w.a((e)this, this.p);
            return;
        }
        this.aE.removeAllElements();
        for (n = 0; n < this.h.length; ++n) {
            byte[] byArray = this.h[n];
            object = byArray;
            if (byArray[1] != this.I && object[1] != false) continue;
            this.aE.addElement(object);
        }
        this.aF.addElement(this.a);
        if (this.a != null && this.a.d == null) {
            this.a.d = this.w.a("/70");
        }
        this.M = this.t;
        this.p = null;
        this.U = true;
        this.T = true;
        this.L = this.I;
        this.b();
    }

    public final void a(Graphics graphics, boolean bl) {
        int n;
        Object object;
        graphics.setFont(e.r);
        graphics.setColor(0);
        graphics.fillRect(0, 0, 240, 320);
        if (!this.T || this.a.d == null) {
            graphics.setColor(0xFFFFFF);
            graphics.drawString("Please wait...", 120, 160, 65);
            return;
        }
        this.a(graphics, 0, 0, this.E, this.c ? Math.min(279, this.F) : this.F);
        graphics.setClip(0, 0, 240, 320);
        if (!this.c && this.t - this.M < 4000L) {
            object = this.b(this.aD);
            n = e.r.stringWidth((String)object);
            graphics.setColor(8610337);
            graphics.fillRect(240 - n - 6 >> 1, 0, n + 6, e.s);
            graphics.setColor(16173378);
            graphics.drawString((String)object, 120, 0, 17);
        }
        this.ap = (this.ap + 1) % 3;
        if (this.c) {
            if (this.O == null) {
                this.O = this.w.a("/fpanel.png");
            }
            e.a(graphics, this.O, 0, 0, 240, 9, 0, 0, 0, 20);
            graphics.setColor(0);
            object = this.a;
            n = ((j)object).l > 0 ? ((j)object).m * 109 / ((j)object).l : 109;
            graphics.fillRect(119 - n, 2, n, 5);
            int n2 = this.ah * 109 / 720;
            n = this.ag * 109 / 720 + (this.ag + this.ah <= 720 ? n2 : 0);
            graphics.fillRect(238 - n, 2, n, 5);
            if (this.ap != 0 && this.ah > 0 && this.ag + this.ah <= 720) {
                e.a(graphics, this.O, 109 - n, 50, n2, 5, 0, 238 - n, 2, 20);
            }
            if (this.ab == 5) {
                graphics.fillRect(0, 279, 240, 41);
                if (this.aq != null) {
                    graphics.setColor(this.ar);
                    graphics.drawString(this.aq, 1, 320 - (41 - e.s >> 1), 36);
                }
            } else {
                e.a(graphics, this.O, 0, 9, 240, 41, 0, 0, 279, 20);
                if (this.aF.size() < 3) {
                    graphics.fillRect(188, 298, 19, 19);
                }
                int n3 = Math.min(11, this.ae.size());
                for (int k = 0; k < n3; ++k) {
                    Object[] objectArray = (Object[])this.ae.elementAt(k);
                    e.a(graphics, this.O, (Integer)objectArray[0] * 22 + 36, 30, 14, 15, 0, k * 16 + 34, 283, 20);
                }
                if (bl && (this.ab == 4 || this.ab == 3)) {
                    graphics.setColor(Math.abs(255 - ((int)this.t & 0x1FE)) << 8 | 0xFF0000);
                    graphics.drawRect(this.Y * 22 + 33, 298, 19, 19);
                }
            }
            if (this.ab == 3) {
                this.ad[this.Y].a(graphics, true);
            }
            return;
        }
        graphics.setColor(0);
        if (this.N == null) {
            this.N = this.w.a("/cpanel.png");
        }
        graphics.drawImage(this.N, 0, 320, 36);
        if (this.S.size() == 0 || this.ap == 0 || !bl) {
            graphics.fillRect(37, 307, 17, 13);
        }
        int n4 = 122 * b.h >> 8;
        graphics.fillRect(59 + n4, 311, 122 - n4, 4);
        n = 300 - (e.s >> 1);
        graphics.setColor(0xFFFFFF);
        graphics.drawString(b.e, 50, 0 + n, 20);
        graphics.drawString(b.f, 119, 0 + n, 20);
        graphics.drawString(b.g, 167, 0 + n, 20);
    }

    public final void a(Graphics graphics, int n, int n2, int n3, int n4) {
        j j2;
        int n5;
        int n6;
        int n7;
        int n8;
        int n9;
        int n10;
        int n11;
        int n12;
        int n13;
        int n14;
        int n15;
        int n16;
        graphics.setClip(n, n2, n3, n4);
        if (this.c) {
            n16 = (this.Z << 8) + 128;
            n15 = (this.aa << 8) + 128;
        } else {
            n16 = this.a.h;
            n15 = this.a.i;
        }
        int n17 = this.G;
        int n18 = this.H;
        graphics.setColor(0);
        graphics.fillRect(n, n2, n3, n4);
        int n19 = n17 - ((256 + (n16 & 0xFF) - (n15 & 0xFF)) * 16 >> 8);
        int n20 = 1 + n18 - ((256 + (n16 & 0xFF) + (n15 & 0xFF)) * 8 >> 8);
        int n21 = n16 >> 8;
        int n22 = n15 >> 8;
        int n23 = (n - n19 + 3152) / 32 - 99;
        int n24 = (n2 - n20 + 2) / 8 - 2;
        n19 += n23 * 32;
        int n25 = n20 += n24 * 8;
        int n26 = n24;
        while (n25 < n2 + n4) {
            n14 = n21 + n23 + (n26 + 1 >> 1);
            n13 = n22 - n23 + (n26 >> 1);
            for (n12 = n19 + (n26 % 2 != 0 ? 16 : 0); n12 < n + n3; n12 += 32) {
                if ((n14 | n13) >= 0 && n14 < this.ay && n13 < this.az && (n11 = this.aA[n13 * this.ay + n14] & 0xF) != 0) {
                    graphics.drawRegion(this.B, 0, (n11 - 1) * 15, 32, 15, 0, n12, n25, 20);
                }
                ++n14;
                --n13;
            }
            n25 += 8;
            ++n26;
        }
        n26 = ((n16 - n15) * 16 >> 8) - n17;
        n12 = ((n16 + n15) * 8 >> 8) - n18;
        if (this.c) {
            Object object;
            int n27;
            graphics.setClip(n, n2, n3, n4);
            graphics.setColor(0);
            n14 = (this.Z - this.aa) * 16 - n26 - 64;
            n13 = (this.Z + this.aa) * 8 - n12 + 40;
            for (n11 = 0; n11 < 9; ++n11) {
                n10 = 1 + n11;
                if (n10 > 4) {
                    n10 = Math.min(4, 10 - n10);
                }
                graphics.drawLine(n14 + 16 * (-n10 + n11) - 1, n13 + 8 * (-n10 - n11), n14 + 16 * (n10 + n11), n13 + 8 * (n10 - n11));
                graphics.drawLine(n14 + 16 * (-n10 + n11) - 1, n13 + 8 * (n10 + n11 - 8), n14 + 16 * (n10 + n11), n13 + 8 * (-n10 + n11 - 8));
            }
            if (this.ab == 0) {
                graphics.setColor(Math.abs(255 - ((int)this.t & 0x1FE)) << 8);
            } else {
                graphics.setColor(65280);
            }
            n11 = this.ac.h >>> 8;
            n10 = this.ac.i >>> 8;
            int n28 = (n11 - n10) * 16 - n26;
            n9 = (n11 + n10) * 8 - n12 - 8;
            graphics.drawLine(n28 - 1, n9, n28 + 16, n9 + 8);
            graphics.drawLine(n28 + 16, n9 + 8, n28 - 1, n9 + 16);
            graphics.drawLine(n28 - 1, n9 + 16, n28 - 16 - 1, n9 + 8);
            graphics.drawLine(n28 - 16 - 1, n9 + 8, n28, n9);
            if (this.ab == 2) {
                graphics.setColor(Math.abs(255 - ((int)this.t & 0x1FE)) << 8 | 0xFF);
                graphics.fillRect((this.al[0] - this.al[1]) * 16 - n26 - 8, (this.al[0] + this.al[1]) * 8 - n12 - 4, 16, 8);
            } else if (this.ab == 1) {
                graphics.setColor(Math.abs(255 - ((int)this.t & 0x1FE)) << 8 | 0xFF);
                for (n27 = this.aj.size() - 1; n27 >= 0; --n27) {
                    byte[] byArray = (byte[])this.aj.elementAt(n27);
                    object = byArray;
                    n8 = byArray[0] & 0xFF;
                    n7 = object[1] & 0xFF;
                    graphics.fillRect((n8 - n7) * 16 - n26 - 8, (n8 + n7) * 8 - n12 - 4, 16, 8);
                    graphics.setColor(0x6060FF);
                }
            } else {
                graphics.setColor(255);
                for (n27 = 0; n27 < this.ai.size(); ++n27) {
                    object = (Vector)this.ai.elementAt(n27);
                    for (n8 = 0; n8 < ((Vector)object).size(); ++n8) {
                        byte[] byArray = (byte[])((Vector)object).elementAt(n8);
                        n6 = byArray[0] & 0xFF;
                        n5 = byArray[1] & 0xFF;
                        graphics.fillRect((n6 - n5) * 16 - n26 - 8, (n6 + n5) * 8 - n12 - 4, 16, 8);
                    }
                }
            }
        }
        if ((n14 = this.aF.size()) > 0) {
            n13 = 0;
            n11 = Integer.MIN_VALUE;
            n10 = 0;
            block6: while (n10 == 0) {
                j j3 = (j)this.aF.elementAt(n13);
                n9 = j3.e();
                while (n13 < n14) {
                    j j4 = j3;
                    int n29 = n9;
                    if (++n13 < n14 && (n9 = (j3 = (j)this.aF.elementAt(n13)).e()) < n29) {
                        this.aF.setElementAt(j3, n13 - 1);
                        this.aF.setElementAt(j4, n13);
                        j3 = j4;
                        n8 = n9;
                        n9 = n29;
                        n29 = n8;
                    }
                    if (n29 < n11) break block6;
                    n11 = n29;
                }
                n10 = 1;
            }
        }
        n19 += 16;
        n25 = n20 + 8;
        n13 = 0;
        if (n14 == 0) {
            j2 = null;
            n10 = Integer.MAX_VALUE;
        } else {
            j2 = (j)this.aF.elementAt(0);
            n10 = (j2.e() * 8 >> 8) - n12;
        }
        long l = System.currentTimeMillis();
        int n30 = n24;
        while (n25 < n2 + n4 + 32) {
            int n31;
            while (n10 < n25) {
                n31 = j2.b;
                graphics.setClip(n, n2, n3, n4);
                n8 = ((this.n[n31].h - this.n[n31].i) * 16 >> 8) - n26;
                this.n[n31].a(graphics, n8, n10, l);
                if (++n13 < n14) {
                    j2 = (j)this.aF.elementAt(n13);
                    n10 = (j2.e() * 8 >> 8) - n12;
                    continue;
                }
                n10 = Integer.MAX_VALUE;
            }
            n8 = n21 + n23 + (n30 + 1 >> 1);
            n7 = n22 - n23 + (n30 >> 1);
            for (n31 = n19 + (n30 % 2 != 0 ? 16 : 0); n31 < n + n3 + 32; n31 += 32) {
                if ((n8 | n7) >= 0 && n8 < this.ay && n7 < this.az && (n6 = (this.aA[n7 * this.ay + n8] & 0xF0) >> 4) >= 2) {
                    n5 = n6 - 2 << 3;
                    graphics.drawRegion(this.C, this.D[n5 + 2] << 8 | this.D[n5 + 2 + 1] & 0xFF, this.D[n5 + 4] << 8 | this.D[n5 + 4 + 1] & 0xFF, (int)this.D[n5 + 0], (int)this.D[n5 + 1], 0, n31 + this.D[n5 + 6], n25 + this.D[n5 + 7], 20);
                }
                ++n8;
                --n7;
            }
            n25 += 8;
            ++n30;
        }
        j j5 = this.d;
        if (j5 != null && j5.b == -1) {
            graphics.setClip(n, n2, n3, n4);
            j5.a(graphics, ((j5.h - j5.i) * 16 >> 8) - n26, ((j5.h + j5.i) * 8 >> 8) - n12, l);
        }
    }

    public final void b() {
        int n;
        int n2;
        Object object;
        int n3;
        this.S.removeAllElements();
        if (this.c || this.I != this.L || this.k) {
            return;
        }
        block4: for (n3 = 0; n3 < this.aE.size(); ++n3) {
            object = (byte[])this.aE.elementAt(n3);
            if (this.i[object[0] & 0xFF] != 2 || object[1] != this.L && object[1] != 0 || object[4] != 0 && ((object[2] & 0xFF) > this.Q || (object[3] & 0xFF) > this.R || (object[4] & 0xFF) <= this.Q || (object[5] & 0xFF) <= this.R)) continue;
            n2 = 14 + (object[13] & 0xFF);
            for (n = 1; n < object[n2]; ++n) {
                if (object[n2 + 1] == 0 && this.i[object[n2 + 1 + n] & 0xFF] != 3 || object[n2 + 1] == 1 && this.l[object[n2 + 1 + n] & 0xFF] != 3) continue block4;
            }
            switch (object[6]) {
                case 0: {
                    if (!this.a(object)) continue block4;
                    n3 = -1;
                    continue block4;
                }
                case 1: {
                    this.S.addElement(object);
                }
            }
        }
        while (!this.av.empty()) {
            b b2 = (b)this.av.pop();
            this.d(b2);
            this.w.a((e)this, b2);
        }
        for (n3 = 0; n3 < this.aF.size(); ++n3) {
            j j2 = (j)this.aF.elementAt(n3);
            object = j2;
            if (j2.b == 0) continue;
            n2 = Math.abs(this.a.h - object.h) >> 8;
            n = Math.abs(this.a.i - object.i) >> 8;
            byte by = object.c[9];
            byte by2 = object.c[10];
            if (by > 0 && n2 < by && n < by && !this.aw && this.a(this.a, (j)object)) {
                this.a(this.a(object.c[5], object.c[6]), new byte[]{(byte)object.b});
                return;
            }
            if (by2 <= 0 || n2 >= by2 || n >= by2 || !this.a(this.a, (j)object)) continue;
            this.S.addElement(object);
        }
    }

    private boolean a(j j2, j j3) {
        int n = j2.h + 128 >> 8;
        int n2 = j2.i + 128 >> 8;
        int n3 = j3.h + 128 >> 8;
        int n4 = j3.i + 128 >> 8;
        while (n != n3 || n2 != n4) {
            if (Math.abs(n - n3) > Math.abs(n2 - n4)) {
                n = n > n3 ? --n : ++n;
            } else {
                n2 = n2 > n4 ? --n2 : ++n2;
            }
            if (this.b(n, n2)) continue;
            return false;
        }
        return true;
    }

    public final void a(String string, byte[] byArray) {
        if (this.aw) {
            return;
        }
        this.aw = true;
        this.e = byArray;
        h h2 = new h(36, null, string, new String[]{"Auto fight", "Manual"});
        new h(36, null, string, new String[]{"Auto fight", "Manual"}).c = true;
        if (!this.f) {
            h2.b = 1;
        }
        this.w.a((e)this, h2, false);
    }

    public final void a(byte[] byArray, boolean bl) {
        b b2 = new b(12, this);
        if (byArray.length > 0) {
            this.d(b2);
        }
        b2.a(1, byArray);
        byte[] byArray2 = new byte[this.aF.size() * 3];
        for (int k = 0; k < this.aF.size(); ++k) {
            j j2 = (j)this.aF.elementAt(k);
            if (this.l[j2.b] == 1) {
                this.l[j2.b] = 2;
            }
            int n = k * 3;
            byArray2[n] = (byte)j2.b;
            byArray2[n + 1] = (byte)(j2.h + 128 >> 8);
            byArray2[n + 2] = (byte)(j2.i + 128 >> 8);
        }
        b2.a(2, byArray2);
        if (bl) {
            b2.b(3, 1);
            b2.i = true;
        }
        this.w.a((e)this, b2);
    }

    public final void a(b b2) {
        for (int k = 0; k < 6; ++k) {
            Vector vector = b2.a(30 + k);
            if (vector.isEmpty()) {
                vector.addElement("Empty");
            }
            this.ad[k] = new c(k, y[k], vector, 9, 279);
        }
        this.Z = b2.b(20);
        this.aa = b2.b(21);
        this.an = new Vector();
        this.aF.removeAllElements();
        Vector vector = b2.a(22);
        for (int k = 0; k < vector.size(); ++k) {
            byte[] byArray = (byte[])vector.elementAt(k);
            j j2 = this.n[byArray[0] & 0xFF];
            if (j2 == null) {
                throw new RuntimeException("Mob " + (byArray[0] & 0xFF) + " dead");
            }
            this.aF.addElement(j2);
            this.an.addElement(j2);
            j2.f();
            j2.h = byArray[1] << 8;
            j2.i = byArray[2] << 8;
            j2.l = byArray[3] << 8 | byArray[4] & 0xFF;
            j2.m = byArray[5] << 8 | byArray[6] & 0xFF;
            j2.a = byArray[7] & 0xFF;
        }
        this.ac = (j)this.aF.elementAt(1);
        this.c = true;
        this.l();
        this.k = false;
    }

    private void l() {
        this.ab = 4;
        this.ag = 0;
        this.ad[7].c = 0;
        this.ad[6].c = 0;
        this.as = null;
        this.ae.removeAllElements();
        this.Y = 0;
        this.ax = System.currentTimeMillis();
        this.aq = null;
        this.o();
    }

    public final void b(b b2) {
        switch (b2.c) {
            case 1: {
                e.a(Display.getDisplay((MIDlet)g.b), 600);
                this.w.a((e)this, new h(30, null, "New turn starts", null, 3000), false);
                this.l();
                return;
            }
            case 2: {
                this.w.a((e)this, new h(30, null, "Congratulations, you won the fight!", null, 3000), false);
                String string = (String)b2.d.get(new Integer(24));
                if (string != null) {
                    this.w.a((e)this, new h(30, "Battle report", string), false);
                }
                this.c(b2);
                this.l = (byte[])b2.d.get(new Integer(23));
                this.a(b2, (byte[])b2.d.get(new Integer(28)));
                return;
            }
            case 3: {
                this.w.a((e)this, new h(30, null, "You lost the fight!\n\nLuckily someone found you and brought you back to the start of this adventure so that you can continue your quest."), false);
                this.I = b2.b(25);
                this.Q = b2.b(26);
                this.J = this.Q << 8;
                this.R = b2.b(27);
                this.K = this.R << 8;
                this.T = false;
                this.a(b2, null);
                return;
            }
            case 4: {
                this.w.a((e)this, new h(30, null, "You flee"), false);
                this.a(b2, null);
                this.Q = this.W;
                this.a.h = (short)(this.Q << 8);
                this.R = this.X;
                this.a.i = (short)(this.R << 8);
            }
        }
    }

    public final void a(b b2, byte[] byArray) {
        int n;
        int n2;
        if (byArray != null) {
            for (n2 = 0; n2 < byArray.length; ++n2) {
                int n3 = byArray[n2] & 0xFF;
                this.c(n3);
                this.aF.removeElement(this.n[n3]);
            }
        }
        if (!b2.i) {
            this.ae.removeAllElements();
            for (n2 = 0; n2 < this.an.size(); ++n2) {
                j j2 = (j)this.an.elementAt(n2);
                j2.g();
            }
            this.aF.removeAllElements();
            for (n2 = 0; n2 < this.j.length; ++n2) {
                byte[] byArray2 = this.j[n2];
                n = byArray2[0] & 0xFF;
                if (byArray2[1] != this.L || this.l[n] != 2) continue;
                this.aF.addElement(this.n[n]);
            }
            this.aF.addElement(this.a);
            this.a.a = 15;
            this.c = false;
            this.ac = null;
            this.am = null;
            for (n2 = 0; n2 < 6; ++n2) {
                this.ad[n2] = null;
            }
        }
        if (byArray != null) {
            for (n2 = 0; n2 < this.h.length; ++n2) {
                byte[] byArray3 = this.h[n2];
                n = byArray3[6];
                if (n != 2 && n != 3 || this.i[byArray3[0] & 0xFF] != 2) continue;
                int n4 = byArray3[8] & 0xFF;
                for (int k = 0; k < byArray.length; ++k) {
                    int n5 = byArray[k] & 0xFF;
                    if ((n != 2 || n5 != n4) && (n != 3 || this.n[n5] == null || this.n[n5].c[2] != n4)) continue;
                    this.a((Object)byArray3);
                }
            }
        }
        this.an = null;
        this.aw = false;
        this.c(b2);
        this.au = null;
        g.a(true);
    }

    public final boolean a(Object object) {
        int n;
        int n2;
        int n3;
        if (object instanceof j) {
            if (!this.aw) {
                j j2 = (j)object;
                this.a(this.a(j2.c[7], j2.c[8]), new byte[]{(byte)j2.b});
            }
            return false;
        }
        byte[] byArray = (byte[])object;
        boolean bl = false;
        int n4 = byArray[13] & 0xFF;
        block0 : switch (byArray[12]) {
            case 1: {
                this.w.a((e)this, new h(30, null, this.a(byArray[14], byArray[15])), false);
                this.n();
                break;
            }
            case 2: {
                if (this.aw) {
                    return false;
                }
                byte[] byArray2 = new byte[n4];
                System.arraycopy(byArray, 14, byArray2, 0, byArray2.length);
                this.a("Entering fight", byArray2);
                for (n3 = 0; n3 < n4; ++n3) {
                    n2 = byArray[14 + n3];
                    for (n = 0; n < this.aF.size(); ++n) {
                        j j3 = (j)this.aF.elementAt(n);
                        if (j3.b != n2) continue;
                        this.w.a((e)this, new h(30, null, this.a(j3.c[5], j3.c[6])), false);
                        break block0;
                    }
                }
                break;
            }
            case 3: {
                b b2 = new b(11, this);
                b2.b(1, byArray[0] & 0xFF);
                this.av.push(b2);
                break;
            }
            case 4: {
                this.Q = byArray[15] & 0xFF;
                this.J = (short)(this.Q << 8);
                this.R = byArray[16] & 0xFF;
                this.K = (short)(this.R << 8);
                if (byArray[14] != this.L) {
                    this.I = byArray[14];
                    this.T = false;
                    break;
                }
                this.a.h = this.J;
                this.a.i = this.K;
                break;
            }
            case 5: {
                Object object2;
                block13: for (n2 = 0; n2 < n4; ++n2) {
                    n = byArray[14 + n2] & 0xFF;
                    for (int k = 0; k < this.j.length; ++k) {
                        object2 = this.j[k];
                        if (object2[0] != n) continue;
                        this.a((byte[])object2);
                        continue block13;
                    }
                }
                break;
            }
            case 7: {
                Object object2;
                block15: for (n2 = 0; n2 < n4; ++n2) {
                    n = byArray[14 + n2] & 0xFF;
                    this.c(n);
                    for (int k = 0; k < this.aF.size(); ++k) {
                        j j4 = (j)this.aF.elementAt(k);
                        object2 = j4;
                        if (j4 == null || object2.b != n) continue;
                        this.aF.removeElementAt(k);
                        continue block15;
                    }
                }
                break;
            }
            case 6: {
                if (this.L != (byArray[14] & 0xFF)) break;
                this.b(byArray);
                break;
            }
            case 10: {
                this.a.d = null;
                this.w.a((e)this, new c(11, "Pick interest", i.a(b)), false);
                break;
            }
            case 11: {
                this.av.push(new b(17, this));
            }
        }
        int n5 = 14 + n4 + 1 + byArray[14 + n4];
        for (n3 = 1; n3 <= byArray[n5]; ++n3) {
            n2 = byArray[n5 + n3] & 0xFF;
            if (this.i[n2] != 1) continue;
            this.i[n2] = 2;
            bl = true;
        }
        n3 = n5 + byArray[n5] + 1;
        for (n2 = 1; n2 <= byArray[n3]; ++n2) {
            n = byArray[n3 + n2] & 0xFF;
            if (this.i[n] != 2) continue;
            this.i[n] = 3;
            if (n != byArray[0]) {
                for (int k = 0; k < this.h.length; ++k) {
                    if (this.h[k][0] != n || this.h[k][12] != 6) continue;
                    this.a((Object)this.h[k]);
                }
            }
            bl = true;
        }
        n2 = n3 + byArray[n3] + 1;
        for (n = 1; n <= byArray[n2]; ++n) {
            int n6 = byArray[n2 + n] & 0xFF;
            if (this.i[n6] == 3) continue;
            this.i[n6] = 4;
        }
        return bl;
    }

    private void a(byte[] byArray) {
        int n = byArray[0] & 0xFF;
        this.l[n] = 2;
        j j2 = this.n[n];
        if (byArray[1] == this.L && j2 != null && !this.aF.contains(j2)) {
            this.aF.addElement(j2);
        }
    }

    private void c(int n) {
        for (int k = 0; k < this.j.length; ++k) {
            byte[] byArray = this.j[k];
            if (byArray[0] != n) continue;
            this.l[n] = 3;
            this.m[n] = byArray[11];
            return;
        }
    }

    private void b(byte[] byArray) {
        for (int k = 0; k < byArray[18]; ++k) {
            System.arraycopy(byArray, k * byArray[17] + 14 + 5, this.aA, (byArray[16] + k) * this.ay + byArray[15], byArray[17]);
        }
    }

    public final void a() {
        if (!this.T) {
            this.n();
            if (this.p == null || !this.p.b.isAlive()) {
                this.k();
            }
            return;
        }
        this.w.d();
        this.w.serviceRepaints();
        if (this.k) {
            this.a(new byte[0], false);
            return;
        }
        if (this.c) {
            int n;
            if (this.ab != 5 && this.ab != 6 && (n = (int)((this.t - this.ax) / 1000L)) != 0) {
                long l = (this.t - this.ax) % 1000L;
                this.ax = this.t - l;
                this.ag += n * 5;
                if (this.ag > 720) {
                    this.j();
                    this.ag = 720;
                }
            }
            if (this.ab == 3 && this.Y < 6) {
                Vector vector = this.ad[this.Y].b;
                for (int k = 0; k < vector.size(); ++k) {
                    f f2 = (f)vector.elementAt(k);
                    byte[] byArray = (byte[])f2.k;
                    if (this.ag + ((byArray[0] & 0xFF) << 8 | byArray[1] & 0xFF) > 720) {
                        f2.g |= 0x18;
                        continue;
                    }
                    f2.g &= 0xFFFFFFE7;
                }
            } else if (this.ab == 5 && (this.d == null || this.d.h() && this.d.g + (long)this.at < System.currentTimeMillis())) {
                if (this.ao < this.am.size()) {
                    if (this.as != null && this.as[2] == 1) {
                        this.o();
                    }
                    this.as = (byte[])this.am.elementAt(this.ao);
                    this.at = (this.as[1] & 0xFF) << 4;
                    this.ar = this.as[3] == 0 ? 65280 : 0xFF2020;
                    this.aq = b.a(this.as, 5, this.as[4]);
                    n = 5 + this.as[4];
                    int n2 = this.as[n] & 0xFF;
                    int n3 = this.as[n + 1] & 0xFF;
                    switch (this.as[0]) {
                        case 0: {
                            for (int k = 0; k < this.as[n] << 1; k += 2) {
                                this.n[this.as[n + 1 + k] & 0xFF].a = this.as[n + 2 + k] & 0xFF;
                            }
                            break;
                        }
                        case 1: {
                            this.d = this.n[n2];
                            this.d.a(n3, false);
                            for (int k = 0; k < this.as[n + 2]; ++k) {
                                j j2 = this.n[this.as[n + 3 + k * 3] & 0xFF];
                                try {
                                    j2.a(this.as[n + 4 + k * 3] << 8 | this.as[n + 5 + k * 3] & 0xFF, this.ar);
                                    continue;
                                }
                                catch (Exception exception) {}
                            }
                            break;
                        }
                        case 2: {
                            if (this.n[n2] == null) break;
                            this.d = this.n[n2];
                            this.d.a(this.as[n + 3] & 0xFF, n3, this.as[n + 2] & 0xFF);
                            break;
                        }
                        case 4: {
                            this.n[n2].h = (short)(this.as[n + 1] << 8);
                            this.n[n2].i = (short)(this.as[n + 2] << 8);
                            break;
                        }
                        case 3: {
                            if (this.n[n2] == null) break;
                            this.d = this.n[n2].d();
                            this.d.a(this.as[n + 3] & 0xFF, n3, this.as[n + 2] & 0xFF);
                            break;
                        }
                        case 6: {
                            for (int k = 0; k < this.as[n]; ++k) {
                                j j3 = this.n[this.as[n + 1 + k] & 0xFF];
                                if (j3.b != 0) {
                                    this.aF.removeElement(j3);
                                }
                                if (j3.b != this.ac.b || this.aF.size() <= 1) continue;
                                this.m();
                            }
                            break;
                        }
                    }
                    ++this.ao;
                } else {
                    this.d = null;
                    this.b(this.au);
                }
            }
        } else {
            Object object;
            int n;
            long l = this.t - this.P;
            boolean bl = this.t - this.V > 1000L;
            for (n = 0; n < this.aF.size(); ++n) {
                int n4;
                object = (j)this.aF.elementAt(n);
                byte[] byArray = ((j)object).c;
                if (((j)object).c[15] == 0) continue;
                int n5 = ((j)object).b;
                if ((((j)object).j | ((j)object).k) == 0) continue;
                short s = (short)(((j)object).h + d.a((int)((long)((j)object).j * l >> 7), -256, 256));
                short s2 = (short)(((j)object).i + d.a((int)((long)((j)object).k * l >> 7), -256, 256));
                int n6 = s + 128 >> 8;
                int n7 = s2 + 128 >> 8;
                if ((n5 == 0 || (x.nextInt() & 0xF) != 0) && this.b(n6, n7) && (byArray[18] == 0 || (byArray[16] & 0xFF) <= n6 && (byArray[17] & 0xFF) <= n7 && (byArray[18] & 0xFF) > n6 && (byArray[19] & 0xFF) > n7)) {
                    ((j)object).h = s;
                    ((j)object).i = s2;
                    if (n5 != 0) continue;
                    this.Q = n6;
                    this.R = n7;
                    n4 = this.R * this.ay + this.Q;
                    if (this.o == n4) continue;
                    bl = true;
                    this.o = n4;
                    continue;
                }
                if (n5 == 0) {
                    if (((j)object).j != 0) {
                        ((j)object).h = (short)((((j)object).h - 128 & 0xFFFFFF00) + (((j)object).j > 0 ? 383 : 128));
                        continue;
                    }
                    if (((j)object).k == 0) continue;
                    ((j)object).i = (short)((((j)object).i - 128 & 0xFFFFFF00) + (((j)object).k > 0 ? 383 : 128));
                    continue;
                }
                n4 = x.nextInt() > 0 ? 60 : -60;
                int n8 = 14;
                if (x.nextInt() > 0) {
                    ((j)object).j = n4;
                    ((j)object).k = 0;
                    if (n4 > 0) {
                        n8 = 206;
                    }
                } else {
                    ((j)object).j = 0;
                    ((j)object).k = n4;
                    n8 = n4 > 0 ? 78 : 142;
                }
                ((j)object).a(n8, true);
            }
            if (bl) {
                this.b();
                this.V = this.t;
            }
            if (this.t - this.g > 10000L) {
                this.g = this.t;
                for (n = 0; n < this.j.length; ++n) {
                    object = this.j[n];
                    if (this.m[object[0]] == 0) continue;
                    Object object2 = object[0];
                    this.m[object2] = (byte)(this.m[object2] - 1);
                    if (this.m[object2] != 0) continue;
                    this.a((byte[])object);
                }
            }
        }
        this.P = this.t;
        this.e();
    }

    private void m() {
        this.ac = (j)this.aF.elementAt((this.aF.indexOf(this.ac) + 1) % this.aF.size());
        if (this.ac.b == 0) {
            this.m();
        }
    }

    private void n() {
        if (this.a != null) {
            this.a.k = 0;
            this.a.j = 0;
            this.a.c();
        }
    }

    private void o() {
        for (int k = 0; k < this.n.length; ++k) {
            if (this.n[k] == null) continue;
            this.n[k].b();
        }
    }

    public final void c(b b2) {
        this.aG = b2.b(21);
        if (this.aG == 0) {
            return;
        }
        this.aH = (byte[])b2.d.get(new Integer(22));
        this.aI = new byte[6];
        this.a(-1);
    }

    public final void a(int n) {
        Vector<Object> vector = new Vector<Object>();
        for (int k = 0; k < 6; ++k) {
            int n2;
            int n3 = this.aH[k] < 48 ? 3 : (n2 = this.aH[k] < 78 ? 2 : 1);
            if (n == k) {
                --this.aG;
                int n4 = k;
                this.aI[n4] = (byte)(this.aI[n4] + 1);
                int n5 = k;
                this.aH[n5] = (byte)(this.aH[n5] + n2);
            }
            f f2 = new f(String.valueOf('\u000b') + (char)k + this.aH[k] + z[k]);
            new f(String.valueOf('\u000b') + (char)k + this.aH[k] + z[k]).c = "Click to add: " + n2 + "" + '\u000b' + (char)k;
            f2.k = A[k];
            vector.addElement(f2);
        }
        if (this.aG <= 0) {
            this.f();
            return;
        }
        vector.addElement("Save points for later");
        c c2 = new c(14, "Raises left: " + this.aG, vector);
        if (this.aJ != null) {
            c2.c = this.aJ.c;
            this.w.a((e)this.aJ, (e)c2);
        } else {
            this.w.a((e)this, c2, false);
        }
        this.aJ = c2;
    }

    public final void f() {
        this.w.b(this.aJ);
        this.aJ = null;
        b b2 = new b(14, this);
        b2.a(1, this.aI);
        this.w.a((e)this, b2);
    }

    private boolean b(int n, int n2) {
        int n3 = (n | n2) < 0 || n >= this.ay || n2 >= this.az ? 0 : this.aA[n2 * this.ay + n];
        return (this.aB >> (n3 & 0xF) & this.aC >> ((n3 & 0xF0) >> 4) & 1) == 1 ^ (n3 & 0xF0) == 16;
    }

    public final boolean a(int n, int n2) {
        if (!this.T) {
            return false;
        }
        switch (n) {
            case 51: {
                n2 = 1;
                break;
            }
            case 57: {
                n2 = 5;
                break;
            }
            case 55: {
                n2 = 6;
                break;
            }
            case 49: {
                n2 = 2;
            }
        }
        if (this.c) {
            block6 : switch (this.ab) {
                case 3: 
                case 4: {
                    byte[] byArray;
                    Object object;
                    switch (n2) {
                        case 2: {
                            --this.Y;
                            break;
                        }
                        case 5: {
                            ++this.Y;
                            break;
                        }
                        case 1: 
                        case 6: {
                            if (this.ab == 3) {
                                this.ad[this.Y].a(n, n2);
                            }
                            this.ab = 3;
                            break;
                        }
                        case -10: {
                            this.j();
                            break;
                        }
                        case 3: 
                        case 8: {
                            Object e2;
                            if (this.ab == 3) {
                                e2 = this.ad[this.Y].b.elementAt(this.ad[this.Y].c);
                                if (e2 instanceof f) {
                                    object = (f)e2;
                                    if (!((f)object).c()) {
                                        byArray = (byte[])((f)object).k;
                                        this.ak = (byArray[0] & 0xFF) << 8 | byArray[1] & 0xFF;
                                        if (byArray[2] == 2 || byArray[2] == 1) {
                                            this.al = new byte[2];
                                            this.al[0] = (byte)(this.a.h >> 8);
                                            this.al[1] = (byte)(this.a.i >> 8);
                                            if (byArray[2] == 1) {
                                                Stack stack;
                                                if (!this.ai.isEmpty() && !(stack = (Stack)this.ai.peek()).isEmpty()) {
                                                    System.arraycopy(stack.peek(), 0, this.al, 0, 2);
                                                }
                                                this.ah = 0;
                                            }
                                            this.aj = new Stack();
                                            this.aj.push(this.al);
                                            this.ab = byArray[2];
                                            break block6;
                                        }
                                        if (this.ag + this.ak <= 720) {
                                            this.ag += this.ak;
                                            this.ae.push(new Object[]{new Integer(this.Y), e2, new Integer(this.ag), new byte[]{(byte)this.ac.b}});
                                        }
                                    } else {
                                        this.w.a((e)this, new h(30, null, "Not enough time.\nYou can free up time by removing last selection with right screen key"), false);
                                    }
                                } else if (e2 == "Try to flee") {
                                    this.w.a((e)this, new h(35, "Confirmation", "Try to flee", new String[]{"Cancel", "Continue"}), false);
                                } else if (e2 == "End turn") {
                                    this.j();
                                } else if (e2 == "Change target") {
                                    this.ab = 0;
                                    break;
                                }
                                this.ab = 4;
                                break;
                            }
                            this.ab = 3;
                            break;
                        }
                        case -8: 
                        case 4: {
                            Object e2;
                            if (this.ab == 4 && !this.ae.isEmpty() && (e2 = this.ae.pop()) != af) {
                                byte[] byArray2 = (byte[])((f)((Object[])e2)[1]).k;
                                object = byArray2;
                                int n3 = byArray2[0] << 8 | object[1] & 0xFF;
                                if (object[2] == true && !this.ai.isEmpty()) {
                                    n3 *= ((Stack)this.ai.pop()).size() - 1;
                                }
                                this.ag -= n3;
                            }
                            this.ab = 4;
                            break;
                        }
                        default: {
                            return false;
                        }
                    }
                    int n4 = this.aF.size() < 3 ? 7 : 8;
                    this.Y = (this.Y + n4) % n4;
                    object = this.ad[this.Y].b.elementAt(this.ad[this.Y].c);
                    if (this.ab == 3 && object instanceof f) {
                        byArray = (byte[])((f)object).k;
                        this.ah = byArray[0] << 8 | byArray[1] & 0xFF;
                        break;
                    }
                    this.ah = 0;
                    break;
                }
                case 0: {
                    switch (n2) {
                        case 1: 
                        case 2: 
                        case 5: 
                        case 6: {
                            this.m();
                            break block6;
                        }
                        case 3: 
                        case 4: 
                        case 8: {
                            this.ab = 4;
                            break block6;
                        }
                    }
                    break;
                }
                case 1: 
                case 2: {
                    byte[] byArray = new byte[2];
                    System.arraycopy(this.al, 0, byArray, 0, 2);
                    switch (n2) {
                        case 2: {
                            byArray[0] = (byte)(byArray[0] - 1);
                            break;
                        }
                        case 1: {
                            byArray[1] = (byte)(byArray[1] - 1);
                            break;
                        }
                        case 5: {
                            byArray[0] = (byte)(byArray[0] + 1);
                            break;
                        }
                        case 6: {
                            byArray[1] = (byte)(byArray[1] + 1);
                            break;
                        }
                        case 3: 
                        case 8: {
                            Object e3 = this.ad[this.Y].b.elementAt(this.ad[this.Y].c);
                            this.ag += this.ah;
                            if (this.ab == 2) {
                                if ((this.d(byArray[0] & 0xFF, byArray[1] & 0xFF) & 0xF) == 0) break block6;
                                this.ae.push(new Object[]{new Integer(this.Y), e3, new Integer(this.ag), byArray});
                            } else {
                                this.ai.addElement(this.aj);
                                byte[] byArray3 = new byte[(this.aj.size() << 1) - 1];
                                byte[] byArray4 = byArray3;
                                byArray3[0] = (byte)(this.aj.size() - 1);
                                for (int k = 1; k < this.aj.size(); ++k) {
                                    System.arraycopy(this.aj.elementAt(k), 0, byArray4, (k << 1) - 1, 2);
                                }
                                this.ae.push(new Object[]{new Integer(this.Y), e3, new Integer(this.ag), byArray4});
                            }
                            this.ah = 0;
                        }
                        case 4: {
                            this.ab = 4;
                            this.ah = 0;
                            break block6;
                        }
                        default: {
                            break block6;
                        }
                    }
                    int n5 = (byArray[0] & 0xFF) - this.Z;
                    int n6 = (byArray[1] & 0xFF) - this.aa;
                    if (Math.abs(n5) + Math.abs(n6) + (n5 <= 0 ? 1 : 0) + (n6 <= 0 ? 1 : 0) < 6 && (this.ab == 2 || this.b(byArray[0] & 0xFF, byArray[1] & 0xFF))) {
                        if (this.ab == 1) {
                            byte[] byArray5;
                            if (this.aj.size() > 1 && byArray[0] == (byArray5 = (byte[])this.aj.elementAt(this.aj.size() - 2))[0] && byArray[1] == byArray5[1]) {
                                this.ah -= this.ak;
                                this.aj.pop();
                                this.al = byArray;
                            } else {
                                if (this.ag + this.ah + this.ak >= 720) break;
                                this.aj.addElement(byArray);
                                this.ah += this.ak;
                            }
                        }
                        this.al = byArray;
                    } else {
                        break;
                    }
                }
            }
        } else {
            switch (n2) {
                case 2: {
                    this.a.j = -45;
                    this.a.a(14, true);
                    break;
                }
                case 5: {
                    this.a.j = 45;
                    this.a.a(206, true);
                    break;
                }
                case 1: {
                    this.a.k = -45;
                    this.a.a(142, true);
                    break;
                }
                case 6: {
                    this.a.k = 45;
                    this.a.a(78, true);
                    break;
                }
                case 3: 
                case 8: {
                    if (this.S.size() == 0) break;
                    Vector<Object> vector = new Vector<Object>();
                    for (int k = 0; k < this.S.size(); ++k) {
                        Object e4 = this.S.elementAt(k);
                        byte[] byArray = e4 instanceof j ? ((j)e4).c : (byte[])e4;
                        vector.addElement(new f(this.a(byArray[7], byArray[8]), e4));
                    }
                    vector.addElement("Cancel");
                    this.w.a((e)this, new c(32, "Choose action", vector), false);
                    this.n();
                    break;
                }
                default: {
                    return false;
                }
            }
        }
        this.w.b();
        return true;
    }

    public final void g() {
        this.ae.removeAllElements();
        this.ae.push(af);
        this.ag = 0;
        this.j();
        this.ab = 4;
    }

    public final void c(int n, int n2) {
        if (!this.T) {
            return;
        }
        switch (n) {
            case 51: {
                n2 = 1;
                break;
            }
            case 57: {
                n2 = 5;
                break;
            }
            case 55: {
                n2 = 6;
                break;
            }
            case 49: {
                n2 = 2;
            }
        }
        switch (n2) {
            case 2: 
            case 5: {
                this.a.j = 0;
                break;
            }
            case 1: 
            case 6: {
                this.a.k = 0;
            }
        }
        if ((this.a.j | this.a.k) == 0) {
            this.a.c();
        }
    }

    private byte d(int n, int n2) {
        if ((n | n2) < 0 || n >= this.ay || n2 >= this.az) {
            return 0;
        }
        return this.aA[n2 * this.ay + n];
    }

    public final void d() {
        this.n();
    }

    public final void c() {
        this.M = System.currentTimeMillis();
        if (this.T) {
            this.b();
        }
        if (this.T && this.a != null && this.a.d == null) {
            this.a.d = this.w.a("/70");
        }
    }

    public final String h() {
        Vector<Integer> vector = new Vector<Integer>();
        Vector<Integer> vector2 = new Vector<Integer>();
        StringBuffer stringBuffer = new StringBuffer("\t\tMain quests:\t\b");
        StringBuffer stringBuffer2 = new StringBuffer("\f\t\tOptional quests:\t\b");
        for (int k = 0; k < this.h.length; ++k) {
            byte[] byArray = this.h[k];
            if (this.i[byArray[0] & 0xFF] != 2) continue;
            Integer n = new Integer((byArray[9] & 0xFF) << 8 | byArray[10] & 0xFF);
            if (byArray[11] == 1) {
                if (vector.contains(n)) continue;
                vector.addElement(n);
                stringBuffer.append("\n\n").append(this.a(byArray[9], byArray[10]));
                continue;
            }
            if (byArray[11] != 2 || vector2.contains(n)) continue;
            vector2.addElement(n);
            stringBuffer2.append("\n\n").append(this.a(byArray[9], byArray[10]));
        }
        if (vector.isEmpty()) {
            stringBuffer.append("\n\nNone");
        }
        if (vector2.isEmpty()) {
            stringBuffer2.append("\n\nNone");
        }
        return stringBuffer.append((Object)stringBuffer2).toString();
    }

    public final Vector i() {
        Vector<f> vector = new Vector<f>();
        block2: for (int k = 0; k < this.h.length; ++k) {
            byte[] byArray = this.h[k];
            if (byArray[12] != 8 || this.i[byArray[0] & 0xFF] != 3) continue;
            try {
                f f2 = new f(new DataInputStream(new ByteArrayInputStream(byArray, 14, byArray[13])));
                for (int i2 = 0; i2 < this.h.length; ++i2) {
                    String string;
                    if (this.h[i2][12] == 9 && this.i[this.h[i2][0] & 0xFF] == 3 && (string = b.a(this.h[i2], 14, this.h[i2][13])).equals(f2.b)) continue block2;
                }
                f2.a = this.b(Integer.parseInt(f2.a));
                vector.addElement(f2);
                continue;
            }
            catch (IOException iOException) {}
        }
        return vector;
    }

    public final String a(byte by, byte by2) {
        return this.b((by & 0xFF) << 8 | by2 & 0xFF);
    }

    public final String b(int n) {
        Integer n2 = new Integer(n);
        String string = (String)this.w.f.get(n2);
        if (string != null) {
            return string;
        }
        if (this.q == null) {
            return "map texts null";
        }
        string = (String)this.q.get(n2);
        if (string != null) {
            return string;
        }
        return "WTT #" + n;
    }

    public final void d(b b2) {
        b2.a(10, this.i);
        b2.b(11, this.I);
        b2.b(12, this.Q);
        b2.b(13, this.R);
        b2.a(14, this.l);
        b2.b(15, this.W);
        b2.b(16, this.X);
    }

    private static final int a(int n, int n2, int n3) {
        if (n < n2) {
            return n2;
        }
        if (n > n3) {
            return n3;
        }
        return n;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    public final void j() {
        e e2 = this;
        synchronized (e2) {
            if (this.ab == 6 || this.ab == 5) {
                return;
            }
        }
        this.ab = 6;
        e2 = new b(13, this);
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        DataOutputStream dataOutputStream = new DataOutputStream(byteArrayOutputStream);
        for (int k = 0; k < this.ae.size(); ++k) {
            Object[] objectArray = (Object[])this.ae.elementAt(k);
            try {
                if (objectArray == af) {
                    byteArrayOutputStream.write((byte[])objectArray[1]);
                } else {
                    f f2 = (f)objectArray[1];
                    byte[] byArray = f2.b.getBytes();
                    dataOutputStream.write(byArray.length);
                    ((OutputStream)dataOutputStream).write(byArray);
                    dataOutputStream.writeShort((Integer)objectArray[2]);
                    dataOutputStream.write(((byte[])f2.k)[2]);
                    ((OutputStream)dataOutputStream).write((byte[])objectArray[3]);
                }
                ((b)e2).a(1, byteArrayOutputStream.toByteArray());
            }
            catch (IOException iOException) {}
            byteArrayOutputStream.reset();
        }
        this.ai.removeAllElements();
        this.w.a((e)this, (b)e2);
    }

    public final void e(b b2) {
        this.am = b2.a(20);
        this.ao = 0;
        for (int k = 0; k < this.am.size(); ++k) {
            this.am.elementAt(k);
            Object var3_3 = null;
        }
        this.ab = 5;
        this.au = b2;
    }

    static {
        char[] cArray = new char[]{'?', '-', '+', 'C', 'D'};
        char[] cArray2 = new char[]{'?', '-', '+', 'D'};
        x = new Random();
        y = new String[]{"Movement", "Melee attack", "Ranged attack", "Defence", "Offence spells", "Defensive spells"};
        z = new String[]{" Strength", " Intelligence", " Dexterity", " Toughness", " Willpower", " Speed"};
        A = new String[]{"Strength gives:\n+weapon damage\n+carry more weight\n+heavier weapons", "Intelligence gives:\n+effect to all spells cast on foe", "Dexterity gives:\n+hit chance\n+defense\n+complex weapon", "Toughness gives:\n+life points", "Willpower gives:\n+spell resistance\n+protect spells cheaper prices", "Speed makes U:\n+Faster when using skills and spells in fight"};
        b = new String[]{"Melee weapons", "Missile weapons", "Armours", "Skills", "Spells", "Back"};
        af = new Object[]{new Integer(6), new byte[]{1, 102, 0, 0}};
    }
}

