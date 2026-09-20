import java.util.Vector;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public final class h extends a {
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
   private char E = 1;
   private Font F = e.r;
   private int G = -1;
   private boolean H;
   private int[] I = new int[]{0, this.E, 0};
   private int J;
   public boolean c;

   public h(int var1, String var2, String var3) {
      this(var1, var2, var3, null);
   }

   public h(int var1, String var2, String var3, String[] var4) {
      this(var1, var2, var3, var4, Integer.MAX_VALUE);
   }

   public h(int var1, String var2, String var3, String[] var4, int var5) {
      this(var1, 220, 300, var2, var3, var4, var5);
   }

   private h(int var1, int var2, int var3, String var4, String var5, String[] var6, int var7) {
      super(var1, var4);
      this.d(var2);
      this.B = System.currentTimeMillis() + var7;
      this.a = var5;
      this.e = var6;
      this.C = var2 - 6 - 2;
      this.d(var2);
      var3 = Math.min(302 - super.q - super.p - 2, var3);
      int var8 = 0;
      int var9 = 0;

      while (var8 < var5.length()) {
         char var10;
         switch (var10 = var5.charAt(var8++)) {
            case '\u0001':
            case '\u0002':
            case '\u0003':
               this.b(var9, var8 - 1);
               var9 = var8;
               this.E = var10;
               break;
            case '\u0004':
               this.b(var9, var8 - 1);
               var9 = var8;
               this.a(0, 0, 0, 0);
               this.H = true;
            case '\u0005':
            case '\b':
            default:
               break;
            case '\u0006':
               this.b(var9, var8 - 1);
               this.D = (var5.charAt(var8) & 255) << 16 | (var5.charAt(var8 + 1) & 255) << 8 | var5.charAt(var8 + 2) & 255;
               var9 = var8 += 3;
               break;
            case '\u0007':
               this.b(var9, var8 - 1);
               var9 = var8;
               this.D = 16173378;
               break;
            case '\t':
               this.b(var9, var8 - 1);
               this.G = var5.charAt(var8);
               this.F = Font.getFont(this.G & 96, this.G & 7, this.G & 24);
               var9 = ++var8;
               break;
            case '\n':
               this.b(var9, var8 - 1);
               var9 = var8;
               this.b();
               break;
            case '\u000b':
               this.b(var9, var8 - 1);
               if (10 + this.I[0] > this.C) {
                  this.b();
               }

               this.a(10, 9, -11, var5.charAt(var8));
               var9 = ++var8;
               break;
            case '\f':
               this.b(var9, var8 - 1);
               var9 = var8;
               if (this.I.length > 3) {
                  this.b();
               }

               this.d.addElement(new int[]{0, 12, 5});
         }
      }

      this.b(var9, var8);
      this.b();
      int var15 = 0;
      int var11 = 0;

      for (int var12 = 0; var12 < this.d.size(); var12++) {
         int[] var13 = (int[])this.d.elementAt(var12);
         this.J = this.J + var13[2];
         var15 = Math.max(var15, var13[0]);
         if (this.J <= var3) {
            var11 = this.J;
         }
      }

      this.d(Math.min(this.J, var11) + 4, var6 != null ? e.s + 4 : 0);
      if (var6 != null) {
         int var16 = var6.length << 2;

         for (int var17 = 0; var17 < var6.length; var17++) {
            var16 += e.r.stringWidth(var6[var17]);
         }

         this.g = var16;
         super.v = 100;
      } else {
         this.g = 0;
         super.v = var7;
      }

      this.d(Math.max(var15 + (super.n - 2 < this.J ? 8 : 2), Math.min(this.g, super.m)));
   }

   private void b(int var1, int var2) {
      if (var1 != var2) {
         int var3 = 0;
         int var4 = var1;

         while (var3 <= this.C - this.I[0] && var4 < var2) {
            int var5 = var4;

            char var6;
            while (var4 < var2 && (var6 = this.a.charAt(var4++)) != 32 && var6 != 45) {
            }

            var6 = this.F.substringWidth(this.a, var5, var4 - var5);
            if (var3 + var6 <= this.C - this.I[0]) {
               var3 += var6;
            } else {
               if (var1 == var5 && this.I.length == 3) {
                  var3 += var6;

                  while (var3 > this.C - this.I[0]) {
                     char var7 = this.a.charAt(--var4);
                     var3 -= this.F.charWidth(var7);
                  }
               } else {
                  var4 = var5;
               }

               if (var3 > 0) {
                  this.a(var3, e.s, var1, var4 - var1);
               }

               this.b();
               var3 = 0;
               var1 = var4;
            }
         }

         this.a(var3, e.s, var1, var4 - var1);
      }
   }

   private void a(int var1, int var2, int var3, int var4) {
      int[] var5 = new int[this.I.length + 5];
      System.arraycopy(this.I, 0, var5, 0, this.I.length);
      var5[this.I.length + 0] = var1;
      var5[this.I.length + 1] = this.G;
      var5[this.I.length + 2] = this.D;
      var5[this.I.length + 3] = var3;
      var5[this.I.length + 4] = var4;
      var5[0] += var1;
      var5[1] = this.E;
      var5[2] = Math.max(var5[2], var2);
      this.I = var5;
   }

   private void b() {
      if (this.H) {
         this.H = false;

         for (byte var1 = 3; var1 < this.I.length; var1 += 5) {
            if (this.I[var1 + 0] == 0) {
               this.I[var1 + 0] = this.C - this.I[0];
               this.I[0] = this.C;
               this.I[var1 + 2] = 6316128;
               break;
            }
         }
      }

      this.d.addElement(this.I);
      this.I = new int[]{0, this.E, e.s};
   }

   public final void a(Graphics var1, boolean var2) {
      this.a(var1);
      var1.setColor(0);
      var1.fillRect(super.k, super.l, super.m, super.n);
      if (super.n - 2 < this.J) {
         e.a(var1, super.k + super.m - 6, super.l + 1, super.n - 2, this.f * 10, super.n - 2, this.J, 11369747, 16173378);
      }

      int var3 = -1;
      int var4 = Math.max(-this.f * 10 + 1, -this.J + super.n - 1);
      int var5 = super.k + 1;
      var1.setClip(super.k + 1, super.l + 1, super.m - 2, super.n - 2);

      for (int var6 = 0; var6 < this.d.size() && var4 <= super.n; var6++) {
         int[] var7 = (int[])this.d.elementAt(var6);
         if (var4 + var7[2] > 0) {
            int var8 = var5;
            switch (var7[1]) {
               case 2:
                  var8 = super.k + super.m - 7 - var7[0];
                  break;
               case 3:
                  var8 += super.m - 7 - var7[0] >> 1;
                  break;
               case 12:
                  var1.drawLine(super.k + 5, super.l + 2 + var4, super.k + super.m - (super.n - 2 < this.J ? 12 : 6), super.l + 2 + var4);
            }

            for (byte var9 = 3; var9 < var7.length; var9 += 5) {
               if (var7[var9 + 3] == -11) {
                  Image var10 = a.j;
                  if (a.j == null) {
                     a.j = var10 = super.w.a("/symb.png");
                  }

                  int var11 = super.l + var4 + (var7[2] - 9 >> 1);
                  e.a(var1, var10, var7[var9 + 4] * 9, 0, 9, 9, 0, var8, var11, 20);
               } else {
                  var1.setColor(var7[var9 + 2]);
                  if (var7[var9 + 4] == 0) {
                     int var20 = this.F.charWidth('.');

                     for (int var22 = 0; var22 < var7[var9 + 0]; var22 += var20) {
                        var1.drawChar('.', var8 + var22, 0 + super.l + var4, 20);
                     }

                     var8 += var7[var9 + 0];
                     continue;
                  }

                  if (var3 != var7[var9 + 1]) {
                     Font var19 = Font.getFont((var3 = var7[var9 + 1]) & 96, var3 & 7, var3 & 24);
                     var1.setFont(var19);
                  }

                  var1.drawSubstring(this.a, var7[var9 + 3], var7[var9 + 4], var8, 0 + super.l + var4, 20);
               }

               var8 += var7[var9 + 0];
            }
         }

         var4 += var7[2];
      }

      if (this.e != null) {
         var1.setClip(super.k, super.l + super.n + 1, super.m, super.p - 1);
         var1.setColor(4210752);
         var1.fillRect(super.k, super.l + super.n, super.m, super.p);
         var1.setFont(e.r);
         var1.setClip(super.k + 1, super.l + super.n, super.m - 2, super.p);
         int var13;
         if (this.g < super.m) {
            var13 = super.k + (super.m - this.g >> 1);
         } else if (this.b == 0) {
            var13 = super.k + 3;
         } else {
            int var14 = 0;

            for (int var16 = 0; var16 < this.b; var16++) {
               var14 += e.r.stringWidth(this.e[var16]) + 4;
            }

            if (this.h + var14 < super.k + 10) {
               this.h = 12 - var14;
            } else if (this.h + var14 + e.r.stringWidth(this.e[this.b]) > super.k + super.m - 10) {
               this.h = super.m - 12 - var14 - e.r.stringWidth(this.e[this.b]);
            }

            var13 = super.k + 3 + this.h;
         }

         for (int var15 = 0; var15 < this.e.length; var15++) {
            int var17 = e.r.stringWidth(this.e[var15]) + 1;
            int var12;
            int var18;
            int var21;
            int var23;
            if (this.b == var15) {
               var18 = 12686873;
               var21 = var23 = (this.i = !this.i) ? 16777215 : 0;
               var12 = 16645016;
            } else {
               var18 = 9137427;
               var21 = 11898650;
               var23 = 6311968;
               var12 = 16173378;
            }

            var1.setColor(var18);
            var1.fillRect(var13 - 1, super.l + super.n + 3, var17, e.s);
            var1.setColor(var21);
            var1.drawLine(var13 - 2, super.l + super.n + 2, var13 + var17 - 1, super.l + super.n + 2);
            var1.drawLine(var13 - 2, super.l + super.n + 2, var13 - 2, super.l + super.n + super.p - 2);
            var1.setColor(var23);
            var1.drawLine(var13 - 2, super.l + super.n + super.p - 2, var13 + var17 - 1, super.l + super.n + super.p - 2);
            var1.drawLine(var13 + var17 - 1, super.l + super.n + 2, var13 + var17 - 1, super.l + super.n + super.p - 2);
            var1.setColor(var12);
            var1.drawString(this.e[var15], var13, 0 + super.l + super.n + 3, 20);
            var13 += var17 + 3;
         }
      }
   }

   public final void a() {
      if (this.B < super.t) {
         super.w.b(this);
         super.w.d();
      }

      this.e();
   }

   public final boolean a(int var1, int var2) {
      if (var2 != 1 && var2 != 6) {
         if (this.e == null || var2 != 2 && var2 != 5) {
            if (var2 != 8 && var2 != 3 && var2 != 4) {
               return false;
            }

            if (this.e != null && var2 != 4) {
               super.w.b(this, this.b, this.e[this.b]);
            } else if (!this.c) {
               super.w.b(this);
            }
         } else {
            this.b = (this.b + this.e.length + (var2 == 5 ? 1 : -1)) % this.e.length;
         }
      } else {
         this.f = Math.max(0, Math.min(this.f + (var2 == 1 ? -1 : 1), (this.J - super.n + 1 + 10) / 10));
      }

      return true;
   }
}
