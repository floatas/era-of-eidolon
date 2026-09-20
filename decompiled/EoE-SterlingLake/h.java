/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Font
 *  javax.microedition.lcdui.Graphics
 *  javax.microedition.lcdui.Image
 */
import java.util.Vector;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public final class h
extends a {
    private final Vector d = new Vector();
    public final String a;
    private final String[] e;
    private int f;
    public int b;
    private final int g;
    private int h;
    private boolean i;
    private final long B;
    private final int C;
    private int D = 16173378;
    private char E = '\u0001';
    private Font F = e.r;
    private int G = -1;
    private boolean H;
    private int[] I = new int[]{0, this.E, 0};
    private int J;
    public boolean c;

    public h(int n, String string, String string2) {
        this(n, string, string2, null);
    }

    public h(int n, String string, String string2, String[] stringArray) {
        this(n, string, string2, stringArray, Integer.MAX_VALUE);
    }

    public h(int n, String string, String string2, String[] stringArray, int n2) {
        this(n, 220, 300, string, string2, stringArray, n2);
    }

    private h(int n, int n2, int n3, String string, String string2, String[] stringArray, int n4) {
        super(n, string);
        int n5;
        int n6;
        this.d(n2);
        this.B = System.currentTimeMillis() + (long)n4;
        this.a = string2;
        this.e = stringArray;
        this.C = n2 - 6 - 2;
        this.d(n2);
        n3 = Math.min(302 - this.q - this.p - 2, n3);
        int n7 = 0;
        int n8 = 0;
        while (n7 < string2.length()) {
            n6 = string2.charAt(n7++);
            switch (n6) {
                case 10: {
                    this.b(n8, n7 - 1);
                    n8 = n7;
                    this.b();
                    break;
                }
                case 12: {
                    this.b(n8, n7 - 1);
                    n8 = n7;
                    if (this.I.length > 3) {
                        this.b();
                    }
                    this.d.addElement(new int[]{0, 12, 5});
                    break;
                }
                case 11: {
                    this.b(n8, n7 - 1);
                    if (10 + this.I[0] > this.C) {
                        this.b();
                    }
                    this.a(10, 9, -11, string2.charAt(n7));
                    n8 = ++n7;
                    break;
                }
                case 1: 
                case 2: 
                case 3: {
                    this.b(n8, n7 - 1);
                    n8 = n7;
                    this.E = n6;
                    break;
                }
                case 4: {
                    this.b(n8, n7 - 1);
                    n8 = n7;
                    this.a(0, 0, 0, 0);
                    this.H = true;
                    break;
                }
                case 6: {
                    this.b(n8, n7 - 1);
                    this.D = (string2.charAt(n7) & 0xFF) << 16 | (string2.charAt(n7 + 1) & 0xFF) << 8 | string2.charAt(n7 + 2) & 0xFF;
                    n8 = n7 += 3;
                    break;
                }
                case 7: {
                    this.b(n8, n7 - 1);
                    n8 = n7;
                    this.D = 16173378;
                    break;
                }
                case 9: {
                    this.b(n8, n7 - 1);
                    this.G = string2.charAt(n7);
                    this.F = Font.getFont((int)(this.G & 0x60), (int)(this.G & 7), (int)(this.G & 0x18));
                    n8 = ++n7;
                }
            }
        }
        this.b(n8, n7);
        this.b();
        n6 = 0;
        int n9 = 0;
        for (n5 = 0; n5 < this.d.size(); ++n5) {
            int[] nArray = (int[])this.d.elementAt(n5);
            this.J += nArray[2];
            n6 = Math.max(n6, nArray[0]);
            if (this.J > n3) continue;
            n9 = this.J;
        }
        this.d(Math.min(this.J, n9) + 4, stringArray != null ? e.s + 4 : 0);
        if (stringArray != null) {
            n5 = stringArray.length << 2;
            for (int k = 0; k < stringArray.length; ++k) {
                n5 += e.r.stringWidth(stringArray[k]);
            }
            this.g = n5;
            this.v = 100;
        } else {
            this.g = 0;
            this.v = n4;
        }
        this.d(Math.max(n6 + (this.n - 2 < this.J ? 8 : 2), Math.min(this.g, this.m)));
    }

    private void b(int n, int n2) {
        if (n == n2) {
            return;
        }
        int n3 = 0;
        int n4 = n;
        while (n3 <= this.C - this.I[0] && n4 < n2) {
            int n5;
            int n6 = n4;
            while (n4 < n2 && (n5 = this.a.charAt(n4++)) != 32 && n5 != 45) {
            }
            n5 = this.F.substringWidth(this.a, n6, n4 - n6);
            if (n3 + n5 > this.C - this.I[0]) {
                if (n == n6 && this.I.length == 3) {
                    n3 += n5;
                    while (n3 > this.C - this.I[0]) {
                        char c2 = this.a.charAt(--n4);
                        n3 -= this.F.charWidth(c2);
                    }
                } else {
                    n4 = n6;
                }
                if (n3 > 0) {
                    this.a(n3, e.s, n, n4 - n);
                }
                this.b();
                n3 = 0;
                n = n4;
                continue;
            }
            n3 += n5;
        }
        this.a(n3, e.s, n, n4 - n);
    }

    private void a(int n, int n2, int n3, int n4) {
        int[] nArray = new int[this.I.length + 5];
        System.arraycopy(this.I, 0, nArray, 0, this.I.length);
        nArray[this.I.length + 0] = n;
        nArray[this.I.length + 1] = this.G;
        nArray[this.I.length + 2] = this.D;
        nArray[this.I.length + 3] = n3;
        nArray[this.I.length + 4] = n4;
        nArray[0] = nArray[0] + n;
        nArray[1] = this.E;
        nArray[2] = Math.max(nArray[2], n2);
        this.I = nArray;
    }

    private void b() {
        if (this.H) {
            this.H = false;
            for (int k = 3; k < this.I.length; k += 5) {
                if (this.I[k + 0] != 0) continue;
                this.I[k + 0] = this.C - this.I[0];
                this.I[0] = this.C;
                this.I[k + 2] = 0x606060;
                break;
            }
        }
        this.d.addElement(this.I);
        this.I = new int[]{0, this.E, e.s};
    }

    public final void a(Graphics graphics, boolean bl) {
        int n;
        int n2;
        int n3;
        int n4;
        int[] nArray;
        this.a(graphics);
        graphics.setColor(0);
        graphics.fillRect(this.k, this.l, this.m, this.n);
        if (this.n - 2 < this.J) {
            e.a(graphics, this.k + this.m - 6, this.l + 1, this.n - 2, this.f * 10, this.n - 2, this.J, 11369747, 16173378);
        }
        int n5 = -1;
        int n6 = Math.max(-this.f * 10 + 1, -this.J + this.n - 1);
        int n7 = this.k + 1;
        graphics.setClip(this.k + 1, this.l + 1, this.m - 2, this.n - 2);
        for (n4 = 0; n4 < this.d.size() && n6 <= this.n; n6 += nArray[2], ++n4) {
            nArray = (int[])this.d.elementAt(n4);
            if (n6 + nArray[2] <= 0) continue;
            n3 = n7;
            switch (nArray[1]) {
                case 2: {
                    n3 = this.k + this.m - 7 - nArray[0];
                    break;
                }
                case 3: {
                    n3 += this.m - 7 - nArray[0] >> 1;
                    break;
                }
                case 12: {
                    graphics.drawLine(this.k + 5, this.l + 2 + n6, this.k + this.m - (this.n - 2 < this.J ? 12 : 6), this.l + 2 + n6);
                }
            }
            for (n2 = 3; n2 < nArray.length; n2 += 5) {
                if (nArray[n2 + 3] == -11) {
                    Image image = a.j;
                    if (image == null) {
                        a.j = image = this.w.a("/symb.png");
                    }
                    n = this.l + n6 + (nArray[2] - 9 >> 1);
                    e.a(graphics, image, nArray[n2 + 4] * 9, 0, 9, 9, 0, n3, n, 20);
                } else {
                    graphics.setColor(nArray[n2 + 2]);
                    if (nArray[n2 + 4] == 0) {
                        int n8 = this.F.charWidth('.');
                        for (n = 0; n < nArray[n2 + 0]; n += n8) {
                            graphics.drawChar('.', n3 + n, 0 + this.l + n6, 20);
                        }
                        n3 += nArray[n2 + 0];
                        continue;
                    }
                    if (n5 != nArray[n2 + 1]) {
                        n5 = nArray[n2 + 1];
                        Font font = Font.getFont((int)(n5 & 0x60), (int)(n5 & 7), (int)(n5 & 0x18));
                        graphics.setFont(font);
                    }
                    graphics.drawSubstring(this.a, nArray[n2 + 3], nArray[n2 + 4], n3, 0 + this.l + n6, 20);
                }
                n3 += nArray[n2 + 0];
            }
        }
        if (this.e != null) {
            graphics.setClip(this.k, this.l + this.n + 1, this.m, this.p - 1);
            graphics.setColor(0x404040);
            graphics.fillRect(this.k, this.l + this.n, this.m, this.p);
            graphics.setFont(e.r);
            graphics.setClip(this.k + 1, this.l + this.n, this.m - 2, this.p);
            if (this.g < this.m) {
                n4 = this.k + (this.m - this.g >> 1);
            } else if (this.b != 0) {
                int n9 = 0;
                for (n3 = 0; n3 < this.b; ++n3) {
                    n9 += e.r.stringWidth(this.e[n3]) + 4;
                }
                if (this.h + n9 < this.k + 10) {
                    this.h = 12 - n9;
                } else if (this.h + n9 + e.r.stringWidth(this.e[this.b]) > this.k + this.m - 10) {
                    this.h = this.m - 12 - n9 - e.r.stringWidth(this.e[this.b]);
                }
                n4 = this.k + 3 + this.h;
            } else {
                n4 = this.k + 3;
            }
            for (int k = 0; k < this.e.length; ++k) {
                int n10;
                int n11;
                n3 = e.r.stringWidth(this.e[k]) + 1;
                if (this.b == k) {
                    n2 = 12686873;
                    this.i = !this.i;
                    n = this.i ? 0xFFFFFF : 0;
                    n11 = n;
                    n10 = 16645016;
                } else {
                    n2 = 9137427;
                    n11 = 11898650;
                    n = 6311968;
                    n10 = 16173378;
                }
                graphics.setColor(n2);
                graphics.fillRect(n4 - 1, this.l + this.n + 3, n3, e.s);
                graphics.setColor(n11);
                graphics.drawLine(n4 - 2, this.l + this.n + 2, n4 + n3 - 1, this.l + this.n + 2);
                graphics.drawLine(n4 - 2, this.l + this.n + 2, n4 - 2, this.l + this.n + this.p - 2);
                graphics.setColor(n);
                graphics.drawLine(n4 - 2, this.l + this.n + this.p - 2, n4 + n3 - 1, this.l + this.n + this.p - 2);
                graphics.drawLine(n4 + n3 - 1, this.l + this.n + 2, n4 + n3 - 1, this.l + this.n + this.p - 2);
                graphics.setColor(n10);
                graphics.drawString(this.e[k], n4, 0 + this.l + this.n + 3, 20);
                n4 += n3 + 3;
            }
        }
    }

    public final void a() {
        if (this.B < this.t) {
            this.w.b(this);
            this.w.d();
        }
        this.e();
    }

    public final boolean a(int n, int n2) {
        if (n2 == 1 || n2 == 6) {
            this.f = Math.max(0, Math.min(this.f + (n2 == 1 ? -1 : 1), (this.J - this.n + 1 + 10) / 10));
        } else if (this.e != null && (n2 == 2 || n2 == 5)) {
            this.b = (this.b + this.e.length + (n2 == 5 ? 1 : -1)) % this.e.length;
        } else if (n2 == 8 || n2 == 3 || n2 == 4) {
            if (this.e != null && n2 != 4) {
                this.w.b((e)this, this.b, this.e[this.b]);
            } else if (!this.c) {
                this.w.b(this);
            }
        } else {
            return false;
        }
        return true;
    }
}

