/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.io.Connector
 *  javax.microedition.io.HttpConnection
 */
package com.watAgame.eoe_town;

import com.watAgame.eoe_town.b;
import java.io.ByteArrayOutputStream;
import java.io.EOFException;
import java.io.IOException;
import javax.microedition.io.Connector;
import javax.microedition.io.HttpConnection;

final class d
extends Thread {
    private int b = 0;
    private final String d;
    private String f;
    private final int e;
    private String c;
    private final b i;
    private static int a;
    private static String h;
    private static final Object g;

    public d(b b2, int n, String string, String string2) {
        this.i = b2;
        this.e = n;
        this.d = string;
        this.f = string2;
        this.start();
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     * Unable to fully structure code
     * Enabled aggressive block sorting
     * Enabled unnecessary exception pruning
     * Enabled aggressive exception aggregation
     */
    public final void run() {
        var1_1 = com.watAgame.eoe_town.d.g;
        synchronized (var1_1) {
            if (com.watAgame.eoe_town.d.h != null) {
                this.f = "\u00a6id=" + com.watAgame.eoe_town.d.h + this.f;
            } else if (this.e == 100) {
                return;
            }
            var2_2 = null;
            var3_3 = null;
            var4_4 = null;
            while (true) {
                block72: {
                    block71: {
                        block70: {
                            if (this.b > 2) {
                                this.i.a("3");
                                return;
                            }
                            var2_2 = (HttpConnection)Connector.open((String)this.d, (int)3, (boolean)true);
                            var2_2.setRequestMethod("POST");
                            if (this.d.indexOf("login.pl") >= 0 || this.e == 100) {
                                var5_6 = System.getProperty("microedition.platform");
                                if (var5_6 == null) {
                                    var5_6 = this.i.ab.getAppProperty("UA");
                                }
                                if (var5_6 == null) {
                                    var5_6 = "no30";
                                }
                                var2_2.setRequestProperty("X-User-Agent", var5_6);
                                var6_9 = this.i.ab.getAppProperty("PID-CHKSUM");
                                if (var6_9 != null) {
                                    var2_2.setRequestProperty("X-pid", (String)var6_9);
                                }
                            }
                            var3_3 = var2_2.openOutputStream();
                            var3_3.write(com.watAgame.eoe_town.b.c(this.f));
                            if (var2_2.getResponseCode() == 200) break block70;
                            this.i.a(var2_2.getResponseCode() + " r" + this.e);
                            try {
                                if (var3_3 != null) {
                                    var3_3.close();
                                }
                                if (var4_4 != null) {
                                    var4_4.close();
                                }
                                if (var2_2 == null) return;
                                var2_2.close();
                            }
                            catch (IOException v0) {}
                            return;
                        }
                        var4_4 = var2_2.openDataInputStream();
                        var5_7 = (int)var2_2.getLength();
                        if (var5_7 > 0) {
                            var6_9 = new byte[var5_7];
                            var4_4.readFully((byte[])var6_9);
                            this.c = com.watAgame.eoe_town.b.a((byte[])var6_9);
                        } else {
                            var6_9 = new ByteArrayOutputStream();
                            var7_11 = new byte[1];
                            try {
                                while (true) {
                                    var4_4.readFully(var7_11, 0, 1);
                                    var6_9.write(var7_11[0]);
                                }
                            }
                            catch (EOFException v1) {
                                this.c = com.watAgame.eoe_town.b.a(var6_9.toByteArray());
                            }
                        }
                        if (this.e != 100) break block71;
                        try {
                            if (var3_3 != null) {
                                var3_3.close();
                            }
                            if (var4_4 != null) {
                                var4_4.close();
                            }
                            if (var2_2 == null) return;
                            var2_2.close();
                        }
                        catch (IOException v2) {}
                        return;
                    }
                    if (this.c.startsWith("\u00a6")) {
                        this.c = this.c.substring(1);
                        if (this.c.equals("-2")) {
                            this.i.a("1");
                            break block72;
                        }
                        var6_10 = this.c.indexOf(166) + 1;
                        var7_12 = this.c.indexOf(166, var6_10);
                        if (var6_10 > 0 && var7_12 > 0) {
                            com.watAgame.eoe_town.d.h = this.c.substring(var6_10, var7_12);
                        }
                        try {
                            if (this.e == 0 || this.e == 1) {
                                this.i.b(this.e, this.c);
                                break block72;
                            }
                            this.i.a(this.e, this.c);
                        }
                        catch (Throwable var8_13) {
                            this.i.a("net(" + (this.e == 0 || this.e == 1 ? "p" : "r" + this.e) + ")", var8_13, false);
                        }
                        break block72;
                    }
                    if (this.b < 2) break block72;
                    this.i.a("2");
                }
                try {
                    if (var3_3 != null) {
                        var3_3.close();
                    }
                    if (var4_4 != null) {
                        var4_4.close();
                    }
                    if (var2_2 == null) return;
                    var2_2.close();
                }
                catch (IOException v3) {}
                return;
                catch (SecurityException v4) {
                    if (com.watAgame.eoe_town.d.a++ >= 1) {
                        this.i.ab.destroyApp(true);
                    }
                    this.i.Y = 2;
                    this.i.a("Please allow#GPRS-connection.#EoE only uses#0.1 MB per hour =#approx. EUR 0.30", 0, -1, 0L);
                    {
                        catch (Throwable var9_14) {
                            try {
                                if (var3_3 != null) {
                                    var3_3.close();
                                }
                                if (var4_4 != null) {
                                    var4_4.close();
                                }
                                if (var2_2 == null) throw var9_14;
                                var2_2.close();
                                throw var9_14;
                            }
                            catch (IOException v5) {}
                            throw var9_14;
                        }
                    }
                    try {
                        if (var3_3 != null) {
                            var3_3.close();
                        }
                        if (var4_4 != null) {
                            var4_4.close();
                        }
                        if (var2_2 == null) return;
                        var2_2.close();
                    }
                    catch (IOException v6) {}
                    return;
                    catch (Throwable var5_5) {
                        block73: {
                            if (this.b < 2) ** GOTO lbl149
                            if (this.e == 100) break block73;
                            this.i.a("net", var5_5, false);
                        }
                        try {
                            if (var3_3 != null) {
                                var3_3.close();
                            }
                            if (var4_4 != null) {
                                var4_4.close();
                            }
                            if (var2_2 == null) return;
                            var2_2.close();
                        }
                        catch (IOException v7) {}
                        return;
lbl149:
                        // 2 sources

                        try {
                            if (var3_3 != null) {
                                var3_3.close();
                            }
                            if (var4_4 != null) {
                                var4_4.close();
                            }
                            if (var2_2 != null) {
                                var2_2.close();
                            }
                        }
                        catch (IOException v8) {}
                    }
                }
                ++this.b;
            }
        }
    }

    static {
        g = new Object();
    }
}

