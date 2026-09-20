/*
 * Decompiled with CFR 0.152.
 */
package com.watAgame.eoe_town;

import com.watAgame.eoe_town.b;
import com.watAgame.eoe_town.d;

final class a
implements Runnable {
    private final b e;
    private final int c;
    private boolean d;
    private final String b;
    private final String a;

    public a(b b2, int n) {
        this.e = b2;
        this.c = n;
        this.d = false;
        switch (this.c) {
            case 2: {
                this.b = "battleping.pl";
                this.a = "";
                break;
            }
            default: {
                this.b = "ping.pl";
                this.a = "\u00a6onlinestatus=";
            }
        }
        if (!this.d) {
            this.d = true;
            new Thread(this).start();
        }
    }

    public final void run() {
        while (this.d) {
            try {
                int n = 0;
                n = this.e.Y == 41 ? 7000 : (this.c == 2 ? 5000 : 15000);
                Thread.sleep(n);
                if (!this.d) {
                    return;
                }
                StringBuffer stringBuffer = new StringBuffer(this.e.P);
                stringBuffer.append(this.b);
                d d2 = new d(this.e, this.c == 2 ? 1 : 0, stringBuffer.toString(), this.c == 1 ? this.a + this.e.w() : this.a);
                d2.join();
            }
            catch (Exception exception) {
                this.e.a("ping", exception, false);
            }
        }
    }

    public final void a() {
        this.d = false;
    }
}

