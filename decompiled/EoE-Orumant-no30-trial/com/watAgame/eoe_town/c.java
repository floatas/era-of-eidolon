/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Font
 *  javax.microedition.lcdui.Graphics
 */
package com.watAgame.eoe_town;

import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;

public final class c {
    private final String[] d;
    public final int e;
    public int c;
    public final long a;
    public boolean b = false;

    public c(String[] stringArray, int n, int n2, long l) {
        this.d = stringArray;
        this.e = n;
        this.c = n2;
        this.a = l;
    }

    public final void a(Graphics graphics) {
        int n;
        Font font = graphics.getFont();
        int n2 = font.getHeight() + 1;
        int n3 = 84;
        for (n = 0; n < this.d.length; ++n) {
            n3 = Math.max(n3, font.stringWidth(this.d[n]) + 5);
        }
        n = n2 * this.d.length + 5;
        String string = null;
        if (this.e == 2) {
            string = "Challenge        Back";
            n += n2;
        } else if (this.e == 3) {
            string = "Fight           Decline";
            n += n2;
        }
        if (string != null) {
            n3 = Math.max(n3, font.stringWidth(string));
        }
        int n4 = 65 - n >> 1;
        switch (this.e) {
            case 11: {
                graphics.setColor(0xC0FFC0);
                break;
            }
            case 12: {
                graphics.setColor(0xFFB0B0);
                break;
            }
            default: {
                graphics.setColor(0xFFFFAA);
            }
        }
        graphics.fillRect(96 - n3 >> 1, n4, n3, n);
        graphics.setColor(0);
        graphics.drawRect(96 - n3 >> 1, n4, n3, n);
        for (int i = 0; i < this.d.length; ++i) {
            graphics.setColor(i == 0 && (this.e == 2 || this.e == 3) ? 255 : 0);
            graphics.drawString(this.d[i], 48, n4 + i * n2 + 3, 17);
        }
        if (string != null) {
            graphics.setColor(0xFF0000);
            graphics.drawString(string, 48, n4 + this.d.length * n2 + 3, 17);
        }
    }

    public final String toString() {
        return "\"" + this.d[0].substring(0, Math.min(10, this.d[0].length())) + "...\"[" + this.d.length + "]" + (this.c != -1 ? "->" + this.c : "") + "@" + this.e + "." + this.a;
    }
}

