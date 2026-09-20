/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  com.nokia.mid.ui.DeviceControl
 *  javax.microedition.lcdui.Display
 *  javax.microedition.lcdui.Font
 *  javax.microedition.lcdui.Graphics
 *  javax.microedition.lcdui.Image
 */
import com.nokia.mid.ui.DeviceControl;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public class e {
    public static final Font r = Font.getFont((int)0, (int)0, (int)8);
    public static final int s = r.getHeight();
    public long t;
    public int u;
    private int a_;
    public int v = Integer.MAX_VALUE;
    public g w;

    public e(int n) {
        this.u = n;
    }

    public e(int n, int n2) {
        this.u = n;
        this.a_ = n2;
    }

    public e(int n, int n2, int n3) {
        this.u = n;
        this.a_ = n2;
        this.v = n3;
    }

    public void a(Graphics graphics, boolean bl) {
    }

    public boolean a(int n, int n2) {
        return false;
    }

    public void c(int n, int n2) {
    }

    public void a() {
    }

    public void c() {
        if (this.a_ == 1) {
            g.b.notifyDestroyed();
        }
    }

    public void d() {
    }

    public final void e() {
        this.w.repaint();
    }

    public static final void a(Graphics graphics, int n, int n2, int n3, int n4, int n5, int n6, int n7, int n8) {
        int n9 = n4 * (n3 - 7) / n6;
        int n10 = Math.min(n5 * (n3 - 7) / n6, n3 - 8 - n9);
        graphics.setColor(n7);
        graphics.fillRect(n, n2 + 4 + n9, 5, n10);
        graphics.setColor(n8);
        graphics.drawLine(n + 2, n2, n + 2, n2);
        graphics.drawLine(n + 1, n2 + 1, n + 3, n2 + 1);
        graphics.drawLine(n, n2 + 2, n + 4, n2 + 2);
        graphics.drawLine(n, n2 + n3 - 3, n + 4, n2 + n3 - 3);
        graphics.drawLine(n + 1, n2 + n3 - 2, n + 3, n2 + n3 - 2);
        graphics.drawLine(n + 2, n2 + n3 - 1, n + 2, n2 + n3 - 1);
    }

    public static final void a(Graphics graphics, Image image, byte[] byArray, int n, int n2, int n3, int n4, int n5) {
        int n6 = n << 3;
        n2 = n4 == 2 ? (n2 -= byArray[n6 + 6] + byArray[n6 + 0]) : (n2 += byArray[n6 + 6]);
        e.a(graphics, image, byArray[n6 + 2] << 8 | byArray[n6 + 2 + 1] & 0xFF, byArray[n6 + 4] << 8 | byArray[n6 + 4 + 1] & 0xFF, byArray[n6 + 0], byArray[n6 + 1], n4, n2, n3 + byArray[n6 + 7], n5);
    }

    public static final void a(boolean bl) {
        DeviceControl.setLights((int)0, (int)(bl ? 100 : 0));
    }

    public static final void a(Display display, int n) {
        display.vibrate(n);
    }

    public static final void a(Graphics graphics, Image image, int n, int n2, int n3, int n4, int n5, int n6, int n7, int n8) {
        graphics.drawRegion(image, n, n2, n3, n4, n5, n6, n7, n8);
    }
}

