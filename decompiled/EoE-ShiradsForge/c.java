/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Graphics
 *  javax.microedition.lcdui.Image
 */
import java.io.IOException;
import java.util.Vector;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public final class c
extends a {
    private static final String[] e = new String[]{" 0", "1.,:;-_'?!\"", "abc2", "def3", "ghi4", "jkl5", "mno6", "pqrs7", "tuv8", "wxyz9"};
    public static final int a = e.s;
    private int f = 0;
    public final Vector b;
    public int c;
    private int g;
    private int h;
    private boolean i;
    private boolean B;
    private int C;
    private int D;
    private int E;
    private long F;
    private int G;
    private int H;
    public static Image d;

    public c(int n, String string, Vector vector) {
        super(n, string);
        this.b = vector;
        this.b();
    }

    public c(int n, String string, Vector vector, int n2, int n3) {
        super(n, string, n2, n3);
        this.b = vector;
        this.b();
    }

    public final void b() {
        int n;
        this.g = 0;
        this.h = a;
        boolean bl = false;
        for (n = 0; n < this.b.size(); ++n) {
            if (this.b.elementAt(n) instanceof f) {
                f f2 = (f)this.b.elementAt(n);
                this.g = Math.max(this.g, f2.a());
                if (f2.c != null) {
                    bl = true;
                }
                if (f2.f < 0) continue;
                this.h = 14;
                continue;
            }
            this.g = Math.max(this.g, f.a(this.b.elementAt(n).toString(), true));
        }
        n = bl ? Math.max(a, 9) + 2 : 0;
        this.d(this.b.size() * this.h + 2, n);
        this.G = Math.min(this.b.size(), (this.n - 2) / this.h);
        this.H = this.b.size() > this.G ? 6 : 0;
        this.d(this.g + 2 + this.H);
        this.d(this.G * this.h + 2, n);
        this.c = Math.min(this.c, this.b.size() - 1);
    }

    public final void a(Graphics graphics, boolean bl) {
        String string;
        graphics.setColor(0);
        graphics.fillRect(this.k, this.l, this.m, this.n);
        graphics.setColor(0x404040);
        graphics.fillRect(this.k, this.l + this.n, this.m, this.p);
        this.a(graphics);
        if (this.H != 0) {
            this.f = Math.min(this.f, this.c - 1);
            this.f = Math.max(this.f, Math.max(this.c - this.G + 2, 0));
            this.f = Math.min(this.f, this.b.size() - this.G);
            e.a(graphics, this.k + this.m - 6, this.l + 1, this.n - 2, this.f, this.G, this.b.size(), 11369747, 16173378);
        }
        int n = this.k + 1;
        int n2 = this.l + 1 + (this.h - a >> 1);
        int n3 = this.l + 1 + (this.h - 14 >> 1);
        int n4 = 0;
        for (int k = this.f; k < this.b.size() && n4 <= this.n - this.h; n4 += this.h, ++k) {
            f f2;
            f f3 = f2 = this.b.elementAt(k) instanceof f ? (f)this.b.elementAt(k) : null;
            if (k == this.c) {
                if (f2 != null && (f2.g & 0x30) != 0) {
                    switch (f2.g & 0x30) {
                        case 16: {
                            graphics.setColor(0x6D6D6D);
                            break;
                        }
                        case 32: {
                            graphics.setColor(0xCD0000);
                        }
                    }
                } else {
                    graphics.setColor(12686873);
                }
                if (f2 != null && f2.f >= 0) {
                    graphics.fillRect(n + 14, this.l + n4 + 1, this.m - this.H - 2 - 14, this.h);
                } else {
                    graphics.fillRect(n, this.l + n4 + 1, this.m - this.H - 2, this.h);
                }
                graphics.setColor(16645016);
            } else {
                graphics.setColor(16173378);
            }
            if (f2 != null) {
                int n5;
                int n6;
                Object object;
                switch (f2.g & 0x30) {
                    case 16: {
                        graphics.setColor(0xCACACA);
                        break;
                    }
                    case 32: {
                        graphics.setColor(k == this.c ? 0xFFBBBB : 0xFF7070);
                    }
                }
                if (f2.e != 0 || f2.i != null) {
                    if (f2.e != 0) {
                        if (k == this.c && this.B || f2.d.length() > 0) {
                            object = f2.d.toString();
                        } else {
                            object = f2.a;
                            graphics.setColor(16645016);
                        }
                    } else if (f2.j >= 0) {
                        object = f2.i[f2.j][0].toString();
                    } else {
                        object = f2.a;
                        graphics.setColor(16645016);
                    }
                    n6 = this.l + n4 + (this.h >> 1);
                    graphics.drawLine(n, n6 - 3, n, n6 + 3);
                    graphics.drawLine(n + 1, n6 - 2, n + 1, n6 + 2);
                    graphics.drawLine(n + 2, n6 - 1, n + 2, n6 + 1);
                    graphics.drawLine(n + 3, n6, n + 3, n6);
                    graphics.drawString((String)object, n + 5, 0 + n2 + n4, 20);
                    if (k != this.c || !this.B || System.currentTimeMillis() - this.F >= 1000L && !(this.i = !this.i)) continue;
                    graphics.setColor(0xFFFFFF);
                    n5 = n + 5 + e.r.substringWidth((String)object, 0, this.E);
                    graphics.fillRect(n5, n2 + n4, 2, a);
                    continue;
                }
                if (f2.f >= 0) {
                    object = d;
                    if (object == null) {
                        try {
                            d = object = Image.createImage((String)"/items.png");
                        }
                        catch (IOException iOException) {}
                    }
                    n6 = f2.f * 14 % object.getWidth();
                    n5 = f2.f * 14 / object.getWidth() * 14;
                    e.a(graphics, object, n6, n5, 14, 14, 0, n, n3 + n4, 20);
                    this.a(graphics, f2.a, n + 14 + 1, n2 + n4, this.g - 14 - 1, this.h);
                    continue;
                }
                this.a(graphics, f2.a, n, n2 + n4, this.g, this.h);
                continue;
            }
            this.a(graphics, this.b.elementAt(k).toString(), n, n2 + n4, this.g, this.h);
        }
        if (this.p != 0 && this.b.elementAt(this.c) instanceof f && (string = ((f)this.b.elementAt((int)this.c)).c) != null) {
            graphics.setColor(16645016);
            this.a(graphics, string, n, this.l + this.n + 2, this.m - 2, this.h);
        }
    }

    public final void a(Graphics graphics, String string, int n, int n2, int n3, int n4) {
        int n5 = graphics.getColor();
        int n6 = 0;
        int n7 = 0;
        char c2 = '\u0000';
        while (n7 < string.length()) {
            while (n7 < string.length() && (c2 = string.charAt(n7)) > '\u000b') {
                ++n7;
            }
            graphics.drawSubstring(string, n6, n7 - n6, n, 0 + n2, 20);
            n += e.r.substringWidth(string, n6, n7 - n6);
            n6 = n7++;
            switch (c2) {
                case '\u000b': {
                    Image image = a.j;
                    if (image == null) {
                        a.j = image = this.w.a("/symb.png");
                    }
                    e.a(graphics, image, string.charAt(++n7) * 9, 0, 9, 9, 0, n, n2 + (n4 - 9 >> 1), 20);
                    n += 10;
                    n6 = ++n7;
                    c2 = '\u0000';
                    break;
                }
                case '\u0007': {
                    graphics.setColor(n5);
                    n6 = n7;
                    break;
                }
                case '\u0002': 
                case '\u0004': {
                    n += n3 - f.a(string, false);
                }
                case '\u0001': {
                    n6 = ++n7;
                    break;
                }
                case '\u0003': {
                    n += n3 - f.a(string, false) >> 1;
                    n6 = ++n7;
                    break;
                }
                case '\u0006': {
                    graphics.setColor((string.charAt(n7 + 1) & 0xFF) << 16 | (string.charAt(n7 + 2) & 0xFF) << 8 | string.charAt(n7 + 3) & 0xFF);
                    n6 = n7 += 4;
                }
            }
        }
    }

    public final void a() {
        this.e();
    }

    public final boolean a(int n, int n2) {
        if (this.b.size() <= 0) {
            return false;
        }
        long l = System.currentTimeMillis();
        if (this.B && (n >= 48 && n <= 57 || n == 42 || n == -7 || n == -8)) {
            f f2 = (f)this.b.elementAt(this.c);
            if (n == -7 || n == -8) {
                if (this.E > 0) {
                    f2.d.deleteCharAt(--this.E);
                }
                if (this.E == 0 && f2.d.length() > 0) {
                    f2.d.setCharAt(0, Character.toUpperCase(f2.d.charAt(0)));
                }
            } else {
                String string;
                String string2 = string = n == 42 ? "@%&/()=+*" : e[n - 48];
                if (this.C == n && l - this.F < 1000L) {
                    f2.d.setCharAt(this.E - 1, string.charAt(++this.D % string.length()));
                    this.F = l;
                } else {
                    this.D = 0;
                    if (f2.d.length() < f2.e) {
                        f2.d.insert(this.E++, string.charAt(this.D % string.length()));
                        this.C = n;
                        this.F = l;
                    }
                }
                f2.d.setCharAt(0, Character.toUpperCase(f2.d.charAt(0)));
                for (int k = 1; k < f2.d.length(); ++k) {
                    f2.d.setCharAt(k, Character.toLowerCase(f2.d.charAt(k)));
                }
                this.g = Math.max(this.g, f2.a());
                this.d(this.g + 2 + this.H);
                this.i = true;
            }
        } else if (this.B && n2 == 2 && this.E > 0) {
            this.F = 0L;
            --this.E;
        } else if (this.B && n2 == 5) {
            this.F = 0L;
            if (this.E < ((f)this.b.elementAt((int)this.c)).d.length()) {
                ++this.E;
            }
        } else if (n2 == 6 || n2 == 1) {
            this.c = (this.c + this.b.size() + (n2 == 6 ? 1 : -1)) % this.b.size();
            this.B = false;
            this.v = Integer.MAX_VALUE;
        } else if (n2 == 8 || n2 == 3) {
            if (this.b.elementAt(this.c) instanceof f) {
                f f3 = (f)this.b.elementAt(this.c);
                if (!f3.c()) {
                    if (f3.e != 0) {
                        this.B = !this.B;
                        if (this.B) {
                            this.E = f3.d.length();
                            this.v = 400;
                            this.w.b();
                        } else {
                            this.v = Integer.MAX_VALUE;
                        }
                    } else if (f3.i != null) {
                        f3.j = (f3.j + 1) % f3.i.length;
                        this.g = Math.max(this.g, f3.a());
                        this.d(this.g + 2 + this.H);
                    } else {
                        this.w.b((e)this, this.c, this.b.elementAt(this.c));
                    }
                }
            } else {
                this.w.b((e)this, this.c, this.b.elementAt(this.c));
            }
        } else {
            return false;
        }
        return true;
    }

    public final f a(int n) {
        return (f)this.b.elementAt(n);
    }

    public final f f() {
        return (f)this.b.elementAt(this.c);
    }

    public final void a(Object object) {
        if (object instanceof f) {
            object = ((f)object).a;
        }
        for (int k = 0; k < this.b.size(); ++k) {
            Object e2 = this.b.elementAt(k);
            if (e2 instanceof f) {
                if (!((f)e2).a.equals(object)) continue;
                this.b.removeElementAt(k);
                this.b();
                return;
            }
            if (!e2.equals(object)) continue;
            this.b.removeElementAt(k);
            this.b();
            return;
        }
    }
}

