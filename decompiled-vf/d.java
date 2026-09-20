import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.util.Hashtable;
import java.util.Random;
import java.util.Stack;
import java.util.Vector;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public final class d extends e {
   private final byte[][] h;
   private final byte[] i;
   private final byte[][] j;
   private boolean k;
   private byte[] l;
   private final byte[] m;
   private final j[] n;
   public j a;
   private int o;
   private b p;
   private Hashtable q;
   private static final Random x = new Random();
   private static final String[] y = new String[]{"Movement", "Melee attack", "Ranged attack", "Defence", "Offence spells", "Defensive spells"};
   private static final String[] z = new String[]{" Strength", " Intelligence", " Dexterity", " Toughness", " Willpower", " Speed"};
   private static final String[] A = new String[]{
      "Strength gives:\n+weapon damage\n+carry more weight\n+heavier weapons",
      "Intelligence gives:\n+effect to all spells cast on foe",
      "Dexterity gives:\n+hit chance\n+defense\n+complex weapon",
      "Toughness gives:\n+life points",
      "Willpower gives:\n+spell resistance\n+protect spells cheaper prices",
      "Speed makes U:\n+Faster when using skills and spells in fight"
   };
   public static final String[] b = new String[]{"Melee weapons", "Missile weapons", "Armours", "Skills", "Spells", "Back"};
   private Image B;
   private Image C;
   private byte[] D;
   private final int E;
   private final int F;
   private int G;
   private int H;
   private int I;
   private int J;
   private int K;
   private int L;
   private long M;
   private Image N;
   private Image O;
   private long P;
   private int Q;
   private int R;
   private final Vector S;
   private boolean T;
   private boolean U;
   private long V;
   private int W;
   private int X;
   public boolean c;
   private int Y;
   private int Z;
   private int aa;
   private int ab;
   private j ac;
   private final c[] ad;
   private final Stack ae;
   private static final Object[] af = new Object[]{new Integer(6), new byte[]{1, 102, 0, 0}};
   private int ag;
   private int ah;
   private final Stack ai;
   private Stack aj;
   private int ak;
   private byte[] al;
   private Vector am;
   private Vector an;
   private int ao;
   private int ap;
   private String aq;
   private int ar;
   public j d;
   private byte[] as;
   private int at;
   private b au;
   private Stack av;
   private boolean aw;
   private long ax;
   public byte[] e;
   public boolean f;
   private int ay;
   private int az;
   private byte[] aA;
   private int aB;
   private int aC;
   private int aD;
   private final Vector aE;
   private final Vector aF;
   public long g;
   private int aG;
   private byte[] aH;
   private byte[] aI;
   private c aJ;

   public d(int var1, int var2, int var3, byte[][] var4, byte[][] var5, b var6, boolean var7) {
      super(var1);
      System.currentTimeMillis();
      this.S = new Vector();
      this.ad = new c[8];
      this.ae = new Stack();
      this.ai = new Stack();
      this.aj = new Stack();
      this.al = new byte[2];
      this.av = new Stack();
      this.f = true;
      this.aE = new Vector();
      this.aF = new Vector();
      this.E = var2;
      this.F = var3;
      this.h = var4;
      this.j = var5;
      this.k = var7;
      this.i = (byte[])var6.d.get(new Integer(21));
      this.l = (byte[])var6.d.get(new Integer(25));
      this.n = new j[this.l.length];
      this.m = new byte[this.l.length];

      for (int var8 = 0; var8 < var5.length; var8++) {
         byte[] var9;
         int var10 = (var9 = var5[var8])[0] & 255;
         if (var9[11] != 0 && this.l[var10] == 3) {
            this.l[var10] = 2;
         }
      }

      super.v = 50;
      this.G = var2 >> 1;
      this.H = (var3 >> 1) + 6;
      this.W = var6.b(26);
      this.X = var6.b(27);
      this.I = var6.b(22);
      this.J = var6.b(23) << 8;
      this.K = var6.b(24) << 8;
      this.ad[6] = new c(6, null, i.a(new Object[]{"End turn", "Try to flee"}), 9, 279);
      this.ad[7] = new c(7, "Target", i.a(new Object[]{"Change target"}), 9, 279);
   }

   private void k() {
      this.T = false;
      Vector var1 = new Vector();
      if (this.p == null) {
         super.w.e = new Hashtable();
      }

      if (this.L != this.I) {
         this.Q = this.J + 128 >> 8;
         this.R = this.K + 128 >> 8;
      }

      if (!this.U) {
         Image var2 = super.w.a("/70");
         byte[] var3 = super.w.b(8, 0, var1);
         Hashtable var4 = super.w.a(0, var1);
         byte[] var5;
         (var5 = new byte[19])[15] = 1;
         this.a = new j(this, 0, var5);
         this.a.a(var2, var3, var4);
         this.n[0] = this.a;
         super.w.e();
      } else {
         this.W = this.Q;
         this.X = this.R;
      }

      this.a.h = this.J;
      this.a.i = this.K;
      DataInputStream var18;
      if ((var18 = super.w.c(2, this.I, var1)) != null) {
         try {
            var18.readByte();
            var18.readShort();
            this.aB = var18.readUnsignedShort();
            this.aC = var18.readUnsignedShort();
            this.aD = var18.readUnsignedShort();
            this.ay = var18.readShort();
            this.az = var18.readShort();
            this.aA = new byte[this.ay * this.az];
            var18.readFully(this.aA);
         } catch (Exception var15) {
            throw new RuntimeException("Unable to read map '" + this.I + "'");
         } finally {
            try {
               var18.close();
            } catch (Exception var14) {
            }
         }

         for (int var19 = 0; var19 < this.h.length; var19++) {
            byte[] var24;
            int var29 = (var24 = this.h[var19])[0] & 255;
            if (this.i[var29] == 3 && var24[12] == 6 && this.I == var24[14]) {
               this.b(var24);
            }
         }
      }

      this.q = super.w.b(this.I, var1);
      this.B = super.w.a(4, 0, var1);
      this.C = super.w.a(5, 2, var1);
      this.D = super.w.b(6, 2, var1);
      this.aF.removeAllElements();

      for (int var20 = 0; var20 < this.j.length; var20++) {
         byte[] var25;
         int var30 = (var25 = this.j[var20])[0] & 255;
         if (var25[1] == this.I && (this.l[var30] == 1 || this.l[var30] == 2 || var25[11] != 0)) {
            Image var6 = super.w.a(7, var25[12], var1);
            byte[] var7 = super.w.b(8, var25[12], var1);
            Hashtable var8 = super.w.a(var25[12], var1);
            if (var6 != null && var7 != null && var8 != null) {
               if (this.n[var30] == null) {
                  this.n[var30] = new j(this, var30, var25);
               }

               this.n[var30].a(var6, var7, var8);
               this.n[var30].e = this.n[var30].a = var25[13] & 255;
               if (var25[15] > 0) {
                  this.n[var30].a(14, true);
               } else {
                  this.n[var30].f = true;
               }

               if (this.l[var30] == 2) {
                  this.aF.addElement(this.n[var30]);
               }
            }
         } else if (this.n[var30] != null) {
            this.n[var30].a();
         }
      }

      if (var1.size() <= 0) {
         this.aE.removeAllElements();

         for (int var21 = 0; var21 < this.h.length; var21++) {
            byte[] var26;
            if ((var26 = this.h[var21])[1] == this.I || var26[1] == 0) {
               this.aE.addElement(var26);
            }
         }

         this.aF.addElement(this.a);
         if (this.a != null && this.a.d == null) {
            this.a.d = super.w.a("/70");
         }

         this.M = super.t;
         this.p = null;
         this.U = true;
         this.T = true;
         this.L = this.I;
         this.b();
      } else if (this.p != null) {
         StringBuffer var23 = new StringBuffer("Unable to get resources from server:");

         for (int var28 = 0; var28 < var1.size(); var28++) {
            var23.append("\n").append(Integer.toHexString(((Integer)var1.elementAt(var28)).shortValue()));
         }

         throw new RuntimeException(var23.toString());
      } else {
         ByteArrayOutputStream var22 = new ByteArrayOutputStream();
         DataOutputStream var27 = new DataOutputStream(var22);

         try {
            for (int var31 = 0; var31 < var1.size(); var31++) {
               var27.writeShort(((Integer)var1.elementAt(var31)).shortValue());
            }
         } catch (IOException var17) {
         }

         this.p = new b(10, this);
         this.p.a(1, var22.toByteArray());
         this.p.a(super.w.d);
         this.p.a(3, super.w.c);
         if (this.U) {
            this.d(this.p);
         }

         super.w.a(this, this.p);
      }
   }

   public final void a(Graphics var1, boolean var2) {
      var1.setFont(e.r);
      var1.setColor(0);
      var1.fillRect(0, 0, 240, 320);
      if (this.T && this.a.d != null) {
         this.a(var1, 0, 0, this.E, this.c ? Math.min(279, this.F) : this.F);
         var1.setClip(0, 0, 240, 320);
         if (!this.c && super.t - this.M < 4000L) {
            String var3 = this.b(this.aD);
            int var4 = e.r.stringWidth(var3);
            var1.setColor(8610337);
            var1.fillRect(240 - var4 - 6 >> 1, 0, var4 + 6, e.s);
            var1.setColor(16173378);
            var1.drawString(var3, 120, 0, 17);
         }

         this.ap = (this.ap + 1) % 3;
         if (this.c) {
            if (this.O == null) {
               this.O = super.w.a("/fpanel.png");
            }

            e.a(var1, this.O, 0, 0, 240, 9, 0, 0, 0, 20);
            var1.setColor(0);
            j var10 = this.a;
            int var12 = this.a.l > 0 ? var10.m * 109 / var10.l : 109;
            var1.fillRect(119 - var12, 2, var12, 5);
            int var5 = this.ah * 109 / 720;
            var12 = this.ag * 109 / 720 + (this.ag + this.ah <= 720 ? var5 : 0);
            var1.fillRect(238 - var12, 2, var12, 5);
            if (this.ap != 0 && this.ah > 0 && this.ag + this.ah <= 720) {
               e.a(var1, this.O, 109 - var12, 50, var5, 5, 0, 238 - var12, 2, 20);
            }

            if (this.ab == 5) {
               var1.fillRect(0, 279, 240, 41);
               if (this.aq != null) {
                  var1.setColor(this.ar);
                  var1.drawString(this.aq, 1, 320 - (41 - e.s >> 1), 36);
               }
            } else {
               e.a(var1, this.O, 0, 9, 240, 41, 0, 0, 279, 20);
               if (this.aF.size() < 3) {
                  var1.fillRect(188, 298, 19, 19);
               }

               int var6 = Math.min(11, this.ae.size());

               for (int var7 = 0; var7 < var6; var7++) {
                  Object[] var8 = (Object[])this.ae.elementAt(var7);
                  e.a(var1, this.O, (Integer)var8[0] * 22 + 36, 30, 14, 15, 0, var7 * 16 + 34, 283, 20);
               }

               if (var2 && (this.ab == 4 || this.ab == 3)) {
                  var1.setColor(Math.abs(255 - ((int)super.t & 510)) << 8 | 0xFF0000);
                  var1.drawRect(this.Y * 22 + 33, 298, 19, 19);
               }
            }

            if (this.ab == 3) {
               this.ad[this.Y].a(var1, true);
            }
         } else {
            var1.setColor(0);
            if (this.N == null) {
               this.N = super.w.a("/cpanel.png");
            }

            var1.drawImage(this.N, 0, 320, 36);
            if (this.S.size() == 0 || this.ap == 0 || !var2) {
               var1.fillRect(37, 307, 17, 13);
            }

            int var9 = 122 * b.h >> 8;
            var1.fillRect(59 + var9, 311, 122 - var9, 4);
            int var11 = 300 - (e.s >> 1);
            var1.setColor(16777215);
            var1.drawString(b.e, 50, 0 + var11, 20);
            var1.drawString(b.f, 119, 0 + var11, 20);
            var1.drawString(b.g, 167, 0 + var11, 20);
         }
      } else {
         var1.setColor(16777215);
         var1.drawString("Please wait...", 120, 160, 65);
      }
   }

   public final void a(Graphics var1, int var2, int var3, int var4, int var5) {
      var1.setClip(var2, var3, var4, var5);
      int var6;
      int var7;
      if (this.c) {
         var6 = (this.Z << 8) + 128;
         var7 = (this.aa << 8) + 128;
      } else {
         var6 = this.a.h;
         var7 = this.a.i;
      }

      int var8 = this.G;
      int var9 = this.H;
      var1.setColor(0);
      var1.fillRect(var2, var3, var4, var5);
      int var10 = var8 - ((256 + (var6 & 0xFF) - (var7 & 0xFF)) * 16 >> 8);
      int var11 = 1 + var9 - ((256 + (var6 & 0xFF) + (var7 & 0xFF)) * 8 >> 8);
      int var12 = var6 >> 8;
      int var13 = var7 >> 8;
      int var14 = (var2 - var10 + 3152) / 32 - 99;
      int var15 = (var3 - var11 + 2) / 8 - 2;
      var10 += var14 * 32;
      int var33;
      int var16 = var33 = var11 + var15 * 8;

      for (int var17 = var15; var16 < var3 + var5; var17++) {
         int var18 = var10 + (var17 % 2 != 0 ? 16 : 0);
         int var19 = var12 + var14 + (var17 + 1 >> 1);
         int var20 = var13 - var14 + (var17 >> 1);

         while (var18 < var2 + var4) {
            int var21;
            if ((var19 | var20) >= 0 && var19 < this.ay && var20 < this.az && (var21 = this.aA[var20 * this.ay + var19] & 15) != 0) {
               var1.drawRegion(this.B, 0, (var21 - 1) * 15, 32, 15, 0, var18, var16, 20);
            }

            var19++;
            var20--;
            var18 += 32;
         }

         var16 += 8;
      }

      int var35 = ((var6 - var7) * 16 >> 8) - var8;
      int var36 = ((var6 + var7) * 8 >> 8) - var9;
      if (this.c) {
         var1.setClip(var2, var3, var4, var5);
         var1.setColor(0);
         int var37 = (this.Z - this.aa) * 16 - var35 - 64;
         int var39 = (this.Z + this.aa) * 8 - var36 + 40;

         for (int var42 = 0; var42 < 9; var42++) {
            int var22;
            if ((var22 = 1 + var42) > 4) {
               var22 = Math.min(4, 10 - var22);
            }

            var1.drawLine(var37 + 16 * (-var22 + var42) - 1, var39 + 8 * (-var22 - var42), var37 + 16 * (var22 + var42), var39 + 8 * (var22 - var42));
            var1.drawLine(var37 + 16 * (-var22 + var42) - 1, var39 + 8 * (var22 + var42 - 8), var37 + 16 * (var22 + var42), var39 + 8 * (-var22 + var42 - 8));
         }

         if (this.ab == 0) {
            var1.setColor(Math.abs(255 - ((int)super.t & 510)) << 8);
         } else {
            var1.setColor(65280);
         }

         int var43 = this.ac.h >>> 8;
         int var46 = this.ac.i >>> 8;
         int var23 = (var43 - var46) * 16 - var35;
         int var24 = (var43 + var46) * 8 - var36 - 8;
         var1.drawLine(var23 - 1, var24, var23 + 16, var24 + 8);
         var1.drawLine(var23 + 16, var24 + 8, var23 - 1, var24 + 16);
         var1.drawLine(var23 - 1, var24 + 16, var23 - 16 - 1, var24 + 8);
         var1.drawLine(var23 - 16 - 1, var24 + 8, var23, var24);
         if (this.ab == 2) {
            var1.setColor(Math.abs(255 - ((int)super.t & 510)) << 8 | 0xFF);
            var1.fillRect((this.al[0] - this.al[1]) * 16 - var35 - 8, (this.al[0] + this.al[1]) * 8 - var36 - 4, 16, 8);
         } else if (this.ab == 1) {
            var1.setColor(Math.abs(255 - ((int)super.t & 510)) << 8 | 0xFF);

            for (int var25 = this.aj.size() - 1; var25 >= 0; var25--) {
               byte[] var26;
               int var27 = (var26 = (byte[])this.aj.elementAt(var25))[0] & 255;
               int var28 = var26[1] & 255;
               var1.fillRect((var27 - var28) * 16 - var35 - 8, (var27 + var28) * 8 - var36 - 4, 16, 8);
               var1.setColor(6316287);
            }
         } else {
            var1.setColor(255);

            for (int var52 = 0; var52 < this.ai.size(); var52++) {
               Vector var56 = (Vector)this.ai.elementAt(var52);

               for (int var60 = 0; var60 < var56.size(); var60++) {
                  byte[] var64;
                  int var29 = (var64 = (byte[])var56.elementAt(var60))[0] & 255;
                  int var30 = var64[1] & 255;
                  var1.fillRect((var29 - var30) * 16 - var35 - 8, (var29 + var30) * 8 - var36 - 4, 16, 8);
               }
            }
         }
      }

      int var38;
      if ((var38 = this.aF.size()) > 0) {
         int var40 = 0;
         int var44 = Integer.MIN_VALUE;

         label135:
         for (boolean var47 = false; !var47; var47 = true) {
            j var49;
            int var51 = (var49 = (j)this.aF.elementAt(var40)).e();

            while (var40 < var38) {
               j var53 = var49;
               int var57 = var51;
               var40++;
               if (var40 < var38 && (var51 = (var49 = (j)this.aF.elementAt(var40)).e()) < var57) {
                  this.aF.setElementAt(var49, var40 - 1);
                  this.aF.setElementAt(var53, var40);
                  var49 = var53;
                  int var61 = var51;
                  var51 = var57;
                  var57 = var61;
               }

               if (var57 < var44) {
                  break label135;
               }

               var44 = var57;
            }
         }
      }

      var10 += 16;
      var16 = var33 + 8;
      int var41 = 0;
      j var45;
      int var48;
      if (var38 == 0) {
         var45 = null;
         var48 = Integer.MAX_VALUE;
      } else {
         var48 = ((var45 = (j)this.aF.elementAt(0)).e() * 8 >> 8) - var36;
      }

      long var50 = System.currentTimeMillis();

      for (int var54 = var15; var16 < var3 + var5 + 32; var54++) {
         while (var48 < var16) {
            int var58 = var45.b;
            var1.setClip(var2, var3, var4, var5);
            int var62 = ((this.n[var58].h - this.n[var58].i) * 16 >> 8) - var35;
            this.n[var58].a(var1, var62, var48, var50);
            if (++var41 < var38) {
               var48 = ((var45 = (j)this.aF.elementAt(var41)).e() * 8 >> 8) - var36;
            } else {
               var48 = Integer.MAX_VALUE;
            }
         }

         int var59 = var10 + (var54 % 2 != 0 ? 16 : 0);
         int var63 = var12 + var14 + (var54 + 1 >> 1);
         int var65 = var13 - var14 + (var54 >> 1);

         while (var59 < var2 + var4 + 32) {
            int var66;
            if ((var63 | var65) >= 0 && var63 < this.ay && var65 < this.az && (var66 = (this.aA[var65 * this.ay + var63] & 240) >> 4) >= 2) {
               int var67 = var66 - 2 << 3;
               var1.drawRegion(
                  this.C,
                  this.D[var67 + 2] << 8 | this.D[var67 + 2 + 1] & 255,
                  this.D[var67 + 4] << 8 | this.D[var67 + 4 + 1] & 255,
                  this.D[var67 + 0],
                  this.D[var67 + 1],
                  0,
                  var59 + this.D[var67 + 6],
                  var16 + this.D[var67 + 7],
                  20
               );
            }

            var63++;
            var65--;
            var59 += 32;
         }

         var16 += 8;
      }

      j var55 = this.d;
      if (this.d != null && var55.b == -1) {
         var1.setClip(var2, var3, var4, var5);
         var55.a(var1, ((var55.h - var55.i) * 16 >> 8) - var35, ((var55.h + var55.i) * 8 >> 8) - var36, var50);
      }
   }

   public final void b() {
      this.S.removeAllElements();
      if (!this.c && this.I == this.L && !this.k) {
         label101:
         for (int var1 = 0; var1 < this.aE.size(); var1++) {
            byte[] var2 = (byte[])this.aE.elementAt(var1);
            if (this.i[var2[0] & 0xFF] == 2
               && (var2[1] == this.L || var2[1] == 0)
               && (var2[4] == 0 || (var2[2] & 255) <= this.Q && (var2[3] & 255) <= this.R && (var2[4] & 255) > this.Q && (var2[5] & 255) > this.R)) {
               int var3 = 14 + (var2[13] & 255);

               for (int var4 = 1; var4 < var2[var3]; var4++) {
                  if (var2[var3 + 1] == 0 && this.i[var2[var3 + 1 + var4] & 0xFF] != 3 || var2[var3 + 1] == 1 && this.l[var2[var3 + 1 + var4] & 0xFF] != 3) {
                     continue label101;
                  }
               }

               switch (var2[6]) {
                  case 0:
                     if (this.a(var2)) {
                        var1 = -1;
                     }
                     break;
                  case 1:
                     this.S.addElement(var2);
               }
            }
         }

         while (!this.av.empty()) {
            b var7 = (b)this.av.pop();
            this.d(var7);
            super.w.a(this, var7);
         }

         for (int var8 = 0; var8 < this.aF.size(); var8++) {
            j var9;
            if ((var9 = (j)this.aF.elementAt(var8)).b != 0) {
               int var10 = Math.abs(this.a.h - var9.h) >> 8;
               int var11 = Math.abs(this.a.i - var9.i) >> 8;
               byte var5 = var9.c[9];
               byte var6 = var9.c[10];
               if (var5 > 0 && var10 < var5 && var11 < var5 && !this.aw && this.a(this.a, var9)) {
                  this.a(this.a(var9.c[5], var9.c[6]), new byte[]{(byte)var9.b});
                  return;
               }

               if (var6 > 0 && var10 < var6 && var11 < var6 && this.a(this.a, var9)) {
                  this.S.addElement(var9);
               }
            }
         }
      }
   }

   private boolean a(j var1, j var2) {
      int var3 = var1.h + 128 >> 8;
      int var4 = var1.i + 128 >> 8;
      int var5 = var2.h + 128 >> 8;
      int var6 = var2.i + 128 >> 8;

      while (var3 != var5 || var4 != var6) {
         if (Math.abs(var3 - var5) > Math.abs(var4 - var6)) {
            if (var3 > var5) {
               var3--;
            } else {
               var3++;
            }
         } else if (var4 > var6) {
            var4--;
         } else {
            var4++;
         }

         if (!this.b(var3, var4)) {
            return false;
         }
      }

      return true;
   }

   public final void a(String var1, byte[] var2) {
      if (!this.aw) {
         this.aw = true;
         this.e = var2;
         h var3;
         (var3 = new h(36, null, var1, new String[]{"Auto fight", "Manual"})).c = true;
         if (!this.f) {
            var3.b = 1;
         }

         super.w.a(this, var3, false);
      }
   }

   public final void a(byte[] var1, boolean var2) {
      b var3 = new b(12, this);
      if (var1.length > 0) {
         this.d(var3);
      }

      var3.a(1, var1);
      byte[] var4 = new byte[this.aF.size() * 3];

      for (int var5 = 0; var5 < this.aF.size(); var5++) {
         j var6 = (j)this.aF.elementAt(var5);
         if (this.l[var6.b] == 1) {
            this.l[var6.b] = 2;
         }

         int var7 = var5 * 3;
         var4[var7] = (byte)var6.b;
         var4[var7 + 1] = (byte)(var6.h + 128 >> 8);
         var4[var7 + 2] = (byte)(var6.i + 128 >> 8);
      }

      var3.a(2, var4);
      if (var2) {
         var3.b(3, 1);
         var3.i = true;
      }

      super.w.a(this, var3);
   }

   public final void a(b var1) {
      for (int var2 = 0; var2 < 6; var2++) {
         Vector var3;
         if ((var3 = var1.a(30 + var2)).isEmpty()) {
            var3.addElement("Empty");
         }

         this.ad[var2] = new c(var2, y[var2], var3, 9, 279);
      }

      this.Z = var1.b(20);
      this.aa = var1.b(21);
      this.an = new Vector();
      this.aF.removeAllElements();
      Vector var6 = var1.a(22);

      for (int var7 = 0; var7 < var6.size(); var7++) {
         byte[] var4 = (byte[])var6.elementAt(var7);
         j var5;
         if ((var5 = this.n[var4[0] & 0xFF]) == null) {
            throw new RuntimeException("Mob " + (var4[0] & 0xFF) + " dead");
         }

         this.aF.addElement(var5);
         this.an.addElement(var5);
         var5.f();
         var5.h = var4[1] << 8;
         var5.i = var4[2] << 8;
         var5.l = var4[3] << 8 | var4[4] & 255;
         var5.m = var4[5] << 8 | var4[6] & 255;
         var5.a = var4[7] & 255;
      }

      this.ac = (j)this.aF.elementAt(1);
      this.c = true;
      this.l();
      this.k = false;
   }

   private void l() {
      this.ab = 4;
      this.ag = 0;
      this.ad[6].c = this.ad[7].c = 0;
      this.as = null;
      this.ae.removeAllElements();
      this.Y = 0;
      this.ax = System.currentTimeMillis();
      this.aq = null;
      this.o();
   }

   public final void b(b var1) {
      switch (var1.c) {
         case 1:
            e.a(Display.getDisplay(g.b), 600);
            super.w.a(this, new h(30, null, "New turn starts", null, 3000), false);
            this.l();
            return;
         case 2:
            super.w.a(this, new h(30, null, "Congratulations, you won the fight!", null, 3000), false);
            String var2;
            if ((var2 = (String)var1.d.get(new Integer(24))) != null) {
               super.w.a(this, new h(30, "Battle report", var2), false);
            }

            this.c(var1);
            this.l = (byte[])var1.d.get(new Integer(23));
            this.a(var1, (byte[])var1.d.get(new Integer(28)));
            return;
         case 3:
            super.w
               .a(
                  this,
                  new h(
                     30,
                     null,
                     "You lost the fight!\n\nLuckily someone found you and brought you back to the start of this adventure so that you can continue your quest."
                  ),
                  false
               );
            this.I = var1.b(25);
            this.J = (this.Q = var1.b(26)) << 8;
            this.K = (this.R = var1.b(27)) << 8;
            this.T = false;
            this.a(var1, null);
            return;
         case 4:
            super.w.a(this, new h(30, null, "You flee"), false);
            this.a(var1, null);
            this.a.h = (short)((this.Q = this.W) << 8);
            this.a.i = (short)((this.R = this.X) << 8);
      }
   }

   public final void a(b var1, byte[] var2) {
      if (var2 != null) {
         for (int var3 = 0; var3 < var2.length; var3++) {
            int var4 = var2[var3] & 255;
            this.c(var4);
            this.aF.removeElement(this.n[var4]);
         }
      }

      if (!var1.i) {
         this.ae.removeAllElements();

         for (int var9 = 0; var9 < this.an.size(); var9++) {
            ((j)this.an.elementAt(var9)).g();
         }

         this.aF.removeAllElements();

         for (int var10 = 0; var10 < this.j.length; var10++) {
            byte[] var13;
            int var5 = (var13 = this.j[var10])[0] & 255;
            if (var13[1] == this.L && this.l[var5] == 2) {
               this.aF.addElement(this.n[var5]);
            }
         }

         this.aF.addElement(this.a);
         this.a.a = 15;
         this.c = false;
         this.ac = null;
         this.am = null;

         for (int var11 = 0; var11 < 6; var11++) {
            this.ad[var11] = null;
         }
      }

      if (var2 != null) {
         for (int var12 = 0; var12 < this.h.length; var12++) {
            byte[] var14;
            byte var15;
            if (((var15 = (var14 = this.h[var12])[6]) == 2 || var15 == 3) && this.i[var14[0] & 0xFF] == 2) {
               int var6 = var14[8] & 255;

               for (int var7 = 0; var7 < var2.length; var7++) {
                  int var8 = var2[var7] & 255;
                  if (var15 == 2 && var8 == var6 || var15 == 3 && this.n[var8] != null && this.n[var8].c[2] == var6) {
                     this.a(var14);
                  }
               }
            }
         }
      }

      this.an = null;
      this.aw = false;
      this.c(var1);
      this.au = null;
      g.a(true);
   }

   public final boolean a(Object var1) {
      if (var1 instanceof j) {
         if (!this.aw) {
            j var11 = (j)var1;
            this.a(this.a(var11.c[7], var11.c[8]), new byte[]{(byte)var11.b});
         }

         return false;
      } else {
         byte[] var2;
         boolean var3;
         int var4;
         var2 = (byte[])var1;
         var3 = false;
         var4 = var2[13] & 255;
         label150:
         switch (var2[12]) {
            case 1:
               super.w.a(this, new h(30, null, this.a(var2[14], var2[15])), false);
               this.n();
               break;
            case 2:
               if (this.aw) {
                  return false;
               }

               byte[] var5 = new byte[var4];
               System.arraycopy(var2, 14, var5, 0, var5.length);
               this.a("Entering fight", var5);

               for (int var13 = 0; var13 < var4; var13++) {
                  byte var17 = var2[14 + var13];

                  for (int var22 = 0; var22 < this.aF.size(); var22++) {
                     j var26;
                     if ((var26 = (j)this.aF.elementAt(var22)).b == var17) {
                        super.w.a(this, new h(30, null, this.a(var26.c[5], var26.c[6])), false);
                        break label150;
                     }
                  }
               }
               break;
            case 3:
               b var6;
               (var6 = new b(11, this)).b(1, var2[0] & 255);
               this.av.push(var6);
               break;
            case 4:
               this.J = (short)((this.Q = var2[15] & 255) << 8);
               this.K = (short)((this.R = var2[16] & 255) << 8);
               if (var2[14] != this.L) {
                  this.I = var2[14];
                  this.T = false;
               } else {
                  this.a.h = this.J;
                  this.a.i = this.K;
               }
               break;
            case 5:
               for (int var16 = 0; var16 < var4; var16++) {
                  int var21 = var2[14 + var16] & 255;

                  for (int var25 = 0; var25 < this.j.length; var25++) {
                     byte[] var29;
                     if ((var29 = this.j[var25])[0] == var21) {
                        this.a(var29);
                        break;
                     }
                  }
               }
               break;
            case 6:
               if (this.L == (var2[14] & 255)) {
                  this.b(var2);
               }
               break;
            case 7:
               for (int var7 = 0; var7 < var4; var7++) {
                  int var8 = var2[14 + var7] & 255;
                  this.c(var8);

                  for (int var9 = 0; var9 < this.aF.size(); var9++) {
                     j var10;
                     if ((var10 = (j)this.aF.elementAt(var9)) != null && var10.b == var8) {
                        this.aF.removeElementAt(var9);
                        break;
                     }
                  }
               }
            case 8:
            case 9:
            default:
               break;
            case 10:
               this.a.d = null;
               super.w.a(this, new c(11, "Pick interest", i.a(b)), false);
               break;
            case 11:
               this.av.push(new b(17, this));
         }

         int var12 = 14 + var4 + 1 + var2[14 + var4];

         for (int var14 = 1; var14 <= var2[var12]; var14++) {
            int var18 = var2[var12 + var14] & 255;
            if (this.i[var18] == 1) {
               this.i[var18] = 2;
               var3 = true;
            }
         }

         int var15 = var12 + var2[var12] + 1;

         for (int var19 = 1; var19 <= var2[var15]; var19++) {
            int var23 = var2[var15 + var19] & 255;
            if (this.i[var23] == 2) {
               this.i[var23] = 3;
               if (var23 != var2[0]) {
                  for (int var27 = 0; var27 < this.h.length; var27++) {
                     if (this.h[var27][0] == var23 && this.h[var27][12] == 6) {
                        this.a(this.h[var27]);
                     }
                  }
               }

               var3 = true;
            }
         }

         int var20 = var15 + var2[var15] + 1;

         for (int var24 = 1; var24 <= var2[var20]; var24++) {
            int var28 = var2[var20 + var24] & 255;
            if (this.i[var28] != 3) {
               this.i[var28] = 4;
            }
         }

         return var3;
      }
   }

   private void a(byte[] var1) {
      int var2 = var1[0] & 255;
      this.l[var2] = 2;
      j var3 = this.n[var2];
      if (var1[1] == this.L && var3 != null && !this.aF.contains(var3)) {
         this.aF.addElement(var3);
      }
   }

   private void c(int var1) {
      for (int var2 = 0; var2 < this.j.length; var2++) {
         byte[] var3;
         if ((var3 = this.j[var2])[0] == var1) {
            this.l[var1] = 3;
            this.m[var1] = var3[11];
            return;
         }
      }
   }

   private void b(byte[] var1) {
      for (int var2 = 0; var2 < var1[18]; var2++) {
         System.arraycopy(var1, var2 * var1[17] + 14 + 5, this.aA, (var1[16] + var2) * this.ay + var1[15], var1[17]);
      }
   }

   public final void a() {
      if (!this.T) {
         this.n();
         if (this.p == null || !this.p.b.isAlive()) {
            this.k();
         }
      } else {
         super.w.d();
         super.w.serviceRepaints();
         if (this.k) {
            this.a(new byte[0], false);
         } else {
            if (this.c) {
               int var1;
               if (this.ab != 5 && this.ab != 6 && (var1 = (int)((super.t - this.ax) / 1000L)) != 0) {
                  long var2 = (super.t - this.ax) % 1000L;
                  this.ax = super.t - var2;
                  this.ag += var1 * 5;
                  if (this.ag > 720) {
                     this.j();
                     this.ag = 720;
                  }
               }

               if (this.ab == 3 && this.Y < 6) {
                  Vector var16 = this.ad[this.Y].b;

                  for (int var19 = 0; var19 < var16.size(); var19++) {
                     f var20;
                     byte[] var24 = (byte[])(var20 = (f)var16.elementAt(var19)).k;
                     if (this.ag + ((var24[0] & 255) << 8 | var24[1] & 255) > 720) {
                        var20.g |= 24;
                     } else {
                        var20.g &= -25;
                     }
                  }
               } else if (this.ab == 5 && (this.d == null || this.d.h() && this.d.g + this.at < System.currentTimeMillis())) {
                  if (this.ao < this.am.size()) {
                     if (this.as != null && this.as[2] == 1) {
                        this.o();
                     }

                     this.as = (byte[])this.am.elementAt(this.ao);
                     this.at = (this.as[1] & 255) << 4;
                     this.ar = this.as[3] == 0 ? 65280 : 16719904;
                     this.aq = b.a(this.as, 5, this.as[4]);
                     var1 = 5 + this.as[4];
                     int var18 = this.as[var1] & 255;
                     int var3 = this.as[var1 + 1] & 255;
                     switch (this.as[0]) {
                        case 0:
                           for (byte var23 = 0; var23 < this.as[var1] << 1; var23 += 2) {
                              this.n[this.as[var1 + 1 + var23] & 0xFF].a = this.as[var1 + 2 + var23] & 255;
                           }
                           break;
                        case 1:
                           this.d = this.n[var18];
                           this.d.a(var3, false);

                           for (int var22 = 0; var22 < this.as[var1 + 2]; var22++) {
                              j var27 = this.n[this.as[var1 + 3 + var22 * 3] & 0xFF];

                              try {
                                 var27.a(this.as[var1 + 4 + var22 * 3] << 8 | this.as[var1 + 5 + var22 * 3] & 255, this.ar);
                              } catch (Exception var14) {
                              }
                           }
                           break;
                        case 2:
                           if (this.n[var18] != null) {
                              this.d = this.n[var18];
                              this.d.a(this.as[var1 + 3] & 255, var3, this.as[var1 + 2] & 255);
                           }
                           break;
                        case 3:
                           if (this.n[var18] != null) {
                              this.d = this.n[var18].d();
                              this.d.a(this.as[var1 + 3] & 255, var3, this.as[var1 + 2] & 255);
                           }
                           break;
                        case 4:
                           this.n[var18].h = (short)(this.as[var1 + 1] << 8);
                           this.n[var18].i = (short)(this.as[var1 + 2] << 8);
                        case 5:
                        default:
                           break;
                        case 6:
                           for (int var4 = 0; var4 < this.as[var1]; var4++) {
                              j var5;
                              if ((var5 = this.n[this.as[var1 + 1 + var4] & 0xFF]).b != 0) {
                                 this.aF.removeElement(var5);
                              }

                              if (var5.b == this.ac.b && this.aF.size() > 1) {
                                 this.m();
                              }
                           }
                     }

                     this.ao++;
                  } else {
                     this.d = null;
                     this.b(this.au);
                  }
               }
            } else {
               long var17 = super.t - this.P;
               boolean var21 = super.t - this.V > 1000L;

               for (int var25 = 0; var25 < this.aF.size(); var25++) {
                  byte[] var6;
                  j var28;
                  if ((var6 = (var28 = (j)this.aF.elementAt(var25)).c)[15] != 0) {
                     int var7 = var28.b;
                     if ((var28.j | var28.k) != 0) {
                        short var8 = (short)(var28.h + a((int)(var28.j * var17 >> 7), -256, 256));
                        short var9 = (short)(var28.i + a((int)(var28.k * var17 >> 7), -256, 256));
                        int var10 = var8 + 128 >> 8;
                        int var11 = var9 + 128 >> 8;
                        if ((var7 == 0 || (x.nextInt() & 15) != 0)
                           && this.b(var10, var11)
                           && (var6[18] == 0 || (var6[16] & 255) <= var10 && (var6[17] & 255) <= var11 && (var6[18] & 255) > var10 && (var6[19] & 255) > var11)
                           )
                         {
                           var28.h = var8;
                           var28.i = var9;
                           if (var7 == 0) {
                              this.Q = var10;
                              this.R = var11;
                              int var30 = this.R * this.ay + this.Q;
                              if (this.o != var30) {
                                 var21 = true;
                                 this.o = var30;
                              }
                           }
                        } else if (var7 == 0) {
                           if (var28.j != 0) {
                              var28.h = (short)((var28.h - 128 & -256) + (var28.j > 0 ? 383 : 128));
                           } else if (var28.k != 0) {
                              var28.i = (short)((var28.i - 128 & -256) + (var28.k > 0 ? 383 : 128));
                           }
                        } else {
                           int var12 = x.nextInt() > 0 ? 60 : -60;
                           short var13 = 14;
                           if (x.nextInt() > 0) {
                              var28.j = var12;
                              var28.k = 0;
                              if (var12 > 0) {
                                 var13 = 206;
                              }
                           } else {
                              var28.j = 0;
                              var28.k = var12;
                              if (var12 > 0) {
                                 var13 = 78;
                              } else {
                                 var13 = 142;
                              }
                           }

                           var28.a(var13, true);
                        }
                     }
                  }
               }

               if (var21) {
                  this.b();
                  this.V = super.t;
               }

               if (super.t - this.g > 10000L) {
                  this.g = super.t;

                  for (int var26 = 0; var26 < this.j.length; var26++) {
                     byte[] var29 = this.j[var26];
                     if (this.m[var29[0]] != 0 && --this.m[var29[0]] == 0) {
                        this.a(var29);
                     }
                  }
               }
            }

            this.P = super.t;
            this.e();
         }
      }
   }

   private void m() {
      this.ac = (j)this.aF.elementAt((this.aF.indexOf(this.ac) + 1) % this.aF.size());
      if (this.ac.b == 0) {
         this.m();
      }
   }

   private void n() {
      if (this.a != null) {
         this.a.j = this.a.k = 0;
         this.a.c();
      }
   }

   private void o() {
      for (int var1 = 0; var1 < this.n.length; var1++) {
         if (this.n[var1] != null) {
            this.n[var1].b();
         }
      }
   }

   public final void c(b var1) {
      this.aG = var1.b(21);
      if (this.aG != 0) {
         this.aH = (byte[])var1.d.get(new Integer(22));
         this.aI = new byte[6];
         this.a(-1);
      }
   }

   public final void a(int var1) {
      Vector var2 = new Vector();

      for (int var3 = 0; var3 < 6; var3++) {
         int var4 = this.aH[var3] < 48 ? 3 : (this.aH[var3] < 78 ? 2 : 1);
         if (var1 == var3) {
            this.aG--;
            this.aI[var3]++;
            this.aH[var3] = (byte)(this.aH[var3] + var4);
         }

         f var5;
         (var5 = new f(String.valueOf('\u000b') + (char)var3 + this.aH[var3] + z[var3])).c = "Click to add: " + var4 + "" + '\u000b' + (char)var3;
         var5.k = A[var3];
         var2.addElement(var5);
      }

      if (this.aG <= 0) {
         this.f();
      } else {
         var2.addElement("Save points for later");
         c var6 = new c(14, "Raises left: " + this.aG, var2);
         if (this.aJ != null) {
            var6.c = this.aJ.c;
            super.w.a(this.aJ, var6);
         } else {
            super.w.a(this, var6, false);
         }

         this.aJ = var6;
      }
   }

   public final void f() {
      super.w.b(this.aJ);
      this.aJ = null;
      b var1;
      (var1 = new b(14, this)).a(1, this.aI);
      super.w.a(this, var1);
   }

   private boolean b(int var1, int var2) {
      byte var3 = (var1 | var2) >= 0 && var1 < this.ay && var2 < this.az ? this.aA[var2 * this.ay + var1] : 0;
      return (this.aB >> (var3 & 15) & this.aC >> ((var3 & 240) >> 4) & 1) == 1 ^ (var3 & 240) == 16;
   }

   public final boolean a(int var1, int var2) {
      if (!this.T) {
         return false;
      }

      switch (var1) {
         case 49:
            var2 = 2;
         case 50:
         case 52:
         case 53:
         case 54:
         case 56:
         default:
            break;
         case 51:
            var2 = 1;
            break;
         case 55:
            var2 = 6;
            break;
         case 57:
            var2 = 5;
      }

      if (this.c) {
         label187:
         switch (this.ab) {
            case 0:
               switch (var2) {
                  case 1:
                  case 2:
                  case 5:
                  case 6:
                     this.m();
                     break label187;
                  case 3:
                  case 4:
                  case 8:
                     this.ab = 4;
                  case 7:
                  default:
                     break label187;
               }
            case 1:
            case 2:
               byte[] var18 = new byte[2];
               System.arraycopy(this.al, 0, var18, 0, 2);
               switch (var2) {
                  case 1:
                     var18[1]--;
                     break;
                  case 2:
                     var18[0]--;
                     break;
                  case 3:
                  case 8:
                     Object var20 = this.ad[this.Y].b.elementAt(this.ad[this.Y].c);
                     this.ag = this.ag + this.ah;
                     if (this.ab == 2) {
                        if ((this.d(var18[0] & 255, var18[1] & 255) & 15) == 0) {
                           break label187;
                        }

                        this.ae.push(new Object[]{new Integer(this.Y), var20, new Integer(this.ag), var18});
                     } else {
                        this.ai.addElement(this.aj);
                        byte[] var7;
                        (var7 = new byte[(this.aj.size() << 1) - 1])[0] = (byte)(this.aj.size() - 1);

                        for (int var8 = 1; var8 < this.aj.size(); var8++) {
                           System.arraycopy(this.aj.elementAt(var8), 0, var7, (var8 << 1) - 1, 2);
                        }

                        this.ae.push(new Object[]{new Integer(this.Y), var20, new Integer(this.ag), var7});
                     }

                     this.ah = 0;
                  case 4:
                     this.ab = 4;
                     this.ah = 0;
                     break label187;
                  case 5:
                     var18[0]++;
                     break;
                  case 6:
                     var18[1]++;
                     break;
                  case 7:
                  default:
                     break label187;
               }

               int var21 = (var18[0] & 255) - this.Z;
               int var22 = (var18[1] & 255) - this.aa;
               if (Math.abs(var21) + Math.abs(var22) + (var21 <= 0 ? 1 : 0) + (var22 <= 0 ? 1 : 0) < 6
                  && (this.ab == 2 || this.b(var18[0] & 255, var18[1] & 255))) {
                  label155:
                  if (this.ab == 1) {
                     if (this.aj.size() > 1) {
                        byte[] var23 = (byte[])this.aj.elementAt(this.aj.size() - 2);
                        if (var18[0] == var23[0] && var18[1] == var23[1]) {
                           this.ah = this.ah - this.ak;
                           this.aj.pop();
                           this.al = var18;
                           break label155;
                        }
                     }

                     if (this.ag + this.ah + this.ak >= 720) {
                        break;
                     }

                     this.aj.addElement(var18);
                     this.ah = this.ah + this.ak;
                  }

                  this.al = var18;
               }
               break;
            case 3:
            case 4:
               label239: {
                  switch (var2) {
                     case -10:
                        this.j();
                        break;
                     case -9:
                     case -7:
                     case -6:
                     case -5:
                     case -4:
                     case -3:
                     case -2:
                     case -1:
                     case 0:
                     case 7:
                     default:
                        return false;
                     case -8:
                     case 4:
                        Object var10;
                        if (this.ab == 4 && !this.ae.isEmpty() && (var10 = this.ae.pop()) != af) {
                           byte[] var13;
                           int var16 = (var13 = (byte[])((f)((Object[])var10)[1]).k)[0] << 8 | var13[1] & 255;
                           if (var13[2] == 1 && !this.ai.isEmpty()) {
                              var16 *= ((Stack)this.ai.pop()).size() - 1;
                           }

                           this.ag -= var16;
                        }

                        this.ab = 4;
                        break;
                     case 1:
                     case 6:
                        if (this.ab == 3) {
                           this.ad[this.Y].a(var1, var2);
                        }

                        this.ab = 3;
                        break;
                     case 2:
                        this.Y--;
                        break;
                     case 3:
                     case 8:
                        if (this.ab == 3) {
                           Object var9;
                           if ((var9 = this.ad[this.Y].b.elementAt(this.ad[this.Y].c)) instanceof f) {
                              f var12;
                              if (!(var12 = (f)var9).c()) {
                                 byte[] var15 = (byte[])var12.k;
                                 this.ak = (var15[0] & 255) << 8 | var15[1] & 255;
                                 if (var15[2] == 2 || var15[2] == 1) {
                                    this.al = new byte[2];
                                    this.al[0] = (byte)(this.a.h >> 8);
                                    this.al[1] = (byte)(this.a.i >> 8);
                                    if (var15[2] == 1) {
                                       Stack var19;
                                       if (!this.ai.isEmpty() && !(var19 = (Stack)this.ai.peek()).isEmpty()) {
                                          System.arraycopy(var19.peek(), 0, this.al, 0, 2);
                                       }

                                       this.ah = 0;
                                    }

                                    this.aj = new Stack();
                                    this.aj.push(this.al);
                                    this.ab = var15[2];
                                    break label239;
                                 }

                                 if (this.ag + this.ak <= 720) {
                                    this.ag = this.ag + this.ak;
                                    this.ae.push(new Object[]{new Integer(this.Y), var9, new Integer(this.ag), new byte[]{(byte)this.ac.b}});
                                 }
                              } else {
                                 super.w
                                    .a(this, new h(30, null, "Not enough time.\nYou can free up time by removing last selection with right screen key"), false);
                              }
                           } else if (var9 == "Try to flee") {
                              super.w.a(this, new h(35, "Confirmation", "Try to flee", new String[]{"Cancel", "Continue"}), false);
                           } else if (var9 == "End turn") {
                              this.j();
                           } else if (var9 == "Change target") {
                              this.ab = 0;
                              break;
                           }

                           this.ab = 4;
                           break;
                        }

                        this.ab = 3;
                        break;
                     case 5:
                        this.Y++;
                  }

                  int var11 = this.aF.size() < 3 ? 7 : 8;
                  this.Y = (this.Y + var11) % var11;
                  Object var14 = this.ad[this.Y].b.elementAt(this.ad[this.Y].c);
                  if (this.ab == 3 && var14 instanceof f) {
                     byte[] var17 = (byte[])((f)var14).k;
                     this.ah = var17[0] << 8 | var17[1] & 255;
                  } else {
                     this.ah = 0;
                  }
               }
         }
      } else {
         switch (var2) {
            case 1:
               this.a.k = -45;
               this.a.a(142, true);
               break;
            case 2:
               this.a.j = -45;
               this.a.a(14, true);
               break;
            case 3:
            case 8:
               if (this.S.size() != 0) {
                  Vector var3 = new Vector();

                  for (int var4 = 0; var4 < this.S.size(); var4++) {
                     byte[] var5;
                     Object var6;
                     if ((var6 = this.S.elementAt(var4)) instanceof j) {
                        var5 = ((j)var6).c;
                     } else {
                        var5 = (byte[])var6;
                     }

                     var3.addElement(new f(this.a(var5[7], var5[8]), var6));
                  }

                  var3.addElement("Cancel");
                  super.w.a(this, new c(32, "Choose action", var3), false);
                  this.n();
               }
               break;
            case 4:
            case 7:
            default:
               return false;
            case 5:
               this.a.j = 45;
               this.a.a(206, true);
               break;
            case 6:
               this.a.k = 45;
               this.a.a(78, true);
         }
      }

      super.w.b();
      return true;
   }

   public final void g() {
      this.ae.removeAllElements();
      this.ae.push(af);
      this.ag = 0;
      this.j();
      this.ab = 4;
   }

   public final void c(int var1, int var2) {
      if (this.T) {
         switch (var1) {
            case 49:
               var2 = 2;
            case 50:
            case 52:
            case 53:
            case 54:
            case 56:
            default:
               break;
            case 51:
               var2 = 1;
               break;
            case 55:
               var2 = 6;
               break;
            case 57:
               var2 = 5;
         }

         switch (var2) {
            case 1:
            case 6:
               this.a.k = 0;
               break;
            case 2:
            case 5:
               this.a.j = 0;
            case 3:
            case 4:
         }

         if ((this.a.j | this.a.k) == 0) {
            this.a.c();
         }
      }
   }

   private byte d(int var1, int var2) {
      return (var1 | var2) >= 0 && var1 < this.ay && var2 < this.az ? this.aA[var2 * this.ay + var1] : 0;
   }

   public final void d() {
      this.n();
   }

   public final void c() {
      this.M = System.currentTimeMillis();
      if (this.T) {
         this.b();
      }

      if (this.T && this.a != null && this.a.d == null) {
         this.a.d = super.w.a("/70");
      }
   }

   public final String h() {
      Vector var1 = new Vector();
      Vector var2 = new Vector();
      StringBuffer var3 = new StringBuffer("\t\tMain quests:\t\b");
      StringBuffer var4 = new StringBuffer("\f\t\tOptional quests:\t\b");

      for (int var5 = 0; var5 < this.h.length; var5++) {
         byte[] var6 = this.h[var5];
         if (this.i[var6[0] & 0xFF] == 2) {
            Integer var7 = new Integer((var6[9] & 255) << 8 | var6[10] & 255);
            if (var6[11] == 1) {
               if (!var1.contains(var7)) {
                  var1.addElement(var7);
                  var3.append("\n\n").append(this.a(var6[9], var6[10]));
               }
            } else if (var6[11] == 2 && !var2.contains(var7)) {
               var2.addElement(var7);
               var4.append("\n\n").append(this.a(var6[9], var6[10]));
            }
         }
      }

      if (var1.isEmpty()) {
         var3.append("\n\nNone");
      }

      if (var2.isEmpty()) {
         var4.append("\n\nNone");
      }

      return var3.append((Object)var4).toString();
   }

   public final Vector i() {
      Vector var1 = new Vector();

      label40:
      for (int var2 = 0; var2 < this.h.length; var2++) {
         byte[] var3;
         if ((var3 = this.h[var2])[12] == 8 && this.i[var3[0] & 0xFF] == 3) {
            try {
               f var4 = new f(new DataInputStream(new ByteArrayInputStream(var3, 14, var3[13])));

               for (int var5 = 0; var5 < this.h.length; var5++) {
                  if (this.h[var5][12] == 9 && this.i[this.h[var5][0] & 0xFF] == 3 && b.a(this.h[var5], 14, this.h[var5][13]).equals(var4.b)) {
                     continue label40;
                  }
               }

               var4.a = this.b(Integer.parseInt(var4.a));
               var1.addElement(var4);
            } catch (IOException var7) {
            }
         }
      }

      return var1;
   }

   public final String a(byte var1, byte var2) {
      return this.b((var1 & 255) << 8 | var2 & 255);
   }

   public final String b(int var1) {
      Integer var2 = new Integer(var1);
      String var3;
      if ((var3 = (String)super.w.f.get(var2)) != null) {
         return var3;
      } else if (this.q == null) {
         return "map texts null";
      } else {
         return (var3 = (String)this.q.get(var2)) != null ? var3 : "WTT #" + var1;
      }
   }

   public final void d(b var1) {
      var1.a(10, this.i);
      var1.b(11, this.I);
      var1.b(12, this.Q);
      var1.b(13, this.R);
      var1.a(14, this.l);
      var1.b(15, this.W);
      var1.b(16, this.X);
   }

   private static final int a(int var0, int var1, int var2) {
      if (var0 < var1) {
         return var1;
      } else {
         return var0 > var2 ? var2 : var0;
      }
   }

   public final void j() {
      synchronized (this) {
         if (this.ab == 6 || this.ab == 5) {
            return;
         }
      }

      this.ab = 6;
      b var1 = new b(13, this);
      ByteArrayOutputStream var2 = new ByteArrayOutputStream();
      DataOutputStream var3 = new DataOutputStream(var2);

      for (int var4 = 0; var4 < this.ae.size(); var4++) {
         Object[] var5 = (Object[])this.ae.elementAt(var4);

         try {
            if (var5 == af) {
               var2.write((byte[])var5[1]);
            } else {
               f var6;
               byte[] var7 = (var6 = (f)var5[1]).b.getBytes();
               var3.write(var7.length);
               var3.write(var7);
               var3.writeShort((Integer)var5[2]);
               var3.write(((byte[])var6.k)[2]);
               var3.write((byte[])var5[3]);
            }

            var1.a(1, var2.toByteArray());
         } catch (IOException var8) {
         }

         var2.reset();
      }

      this.ai.removeAllElements();
      super.w.a(this, var1);
   }

   public final void e(b var1) {
      this.am = var1.a(20);
      this.ao = 0;

      for (int var2 = 0; var2 < this.am.size(); var2++) {
         this.am.elementAt(var2);
         Object var3 = null;
      }

      this.ab = 5;
      this.au = var1;
   }

   static {
      char[] var10000 = new char[]{'?', '-', '+', 'C', 'D'};
      var10000 = new char[]{'?', '-', '+', 'D'};
   }
}
