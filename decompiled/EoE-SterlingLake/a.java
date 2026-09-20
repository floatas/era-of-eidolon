/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Graphics
 *  javax.microedition.lcdui.Image
 */
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public class a
extends e {
    public static Image j;
    private static Image x;
    public int k;
    public int l;
    public int m;
    public int n;
    public String o;
    public int p;
    public final int q;
    private int y;
    private int z;
    private int A;

    public a(int n, String string) {
        super(n);
        this.o = string;
        this.q = string == null ? 0 : e.s + 1;
    }

    public a(int n, String string, int n2, int n3) {
        this(n, string);
        this.y = n2;
        this.z = n3;
    }

    public final void d(int n) {
        this.A = n;
        this.b(this.o);
        this.k = Math.max(0, 240 - this.m >> 1);
    }

    public final void b(String string) {
        this.o = string;
        if (string != null) {
            this.m = Math.max(this.A, e.r.stringWidth(string) + 1);
            return;
        }
        this.m = this.A;
    }

    public final void d(int n, int n2) {
        this.p = n2 == 0 ? 0 : n2 + 1;
        this.n = Math.min(320 - this.q - n2 - 2, n);
        if (this.y != 0) {
            this.n = Math.min(this.n, this.z - this.y - this.q - 2);
            this.l = (this.z - this.y - this.n - this.q >> 1) + this.q + this.y;
            return;
        }
        this.l = (320 - this.n - this.q - n2 >> 1) + this.q;
    }

    public final void a(Graphics graphics) {
        graphics.setFont(e.r);
        if (x == null) {
            x = this.w.a("/menu.png");
        }
        int n = this.k;
        do {
            int n2 = Math.min(x.getWidth(), this.m + this.k - n);
            e.a(graphics, x, 0, 0, n2, x.getHeight(), 0, n, this.l - this.q - 9, 20);
            e.a(graphics, x, 0, 0, n2, x.getHeight(), 0, n, this.l + this.n + this.p, 20);
        } while ((n += x.getWidth()) < this.m + this.k);
        graphics.setClip(0, 0, 240, 320);
        graphics.setColor(0x505040);
        graphics.drawRect(this.k - 2, this.l - this.q - 1 - 9, this.m + 3, this.n + 1 + 18 + this.q + this.p);
        graphics.setColor(11369747);
        graphics.drawLine(this.k - 1, this.l - this.q - 9, this.k - 1, this.l + this.n + 9 + this.p - 1);
        graphics.drawLine(this.k + this.m, this.l - this.q - 9, this.k + this.m, this.l + this.n + 9 + this.p - 1);
        if (this.q > 0) {
            graphics.setColor(8610337);
            graphics.fillRect(this.k, this.l - this.q, this.m, this.q);
            graphics.setColor(16173378);
            graphics.drawString(this.o, this.k + (this.m - 1 >> 1) + 1, 0 + this.l - this.q, 17);
            graphics.setColor(11369747);
            graphics.drawLine(this.k, this.l - 1, this.k + this.m, this.l - 1);
        }
        if (this.p > 0) {
            graphics.setColor(11369747);
            graphics.drawLine(this.k, this.l + this.n, this.k + this.m, this.l + this.n);
        }
    }
}

