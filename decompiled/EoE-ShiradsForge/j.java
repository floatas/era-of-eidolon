/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Display
 *  javax.microedition.lcdui.Graphics
 *  javax.microedition.lcdui.Image
 *  javax.microedition.midlet.MIDlet
 */
import java.util.Hashtable;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.midlet.MIDlet;

public final class j {
    public int a;
    private final d n;
    public final int b;
    public final byte[] c;
    public Image d;
    private byte[] o;
    private Hashtable p;
    private int q;
    private byte[] r;
    public int e;
    private int s;
    private long t;
    private long u;
    private boolean v;
    public boolean f;
    public long g;
    private boolean w;
    private short x;
    private short y;
    private int z;
    private int A;
    private long B;
    public int h;
    public int i;
    public int j;
    public int k;
    public int l;
    public int m;
    private int C;
    private int D;
    private String E;
    private int F;
    private long G;

    public j(d d2, int n, byte[] byArray) {
        this.e = this.a = 15;
        this.s = -1;
        this.n = d2;
        this.b = n;
        this.c = byArray;
        this.h = byArray[3] << 8;
        this.i = byArray[4] << 8;
        if (n != 0 && byArray[15] > 0) {
            this.j = 60;
        }
    }

    public final void a(Image image, byte[] byArray, Hashtable hashtable) {
        this.d = image;
        this.o = byArray;
        this.p = hashtable;
    }

    public final void a() {
        this.d = null;
        this.o = null;
        this.p = null;
    }

    public final void a(Graphics graphics, int n, int n2, long l) {
        int n3;
        int n4;
        long l2 = this.g;
        Image image = this.d;
        if ((this.e & 0x3F) == 0 || image == null) {
            if (l2 == 0L) {
                this.g = l;
            }
            return;
        }
        if (this.e != this.s) {
            this.r = (byte[])this.p.get(new Integer(this.e & 0x7F));
            boolean bl = this.v = (this.e & 0x80) != 0;
            if (this.r == null) {
                this.r = (byte[])this.p.get(new Integer(this.e & 0x3F));
            }
            if (this.r == null) {
                throw new RuntimeException("Unable to get anim " + (this.e & 0x3F) + " for " + (this.b == -1 ? "AMMU" : "monster id " + this.b));
            }
            this.q = 1;
            this.t = l;
            this.u = (this.r[this.q] & 0xFF) << 4;
            this.s = this.e;
        }
        int n5 = this.r[this.q + 1] * 3 + this.q;
        if (this.v) {
            for (n4 = this.q + 2; n4 <= n5; n4 += 3) {
                e.a(graphics, image, this.o, this.r[n4 + 2] & 0xFF, n - this.r[n4], n2 + this.r[n4 + 1], 2, 20);
            }
        } else {
            for (n4 = this.q + 2; n4 <= n5; n4 += 3) {
                e.a(graphics, image, this.o, this.r[n4 + 2] & 0xFF, n + this.r[n4], n2 + this.r[n4 + 1], 0, 20);
            }
        }
        if (this.n.c && this.l > 0) {
            if (this.b > 0) {
                n4 = Math.max(n2 - 42, 10);
                n3 = ((this.l - this.m) * 14 + this.l - 1) / this.l;
                graphics.setColor(0);
                graphics.fillRect(n - 8, n4 - 1, 16, 3);
                if (n3 > 0) {
                    graphics.setColor(65280);
                    graphics.drawLine(n - 8 + 1, n4, n + n3 - 8, n4);
                }
            }
            if (l - this.G < 2500L) {
                n4 = Math.max(n2 - (int)(l - this.G >> 7) + 0 - 42, 10);
                graphics.setColor(0);
                graphics.drawString(this.E, n, n4 + 1, 17);
                graphics.drawString(this.E, n, n4 - 1, 17);
                graphics.drawString(this.E, n + 1, n4, 17);
                graphics.drawString(this.E, n - 1, n4, 17);
                graphics.setColor(this.F);
                graphics.drawString(this.E, n, n4, 17);
            }
        }
        if (this.w) {
            n3 = this.z * (int)(l - this.B) >> 6;
            n4 = this.z == 0 ? 1 : 0;
            this.h += n3;
            if (this.z < 0 && this.h <= this.x || this.z > 0 && this.h >= this.x || this.z == 0) {
                this.h = this.x;
                n4 = 1;
            }
            n3 = this.A * (int)(l - this.B) >> 6;
            this.i += n3;
            if (this.A < 0 && this.i <= this.y || this.A > 0 && this.i >= this.y || this.A == 0) {
                this.i = this.y;
                if (n4 != 0) {
                    this.b();
                    l2 = l;
                    this.w = false;
                }
            }
            this.B = l;
        } else if (l2 > 0L && !this.f || this.r[0] <= 1) {
            if (l2 == 0L) {
                l2 = l;
            }
            this.g = l2;
            return;
        }
        while (l - this.t > this.u) {
            this.t += this.u;
            if (2 + n5 >= this.r.length) {
                if (!this.w && !this.f) {
                    if (l2 == 0L) {
                        l2 = l;
                    }
                } else {
                    this.q = 1;
                }
            } else {
                this.q = 2 + n5;
            }
            this.u = (this.r[this.q] & 0xFF) << 4;
        }
        this.g = l2;
    }

    public final void b() {
        this.e = this.a;
        this.w = false;
        this.f = true;
        this.g = 1L;
    }

    public final void c() {
        this.e = this.a & 0x3F | this.s & 0xC0;
        this.w = false;
        this.f = true;
        this.g = 1L;
    }

    public final void a(int n, boolean bl) {
        this.e = n;
        this.g = 0L;
        this.q = 1;
        this.t = this.n.t;
        this.f = bl;
    }

    public final void a(int n, int n2, int n3) {
        this.e = n;
        this.g = 0L;
        this.q = 1;
        this.t = this.B = this.n.t;
        this.w = true;
        this.f = true;
        this.x = (short)(n2 << 8);
        this.y = (short)(n3 << 8);
        int n4 = this.x - this.h;
        int n5 = this.y - this.i;
        int n6 = j.a(n4 * n4 + n5 * n5);
        if (n6 != 0) {
            this.z = (n4 << 6) / n6;
            this.A = (n5 << 6) / n6;
            if (this.z == 0 && this.A == 0) {
                this.g = 1L;
            }
        }
    }

    public final j d() {
        j j2 = new j(this.n, -1, new byte[19]);
        new j(this.n, -1, new byte[19]).d = this.d;
        j2.o = this.o;
        j2.p = this.p;
        j2.h = this.h;
        j2.i = this.i;
        j2.a = 0;
        return j2;
    }

    private static final int a(int n) {
        int n2;
        int n3 = 0;
        int n4 = n2 = n >= 65536 ? 0x40000000 : 16384;
        do {
            int n5;
            if (n >= (n5 = n3 + n2)) {
                n -= n5;
                n3 = n5 + n2;
            }
            n3 >>= 1;
        } while ((n2 >>= 2) != 0);
        return n3;
    }

    public final int e() {
        return this.h + this.i;
    }

    public final void f() {
        this.C = this.h;
        this.D = this.i;
    }

    public final void g() {
        this.h = this.C;
        this.i = this.D;
    }

    public final void a(int n, int n2) {
        if (this.b == 0 && n > 0) {
            e.a(Display.getDisplay((MIDlet)g.b), 300);
        }
        this.m = Math.min(this.l, this.m + n);
        this.E = Integer.toString(n);
        this.F = n2;
        this.G = System.currentTimeMillis();
    }

    public final boolean h() {
        return this.g > 0L && !this.w || this.w && this.i == this.y && this.h == this.x;
    }
}

