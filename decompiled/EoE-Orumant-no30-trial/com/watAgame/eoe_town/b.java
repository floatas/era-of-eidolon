/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  com.nokia.mid.ui.DeviceControl
 *  com.nokia.mid.ui.DirectUtils
 *  com.nokia.mid.ui.FullCanvas
 *  javax.microedition.lcdui.Display
 *  javax.microedition.lcdui.Displayable
 *  javax.microedition.lcdui.Font
 *  javax.microedition.lcdui.Graphics
 *  javax.microedition.lcdui.Image
 *  javax.microedition.midlet.MIDlet
 *  javax.microedition.rms.RecordStoreException
 *  javax.microedition.rms.RecordStoreFullException
 */
package com.watAgame.eoe_town;

import com.nokia.mid.ui.DeviceControl;
import com.nokia.mid.ui.DirectUtils;
import com.nokia.mid.ui.FullCanvas;
import com.watAgame.eoe_town.EoETown;
import com.watAgame.eoe_town.a;
import com.watAgame.eoe_town.c;
import com.watAgame.eoe_town.d;
import java.io.ByteArrayOutputStream;
import java.util.Vector;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.midlet.MIDlet;
import javax.microedition.rms.RecordStoreException;
import javax.microedition.rms.RecordStoreFullException;

public final class b
extends FullCanvas
implements Runnable {
    private static final int[] am = new int[]{41, 48, 42, 49, 45, 46, 43, 44};
    private static final String[] aN = new String[]{"Arena", "Tavern", "Home", "Town gate", "Market", "Wise man", "Academy", "Tower"};
    private static final String[] bq = new String[]{" 0", "1.,:;-_'?!\"", "abc2", "def3", "ghi4", "jkl5", "mno6", "pqrs7", "tuv8", "wxyz9"};
    private static final String[] bp = com.watAgame.eoe_town.b.b("Game controls#Fight#Hero#Weapons#Armour#Skills#Spells#Community#Clans#Events");
    public EoETown ab;
    public int Y;
    private final Vector bN = new Vector();
    public volatile Thread ay;
    private int bj;
    private long co;
    public boolean C;
    private int cc;
    private String bY;
    private int bZ;
    private int bh;
    private String[] o;
    private String[] aO;
    private String[] B;
    public boolean aw;
    boolean q = false;
    private boolean r;
    private final Vector bs = new Vector();
    private c V;
    private long aF;
    private long bX;
    private boolean p;
    private int bC;
    public a Z;
    private String j;
    public String P = "http://81.7.141.67/1/";
    private d s;
    private String bE;
    private String ao;
    private String b;
    private String X;
    private String cf;
    private String[] K;
    private Image cq;
    private Image v;
    private Image U;
    private Image bK;
    private Image bu;
    private Image bJ;
    private Image L;
    private Image aq;
    private Image n;
    private Image m;
    private Image al;
    private Image J;
    private Image aB;
    private Image bk;
    private Image aP;
    private Image aI;
    private Image aL;
    private Graphics az;
    private int cj;
    private boolean br;
    private boolean aU;
    private boolean bd;
    private boolean cp;
    private boolean bb;
    private String ca = null;
    private String d = null;
    private char bQ = '\u0000';
    private int bF;
    private int aa;
    private int bO = 1;
    private String A = "";
    private String[][] aY = null;
    private String aH;
    private String aZ;
    private int au;
    private int ac;
    public String[][] bx;
    public String G;
    public String ai;
    public String aJ;
    public String af;
    private String[] bz;
    public boolean be = true;
    private String bA;
    private String bI;
    private String x;
    private String bT;
    private String g;
    private String at;
    private String z;
    private String bB;
    private String T;
    private String bn;
    private int aE;
    private int bi;
    private String[] bV;
    private String u = "0";
    private int aR;
    private String ah;
    private String ak;
    private int O;
    private String[][] bt;
    private char an = (char)110;
    private String E;
    private boolean cd = false;
    private boolean cu = false;
    private boolean bU = false;
    static final Font cm;
    static final Font R;
    static final Font bP;
    static final Font cn;
    static final Font as;
    static final int[][] bM;
    static final int[][] h;
    static final int[] aX;
    private static final int ci;
    private boolean c;
    private int[][] aD;
    private int[][] a;
    private int cl;
    private int bS;
    private int bL;
    private int bg;
    private int aS;
    private Vector bv;
    private int[][] cg;
    private String[][] bc;
    private String[][] aV;
    private int[] M;
    private int[] ch;
    private int[] aT;
    private static final int[] bo;
    private int[][] bl;
    private long aA;
    private long bR;
    private long w;
    private int aW;
    private int ae;
    private int aG;
    private int ag;
    private int W;
    private int aK;
    private int ad;
    private int aM;
    private int bf;
    private Vector F;
    private String[] i;
    private int[] ar;
    private int[] ba;
    private String ck;
    private String aC;
    private String I;
    private String y;
    private String av;
    private int[] ce;
    private boolean N;
    private boolean t;
    private String[] ct;
    private int cr;
    private int ax;
    private int cs;
    private String[] f;
    private int cv = 0;
    private int k = 0;
    private boolean H;
    private boolean bw = false;
    private boolean S = false;
    private char bD = '\u0000';
    private int D = 0;
    private int bm = 0;
    private int aQ = 0;
    private StringBuffer aj = null;
    private Vector cw = null;
    private String by = null;
    private long cb;
    int bG;
    int[][][] ap;
    private static final int[] bH;
    private static final int[] bW;
    private static final int[] Q;
    private static final int[] e;
    private long l;

    public b(EoETown eoETown) {
        this.ab = eoETown;
        this.ay = new Thread(this);
        this.ay.start();
    }

    public final void run() {
        long l = 0L;
        long l2 = 0L;
        while (this.ay != null) {
            long l3;
            l = l3 = System.currentTimeMillis();
            try {
                boolean bl;
                this.bj = 1000;
                com.watAgame.eoe_town.b.a(true);
                if (this.V != null && this.V.e != 17) {
                    if (this.Y == 90 || this.Y == 89) {
                        this.r();
                    }
                    if (this.V.a > 0L && System.currentTimeMillis() - this.cb > this.V.a) {
                        if (this.V.e != 16 || !this.q) {
                            this.v();
                            this.repaint();
                            this.bj = 0;
                        }
                    } else if (this.V.e == 16 && !this.q && this.V.b) {
                        this.v();
                        this.repaint();
                        this.bj = 0;
                    }
                }
                if (this.V == null) {
                    switch (this.Y) {
                        case 0: {
                            this.co = l3;
                            this.bj = 0;
                            this.aw = true;
                            this.bC = 0;
                            this.i(2);
                            break;
                        }
                        case 2: {
                            if (this.bC < 10) {
                                ++this.bC;
                            } else {
                                this.i(4);
                                this.l(34);
                            }
                            this.bj = 500;
                            break;
                        }
                        case 7: {
                            if (this.cj < 0) {
                                this.cj = 0;
                                this.l = l3;
                            } else if (!this.bb && l3 - this.l > 4000L) {
                                bl = false;
                                if (!this.br) {
                                    this.l(30);
                                    bl = true;
                                } else if (!this.aU) {
                                    this.l(31);
                                    bl = true;
                                } else if (!this.bd) {
                                    this.l(32);
                                    bl = true;
                                } else if (!this.cp) {
                                    this.l(33);
                                    bl = true;
                                } else if (this.cj >= 4) {
                                    this.m();
                                    break;
                                }
                                if (bl) {
                                    ++this.cj;
                                    this.l = l3;
                                    this.bb = true;
                                    this.repaint();
                                }
                            }
                            this.bj = 250;
                            break;
                        }
                        case 14: {
                            this.cq = null;
                            break;
                        }
                        case 66: {
                            if (Display.getDisplay((MIDlet)this.ab).getCurrent() != this) break;
                            this.ab.a(this.bx);
                            break;
                        }
                        case 68: {
                            if (Display.getDisplay((MIDlet)this.ab).getCurrent() != this) break;
                            this.ab.a(this.bz);
                            break;
                        }
                        case 40: {
                            ++this.aa;
                            this.bj = 200;
                            this.repaint();
                            break;
                        }
                        case 12: 
                        case 31: 
                        case 59: 
                        case 60: 
                        case 71: 
                        case 73: 
                        case 80: 
                        case 83: 
                        case 84: 
                        case 112: {
                            this.t();
                            this.bj = 500;
                            this.repaint();
                            break;
                        }
                        case 95: {
                            this.bj = 250;
                            this.repaint();
                            break;
                        }
                        case 88: {
                            if (this.c && this.V == null) {
                                this.aA = System.currentTimeMillis();
                                this.bj = 0;
                                this.i(89);
                                break;
                            }
                            this.bj = 250;
                            this.repaint();
                            break;
                        }
                        case 89: 
                        case 90: 
                        case 91: 
                        case 92: 
                        case 93: {
                            this.r();
                            break;
                        }
                        case 18: {
                            break;
                        }
                        case 94: {
                            if (this.ax < this.cr) {
                                boolean bl2 = this.ct == null;
                                if (bl2 || this.ax > 0) {
                                    this.z();
                                }
                                this.ad = Integer.parseInt(this.ct[2]);
                                this.aK = Integer.parseInt(this.ct[0]);
                                this.e(this.ct[1]);
                                this.a(this.ct[1], this.aK, this.aD, 0);
                                this.e(this.ct[3]);
                                this.a(this.ct[3], this.ad, this.a, 0);
                                if (bl2) {
                                    this.repaint();
                                    break;
                                }
                                this.cs = 0;
                                this.e(this.ct[10]);
                                this.i(96);
                                break;
                            }
                            if (this.ct != null && this.ct[4].equals("0")) {
                                this.i(18);
                                this.l(28);
                                this.a(this.g(44), 16, 100, 5000L);
                                break;
                            }
                            if (this.ct != null && this.ct[4].equals("1")) {
                                this.i(18);
                                this.l(28);
                                this.a(this.g(43), 16, 100, 5000L);
                                break;
                            }
                            this.c = false;
                            this.l(25);
                            this.i(88);
                            this.a(this.g(42), 16, -1, 5000L);
                            this.cd = false;
                            break;
                        }
                        case 96: {
                            if (this.cs >= this.bG) {
                                if (this.ct[12].length() > 0) {
                                    this.i(97);
                                } else if (this.ct[11].length() > 0) {
                                    this.cs = 0;
                                    this.e(this.ct[11]);
                                    this.i(98);
                                } else {
                                    this.i(99);
                                }
                                this.bj = 0;
                                break;
                            }
                            if (this.ct[9].equals("0")) {
                                this.a(this.ct[10], this.aK, this.aD, this.cs);
                            } else {
                                this.a(this.ct[10], this.ad, this.a, this.cs);
                            }
                            ++this.cs;
                            this.bj = 250;
                            this.repaint();
                            break;
                        }
                        case 97: {
                            if (this.ce == null) {
                                int n = this.ct[9].equals("0") ? Integer.parseInt(this.ct[0]) : Integer.parseInt(this.ct[2]);
                                int n2 = Integer.parseInt(this.ct[13]);
                                int n3 = h[n][0];
                                int n4 = h[n][1];
                                int n5 = h[n2][0];
                                int n6 = h[n2][1];
                                int n7 = n2 % 6 - n % 6;
                                int n8 = n2 / 6 - n / 6;
                                int n9 = 300 * com.watAgame.eoe_town.b.d(n7 * n7 + n8 * n8 << 8) >> 4;
                                if (n9 != 0) {
                                    int n10 = (n5 - n3 << 16) / n9;
                                    int n11 = (n6 - n4 << 16) / n9;
                                    this.ce = new int[]{n3, n4, n5, n6, n10, n11};
                                } else {
                                    this.N = true;
                                }
                            }
                            if (this.N) {
                                if (this.ct[11].length() > 0) {
                                    this.cs = 0;
                                    this.e(this.ct[11]);
                                    this.i(98);
                                } else {
                                    this.i(99);
                                }
                                this.ce = null;
                                this.N = false;
                                this.bj = 0;
                                break;
                            }
                            this.repaint();
                            this.serviceRepaints();
                            this.bj = 0;
                            break;
                        }
                        case 98: {
                            if (this.cs >= this.bG) {
                                this.i(99);
                                this.bj = 0;
                                break;
                            }
                            if (this.ct[9].equals("0")) {
                                this.a(this.ct[11], this.ad, this.a, this.cs);
                            } else {
                                this.a(this.ct[11], this.aK, this.aD, this.cs);
                            }
                            ++this.cs;
                            this.bj = 250;
                            this.repaint();
                            break;
                        }
                        case 99: {
                            if (!this.t && this.ct[7].length() > 0) {
                                this.t = true;
                                if (this.ct[5].equals("0") || this.ct[5].equals("2")) {
                                    try {
                                        com.watAgame.eoe_town.b.a(Display.getDisplay((MIDlet)this.ab), 600);
                                    }
                                    catch (IllegalStateException illegalStateException) {}
                                    this.aG += Integer.parseInt(this.ct[6]);
                                }
                                this.bj = 1500;
                                this.repaint();
                                break;
                            }
                            this.t = false;
                            ++this.ax;
                            this.i(94);
                            this.bj = 0;
                            break;
                        }
                        case 100: {
                            if (this.f[7].length() > 0) {
                                this.a(com.watAgame.eoe_town.b.b(this.f[7]), 0, 100, 0L);
                                this.f[7] = "";
                                this.i(101);
                                break;
                            }
                            if (this.f[0].length() > 0) {
                                this.a(this.g(59), 0, 103, 0L);
                                this.i(101);
                                break;
                            }
                            if (this.Z == null) {
                                this.Z = new a(this, 1);
                            }
                            this.cv = 0;
                            this.i(104);
                            break;
                        }
                        case 101: {
                            this.repaint();
                        }
                    }
                }
                if (this.Y == 7 || this.Y == 18 || this.Y == 95 || this.s != null && this.s.isAlive()) {
                    this.bj = Math.min(this.bj, 600);
                    if (this.aI == null) {
                        this.aI = com.watAgame.eoe_town.b.a("wait", true);
                    }
                    this.repaint(2, 0, this.aI.getWidth(), 10);
                }
                bl = false;
                if (this.cc == 1 && l3 - this.aF < 6000L || this.bZ == 1 && l3 - this.bX < 6000L) {
                    this.bj = Math.min(this.bj, 200);
                    bl = true;
                } else if (this.aF != 0L) {
                    bl = true;
                    this.aF = 0L;
                }
                if (bl) {
                    if (this.bK == null) {
                        this.bK = com.watAgame.eoe_town.b.a("mail", true);
                    }
                    if (this.bu == null) {
                        this.bu = com.watAgame.eoe_town.b.a("challenge", true);
                    }
                    this.repaint(37, 57, 51 + this.bK.getWidth(), Math.max(this.bu.getHeight(), this.bK.getHeight()));
                }
                ++this.bF;
                l3 = System.currentTimeMillis();
                if (l3 - this.co > 600000L && !this.r) {
                    this.a("0");
                }
                long l4 = (long)this.bj + l - l3;
                if (this.bj == 1000 && l3 - l2 > 5000L || l3 - l2 > 10000L) {
                    System.gc();
                    l2 = l3;
                    l4 = (long)this.bj + l - System.currentTimeMillis();
                }
                if (l4 <= 0L) continue;
                Thread.sleep(l4);
            }
            catch (Throwable throwable) {
                this.a("run", throwable, false);
            }
        }
    }

    /*
     * Unable to fully structure code
     */
    protected final void keyPressed(int var1_1) {
        try {
            block333: {
                block332: {
                    block335: {
                        block334: {
                            var2_2 = 0;
                            try {
                                var2_2 = this.getGameAction(var1_1);
                            }
                            catch (Exception v0) {}
                            var3_4 = this.V;
                            if (var3_4 == null || var3_4.e == 17) break block332;
                            var4_5 = var3_4.e;
                            var5_16 = var3_4.c;
                            if (var1_1 != -6 && var1_1 != -7 && var2_2 != 8) break block333;
                            if (var4_5 != 14) break block334;
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.l(8);
                                this.a("Action successful.", 0, -1, 1000L);
                            } else if (var1_1 == -7) {
                                this.v();
                            }
                            break block335;
                        }
                        if (var4_5 != 0 && var4_5 != 11) ** GOTO lbl29
                        if (var5_16 == 86 || var5_16 == 87) {
                            this.a(com.watAgame.eoe_town.b.b(this.bt[this.cv][1]), var5_16 == 86 && this.bt[this.cv][2].startsWith("*") != false ? 1 : 10, var5_16, 0L);
                        } else {
                            if (System.currentTimeMillis() - this.cb > 500L) {
                                this.v();
                            }
                            this.repaint();
                            return;
lbl29:
                            // 1 sources

                            if (this.V.e == 16) {
                                this.V.b = true;
                                if (!this.q) {
                                    this.v();
                                }
                                return;
                            }
                            if (var4_5 == 1 && var5_16 == 86) {
                                this.i(var5_16);
                            } else if (var4_5 == 12 || var4_5 == 13 || var4_5 == 18) {
                                if (var1_1 == -6 || var2_2 == 8 || var4_5 == 18 || var4_5 == 12) {
                                    if (this.s != null) {
                                        this.s.join();
                                    }
                                    this.ab.destroyApp(true);
                                } else if (var1_1 == -7) {
                                    this.v();
                                }
                            } else if (var1_1 == -7 && (var4_5 == 0 || var4_5 == 1 || var4_5 == 2 || var4_5 == 15 || var4_5 == 6 || var4_5 == 8 || var4_5 == 9 || var4_5 == 10)) {
                                if (var5_16 == 11 && (var4_5 == 15 || var4_5 == 9)) {
                                    this.ab.destroyApp(true);
                                } else if (var5_16 == 11 && var4_5 == 8) {
                                    this.cv = 1;
                                    this.i(var5_16);
                                } else {
                                    if (var4_5 == 10 && var5_16 == 48) {
                                        this.c();
                                        this.l(71);
                                    } else if (var4_5 == 10 && var5_16 == 75) {
                                        this.i(75);
                                    } else if (var4_5 != 10 && var5_16 != 89 && var4_5 != 6 && var4_5 != 15) {
                                        this.cv = 0;
                                    }
                                    this.i(var5_16);
                                }
                            } else if ((var1_1 == -6 || var2_2 == 8 || var1_1 == -7) && var4_5 == 3) {
                                this.an = var1_1 == -6 || var2_2 == 8 ? (char)121 : (char)110;
                                this.l(23);
                            } else if (var4_5 == 2 && (var1_1 == -6 || var2_2 == 8)) {
                                this.l(24);
                            } else if (var1_1 == -6 || var2_2 == 8) {
                                if (var4_5 == 15) {
                                    if (!this.cd) {
                                        this.cd = true;
                                        this.i(95);
                                        this.a(this.g(40), 17, -1, 0L);
                                        this.l(26);
                                    }
                                } else if (var4_5 == 6) {
                                    this.l(27);
                                } else if (var4_5 == 10) {
                                    if (var5_16 == 86) {
                                        this.l(20);
                                    } else if (var5_16 == 87) {
                                        this.l(22);
                                    } else if (var5_16 == 48) {
                                        this.l(68);
                                    } else if (var5_16 == 81) {
                                        this.l(66);
                                    } else if (var5_16 == 75) {
                                        this.l(72);
                                    } else if (var5_16 == 11) {
                                        this.l(5);
                                    } else if (var5_16 == 103) {
                                        var6_22 = Integer.parseInt(this.f[this.cv + 1]);
                                        this.f[this.cv + 1] = var7_24 = Integer.toString(var6_22 + this.ba[this.cv]);
                                        this.f[0] = Integer.toString(Integer.parseInt(this.f[0]) - 1);
                                        if (Integer.parseInt(this.f[0]) <= 0) {
                                            this.l(35);
                                        }
                                    }
                                }
                            }
                        }
                    }
                    this.v();
                    break block333;
                }
                if (this.aw && !this.q && this.Y != 18 && this.Y != 94 && this.Y != 96 && this.Y != 97 && this.Y != 98 && this.Y != 99 && this.Y != 100) {
                    this.co = System.currentTimeMillis();
                    if (com.watAgame.eoe_town.b.c(var1_1) && this.Y != 89 && this.Y != 71 && this.Y != 73 && this.Y != 60 && this.Y != 59 && this.Y != 31 && this.Y != 12 && (this.Y < 88 || this.Y > 99) && this.Y != 100 && this.Y != 80 && this.Y != 112 && this.Y != 84 && this.Y != 83 && this.Y != 11 && this.Y != 14 && this.V == null) {
                        if (this.cc == 1) {
                            this.a(this.o, this.Y, 3);
                            return;
                        }
                        this.a("Sorry! Nobody#is challenging U#right now. Swords#will appear below#upon a challenge", 0, -1, 0L);
                        return;
                    }
                    switch (this.Y) {
                        case 2: {
                            this.l(34);
                            this.i(4);
                            break;
                        }
                        case 5: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.l(5);
                                break;
                            }
                            if (var1_1 != -7) break;
                            this.ab.destroyApp(true);
                            break;
                        }
                        case 11: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                switch (this.cv) {
                                    case 0: {
                                        this.a(this.bE, true, 14);
                                        this.i(12);
                                        break;
                                    }
                                    case 1: {
                                        this.a(this.ao, false, 14);
                                        this.i(12);
                                        break;
                                    }
                                    case 2: {
                                        this.l(3);
                                        break;
                                    }
                                    case 3: {
                                        this.l(4);
                                    }
                                }
                                break;
                            }
                            if (this.bE.length() == 0 || this.ao.length() == 0) {
                                if (var2_2 != 6 && var2_2 != 1) break;
                                this.cv = (this.cv + 1) % 2;
                                break;
                            }
                            this.b(var2_2, "01".equals("03") != false ? 3 : 4);
                            break;
                        }
                        case 12: {
                            if (var1_1 == -6 || var1_1 == -5 || var1_1 == -1 || var1_1 == -2) {
                                if (this.cv == 0) {
                                    this.bE = this.n();
                                    if (this.ao.length() > 0 && this.bE.length() > 0) {
                                        this.cv = 2;
                                    } else {
                                        this.cv = 1;
                                        this.a(this.ao, false, 14);
                                    }
                                } else if (this.cv == 1) {
                                    this.ao = this.n();
                                    this.cv = this.bE.length() == 0 || var1_1 == -1 ? 0 : (this.ao.length() == 0 ? 1 : 2);
                                }
                                this.i(11);
                                break;
                            }
                            this.j(var1_1);
                            break;
                        }
                        case 14: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                switch (this.cv) {
                                    case 0: 
                                    case 1: {
                                        if (this.K[this.cv].length() == 0) {
                                            this.e();
                                            break;
                                        }
                                        this.l(6);
                                        break;
                                    }
                                    case 2: {
                                        if (this.K[0].length() == 0 && this.K[1].length() == 0) break;
                                        this.B = this.K[0].length() > 0 && this.K[1].length() > 0 ? new String[]{this.K[0], this.K[1]} : (this.K[0].length() > 0 ? new String[]{this.K[0]} : new String[]{this.K[1]});
                                        this.k = 0;
                                        this.i(15);
                                        this.repaint();
                                        this.serviceRepaints();
                                    }
                                }
                                if (this.Y == 15 || this.Y == 30) break;
                                this.bN.addElement(new Integer(14));
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 15: {
                            if (var1_1 == -7) {
                                this.i(14);
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.a(this.g(77), 14, -1, 0L);
                                break;
                            }
                            if (var2_2 != 1 && var2_2 != 6 || this.K[0].length() <= 0 || this.K[1].length() <= 0) break;
                            this.k = (this.k + 1) % 2;
                            break;
                        }
                        case 30: {
                            if (var1_1 == -7 && !this.bN.isEmpty()) {
                                this.ca = "";
                                this.bQ = '\u0000';
                                this.cv = 0;
                                this.i(this.c());
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                switch (this.cv) {
                                    case 0: {
                                        this.a(this.ca, true, 14);
                                        this.i(31);
                                        break;
                                    }
                                    case 1: {
                                        this.B = new String[]{"Male", "Female"};
                                        this.k = 0;
                                        this.i(32);
                                        break;
                                    }
                                    case 2: {
                                        this.l(7);
                                        this.cv = 0;
                                    }
                                }
                                break;
                            }
                            if (this.ca.length() == 0 || this.bQ == '\u0000') {
                                this.b(var2_2, 2);
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 31: {
                            if (var1_1 == -6 || var1_1 == -5 || var1_1 == -1 || var1_1 == -2) {
                                this.ca = this.n();
                                this.i(30);
                                if (this.bQ != '\u0000' && var1_1 == -1 && this.ca.length() > 0) {
                                    this.cv = 2;
                                    break;
                                }
                                this.cv = 1;
                                break;
                            }
                            this.j(var1_1);
                            break;
                        }
                        case 32: {
                            if (var1_1 == -7) {
                                this.bQ = '\u0000';
                                this.i(30);
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.i(30);
                                this.cv = this.ca.length() > 0 ? 2 : 0;
                                if (this.k == 0) {
                                    this.bQ = (char)109;
                                    break;
                                }
                                this.bQ = (char)102;
                                break;
                            }
                            if (var2_2 != 1 && var2_2 != 6) break;
                            this.k = (this.k + 1) % 2;
                            break;
                        }
                        case 40: {
                            if (var1_1 == -7 && !this.bN.isEmpty()) {
                                this.cv = 0;
                                this.i(this.c());
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.cv == 3) {
                                    this.a(this.g(39), 13, -1, 0L);
                                    break;
                                }
                                this.bN.addElement(new Integer(40));
                                this.i(com.watAgame.eoe_town.b.am[this.cv]);
                                if (this.cv == 5) {
                                    this.O = com.watAgame.eoe_town.b.bp.length;
                                    this.ah = "Help categories:";
                                    this.ak = "";
                                    this.bt = new String[this.O][4];
                                    for (var4_6 = 0; var4_6 < this.O; ++var4_6) {
                                        for (var5_17 = 0; var5_17 < 4; ++var5_17) {
                                            if (var5_17 == 2) {
                                                this.bt[var4_6][2] = com.watAgame.eoe_town.b.bp[var4_6];
                                                continue;
                                            }
                                            this.bt[var4_6][var5_17] = "";
                                        }
                                    }
                                    this.bi = 0;
                                }
                                this.cv = 0;
                                break;
                            }
                            this.b(var2_2, 8);
                            this.aa = 0;
                            break;
                        }
                        case 41: {
                            if (var1_1 == -7 && !this.bN.isEmpty()) {
                                this.cv = 0;
                                this.aa = 0;
                                this.i(this.c());
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.bN.addElement(new Integer(41));
                                if (this.cv == 0) {
                                    this.l(10);
                                    break;
                                }
                                if (this.cv == 1) {
                                    this.l(9);
                                    break;
                                }
                                if (this.cv == 2) {
                                    this.l(55);
                                    break;
                                }
                                if (this.cv == 3) {
                                    this.l(56);
                                    break;
                                }
                                if (this.cv != 4) break;
                                this.aH = "";
                                this.aZ = "";
                                this.cv = 0;
                                this.i(57);
                                break;
                            }
                            this.b(var2_2, 5);
                            break;
                        }
                        case 52: 
                        case 58: 
                        case 72: 
                        case 74: 
                        case 86: 
                        case 87: 
                        case 106: 
                        case 114: 
                        case 115: 
                        case 117: {
                            if (var1_1 == -7) {
                                if (this.Y == 86 || this.Y == 114 || this.Y == 117 || this.Y == 106) {
                                    this.cv = 0;
                                    this.i(this.c());
                                    break;
                                }
                                if (this.Y == 115) {
                                    this.cv = 2;
                                    this.c();
                                    this.i(110);
                                    break;
                                }
                                if (this.Y == 58) {
                                    this.cv = 2;
                                    this.c();
                                    this.i(41);
                                    break;
                                }
                                if (this.Y == 72 || this.Y == 74) {
                                    this.cv = this.Y == 72 ? 2 : 3;
                                    this.i(this.c());
                                    break;
                                }
                                this.i(this.c());
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.Y == 52 || this.Y == 58) {
                                    this.a(this.bt[this.cv], this.Y, 2);
                                    break;
                                }
                                if (this.Y == 114) {
                                    this.bV[this.aR] = this.bt[this.cv][0];
                                    this.cv = this.aR;
                                    this.i(this.c());
                                    break;
                                }
                                if (this.Y == 115) {
                                    this.u = this.bt[this.cv][0];
                                    this.bV[3] = this.bt[this.cv][2];
                                    this.cv = 2;
                                    this.i(110);
                                    break;
                                }
                                if (this.Y == 72) {
                                    this.l(47);
                                    break;
                                }
                                if (this.Y == 74) {
                                    this.l(50);
                                    break;
                                }
                                if (this.Y == 117) {
                                    var4_7 = this.bt[this.cv][3];
                                    this.a(com.watAgame.eoe_town.b.b(var4_7), 0, 117, 0L);
                                    break;
                                }
                                if (this.Y == 106) break;
                                var4_8 = this.bt[this.cv][3];
                                this.a(this.g(Integer.parseInt(var4_8)), 0, this.Y, 0L);
                                break;
                            }
                            if (var2_2 != 6 && var2_2 != 1 || this.O == 0) break;
                            this.f(var2_2);
                            break;
                        }
                        case 76: 
                        case 78: 
                        case 116: {
                            if (var1_1 == -7) {
                                this.cv = 0;
                                this.i(this.c());
                            }
                            if (var2_2 != 6 && var2_2 != 1 || this.O == 0) break;
                            this.f(var2_2);
                            break;
                        }
                        case 46: {
                            if (var1_1 == -7) {
                                this.cv = 5;
                                this.i(this.c());
                                break;
                            }
                            if (var2_2 == 6 || var2_2 == 1) {
                                this.f(var2_2);
                                break;
                            }
                            if (var1_1 != -6 && var2_2 != 8) break;
                            this.l(53);
                            break;
                        }
                        case 47: {
                            if (var1_1 == -7) {
                                this.O = 10;
                                this.ah = "Help categories:";
                                this.ak = "";
                                this.bt = new String[10][4];
                                for (var4_9 = 0; var4_9 < 10; ++var4_9) {
                                    for (var5_18 = 0; var5_18 < 4; ++var5_18) {
                                        if (var5_18 == 2) {
                                            this.bt[var4_9][2] = com.watAgame.eoe_town.b.bp[var4_9];
                                            continue;
                                        }
                                        this.bt[var4_9][var5_18] = "";
                                    }
                                }
                                this.bi = 0;
                                this.cv = 0;
                                this.i(46);
                                break;
                            }
                            if (var2_2 == 6 || var2_2 == 1) {
                                this.f(var2_2);
                                break;
                            }
                            if (var1_1 != -6 && var2_2 != 8) break;
                            var4_10 = this.bt[this.cv][1];
                            this.a(com.watAgame.eoe_town.b.b(var4_10), 0, this.Y, 0L);
                            break;
                        }
                        case 54: {
                            if (var1_1 == -7) {
                                this.cv = 0;
                                this.i(this.c());
                                break;
                            }
                            if (var2_2 == 6) {
                                if (this.cv == this.aY.length - 1) {
                                    this.l(10);
                                    break;
                                }
                                this.cv = (this.cv + 1) % this.aY.length;
                                break;
                            }
                            if (var2_2 == 1) {
                                this.cv = (this.cv + this.aY.length - 1) % this.aY.length;
                                break;
                            }
                            if (var1_1 != -6 && var2_2 != 8) break;
                            this.a(this.aY[this.cv], 54, 2);
                            break;
                        }
                        case 57: {
                            if (var1_1 == -7 && !this.bN.isEmpty()) {
                                this.aH = "";
                                this.aZ = "";
                                this.cv = 2;
                                this.i(this.c());
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                switch (this.cv) {
                                    case 0: {
                                        this.a(this.aH, true, 14);
                                        this.i(59);
                                        break;
                                    }
                                    case 1: {
                                        this.a(this.aZ, false, 30);
                                        this.i(60);
                                        break;
                                    }
                                    case 2: {
                                        this.l(11);
                                    }
                                }
                                break;
                            }
                            if (this.aH.length() == 0 && this.aZ.length() == 0) {
                                this.b(var2_2, 2);
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 59: {
                            if (var1_1 == -6 || var1_1 == -5 || var1_1 == -2) {
                                this.aH = this.n();
                                this.i(57);
                                this.cv = 1;
                                break;
                            }
                            if (var1_1 == -1) {
                                this.aH = this.n();
                                this.i(57);
                                if (this.aH.length() == 0 && this.aZ.length() == 0) {
                                    this.cv = 1;
                                    break;
                                }
                                this.cv = 2;
                                break;
                            }
                            this.j(var1_1);
                            break;
                        }
                        case 60: {
                            if (var1_1 == -6 || var1_1 == -5 || var1_1 == -2) {
                                this.aZ = this.n();
                                this.i(57);
                                if (this.aH.length() == 0 && this.aZ.length() == 0) {
                                    this.cv = 0;
                                    break;
                                }
                                this.cv = 2;
                                break;
                            }
                            if (var1_1 == -1) {
                                this.aZ = this.n();
                                this.i(57);
                                this.cv = 0;
                                break;
                            }
                            this.j(var1_1);
                            break;
                        }
                        case 43: 
                        case 44: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.bN.addElement(new Integer(this.Y));
                                this.aE = this.Y == 43 ? this.cv + 9 : this.cv + 13;
                                this.l(19);
                                break;
                            }
                            if (var1_1 == -7) {
                                if (this.Y == 43) {
                                    this.cv = 6;
                                } else if (this.Y == 44) {
                                    this.cv = 7;
                                }
                                this.i(this.c());
                                break;
                            }
                            this.b(var2_2, 4);
                            break;
                        }
                        case 45: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.bN.addElement(new Integer(this.Y));
                                if (this.cv == 0) {
                                    this.i(85);
                                    break;
                                }
                                if (this.cv >= 1 && this.cv < 5) {
                                    this.aE = this.cv + 3;
                                    this.l(19);
                                    break;
                                }
                                if (this.cv != 5) break;
                                this.l(21);
                                break;
                            }
                            if (var1_1 == -7) {
                                this.cv = 4;
                                this.i(this.c());
                                break;
                            }
                            this.b(var2_2, 6);
                            break;
                        }
                        case 85: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.bN.addElement(new Integer(this.Y));
                                this.aE = this.cv + 1;
                                this.l(19);
                                break;
                            }
                            if (var1_1 == -7) {
                                this.cv = 0;
                                this.i(this.c());
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 48: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.cv != 0 && this.cv != 1) {
                                    this.bN.addElement(new Integer(this.Y));
                                }
                                if (this.cv == 0) {
                                    this.l(13);
                                    break;
                                }
                                if (this.cv == 1) {
                                    this.l(15);
                                    break;
                                }
                                if (this.cv == 2) {
                                    this.cv = 0;
                                    this.i(70);
                                    break;
                                }
                                if (this.cv == 3) {
                                    this.l(67);
                                    break;
                                }
                                if (this.cv != 4) break;
                                this.cv = 0;
                                this.i(77);
                                break;
                            }
                            if (var1_1 == -7 && !this.bN.isEmpty()) {
                                this.cv = 1;
                                this.aa = 0;
                                this.i(this.c());
                                break;
                            }
                            this.b(var2_2, 5);
                            break;
                        }
                        case 70: {
                            if (var1_1 == -7) {
                                this.i(this.c());
                                this.cv = 0;
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                switch (this.cv) {
                                    case 0: {
                                        this.a(this.A, true, 14);
                                        this.i(71);
                                        break;
                                    }
                                    case 1: {
                                        this.a(this.A, true, 14);
                                        this.i(73);
                                        break;
                                    }
                                    case 2: {
                                        this.l(46);
                                        break;
                                    }
                                    case 3: {
                                        this.l(49);
                                    }
                                }
                                break;
                            }
                            if (var2_2 == 6) {
                                this.cv = (this.cv + 1) % 4;
                                break;
                            }
                            if (var2_2 != 1) break;
                            this.cv = (this.cv + 3) % 4;
                            break;
                        }
                        case 71: 
                        case 73: {
                            if (var1_1 == -6 || var1_1 == -5) {
                                this.A = this.n();
                                if (this.A.length() > 0) {
                                    if (this.Y == 71) {
                                        this.l(45);
                                        break;
                                    }
                                    this.l(48);
                                    break;
                                }
                                this.i(70);
                                break;
                            }
                            this.j(var1_1);
                            break;
                        }
                        case 75: {
                            if (var1_1 == -7) {
                                this.i(this.c());
                                this.cv = 3;
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.cv == 0) {
                                    this.l(60);
                                    break;
                                }
                                if (this.cv == 1) {
                                    this.l(61);
                                    break;
                                }
                                if (this.cv != 2) break;
                                if (this.bI.equals("3")) {
                                    this.a(com.watAgame.eoe_town.b.b(this.g), 10, 75, 0L);
                                    break;
                                }
                                if (!this.bI.equals("4")) break;
                                this.cv = 0;
                                this.bA = "";
                                this.i(79);
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 79: {
                            if (var1_1 == -7) {
                                this.cv = 2;
                                this.i(75);
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.cv == 0) {
                                    this.a(this.bA, true, 14);
                                    this.i(80);
                                    break;
                                }
                                if (this.cv == 1) {
                                    this.l(65);
                                    break;
                                }
                                if (this.cv != 2) break;
                                this.l(69);
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 80: {
                            if (var1_1 == -6 || var1_1 == -5) {
                                this.bA = this.n();
                                if (this.bA.length() > 0) {
                                    this.l(63);
                                    break;
                                }
                                this.i(79);
                                break;
                            }
                            this.j(var1_1);
                            break;
                        }
                        case 82: {
                            if (var1_1 == -7) {
                                this.i(79);
                                this.cv = 2;
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.cv == 0) {
                                    this.a(this.T, true, 14);
                                    this.i(83);
                                    break;
                                }
                                if (this.cv == 1) {
                                    this.a(this.bn, true, 3);
                                    this.i(84);
                                    break;
                                }
                                if (this.cv != 2) break;
                                this.l(64);
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 83: {
                            if (var1_1 == -6 || var1_1 == -5 || var1_1 == -1 || var1_1 == -2) {
                                this.T = this.n();
                                if (this.T.length() == 0) {
                                    this.T = this.z;
                                }
                                this.cv = var1_1 == -6 || var1_1 == -5 || var1_1 == -1 ? 1 : 2;
                                this.i(82);
                                break;
                            }
                            this.j(var1_1);
                            break;
                        }
                        case 84: {
                            if (var1_1 == -6 || var1_1 == -5 || var1_1 == -1 || var1_1 == -2) {
                                this.bn = this.n();
                                if (this.bn.length() == 0) {
                                    this.bn = this.bB;
                                }
                                this.cv = var1_1 == -6 || var1_1 == -5 || var1_1 == -2 ? 2 : 0;
                                this.i(82);
                                break;
                            }
                            this.j(var1_1);
                            break;
                        }
                        case 81: {
                            if (var1_1 == -7) {
                                this.cv = 1;
                                this.i(79);
                            } else if (var1_1 == -6 || var2_2 == 8) {
                                this.a(this.g(77), 10, 81, 0L);
                            }
                            if (var2_2 != 6 && var2_2 != 1 || this.O == 0) break;
                            this.f(var2_2);
                            break;
                        }
                        case 77: {
                            if (var1_1 == -7) {
                                this.i(this.c());
                                this.cv = 0;
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.l(52);
                                break;
                            }
                            this.b(var2_2, 6);
                            break;
                        }
                        case 42: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.bN.addElement(new Integer(this.Y));
                                if (this.cv == 0) {
                                    this.l(39);
                                    break;
                                }
                                if (this.cv == 1) {
                                    this.l(40);
                                    break;
                                }
                                if (this.cv == 2) {
                                    this.cv = 0;
                                    this.i(118);
                                    break;
                                }
                                if (this.cv == 3) {
                                    this.cv = 0;
                                    this.i(121);
                                    break;
                                }
                                if (this.cv == 4) {
                                    this.l(36);
                                    break;
                                }
                                if (this.cv != 5) break;
                                this.cv = 0;
                                this.i(122);
                                break;
                            }
                            if (var1_1 == -7) {
                                this.cv = 2;
                                this.i(this.c());
                                break;
                            }
                            this.b(var2_2, 6);
                            break;
                        }
                        case 110: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.cv == 0) {
                                    this.bN.addElement(new Integer(this.Y));
                                    this.i(111);
                                    break;
                                }
                                if (this.cv == 1) {
                                    this.cv = 0;
                                    this.aR = 0;
                                    this.bN.addElement(new Integer(this.Y));
                                    this.i(113);
                                    break;
                                }
                                if (this.cv != 2) break;
                                this.l(37);
                                break;
                            }
                            if (var1_1 == -7) {
                                this.l(38);
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 111: {
                            if (var1_1 == -7) {
                                this.cv = 0;
                                this.i(this.c());
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.a(this.bV[4 + this.cv], true, 16);
                                this.i(112);
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 113: {
                            if (var1_1 == -7) {
                                this.cv = 1;
                                this.i(this.c());
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.cv == 0) {
                                    this.ah = "Pick greeting:";
                                } else if (this.cv == 1) {
                                    this.ah = "Pick victory yell:";
                                } else if (this.cv == 2) {
                                    this.ah = "Pick loser cry:";
                                }
                                this.ak = "";
                                this.O = 10;
                                this.bt = new String[this.O][4];
                                this.aR = this.cv;
                                this.bi = 0;
                                for (var4_11 = 0; var4_11 < this.O; ++var4_11) {
                                    for (var5_19 = 0; var5_19 < 4; ++var5_19) {
                                        var6_23 = var4_11 + 149 + this.cv * 10;
                                        this.bt[var4_11][var5_19] = var5_19 == 0 ? Integer.toString(var6_23) : (var5_19 == 2 ? this.g(var6_23)[0] : "");
                                    }
                                }
                                this.bN.addElement(new Integer(this.Y));
                                this.i(114);
                                this.cv = 0;
                                break;
                            }
                            this.b(var2_2, 3);
                            break;
                        }
                        case 112: {
                            if (var1_1 == -6 || var1_1 == -5 || var1_1 == -1 || var1_1 == -2) {
                                this.bV[4 + this.cv] = this.n();
                                this.cv = var1_1 == -2 || var1_1 == -6 || var1_1 == -5 ? (this.cv + 1) % 3 : (this.cv + 2) % 3;
                                this.i(111);
                                break;
                            }
                            this.j(var1_1);
                            break;
                        }
                        case 118: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.aE = this.cv + 9;
                                this.bN.addElement(new Integer(this.Y));
                                this.l(41);
                                break;
                            }
                            if (var1_1 == -7) {
                                this.cv = 2;
                                this.i(this.c());
                                break;
                            }
                            this.b(var2_2, 4);
                            break;
                        }
                        case 119: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.aR = this.cv;
                                this.k = 0;
                                if (this.B == null) {
                                    this.B = new String[2];
                                }
                                this.B[0] = "View";
                                this.B[1] = "Delete";
                                this.k = 0;
                                this.i(120);
                                break;
                            }
                            if (var1_1 == -7) {
                                this.cv = this.aR;
                                this.i(this.c());
                                if (this.Y == 118) {
                                    this.cv = this.aE - 9;
                                    break;
                                }
                                if (this.Y != 121) break;
                                this.cv = this.aE - 13;
                                break;
                            }
                            this.f(var2_2);
                            break;
                        }
                        case 120: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.k == 0) {
                                    var4_12 = this.bt[this.aR][3];
                                    var5_20 = new String[com.watAgame.eoe_town.b.b(var4_12).length];
                                    System.arraycopy(com.watAgame.eoe_town.b.b(var4_12), 0, var5_20, 0, var5_20.length);
                                    this.a(var5_20, 0, 119, 0L);
                                    break;
                                }
                                this.l(42);
                                break;
                            }
                            if (var2_2 == 6 || var2_2 == 1) {
                                this.k = (this.k + 1) % 2;
                                break;
                            }
                            if (var1_1 != -7) break;
                            this.cv = this.aR;
                            this.i(119);
                            break;
                        }
                        case 121: {
                            if (var1_1 == -7) {
                                this.cv = 3;
                                this.i(this.c());
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.aE = this.cv + 13;
                                this.bN.addElement(new Integer(this.Y));
                                this.l(41);
                                break;
                            }
                            this.b(var2_2, 4);
                            break;
                        }
                        case 123: {
                            if (var1_1 == -7) {
                                this.cv = 0;
                                this.i(this.c());
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.l(44);
                                break;
                            }
                            if (var2_2 != 6 && var2_2 != 1 || this.O == 0) break;
                            this.f(var2_2);
                            break;
                        }
                        case 122: {
                            if (var1_1 == -7) {
                                this.i(this.c());
                                this.cv = 5;
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.aE = this.cv;
                                this.bN.addElement(new Integer(this.Y));
                                this.l(43);
                                break;
                            }
                            this.b(var2_2, 6);
                            break;
                        }
                        case 89: {
                            if (com.watAgame.eoe_town.b.c(var1_1)) {
                                this.a(this.g(38), 15, this.Y, 0L);
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.cv == 7) {
                                    this.k = 0;
                                    this.i(90);
                                    break;
                                }
                                if (this.bS > 10 || (var4_13 = (String[][])this.bv.elementAt(this.cv)).length == 0) break;
                                this.M = new int[var4_13.length];
                                if (var4_13.length <= 5) {
                                    this.bc = new String[var4_13.length][4];
                                    System.arraycopy(var4_13, 0, this.bc, 0, this.bc.length);
                                    this.cu = false;
                                } else {
                                    this.bc = new String[5][4];
                                    this.aV = new String[var4_13.length - 5][4];
                                    System.arraycopy(var4_13, 0, this.bc, 0, this.bc.length);
                                    this.cu = true;
                                    System.arraycopy(var4_13, 5, this.aV, 0, this.aV.length);
                                }
                                this.k = 0;
                                this.bO = 1;
                                this.i(91);
                                break;
                            }
                            if (var2_2 == 5 || var2_2 == 6 || var2_2 == 2 || var2_2 == 1) {
                                this.cv = var2_2 == 2 || var2_2 == 1 ? (this.cv + 7) % 8 : (this.cv + 1) % 8;
                                this.repaint(0, 53, 96, 11);
                                break;
                            }
                            if (var1_1 != -7 && var1_1 != -8 || this.bS == 0) break;
                            --this.bS;
                            this.bl[this.bS][0] = -1;
                            if (this.bl[this.bS][2] == 1) {
                                var4_14 = (String[])this.F.elementAt(this.F.size() - 1);
                                var5_21 = com.watAgame.eoe_town.b.d(var4_14[2]);
                                this.bL -= var5_21;
                                this.bf = this.bL;
                                this.W = this.ag = this.ch[this.bf];
                                this.aW -= this.bl[this.bS][1] / 10;
                            } else {
                                if (this.bl[this.bS][2] == 2) {
                                    --this.aS;
                                    this.ar[this.aS] = -1;
                                }
                                this.aW -= this.bl[this.bS][1] / 10;
                            }
                            this.F.removeElementAt(this.F.size() - 1);
                            this.bl[this.bS][1] = -1;
                            break;
                        }
                        case 91: {
                            if (var1_1 == -7 || var1_1 == -8) {
                                this.k = 0;
                                this.i(89);
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                if ((this.bO != 1 || this.M[this.k] != 1) && (this.bO != 2 || this.M[this.k + 5 - 1] != 1)) break;
                                this.bR = System.currentTimeMillis();
                                this.i = this.bO == 1 ? new String[]{Integer.toString((int)(this.bR - this.aA)), this.bc[this.k][0], ""} : new String[]{Integer.toString((int)(this.bR - this.aA)), this.aV[this.k][0], ""};
                                if (this.bO == 1) {
                                    this.bl[this.bS][1] = Integer.parseInt(this.bc[this.k][2]);
                                    this.bl[this.bS][2] = Integer.parseInt(this.bc[this.k][3]);
                                } else {
                                    this.bl[this.bS][1] = Integer.parseInt(this.aV[this.k][2]);
                                    this.bl[this.bS][2] = Integer.parseInt(this.aV[this.k][3]);
                                }
                                if (this.bO == 1 && this.bc[this.k][3].equals("2") || this.bO == 2 && this.aV[this.k][3].equals("2")) {
                                    this.W = this.ag;
                                    this.i(93);
                                    break;
                                }
                                if (this.bO == 1 && this.bc[this.k][3].equals("1") || this.bO == 2 && this.aV[this.k][3].equals("1")) {
                                    this.aT = new int[8];
                                    this.bg = 0;
                                    this.i(92);
                                    break;
                                }
                                this.bO = 1;
                                this.k = 0;
                                this.bl[this.bS][0] = this.cv;
                                this.F.addElement(this.i);
                                this.aW += this.bl[this.bS][1] / 10;
                                ++this.bS;
                                this.i(89);
                                break;
                            }
                            if (var2_2 == 6) {
                                if (this.bO == 1 && this.k >= this.bc.length - 1) {
                                    if (this.cu) {
                                        this.bO = 2;
                                    }
                                    this.k = 0;
                                    break;
                                }
                                if (this.bO == 2 && this.k >= this.aV.length - 1) {
                                    this.bO = 1;
                                    this.k = 0;
                                    break;
                                }
                                ++this.k;
                                break;
                            }
                            if (var2_2 != 1) break;
                            if (this.bO == 1 && this.k <= 0) {
                                if (this.cu) {
                                    this.bO = 2;
                                    this.k = this.aV.length - 1;
                                    break;
                                }
                                this.k = this.bc.length - 1;
                                break;
                            }
                            if (this.bO == 2 && this.k <= 0) {
                                this.bO = 1;
                                this.k = this.bc.length - 1;
                                break;
                            }
                            --this.k;
                            break;
                        }
                        case 93: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.A();
                                break;
                            }
                            if (var1_1 == -7 || var2_2 == -8) {
                                this.i(89);
                                break;
                            }
                            if (var2_2 == 1) {
                                this.aM = this.W >= 0 && this.W <= 5 ? this.W + 18 : this.W - 6;
                                this.W = this.aM;
                                break;
                            }
                            if (var2_2 == 5) {
                                this.aM = this.W % 6 == 5 ? this.W - 5 : this.W + 1;
                                this.W = this.aM;
                                break;
                            }
                            if (var2_2 == 6) {
                                this.aM = this.W >= 18 && this.W <= 23 ? this.W - 18 : this.W + 6;
                                this.W = this.aM;
                                break;
                            }
                            if (var2_2 != 2) break;
                            this.aM = this.W % 6 == 0 ? this.W + 5 : this.W - 1;
                            this.W = this.aM;
                            break;
                        }
                        case 92: {
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.d();
                                break;
                            }
                            if (var1_1 == -7 || var1_1 == -8) {
                                this.i(89);
                                this.ag = this.ch[this.bf];
                                for (var4_15 = this.bf + 1; var4_15 <= this.bL; ++var4_15) {
                                    this.ch[var4_15] = -1;
                                    --this.bL;
                                }
                                this.bU = false;
                                break;
                            }
                            if (var2_2 == 1) {
                                if (this.ag <= 5) break;
                                this.aM = this.ag - 6;
                                if (!this.a(this.aM)) break;
                                this.x();
                                break;
                            }
                            if (var2_2 == 5) {
                                if (this.ag % 6 == 5) break;
                                this.aM = this.ag + 1;
                                if (!this.a(this.aM)) break;
                                this.x();
                                break;
                            }
                            if (var2_2 == 6) {
                                if (this.ag >= 18) break;
                                this.aM = this.ag + 6;
                                if (!this.a(this.aM)) break;
                                this.x();
                                break;
                            }
                            if (var2_2 != 2 || this.ag % 6 == 0) break;
                            this.aM = this.ag - 1;
                            if (!this.a(this.aM)) break;
                            this.x();
                            break;
                        }
                        case 90: {
                            if (var1_1 == -7 || var1_1 == -8) {
                                this.i(89);
                                break;
                            }
                            if (var1_1 == -6 || var2_2 == 8) {
                                if (this.k == 0) {
                                    this.a(this.g(38), 15, 89, 0L);
                                    break;
                                }
                                if (this.k != 1) break;
                                this.a(this.g(39), 6, 89, 0L);
                                break;
                            }
                            if (var2_2 != 1 && var2_2 != 6) break;
                            this.k = (this.k + 1) % 2;
                            break;
                        }
                        case 103: {
                            if (Integer.parseInt(this.f[0]) <= 0) break;
                            if (var1_1 == -6 || var2_2 == 8) {
                                this.a(this.g(this.cv + 53), 10, 103, 0L);
                                break;
                            }
                            this.b(var2_2, 6);
                            break;
                        }
                        case 104: {
                            if (var1_1 == -6 || var2_2 == 8 || var1_1 == -7) {
                                if (this.cv == 5 || var1_1 == -7) {
                                    if (this.bY != null) {
                                        this.bY = "";
                                    }
                                    this.j();
                                    break;
                                }
                                if (this.cv == 4) {
                                    this.l(51);
                                    break;
                                }
                                this.bN.addElement(new Integer(104));
                                this.l(29);
                                break;
                            }
                            this.b(var2_2, 6);
                        }
                    }
                }
            }
            this.repaint();
            return;
        }
        catch (Throwable var2_3) {
            this.a("key", var2_3, false);
            return;
        }
    }

    private final void k(Graphics graphics) {
        boolean bl = false;
        graphics.setColor(7255290);
        graphics.fillRect(0, 0, 96, 65);
        graphics.setColor(0);
        graphics.setFont(as);
        int n = as.getHeight() + -1;
        int n2 = cn.getHeight() + -1;
        int n3 = (n << 1) + (n2 << 2);
        int n4 = 65 - n3 >> 1;
        graphics.drawString("\u00a9watAgame 2004", 48, n4, 17);
        n4 += n2;
        graphics.setFont(cn);
        graphics.drawString("All rights reserved.", 48, n4 += n2, 17);
        graphics.drawString("Era of Eidolon\u2122", 48, n4 += n2, 17);
        graphics.drawString("is a trademark", 48, n4 += n2, 17);
        graphics.drawString("of watAgame ApS.", 48, n4 + n2, 17);
    }

    private final void n(Graphics graphics) {
        if (this.aI == null) {
            this.aI = com.watAgame.eoe_town.b.a("wait", true);
        }
        com.watAgame.eoe_town.b.a(graphics, this.aI, 0, this.bF % 6 * 10, this.aI.getWidth(), 10, 0, 2, 0, 20);
    }

    static final Image a(String string, boolean bl) {
        for (int i = 5; i > 0; --i) {
            try {
                System.gc();
                Thread.sleep(200L);
                return Image.createImage((String)("/" + string + ".png"));
            }
            catch (Throwable throwable) {
                if (string.equals("unread")) {
                    return com.watAgame.eoe_town.b.a("mail", true);
                }
                if (!bl) continue;
                throwable.printStackTrace();
                continue;
            }
        }
        if (bl) {
            return Image.createImage((int)100, (int)1);
        }
        return null;
    }

    private final Image e(int n) {
        StringBuffer stringBuffer = new StringBuffer();
        for (int i = 0; i < n; ++i) {
            stringBuffer.append(this.o());
            stringBuffer.append('\u00a6');
        }
        String string = this.o();
        stringBuffer.append(string);
        byte[] byArray = stringBuffer.toString().getBytes();
        System.gc();
        return Image.createImage((byte[])byArray, (int)0, (int)byArray.length);
    }

    protected final void paint(Graphics graphics) {
        try {
            Graphics graphics2 = graphics;
            if (!this.isDoubleBuffered()) {
                if (this.az == null) {
                    this.aL = Image.createImage((int)96, (int)65);
                    this.az = this.aL.getGraphics();
                }
                graphics = this.az;
            }
            graphics.setClip(0, 0, this.getWidth(), this.getHeight());
            if (this.V == null || this.V.e != 12) {
                switch (this.Y) {
                    case 0: {
                        this.k(graphics);
                        break;
                    }
                    case 3: {
                        com.watAgame.eoe_town.b.a(graphics, com.watAgame.eoe_town.b.b("Your hero was#asleep, but says:#I will be ready#in two minutes."));
                        break;
                    }
                    case 4: {
                        if (this.cq == null) {
                            this.cq = com.watAgame.eoe_town.b.a("logo", true);
                        }
                        graphics.drawImage(this.cq, 0, 0, 20);
                        break;
                    }
                    case 7: {
                        this.b(graphics);
                        this.n(graphics);
                        break;
                    }
                    case 11: 
                    case 12: {
                        if ("01".equals("03")) {
                            this.a(graphics, "Enter Eidolon");
                            break;
                        }
                        this.e(graphics, "Enter Eidolon");
                        break;
                    }
                    case 14: {
                        this.a(graphics, "Your heroes:");
                        break;
                    }
                    case 30: {
                        this.a(graphics, "Create Hero:");
                        break;
                    }
                    case 15: {
                        this.a(graphics, "Your heroes:");
                        this.j(graphics);
                        break;
                    }
                    case 32: 
                    case 120: {
                        this.j(graphics);
                        break;
                    }
                    case 40: {
                        this.d(graphics);
                        break;
                    }
                    case 41: {
                        this.b(graphics, "Pick a fight:");
                        break;
                    }
                    case 46: 
                    case 47: 
                    case 52: 
                    case 58: 
                    case 72: 
                    case 74: 
                    case 76: 
                    case 78: 
                    case 81: 
                    case 86: 
                    case 87: 
                    case 106: 
                    case 114: 
                    case 115: 
                    case 116: 
                    case 117: 
                    case 119: 
                    case 123: {
                        this.a(graphics, this.ah, this.ak);
                        break;
                    }
                    case 54: {
                        this.a(graphics, "Pick a foe:");
                        break;
                    }
                    case 57: {
                        this.a(graphics, "Invite friend by:");
                        break;
                    }
                    case 48: {
                        this.b(graphics, "Tavern");
                        break;
                    }
                    case 70: {
                        this.e(graphics, "Manage");
                        break;
                    }
                    case 77: {
                        this.d(graphics, "View rankings:");
                        break;
                    }
                    case 75: {
                        this.a(graphics, this.x);
                        break;
                    }
                    case 79: {
                        this.a(graphics, "Chief's area:");
                        break;
                    }
                    case 82: {
                        this.a(graphics, this.at);
                        break;
                    }
                    case 118: {
                        this.e(graphics, "Hero skills:");
                        break;
                    }
                    case 43: {
                        this.e(graphics, "Buy skills:");
                        break;
                    }
                    case 85: {
                        this.a(graphics, "Choose class:");
                        break;
                    }
                    case 45: {
                        this.d(graphics, "Buy & sell:");
                        break;
                    }
                    case 44: {
                        this.e(graphics, "Buy magic:");
                        break;
                    }
                    case 42: {
                        this.d(graphics, "Hero overview:");
                        break;
                    }
                    case 111: {
                        this.a(graphics, "Write taunts:");
                        break;
                    }
                    case 110: {
                        this.a(graphics, "Customize:");
                        break;
                    }
                    case 113: {
                        this.a(graphics, "Pick mottos:");
                        break;
                    }
                    case 122: {
                        this.d(graphics, "Equip");
                        break;
                    }
                    case 18: 
                    case 95: {
                        this.n(graphics);
                        break;
                    }
                    case 89: 
                    case 92: 
                    case 93: {
                        this.h(graphics);
                        this.m(graphics);
                        break;
                    }
                    case 91: {
                        this.h(graphics);
                        this.l(graphics);
                        this.m(graphics);
                        break;
                    }
                    case 94: 
                    case 96: 
                    case 98: 
                    case 101: {
                        if (this.ct == null) break;
                        this.f(graphics);
                        break;
                    }
                    case 97: {
                        if (this.ce == null || this.ct == null) break;
                        boolean bl = false;
                        boolean bl2 = false;
                        int n = (int)(System.currentTimeMillis() - this.l);
                        int n2 = this.ce[0];
                        int n3 = this.ce[1];
                        int n4 = this.ce[4] * n >> 16;
                        int n5 = this.ce[5] * n >> 16;
                        if (Math.abs(n4) >= Math.abs(this.ce[2] - n2)) {
                            n2 = this.ce[2];
                            bl = true;
                        } else {
                            n2 += n4;
                        }
                        if (Math.abs(n5) >= Math.abs(this.ce[3] - n3)) {
                            n3 = this.ce[3];
                            bl2 = true;
                        } else {
                            n3 += n5;
                        }
                        this.N = bl && bl2;
                        int n6 = Integer.parseInt(this.ct[12]) * 10;
                        boolean bl3 = false;
                        this.i(graphics);
                        this.a(graphics, n6, 0, n2, n3);
                        break;
                    }
                    case 99: {
                        if (this.ct == null) break;
                        this.g(graphics);
                        break;
                    }
                    case 103: {
                        this.d(graphics, "Points left:".concat(this.f[0]));
                        break;
                    }
                    case 104: {
                        this.d(graphics, "Battle reports:");
                        break;
                    }
                    case 2: {
                        this.k(graphics);
                        break;
                    }
                    case 31: {
                        this.a(graphics, "Create Hero:");
                        break;
                    }
                    case 59: {
                        this.a(graphics, "Invite friend by:");
                        break;
                    }
                    case 60: {
                        this.a(graphics, "Invite friend by:");
                        break;
                    }
                    case 71: 
                    case 73: {
                        this.e(graphics, "Manage");
                        break;
                    }
                    case 80: {
                        this.a(graphics, "Chief's area:");
                        break;
                    }
                    case 83: {
                        this.a(graphics, this.at);
                        break;
                    }
                    case 84: {
                        this.a(graphics, this.at);
                        break;
                    }
                    case 112: {
                        this.a(graphics, "Write taunts:");
                        break;
                    }
                    case 121: {
                        this.e(graphics, "Hero spells:");
                        break;
                    }
                    case 90: {
                        this.m(graphics);
                        this.e(graphics);
                    }
                }
            }
            if (this.Y != 89 && this.Y != 92 && this.Y != 93 && this.Y != 91 && this.Y != 101 && this.Y != 97 && this.Y != 98 && this.Y != 96 && this.Y != 99 && this.Y != 94 && this.Y != 95 && this.Y != 18) {
                if (this.cc == 1 && (this.bF % 2 == 0 || System.currentTimeMillis() - this.aF > 6000L)) {
                    if (this.bu == null) {
                        this.bu = com.watAgame.eoe_town.b.a("challenge", true);
                    }
                    graphics.drawImage(this.bu, 37, 57, 20);
                }
                if (this.bZ == 1 && (this.bF % 2 == 0 || System.currentTimeMillis() - this.bX > 6000L)) {
                    if (this.bK == null) {
                        this.bK = com.watAgame.eoe_town.b.a("mail", true);
                    }
                    graphics.drawImage(this.bK, 51, 57, 20);
                }
            }
            if (this.s != null && this.s.isAlive()) {
                this.n(graphics);
            }
            if (this.V != null) {
                graphics.setFont(cm);
                this.V.a(graphics);
            }
            if (this.az != null) {
                graphics2.drawImage(this.aL, 0, 0, 20);
            }
            if (this.getHeight() > 65) {
                graphics2.setColor(0);
                graphics2.fillRect(0, 65, this.getWidth(), this.getHeight() - 65);
            }
            if (this.getWidth() > 96) {
                graphics2.setColor(0);
                graphics2.fillRect(96, 0, this.getWidth() - 96, 65);
            }
            this.p = false;
            return;
        }
        catch (Throwable throwable) {
            if (!this.p) {
                throwable.printStackTrace();
                this.repaint();
            }
            this.p = true;
            return;
        }
    }

    private final void b(Graphics graphics) {
        int n;
        if (this.cj < 0) {
            return;
        }
        if (this.cq == null) {
            this.cq = com.watAgame.eoe_town.b.a("logo", true);
        }
        graphics.drawImage(this.cq, 0, 0, 20);
        String[] stringArray = new String[]{"- Installing game -##Welcome to the#World of Eidolon.#You begin in#Orumant, a town", "- Installed 20% -##ruled by beautiful#Queen Sorena#youngest of#three sisters.", "- Installed 40% -##A war threatens#peace in Eidolon#and the Queens#have ordered all", "- Installed 60% -##heroes to go and#fight in the arena#to prepare for the#coming battle.", "- Installed 80% -##You have mail#waiting for you in#the TAVERN inbox.#Go and check it."};
        Font font = cn;
        graphics.setFont(font);
        int n2 = font.getHeight();
        n2 += n2 >> 2;
        String[] stringArray2 = com.watAgame.eoe_town.b.b(stringArray[this.cj % 5]);
        int n3 = 84;
        for (n = 0; n < stringArray2.length; ++n) {
            n3 = Math.max(n3, font.stringWidth(stringArray2[n]) + 5);
        }
        n = n2 * (stringArray.length + 1) + 5;
        graphics.setColor(0xFFFFAA);
        graphics.fillRect(96 - n3 >> 1, 65 - n >> 1, n3, n);
        graphics.setColor(0);
        graphics.drawRect(96 - n3 >> 1, 65 - n >> 1, n3, n);
        for (int i = 0; i < stringArray2.length; ++i) {
            graphics.drawString(stringArray2[i], 48, (65 - n >> 1) + i * n2 + 3, 17);
        }
    }

    private final void g() {
        if (this.bJ != null) {
            this.n = null;
            this.aP = null;
            this.bk = null;
            this.aB = null;
            this.J = null;
            this.bJ = null;
            System.gc();
            try {
                Thread.sleep(500L);
                return;
            }
            catch (InterruptedException interruptedException) {}
        }
    }

    private final void c(Graphics graphics) {
        this.g();
        if (this.v == null) {
            this.v = com.watAgame.eoe_town.b.a("background", true);
        }
        graphics.drawImage(this.v, 0, 0, 20);
        com.watAgame.eoe_town.b.a(graphics, this.v, 0, 0, this.v.getWidth(), this.v.getHeight(), 2, this.v.getWidth(), 0, 20);
    }

    private final void c(Graphics graphics, String string) {
        graphics.setColor(0);
        graphics.setFont(bP);
        graphics.drawString("" + string, 48, 8 - (bP.getHeight() >> 1), 17);
    }

    private final void d(Graphics graphics, String string) {
        int n;
        String[] stringArray = null;
        if (string == "Hero overview:") {
            stringArray = new String[]{"Stats", "Weapons", "Skills", "Spells", "Custom", "Equip"};
        } else if (string == "Battle reports:") {
            stringArray = new String[]{"Stats", "Weapons", "Skills", "Spells", "+Friend", "Town"};
        } else if (string == "Equip") {
            stringArray = new String[]{"Melee", "Trap", "Bow", "Bombs", "Armour", "Magic"};
        } else if (string == "Buy & sell:") {
            stringArray = new String[]{"Melee", "Bow", "Bombs", "Trap", "Armour", "Sell"};
        } else if (string == "View rankings:") {
            stringArray = com.watAgame.eoe_town.b.b("Respect#Level#Clan#Contest#Hotshot#Friends");
        } else if (string != null && string.equals("Points left:".concat(this.f[0]))) {
            stringArray = new String[6];
            System.arraycopy(this.f, 1, stringArray, 0, 6);
            this.ba = new int[6];
            String[] stringArray2 = com.watAgame.eoe_town.b.b("St:#In:#Dx:#To:#Wi:#Sp:");
            for (int i = 0; i < 6; ++i) {
                int n2 = Integer.parseInt(stringArray[i]);
                if (n2 >= 15 && n2 <= 45) {
                    this.ba[i] = 3;
                } else if (n2 >= 48 && n2 <= 76) {
                    this.ba[i] = 2;
                } else if (n2 >= 78 && n2 <= 98) {
                    this.ba[i] = 1;
                }
                stringArray[i] = stringArray2[i] + stringArray[i] + "(" + Integer.toString(this.ba[i]) + ")";
            }
        }
        this.c(graphics);
        if (this.U == null) {
            this.U = com.watAgame.eoe_town.b.a("divider", true);
        }
        for (n = 0; n < 3; ++n) {
            graphics.drawImage(this.U, 48, aX[n], 17);
        }
        this.c(graphics, string);
        graphics.setFont(cm);
        if (stringArray == null) {
            return;
        }
        n = stringArray.length;
        while (--n >= 0) {
            graphics.setColor(n == this.cv ? 0xFF0000 : 0);
            if (n < 3) {
                graphics.drawString(stringArray[n], 27, aX[n] + 5 - ci, 17);
                continue;
            }
            graphics.drawString(stringArray[n], 69, aX[n - 3] + 5 - ci, 17);
        }
    }

    private final void e(Graphics graphics, String string) {
        String[] stringArray = null;
        if (string == "Buy magic:" || string == "Hero spells:") {
            stringArray = com.watAgame.eoe_town.b.b("Spectral#Guardian#Bane#Spirit");
        } else if (string == "Enter Eidolon") {
            stringArray = this.bE.length() > 0 && this.ao.length() > 0 ? new String[]{this.bE, this.ao, "Login", "Register"} : (this.bE.length() > 0 ? new String[]{this.bE, ">Password", "Login", "Register"} : (this.ao.length() > 0 ? new String[]{">Nickname", this.ao, "Login", "Register"} : new String[]{">Nickname", ">Password", "Login", "Register"}));
        } else if (string == "Buy skills:" || string == "Hero skills:") {
            stringArray = com.watAgame.eoe_town.b.b("Close combat#Ranged attack#Defence#Move");
        } else if (string == "Manage") {
            stringArray = this.A.length() > 0 && this.cv == 0 ? new String[]{this.A, ">Ban a hero", "Add a friend", "-Ban"} : (this.A.length() > 0 && this.cv == 1 ? new String[]{">Add a friend", this.A, "-Friend", "-Ban"} : new String[]{">Add a friend", ">Ban a hero", "-Friend", "-Ban"});
        }
        this.c(graphics);
        if (this.U == null) {
            this.U = com.watAgame.eoe_town.b.a("divider", true);
        }
        graphics.drawImage(this.U, 48, aX[2], 17);
        this.c(graphics, string);
        graphics.setFont(cm);
        if (stringArray == null) {
            return;
        }
        int n = stringArray.length;
        while (--n >= 0) {
            graphics.setColor(n == this.cv ? 0xFF0000 : 0);
            if (n == 0 && (this.Y == 71 || this.Y == 12 && this.cv == 0)) {
                this.a(graphics, 0);
                continue;
            }
            if (n == 1 && (this.Y == 73 || this.Y == 12 && this.cv == 1)) {
                this.a(graphics, 1);
                continue;
            }
            if (n < 2) {
                graphics.drawString(stringArray[n], 48, aX[n] + 5 - ci, 17);
                continue;
            }
            if (n == 2) {
                graphics.drawString(stringArray[n], 27, aX[n] + 5 - ci, 17);
                continue;
            }
            if (n != 3) continue;
            graphics.drawString(stringArray[n], 69, aX[2] + 5 - ci, 17);
        }
    }

    private final void b(Graphics graphics, String string) {
        String[] stringArray = null;
        if (string == "Pick a fight:") {
            stringArray = new String[]{"Get random foe", "Friend", "Gladiator", "Special", "Invite"};
        } else if (string == "Tavern") {
            stringArray = com.watAgame.eoe_town.b.b("Inbox#Write#Friends#My clan#Ranking");
        }
        this.c(graphics);
        if (this.U == null) {
            this.U = com.watAgame.eoe_town.b.a("divider", true);
        }
        graphics.drawImage(this.U, 48, aX[1], 17);
        graphics.drawImage(this.U, 48, aX[2], 17);
        this.c(graphics, string);
        graphics.setFont(cm);
        if (stringArray == null) {
            return;
        }
        int n = stringArray.length;
        while (--n >= 0) {
            graphics.setColor(n == this.cv ? 0xFF0000 : 0);
            if (n == 0) {
                graphics.drawString(stringArray[n], 48, aX[n] + 5 - ci, 17);
                continue;
            }
            if (n == 1 || n == 2) {
                graphics.drawString(stringArray[n], 27, aX[n] + 5 - ci, 17);
                continue;
            }
            graphics.drawString(stringArray[n], 69, aX[n - 2] + 5 - ci, 17);
        }
    }

    private final void a(Graphics graphics, String string) {
        String[] stringArray = null;
        if (string == "Create Hero:") {
            stringArray = this.ca.length() != 0 && this.bQ != '\u0000' ? new String[]{this.ca, this.bQ == 'f' ? "Female" : "Male", "Create"} : (this.ca.length() != 0 ? new String[]{this.ca, "Gender", "Create"} : (this.bQ != '\u0000' ? new String[]{"Hero name?", this.bQ == 'f' ? "Female" : "Male", "Create"} : new String[]{"Hero name?", "Gender", "Create"}));
        } else if (string == "Enter Eidolon") {
            stringArray = this.bE.length() > 0 && this.ao.length() > 0 ? new String[]{this.bE, this.ao, "Login"} : (this.bE.length() > 0 ? new String[]{this.bE, ">Password", "Login"} : (this.ao.length() > 0 ? new String[]{">Nickname", this.ao, "Login"} : new String[]{">Nickname", ">Password", "Login"}));
        } else if (string == "Your heroes:") {
            stringArray = this.K[0].length() > 0 && this.K[1].length() > 0 ? new String[]{this.K[0], this.K[1], "Delete Hero"} : (this.K[0].length() > 0 ? new String[]{this.K[0], "Create Hero", "Delete Hero"} : (this.K[1].length() > 0 ? new String[]{"Create Hero", this.K[1], "Delete Hero"} : new String[]{"Create Hero", "Create Hero", "Delete Hero"}));
        } else if (string == "Pick a foe:" && this.aY != null) {
            stringArray = new String[this.aY.length];
            int n = stringArray.length;
            while (--n >= 0) {
                stringArray[n] = this.aY[n][2];
            }
        } else if (string == "Customize:") {
            stringArray = new String[]{"Taunts", "Mottos", "Head: " + this.bV[3]};
        } else if (string == "Write taunts:") {
            stringArray = new String[]{this.bV[4], this.bV[5], this.bV[6]};
        } else if (string == "Pick mottos:") {
            stringArray = new String[]{"Greeting", "Victory yell", "Loser cry"};
        } else if (string == "Invite friend by:") {
            String string2 = "";
            if (this.aZ.length() > 0) {
                string2 = this.aZ.length() > 12 ? this.aZ.substring(0, 12) : this.aZ;
            }
            stringArray = this.aH.length() > 0 && this.aZ.length() > 0 ? new String[]{this.aH, string2, "Send invitation"} : (this.aH.length() > 0 ? new String[]{this.aH, ">or email", "Send invitation"} : (this.aZ.length() > 0 ? new String[]{">phone no.", string2, "Send invitation"} : new String[]{">phone no.", ">or email", "Send invitation"}));
        } else if (string == "Choose class:") {
            stringArray = new String[]{"Sword", "Hammer", "Axe"};
        } else if (this.x != null && string != null && string.equals(this.x)) {
            stringArray = new String[]{"Clan stats", "Clan members", this.bT};
        } else if (string == "Chief's area:") {
            stringArray = this.bA == null || this.bA.length() == 0 ? new String[]{">Invite hero", "Kick hero", "Edit clan"} : new String[]{this.bA, "Kick hero", "Edit clan"};
        } else if (this.at != null && string != null && string.equals(this.at)) {
            stringArray = new String[]{this.T, this.bn, "Update"};
        }
        this.c(graphics);
        this.c(graphics, string);
        graphics.setFont(cm);
        if (stringArray == null) {
            return;
        }
        for (int i = 0; i < stringArray.length; ++i) {
            graphics.setColor(i == this.cv ? 0xFF0000 : 0);
            if (i == 0 && this.cv == 0 && (this.Y == 31 || this.Y == 112 || this.Y == 59 || this.Y == 83 || this.Y == 80 || this.Y == 12)) {
                this.a(graphics, 0);
                continue;
            }
            if (i == 1 && this.cv == 1 && (this.Y == 112 || this.Y == 84 || this.Y == 12)) {
                this.a(graphics, 1);
                continue;
            }
            if (i == 1 && this.cv == 1 && this.Y == 60) {
                int n = this.aj.length();
                if (n > 11) {
                    StringBuffer stringBuffer = new StringBuffer(this.aj.toString());
                    for (int j = 0; j < n - 11; ++j) {
                        this.aj.deleteCharAt(0);
                    }
                    this.a(graphics, 1);
                    this.aj = stringBuffer;
                    continue;
                }
                this.a(graphics, 1);
                continue;
            }
            if (i == 2 && this.cv == 2 && this.Y == 112) {
                this.a(graphics, 2);
                continue;
            }
            graphics.drawString(stringArray[i], 48, aX[i] + 5 - ci, 17);
        }
    }

    private final void a(Graphics graphics) {
        int n = 36 * this.aG / this.ae;
        if (n > 36) {
            n = 36;
        }
        graphics.setColor(5327691);
        graphics.fillRect(47 - n, 1, n, 6);
    }

    private final void m(Graphics graphics) {
        int n = 36 * this.aW / 72;
        graphics.setColor(8825809);
        graphics.fillRect(95 - n, 1, n, 3);
    }

    private final void b(Graphics graphics, int n) {
        int n2 = 36 * n / 720;
        graphics.setColor(2219775);
        graphics.fillRect(59, 4, 36, 3);
        graphics.setColor(15964948);
        graphics.fillRect(59, 4, n2, 3);
    }

    private final void h(Graphics graphics) {
        int n;
        if (this.bJ == null) {
            this.bJ = com.watAgame.eoe_town.b.a("battlefield", true);
        }
        graphics.drawImage(this.bJ, 0, 0, 20);
        this.a(graphics);
        this.m(graphics);
        if (this.bl == null) {
            return;
        }
        if (this.Y == 92) {
            this.b(graphics, this.bl[this.bS][1] * this.bg);
        } else if (this.Y == 93) {
            this.b(graphics, this.bl[this.bS][1]);
        }
        int n2 = 0;
        for (n = 0; n < this.bl.length; ++n) {
            if (this.bl[n][0] == -1) continue;
            com.watAgame.eoe_town.b.a(graphics, this.bJ, 2 + this.bl[n][0] * 12, 55, 9, 9, 0, n2, 9, 20);
            n2 += 9;
        }
        graphics.setColor(51200);
        for (n = 1; n <= this.bL; ++n) {
            if (this.ch[n] == -1) continue;
            graphics.fillRect(h[this.ch[n]][0] + 3, h[this.ch[n]][1] + 16, 6, 4);
        }
        graphics.setColor(0);
        for (n = 0; n < this.aS; ++n) {
            graphics.fillRect(h[this.ar[n]][0] + 3, h[this.ar[n]][1] + 16, 6, 4);
        }
        if (this.Y == 92 || this.Y == 93) {
            if (this.Y == 92) {
                graphics.setColor(51200);
                graphics.fillRect(h[this.ch[0]][0] + 3, h[this.ch[0]][1] + 16, 6, 4);
            } else {
                graphics.setColor(51200);
                graphics.drawRect(h[this.ag][0] + 3, h[this.ag][1] + 16, 6, 4);
                graphics.setColor(0);
                graphics.fillRect(h[this.W][0] + 3, h[this.W][1] + 16, 6, 4);
            }
            graphics.setColor(0xC80000);
            graphics.drawRect(h[this.ad][0] + 3, h[this.ad][1] + 16, 6, 4);
        } else {
            graphics.setColor(51200);
            graphics.fillRect(h[this.aK][0] + 3, h[this.aK][1] + 16, 6, 4);
        }
        if (this.Y == 92 || this.Y == 93) {
            n = this.cg.length;
            while (--n >= 0) {
                this.a(graphics, this.cg[n][1] - 1, h[this.cg[n][0]][0], h[this.cg[n][0]][1]);
            }
        } else {
            for (n = 0; n <= 18; n += 6) {
                this.a(graphics, n, n + 5);
            }
        }
        graphics.setColor(0xFF0000);
        graphics.drawRect(1 + 12 * this.cv, 53, 10, 11);
    }

    private final void f(Graphics graphics) {
        if (this.bJ == null) {
            this.bJ = com.watAgame.eoe_town.b.a("battlefield", true);
        }
        graphics.drawImage(this.bJ, 0, 0, 20);
        this.a(graphics);
        for (int i = 0; i <= 18; i += 6) {
            this.a(graphics, i, i + 5);
        }
        if (this.ct[8].length() > 0) {
            graphics.setFont(R);
            com.watAgame.eoe_town.b.a(graphics, this.ct[9].equals("0") ? 65344 : 0xFF3030, this.ct[8]);
            return;
        }
        com.watAgame.eoe_town.b.a(graphics, 5327691, "");
    }

    private final void i(Graphics graphics) {
        if (this.bJ == null) {
            this.bJ = com.watAgame.eoe_town.b.a("battlefield", true);
        }
        graphics.drawImage(this.bJ, 0, 0, 20);
        this.a(graphics);
        com.watAgame.eoe_town.b.a(graphics, 5327691, "");
        for (int i = 0; i <= 18; i += 6) {
            this.a(graphics, i, i + 5);
        }
    }

    private static final void a(Graphics graphics, int n, String string) {
        graphics.setColor(n);
        graphics.fillRect(0, 53, 96, 12);
        graphics.setColor(0);
        graphics.drawString(string, 1, 58 - ci, 20);
    }

    private final void g(Graphics graphics) {
        if (this.ct[7].length() > 0) {
            int n = Integer.parseInt(this.ct[7]);
            boolean bl = this.ct[9].equals("0") && n >= 141 || this.ct[9].equals("1") && n < 141;
            graphics.setFont(R);
            String string = this.g(n)[0];
            if (n == 141 || n == 142 || n == 143 || n == 144) {
                string = string + "  " + this.ct[6];
                this.a(graphics);
            }
            com.watAgame.eoe_town.b.a(graphics, bl ? 65344 : 0xFF3030, string);
        }
    }

    private final void a(Graphics graphics, int n, int n2, int n3, int n4) {
        if (this.aP == null) {
            this.aP = com.watAgame.eoe_town.b.a("ammu", true);
        }
        com.watAgame.eoe_town.b.a(graphics, this.aP, n, n2, 10, this.aP.getHeight(), 0, n3 + 1, n4 + 3, 20);
    }

    private final void a(Graphics graphics, int n, int n2, int n3) {
        if (this.n == null) {
            this.n = com.watAgame.eoe_town.b.a("obstacle", true);
        }
        com.watAgame.eoe_town.b.a(graphics, this.n, n * 12, 0, 12, this.n.getHeight(), 0, n2 + 1, n3 + 0, 20);
    }

    private final void a(Graphics graphics, int[][] nArray, boolean bl) {
        int n = nArray[0][4];
        if (this.J == null) {
            this.J = com.watAgame.eoe_town.b.a("torso", true);
        }
        int n2 = -nArray[1][0];
        int n3 = -nArray[1][1];
        while (n2 + 16 > this.J.getWidth()) {
            n2 -= this.J.getWidth();
            n3 += 14;
        }
        com.watAgame.eoe_town.b.a(graphics, this.J, n2, n3, 16, 14, n, nArray[1][2], nArray[1][3], 20);
        if (!this.H && this.aB == null) {
            this.aB = com.watAgame.eoe_town.b.a("legs", false);
            if (this.aB == null) {
                this.H = true;
            }
        }
        if (this.aB != null) {
            com.watAgame.eoe_town.b.a(graphics, this.aB, -nArray[2][0], -nArray[2][1], 12, this.aB.getHeight(), n, nArray[2][2], nArray[2][3], 20);
        }
        if (this.Y == 94 || this.Y == 96 || this.Y == 97 || this.Y == 98 || this.Y == 99) {
            if (this.bk == null) {
                this.bk = com.watAgame.eoe_town.b.a("weapons", true);
            }
            com.watAgame.eoe_town.b.a(graphics, this.bk, -nArray[3][0], -nArray[3][1], 13, this.bk.getHeight(), n, nArray[3][2], nArray[3][3], 20);
        }
        if (bl) {
            if (this.m != null) {
                com.watAgame.eoe_town.b.a(graphics, this.m, -nArray[0][0], -nArray[0][1], 7, this.m.getHeight(), n, nArray[0][2], nArray[0][3], 20);
                return;
            }
        } else if (this.al != null) {
            com.watAgame.eoe_town.b.a(graphics, this.al, -nArray[0][0], -nArray[0][1], 7, this.al.getHeight(), n, nArray[0][2], nArray[0][3], 20);
        }
    }

    private final void a(Graphics graphics, int n, int n2) {
        for (int i = n; i <= n2; ++i) {
            if (i == this.aK) {
                this.a(graphics, this.aD, true);
                continue;
            }
            if (i == this.ad) {
                this.a(graphics, this.a, false);
                continue;
            }
            int n3 = this.cg.length;
            while (--n3 >= 0) {
                if (i != this.cg[n3][0]) continue;
                this.a(graphics, this.cg[n3][1] - 1, h[this.cg[n3][0]][0], h[this.cg[n3][0]][1]);
            }
        }
    }

    private static final void a(Graphics graphics, String[] stringArray) {
        int n;
        Font font = cm;
        graphics.setFont(font);
        int n2 = font.getHeight() + 1;
        int n3 = 84;
        for (n = 0; n < stringArray.length; ++n) {
            n3 = Math.max(n3, font.stringWidth(stringArray[n]) + 5);
        }
        n = n2 * stringArray.length + 5;
        graphics.setColor(0xFFFFAA);
        graphics.fillRect(96 - n3 >> 1, 65 - n >> 1, n3, n);
        graphics.setColor(0);
        graphics.drawRect(96 - n3 >> 1, 65 - n >> 1, n3, n);
        for (int i = 0; i < stringArray.length; ++i) {
            graphics.drawString(stringArray[i], 48, (65 - n >> 1) + i * n2 + 3, 17);
        }
    }

    private final void j(Graphics graphics) {
        int n;
        for (n = 0; n < this.B.length; ++n) {
            if (n == this.k) {
                graphics.setColor(0xFFFFFF);
            } else {
                graphics.setColor(0xFFFFAA);
            }
            graphics.fillRect(4, 1 + n * 11, 86, 11);
        }
        graphics.setFont(cm);
        for (n = 0; n < this.B.length; ++n) {
            graphics.setColor(n == this.k ? 0xFF0000 : 0);
            graphics.drawString(n == this.k ? '>' + this.B[n] + '<' : this.B[n], 6, 1 + n * 11 + 0, 20);
        }
        graphics.setColor(0);
        graphics.drawRect(3, 0, 87, this.B.length * 11 + 1);
    }

    private final void e(Graphics graphics) {
        String[] stringArray = com.watAgame.eoe_town.b.b("End turn#Flee fight");
        graphics.setFont(cm);
        graphics.setColor(0xFFFFAA);
        graphics.fillRect(4, 8, 86, 22);
        for (int i = 0; i < stringArray.length; ++i) {
            if (i == this.k) {
                graphics.setColor(0xFFFFFF);
                graphics.fillRect(4, 8 + i * 11, 86, 11);
                graphics.setColor(0xFF0000);
            } else {
                graphics.setColor(0);
            }
            graphics.drawString(i == this.k ? '>' + stringArray[i] + '<' : stringArray[i], 6, 8 + i * 11 + 0, 20);
        }
        graphics.setColor(0);
        graphics.drawRect(3, 7, 87, 23);
    }

    private final void l(Graphics graphics) {
        String[][] stringArray = null;
        stringArray = this.bO == 1 ? this.bc : this.aV;
        this.m(graphics);
        graphics.setFont(cm);
        graphics.setColor(0xFFFFAA);
        graphics.fillRect(4, 8, 86, stringArray.length * 11);
        graphics.setColor(0xFFFFFF);
        graphics.fillRect(4, 8 + this.k * 11, 86, 11);
        for (int i = 0; i < stringArray.length; ++i) {
            this.b(graphics, Integer.parseInt(stringArray[this.k][2]));
            if (72000 - this.aW * 1000 > Integer.parseInt(stringArray[i][2]) * 100) {
                graphics.setColor(i == this.k ? 0xFF0000 : 0);
                if (this.bO == 1) {
                    this.M[i] = 1;
                } else {
                    this.M[i + 5 - 1] = 1;
                }
            } else {
                graphics.setColor(0xAFAFAF);
                if (this.bO == 1) {
                    this.M[i] = 0;
                } else {
                    this.M[i + 5 - 1] = 0;
                }
            }
            graphics.drawString(i == this.k ? '>' + stringArray[i][1] + '<' : stringArray[i][1], 6, 8 + i * 11 + 0, 20);
        }
        graphics.setColor(0);
        if (this.bO == 1 && this.cu) {
            graphics.drawChar('V', 82, 53, 20);
        } else if (this.bO == 2) {
            graphics.drawChar('\u039b', 82, 10, 20);
        }
        graphics.drawRect(3, 7, 87, stringArray.length * 11 + 1);
    }

    private final void d(Graphics graphics) {
        this.g();
        if (this.L == null) {
            this.L = com.watAgame.eoe_town.b.a("town", true);
        }
        if (this.aq == null) {
            this.aq = com.watAgame.eoe_town.b.a("cursor", true);
        }
        graphics.drawImage(this.L, 0, 0, 20);
        graphics.drawImage(this.aq, bM[this.cv][0], bM[this.cv][1] + 3 * (this.bF % 3), 20);
        if (this.aa < 10) {
            boolean bl = false;
            int n = R.stringWidth(aN[this.cv]) + 8;
            graphics.setColor(0xFFFFFF);
            int n2 = R.getHeight();
            graphics.fillRect(48 - (n >> 1), 2, n, n2 + 4);
            graphics.setColor(0);
            graphics.drawRect(48 - (n >> 1), 2, n - 1, n2 + 3);
            graphics.setFont(R);
            graphics.drawString(aN[this.cv], 48, 4, 17);
        }
    }

    final void a(String string, boolean bl, int n) {
        this.S = bl;
        this.D = n;
        this.aj = null;
        this.aj = new StringBuffer(string);
        this.bw = false;
        this.aQ = 0;
    }

    final String n() {
        if (this.aj != null) {
            if (this.bD > '\u0000') {
                this.aj.append(this.bD);
                this.bD = '\u0000';
            }
            if (this.S && this.aj.length() > 0) {
                this.aj.setCharAt(0, Character.toUpperCase(this.aj.charAt(0)));
            }
            return this.aj.toString();
        }
        return "";
    }

    final void t() {
        boolean bl = this.bw = !this.bw;
        if (this.aQ > 0) {
            --this.aQ;
        }
    }

    final void j(int n) {
        if (n == -7 || n == -8) {
            if (this.bD > '\u0000') {
                this.bD = '\u0000';
                return;
            }
            if (this.aj.length() > 0) {
                this.aj.deleteCharAt(this.aj.length() - 1);
                return;
            }
        } else if (this.aj.length() < this.D || this.aj.length() <= this.D && this.aQ > 0 && n == this.bm) {
            String string = "";
            if (n == 42) {
                string = "@%&/()=+*";
            } else if (n >= 48 && n <= 57) {
                string = bq[n - 48];
            }
            try {
                int n2;
                if (n == this.bm && this.aQ > 0) {
                    n2 = string.indexOf(this.bD) + 1;
                    if (n2 > string.length() - 1) {
                        n2 = 0;
                    }
                } else {
                    if (this.bD > '\u0000') {
                        this.aj.append(this.bD);
                        this.bD = '\u0000';
                    }
                    n2 = 0;
                }
                this.bD = string.length() > 0 && this.aj.length() < this.D ? string.charAt(n2) : (char)'\u0000';
            }
            catch (IndexOutOfBoundsException indexOutOfBoundsException) {
                this.bD = '\u0000';
            }
            this.bm = n;
            this.aQ = 2;
        }
    }

    final void a(Graphics graphics, int n) {
        Font font = graphics.getFont();
        String string = this.aj == null ? "" : this.aj.toString();
        if (this.bD > '\u0000') {
            string = string + this.bD;
        }
        if (this.S && string.length() > 0) {
            string = Character.toUpperCase(string.charAt(0)) + string.substring(1);
        }
        int n2 = font.stringWidth(string);
        graphics.setColor(0);
        graphics.setStrokeStyle(0);
        if (this.bw && this.aQ == 0) {
            graphics.drawLine(10 + n2, aX[n] + 5 - 6, 10 + n2, aX[n] + 5 + 6);
        }
        graphics.drawString(string, 10, aX[n] + 5 - ci, 20);
    }

    private final void l(int n) {
        this.s = null;
        this.q = true;
        StringBuffer stringBuffer = new StringBuffer(this.P);
        StringBuffer stringBuffer2 = new StringBuffer();
        switch (n) {
            case 30: 
            case 31: 
            case 32: {
                stringBuffer.append("pmessages.pl");
                stringBuffer2.append("\u00a6idx=");
                stringBuffer2.append(n - 30 + 1);
                stringBuffer2.append("\u00a6langcode=");
                stringBuffer2.append("01");
                break;
            }
            case 33: {
                stringBuffer.append("panimscripts.pl");
                stringBuffer2.append("\u00a6model=");
                stringBuffer2.append("01");
                break;
            }
            case 12: {
                stringBuffer.append("betaentry.pl");
                break;
            }
            case 34: {
                stringBuffer.append("version.pl");
                stringBuffer2.append("\u00a6client=");
                stringBuffer2.append("01010502");
                stringBuffer2.append("\u00a6build=");
                stringBuffer2.append("5.2.8");
                stringBuffer2.append("\u00a6model=");
                stringBuffer2.append("no30");
                break;
            }
            case 2: {
                stringBuffer.append("login.pl");
                stringBuffer2.append("\u00a6key=");
                stringBuffer2.append(this.j);
                stringBuffer2.append("\u00a6productid=");
                stringBuffer2.append("01010101");
                stringBuffer2.append("\u00a6build=");
                stringBuffer2.append("5.2.8");
                stringBuffer2.append("\u00a6model=");
                stringBuffer2.append("no30");
                break;
            }
            case 4: {
                stringBuffer.append("register.pl");
                stringBuffer2.append("\u00a6nickname=");
                stringBuffer2.append(this.bE);
                stringBuffer2.append("\u00a6reqpass=");
                stringBuffer2.append(this.ao);
                stringBuffer2.append("\u00a6productid=");
                stringBuffer2.append("01010101");
                stringBuffer2.append("\u00a6build=");
                stringBuffer2.append("5.2.8");
                stringBuffer2.append("\u00a6model=");
                stringBuffer2.append("no30");
                break;
            }
            case 3: {
                stringBuffer.append("login.pl");
                stringBuffer2.append("\u00a6login=");
                stringBuffer2.append(this.bE);
                stringBuffer2.append("\u00a6pass=");
                stringBuffer2.append(this.ao);
                stringBuffer2.append("\u00a6productid=");
                stringBuffer2.append("01010101");
                stringBuffer2.append("\u00a6build=");
                stringBuffer2.append("5.2.8");
                stringBuffer2.append("\u00a6model=");
                stringBuffer2.append("no30");
                break;
            }
            case 5: {
                stringBuffer.append("pay.pl");
                stringBuffer2.append("\u00a6amount=");
                stringBuffer2.append(this.o());
                break;
            }
            case 7: {
                stringBuffer.append("charselectcreate.pl");
                stringBuffer2.append("\u00a6charname=");
                stringBuffer2.append(this.ca);
                stringBuffer2.append("\u00a6gender=");
                stringBuffer2.append(this.bQ);
                break;
            }
            case 6: {
                stringBuffer.append("charselectchoose.pl");
                stringBuffer2.append("\u00a6charname=");
                stringBuffer2.append(this.K[this.cv]);
                break;
            }
            case 8: {
                stringBuffer.append("charselectdelete.pl");
                stringBuffer2.append("\u00a6charname=");
                stringBuffer2.append(this.B[this.k]);
                break;
            }
            case 46: {
                stringBuffer.append("friendlist.pl");
                break;
            }
            case 9: {
                stringBuffer.append("arenachflist.pl");
                break;
            }
            case 10: {
                stringBuffer.append("arenachran.pl");
                break;
            }
            case 11: {
                stringBuffer.append("invite.pl");
                stringBuffer2.append("\u00a6phoneno=");
                stringBuffer2.append(this.aH);
                stringBuffer2.append("\u00a6email=");
                stringBuffer2.append(this.aZ);
                break;
            }
            case 55: {
                stringBuffer.append("arenachtlist.pl");
                break;
            }
            case 56: {
                stringBuffer.append("arenachslist.pl");
                break;
            }
            case 51: {
                stringBuffer.append("friendadd.pl");
                stringBuffer2.append("\u00a6name=");
                stringBuffer2.append(this.bY);
                break;
            }
            case 45: {
                stringBuffer.append("friendadd.pl");
                stringBuffer2.append("\u00a6name=");
                stringBuffer2.append(this.A);
                break;
            }
            case 13: {
                stringBuffer.append("inbox.pl");
                break;
            }
            case 14: {
                stringBuffer.append("readmail.pl");
                stringBuffer2.append("\u00a6mailid=");
                stringBuffer2.append(this.ai);
                break;
            }
            case 17: {
                stringBuffer.append("deletemail.pl");
                stringBuffer2.append("\u00a6mailid=");
                stringBuffer2.append(this.ai);
                break;
            }
            case 15: {
                stringBuffer.append("mailflist.pl");
                break;
            }
            case 18: {
                stringBuffer.append("sendmail.pl");
                stringBuffer2.append("\u00a6receivername=");
                stringBuffer2.append(this.aJ);
                stringBuffer2.append("\u00a6mailbody=");
                stringBuffer2.append(this.af);
                break;
            }
            case 19: {
                stringBuffer.append("ilistbuy.pl");
                stringBuffer2.append("\u00a6classID=");
                stringBuffer2.append(this.aE);
                break;
            }
            case 20: {
                stringBuffer.append("buyitem.pl");
                stringBuffer2.append("\u00a6genericID=");
                stringBuffer2.append(this.bt[this.cv][0]);
                break;
            }
            case 21: {
                stringBuffer.append("selllist.pl");
                break;
            }
            case 22: {
                stringBuffer.append("sellitem.pl");
                stringBuffer2.append("\u00a6genericID=");
                stringBuffer2.append(this.bt[this.cv][0]);
                break;
            }
            case 36: {
                stringBuffer.append("customget.pl");
                this.u = "0";
                break;
            }
            case 37: {
                stringBuffer.append("headlist.pl");
                stringBuffer2.append("\u00a6headid=");
                stringBuffer2.append(this.u);
                break;
            }
            case 38: {
                stringBuffer.append("customupload.pl");
                stringBuffer2.append("\u00a6taunt1=");
                stringBuffer2.append(this.bV[4]);
                stringBuffer2.append("\u00a6taunt2=");
                stringBuffer2.append(this.bV[5]);
                stringBuffer2.append("\u00a6taunt3=");
                stringBuffer2.append(this.bV[6]);
                stringBuffer2.append("\u00a6greeting=");
                stringBuffer2.append(this.bV[0]);
                stringBuffer2.append("\u00a6victory=");
                stringBuffer2.append(this.bV[1]);
                stringBuffer2.append("\u00a6loose=");
                stringBuffer2.append(this.bV[2]);
                stringBuffer2.append("\u00a6headid=");
                stringBuffer2.append(this.u);
                break;
            }
            case 39: {
                stringBuffer.append("herostats.pl");
                break;
            }
            case 43: {
                stringBuffer.append("equiplist.pl");
                stringBuffer2.append("\u00a6equipid=");
                stringBuffer2.append(this.aE);
                break;
            }
            case 44: {
                stringBuffer.append("equipdo.pl");
                stringBuffer2.append("\u00a6genericid=");
                stringBuffer2.append(this.bt[this.cv][0]);
                break;
            }
            case 47: {
                stringBuffer.append("friendremoved.pl");
                stringBuffer2.append("\u00a6name=");
                stringBuffer2.append(this.bt[this.cv][2]);
                break;
            }
            case 48: {
                stringBuffer.append("banlistadd.pl");
                stringBuffer2.append("\u00a6name=");
                stringBuffer2.append(this.A);
                break;
            }
            case 49: {
                stringBuffer.append("banlist.pl");
                break;
            }
            case 50: {
                stringBuffer.append("banlistremove.pl");
                stringBuffer2.append("\u00a6name=");
                stringBuffer2.append(this.bt[this.cv][2]);
                break;
            }
            case 23: {
                stringBuffer.append("chalreceive.pl");
                stringBuffer2.append("\u00a6name=");
                stringBuffer2.append(this.o[2]);
                this.bY = this.o[2];
                stringBuffer2.append("\u00a6accept=");
                stringBuffer2.append(this.an);
                break;
            }
            case 24: {
                stringBuffer.append("chalissue.pl");
                stringBuffer2.append("\u00a6name=");
                stringBuffer2.append(this.E);
                break;
            }
            case 25: {
                stringBuffer.append("boarddl.pl");
                break;
            }
            case 70: {
                stringBuffer.append("pgethead.pl");
                stringBuffer2.append("\u00a6headflag=");
                stringBuffer2.append(this.I);
                break;
            }
            case 27: {
                stringBuffer.append("flee.pl");
                break;
            }
            case 26: {
                stringBuffer.append("submit.pl");
                for (int i = 1; i <= this.F.size(); ++i) {
                    String[] stringArray = (String[])this.F.elementAt(i - 1);
                    stringBuffer2.append("\u00a6t");
                    stringBuffer2.append(i);
                    stringBuffer2.append("=");
                    stringBuffer2.append(stringArray[0]);
                    stringBuffer2.append("\u00a6a");
                    stringBuffer2.append(i);
                    stringBuffer2.append("=");
                    stringBuffer2.append(stringArray[1]);
                    if (stringArray[2].length() <= 0) continue;
                    stringBuffer2.append("\u00a6e");
                    stringBuffer2.append(i);
                    stringBuffer2.append("=");
                    stringBuffer2.append(stringArray[2]);
                }
                break;
            }
            case 40: {
                this.aE = 1;
            }
            case 41: {
                stringBuffer.append("herosksp.pl");
                stringBuffer2.append("\u00a6classID=");
                stringBuffer2.append(this.aE);
                break;
            }
            case 42: {
                stringBuffer.append("heroskspdelete.pl");
                stringBuffer2.append("\u00a6genericID=");
                stringBuffer2.append(this.bt[this.aR][0]);
                break;
            }
            case 28: {
                stringBuffer.append("fightresult.pl");
                break;
            }
            case 29: {
                stringBuffer.append("battlereport.pl");
                stringBuffer2.append("\u00a6type=");
                stringBuffer2.append(this.cv);
                break;
            }
            case 35: {
                stringBuffer.append("incabil.pl");
                stringBuffer2.append("\u00a6str=");
                stringBuffer2.append(this.f[1]);
                stringBuffer2.append("\u00a6int=");
                stringBuffer2.append(this.f[2]);
                stringBuffer2.append("\u00a6dex=");
                stringBuffer2.append(this.f[3]);
                stringBuffer2.append("\u00a6tou=");
                stringBuffer2.append(this.f[4]);
                stringBuffer2.append("\u00a6wil=");
                stringBuffer2.append(this.f[5]);
                stringBuffer2.append("\u00a6spd=");
                stringBuffer2.append(this.f[6]);
                break;
            }
            case 52: {
                stringBuffer.append("getranklist.pl");
                stringBuffer2.append("\u00a6ranklistid=");
                stringBuffer2.append(this.cv);
                break;
            }
            case 53: {
                stringBuffer.append("wiseman.pl");
                stringBuffer2.append("\u00a6category=");
                stringBuffer2.append(this.cv);
                break;
            }
            case 67: {
                stringBuffer.append("myclan.pl");
                break;
            }
            case 60: {
                stringBuffer.append("clanstats.pl");
                break;
            }
            case 65: {
                stringBuffer.append("clanlist.pl");
                break;
            }
            case 61: {
                stringBuffer.append("clanhierarchy.pl");
                break;
            }
            case 68: {
                stringBuffer.append("clanjoin.pl");
                break;
            }
            case 71: {
                stringBuffer.append("clanreject.pl");
                break;
            }
            case 63: {
                stringBuffer.append("claninvite.pl");
                stringBuffer2.append("\u00a6heroname=");
                stringBuffer2.append(this.bA);
                break;
            }
            case 66: {
                stringBuffer.append("clankick.pl");
                stringBuffer2.append("\u00a6heroidx=");
                stringBuffer2.append(this.cv);
                break;
            }
            case 69: {
                stringBuffer.append("clanedit.pl");
                break;
            }
            case 64: {
                stringBuffer.append("clancreate.pl");
                stringBuffer2.append("\u00a6clanname=");
                stringBuffer2.append(this.T);
                stringBuffer2.append("\u00a6clanshortname=");
                stringBuffer2.append(this.bn);
                break;
            }
            case 72: {
                stringBuffer.append("clanleave.pl");
            }
        }
        this.s = new d(this, n, stringBuffer.toString(), stringBuffer2.toString());
    }

    final void a(int n, String string) {
        block141: {
            block140: {
                this.cw = null;
                this.by = null;
                this.s = null;
                if (!string.equals("0")) break block140;
                if (n == 2) {
                    this.a();
                }
                break block141;
            }
            if (!this.b(n, string)) break block141;
            switch (n) {
                case 30: 
                case 31: 
                case 32: {
                    boolean bl = false;
                    if (n == 30) {
                        try {
                            EoETown.a("watgreet");
                        }
                        catch (RecordStoreException recordStoreException) {}
                    }
                    try {
                        EoETown.a("watgreet", this.cw);
                    }
                    catch (RecordStoreFullException recordStoreFullException) {
                        bl = true;
                        this.a("Not enough free#phone memory!#Please free up#at least 20 kb#& try again(1)", 12, -1, 0L);
                    }
                    catch (RecordStoreException recordStoreException) {
                        bl = true;
                        this.a("Game initialization#failed.#Try again.", 12, -1, 0L);
                    }
                    if (bl) break;
                    if (this.C) {
                        if (n == 30) {
                            this.b(31);
                            break;
                        }
                        if (n == 31) {
                            this.b(32);
                            break;
                        }
                        if (n != 32) break;
                        String string2 = EoETown.a("watscript", 1);
                        if (!this.X.equals(string2)) {
                            this.b(33);
                            break;
                        }
                        this.m();
                        break;
                    }
                    if (n == 30) {
                        this.br = true;
                    } else if (n == 31) {
                        this.aU = true;
                    } else {
                        this.bd = true;
                    }
                    this.bb = false;
                    break;
                }
                case 33: {
                    try {
                        EoETown.a("watscript");
                    }
                    catch (RecordStoreException recordStoreException) {}
                    boolean bl = false;
                    try {
                        EoETown.a("watscript", this.cw);
                    }
                    catch (RecordStoreFullException recordStoreFullException) {
                        bl = true;
                        this.a("Not enough free#phone memory!#Please free up#at least 20 kb#& try again(2)", 12, -1, 0L);
                    }
                    catch (RecordStoreException recordStoreException) {
                        bl = true;
                        this.a("Game initialization#failed.#Try again.", 12, -1, 0L);
                    }
                    if (bl) break;
                    this.cp = true;
                    try {
                        if (!this.C) {
                            EoETown.a("watkey", this.j);
                        }
                    }
                    catch (RecordStoreFullException recordStoreFullException) {
                        this.a("Not enough free#phone memory!#Please free up#at least 20 kb#& try again(3)", 12, -1, 0L);
                    }
                    catch (RecordStoreException recordStoreException) {}
                    this.bb = false;
                    this.m();
                    break;
                }
                case 12: {
                    if (!this.by.equals("1")) break;
                    this.k(12);
                    break;
                }
                case 34: {
                    if (this.by.equals("1")) {
                        this.b = this.o();
                        this.X = this.o();
                        String string3 = this.o();
                        if (string3.length() > 0) {
                            this.a(com.watAgame.eoe_town.b.b(string3), 0, -1, 5000L);
                        }
                        this.j = EoETown.a("watkey", -1);
                        this.l(2);
                        break;
                    }
                    if (!this.by.equals("2")) break;
                    this.a(com.watAgame.eoe_town.b.b(this.o()), 12, -1, 0L);
                    break;
                }
                case 2: {
                    if (this.by.equals("1")) {
                        this.k(2);
                        break;
                    }
                    if (this.by.equals("2")) {
                        this.a(com.watAgame.eoe_town.b.b(this.o()));
                        this.i(5);
                        break;
                    }
                    if (!this.by.equals("3")) break;
                    this.a(com.watAgame.eoe_town.b.b(this.o()), 12, -1, 0L);
                    break;
                }
                case 4: {
                    if (this.by.equals("1")) {
                        this.k(3);
                        break;
                    }
                    if (!this.by.equals("0")) break;
                    this.a(com.watAgame.eoe_town.b.b(this.o()), 0, 11, 0L);
                    break;
                }
                case 3: {
                    if (this.by.equals("1")) {
                        this.k(3);
                        break;
                    }
                    if (this.by.equals("0")) {
                        this.a(com.watAgame.eoe_town.b.b(this.o()), 0, 11, 0L);
                        break;
                    }
                    if (this.by.equals("2")) {
                        this.a(com.watAgame.eoe_town.b.b(this.o()), 10, 11, 0L);
                        break;
                    }
                    if (!this.by.equals("3")) break;
                    this.a(com.watAgame.eoe_town.b.b(this.o()), 12, -1, 0L);
                    break;
                }
                case 5: {
                    if (this.by.equals("1")) {
                        this.k(2);
                        break;
                    }
                    if (!this.by.equals("3")) break;
                    this.a(com.watAgame.eoe_town.b.b(this.o()), 12, -1, 0L);
                    break;
                }
                case 7: {
                    if (this.by.equals("0")) {
                        this.d = (String)this.cw.elementAt(0);
                        this.cw.removeElementAt(0);
                        this.ca = this.d;
                        this.a(this.g(6), 0, 30, 0L);
                        break;
                    }
                    if (!this.by.equals("1")) break;
                    if (this.K[0].length() > 0) {
                        this.K[1] = this.ca;
                    } else {
                        this.K[0] = this.ca;
                    }
                    this.h();
                    break;
                }
                case 6: {
                    if (!this.by.equals("1")) break;
                    this.h();
                    this.cv = 0;
                    break;
                }
                case 8: {
                    if (!this.by.equals("1")) break;
                    this.cv = 0;
                    this.K[this.k] = "";
                    this.i(14);
                    break;
                }
                case 36: {
                    if (!this.by.equals("1")) break;
                    this.bV = new String[7];
                    for (int i = 0; i < 7; ++i) {
                        this.bV[i] = this.o();
                    }
                    this.cv = 0;
                    this.i(110);
                    break;
                }
                case 38: {
                    if (!this.by.equals("1")) break;
                    this.cv = 4;
                    this.c();
                    this.i(42);
                    break;
                }
                case 67: {
                    if (!this.by.equals("1")) break;
                    this.bI = this.o();
                    this.x = this.o();
                    this.bT = this.o();
                    this.g = this.o();
                    if (this.bI.equals("1")) {
                        this.c();
                        this.a(com.watAgame.eoe_town.b.b(this.g), 0, 48, 0L);
                        break;
                    }
                    if (this.bI.equals("2")) {
                        this.a(com.watAgame.eoe_town.b.b(this.g), 10, 48, 0L);
                        break;
                    }
                    if (!this.bI.equals("3") && !this.bI.equals("4")) break;
                    this.cv = 0;
                    this.i(75);
                    break;
                }
                case 9: 
                case 19: 
                case 21: 
                case 29: 
                case 37: 
                case 39: 
                case 40: 
                case 41: 
                case 46: 
                case 49: 
                case 52: 
                case 53: 
                case 55: 
                case 56: 
                case 60: 
                case 61: 
                case 65: {
                    if (!this.by.equals("1")) break;
                    this.y();
                    if (n == 40) {
                        this.i(117);
                        break;
                    }
                    if (n == 19) {
                        this.i(86);
                        break;
                    }
                    if (n == 21) {
                        this.i(87);
                        break;
                    }
                    if (n == 9) {
                        this.i(52);
                        break;
                    }
                    if (n == 29) {
                        this.i(106);
                        break;
                    }
                    if (n == 37) {
                        this.i(115);
                        break;
                    }
                    if (n == 39) {
                        this.i(116);
                        break;
                    }
                    if (n == 41) {
                        this.i(119);
                        break;
                    }
                    if (n == 46) {
                        this.bN.addElement(new Integer(70));
                        this.i(72);
                        break;
                    }
                    if (n == 49) {
                        this.bN.addElement(new Integer(70));
                        this.i(74);
                        break;
                    }
                    if (n == 52) {
                        this.bN.addElement(new Integer(this.Y));
                        this.i(78);
                        break;
                    }
                    if (n == 55 || n == 56) {
                        this.i(58);
                        break;
                    }
                    if (n == 53) {
                        this.i(47);
                        break;
                    }
                    if (n == 60 || n == 61) {
                        this.i(76);
                        break;
                    }
                    if (n != 65) break;
                    this.bN.addElement(new Integer(this.Y));
                    this.i(81);
                    break;
                }
                case 43: {
                    if (this.by.equals("1")) {
                        this.i(123);
                        this.y();
                        break;
                    }
                    if (!this.by.equals("0")) break;
                    this.a(this.g(Integer.parseInt(this.o())), 0, 122, 0L);
                    break;
                }
                case 44: {
                    if (!this.by.equals("1")) break;
                    this.c();
                    this.cv = 0;
                    this.i(122);
                    break;
                }
                case 20: {
                    if (this.by.equals("0")) {
                        this.a(com.watAgame.eoe_town.b.b(this.o()), 1, 86, 0L);
                        break;
                    }
                    if (!this.by.equals("1")) break;
                    this.ak = this.o();
                    this.a(this.g(197), 1, 86, 0L);
                    break;
                }
                case 22: {
                    if (!this.by.equals("1")) break;
                    this.y();
                    this.i(87);
                    break;
                }
                case 42: {
                    if (!this.by.equals("1")) break;
                    if (this.aE < 13) {
                        this.cv = this.aE - 9;
                        this.c();
                        this.i(118);
                        break;
                    }
                    this.cv = this.aE - 13;
                    this.c();
                    this.i(121);
                    break;
                }
                case 10: {
                    if (this.by.equals("1")) {
                        this.aY = new String[this.cw.size() / 4][4];
                        for (int i = 0; i < this.aY.length; ++i) {
                            for (int j = 0; j < 4; ++j) {
                                this.aY[i][j] = this.o();
                            }
                        }
                        this.cv = 0;
                        this.i(54);
                        break;
                    }
                    this.cv = 0;
                    this.a(this.g(67), 0, 41, 0L);
                    break;
                }
                case 11: {
                    if (!this.by.equals("1")) break;
                    this.a(com.watAgame.eoe_town.b.b(this.o()), 0, 41, 0L);
                    break;
                }
                case 13: {
                    if (this.by.equals("0")) {
                        this.a(new String[]{"No mail."}, 0, 48, 0L);
                        break;
                    }
                    if (!this.by.equals("1")) break;
                    this.cf = "6";
                    this.au = Integer.parseInt(this.o());
                    this.bx = new String[this.au][3];
                    for (int i = 0; i < this.au; ++i) {
                        for (int j = 0; j < 3; ++j) {
                            this.bx[i][j] = this.o();
                        }
                    }
                    if (this.au >= 15) {
                        this.a(this.g(30), 0, 66, 3000L);
                        break;
                    }
                    this.i(66);
                    break;
                }
                case 14: {
                    if (!this.by.equals("1")) break;
                    this.G = this.o();
                    this.af = this.o();
                    this.i(65);
                    this.ab.c();
                    break;
                }
                case 15: {
                    if (!this.by.equals("1")) break;
                    this.cf = "6";
                    this.ac = Integer.parseInt(this.o());
                    this.bz = new String[this.ac];
                    for (int i = 0; i < this.ac; ++i) {
                        this.bz[i] = this.o();
                    }
                    this.i(68);
                    break;
                }
                case 17: {
                    if (!this.by.equals("1")) break;
                    this.be = true;
                    this.i(65);
                    this.ab.a(this.bx);
                    break;
                }
                case 18: {
                    if (this.by.equals("1")) {
                        this.i(48);
                    } else if (this.by.equals("2")) {
                        this.a(this.g(29), 0, -1, 3000L);
                        this.i(48);
                    }
                    this.cf = "4";
                    break;
                }
                case 51: {
                    if (this.by.equals("1")) {
                        this.a("Action successful.", 0, 104, 1000L);
                        break;
                    }
                    if (!this.by.equals("0")) break;
                    this.a(this.g(Integer.parseInt(this.o())), 0, 104, 0L);
                    break;
                }
                case 45: 
                case 48: {
                    if (this.by.equals("0")) {
                        this.A = "";
                        if (n == 45) {
                            this.a(this.g(Integer.parseInt(this.o())), 0, 70, 0L);
                            break;
                        }
                        this.a(this.g(Integer.parseInt(this.o())), 0, 70, 0L);
                        break;
                    }
                    if (!this.by.equals("1")) break;
                    this.A = "";
                    this.i(70);
                    break;
                }
                case 47: 
                case 50: {
                    if (!this.by.equals("1")) break;
                    this.cv = n == 47 ? 2 : 3;
                    this.c();
                    this.i(70);
                    break;
                }
                case 23: {
                    if (this.an == 'n') break;
                    if (this.by.equals("0")) {
                        this.a(this.g(111));
                        break;
                    }
                    this.p();
                    this.i(88);
                    break;
                }
                case 24: {
                    if (this.by.equals("0")) {
                        this.a(this.g(102));
                        break;
                    }
                    if (this.by.equals("2")) {
                        this.a(this.g(101));
                        break;
                    }
                    if (this.by.equals("3")) {
                        this.a(this.g(100));
                        break;
                    }
                    if (this.by.equals("4")) {
                        this.a(this.g(108));
                        break;
                    }
                    if (!this.by.equals("1")) break;
                    this.a(this.g(103));
                    break;
                }
                case 25: {
                    int n2;
                    this.F = new Vector();
                    if (this.ae == -1) {
                        this.ae = Integer.parseInt((String)this.cw.elementAt(0));
                        this.aG = 0;
                    }
                    this.cl = Integer.parseInt((String)this.cw.elementAt(7));
                    this.cg = new int[this.cl][2];
                    for (n2 = 0; n2 < this.cl; ++n2) {
                        this.cg[n2][0] = Integer.parseInt((String)this.cw.elementAt(8 + n2 * 2));
                        this.cg[n2][1] = Integer.parseInt((String)this.cw.elementAt(9 + n2 * 2));
                    }
                    this.bv = new Vector();
                    int n3 = Integer.parseInt((String)this.cw.elementAt(7)) * 2 + 8;
                    int n4 = Integer.parseInt((String)this.cw.elementAt(n3));
                    for (n2 = 0; n2 < 7; ++n2) {
                        this.a(n3 + 1, n4);
                        if (n2 + 1 >= 7) continue;
                        n3 = n3 + 4 * n4 + 1;
                        n4 = Integer.parseInt((String)this.cw.elementAt(n3));
                    }
                    this.aW = 0;
                    this.ag = this.W = Integer.parseInt((String)this.cw.elementAt(2));
                    this.bf = 0;
                    this.ch = new int[]{-1, -1, -1, -1, -1, -1, -1, -1};
                    this.ch[0] = this.ag;
                    this.bL = 0;
                    if (this.ar == null) {
                        this.ar = new int[]{-1, -1, -1, -1, -1, -1, -1, -1, -1, -1};
                    }
                    this.aS = 0;
                    this.ad = Integer.parseInt((String)this.cw.elementAt(5));
                    this.aK = this.W;
                    this.a = new int[4][4];
                    this.aD = new int[4][4];
                    this.av = (String)this.cw.elementAt(6);
                    this.e(this.av);
                    this.a(this.av, this.ad, this.a, 0);
                    this.y = (String)this.cw.elementAt(3);
                    this.e(this.y);
                    this.a(this.y, this.aK, this.aD, 0);
                    this.bl = new int[][]{{-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}};
                    this.bS = 0;
                    this.cv = 0;
                    String string4 = (String)this.cw.elementAt(1);
                    String string5 = (String)this.cw.elementAt(4);
                    if (this.ck == null || !this.ck.equals(string4) && !this.aC.equals(string5)) {
                        this.ck = string4;
                        this.aC = string5;
                        this.I = "3";
                        this.l(70);
                        break;
                    }
                    if (!this.ck.equals(string4)) {
                        this.ck = string4;
                        this.I = "1";
                        this.l(70);
                        break;
                    }
                    if (!this.aC.equals(string5)) {
                        this.aC = string5;
                        this.I = "2";
                        this.l(70);
                        break;
                    }
                    this.c = true;
                    break;
                }
                case 70: {
                    if (!this.by.equals("1")) break;
                    try {
                        int n5 = Integer.parseInt(this.o());
                        if (this.I.equals("3")) {
                            this.m = this.e(n5);
                            n5 = Integer.parseInt(this.o());
                            this.al = this.e(n5);
                        } else if (this.I.equals("2")) {
                            this.al = this.e(n5);
                        } else if (this.I.equals("1")) {
                            this.m = this.e(n5);
                        }
                        this.c = true;
                    }
                    catch (Throwable throwable) {
                        this.a("gethead", throwable, false);
                    }
                    break;
                }
                case 26: {
                    this.i(95);
                    this.q();
                    if (!this.by.equals("1")) break;
                    if (this.Z != null) {
                        this.Z.a();
                    }
                    this.Z = new a(this, 2);
                    break;
                }
                case 27: {
                    if (!this.by.equals("1")) break;
                    this.j();
                    break;
                }
                case 28: {
                    if (!this.by.equals("1")) break;
                    this.f = new String[9];
                    for (int i = 0; i < 9; ++i) {
                        this.f[i] = this.o();
                    }
                    break;
                }
                case 35: {
                    if (!this.by.equals("1")) break;
                    this.cv = 0;
                    this.i(104);
                    break;
                }
                case 63: {
                    if (!this.by.equals("1")) break;
                    this.ca = "";
                    this.bA = "";
                    this.a(this.g(Integer.parseInt(this.o())), 0, 79, 0L);
                    break;
                }
                case 66: {
                    if (!this.by.equals("1")) break;
                    this.a("Action successful.", 0, 79, 1000L);
                    break;
                }
                case 68: {
                    if (!this.by.equals("1")) break;
                    String string6 = this.o();
                    this.x = this.o();
                    this.bT = this.o();
                    this.g = this.o();
                    if (string6.equals("1")) {
                        this.c();
                        this.a(com.watAgame.eoe_town.b.b(this.g), 0, 48, 0L);
                        break;
                    }
                    if (!string6.equals("3")) break;
                    this.cv = 0;
                    this.i(75);
                    break;
                }
                case 71: {
                    if (!this.by.equals("1")) break;
                    this.i(48);
                    break;
                }
                case 69: {
                    if (!this.by.equals("1")) break;
                    this.at = this.o();
                    this.z = this.o();
                    this.bB = this.o();
                    this.T = this.z;
                    this.bn = this.bB;
                    this.cv = 0;
                    this.i(82);
                    break;
                }
                case 64: {
                    if (this.by.equals("1")) {
                        this.cv = 3;
                        this.a(com.watAgame.eoe_town.b.b(this.o()), 0, 48, 0L);
                        break;
                    }
                    if (!this.by.equals("2")) break;
                    this.a(com.watAgame.eoe_town.b.b(this.o()), 0, 82, 0L);
                    break;
                }
                case 72: {
                    if (!this.by.equals("1")) break;
                    this.i(75);
                }
            }
        }
        this.bj = 0;
        this.q = false;
        this.repaint();
    }

    public final boolean b(int n, String string) {
        int n2;
        this.cw = new Vector();
        int n3 = 0;
        while (true) {
            if ((n2 = string.indexOf(166, n3)) == -1) break;
            this.cw.addElement(string.substring(n3, n2));
            n3 = n2 + 1;
        }
        this.cw.addElement(string.substring(n3));
        this.by = this.o();
        this.o();
        n2 = this.cc;
        int n4 = this.bZ;
        this.cc = Integer.parseInt(this.o());
        this.bh = Integer.parseInt(this.o());
        this.bZ = Integer.parseInt(this.o());
        if (this.cc == 1 && n2 != this.cc) {
            this.aF = System.currentTimeMillis();
        }
        if (this.bZ == 1 && n4 != this.bZ) {
            this.bX = System.currentTimeMillis();
        }
        if (n == 26 || n == 1) {
            if (this.by.equals("2")) {
                if (this.Z != null) {
                    this.Z.a();
                    this.Z = null;
                }
                this.cr = Integer.parseInt(this.o());
                this.cs = 0;
                this.ax = 0;
                this.ct = null;
                this.q();
                this.cd = false;
                try {
                    com.watAgame.eoe_town.b.a(Display.getDisplay((MIDlet)this.ab), 600);
                }
                catch (IllegalStateException illegalStateException) {}
                this.i(18);
                this.u();
                this.a(this.g(41), 0, 94, 10000L);
                return false;
            }
        } else {
            if (this.cc == 1) {
                this.o = new String[4];
                this.o[3] = "5";
                for (int i = 0; i < 3; ++i) {
                    this.o[i] = this.o();
                }
            }
            if (this.bh != 0) {
                String string2 = this.o();
                String[] stringArray = null;
                if (this.bh == -1) {
                    this.a(string2, 11, -1, 0L);
                } else if (this.bh == 2) {
                    stringArray = this.g(105);
                } else if (this.bh == 3) {
                    stringArray = this.g(106);
                } else if (this.bh == 4) {
                    stringArray = this.g(107);
                } else if (this.bh == 1 && (this.V == null || this.V.e != 11)) {
                    switch (this.Y) {
                        case 40: 
                        case 41: 
                        case 42: 
                        case 43: 
                        case 44: 
                        case 45: 
                        case 46: 
                        case 47: 
                        case 48: 
                        case 52: 
                        case 54: 
                        case 57: 
                        case 58: 
                        case 59: 
                        case 60: 
                        case 70: 
                        case 71: 
                        case 72: 
                        case 73: 
                        case 74: 
                        case 75: 
                        case 76: 
                        case 77: 
                        case 78: 
                        case 79: 
                        case 80: 
                        case 81: 
                        case 82: 
                        case 83: 
                        case 84: 
                        case 85: 
                        case 86: 
                        case 87: 
                        case 110: 
                        case 111: 
                        case 112: 
                        case 113: 
                        case 114: 
                        case 115: 
                        case 116: 
                        case 117: 
                        case 118: 
                        case 119: 
                        case 120: 
                        case 121: 
                        case 122: 
                        case 123: {
                            this.i(18);
                            String[] stringArray2 = this.g(104);
                            int n5 = stringArray2.length;
                            String[] stringArray3 = new String[n5];
                            String[] stringArray4 = stringArray3;
                            stringArray3[0] = string2;
                            System.arraycopy(stringArray2, 0, stringArray4, 1, n5 - 1);
                            this.i();
                            this.bY = string2;
                            this.p();
                            this.i(88);
                            this.a(stringArray4, 16, -1, 10000L);
                            return false;
                        }
                    }
                }
                if (stringArray != null) {
                    int n6 = stringArray.length;
                    String[] stringArray5 = new String[n6];
                    String[] stringArray6 = stringArray5;
                    stringArray5[0] = string2;
                    System.arraycopy(stringArray, 0, stringArray6, 1, n6 - 1);
                    this.a(stringArray6);
                }
            }
        }
        this.repaint();
        return true;
    }

    final void a(String string, int n, int n2, long l) {
        String[] stringArray = com.watAgame.eoe_town.b.b(string);
        for (int i = 0; i < stringArray.length; i += 5) {
            int n3 = Math.min(5, stringArray.length - i);
            String[] stringArray2 = new String[n3];
            System.arraycopy(stringArray, i, stringArray2, 0, n3);
            this.a(stringArray2, n, n2, l);
        }
    }

    final synchronized void a(String[] stringArray, int n, int n2, long l) {
        c c2 = new c(stringArray, n, n2, l);
        if (this.V == null) {
            this.V = c2;
            this.repaint();
            this.serviceRepaints();
            this.cb = System.currentTimeMillis();
            return;
        }
        this.bs.addElement(c2);
    }

    final void a(String[] stringArray) {
        this.a(stringArray, 0, -1, 0L);
    }

    private final synchronized void v() {
        if (this.V != null) {
            if (this.V.c != -1) {
                this.i(this.V.c);
            }
            if (!this.bs.isEmpty()) {
                this.V = (c)this.bs.elementAt(0);
                this.bs.removeElementAt(0);
                this.cb = System.currentTimeMillis();
                return;
            }
            this.V = null;
        }
    }

    private final void u() {
        this.V = null;
        this.bs.removeAllElements();
    }

    private final synchronized void i() {
        if (this.V != null) {
            for (int i = 0; i < this.bs.size(); ++i) {
                if (((c)this.bs.elementAt((int)i)).e == 11) continue;
                this.bs.removeElementAt(i--);
            }
            if (this.V.e != 11) {
                this.V.c = -1;
                this.v();
            }
        }
    }

    private final void y() {
        this.O = Integer.parseInt(this.o());
        this.ah = this.o();
        this.ak = this.o();
        this.bt = new String[this.O][4];
        for (int i = 0; i < this.O; ++i) {
            for (int j = 0; j < 4; ++j) {
                this.bt[i][j] = this.o();
            }
        }
        this.bi = 0;
        this.cv = 0;
    }

    private final void f(int n) {
        if (n == 6 || n == 1) {
            this.cv = (this.cv + this.bt.length + (n == 6 ? 1 : -1)) % this.bt.length;
        }
    }

    private final void k(int n) {
        this.K = new String[2];
        this.cv = 0;
        for (int i = 0; i < 2; ++i) {
            this.K[i] = this.o();
        }
        if (n == 2) {
            this.bE = this.o();
            String string = EoETown.a("watgreet", 1);
            String string2 = EoETown.a("watscript", 1);
            if (!this.b.equals(string)) {
                this.b(30);
            } else if (!this.X.equals(string2)) {
                this.b(33);
            }
            if (!this.C) {
                this.m();
            }
            return;
        }
        if (n == 3) {
            this.j = this.o();
            try {
                EoETown.a("watkey");
            }
            catch (RecordStoreException recordStoreException) {}
            this.i(7);
        }
    }

    private final void b(int n) {
        this.C = true;
        this.l(n);
        this.i(3);
    }

    private final void m() {
        if (this.K[0].length() == 0 && this.K[1].length() == 0) {
            this.a("Now it is time#to create your first#hero! Simply#enter a cool Name,#pick a Gender &#choose Create.#A hero comes with#all basic equipment#so U can start#playing right away", 11, -1, 0L);
        }
        if (this.K[0].length() > 0) {
            this.i(14);
            return;
        }
        this.e();
    }

    public final String o() {
        if (this.cw.isEmpty()) {
            return "";
        }
        String string = (String)this.cw.elementAt(0);
        this.cw.removeElementAt(0);
        return string;
    }

    private final int c() {
        int n = (Integer)this.bN.lastElement();
        this.bN.removeElementAt(this.bN.size() - 1);
        return n;
    }

    private final void a(String[] stringArray, int n, int n2) {
        if (stringArray[3].equals("1")) {
            this.a(this.g(100), 0, n, 0L);
            return;
        }
        if (stringArray[3].equals("2")) {
            this.a(this.g(101), 0, n, 0L);
            return;
        }
        if (stringArray[3].equals("3")) {
            this.a(this.g(102), 0, n, 0L);
            return;
        }
        if (stringArray[3].equals("4") || stringArray[3].equals("5")) {
            this.aO = new String[]{"", ""};
            String[] stringArray2 = this.g(Integer.parseInt(stringArray[1]));
            System.arraycopy(stringArray2, 0, this.aO, 0, stringArray2.length);
            this.E = stringArray[2];
            this.a(new String[]{stringArray[2], this.aO[0], this.aO[1], stringArray[0]}, n2, n, 0L);
        }
    }

    private final String[] g(int n) {
        return com.watAgame.eoe_town.b.b(EoETown.a("watgreet", n));
    }

    private static final String[] b(String string) {
        Vector<String> vector = new Vector<String>();
        int n = 0;
        while (true) {
            int n2;
            if ((n2 = string.indexOf(35, n)) == -1) break;
            vector.addElement(string.substring(n, n2));
            n = n2 + 1;
        }
        vector.addElement(string.substring(n));
        String[] stringArray = new String[vector.size()];
        for (int i = 0; i < vector.size(); ++i) {
            stringArray[i] = (String)vector.elementAt(i);
        }
        return stringArray;
    }

    public final String w() {
        return this.cf;
    }

    private final void p() {
        if (this.Z != null) {
            this.Z.a();
            this.Z = null;
        }
        this.u();
        this.L = null;
        this.aq = null;
        this.v = null;
        this.bK = null;
        this.bu = null;
        this.U = null;
        System.gc();
        this.ae = -1;
        this.cv = 0;
        this.bO = 1;
        this.c = false;
        this.cd = false;
        this.l(25);
    }

    private final void j() {
        this.ap = null;
        this.ct = null;
        this.f = null;
        this.cv = 0;
        this.aa = 0;
        if (this.Z == null) {
            this.Z = new a(this, 1);
        }
        this.bN.removeAllElements();
        this.h();
    }

    private final void a(int n, int n2) {
        String[][] stringArray = new String[n2][4];
        for (int i = 0; i < n2; ++i) {
            for (int j = 0; j < 4; ++j) {
                stringArray[i][j] = (String)this.cw.elementAt(n + 4 * i + j);
            }
        }
        this.bv.addElement(stringArray);
    }

    private final boolean a(int n) {
        for (int i = 0; i < this.cg.length; ++i) {
            if (n != this.cg[i][0]) continue;
            return false;
        }
        return true;
    }

    private final void x() {
        if (this.bL - 1 >= 0 && this.aM == this.ch[this.bL - 1] && this.bU && this.bL - 1 >= this.bf) {
            this.ch[this.bL] = -1;
            this.ag = this.aM;
            --this.bL;
            --this.bg;
        } else if (this.bL + 1 < 8 && this.f()) {
            ++this.bL;
            this.ch[this.bL] = this.aM;
            this.ag = this.aM;
            ++this.bg;
            this.aT[this.bg] = this.aM;
        }
        this.bU = true;
    }

    private final String k() {
        if (this.bL == 0) {
            return "";
        }
        StringBuffer stringBuffer = new StringBuffer(Integer.toString(this.ch[this.bf]));
        for (int i = this.bf + 1; i <= this.bL; ++i) {
            stringBuffer.append("_");
            stringBuffer.append(Integer.toString(this.ch[i]));
        }
        return stringBuffer.toString();
    }

    private final boolean f() {
        return this.aW * 10 + this.bl[this.bS][1] * (this.bL + 1 - this.bf) < 720;
    }

    private final void r() {
        if (this.Y == 93) {
            this.bR = System.currentTimeMillis();
            this.w = this.bR - this.aA;
            if ((long)(this.bl[this.bS][1] * 100) + this.w >= 72000L) {
                this.i(89);
            } else {
                ++this.aW;
            }
        } else if (this.aW < 72) {
            ++this.aW;
        } else if (!this.cd) {
            this.u();
            this.repaint();
            this.serviceRepaints();
            this.cd = true;
            this.i(95);
            this.a(this.g(40), 17, -1, 0L);
            this.l(26);
            this.bj = 0;
        }
        this.repaint(59, 1, 36, 3);
    }

    private final void d() {
        int n;
        this.bR = System.currentTimeMillis();
        for (n = this.bL; n >= 0 && this.bl[this.bS][1] * (n - this.bf) * 100 + this.aW * 1000 >= 71000; --n) {
        }
        this.bL = n;
        if (this.bf != this.bL) {
            int n2;
            this.bl[this.bS][0] = this.cv;
            this.bl[this.bS][1] = n2 = this.bl[this.bS][1] * (this.bL - this.bf);
            this.aW += n2 / 10;
            ++this.bS;
            this.i[0] = Integer.toString((int)(this.bR - this.aA));
            this.i[2] = this.k();
            this.F.addElement(this.i);
            this.bf = n;
            this.W = this.ch[this.bL];
        }
        this.i(89);
        this.bU = false;
    }

    private final void A() {
        if (this.ar == null) {
            this.ar = new int[]{-1, -1, -1, -1, -1, -1, -1, -1, -1, -1};
            this.aS = 0;
        }
        this.bR = System.currentTimeMillis();
        this.bl[this.bS][0] = this.cv;
        this.aW += this.bl[this.bS][1] / 10;
        ++this.bS;
        this.i[0] = Integer.toString((int)(this.bR - this.aA));
        this.i[2] = Integer.toString(this.W);
        this.ar[this.aS] = this.W;
        ++this.aS;
        this.F.addElement(this.i);
        this.i(89);
    }

    private static final int d(String string) {
        int n = 0;
        while (string.indexOf(95) != -1) {
            string = string.substring(string.indexOf("_") + 1);
            ++n;
        }
        return n;
    }

    private final void q() {
        this.bv = null;
        this.bl = null;
        this.F = null;
    }

    private final void e() {
        this.bN.addElement(new Integer(14));
        this.ca = "";
        this.bQ = '\u0000';
        this.cv = 0;
        this.i(30);
    }

    private final void h() {
        if (this.cf == null) {
            this.cf = "4";
        }
        this.cv = 0;
        this.i(40);
        if (this.Z == null) {
            this.Z = new a(this, 1);
        }
    }

    private final void a() {
        this.bE = "";
        this.ao = "";
        this.i(11);
        this.a("CONTROLS:#- Navigation keys#or joystick move#the Cursor#>#- Left menu key#accepts a choice#- Right menu key#goes back or#cancels >#NEW ACCOUNT:#To open a new#account enter a#Nickname & Pass.#& select Register >#ACCOUNT LOGIN:#To use an existing#account enter your#Nickname & Pass.#& select Login", 11, -1, 0L);
    }

    private final void e(String string) {
        String string2 = EoETown.a("watscript", Math.abs(Integer.parseInt(string)));
        int n = string2.indexOf(35);
        this.bG = Integer.parseInt(string2.substring(n + 1, n + 2));
        if (this.bG == 0) {
            this.ap = null;
            return;
        }
        this.ap = new int[this.bG][4][3];
        string2 = string2.substring(n + 3);
        n = string2.indexOf(35);
        for (int i = 0; i < this.bG; ++i) {
            for (int j = 0; j < 4; ++j) {
                for (int k = 0; k < 3; ++k) {
                    if (n != -1) {
                        this.ap[i][j][k] = string2.substring(0, n).length() == 0 ? this.ap[i - 1][j][k] : Integer.parseInt(string2.substring(0, n));
                        string2 = string2.substring(n + 1);
                        n = string2.indexOf(35);
                        continue;
                    }
                    this.ap[i][j][k] = string2.length() == 0 ? this.ap[i - 1][j][k] : Integer.parseInt(string2);
                }
            }
        }
    }

    private final void a(String string, int n, int[][] nArray, int n2) {
        boolean bl = string.indexOf("-") != -1;
        for (int i = 0; i < 4; ++i) {
            int n3 = bl ? h[n][0] + 15 - (this.ap[n2][i][1] + bo[i]) : h[n][0] + this.ap[n2][i][1];
            nArray[i] = new int[]{-(this.ap[n2][i][0] * bo[i]), 0, n3, h[n][1] + this.ap[n2][i][2], bl ? 2 : 0};
        }
    }

    private final void z() {
        this.ct = new String[15];
        for (int i = 0; i < 14; ++i) {
            this.ct[i] = this.o();
        }
    }

    final void l() {
        Display.getDisplay((MIDlet)this.ab).setCurrent((Displayable)this);
        this.i(48);
        this.cf = "4";
    }

    final void b() {
        this.be = false;
        this.l(14);
    }

    final void h(int n) {
        --this.au;
        String[][] stringArray = new String[this.au][3];
        int n2 = 0;
        for (int i = 0; i < this.au + 1; ++i) {
            if (i == n) continue;
            System.arraycopy(this.bx[i], 0, stringArray[n2], 0, 3);
            ++n2;
        }
        this.bx = null;
        this.bx = new String[this.au][3];
        System.arraycopy(stringArray, 0, this.bx, 0, this.au);
        this.be = false;
        this.l(17);
    }

    final void s() {
        Display.getDisplay((MIDlet)this.ab).setCurrent((Displayable)this);
        this.l(18);
    }

    private final void a(Graphics graphics, String string, String string2) {
        this.c(graphics);
        if (string != null) {
            this.c(graphics, string + (string2 != null && string2.length() > 0 ? " " + string2 : ""));
        }
        graphics.setFont(cm);
        int n = graphics.getFont().getHeight();
        graphics.setColor(0xFFFFFF);
        graphics.fillRect(8, 17, 80, 37);
        graphics.setColor(0xFFFFFF);
        graphics.drawRect(8, 17, 80, 37);
        if (this.bt == null) {
            return;
        }
        int n2 = 37 / n;
        int n3 = 4;
        if (this.bt.length > n2) {
            this.bi = Math.min(this.bi, this.cv - 1);
            this.bi = Math.max(this.bi, Math.max(this.cv - n2 + 2, 0));
            this.bi = Math.min(this.bi, this.bt.length - n2);
            com.watAgame.eoe_town.b.a(graphics, 81, 17, 37, this.bi, n2, this.bt.length);
        } else {
            n3 += 3;
        }
        int n4 = 37 % n >> 1;
        for (int i = this.bi; i < this.bt.length && n4 <= 37 - n; n4 += n, ++i) {
            if (i == this.cv) {
                graphics.setColor(0xA0A0FF);
                graphics.fillRect(8 + n3 - 2, 17 + n4, 70, n);
            }
            graphics.setColor(0);
            String string3 = this.bt[i][2];
            if (this.Y == 52) {
                if ("2456".indexOf(this.bt[i][3]) < 0) {
                    string3 = "\u00f7 " + string3;
                }
            } else if ((this.Y == 123 || this.Y == 117 || this.Y == 115) && this.bt[i][1].length() > 0) {
                string3 = "\u00d7 " + string3;
            }
            graphics.drawString(string3, 8 + n3, 17 + n4, 20);
        }
    }

    private static final void a(Graphics graphics, int n, int n2, int n3, int n4, int n5, int n6) {
        int n7 = n4 * (n3 - 7) / n6;
        int n8 = n5 * (n3 - 7) / n6;
        graphics.setColor(0x808080);
        graphics.fillRect(n, n2 + 4 + n7, 5, n8);
        graphics.setColor(0);
        graphics.drawLine(n + 2, n2, n + 2, n2);
        graphics.drawLine(n + 1, n2 + 1, n + 3, n2 + 1);
        graphics.drawLine(n, n2 + 2, n + 4, n2 + 2);
        graphics.drawLine(n, n2 + n3 - 3, n + 4, n2 + n3 - 3);
        graphics.drawLine(n + 1, n2 + n3 - 2, n + 3, n2 + n3 - 2);
        graphics.drawLine(n + 2, n2 + n3 - 1, n + 2, n2 + n3 - 1);
    }

    public final void a(String string) {
        this.ab.destroyApp(false);
        this.a(com.watAgame.eoe_town.b.b("Connection lost.#Game is closing#down.#Please try later.#(" + string + ")"), 18, -1, 0L);
        this.cb = System.currentTimeMillis();
        this.q = false;
    }

    final void a(String string, Throwable throwable, boolean bl) {
        throwable.printStackTrace();
        String string2 = throwable.getClass().getName();
        this.u();
        this.a(com.watAgame.eoe_town.b.b(string + "#" + string2.substring(string2.lastIndexOf(46) + 1) + "#" + (throwable.getMessage() != null ? throwable.getMessage() + "#s" : "s") + this.Y + " v" + "5.2.8"), 12, -1, 0L);
        this.q = false;
        String string3 = string + ", " + throwable.toString() + ", s" + this.Y;
        this.s = new d(this, 100, this.P + "errorreport.pl", "\u00a6msg=" + string3 + "\u00a6id=" + "01010502" + "\u00a6productid=" + "01010101" + "\u00a6build=" + "5.2.8" + "\u00a6login=" + this.bE);
    }

    private final void b(int n, int n2) {
        switch (n) {
            case 6: {
                ++this.cv;
                break;
            }
            case 1: {
                --this.cv;
                break;
            }
            case 2: 
            case 5: {
                int n3 = 1;
                if (n == 2) {
                    n3 = -1;
                }
                if (n2 == 5) {
                    n3 = n == 2 ? bH[this.cv] : bW[this.cv];
                } else if (n2 == 6) {
                    n3 = n == 2 ? Q[this.cv] : e[this.cv];
                }
                this.cv += n3;
            }
        }
        this.cv = (this.cv + n2) % n2;
    }

    public static final byte[] c(String string) {
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream(string.length());
        for (int i = 0; i < string.length(); ++i) {
            char c2 = string.charAt(i);
            if (c2 <= '\u007f') {
                byteArrayOutputStream.write(c2);
                continue;
            }
            if (c2 <= '\u07ff') {
                byteArrayOutputStream.write(0xC0 | c2 >> 6);
                byteArrayOutputStream.write(0x80 | c2 & 0x3F);
                continue;
            }
            byteArrayOutputStream.write(0xE0 | c2 >> 12);
            byteArrayOutputStream.write(0x80 | c2 >> 6 & 0x3F);
            byteArrayOutputStream.write(0x80 | c2 & 0x3F);
        }
        return byteArrayOutputStream.toByteArray();
    }

    public static final String a(byte[] byArray) {
        StringBuffer stringBuffer = new StringBuffer();
        int n = 0;
        int n2 = -1;
        for (int i = 0; i < byArray.length; ++i) {
            byte by = byArray[i];
            if ((by & 0xC0) == 128) {
                n = n << 6 | by & 0x3F;
                if (--n2 != 0) continue;
                stringBuffer.append((char)n);
                continue;
            }
            if ((by & 0x80) == 0) {
                stringBuffer.append((char)by);
                continue;
            }
            if ((by & 0xE0) == 192) {
                n = by & 0x1F;
                n2 = 1;
                continue;
            }
            if ((by & 0xF0) == 224) {
                n = by & 0xF;
                n2 = 2;
                continue;
            }
            if ((by & 0xF8) == 240) {
                n = by & 7;
                n2 = 3;
                continue;
            }
            if ((by & 0xFC) == 248) {
                n = by & 3;
                n2 = 4;
                continue;
            }
            n = by & 1;
            n2 = 5;
        }
        return stringBuffer.toString();
    }

    private static final boolean c(int n) {
        return n == -10 || n == 55 || n == 42;
    }

    final synchronized void i(int n) {
        if (n == this.Y) {
            return;
        }
        this.l = System.currentTimeMillis();
        this.Y = n;
        this.repaint();
    }

    private static final int d(int n) {
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

    public static final void a(boolean bl) {
        DeviceControl.setLights((int)0, (int)(bl ? 100 : 0));
    }

    public static final void a(Display display, int n) {
        if (n > 0) {
            DeviceControl.startVibra((int)50, (long)n);
            return;
        }
        DeviceControl.stopVibra();
    }

    public static final void a(Graphics graphics, Image image, int n, int n2, int n3, int n4, int n5, int n6, int n7, int n8) {
        int n9 = graphics.getClipX();
        int n10 = graphics.getClipY();
        int n11 = graphics.getClipWidth();
        int n12 = graphics.getClipHeight();
        boolean bl = image.getWidth() != n3 || image.getHeight() != n4;
        if (bl) {
            graphics.setClip(n6, n7, n3, n4);
        }
        int n13 = n5 == 2 ? n6 - image.getWidth() + n3 + n : n6 - n;
        DirectUtils.getDirectGraphics((Graphics)graphics).drawImage(image, n13, n7 - n2, n8, n5 << 12);
        if (bl) {
            graphics.setClip(n9, n10, n11, n12);
        }
    }

    static {
        R = cm = Font.getFont((int)0, (int)0, (int)8);
        bP = cm;
        cn = Font.getFont((int)0, (int)1, (int)8);
        as = cm;
        bM = new int[][]{{48, 10}, {71, 14}, {81, 25}, {64, 28}, {47, 23}, {37, 15}, {30, 23}, {7, 2}};
        h = new int[][]{{4, 10}, {19, 10}, {34, 10}, {49, 10}, {64, 10}, {79, 10}, {3, 17}, {18, 17}, {34, 17}, {49, 17}, {65, 17}, {80, 17}, {2, 24}, {18, 24}, {33, 24}, {50, 24}, {65, 24}, {81, 24}, {2, 31}, {17, 31}, {33, 31}, {50, 31}, {66, 31}, {81, 31}};
        aX = new int[]{17, 30, 43};
        ci = cm.getHeight() >> 1;
        bo = new int[]{7, 16, 12, 13};
        bH = new int[]{-1, -1, 1, -2, -2};
        bW = new int[]{1, 2, 2, -1, 1};
        Q = new int[]{-1, 2, 2, -3, -3, -3};
        e = new int[]{3, 3, 3, -2, -2, 1};
    }
}

