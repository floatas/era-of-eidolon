package com.watAgame.eoe_town;

import com.nokia.mid.ui.DeviceControl;
import com.nokia.mid.ui.DirectUtils;
import com.nokia.mid.ui.FullCanvas;
import java.io.ByteArrayOutputStream;
import java.util.Vector;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.rms.RecordStoreException;
import javax.microedition.rms.RecordStoreFullException;

public final class b extends FullCanvas implements Runnable {
   private static final int[] an = new int[]{41, 48, 42, 49, 45, 46, 43, 44};
   private static final int[] ad = new int[]{0, 1, 6, 3, 4, 2, 5, 7, 8};
   private static final String[] aM = new String[]{"Arena", "Tavern", "Home", "Town gate", "Market", "Wise man", "Academy", "Tower", "Sound"};
   private static final String[] bo = new String[]{" 0", "1.,:;-_'?!\"", "abc2", "def3", "ghi4", "jkl5", "mno6", "pqrs7", "tuv8", "wxyz9"};
   private static final String[] bn = EoETown.b("Game controls#Fight#Hero#Weapons#Armour#Skills#Spells#Community#Clans#Events");
   public EoETown ab;
   public int Y;
   private final Vector bM = new Vector();
   public volatile Thread az;
   private int bh;
   private long co;
   public boolean C;
   private int cc;
   protected String bY;
   private int bZ;
   private int bf;
   protected String[] o;
   protected String[] B;
   public boolean ax;
   boolean q = false;
   private boolean r;
   private final Vector bq = new Vector();
   private c V;
   private long aF;
   private long bX;
   private boolean p;
   private int bA;
   public a Z;
   protected String j;
   public String P = "http://81.7.141.67/1/";
   private d s;
   protected String bC;
   protected String ap;
   protected String b;
   protected String X;
   private String cf;
   protected String[] K;
   Image v;
   Image U;
   Image bI;
   Image bs;
   Image bH;
   Image L;
   Image ar;
   Image n;
   Image m;
   Image am;
   Image J;
   Image aB;
   Image bi;
   Image aN;
   Image aI;
   private int cj;
   private boolean bp;
   private boolean aS;
   private boolean bb;
   private boolean cp;
   private boolean aZ;
   protected String ca = null;
   private String d = null;
   protected char bP = 0;
   private int bD;
   private int aa;
   private int bN = 1;
   protected String A = "";
   private String[][] aW = (String[][])null;
   protected String aH;
   protected String aX;
   private int av;
   private int ac;
   public String[][] bv;
   public String G;
   public String aj;
   public String aJ;
   public String ag;
   private String[] bx;
   public boolean bc = true;
   protected String by;
   protected String bG;
   protected String x;
   protected String bT;
   protected String g;
   protected String au;
   protected String z;
   protected String bz;
   protected String T;
   protected String bl;
   protected int aE;
   private int bg;
   protected String[] bV;
   protected String u = "0";
   protected int aP;
   private String ai;
   private String al;
   private int O;
   protected String[][] br;
   protected char ao = 'n';
   protected String E;
   private boolean cd = false;
   private boolean ct = false;
   private boolean bU = false;
   static final Font cm = Font.getFont(0, 0, 8);
   static final Font R = cm;
   static final Font bO = cm;
   static final Font cn = Font.getFont(0, 1, 8);
   static final Font at = Font.getFont(0, 1, 0);
   static final int[][] bL = new int[][]{{77, 29}, {112, 39}, {17, 75}, {114, 107}, {56, 73}, {4, 34}, {94, 91}, {29, 7}, {0, 0}};
   static final int[][] h = new int[][]{
      {20, 55},
      {35, 55},
      {50, 55},
      {65, 55},
      {80, 55},
      {95, 55},
      {19, 62},
      {34, 62},
      {50, 62},
      {65, 62},
      {81, 62},
      {96, 62},
      {18, 69},
      {34, 69},
      {49, 69},
      {66, 69},
      {81, 69},
      {97, 69},
      {18, 76},
      {33, 76},
      {49, 76},
      {66, 76},
      {81, 76},
      {97, 76}
   };
   static final int[] aV = new int[]{30, 55, 80};
   private static final int ci = cm.getHeight() >> 1;
   private boolean c;
   private int[][] aD;
   private int[][] a;
   private int cl;
   private int bS;
   private int bK;
   private int be;
   private int aQ;
   private Vector bt;
   private int[][] cg;
   private String[][] ba;
   private String[][] aT;
   private int[] M;
   private int[] ch;
   private int[] aR;
   private static final int[] bm = new int[]{7, 16, 12, 13};
   private int[][] bj;
   private long aA;
   private long bR;
   private long w;
   private int aU;
   private int af;
   private int aG;
   private int ah;
   private int W;
   private int aK;
   private int ae;
   private int aL;
   private int bd;
   protected Vector F;
   private String[] i;
   private int[] as;
   private int[] aY;
   protected String ck;
   protected String aC;
   protected String I;
   protected String y;
   protected String aw;
   private int[] ce;
   private boolean N;
   private boolean t;
   private String[] cs;
   private int cq;
   private int ay;
   private int cr;
   protected String[] f;
   private int bJ;
   private int bQ;
   protected int cu = 0;
   protected int k = 0;
   private boolean H;
   private boolean bu = false;
   private boolean S = false;
   private char bB = 0;
   private int D = 0;
   private int bk = 0;
   private int aO = 0;
   private StringBuffer ak = null;
   private Vector cv = null;
   private String bw = null;
   private long cb;
   int bE;
   int[][][] aq;
   private static final int[] bF = new int[]{-1, -1, 1, -2, -2};
   private static final int[] bW = new int[]{1, 2, 2, -1, 1};
   private static final int[] Q = new int[]{-1, 2, 2, -3, -3, -3};
   private static final int[] e = new int[]{3, 3, 3, -2, -2, 1};
   private long l;

   public b(EoETown var1) {
      this.ab = var1;
      this.az = new Thread(this);
      this.az.start();
   }

   public final void run() {
      long var3 = 0L;

      while (this.az != null) {
         long var5;
         long var1 = var5 = System.currentTimeMillis();

         try {
            this.bh = 1000;
            a(true);
            if (this.V != null && this.V.e != 17) {
               if (this.Y == 90 || this.Y == 89) {
                  this.r();
               }

               if (this.V.a > 0L && System.currentTimeMillis() - this.cb > this.V.a) {
                  if (this.V.e != 16 || !this.q) {
                     this.v();
                     this.repaint();
                     this.bh = 0;
                  }
               } else if (this.V.e == 16 && !this.q && this.V.b) {
                  this.v();
                  this.repaint();
                  this.bh = 0;
               }
            }

            if (this.V == null) {
               switch (this.Y) {
                  case 0:
                     this.co = var5;
                     this.bh = 0;
                     this.ax = true;
                     this.bA = 0;
                     this.i(2);
                  case 1:
                  case 3:
                  case 4:
                  case 5:
                  case 6:
                  case 8:
                  case 9:
                  case 10:
                  case 11:
                  case 13:
                  case 15:
                  case 16:
                  case 17:
                  case 18:
                  case 19:
                  case 20:
                  case 21:
                  case 22:
                  case 23:
                  case 24:
                  case 25:
                  case 26:
                  case 27:
                  case 28:
                  case 29:
                  case 30:
                  case 32:
                  case 33:
                  case 34:
                  case 35:
                  case 36:
                  case 37:
                  case 38:
                  case 39:
                  case 41:
                  case 42:
                  case 43:
                  case 44:
                  case 45:
                  case 46:
                  case 47:
                  case 48:
                  case 49:
                  case 50:
                  case 51:
                  case 52:
                  case 53:
                  case 54:
                  case 55:
                  case 56:
                  case 57:
                  case 58:
                  case 61:
                  case 62:
                  case 63:
                  case 64:
                  case 65:
                  case 67:
                  case 69:
                  case 70:
                  case 72:
                  case 74:
                  case 75:
                  case 76:
                  case 77:
                  case 78:
                  case 79:
                  case 81:
                  case 82:
                  case 85:
                  case 86:
                  case 87:
                  case 102:
                  case 103:
                  case 104:
                  case 105:
                  case 106:
                  case 107:
                  case 108:
                  case 109:
                  case 110:
                  case 111:
                  default:
                     break;
                  case 2:
                     if (this.bA < 10) {
                        this.bA++;
                     } else {
                        this.i(4);
                        this.k(34);
                     }

                     this.bh = 500;
                     break;
                  case 7:
                     if (this.cj < 0) {
                        this.cj = 0;
                        this.l = var5;
                     } else if (!this.aZ && var5 - this.l > 4000L) {
                        boolean var22 = false;
                        if (!this.bp) {
                           this.k(30);
                           var22 = true;
                        } else if (!this.aS) {
                           this.k(31);
                           var22 = true;
                        } else if (!this.bb) {
                           this.k(32);
                           var22 = true;
                        } else if (!this.cp) {
                           this.k(33);
                           var22 = true;
                        } else if (this.cj >= 4) {
                           this.l();
                           break;
                        }

                        if (var22) {
                           this.cj++;
                           this.l = var5;
                           this.aZ = true;
                           this.repaint();
                        }
                     }

                     this.bh = 250;
                     break;
                  case 12:
                  case 31:
                  case 59:
                  case 60:
                  case 71:
                  case 73:
                  case 80:
                  case 83:
                  case 84:
                  case 112:
                     this.t();
                     this.bh = 500;
                     this.repaint();
                     break;
                  case 14:
                     this.ab.b = null;
                     break;
                  case 40:
                     this.aa++;
                     this.bh = 200;
                     this.repaint();
                     break;
                  case 66:
                     if (Display.getDisplay(this.ab).getCurrent() == this) {
                        this.ab.a(this.bv);
                     }
                     break;
                  case 68:
                     if (Display.getDisplay(this.ab).getCurrent() == this) {
                        this.ab.a(this.bx);
                     }
                     break;
                  case 88:
                     if (this.c && this.V == null) {
                        this.aA = System.currentTimeMillis();
                        this.bh = 0;
                        this.i(89);
                     } else {
                        this.bh = 250;
                        this.repaint();
                     }
                     break;
                  case 89:
                  case 90:
                  case 91:
                  case 92:
                  case 93:
                     this.r();
                     break;
                  case 94:
                     if (this.ay < this.cq) {
                        boolean var21;
                        if ((var21 = this.cs == null) || this.ay > 0) {
                           this.z();
                        }

                        this.ae = Integer.parseInt(this.cs[2]);
                        this.aK = Integer.parseInt(this.cs[0]);
                        this.b(this.cs[1]);
                        this.a(this.cs[1], this.aK, this.aD, 0);
                        this.b(this.cs[3]);
                        this.a(this.cs[3], this.ae, this.a, 0);
                        if (var21) {
                           this.repaint();
                           break;
                        }

                        this.cr = 0;
                        this.b(this.cs[10]);
                        this.i(96);
                     } else if (this.cs != null && this.cs[4].equals("0")) {
                        this.i(18);
                        this.k(28);
                        this.a(this.g(44), 16, 100, 5000L);
                     } else if (this.cs != null && this.cs[4].equals("1")) {
                        this.i(18);
                        this.k(28);
                        this.a(this.g(43), 16, 100, 5000L);
                     } else {
                        this.c = false;
                        this.k(25);
                        this.i(88);
                        this.a(this.g(42), 16, -1, 5000L);
                        this.cd = false;
                     }

                     this.bh = 0;
                     break;
                  case 95:
                     this.bh = 250;
                     this.repaint();
                     break;
                  case 96:
                     if (this.cr >= this.bE) {
                        if (this.cs[12].length() > 0) {
                           this.i(97);
                        } else if (this.cs[11].length() > 0) {
                           this.cr = 0;
                           this.b(this.cs[11]);
                           this.i(98);
                        } else {
                           this.i(99);
                        }

                        this.bh = 250;
                     } else {
                        if (this.cs[9].equals("0")) {
                           this.a(this.cs[10], this.aK, this.aD, this.cr);
                        } else {
                           this.a(this.cs[10], this.ae, this.a, this.cr);
                        }

                        this.cr++;
                        this.bh = 250;
                        this.repaint();
                     }
                     break;
                  case 97:
                     if (this.ce == null) {
                        int var11;
                        if (this.cs[9].equals("0")) {
                           var11 = Integer.parseInt(this.cs[0]);
                        } else {
                           var11 = Integer.parseInt(this.cs[2]);
                        }

                        int var12 = Integer.parseInt(this.cs[13]);
                        int var7 = h[var11][0];
                        int var8 = h[var11][1];
                        int var9 = h[var12][0];
                        int var10 = h[var12][1];
                        int var15 = var12 % 6 - var11 % 6;
                        int var16 = var12 / 6 - var11 / 6;
                        int var17;
                        if ((var17 = 300 * EoETown.a(var15 * var15 + var16 * var16 << 8) >> 4) != 0) {
                           int var13 = (var9 - var7 << 16) / var17;
                           int var14 = (var10 - var8 << 16) / var17;
                           this.ce = new int[]{var7, var8, var9, var10, var13, var14};
                        } else {
                           this.N = true;
                        }
                     }

                     if (this.N) {
                        if (this.cs[11].length() > 0) {
                           this.cr = 0;
                           this.b(this.cs[11]);
                           this.i(98);
                        } else {
                           this.i(99);
                        }

                        this.ce = null;
                        this.N = false;
                        this.bh = 0;
                     } else {
                        this.repaint();
                        this.serviceRepaints();
                        this.bh = 0;
                     }
                     break;
                  case 98:
                     if (this.cr >= this.bE) {
                        this.i(99);
                        this.bh = 0;
                     } else {
                        if (this.cs[9].equals("0")) {
                           this.a(this.cs[11], this.ae, this.a, this.cr);
                        } else {
                           this.a(this.cs[11], this.aK, this.aD, this.cr);
                        }

                        this.cr++;
                        this.bh = 250;
                        this.repaint();
                     }
                     break;
                  case 99:
                     if (!this.t && this.cs[7].length() > 0) {
                        this.t = true;
                        if (this.cs[5].equals("0") || this.cs[5].equals("2")) {
                           try {
                              a(Display.getDisplay(this.ab), 600);
                           } catch (IllegalStateException var18) {
                           }

                           this.aG = this.aG + Integer.parseInt(this.cs[6]);
                        }

                        this.bh = 1500;
                        this.repaint();
                     } else {
                        this.t = false;
                        this.ay++;
                        this.i(94);
                        this.bh = 0;
                     }
                     break;
                  case 100:
                     if (this.f != null && this.f[7].length() > 0) {
                        this.a(EoETown.b(this.f[7]), 0, 100, 0L);
                        this.f[7] = "";
                        this.i(101);
                     } else if (this.f != null && this.f[0].length() > 0) {
                        this.a(this.g(59), 0, 103, 0L);
                        this.cu = 0;
                        this.i(101);
                     } else {
                        if (this.Z == null) {
                           this.Z = new a(this, 1);
                        }

                        this.cu = 0;
                        this.i(104);
                     }

                     this.bh = 0;
                     break;
                  case 101:
                     this.repaint();
               }
            }

            if (this.Y == 7 || this.Y == 18 || this.Y == 95 || this.s != null && this.s.isAlive()) {
               this.bh = Math.min(this.bh, 600);
               if (this.aI == null) {
                  this.aI = EoETown.a("wait", true);
               }

               this.repaint(this.bJ + 1, this.bQ + 1, this.aI.getWidth(), 13);
            }

            boolean var23 = false;
            if ((this.cc != 1 || var5 - this.aF >= 6000L) && (this.bZ != 1 || var5 - this.bX >= 6000L)) {
               if (this.aF != 0L) {
                  var23 = true;
                  this.aF = 0L;
               }
            } else {
               this.bh = Math.min(this.bh, 200);
               var23 = true;
            }

            if (var23) {
               if (this.bI == null) {
                  this.bI = EoETown.a("mail", true);
               }

               if (this.bs == null) {
                  this.bs = EoETown.a("challenge", true);
               }

               this.repaint(this.bJ + 49, this.bQ + 117, 67 + this.bI.getWidth(), Math.max(this.bs.getHeight(), this.bI.getHeight()));
            }

            this.bD++;
            if ((var5 = System.currentTimeMillis()) - this.co > 600000L && !this.r) {
               this.a("cto");
            }

            long var24 = this.bh + var1 - var5;
            if (this.bh == 1000 && var5 - var3 > 5000L || var5 - var3 > 10000L) {
               System.gc();
               var3 = var5;
               var24 = this.bh + var1 - System.currentTimeMillis();
            }

            if (var24 > 0L) {
               Thread.sleep(var24);
            }
         } catch (Throwable var19) {
            this.a("run", var19, false);
         }
      }
   }

   protected final void keyPressed(int var1) {
      try {
         int var2 = 0;

         try {
            var2 = this.getGameAction(var1);
         } catch (IllegalArgumentException var8) {
         }

         c var3 = this.V;
         if (this.V != null && var3.e != 17) {
            int var20 = var3.e;
            int var24 = var3.c;
            if (var20 == 11 && (var2 == 2 || var2 == 5)) {
               if (System.currentTimeMillis() - this.cb > 500L) {
                  this.v();
               }

               this.repaint();
               return;
            }

            if (var1 == -6 || var1 == -7 || var2 == 8) {
               if (var20 == 14) {
                  if (var1 == -6 || var2 == 8) {
                     this.k(8);
                     this.a("Action successful.", 0, -1, 1000L);
                  } else if (var1 == -7) {
                     this.v();
                  }
               } else if (var20 != 0 && var20 != 11) {
                  if (this.V.e == 16) {
                     this.V.b = true;
                     if (!this.q) {
                        this.v();
                     }

                     return;
                  }

                  if (var20 == 1 && var24 == 86) {
                     this.i(var24);
                  } else if (var20 != 12 && var20 != 13 && var20 != 18) {
                     if (var1 != -7 || var20 != 0 && var20 != 1 && var20 != 2 && var20 != 15 && var20 != 6 && var20 != 8 && var20 != 9 && var20 != 10) {
                        if ((var1 == -6 || var2 == 8 || var1 == -7) && var20 == 3) {
                           if (var1 != -6 && var2 != 8) {
                              this.ao = 'n';
                           } else {
                              this.ao = 'y';
                           }

                           this.k(23);
                        } else if (var20 != 2 || var1 != -6 && var2 != 8) {
                           if (var1 == -6 || var2 == 8) {
                              if (var20 == 15) {
                                 if (!this.cd) {
                                    this.cd = true;
                                    this.i(95);
                                    this.a(this.g(40), 17, -1, 0L);
                                    this.k(26);
                                 }
                              } else if (var20 == 6) {
                                 this.k(27);
                              } else if (var20 == 10) {
                                 if (var24 == 86) {
                                    this.k(20);
                                 } else if (var24 == 87) {
                                    this.k(22);
                                 } else if (var24 == 48) {
                                    this.k(68);
                                 } else if (var24 == 81) {
                                    this.k(66);
                                 } else if (var24 == 75) {
                                    this.k(72);
                                 } else if (var24 == 11) {
                                    this.k(5);
                                 } else if (var24 == 103) {
                                    String var7 = Integer.toString(Integer.parseInt(this.f[this.cu + 1]) + this.aY[this.cu]);
                                    this.f[this.cu + 1] = var7;
                                    this.f[0] = Integer.toString(Integer.parseInt(this.f[0]) - 1);
                                    if (Integer.parseInt(this.f[0]) <= 0) {
                                       this.k(35);
                                    }
                                 }
                              }
                           }
                        } else {
                           this.k(24);
                        }
                     } else if (var24 != 11 || var20 != 15 && var20 != 9) {
                        if (var24 == 11 && var20 == 8) {
                           this.cu = 1;
                           this.i(var24);
                        } else {
                           if (var20 == 10 && var24 == 48) {
                              this.c();
                              this.k(71);
                           } else if (var20 == 10 && var24 == 75) {
                              this.i(75);
                           } else if (var20 != 10 && var24 != 89 && var20 != 6 && var20 != 15) {
                              this.cu = 0;
                           }

                           this.i(var24);
                        }
                     } else {
                        this.ab.destroyApp(true);
                     }
                  } else if (var1 != -6 && var2 != 8 && var20 != 18 && var20 != 12) {
                     if (var1 == -7) {
                        this.v();
                     }
                  } else {
                     if (this.s != null) {
                        this.s.join();
                     }

                     this.ab.destroyApp(true);
                  }
               } else {
                  if (var24 != 86 && var24 != 87) {
                     if (System.currentTimeMillis() - this.cb > 500L) {
                        this.v();
                     }

                     this.repaint();
                     return;
                  }

                  this.a(EoETown.b(this.br[this.cu][1]), var24 == 86 && this.br[this.cu][2].startsWith("*") ? 1 : 10, var24, 0L);
               }

               this.v();
            }
         } else if (this.ax && !this.q && this.Y != 18 && this.Y != 94 && this.Y != 96 && this.Y != 97 && this.Y != 98 && this.Y != 99 && this.Y != 100) {
            this.co = System.currentTimeMillis();
            if (d(var1)
               && this.Y != 89
               && this.Y != 71
               && this.Y != 73
               && this.Y != 60
               && this.Y != 59
               && this.Y != 31
               && this.Y != 12
               && (this.Y < 88 || this.Y > 99)
               && this.Y != 100
               && this.Y != 80
               && this.Y != 112
               && this.Y != 84
               && this.Y != 83
               && this.Y != 11
               && this.Y != 14
               && this.V == null) {
               if (this.cc == 1) {
                  this.a(this.o, this.Y, 3);
                  return;
               }

               this.a("Sorry! Nobody#is challenging U#right now. Swords#will appear below#upon a challenge", 0, -1, 0L);
               return;
            }

            label1674:
            switch (this.Y) {
               case 2:
                  this.k(34);
                  this.i(4);
               case 3:
               case 4:
               case 6:
               case 7:
               case 8:
               case 9:
               case 10:
               case 13:
               case 16:
               case 17:
               case 18:
               case 19:
               case 20:
               case 21:
               case 22:
               case 23:
               case 24:
               case 25:
               case 26:
               case 27:
               case 28:
               case 29:
               case 33:
               case 34:
               case 35:
               case 36:
               case 37:
               case 38:
               case 39:
               case 49:
               case 50:
               case 51:
               case 53:
               case 55:
               case 56:
               case 61:
               case 62:
               case 63:
               case 64:
               case 65:
               case 66:
               case 67:
               case 68:
               case 69:
               case 88:
               case 94:
               case 95:
               case 96:
               case 97:
               case 98:
               case 99:
               case 100:
               case 101:
               case 102:
               case 105:
               case 107:
               case 108:
               case 109:
               default:
                  break;
               case 5:
                  if (var1 == -6 || var2 == 8) {
                     this.k(5);
                  } else if (var1 == -7) {
                     this.ab.destroyApp(true);
                  }
                  break;
               case 11:
                  if (var1 == -6 || var2 == 8) {
                     switch (this.cu) {
                        case 0:
                           this.a(this.bC, true, 14);
                           this.i(12);
                           break label1674;
                        case 1:
                           this.a(this.ap, false, 14);
                           this.i(12);
                           break label1674;
                        case 2:
                           this.k(3);
                           break label1674;
                        case 3:
                           this.k(4);
                     }
                  } else if (this.bC.length() != 0 && this.ap.length() != 0) {
                     this.b(var2, 4);
                  } else if (var2 == 6 || var2 == 1) {
                     this.cu = (this.cu + 1) % 2;
                  }
                  break;
               case 12:
                  if (var1 != -6 && var1 != -5 && var1 != -1 && var1 != -2) {
                     this.a(var1, false);
                  } else {
                     if (this.cu == 0) {
                        this.bC = this.m();
                        if (this.ap.length() > 0 && this.bC.length() > 0) {
                           this.cu = 2;
                        } else {
                           this.cu = 1;
                           this.a(this.ap, false, 14);
                        }
                     } else if (this.cu == 1) {
                        this.ap = this.m();
                        if (this.bC.length() == 0 || var1 == -1) {
                           this.cu = 0;
                        } else if (this.ap.length() == 0) {
                           this.cu = 1;
                        } else {
                           this.cu = 2;
                        }
                     }

                     this.i(11);
                  }
                  break;
               case 14:
                  if (var1 != -6 && var2 != 8) {
                     this.b(var2, 3);
                  } else {
                     switch (this.cu) {
                        case 0:
                        case 1:
                           if (this.K[this.cu].length() == 0) {
                              this.a(
                                 "You are about to#create a standard#level 12 Hero with#evenly distributed#ability scores.#To create a more#personalised Hero#you must log in to#Orumant and create#your Hero there!",
                                 0,
                                 -1,
                                 0L
                              );
                              this.e();
                           } else {
                              this.k(6);
                           }
                           break;
                        case 2:
                           if (this.K[0].length() != 0 || this.K[1].length() != 0) {
                              if (this.K[0].length() > 0 && this.K[1].length() > 0) {
                                 this.B = new String[]{this.K[0], this.K[1]};
                              } else if (this.K[0].length() > 0) {
                                 this.B = new String[]{this.K[0]};
                              } else {
                                 this.B = new String[]{this.K[1]};
                              }

                              this.k = 0;
                              this.i(15);
                              this.repaint();
                              this.serviceRepaints();
                           }
                     }

                     if (this.Y != 15 && this.Y != 30) {
                        this.c(14);
                     }
                  }
                  break;
               case 15:
                  if (var1 == -7) {
                     this.i(14);
                  } else if (var1 == -6 || var2 == 8) {
                     this.a(this.g(77), 14, -1, 0L);
                  } else if ((var2 == 1 || var2 == 6) && this.K[0].length() > 0 && this.K[1].length() > 0) {
                     this.k = (this.k + 1) % 2;
                  }
                  break;
               case 30:
                  if (var1 == -7) {
                     this.ca = "";
                     this.bP = 0;
                     this.cu = 0;
                     this.c();
                  } else if (var1 == -6 || var2 == 8) {
                     switch (this.cu) {
                        case 0:
                           this.a(this.ca, true, 14);
                           this.i(31);
                           break label1674;
                        case 1:
                           this.B = new String[]{"Male", "Female"};
                           this.k = 0;
                           this.i(32);
                           break label1674;
                        case 2:
                           this.k(7);
                           this.cu = 0;
                     }
                  } else if (this.ca.length() != 0 && this.bP != 0) {
                     this.b(var2, 3);
                  } else {
                     this.b(var2, 2);
                  }
                  break;
               case 31:
                  if (var1 != -6 && var1 != -5 && var1 != -1 && var1 != -2) {
                     this.a(var1, false);
                  } else {
                     this.ca = this.m();
                     this.i(30);
                     if (this.bP != 0 && var1 == -1 && this.ca.length() > 0) {
                        this.cu = 2;
                     } else {
                        this.cu = 1;
                     }
                  }
                  break;
               case 32:
                  if (var1 == -7) {
                     this.bP = 0;
                     this.i(30);
                  } else if (var1 == -6 || var2 == 8) {
                     this.i(30);
                     if (this.ca.length() > 0) {
                        this.cu = 2;
                     } else {
                        this.cu = 0;
                     }

                     if (this.k == 0) {
                        this.bP = 'm';
                     } else {
                        this.bP = 'f';
                     }
                  } else if (var2 == 1 || var2 == 6) {
                     this.k = (this.k + 1) % 2;
                  }
                  break;
               case 40:
                  if (var1 == -7 && !this.bM.isEmpty()) {
                     this.cu = 0;
                     this.c();
                  } else if (var1 != -6 && var2 != 8) {
                     int var19 = 0;

                     while (var19 < 8 && ad[var19] != this.cu) {
                        var19++;
                     }

                     switch (var2) {
                        case 1:
                        case 2:
                           this.cu = ad[(var19 - 1 + 8) % 8];
                        case 3:
                        case 4:
                        default:
                           break;
                        case 5:
                        case 6:
                           this.cu = ad[(var19 + 1) % 8];
                     }

                     this.aa = 0;
                  } else if (this.cu == 3) {
                     this.a(this.g(39), 13, -1, 0L);
                  } else {
                     this.c(40);
                     this.i(an[this.cu]);
                     if (this.cu == 5) {
                        this.O = bn.length;
                        this.ai = "Help categories:";
                        this.al = "";
                        this.br = new String[this.O][4];

                        for (int var18 = 0; var18 < this.O; var18++) {
                           for (int var23 = 0; var23 < 4; var23++) {
                              if (var23 == 2) {
                                 this.br[var18][2] = bn[var18];
                              } else {
                                 this.br[var18][var23] = "";
                              }
                           }
                        }

                        this.bg = 0;
                     }

                     this.cu = 0;
                  }
                  break;
               case 41:
                  if (var1 == -7) {
                     this.cu = 0;
                     this.aa = 0;
                     this.c();
                  } else if (var1 != -6 && var2 != 8) {
                     this.b(var2, 5);
                  } else {
                     this.c(41);
                     if (this.cu == 0) {
                        this.k(10);
                     } else if (this.cu == 1) {
                        this.k(9);
                     } else if (this.cu == 2) {
                        this.k(55);
                     } else if (this.cu == 3) {
                        this.k(56);
                     } else if (this.cu == 4) {
                        this.aH = "";
                        this.aX = "";
                        this.cu = 0;
                        this.i(57);
                     }
                  }
                  break;
               case 42:
                  if (var1 == -6 || var2 == 8) {
                     this.c(this.Y);
                     if (this.cu == 0) {
                        this.k(39);
                     } else if (this.cu == 1) {
                        this.k(40);
                     } else if (this.cu == 2) {
                        this.cu = 0;
                        this.i(118);
                     } else if (this.cu == 3) {
                        this.cu = 0;
                        this.i(121);
                     } else if (this.cu == 4) {
                        this.k(36);
                     } else if (this.cu == 5) {
                        this.cu = 0;
                        this.i(122);
                     }
                  } else if (var1 == -7) {
                     this.cu = 2;
                     this.c();
                  } else {
                     this.b(var2, 6);
                  }
                  break;
               case 43:
               case 44:
                  if (var1 == -6 || var2 == 8) {
                     this.c(this.Y);
                     if (this.Y == 43) {
                        this.aE = this.cu + 9;
                     } else {
                        this.aE = this.cu + 13;
                     }

                     this.k(19);
                  } else if (var1 == -7) {
                     if (this.Y == 43) {
                        this.cu = 6;
                     } else if (this.Y == 44) {
                        this.cu = 7;
                     }

                     this.c();
                  } else {
                     this.b(var2, 4);
                  }
                  break;
               case 45:
                  if (var1 == -6 || var2 == 8) {
                     this.c(this.Y);
                     if (this.cu == 0) {
                        this.i(85);
                     } else if (this.cu >= 1 && this.cu < 5) {
                        this.aE = this.cu + 3;
                        this.k(19);
                     } else if (this.cu == 5) {
                        this.k(21);
                     }
                  } else if (var1 == -7) {
                     this.cu = 4;
                     this.c();
                  } else {
                     this.b(var2, 6);
                  }
                  break;
               case 46:
                  if (var1 == -7) {
                     this.cu = 5;
                     this.c();
                  } else if (var2 == 6 || var2 == 1) {
                     this.f(var2);
                  } else if (var1 == -6 || var2 == 8) {
                     this.k(53);
                  }
                  break;
               case 47:
                  if (var1 == -7) {
                     this.O = 10;
                     this.ai = "Help categories:";
                     this.al = "";
                     this.br = new String[10][4];

                     for (int var16 = 0; var16 < 10; var16++) {
                        for (int var22 = 0; var22 < 4; var22++) {
                           if (var22 == 2) {
                              this.br[var16][2] = bn[var16];
                           } else {
                              this.br[var16][var22] = "";
                           }
                        }
                     }

                     this.bg = 0;
                     this.cu = 0;
                     this.i(46);
                  } else if (var2 == 6 || var2 == 1) {
                     this.f(var2);
                  } else if (var1 == -6 || var2 == 8) {
                     String var17 = this.br[this.cu][1];
                     this.a(EoETown.b(var17), 0, this.Y, 0L);
                  }
                  break;
               case 48:
                  if (var1 != -6 && var2 != 8) {
                     if (var1 == -7) {
                        this.cu = 1;
                        this.aa = 0;
                        this.c();
                     } else {
                        this.b(var2, 5);
                     }
                  } else {
                     if (this.cu != 0 && this.cu != 1) {
                        this.c(this.Y);
                     }

                     if (this.cu == 0) {
                        this.k(13);
                     } else if (this.cu == 1) {
                        this.k(15);
                     } else if (this.cu == 2) {
                        this.cu = 0;
                        this.i(70);
                     } else if (this.cu == 3) {
                        this.k(67);
                     } else if (this.cu == 4) {
                        this.cu = 0;
                        this.i(77);
                     }
                  }
                  break;
               case 52:
               case 58:
               case 72:
               case 74:
               case 86:
               case 87:
               case 106:
               case 114:
               case 115:
               case 117:
                  if (var1 == -7) {
                     if (this.Y == 86 || this.Y == 114 || this.Y == 117 || this.Y == 106) {
                        this.cu = 0;
                        this.c();
                     } else if (this.Y == 115) {
                        this.cu = 2;
                        this.c();
                        this.i(110);
                     } else if (this.Y == 58) {
                        this.cu = 2;
                        this.c();
                        this.i(41);
                     } else if (this.Y != 72 && this.Y != 74) {
                        this.c();
                     } else {
                        if (this.Y == 72) {
                           this.cu = 2;
                        } else {
                           this.cu = 3;
                        }

                        this.c();
                     }
                  } else if (var1 != -6 && var2 != 8) {
                     if (var2 == 6 || var2 == 1) {
                        this.f(var2);
                     }
                  } else if (this.Y == 52 || this.Y == 58) {
                     this.a(this.br[this.cu], this.Y, 2);
                  } else if (this.Y == 114) {
                     this.bV[this.aP] = this.br[this.cu][0];
                     this.cu = this.aP;
                     this.c();
                  } else if (this.Y == 115) {
                     this.u = this.br[this.cu][0];
                     this.bV[3] = this.br[this.cu][2];
                     this.cu = 2;
                     this.i(110);
                  } else if (this.Y == 72) {
                     this.k(47);
                  } else if (this.Y == 74) {
                     this.k(50);
                  } else if (this.Y == 117) {
                     String var14 = this.br[this.cu][3];
                     this.a(EoETown.b(var14), 0, 117, 0L);
                  } else if (this.Y != 106) {
                     String var15 = this.br[this.cu][3];
                     this.a(this.g(Integer.parseInt(var15)), 0, this.Y, 0L);
                  }
                  break;
               case 54:
                  if (var1 == -7) {
                     this.cu = 0;
                     this.c();
                  } else if (var2 == 6) {
                     if (this.cu == this.aW.length - 1) {
                        this.k(10);
                     } else {
                        this.cu = (this.cu + 1) % this.aW.length;
                     }
                  } else if (var2 == 1) {
                     this.cu = (this.cu + this.aW.length - 1) % this.aW.length;
                  } else if (var1 == -6 || var2 == 8) {
                     this.a(this.aW[this.cu], 54, 2);
                  }
                  break;
               case 57:
                  if (var1 == -7) {
                     this.aH = "";
                     this.aX = "";
                     this.cu = 2;
                     this.c();
                  } else if (var1 == -6 || var2 == 8) {
                     switch (this.cu) {
                        case 0:
                           this.a(this.aH, true, 14);
                           this.i(59);
                           break label1674;
                        case 1:
                           this.a(this.aX, false, 30);
                           this.i(60);
                           break label1674;
                        case 2:
                           this.k(11);
                     }
                  } else if (this.aH.length() == 0 && this.aX.length() == 0) {
                     this.b(var2, 2);
                  } else {
                     this.b(var2, 3);
                  }
                  break;
               case 59:
                  if (var1 == -6 || var1 == -5 || var1 == -2) {
                     this.aH = this.m();
                     this.i(57);
                     this.cu = 1;
                  } else if (var1 == -1) {
                     this.aH = this.m();
                     this.i(57);
                     if (this.aH.length() == 0 && this.aX.length() == 0) {
                        this.cu = 1;
                     } else {
                        this.cu = 2;
                     }
                  } else {
                     this.a(var1, true);
                  }
                  break;
               case 60:
                  if (var1 == -6 || var1 == -5 || var1 == -2) {
                     this.aX = this.m();
                     this.i(57);
                     if (this.aH.length() == 0 && this.aX.length() == 0) {
                        this.cu = 0;
                     } else {
                        this.cu = 2;
                     }
                  } else if (var1 == -1) {
                     this.aX = this.m();
                     this.i(57);
                     this.cu = 0;
                  } else {
                     this.a(var1, false);
                  }
                  break;
               case 70:
                  if (var1 == -7) {
                     this.c();
                     this.cu = 0;
                  } else if (var1 == -6 || var2 == 8) {
                     switch (this.cu) {
                        case 0:
                           this.a(this.A, true, 14);
                           this.i(71);
                           break label1674;
                        case 1:
                           this.a(this.A, true, 14);
                           this.i(73);
                           break label1674;
                        case 2:
                           this.k(46);
                           break label1674;
                        case 3:
                           this.k(49);
                     }
                  } else if (var2 == 6) {
                     this.cu = (this.cu + 1) % 4;
                  } else if (var2 == 1) {
                     this.cu = (this.cu + 3) % 4;
                  }
                  break;
               case 71:
               case 73:
                  if (var1 != -6 && var1 != -5) {
                     this.a(var1, false);
                  } else {
                     this.A = this.m();
                     if (this.A.length() > 0) {
                        if (this.Y == 71) {
                           this.k(45);
                        } else {
                           this.k(48);
                        }
                     } else {
                        this.i(70);
                     }
                  }
                  break;
               case 75:
                  if (var1 == -7) {
                     this.c();
                     this.cu = 3;
                  } else if (var1 != -6 && var2 != 8) {
                     this.b(var2, 3);
                  } else if (this.cu == 0) {
                     this.c(this.Y);
                     this.k(60);
                  } else if (this.cu == 1) {
                     this.c(this.Y);
                     this.k(61);
                  } else if (this.cu == 2) {
                     if (this.bG.equals("3")) {
                        this.a(EoETown.b(this.g), 10, 75, 0L);
                     } else if (this.bG.equals("4")) {
                        this.cu = 0;
                        this.by = "";
                        this.i(79);
                     }
                  }
                  break;
               case 76:
               case 78:
               case 116:
                  if (var1 == -7) {
                     this.cu = 0;
                     this.c();
                  }

                  if (var2 == 6 || var2 == 1) {
                     this.f(var2);
                  }
                  break;
               case 77:
                  if (var1 == -7) {
                     this.c();
                     this.cu = 0;
                  } else if (var1 != -6 && var2 != 8) {
                     this.b(var2, 6);
                  } else {
                     this.k(52);
                  }
                  break;
               case 79:
                  if (var1 == -7) {
                     this.cu = 2;
                     this.i(75);
                  } else if (var1 != -6 && var2 != 8) {
                     this.b(var2, 3);
                  } else if (this.cu == 0) {
                     this.a(this.by, true, 14);
                     this.i(80);
                  } else if (this.cu == 1) {
                     this.k(65);
                  } else if (this.cu == 2) {
                     this.k(69);
                  }
                  break;
               case 80:
                  if (var1 != -6 && var1 != -5) {
                     this.a(var1, false);
                  } else {
                     this.by = this.m();
                     if (this.by.length() > 0) {
                        this.k(63);
                     } else {
                        this.i(79);
                     }
                  }
                  break;
               case 81:
                  if (var1 == -7) {
                     this.cu = 1;
                     this.i(79);
                  } else if (var1 == -6 || var2 == 8) {
                     this.a(this.g(77), 10, 81, 0L);
                  }

                  if (var2 == 6 || var2 == 1) {
                     this.f(var2);
                  }
                  break;
               case 82:
                  if (var1 == -7) {
                     this.i(79);
                     this.cu = 2;
                  } else if (var1 != -6 && var2 != 8) {
                     this.b(var2, 3);
                  } else if (this.cu == 0) {
                     this.a(this.T, true, 14);
                     this.i(83);
                  } else if (this.cu == 1) {
                     this.a(this.bl, true, 3);
                     this.i(84);
                  } else if (this.cu == 2) {
                     this.k(64);
                  }
                  break;
               case 83:
                  if (var1 != -6 && var1 != -5 && var1 != -1 && var1 != -2) {
                     this.a(var1, false);
                  } else {
                     this.T = this.m();
                     if (this.T.length() == 0) {
                        this.T = this.z;
                     }

                     if (var1 != -6 && var1 != -5 && var1 != -1) {
                        this.cu = 2;
                     } else {
                        this.cu = 1;
                     }

                     this.i(82);
                  }
                  break;
               case 84:
                  if (var1 != -6 && var1 != -5 && var1 != -1 && var1 != -2) {
                     this.a(var1, false);
                  } else {
                     this.bl = this.m();
                     if (this.bl.length() == 0) {
                        this.bl = this.bz;
                     }

                     if (var1 != -6 && var1 != -5 && var1 != -2) {
                        this.cu = 0;
                     } else {
                        this.cu = 2;
                     }

                     this.i(82);
                  }
                  break;
               case 85:
                  if (var1 == -6 || var2 == 8) {
                     this.c(this.Y);
                     this.aE = this.cu + 1;
                     this.k(19);
                  } else if (var1 == -7) {
                     this.cu = 0;
                     this.c();
                  } else {
                     this.b(var2, 3);
                  }
                  break;
               case 89:
                  if (d(var1)) {
                     this.a(this.g(38), 15, this.Y, 0L);
                  } else if (var1 != -6 && var2 != 8) {
                     if (var2 != 5 && var2 != 6 && var2 != 2 && var2 != 1) {
                        if ((var1 == -7 || var1 == -8) && this.bS != 0) {
                           this.bS--;
                           this.bj[this.bS][0] = -1;
                           if (this.bj[this.bS][2] != 1) {
                              if (this.bj[this.bS][2] == 2) {
                                 this.aQ--;
                                 this.as[this.aQ] = -1;
                              }
                           } else {
                              String var13 = ((String[])this.F.elementAt(this.F.size() - 1))[2];

                              for (int var21 = 0; var21 < var13.length(); var21++) {
                                 if (var13.charAt(var21) == '_') {
                                    this.bK--;
                                 }
                              }

                              this.bd = this.bK;
                              this.ah = this.ch[this.bd];
                              this.W = this.ah;
                           }

                           this.aU = this.aU - this.bj[this.bS][1] / 10;
                           this.F.removeElementAt(this.F.size() - 1);
                           this.bj[this.bS][1] = -1;
                        }
                        break;
                     }

                     if (var2 != 2 && var2 != 1) {
                        this.cu = (this.cu + 1) % 8;
                     } else {
                        this.cu = (this.cu + 7) % 8;
                     }

                     this.repaint(this.bJ, this.bQ + 112, 128, 15);
                     return;
                  } else if (this.cu == 7) {
                     this.k = 0;
                     this.i(90);
                  } else {
                     String[][] var12;
                     if (this.bS <= 10 && (var12 = (String[][])this.bt.elementAt(this.cu)).length != 0) {
                        this.M = new int[var12.length];
                        if (var12.length <= 5) {
                           this.ba = new String[var12.length][4];
                           System.arraycopy(var12, 0, this.ba, 0, this.ba.length);
                           this.ct = false;
                        } else {
                           this.ba = new String[5][4];
                           this.aT = new String[var12.length - 5][4];
                           System.arraycopy(var12, 0, this.ba, 0, this.ba.length);
                           this.ct = true;
                           System.arraycopy(var12, 5, this.aT, 0, this.aT.length);
                        }

                        this.k = 0;
                        this.bN = 1;
                        this.i(91);
                     }
                  }
                  break;
               case 90:
                  if (var1 == -7 || var1 == -8) {
                     this.i(89);
                  } else if (var1 != -6 && var2 != 8) {
                     if (var2 == 1 || var2 == 6) {
                        this.k = (this.k + 1) % 2;
                     }
                  } else if (this.k == 0) {
                     this.a(this.g(38), 15, 89, 0L);
                  } else if (this.k == 1) {
                     this.a(this.g(39), 6, 89, 0L);
                  }
                  break;
               case 91:
                  if (var1 == -7 || var1 == -8) {
                     this.k = 0;
                     this.i(89);
                  } else if (var1 != -6 && var2 != 8) {
                     if (var2 == 6) {
                        if (this.bN == 1 && this.k >= this.ba.length - 1) {
                           if (this.ct) {
                              this.bN = 2;
                           }

                           this.k = 0;
                        } else if (this.bN == 2 && this.k >= this.aT.length - 1) {
                           this.bN = 1;
                           this.k = 0;
                        } else {
                           this.k++;
                        }
                     } else if (var2 == 1) {
                        if (this.bN == 1 && this.k <= 0) {
                           if (this.ct) {
                              this.bN = 2;
                              this.k = this.aT.length - 1;
                           } else {
                              this.k = this.ba.length - 1;
                           }
                        } else if (this.bN == 2 && this.k <= 0) {
                           this.bN = 1;
                           this.k = this.ba.length - 1;
                        } else {
                           this.k--;
                        }
                     }
                  } else if (this.bN == 1 && this.M[this.k] == 1 || this.bN == 2 && this.M[this.k + 5 - 1] == 1) {
                     this.bR = System.currentTimeMillis();
                     if (this.bN == 1) {
                        this.i = new String[]{Integer.toString((int)(this.bR - this.aA)), this.ba[this.k][0], ""};
                     } else {
                        this.i = new String[]{Integer.toString((int)(this.bR - this.aA)), this.aT[this.k][0], ""};
                     }

                     if (this.bN == 1) {
                        this.bj[this.bS][1] = Integer.parseInt(this.ba[this.k][2]);
                        this.bj[this.bS][2] = Integer.parseInt(this.ba[this.k][3]);
                     } else {
                        this.bj[this.bS][1] = Integer.parseInt(this.aT[this.k][2]);
                        this.bj[this.bS][2] = Integer.parseInt(this.aT[this.k][3]);
                     }

                     if ((this.bN != 1 || !this.ba[this.k][3].equals("2")) && (this.bN != 2 || !this.aT[this.k][3].equals("2"))) {
                        if ((this.bN != 1 || !this.ba[this.k][3].equals("1")) && (this.bN != 2 || !this.aT[this.k][3].equals("1"))) {
                           this.bN = 1;
                           this.k = 0;
                           this.bj[this.bS][0] = this.cu;
                           this.F.addElement(this.i);
                           this.aU = this.aU + this.bj[this.bS][1] / 10;
                           this.bS++;
                           this.i(89);
                        } else {
                           this.aR = new int[8];
                           this.be = 0;
                           this.i(92);
                        }
                     } else {
                        this.W = this.ah;
                        this.i(93);
                     }
                  }
                  break;
               case 92:
                  if (var1 == -6 || var2 == 8) {
                     this.d();
                  } else if (var1 == -7 || var1 == -8) {
                     this.i(89);
                     this.ah = this.ch[this.bd];

                     for (int var11 = this.bd + 1; var11 <= this.bK; var11++) {
                        this.ch[var11] = -1;
                        this.bK--;
                     }

                     this.bU = false;
                  } else if (var2 == 1) {
                     if (this.ah > 5) {
                        this.aL = this.ah - 6;
                        if (this.a(this.aL)) {
                           this.x();
                        }
                     }
                  } else if (var2 == 5) {
                     if (this.ah % 6 != 5) {
                        this.aL = this.ah + 1;
                        if (this.a(this.aL)) {
                           this.x();
                        }
                     }
                  } else if (var2 == 6) {
                     if (this.ah < 18) {
                        this.aL = this.ah + 6;
                        if (this.a(this.aL)) {
                           this.x();
                        }
                     }
                  } else if (var2 == 2 && this.ah % 6 != 0) {
                     this.aL = this.ah - 1;
                     if (this.a(this.aL)) {
                        this.x();
                     }
                  }
                  break;
               case 93:
                  if (var1 == -6 || var2 == 8) {
                     this.A();
                  } else if (var1 == -7 || var2 == -8) {
                     this.i(89);
                  } else if (var2 == 1) {
                     if (this.W >= 0 && this.W <= 5) {
                        this.aL = this.W + 18;
                     } else {
                        this.aL = this.W - 6;
                     }

                     this.W = this.aL;
                  } else if (var2 == 5) {
                     if (this.W % 6 == 5) {
                        this.aL = this.W - 5;
                     } else {
                        this.aL = this.W + 1;
                     }

                     this.W = this.aL;
                  } else if (var2 == 6) {
                     if (this.W >= 18 && this.W <= 23) {
                        this.aL = this.W - 18;
                     } else {
                        this.aL = this.W + 6;
                     }

                     this.W = this.aL;
                  } else if (var2 == 2) {
                     if (this.W % 6 == 0) {
                        this.aL = this.W + 5;
                     } else {
                        this.aL = this.W - 1;
                     }

                     this.W = this.aL;
                  }
                  break;
               case 103:
                  if (Integer.parseInt(this.f[0]) > 0) {
                     if (var1 != -6 && var2 != 8) {
                        this.b(var2, 6);
                     } else {
                        this.a(this.g(this.cu + 53), 10, 103, 0L);
                     }
                  }
                  break;
               case 104:
                  if (var1 != -6 && var2 != 8 && var1 != -7) {
                     this.b(var2, 6);
                  } else if (this.cu != 5 && var1 != -7) {
                     if (this.cu == 4) {
                        this.k(51);
                     } else {
                        this.c(104);
                        this.k(29);
                     }
                  } else {
                     if (this.bY != null) {
                        this.bY = "";
                     }

                     this.i();
                  }
                  break;
               case 110:
                  if (var1 != -6 && var2 != 8) {
                     if (var1 == -7) {
                        this.k(38);
                     } else {
                        this.b(var2, 3);
                     }
                  } else if (this.cu == 0) {
                     this.c(this.Y);
                     this.i(111);
                  } else if (this.cu == 1) {
                     this.cu = 0;
                     this.aP = 0;
                     this.c(this.Y);
                     this.i(113);
                  } else if (this.cu == 2) {
                     this.k(37);
                  }
                  break;
               case 111:
                  if (var1 == -7) {
                     this.cu = 0;
                     this.c();
                  } else if (var1 != -6 && var2 != 8) {
                     this.b(var2, 3);
                  } else {
                     this.a(this.bV[4 + this.cu], true, 16);
                     this.i(112);
                  }
                  break;
               case 112:
                  if (var1 != -6 && var1 != -5 && var1 != -1 && var1 != -2) {
                     this.a(var1, false);
                  } else {
                     this.bV[4 + this.cu] = this.m();
                     if (var1 != -2 && var1 != -6 && var1 != -5) {
                        this.cu = (this.cu + 2) % 3;
                     } else {
                        this.cu = (this.cu + 1) % 3;
                     }

                     this.i(111);
                  }
                  break;
               case 113:
                  if (var1 == -7) {
                     this.cu = 1;
                     this.c();
                  }

                  if (var1 != -6 && var2 != 8) {
                     this.b(var2, 3);
                  } else {
                     if (this.cu == 0) {
                        this.ai = "Pick greeting:";
                     } else if (this.cu == 1) {
                        this.ai = "Pick victory yell:";
                     } else if (this.cu == 2) {
                        this.ai = "Pick loser cry:";
                     }

                     this.al = "";
                     this.O = 10;
                     this.br = new String[this.O][4];
                     this.aP = this.cu;
                     this.bg = 0;

                     for (int var10 = 0; var10 < this.O; var10++) {
                        for (int var5 = 0; var5 < 4; var5++) {
                           int var6 = var10 + 149 + this.cu * 10;
                           if (var5 == 0) {
                              this.br[var10][var5] = Integer.toString(var6);
                           } else if (var5 == 2) {
                              this.br[var10][var5] = this.g(var6)[0];
                           } else {
                              this.br[var10][var5] = "";
                           }
                        }
                     }

                     this.c(this.Y);
                     this.i(114);
                     this.cu = 0;
                  }
                  break;
               case 118:
                  if (var1 == -6 || var2 == 8) {
                     this.aE = this.cu + 9;
                     this.c(this.Y);
                     this.k(41);
                  } else if (var1 == -7) {
                     this.cu = 2;
                     this.c();
                  } else {
                     this.b(var2, 4);
                  }
                  break;
               case 119:
                  if ((var1 == -6 || var2 == 8) && this.br.length > 0) {
                     this.aP = this.cu;
                     this.k = 0;
                     if (this.B == null) {
                        this.B = new String[2];
                     }

                     this.B[0] = "View";
                     this.B[1] = "Delete";
                     this.k = 0;
                     this.i(120);
                  } else if (var1 == -7) {
                     this.cu = this.aP;
                     this.c();
                     if (this.Y == 118) {
                        this.cu = this.aE - 9;
                     } else if (this.Y == 121) {
                        this.cu = this.aE - 13;
                     }
                  } else {
                     this.f(var2);
                  }
                  break;
               case 120:
                  if (var1 != -6 && var2 != 8) {
                     if (var2 == 6 || var2 == 1) {
                        this.k = (this.k + 1) % 2;
                     } else if (var1 == -7) {
                        this.cu = this.aP;
                        this.i(119);
                     }
                  } else if (this.k == 0) {
                     String var4 = this.br[this.aP][3];
                     this.a(EoETown.b(var4), 0, 119, 0L);
                  } else {
                     this.k(42);
                  }
                  break;
               case 121:
                  if (var1 == -7) {
                     this.cu = 3;
                     this.c();
                  } else if (var1 != -6 && var2 != 8) {
                     this.b(var2, 4);
                  } else {
                     this.aE = this.cu + 13;
                     this.c(this.Y);
                     this.k(41);
                  }
                  break;
               case 122:
                  if (var1 == -7) {
                     this.c();
                     this.cu = 5;
                  } else if (var1 != -6 && var2 != 8) {
                     this.b(var2, 6);
                  } else {
                     this.aE = this.cu;
                     this.c(this.Y);
                     this.k(43);
                  }
                  break;
               case 123:
                  if (var1 == -7) {
                     this.cu = 0;
                     this.c();
                  } else if (var1 == -6 || var2 == 8) {
                     this.k(44);
                  } else if (var2 == 6 || var2 == 1) {
                     this.f(var2);
                  }
            }
         }

         this.repaint();
      } catch (Throwable var9) {
         this.a("key", var9, false);
      }
   }

   private final void m(Graphics var1) {
      if (this.aI == null) {
         this.aI = EoETown.a("wait", true);
      }

      a(var1, this.aI, 0, this.bD % 6 * 13, this.aI.getWidth(), 13, 0, 1, 1, 20);
   }

   private final Image e(int var1) {
      ByteArrayOutputStream var2 = new ByteArrayOutputStream();

      for (int var3 = 0; var3 < var1; var3++) {
         String var4 = this.n();

         for (int var5 = 0; var5 < var4.length(); var5++) {
            var2.write(var4.charAt(var5));
         }

         var2.write(166);
      }

      String var6 = this.n();

      for (int var7 = 0; var7 < var6.length(); var7++) {
         var2.write(var6.charAt(var7));
      }

      return Image.createImage(var2.toByteArray(), 0, var2.size());
   }

   protected final void paint(Graphics var1) {
      Object var2 = null;

      try {
         var1.setClip(0, 0, 128, 128);
         if (this.V == null || this.V.e != 12) {
            switch (this.Y) {
               case 0:
                  EoETown.a(var1);
               case 1:
               case 5:
               case 6:
               case 8:
               case 9:
               case 10:
               case 13:
               case 16:
               case 17:
               case 19:
               case 20:
               case 21:
               case 22:
               case 23:
               case 24:
               case 25:
               case 26:
               case 27:
               case 28:
               case 29:
               case 33:
               case 34:
               case 35:
               case 36:
               case 37:
               case 38:
               case 39:
               case 49:
               case 50:
               case 51:
               case 53:
               case 55:
               case 56:
               case 61:
               case 62:
               case 63:
               case 64:
               case 65:
               case 66:
               case 67:
               case 68:
               case 69:
               case 88:
               case 100:
               case 102:
               case 105:
               case 107:
               case 108:
               case 109:
               default:
                  break;
               case 2:
                  EoETown.a(var1);
                  break;
               case 3:
                  var1.setFont(cm);
                  new c(EoETown.b("Your hero was#asleep, but says:#I will be ready#in two minutes."), 0, -1, 0L).a(var1);
                  break;
               case 4:
                  this.ab.a(var1, -1);
                  break;
               case 7:
                  this.ab.a(var1, this.cj);
                  this.m(var1);
                  break;
               case 11:
               case 12:
                  this.e(var1, "Enter Eidolon");
                  break;
               case 14:
                  this.a(var1, "Your heroes:");
                  break;
               case 15:
                  this.a(var1, "Your heroes:");
                  this.j(var1);
                  break;
               case 18:
               case 95:
                  this.m(var1);
                  break;
               case 30:
                  this.a(var1, "Create Hero:");
                  break;
               case 31:
                  this.a(var1, "Create Hero:");
                  break;
               case 32:
               case 120:
                  this.j(var1);
                  break;
               case 40:
                  this.c(var1);
                  break;
               case 41:
                  this.b(var1, "Pick a fight:");
                  break;
               case 42:
                  this.d(var1, "Hero overview:");
                  break;
               case 43:
                  this.e(var1, "Buy skills:");
                  break;
               case 44:
                  this.e(var1, "Buy magic:");
                  break;
               case 45:
                  this.d(var1, "Buy & sell:");
                  break;
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
               case 123:
                  this.a(var1, this.ai, this.al);
                  break;
               case 48:
                  this.b(var1, "Tavern");
                  break;
               case 54:
                  this.a(var1, "Pick a foe:");
                  break;
               case 57:
                  this.a(var1, "Invite friend by:");
                  break;
               case 59:
                  this.a(var1, "Invite friend by:");
                  break;
               case 60:
                  this.a(var1, "Invite friend by:");
                  break;
               case 70:
                  this.e(var1, "Manage");
                  break;
               case 71:
               case 73:
                  this.e(var1, "Manage");
                  break;
               case 75:
                  this.a(var1, this.x);
                  break;
               case 77:
                  this.d(var1, "View rankings:");
                  break;
               case 79:
                  this.a(var1, "Chief's area:");
                  break;
               case 80:
                  this.a(var1, "Chief's area:");
                  break;
               case 82:
                  this.a(var1, this.au);
                  break;
               case 83:
                  this.a(var1, this.au);
                  break;
               case 84:
                  this.a(var1, this.au);
                  break;
               case 85:
                  this.a(var1, "Choose class:");
                  break;
               case 89:
               case 92:
               case 93:
                  this.h(var1);
                  this.g(var1);
                  this.k(var1);
                  break;
               case 90:
                  this.k(var1);
                  this.d(var1);
                  break;
               case 91:
                  this.h(var1);
                  this.g(var1);
                  this.k(var1);
                  this.l(var1);
                  break;
               case 94:
               case 96:
               case 98:
               case 101:
                  if (this.cs != null) {
                     this.e(var1);
                  }
                  break;
               case 97:
                  if (this.ce != null && this.cs != null) {
                     boolean var3 = false;
                     boolean var4 = false;
                     int var5 = (int)(System.currentTimeMillis() - this.l);
                     int var6 = this.ce[0];
                     int var7 = this.ce[1];
                     int var8 = this.ce[4] * var5 >> 16;
                     int var9 = this.ce[5] * var5 >> 16;
                     if (Math.abs(var8) >= Math.abs(this.ce[2] - var6)) {
                        var6 = this.ce[2];
                        var3 = true;
                     } else {
                        var6 += var8;
                     }

                     if (Math.abs(var9) >= Math.abs(this.ce[3] - var7)) {
                        var7 = this.ce[3];
                        var4 = true;
                     } else {
                        var7 += var9;
                     }

                     this.N = var3 && var4;
                     this.h(var1);
                     this.i(var1);
                     a(var1, 5327691, "");
                     if (this.aN == null) {
                        this.aN = EoETown.a("ammu", true);
                     }

                     a(var1, this.aN, Integer.parseInt(this.cs[12]) * 10, 0, 10, this.aN.getHeight(), 0, 1 + var6, 3 + var7, 20);
                  }
                  break;
               case 99:
                  if (this.cs != null) {
                     this.f(var1);
                  }
                  break;
               case 103:
                  this.d(var1, "Points left:".concat(this.f[0]));
                  break;
               case 104:
                  this.d(var1, "Battle reports:");
                  break;
               case 110:
                  this.a(var1, "Customize:");
                  break;
               case 111:
                  this.a(var1, "Write taunts:");
                  break;
               case 112:
                  this.a(var1, "Write taunts:");
                  break;
               case 113:
                  this.a(var1, "Pick mottos:");
                  break;
               case 118:
                  this.e(var1, "Hero skills:");
                  break;
               case 121:
                  this.e(var1, "Hero spells:");
                  break;
               case 122:
                  this.d(var1, "Equip");
            }
         }

         if (this.V != null) {
            var1.setFont(cm);
            this.V.a(var1);
         }

         if (this.V == null
            && this.Y != 88
            && this.Y != 89
            && this.Y != 92
            && this.Y != 93
            && this.Y != 91
            && this.Y != 101
            && this.Y != 97
            && this.Y != 98
            && this.Y != 96
            && this.Y != 99
            && this.Y != 94
            && this.Y != 95
            && this.Y != 18) {
            if (this.cc == 1 && (this.bD % 2 == 0 || System.currentTimeMillis() - this.aF > 6000L)) {
               if (this.bs == null) {
                  this.bs = EoETown.a("challenge", true);
               }

               var1.drawImage(this.bs, 49, 117, 20);
            }

            if (this.bZ == 1 && (this.bD % 2 == 0 || System.currentTimeMillis() - this.bX > 6000L)) {
               if (this.bI == null) {
                  this.bI = EoETown.a("mail", true);
               }

               var1.drawImage(this.bI, 67, 117, 20);
            }
         }

         if (this.s != null && this.s.isAlive()) {
            this.m(var1);
         }

         this.p = false;
      } catch (Throwable var10) {
         if (!this.p) {
            this.repaint();
         }

         this.p = true;
      }
   }

   private final void g() {
      if (this.bH != null) {
         this.n = null;
         this.aN = null;
         this.bi = null;
         this.aB = null;
         this.J = null;
         this.bH = null;
         System.gc();

         try {
            Thread.sleep(500L);
            return;
         } catch (InterruptedException var2) {
         }
      }
   }

   private final void b(Graphics var1) {
      this.g();
      if (this.v == null) {
         this.v = EoETown.a("background", true);
      }

      var1.drawImage(this.v, 0, 0, 20);
      a(var1, this.v, 0, 0, this.v.getWidth(), this.v.getHeight(), 2, this.v.getWidth(), 0, 20);
   }

   private final void c(Graphics var1, String var2) {
      var1.setColor(0);
      var1.setFont(bO);
      var1.drawString("" + var2, 64, 12 - (bO.getHeight() >> 1), 17);
   }

   private final void d(Graphics var1, String var2) {
      String[] var3 = null;
      if (var2 == "Hero overview:") {
         var3 = new String[]{"Stats", "Weapons", "Skills", "Spells", "Custom", "Equip"};
      } else if (var2 == "Battle reports:") {
         var3 = new String[]{"Stats", "Weapons", "Skills", "Spells", "+Friend", "Town"};
      } else if (var2 == "Equip") {
         var3 = new String[]{"Melee", "Trap", "Bow", "Bombs", "Armour", "Magic"};
      } else if (var2 == "Buy & sell:") {
         var3 = new String[]{"Melee", "Bow", "Bombs", "Trap", "Armour", "Sell"};
      } else if (var2 == "View rankings:") {
         var3 = EoETown.b("Respect#Level#Clan#Contest#Hotshot#Friends");
      } else if (var2 != null && var2.equals("Points left:".concat(this.f[0]))) {
         var3 = new String[6];
         System.arraycopy(this.f, 1, var3, 0, 6);
         this.aY = new int[6];
         String[] var4 = EoETown.b("St:#In:#Dx:#To:#Wi:#Sp:");

         for (int var5 = 0; var5 < 6; var5++) {
            int var6;
            if ((var6 = Integer.parseInt(var3[var5])) >= 15 && var6 <= 45) {
               this.aY[var5] = 3;
            } else if (var6 >= 48 && var6 <= 76) {
               this.aY[var5] = 2;
            } else if (var6 >= 78 && var6 <= 98) {
               this.aY[var5] = 1;
            }

            var3[var5] = var4[var5] + var3[var5] + "(" + this.aY[var5] + ")";
         }
      }

      this.b(var1);
      if (this.U == null) {
         this.U = EoETown.a("divider", true);
      }

      for (int var7 = 0; var7 < 3; var7++) {
         var1.drawImage(this.U, 64, aV[var7], 17);
      }

      this.c(var1, var2);
      var1.setFont(cm);
      if (var3 != null) {
         int var8 = var3.length;

         while (--var8 >= 0) {
            var1.setColor(var8 == this.cu ? 16711680 : 0);
            if (var8 < 3) {
               var1.drawString(var3[var8], 39, aV[var8] + 12 - ci, 17);
            } else {
               var1.drawString(var3[var8], 89, aV[var8 - 3] + 12 - ci, 17);
            }
         }
      }
   }

   private final void e(Graphics var1, String var2) {
      String[] var3 = null;
      if (var2 == "Buy magic:" || var2 == "Hero spells:") {
         var3 = EoETown.b("Spectral#Guardian#Bane#Spirit");
      } else if (var2 == "Enter Eidolon") {
         if (this.bC.length() > 0 && this.ap.length() > 0) {
            var3 = new String[]{this.bC, this.ap, "Login", "Register"};
         } else if (this.bC.length() > 0) {
            var3 = new String[]{this.bC, ">Password", "Login", "Register"};
         } else if (this.ap.length() > 0) {
            var3 = new String[]{">Nickname", this.ap, "Login", "Register"};
         } else {
            var3 = new String[]{">Nickname", ">Password", "Login", "Register"};
         }
      } else if (var2 == "Buy skills:" || var2 == "Hero skills:") {
         var3 = EoETown.b("Close combat#Ranged attack#Defence#Move");
      } else if (var2 == "Manage") {
         if (this.A.length() > 0 && this.cu == 0) {
            var3 = new String[]{this.A, ">Ban a hero", "-Friend", "-Ban"};
         } else if (this.A.length() > 0 && this.cu == 1) {
            var3 = new String[]{">Add a friend", this.A, "-Friend", "-Ban"};
         } else {
            var3 = new String[]{">Add a friend", ">Ban a hero", "-Friend", "-Ban"};
         }
      }

      this.b(var1);
      if (this.U == null) {
         this.U = EoETown.a("divider", true);
      }

      var1.drawImage(this.U, 64, aV[2], 17);
      this.c(var1, var2);
      var1.setFont(cm);
      if (var3 != null) {
         int var4 = var3.length;

         while (--var4 >= 0) {
            var1.setColor(var4 == this.cu ? 16711680 : 0);
            if (var4 != 0 || this.Y != 71 && (this.Y != 12 || this.cu != 0)) {
               if (var4 != 1 || this.Y != 73 && (this.Y != 12 || this.cu != 1)) {
                  if (var4 < 2) {
                     var1.drawString(var3[var4], 64, aV[var4] + 12 - ci, 17);
                  } else if (var4 == 2) {
                     var1.drawString(var3[var4], 39, aV[var4] + 12 - ci, 17);
                  } else if (var4 == 3) {
                     var1.drawString(var3[var4], 89, aV[2] + 12 - ci, 17);
                  }
               } else {
                  this.a(var1, 1);
               }
            } else {
               this.a(var1, 0);
            }
         }
      }
   }

   private final void b(Graphics var1, String var2) {
      String[] var3 = null;
      if (var2 == "Pick a fight:") {
         var3 = new String[]{"Get random foe", "Friend", "Gladiator", "Special", "Invite"};
      } else if (var2 == "Tavern") {
         var3 = EoETown.b("Inbox#Write#Friends#My clan#Ranking");
      }

      this.b(var1);
      if (this.U == null) {
         this.U = EoETown.a("divider", true);
      }

      var1.drawImage(this.U, 64, aV[1], 17);
      var1.drawImage(this.U, 64, aV[2], 17);
      this.c(var1, var2);
      var1.setFont(cm);
      if (var3 != null) {
         int var4 = var3.length;

         while (--var4 >= 0) {
            var1.setColor(var4 == this.cu ? 16711680 : 0);
            if (var4 == 0) {
               var1.drawString(var3[var4], 64, aV[var4] + 12 - ci, 17);
            } else if (var4 != 1 && var4 != 2) {
               var1.drawString(var3[var4], 89, aV[var4 - 2] + 12 - ci, 17);
            } else {
               var1.drawString(var3[var4], 39, aV[var4] + 12 - ci, 17);
            }
         }
      }
   }

   private final void a(Graphics var1, String var2) {
      String[] var3 = null;
      if (var2 == "Create Hero:") {
         if (this.ca.length() != 0 && this.bP != 0) {
            var3 = new String[]{this.ca, this.bP == 'f' ? "Female" : "Male", "Create"};
         } else if (this.ca.length() != 0) {
            var3 = new String[]{this.ca, "Gender", "Create"};
         } else if (this.bP != 0) {
            var3 = new String[]{"Hero name?", this.bP == 'f' ? "Female" : "Male", "Create"};
         } else {
            var3 = new String[]{"Hero name?", "Gender", "Create"};
         }
      } else if (var2 == "Enter Eidolon") {
         if (this.bC.length() > 0 && this.ap.length() > 0) {
            var3 = new String[]{this.bC, this.ap, "Login"};
         } else if (this.bC.length() > 0) {
            var3 = new String[]{this.bC, ">Password", "Login"};
         } else if (this.ap.length() > 0) {
            var3 = new String[]{">Nickname", this.ap, "Login"};
         } else {
            var3 = new String[]{">Nickname", ">Password", "Login"};
         }
      } else if (var2 == "Your heroes:") {
         if (this.K[0].length() > 0 && this.K[1].length() > 0) {
            var3 = new String[]{this.K[0], this.K[1], "Delete Hero"};
         } else if (this.K[0].length() > 0) {
            var3 = new String[]{this.K[0], "Create Hero", "Delete Hero"};
         } else if (this.K[1].length() > 0) {
            var3 = new String[]{"Create Hero", this.K[1], "Delete Hero"};
         } else {
            var3 = new String[]{"Create Hero", "Create Hero", "Delete Hero"};
         }
      } else if (var2 == "Pick a foe:" && this.aW != null) {
         int var8 = (var3 = new String[this.aW.length]).length;

         while (--var8 >= 0) {
            var3[var8] = this.aW[var8][2];
         }
      } else if (var2 == "Customize:") {
         var3 = new String[]{"Taunts", "Mottos", "Head: " + this.bV[3]};
      } else if (var2 == "Write taunts:") {
         var3 = new String[]{this.bV[4], this.bV[5], this.bV[6]};
      } else if (var2 == "Pick mottos:") {
         var3 = new String[]{"Greeting", "Victory yell", "Loser cry"};
      } else if (var2 == "Invite friend by:") {
         String var4 = "";
         if (this.aX.length() > 0) {
            if (this.aX.length() > 12) {
               var4 = this.aX.substring(0, 12);
            } else {
               var4 = this.aX;
            }
         }

         if (this.aH.length() > 0 && this.aX.length() > 0) {
            var3 = new String[]{this.aH, var4, "Send invitation"};
         } else if (this.aH.length() > 0) {
            var3 = new String[]{this.aH, ">or email", "Send invitation"};
         } else if (this.aX.length() > 0) {
            var3 = new String[]{">phone no.", var4, "Send invitation"};
         } else {
            var3 = new String[]{">phone no.", ">or email", "Send invitation"};
         }
      } else if (var2 == "Choose class:") {
         var3 = new String[]{"Sword", "Hammer", "Axe"};
      } else if (this.x != null && var2 != null && var2.equals(this.x)) {
         var3 = new String[]{"Clan stats", "Clan members", this.bT};
      } else if (var2 == "Chief's area:") {
         if (this.by != null && this.by.length() != 0) {
            var3 = new String[]{this.by, "Kick hero", "Edit clan"};
         } else {
            var3 = new String[]{">Invite hero", "Kick hero", "Edit clan"};
         }
      } else if (this.au != null && var2 != null && var2.equals(this.au)) {
         var3 = new String[]{this.T, this.bl, "Update"};
      }

      this.b(var1);
      this.c(var1, var2);
      var1.setFont(cm);
      if (var3 != null) {
         for (int var9 = 0; var9 < var3.length; var9++) {
            var1.setColor(var9 == this.cu ? 16711680 : 0);
            if (var9 != 0 || this.cu != 0 || this.Y != 31 && this.Y != 112 && this.Y != 59 && this.Y != 83 && this.Y != 80 && this.Y != 12) {
               if (var9 != 1 || this.cu != 1 || this.Y != 112 && this.Y != 84 && this.Y != 12) {
                  if (var9 == 1 && this.cu == 1 && this.Y == 60) {
                     int var5;
                     if ((var5 = this.ak.length()) <= 11) {
                        this.a(var1, 1);
                     } else {
                        StringBuffer var6 = new StringBuffer(this.ak.toString());

                        for (int var7 = 0; var7 < var5 - 11; var7++) {
                           this.ak.deleteCharAt(0);
                        }

                        this.a(var1, 1);
                        this.ak = var6;
                     }
                  } else if (var9 == 2 && this.cu == 2 && this.Y == 112) {
                     this.a(var1, 2);
                  } else {
                     var1.drawString(var3[var9], 64, aV[var9] + 12 - ci, 17);
                  }
               } else {
                  this.a(var1, 1);
               }
            } else {
               this.a(var1, 0);
            }
         }
      }
   }

   private final void a(Graphics var1) {
      int var2;
      if ((var2 = 72 * this.aG / this.af) > 72) {
         var2 = 72;
      }

      var1.setColor(5327691);
      var1.fillRect(105 - var2, 17, var2, 8);
   }

   private final void k(Graphics var1) {
      int var2 = 72 * this.aU / 72;
      var1.setColor(8825809);
      var1.fillRect(105 - var2, 6, var2, 4);
   }

   private final void b(Graphics var1, int var2) {
      int var3 = 72 * var2 / 720;
      var1.setColor(2219775);
      var1.fillRect(33, 10, 72, 4);
      var1.setColor(15964948);
      var1.fillRect(33, 10, var3, 4);
   }

   private final void g(Graphics var1) {
      if (this.bj != null) {
         if (this.Y == 92) {
            this.b(var1, this.bj[this.bS][1] * this.be);
         } else if (this.Y == 93) {
            this.b(var1, this.bj[this.bS][1]);
         }

         var1.setColor(51200);

         for (int var2 = 1; var2 <= this.bK; var2++) {
            if (this.ch[var2] != -1) {
               var1.fillRect(h[this.ch[var2]][0] + 3, h[this.ch[var2]][1] + 16, 6, 4);
            }
         }

         var1.setColor(0);

         for (int var4 = 0; var4 < this.aQ; var4++) {
            var1.fillRect(h[this.as[var4]][0] + 3, h[this.as[var4]][1] + 16, 6, 4);
         }

         if (this.Y != 92 && this.Y != 93) {
            var1.setColor(51200);
            var1.fillRect(h[this.aK][0] + 3, h[this.aK][1] + 16, 6, 4);
         } else {
            if (this.Y == 92) {
               var1.setColor(51200);
               var1.fillRect(h[this.ch[0]][0] + 3, h[this.ch[0]][1] + 16, 6, 4);
            } else {
               var1.setColor(51200);
               var1.drawRect(h[this.ah][0] + 3, h[this.ah][1] + 16, 6, 4);
               var1.setColor(0);
               var1.fillRect(h[this.W][0] + 3, h[this.W][1] + 16, 6, 4);
            }

            var1.setColor(13107200);
            var1.drawRect(h[this.ae][0] + 3, h[this.ae][1] + 16, 6, 4);
         }

         if (this.Y != 92 && this.Y != 93) {
            this.i(var1);
         } else {
            int var5 = this.cg.length;

            while (--var5 >= 0) {
               this.a(var1, this.cg[var5][1] - 1, h[this.cg[var5][0]][0], h[this.cg[var5][0]][1]);
            }
         }

         byte var6 = 4;

         for (int var3 = 0; var3 < this.bj.length; var3++) {
            if (this.bj[var3][0] != -1) {
               a(var1, this.bH, 3 + this.bj[var3][0] * 16, 114, 10, 11, 0, var6, 99, 20);
               var6 += 11;
            }
         }

         var1.setColor(16711680);
         var1.drawRect(1 + 16 * this.cu, 112, 13, 14);
      }
   }

   private final void h(Graphics var1) {
      if (this.bH == null) {
         this.bH = EoETown.a("battlefield", true);
      }

      var1.drawImage(this.bH, 0, 0, 20);
      this.a(var1);
   }

   private final void e(Graphics var1) {
      this.h(var1);
      this.i(var1);
      if (this.cs[8].length() > 0) {
         a(var1, this.cs[9].equals("0") ? 65344 : 16724016, this.cs[8]);
      } else {
         a(var1, 5327691, "");
      }
   }

   private static final void a(Graphics var0, int var1, String var2) {
      var0.setColor(var1);
      var0.fillRect(0, 112, 128, 16);
      var0.setColor(0);
      var0.setFont(R);
      var0.drawString(var2, 2, 121 - ci, 20);
   }

   private final void f(Graphics var1) {
      if (this.cs[7].length() > 0) {
         int var2 = Integer.parseInt(this.cs[7]);
         boolean var3 = this.cs[9].equals("0") && var2 >= 141 || this.cs[9].equals("1") && var2 < 141;
         String var4 = this.g(var2)[0];
         if (var2 >= 141 && var2 <= 144 || var2 == 132) {
            var4 = var4 + "  " + this.cs[6];
            this.a(var1);
         }

         a(var1, var3 ? 65344 : 16724016, var4);
      }
   }

   private final void a(Graphics var1, int var2, int var3, int var4) {
      if (this.n == null) {
         this.n = EoETown.a("obstacle", true);
      }

      a(var1, this.n, var2 * 12, 0, 12, this.n.getHeight(), 0, var3 + 1, var4 + 0, 20);
   }

   private final void a(Graphics var1, int[][] var2, boolean var3) {
      int var4 = var2[0][4];
      if (this.J == null) {
         this.J = EoETown.a("torso", true);
      }

      int var5 = -var2[1][0];

      int var6;
      for (var6 = -var2[1][1]; var5 + 16 > this.J.getWidth(); var6 += 14) {
         var5 -= this.J.getWidth();
      }

      a(var1, this.J, var5, var6, 16, 14, var4, var2[1][2], var2[1][3], 20);
      if (!this.H && this.aB == null) {
         this.aB = EoETown.a("legs", false);
         if (this.aB == null) {
            this.H = true;
         }
      }

      if (this.aB != null) {
         a(var1, this.aB, -var2[2][0], -var2[2][1], 12, this.aB.getHeight(), var4, var2[2][2], var2[2][3], 20);
      }

      if (this.Y == 94 || this.Y == 96 || this.Y == 97 || this.Y == 98 || this.Y == 99) {
         if (this.bi == null) {
            this.bi = EoETown.a("weapons", true);
         }

         a(var1, this.bi, -var2[3][0], -var2[3][1], 13, this.bi.getHeight(), var4, var2[3][2], var2[3][3], 20);
      }

      if (var3) {
         if (this.m != null) {
            a(var1, this.m, -var2[0][0], -var2[0][1], 7, this.m.getHeight(), var4, var2[0][2], var2[0][3], 20);
            return;
         }
      } else if (this.am != null) {
         a(var1, this.am, -var2[0][0], -var2[0][1], 7, this.am.getHeight(), var4, var2[0][2], var2[0][3], 20);
      }
   }

   private final void i(Graphics var1) {
      for (int var2 = 0; var2 <= 24; var2++) {
         if (var2 == this.aK) {
            this.a(var1, this.aD, true);
         } else if (var2 == this.ae) {
            this.a(var1, this.a, false);
         } else {
            int var3 = this.cg.length;

            while (--var3 >= 0) {
               if (var2 == this.cg[var3][0]) {
                  this.a(var1, this.cg[var3][1] - 1, h[this.cg[var3][0]][0], h[this.cg[var3][0]][1]);
               }
            }
         }
      }
   }

   private final void j(Graphics var1) {
      for (int var2 = 0; var2 < this.B.length; var2++) {
         if (var2 == this.k) {
            var1.setColor(16777215);
         } else {
            var1.setColor(16777130);
         }

         var1.fillRect(14, 2 + var2 * 13, 100, 13);
      }

      var1.setFont(cm);

      for (int var3 = 0; var3 < this.B.length; var3++) {
         var1.setColor(var3 == this.k ? 16711680 : 0);
         var1.drawString(var3 == this.k ? '>' + this.B[var3] + '<' : this.B[var3], 16, 3 + var3 * 13 + 2, 20);
      }

      var1.setColor(0);
      var1.drawRect(13, 1, 101, this.B.length * 13 + 1);
   }

   private final void d(Graphics var1) {
      String[] var2 = EoETown.b("End turn#Flee fight");
      var1.setFont(cm);
      var1.setColor(16777130);
      var1.fillRect(14, 29, 100, 26);

      for (int var3 = 0; var3 < var2.length; var3++) {
         if (var3 == this.k) {
            var1.setColor(16777215);
            var1.fillRect(14, 29 + var3 * 13, 100, 13);
            var1.setColor(16711680);
         } else {
            var1.setColor(0);
         }

         var1.drawString(var3 == this.k ? '>' + var2[var3] + '<' : var2[var3], 16, 30 + var3 * 13 + 2, 20);
      }

      var1.setColor(0);
      var1.drawRect(13, 28, 101, 27);
   }

   private final void l(Graphics var1) {
      String[][] var2;
      if (this.bN == 1) {
         var2 = this.ba;
      } else {
         var2 = this.aT;
      }

      this.k(var1);
      var1.setFont(cm);
      var1.setColor(16777130);
      var1.fillRect(14, 29, 100, var2.length * 13);
      var1.setColor(16777215);
      var1.fillRect(14, 29 + this.k * 13, 100, 13);

      for (int var3 = 0; var3 < var2.length; var3++) {
         this.b(var1, Integer.parseInt(var2[this.k][2]));
         if (72000 - this.aU * 1000 > Integer.parseInt(var2[var3][2]) * 100) {
            var1.setColor(var3 == this.k ? 16711680 : 0);
            if (this.bN == 1) {
               this.M[var3] = 1;
            } else {
               this.M[var3 + 5 - 1] = 1;
            }
         } else {
            var1.setColor(11513775);
            if (this.bN == 1) {
               this.M[var3] = 0;
            } else {
               this.M[var3 + 5 - 1] = 0;
            }
         }

         var1.drawString(var3 == this.k ? '>' + var2[var3][1] + '<' : var2[var3][1], 16, 30 + var3 * 13 + 2, 20);
      }

      var1.setColor(0);
      if (this.bN == 1 && this.ct) {
         var1.drawChar('V', 106, 83, 20);
      } else if (this.bN == 2) {
         var1.drawChar('Λ', 106, 27, 20);
      }

      var1.drawRect(13, 28, 101, var2.length * 13 + 1);
   }

   private final void c(Graphics var1) {
      this.g();
      if (this.L == null) {
         this.L = EoETown.a("town", true);
      }

      var1.drawImage(this.L, 0, 0, 20);
      if (this.ar == null) {
         this.ar = EoETown.a("cursor", true);
      }

      var1.drawImage(this.ar, bL[this.cu][0], bL[this.cu][1] + 3 * (this.bD % 3), 20);
      if (this.aa < 10) {
         boolean var2 = false;
         String var3 = aM[this.cu];
         int var4 = R.stringWidth(var3) + 7;
         var1.setColor(16777215);
         int var5 = R.getHeight();
         var1.fillRect(64 - (var4 >> 1), 2, var4, var5 + 3);
         var1.setColor(0);
         var1.drawRect(64 - (var4 >> 1), 2, var4, var5 + 3);
         var1.setFont(R);
         var1.drawString(var3, 64, 6, 17);
      }
   }

   final void a(String var1, boolean var2, int var3) {
      this.S = var2;
      this.D = var3;
      this.ak = null;
      this.ak = new StringBuffer(var1);
      this.bu = false;
      this.aO = 0;
   }

   final String m() {
      if (this.ak != null) {
         if (this.bB > 0) {
            this.ak.append(this.bB);
            this.bB = 0;
         }

         if (this.S && this.ak.length() > 0) {
            this.ak.setCharAt(0, Character.toUpperCase(this.ak.charAt(0)));
         }

         return this.ak.toString();
      } else {
         return "";
      }
   }

   final void t() {
      this.bu = !this.bu;
      if (this.aO > 0) {
         this.aO--;
      }
   }

   final void a(int var1, boolean var2) {
      if (var1 != -7 && var1 != -8) {
         if (this.ak.length() < this.D || this.ak.length() <= this.D && this.aO > 0 && var1 == this.bk) {
            String var3 = "";
            if (var2) {
               if (var1 >= 48 && var1 <= 57) {
                  var3 = "" + (char)var1;
               }
            } else if (var1 == 42) {
               var3 = "@%&/()=+*";
            } else if (var1 >= 48 && var1 <= 57) {
               var3 = bo[var1 - 48];
            }

            try {
               int var4;
               if (var1 == this.bk && this.aO > 0 && !var2) {
                  if ((var4 = var3.indexOf(this.bB) + 1) > var3.length() - 1) {
                     var4 = 0;
                  }
               } else {
                  if (this.bB > 0) {
                     this.ak.append(this.bB);
                     this.bB = 0;
                  }

                  var4 = 0;
               }

               if (var3.length() > 0 && this.ak.length() < this.D) {
                  this.bB = var3.charAt(var4);
               } else {
                  this.bB = 0;
               }
            } catch (IndexOutOfBoundsException var6) {
               this.bB = 0;
            }

            this.bk = var1;
            this.aO = 2;
         }
      } else {
         if (this.bB > 0) {
            this.bB = 0;
            return;
         }

         if (this.ak.length() > 0) {
            this.ak.setLength(this.ak.length() - 1);
            return;
         }
      }
   }

   final void a(Graphics var1, int var2) {
      Font var3 = var1.getFont();
      String var4;
      if (this.ak == null) {
         var4 = "";
      } else {
         var4 = this.ak.toString();
      }

      if (this.bB > 0) {
         var4 = var4 + this.bB;
      }

      if (this.S && var4.length() > 0) {
         var4 = Character.toUpperCase(var4.charAt(0)) + var4.substring(1);
      }

      int var5 = var3.stringWidth(var4);
      var1.setColor(0);
      var1.setStrokeStyle(0);
      if (this.bu && this.aO == 0) {
         var1.drawLine(20 + var5, aV[var2] + 10 - 6, 20 + var5, aV[var2] + 10 + 6);
      }

      var1.drawString(var4, 20, aV[var2] + 12 - ci, 20);
   }

   private final void k(int var1) {
      this.s = new d(this, var1);
   }

   final void a(int var1, String var2) {
      this.cv = null;
      this.bw = null;
      this.s = null;
      if (var2.equals("0")) {
         if (var1 == 2) {
            this.a();
         }
      } else if (this.b(var1, var2)) {
         switch (var1) {
            case 2:
               if (this.bw.equals("1")) {
                  this.j(2);
               } else if (this.bw.equals("2")) {
                  this.a(EoETown.b(this.n()));
                  this.i(5);
               } else if (this.bw.equals("3")) {
                  this.a(EoETown.b(this.n()), 12, -1, 0L);
               }
               break;
            case 3:
               if (this.bw.equals("1")) {
                  this.j(3);
               } else if (this.bw.equals("0")) {
                  this.a(EoETown.b(this.n()), 0, 11, 0L);
               } else if (this.bw.equals("2")) {
                  this.a(EoETown.b(this.n()), 10, 11, 0L);
               } else if (this.bw.equals("3")) {
                  this.a(EoETown.b(this.n()), 12, -1, 0L);
               }
               break;
            case 4:
               if (this.bw.equals("1")) {
                  this.j(3);
               } else if (this.bw.equals("0")) {
                  this.a(EoETown.b(this.n()), 0, 11, 0L);
               }
               break;
            case 5:
               if (this.bw.equals("1")) {
                  this.j(2);
               } else if (this.bw.equals("3")) {
                  this.a(EoETown.b(this.n()), 12, -1, 0L);
               }
               break;
            case 6:
               if (this.bw.equals("1")) {
                  this.q();
                  this.cu = 0;
               }
               break;
            case 7:
               if (this.bw.equals("0")) {
                  this.d = (String)this.cv.elementAt(0);
                  this.cv.removeElementAt(0);
                  this.ca = this.d;
                  this.a(this.g(6), 0, 30, 0L);
               } else if (this.bw.equals("1")) {
                  if (this.K[0].length() > 0) {
                     this.K[1] = this.ca;
                  } else {
                     this.K[0] = this.ca;
                  }

                  this.q();
               }
               break;
            case 8:
               if (this.bw.equals("1")) {
                  this.cu = 0;
                  this.K[this.k] = "";
                  this.i(14);
               }
               break;
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
            case 65:
               if (this.bw.equals("1")) {
                  this.y();
                  if (var1 == 40) {
                     this.i(117);
                  } else if (var1 == 19) {
                     this.i(86);
                  } else if (var1 == 21) {
                     this.i(87);
                  } else if (var1 == 9) {
                     this.i(52);
                  } else if (var1 == 29) {
                     this.i(106);
                  } else if (var1 == 37) {
                     this.i(115);
                  } else if (var1 == 39) {
                     this.i(116);
                  } else if (var1 == 41) {
                     this.i(119);
                  } else if (var1 == 46) {
                     this.c(70);
                     this.i(72);
                  } else if (var1 == 49) {
                     this.c(70);
                     this.i(74);
                  } else if (var1 == 52) {
                     this.c(this.Y);
                     this.i(78);
                  } else if (var1 == 55 || var1 == 56) {
                     this.i(58);
                  } else if (var1 == 53) {
                     this.i(47);
                  } else if (var1 == 60 || var1 == 61) {
                     this.i(76);
                  } else if (var1 == 65) {
                     this.c(this.Y);
                     this.i(81);
                  }
               }
               break;
            case 10:
               this.aW = new String[this.cv.size() / 4][4];

               for (int var27 = 0; var27 < this.aW.length; var27++) {
                  for (int var31 = 0; var31 < 4; var31++) {
                     this.aW[var27][var31] = this.n();
                  }
               }

               this.i(54);
               this.cu = 0;
               break;
            case 11:
               if (this.bw.equals("1")) {
                  this.a(EoETown.b(this.n()), 0, 41, 0L);
               }
               break;
            case 12:
               if (this.bw.equals("1")) {
                  this.j(12);
               }
               break;
            case 13:
               if (this.bw.equals("0")) {
                  this.a(new String[]{"No mail."}, 0, 48, 0L);
               } else if (this.bw.equals("1")) {
                  this.cf = "6";
                  this.av = Integer.parseInt(this.n());
                  this.bv = new String[this.av][3];

                  for (int var26 = 0; var26 < this.av; var26++) {
                     for (int var30 = 0; var30 < 3; var30++) {
                        this.bv[var26][var30] = this.n();
                     }
                  }

                  if (this.av >= 15) {
                     this.a(this.g(30), 0, 66, 3000L);
                  } else {
                     this.i(66);
                  }
               }
               break;
            case 14:
               if (this.bw.equals("1")) {
                  this.G = this.n();
                  this.ag = this.n();
                  this.i(65);
                  this.ab.c();
               }
               break;
            case 15:
               if (this.bw.equals("1")) {
                  this.cf = "6";
                  this.ac = Integer.parseInt(this.n());
                  this.bx = new String[this.ac];

                  for (int var25 = 0; var25 < this.ac; var25++) {
                     this.bx[var25] = this.n();
                  }

                  this.i(68);
               }
            case 16:
            case 54:
            case 57:
            case 58:
            case 59:
            case 62:
            default:
               break;
            case 17:
               if (this.bw.equals("1")) {
                  this.bc = true;
                  this.i(65);
                  this.ab.a(this.bv);
               }
               break;
            case 18:
               this.i(48);
               this.cf = "4";
               break;
            case 20:
               if (this.bw.equals("0")) {
                  this.a(EoETown.b(this.n()), 1, 86, 0L);
               } else if (this.bw.equals("1")) {
                  this.al = this.n();
                  this.a(this.g(197), 1, 86, 0L);
               }
               break;
            case 22:
               if (this.bw.equals("1")) {
                  this.y();
                  this.i(87);
               }
               break;
            case 23:
               if (this.ao != 'n') {
                  if (this.bw.equals("0")) {
                     this.a(this.g(111));
                  } else {
                     this.o();
                     this.i(88);
                  }
               }
               break;
            case 24:
               int[] var24 = new int[]{102, 103, 101, 100, 108};
               this.a(this.g(var24[Integer.parseInt(this.bw)]));
               break;
            case 25:
               this.F = new Vector();
               if (this.af == -1) {
                  this.af = Integer.parseInt((String)this.cv.elementAt(0));
                  this.aG = 0;
               }

               this.cl = Integer.parseInt((String)this.cv.elementAt(7));
               this.cg = new int[this.cl][2];

               for (int var28 = 0; var28 < this.cl; var28++) {
                  this.cg[var28][0] = Integer.parseInt((String)this.cv.elementAt(8 + var28 * 2));
                  this.cg[var28][1] = Integer.parseInt((String)this.cv.elementAt(9 + var28 * 2));
               }

               this.bt = new Vector();
               int var7 = Integer.parseInt((String)this.cv.elementAt(7)) * 2 + 8;
               int var8 = Integer.parseInt((String)this.cv.elementAt(var7));

               for (int var29 = 0; var29 < 7; var29++) {
                  this.a(var7 + 1, var8);
                  if (var29 + 1 < 7) {
                     var7 = var7 + 4 * var8 + 1;
                     var8 = Integer.parseInt((String)this.cv.elementAt(var7));
                  }
               }

               this.aU = 0;
               this.W = Integer.parseInt((String)this.cv.elementAt(2));
               this.ah = this.W;
               this.bd = 0;
               this.ch = new int[]{-1, -1, -1, -1, -1, -1, -1, -1};
               this.ch[0] = this.ah;
               this.bK = 0;
               if (this.as == null) {
                  this.as = new int[]{-1, -1, -1, -1, -1, -1, -1, -1, -1, -1};
               }

               this.aQ = 0;
               this.ae = Integer.parseInt((String)this.cv.elementAt(5));
               this.aK = this.W;
               this.a = new int[4][4];
               this.aD = new int[4][4];
               this.aw = (String)this.cv.elementAt(6);
               this.b(this.aw);
               this.a(this.aw, this.ae, this.a, 0);
               this.y = (String)this.cv.elementAt(3);
               this.b(this.y);
               this.a(this.y, this.aK, this.aD, 0);
               this.bj = new int[][]{
                  {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}
               };
               this.bS = 0;
               this.cu = 0;
               String var9 = (String)this.cv.elementAt(1);
               String var10 = (String)this.cv.elementAt(4);
               if (this.ck != null && (this.ck.equals(var9) || this.aC.equals(var10))) {
                  if (!this.ck.equals(var9)) {
                     this.ck = var9;
                     this.I = "1";
                     this.k(70);
                  } else if (!this.aC.equals(var10)) {
                     this.aC = var10;
                     this.I = "2";
                     this.k(70);
                  } else {
                     this.c = true;
                  }
               } else {
                  this.ck = var9;
                  this.aC = var10;
                  this.I = "3";
                  this.k(70);
               }
               break;
            case 26:
               this.i(95);
               this.p();
               if (this.bw.equals("1")) {
                  if (this.Z != null) {
                     this.Z.a();
                  }

                  this.Z = new a(this, 2);
               }
               break;
            case 27:
               if (this.bw.equals("1")) {
                  this.i();
               }
               break;
            case 28:
               if (this.bw.equals("1")) {
                  this.f = new String[9];

                  for (int var34 = 0; var34 < 9; var34++) {
                     this.f[var34] = this.n();
                  }
               }
               break;
            case 30:
            case 31:
            case 32:
               boolean var3 = false;
               if (var1 == 30) {
                  try {
                     EoETown.a("watgreet");
                  } catch (RecordStoreException var16) {
                  }
               }

               try {
                  EoETown.a("watgreet", this.cv);
               } catch (RecordStoreFullException var17) {
                  var3 = true;
                  this.a("Not enough free#phone memory!#Please free up#at least 20 kb#& try again(1)", 12, -1, 0L);
               } catch (RecordStoreException var18) {
                  var3 = true;
                  String var23 = var18.getClass().getName();
                  this.a(
                     "Game initialization#failed.#Try again.#"
                        + var23.substring(var23.lastIndexOf(46) + 1)
                        + (var18.getMessage() != null ? "#(" + var18.getMessage() + ")" : ""),
                     12,
                     -1,
                     0L
                  );
               }

               if (!var3) {
                  if (this.C) {
                     if (var1 == 30) {
                        this.b(31);
                     } else if (var1 == 31) {
                        this.b(32);
                     } else if (var1 == 32) {
                        String var21 = EoETown.a("watscript", 1);
                        if (!this.X.equals(var21)) {
                           this.b(33);
                        } else {
                           this.l();
                        }
                     }
                  } else {
                     if (var1 == 30) {
                        this.bp = true;
                     } else if (var1 == 31) {
                        this.aS = true;
                     } else {
                        this.bb = true;
                     }

                     this.aZ = false;
                  }
               }
               break;
            case 33:
               try {
                  EoETown.a("watscript");
               } catch (RecordStoreException var15) {
               }

               boolean var4 = false;

               try {
                  EoETown.a("watscript", this.cv);
               } catch (RecordStoreFullException var19) {
                  var4 = true;
                  this.a("Not enough free#phone memory!#Please free up#at least 20 kb#& try again(2)", 12, -1, 0L);
               } catch (RecordStoreException var20) {
                  var4 = true;
                  String var6 = var20.getClass().getName();
                  this.a(
                     "Game initialization#failed.#Try again.#"
                        + var6.substring(var6.lastIndexOf(46) + 1)
                        + (var20.getMessage() != null ? "#(" + var20.getMessage() + ")" : ""),
                     12,
                     -1,
                     0L
                  );
               }

               if (!var4) {
                  this.cp = true;

                  try {
                     if (!this.C) {
                        EoETown.a("watkey", this.j);
                     }
                  } catch (RecordStoreFullException var13) {
                     this.a("Not enough free#phone memory!#Please free up#at least 20 kb#& try again(3)", 12, -1, 0L);
                  } catch (RecordStoreException var14) {
                  }

                  this.aZ = false;
                  this.l();
               }
               break;
            case 34:
               if (this.bw.equals("1")) {
                  this.b = this.n();
                  this.X = this.n();
                  String var22;
                  if ((var22 = this.n()).length() > 0) {
                     this.a(EoETown.b(var22), 0, -1, 5000L);
                  }

                  this.j = EoETown.a("watkey", -1);
                  this.k(2);
               } else if (this.bw.equals("2")) {
                  this.a(EoETown.b(this.n()), 12, -1, 0L);
               }
               break;
            case 35:
               if (this.bw.equals("1")) {
                  this.cu = 0;
                  this.i(104);
               }
               break;
            case 36:
               if (this.bw.equals("1")) {
                  this.bV = new String[7];

                  for (int var5 = 0; var5 < 7; var5++) {
                     this.bV[var5] = this.n();
                  }

                  this.cu = 0;
                  this.i(110);
               }
               break;
            case 38:
               if (this.bw.equals("1")) {
                  this.cu = 4;
                  this.c();
                  this.i(42);
               }
               break;
            case 42:
               if (this.bw.equals("1")) {
                  if (this.aE < 13) {
                     this.cu = this.aE - 9;
                  } else {
                     this.cu = this.aE - 13;
                  }

                  this.c();
               }
               break;
            case 43:
               if (this.bw.equals("1")) {
                  this.i(123);
                  this.y();
               } else if (this.bw.equals("0")) {
                  this.a(this.g(Integer.parseInt(this.n())), 0, 122, 0L);
               }
               break;
            case 44:
               if (this.bw.equals("1")) {
                  this.c();
                  this.cu = 0;
                  this.i(122);
               }
               break;
            case 45:
            case 48:
               if (this.bw.equals("0")) {
                  if (var1 == 45) {
                     this.a(this.g(Integer.parseInt(this.n())), 0, 70, 0L);
                  } else {
                     this.a(this.g(Integer.parseInt(this.n())), 0, 70, 0L);
                  }
               } else if (this.bw.equals("1")) {
                  this.i(70);
               }

               this.A = "";
               break;
            case 47:
            case 50:
               if (this.bw.equals("1")) {
                  if (var1 == 47) {
                     this.cu = 2;
                  } else {
                     this.cu = 3;
                  }

                  this.c();
                  this.i(70);
               }
               break;
            case 51:
               if (this.bw.equals("1")) {
                  this.a("Action successful.", 0, 104, 1000L);
               } else if (this.bw.equals("0")) {
                  this.a(this.g(Integer.parseInt(this.n())), 0, 104, 0L);
               }
               break;
            case 63:
               if (this.bw.equals("1")) {
                  this.ca = "";
                  this.by = "";
                  this.a(this.g(Integer.parseInt(this.n())), 0, 79, 0L);
               }
               break;
            case 64:
               if (this.bw.equals("1")) {
                  this.cu = 3;
                  this.a(EoETown.b(this.n()), 0, 48, 0L);
               } else if (this.bw.equals("2")) {
                  this.a(EoETown.b(this.n()), 0, 82, 0L);
               }
               break;
            case 66:
               if (this.bw.equals("1")) {
                  this.a("Action successful.", 0, 79, 1000L);
               }
               break;
            case 67:
               if (this.bw.equals("1")) {
                  this.bG = this.n();
                  this.x = this.n();
                  this.bT = this.n();
                  this.g = this.n();
                  if (this.bG.equals("1")) {
                     this.c();
                     this.a(EoETown.b(this.g), 0, 48, 0L);
                  } else if (this.bG.equals("2")) {
                     this.a(EoETown.b(this.g), 10, 48, 0L);
                  } else if (this.bG.equals("3") || this.bG.equals("4")) {
                     this.cu = 0;
                     this.i(75);
                  }
               }
               break;
            case 68:
               if (this.bw.equals("1")) {
                  String var33 = this.n();
                  this.x = this.n();
                  this.bT = this.n();
                  this.g = this.n();
                  if (var33.equals("1")) {
                     this.c();
                     this.a(EoETown.b(this.g), 0, 48, 0L);
                  } else if (var33.equals("3")) {
                     this.cu = 0;
                     this.i(75);
                  }
               }
               break;
            case 69:
               if (this.bw.equals("1")) {
                  this.au = this.n();
                  this.z = this.n();
                  this.bz = this.n();
                  this.T = this.z;
                  this.bl = this.bz;
                  this.cu = 0;
                  this.i(82);
               }
               break;
            case 70:
               if (this.bw.equals("1")) {
                  try {
                     int var11 = Integer.parseInt(this.n());
                     if (this.I.equals("3")) {
                        this.m = this.e(var11);
                        var11 = Integer.parseInt(this.n());
                        this.am = this.e(var11);
                     } else if (this.I.equals("2")) {
                        this.am = this.e(var11);
                     } else if (this.I.equals("1")) {
                        this.m = this.e(var11);
                     }

                     this.c = true;
                  } catch (Throwable var12) {
                     this.a("gethead", var12, false);
                  }
               }
               break;
            case 71:
               if (this.bw.equals("1")) {
                  this.i(48);
               }
               break;
            case 72:
               if (this.bw.equals("1")) {
                  this.i(75);
               }
         }
      }

      this.bh = 0;
      this.q = false;
      this.repaint();
   }

   public final boolean b(int var1, String var2) {
      this.cv = new Vector();
      int var3 = 0;

      int var4;
      while ((var4 = var2.indexOf(166, var3)) != -1) {
         this.cv.addElement(var2.substring(var3, var4));
         var3 = var4 + 1;
      }

      this.cv.addElement(var2.substring(var3));
      this.bw = this.n();
      this.n();
      var4 = this.cc;
      int var5 = this.bZ;
      this.cc = Integer.parseInt(this.n());
      this.bf = Integer.parseInt(this.n());
      this.bZ = Integer.parseInt(this.n());
      if (this.cc == 1 && var4 != this.cc) {
         this.aF = System.currentTimeMillis();
      }

      if (this.bZ == 1 && var5 != this.bZ) {
         this.bX = System.currentTimeMillis();
      }

      if (var1 != 26 && var1 != 1) {
         if ((this.Y == 18 || this.Y == 88) && var1 != 25 && var1 != 70 && var1 != 28) {
            return false;
         }

         if (this.cc == 1) {
            this.o = new String[4];
            this.o[3] = "5";

            for (int var6 = 0; var6 < 3; var6++) {
               this.o[var6] = this.n();
            }
         }

         if (this.bf != 0) {
            String var13 = this.n();
            String[] var7 = null;
            if (this.bf == -1) {
               this.a(var13, 11, -1, 0L);
            } else if (this.bf == 2) {
               var7 = this.g(105);
            } else if (this.bf == 3) {
               var7 = this.g(106);
            } else if (this.bf == 4) {
               var7 = this.g(107);
            } else if (this.bf == 1 && (this.V == null || this.V.e != 11)) {
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
                  case 123:
                     this.i(18);
                     String[] var8;
                     int var9;
                     String[] var10;
                     (var10 = new String[var9 = (var8 = this.g(104)).length])[0] = var13;
                     System.arraycopy(var8, 0, var10, 1, var9 - 1);
                     this.h();
                     this.bY = var13;
                     this.o();
                     this.i(88);
                     this.a(var10, 16, -1, 10000L);
                     return false;
                  case 49:
                  case 50:
                  case 51:
                  case 53:
                  case 55:
                  case 56:
                  case 61:
                  case 62:
                  case 63:
                  case 64:
                  case 65:
                  case 66:
                  case 67:
                  case 68:
                  case 69:
                  case 88:
                  case 89:
                  case 90:
                  case 91:
                  case 92:
                  case 93:
                  case 94:
                  case 95:
                  case 96:
                  case 97:
                  case 98:
                  case 99:
                  case 100:
                  case 101:
                  case 102:
                  case 103:
                  case 104:
                  case 105:
                  case 106:
                  case 107:
                  case 108:
                  case 109:
               }
            }

            if (var7 != null) {
               int var14;
               String[] var15;
               (var15 = new String[(var14 = var7.length) + 1])[0] = var13;
               System.arraycopy(var7, 0, var15, 1, var14);
               this.a(var15);
            }
         }
      } else if (this.bw.equals("2")) {
         if (this.Z != null) {
            this.Z.a();
            this.Z = null;
         }

         this.cq = Integer.parseInt(this.n());
         this.cr = 0;
         this.ay = 0;
         this.cs = null;
         this.p();
         this.cd = false;

         try {
            a(Display.getDisplay(this.ab), 600);
         } catch (IllegalStateException var11) {
         }

         this.i(18);
         this.u();
         this.a(this.g(41), 0, 94, 10000L);
         return false;
      }

      this.repaint();
      return true;
   }

   final void a(String var1, int var2, int var3, long var4) {
      String[] var6 = EoETown.b(var1);

      for (byte var7 = 0; var7 < var6.length; var7 += 5) {
         int var8;
         String[] var9 = new String[var8 = Math.min(5, var6.length - var7)];
         System.arraycopy(var6, var7, var9, 0, var8);
         this.a(var9, var2, var3, var4);
      }
   }

   final synchronized void a(String[] var1, int var2, int var3, long var4) {
      c var6 = new c(var1, var2, var3, var4);
      if (this.V == null) {
         this.V = var6;
         this.repaint();
         this.serviceRepaints();
         this.cb = System.currentTimeMillis();
      } else {
         this.bq.addElement(var6);
      }
   }

   final void a(String[] var1) {
      this.a(var1, 0, -1, 0L);
   }

   private final synchronized void v() {
      if (this.V != null) {
         if (this.V.c != -1) {
            this.i(this.V.c);
         }

         if (!this.bq.isEmpty()) {
            this.V = (c)this.bq.elementAt(0);
            this.bq.removeElementAt(0);
            this.cb = System.currentTimeMillis();
            return;
         }

         this.V = null;
      }
   }

   private final void u() {
      this.V = null;
      this.bq.removeAllElements();
   }

   private final synchronized void h() {
      if (this.V != null) {
         for (int var1 = 0; var1 < this.bq.size(); var1++) {
            if (((c)this.bq.elementAt(var1)).e != 11) {
               this.bq.removeElementAt(var1--);
            }
         }

         if (this.V.e != 11) {
            this.V.c = -1;
            this.v();
         }
      }
   }

   private final void y() {
      this.O = Integer.parseInt(this.n());
      this.ai = this.n();
      this.al = this.n();
      this.br = new String[this.O][4];

      for (int var1 = 0; var1 < this.O; var1++) {
         for (int var2 = 0; var2 < 4; var2++) {
            this.br[var1][var2] = this.n();
         }
      }

      this.bg = 0;
      this.cu = 0;
   }

   private final void f(int var1) {
      if ((var1 == 6 || var1 == 1) & this.br.length > 0) {
         this.cu = (this.cu + this.br.length + (var1 == 6 ? 1 : -1)) % this.br.length;
      }
   }

   private final void j(int var1) {
      this.K = new String[2];
      this.cu = 0;

      for (int var2 = 0; var2 < 2; var2++) {
         this.K[var2] = this.n();
      }

      if (var1 == 2) {
         this.bC = this.n();
         String var5 = EoETown.a("watgreet", 1);
         String var3 = EoETown.a("watscript", 1);
         if (!this.b.equals(var5)) {
            this.b(30);
         } else if (!this.X.equals(var3)) {
            this.b(33);
         }

         if (!this.C) {
            this.l();
         }
      } else {
         if (var1 == 3) {
            this.j = this.n();

            try {
               EoETown.a("watkey");
            } catch (RecordStoreException var4) {
            }

            this.i(7);
         }
      }
   }

   private final void b(int var1) {
      this.C = true;
      this.k(var1);
      this.i(3);
   }

   private final void l() {
      if (this.K[0].length() == 0 && this.K[1].length() == 0) {
         this.a(
            "Now it is time#to create your first#hero! Simply#enter a cool Name,#pick a Gender &#choose Create.#A hero comes with#all basic equipment#so U can start#playing right away",
            11,
            -1,
            0L
         );
      }

      if (this.K[0].length() > 0) {
         this.i(14);
      } else {
         this.e();
      }
   }

   public final String n() {
      if (this.cv.isEmpty()) {
         return "";
      }

      String var1 = (String)this.cv.elementAt(0);
      this.cv.removeElementAt(0);
      return var1;
   }

   private final void c(int var1) {
      this.bM.addElement(new Integer(var1));
   }

   private final void c() {
      if (!this.bM.isEmpty()) {
         this.i((Integer)this.bM.lastElement());
         this.bM.removeElementAt(this.bM.size() - 1);
      }
   }

   private final void a(String[] var1, int var2, int var3) {
      int var4;
      switch (var4 = Integer.parseInt(var1[3])) {
         case 1:
         case 2:
         case 3:
            this.a(this.g(99 + var4), 0, var2, 0L);
            return;
         case 4:
         case 5:
            String[] var5 = this.g(Integer.parseInt(var1[1]));
            this.a(new String[]{this.E = var1[2], var5[0], var5[1], var1[0]}, var3, var2, 0L);
      }
   }

   private final String[] g(int var1) {
      return EoETown.b(EoETown.a("watgreet", var1));
   }

   public final String w() {
      return this.cf;
   }

   private final void o() {
      if (this.Z != null) {
         this.Z.a();
         this.Z = null;
      }

      this.u();
      this.L = null;
      this.ar = null;
      this.v = null;
      this.bI = null;
      this.bs = null;
      this.U = null;
      System.gc();
      this.af = -1;
      this.cu = 0;
      this.bN = 1;
      this.c = false;
      this.cd = false;
      this.k(25);
   }

   private final void i() {
      this.aq = (int[][][])null;
      this.cs = null;
      this.f = null;
      this.cu = 0;
      this.aa = 0;
      if (this.Z == null) {
         this.Z = new a(this, 1);
      }

      this.bM.removeAllElements();
      this.q();
   }

   private final void a(int var1, int var2) {
      String[][] var3 = new String[var2][4];

      for (int var4 = 0; var4 < var2; var4++) {
         for (int var5 = 0; var5 < 4; var5++) {
            var3[var4][var5] = (String)this.cv.elementAt(var1 + 4 * var4 + var5);
         }
      }

      this.bt.addElement(var3);
   }

   private final boolean a(int var1) {
      for (int var2 = 0; var2 < this.cg.length; var2++) {
         if (var1 == this.cg[var2][0]) {
            return false;
         }
      }

      return true;
   }

   private final void x() {
      if (this.bK - 1 >= 0 && this.aL == this.ch[this.bK - 1] && this.bU && this.bK - 1 >= this.bd) {
         this.ch[this.bK] = -1;
         this.ah = this.aL;
         this.bK--;
         this.be--;
      } else if (this.bK + 1 < 8 && this.f()) {
         this.bK++;
         this.ch[this.bK] = this.aL;
         this.ah = this.aL;
         this.be++;
         this.aR[this.be] = this.aL;
      }

      this.bU = true;
   }

   private final String j() {
      if (this.bK == 0) {
         return "";
      }

      StringBuffer var1 = new StringBuffer(Integer.toString(this.ch[this.bd]));

      for (int var2 = this.bd + 1; var2 <= this.bK; var2++) {
         var1.append("_");
         var1.append(Integer.toString(this.ch[var2]));
      }

      return var1.toString();
   }

   private final boolean f() {
      return this.aU * 10 + this.bj[this.bS][1] * (this.bK + 1 - this.bd) < 720;
   }

   private final void r() {
      if (this.Y == 93) {
         this.bR = System.currentTimeMillis();
         this.w = this.bR - this.aA;
         if (this.bj[this.bS][1] * 100 + this.w >= 72000L) {
            this.i(89);
         } else {
            this.aU++;
         }
      } else if (this.aU < 72) {
         this.aU++;
      } else if (!this.cd) {
         this.u();
         this.repaint();
         this.serviceRepaints();
         this.cd = true;
         this.i(95);
         this.a(this.g(40), 17, -1, 0L);
         this.k(26);
         this.bh = 0;
      }

      this.repaint(this.bJ + 33, this.bQ + 6, 72, 4);
   }

   private final void d() {
      this.bR = System.currentTimeMillis();
      int var1 = this.bK;

      while (var1 >= 0 && this.bj[this.bS][1] * (var1 - this.bd) * 100 + this.aU * 1000 >= 71000) {
         var1--;
      }

      this.bK = var1;
      if (this.bd != this.bK) {
         this.bj[this.bS][0] = this.cu;
         int var2 = this.bj[this.bS][1] * (this.bK - this.bd);
         this.bj[this.bS][1] = var2;
         this.aU += var2 / 10;
         this.bS++;
         this.i[0] = Integer.toString((int)(this.bR - this.aA));
         this.i[2] = this.j();
         this.F.addElement(this.i);
         this.bd = var1;
         this.W = this.ch[this.bK];
      }

      this.i(89);
      this.bU = false;
   }

   private final void A() {
      if (this.as == null) {
         this.as = new int[]{-1, -1, -1, -1, -1, -1, -1, -1, -1, -1};
         this.aQ = 0;
      }

      this.bR = System.currentTimeMillis();
      this.bj[this.bS][0] = this.cu;
      this.aU = this.aU + this.bj[this.bS][1] / 10;
      this.bS++;
      this.i[0] = Integer.toString((int)(this.bR - this.aA));
      this.i[2] = Integer.toString(this.W);
      this.as[this.aQ] = this.W;
      this.aQ++;
      this.F.addElement(this.i);
      this.i(89);
   }

   private final void p() {
      this.bt = null;
      this.bj = (int[][])null;
      this.F = null;
   }

   private final void e() {
      this.c(14);
      this.ca = "";
      this.bP = 0;
      this.cu = 0;
      this.i(30);
   }

   private final void q() {
      if (this.cf == null) {
         this.cf = "4";
      }

      this.cu = 0;
      this.i(40);
      if (this.Z == null) {
         this.Z = new a(this, 1);
      }
   }

   private final void a() {
      this.bC = "";
      this.ap = "";
      this.i(11);
      this.a(
         "Welcome to the#town of Orumant.#Press left or right#screen key to close#this popup. >#NEW PLAYER:#Please enter a#Nickname &#Password#& select Register >#EXISTING PLAYER:#To use an existing#account enter your#Nickname & Pass.#& select Login >#GAME CONTROLS:#- Navigation keys#or joystick move#the Cursor#>#- Left screen key#accepts a choice#- Right screen key#goes back or#cancels",
         11,
         -1,
         0L
      );
   }

   private final void b(String var1) {
      String var2;
      int var3 = (var2 = EoETown.a("watscript", Math.abs(Integer.parseInt(var1)))).indexOf(35);
      this.bE = Integer.parseInt(var2.substring(var3 + 1, var3 + 2));
      if (this.bE == 0) {
         this.aq = (int[][][])null;
      } else {
         this.aq = new int[this.bE][4][3];
         String var7;
         var3 = (var7 = var2.substring(var3 + 3)).indexOf(35);

         for (int var4 = 0; var4 < this.bE; var4++) {
            for (int var5 = 0; var5 < 4; var5++) {
               for (int var6 = 0; var6 < 3; var6++) {
                  if (var3 != -1) {
                     if (var7.substring(0, var3).length() == 0) {
                        this.aq[var4][var5][var6] = this.aq[var4 - 1][var5][var6];
                     } else {
                        this.aq[var4][var5][var6] = Integer.parseInt(var7.substring(0, var3));
                     }

                     var3 = (var7 = var7.substring(var3 + 1)).indexOf(35);
                  } else if (var7.length() == 0) {
                     this.aq[var4][var5][var6] = this.aq[var4 - 1][var5][var6];
                  } else {
                     this.aq[var4][var5][var6] = Integer.parseInt(var7);
                  }
               }
            }
         }
      }
   }

   private final void a(String var1, int var2, int[][] var3, int var4) {
      boolean var6 = var1.indexOf("-") != -1;

      for (int var7 = 0; var7 < 4; var7++) {
         int var5;
         if (var6) {
            var5 = h[var2][0] + 15 - (this.aq[var4][var7][1] + bm[var7]);
         } else {
            var5 = h[var2][0] + this.aq[var4][var7][1];
         }

         var3[var7] = new int[]{-(this.aq[var4][var7][0] * bm[var7]), 0, var5, h[var2][1] + this.aq[var4][var7][2], var6 ? 2 : 0};
      }
   }

   private final void z() {
      this.cs = new String[15];

      for (int var1 = 0; var1 < 14; var1++) {
         this.cs[var1] = this.n();
      }
   }

   final void k() {
      Display.getDisplay(this.ab).setCurrent(this);
      this.i(48);
      this.cf = "4";
   }

   final void b() {
      this.bc = false;
      this.k(14);
   }

   final void h(int var1) {
      this.av--;
      String[][] var2 = new String[this.av][3];
      int var3 = 0;

      for (int var4 = 0; var4 < this.av + 1; var4++) {
         if (var4 != var1) {
            System.arraycopy(this.bv[var4], 0, var2[var3], 0, 3);
            var3++;
         }
      }

      this.bv = (String[][])null;
      this.bv = new String[this.av][3];
      System.arraycopy(var2, 0, this.bv, 0, this.av);
      this.bc = false;
      this.k(17);
   }

   final void s() {
      Display.getDisplay(this.ab).setCurrent(this);
      this.k(18);
   }

   private final void a(Graphics var1, String var2, String var3) {
      this.b(var1);
      if (var2 != null) {
         this.c(var1, var2 + (var3 != null && var3.length() > 0 ? " " + var3 : ""));
      }

      var1.setFont(cm);
      int var4 = var1.getFont().getHeight();
      var1.setColor(16777215);
      var1.fillRect(14, 31, 99, 68);
      var1.setColor(3601);
      var1.drawRect(14, 30, 99, 69);
      if (this.br != null) {
         int var5 = 68 / var4;
         byte var6 = 4;
         if (this.br.length > var5) {
            this.bg = Math.min(this.bg, this.cu - 1);
            this.bg = Math.max(this.bg, Math.max(this.cu - var5 + 2, 0));
            this.bg = Math.min(this.bg, this.br.length - var5);
            EoETown.a(var1, 106, 31, 68, this.bg, var5, this.br.length);
         } else {
            var6 += 3;
         }

         int var7 = 68 % var4 >> 1;

         for (int var8 = this.bg; var8 < this.br.length && var7 <= 68 - var4; var8++) {
            if (var8 == this.cu) {
               var1.setColor(10526975);
               var1.fillRect(14 + var6 - 2, 31 + var7, 89, var4);
            }

            var1.setColor(0);
            String var9 = this.br[var8][2];
            if (this.Y == 52) {
               if ("2456".indexOf(this.br[var8][3]) < 0) {
                  var9 = "÷ " + var9;
               }
            } else if ((this.Y == 123 || this.Y == 117 || this.Y == 115) && this.br[var8][1].length() > 0) {
               var9 = "× " + var9;
            }

            var1.drawString(var9, 14 + var6, 31 + var7, 20);
            var7 += var4;
         }
      }
   }

   public final void a(String var1) {
      this.ab.destroyApp(false);
      this.a(EoETown.b("Connection lost.#Game is closing#down.#Please try later.#(" + var1 + ")"), 18, -1, 0L);
      this.cb = System.currentTimeMillis();
      this.q = false;
   }

   final void a(String var1, Throwable var2, boolean var3) {
      String var4 = var2.getClass().getName();
      this.u();
      this.a(
         EoETown.b(
            var1
               + '#'
               + var4.substring(var4.lastIndexOf(46) + 1)
               + '#'
               + (var2.getMessage() != null ? var2.getMessage() + "#s" : "s")
               + this.Y
               + " v"
               + "5.3.3"
         ),
         12,
         -1,
         0L
      );
      this.q = false;
      String var5 = var1 + ", " + var2.toString() + ", s" + this.Y;
      this.s = new d(
         this, 100, this.P + "errorreport.pl", "¦msg=" + var5 + "¦id=" + "02010502" + "¦productid=" + "01020202" + "¦build=" + "5.3.3" + "¦login=" + this.bC
      );
   }

   private final void b(int var1, int var2) {
      switch (var1) {
         case 1:
            this.cu--;
            break;
         case 2:
         case 5:
            int var3 = 1;
            if (var1 == 2) {
               var3 = -1;
            }

            if (var2 == 5) {
               if (var1 == 2) {
                  var3 = bF[this.cu];
               } else {
                  var3 = bW[this.cu];
               }
            } else if (var2 == 6) {
               if (var1 == 2) {
                  var3 = Q[this.cu];
               } else {
                  var3 = e[this.cu];
               }
            }

            this.cu += var3;
         case 3:
         case 4:
         default:
            break;
         case 6:
            this.cu++;
      }

      this.cu = (this.cu + var2) % var2;
   }

   private static final boolean d(int var0) {
      return var0 == -10 || var0 == 55 || var0 == 42;
   }

   final synchronized void i(int var1) {
      if (var1 != this.Y) {
         this.l = System.currentTimeMillis();
         this.Y = var1;
         this.repaint();
      }
   }

   public static final void a(boolean var0) {
      DeviceControl.setLights(0, var0 ? 100 : 0);
   }

   public static final void a(Display var0, int var1) {
      if (var1 > 0) {
         DeviceControl.startVibra(50, var1);
      } else {
         DeviceControl.stopVibra();
      }
   }

   public static final void a(Graphics var0, Image var1, int var2, int var3, int var4, int var5, int var6, int var7, int var8, int var9) {
      int var10 = var0.getClipX();
      int var11 = var0.getClipY();
      int var12 = var0.getClipWidth();
      int var13 = var0.getClipHeight();
      boolean var14;
      if (var14 = var1.getWidth() != var4 || var1.getHeight() != var5) {
         var0.setClip(var7, var8, var4, var5);
      }

      int var15 = var6 == 2 ? var7 - var1.getWidth() + var4 + var2 : var7 - var2;
      DirectUtils.getDirectGraphics(var0).drawImage(var1, var15, var8 - var3, var9, var6 << 12);
      if (var14) {
         var0.setClip(var10, var11, var12, var13);
      }
   }
}
