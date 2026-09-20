import java.io.IOException;
import java.util.Vector;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public final class c extends a {
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

   public c(int var1, String var2, Vector var3) {
      super(var1, var2);
      this.b = var3;
      this.b();
   }

   public c(int var1, String var2, Vector var3, int var4, int var5) {
      super(var1, var2, var4, var5);
      this.b = var3;
      this.b();
   }

   public final void b() {
      this.g = 0;
      this.h = a;
      boolean var1 = false;

      for (int var2 = 0; var2 < this.b.size(); var2++) {
         if (this.b.elementAt(var2) instanceof f) {
            f var3 = (f)this.b.elementAt(var2);
            this.g = Math.max(this.g, var3.a());
            if (var3.c != null) {
               var1 = true;
            }

            if (var3.f >= 0) {
               this.h = 14;
            }
         } else {
            this.g = Math.max(this.g, f.a(this.b.elementAt(var2).toString(), true));
         }
      }

      int var4 = var1 ? Math.max(a, 9) + 2 : 0;
      this.d(this.b.size() * this.h + 2, var4);
      this.G = Math.min(this.b.size(), (super.n - 2) / this.h);
      this.H = this.b.size() > this.G ? 6 : 0;
      this.d(this.g + 2 + this.H);
      this.d(this.G * this.h + 2, var4);
      this.c = Math.min(this.c, this.b.size() - 1);
   }

   public final void a(Graphics var1, boolean var2) {
      var1.setColor(0);
      var1.fillRect(super.k, super.l, super.m, super.n);
      var1.setColor(4210752);
      var1.fillRect(super.k, super.l + super.n, super.m, super.p);
      this.a(var1);
      if (this.H != 0) {
         this.f = Math.min(this.f, this.c - 1);
         this.f = Math.max(this.f, Math.max(this.c - this.G + 2, 0));
         this.f = Math.min(this.f, this.b.size() - this.G);
         e.a(var1, super.k + super.m - 6, super.l + 1, super.n - 2, this.f, this.G, this.b.size(), 11369747, 16173378);
      }

      int var3 = super.k + 1;
      int var4 = super.l + 1 + (this.h - a >> 1);
      int var5 = super.l + 1 + (this.h - 14 >> 1);
      int var6 = 0;

      for (int var7 = this.f; var7 < this.b.size() && var6 <= super.n - this.h; var7++) {
         f var8 = this.b.elementAt(var7) instanceof f ? (f)this.b.elementAt(var7) : null;
         if (var7 == this.c) {
            if (var8 != null && (var8.g & 48) != 0) {
               switch (var8.g & 48) {
                  case 16:
                     var1.setColor(7171437);
                     break;
                  case 32:
                     var1.setColor(13434880);
               }
            } else {
               var1.setColor(12686873);
            }

            if (var8 != null && var8.f >= 0) {
               var1.fillRect(var3 + 14, super.l + var6 + 1, super.m - this.H - 2 - 14, this.h);
            } else {
               var1.fillRect(var3, super.l + var6 + 1, super.m - this.H - 2, this.h);
            }

            var1.setColor(16645016);
         } else {
            var1.setColor(16173378);
         }

         if (var8 != null) {
            switch (var8.g & 48) {
               case 16:
                  var1.setColor(13290186);
                  break;
               case 32:
                  var1.setColor(var7 == this.c ? 16759739 : 16740464);
            }

            if (var8.e == 0 && var8.i == null) {
               if (var8.f >= 0) {
                  Image var14 = d;
                  if (d == null) {
                     try {
                        d = var14 = Image.createImage("/items.png");
                     } catch (IOException var12) {
                     }
                  }

                  int var15 = var8.f * 14 % var14.getWidth();
                  int var16 = var8.f * 14 / var14.getWidth() * 14;
                  e.a(var1, var14, var15, var16, 14, 14, 0, var3, var5 + var6, 20);
                  this.a(var1, var8.a, var3 + 14 + 1, var4 + var6, this.g - 14 - 1, this.h);
               } else {
                  this.a(var1, var8.a, var3, var4 + var6, this.g, this.h);
               }
            } else {
               String var9;
               if (var8.e == 0) {
                  if (var8.j >= 0) {
                     var9 = var8.i[var8.j][0].toString();
                  } else {
                     var9 = var8.a;
                     var1.setColor(16645016);
                  }
               } else if ((var7 != this.c || !this.B) && var8.d.length() <= 0) {
                  var9 = var8.a;
                  var1.setColor(16645016);
               } else {
                  var9 = var8.d.toString();
               }

               int var10 = super.l + var6 + (this.h >> 1);
               var1.drawLine(var3, var10 - 3, var3, var10 + 3);
               var1.drawLine(var3 + 1, var10 - 2, var3 + 1, var10 + 2);
               var1.drawLine(var3 + 2, var10 - 1, var3 + 2, var10 + 1);
               var1.drawLine(var3 + 3, var10, var3 + 3, var10);
               var1.drawString(var9, var3 + 5, 0 + var4 + var6, 20);
               if (var7 == this.c && this.B && (System.currentTimeMillis() - this.F < 1000L || (this.i = !this.i))) {
                  var1.setColor(16777215);
                  int var11 = var3 + 5 + e.r.substringWidth(var9, 0, this.E);
                  var1.fillRect(var11, var4 + var6, 2, a);
               }
            }
         } else {
            this.a(var1, this.b.elementAt(var7).toString(), var3, var4 + var6, this.g, this.h);
         }

         var6 += this.h;
      }

      String var13;
      if (super.p != 0 && this.b.elementAt(this.c) instanceof f && (var13 = ((f)this.b.elementAt(this.c)).c) != null) {
         var1.setColor(16645016);
         this.a(var1, var13, var3, super.l + super.n + 2, super.m - 2, this.h);
      }
   }

   public final void a(Graphics var1, String var2, int var3, int var4, int var5, int var6) {
      int var7 = var1.getColor();
      int var8 = 0;
      int var9 = 0;
      byte var10 = 0;

      while (var9 < var2.length()) {
         while (var9 < var2.length() && (var13 = var2.charAt(var9)) > 11) {
            var9++;
         }

         var1.drawSubstring(var2, var8, var9 - var8, var3, 0 + var4, 20);
         var3 += e.r.substringWidth(var2, var8, var9 - var8);
         var8 = var9;
         switch (var13) {
            case '\u0002':
            case '\u0004':
               var3 += var5 - f.a(var2, false);
            case '\u0001':
               var8 = ++var9;
               break;
            case '\u0003':
               var3 += var5 - f.a(var2, false) >> 1;
               var8 = ++var9;
            case '\u0005':
            case '\b':
            case '\t':
            case '\n':
            default:
               break;
            case '\u0006':
               var1.setColor((var2.charAt(var9 + 1) & 255) << 16 | (var2.charAt(var9 + 2) & 255) << 8 | var2.charAt(var9 + 3) & 255);
               var8 = var9 += 4;
               break;
            case '\u0007':
               var1.setColor(var7);
               var8 = ++var9;
               break;
            case '\u000b':
               Image var11 = a.j;
               if (a.j == null) {
                  a.j = var11 = super.w.a("/symb.png");
               }

               e.a(var1, var11, var2.charAt(++var9) * '\t', 0, 9, 9, 0, var3, var4 + (var6 - 9 >> 1), 20);
               var3 += 10;
               var8 = ++var9;
               var10 = 0;
         }
      }
   }

   public final void a() {
      this.e();
   }

   public final boolean a(int var1, int var2) {
      if (this.b.size() <= 0) {
         return false;
      }

      long var3 = System.currentTimeMillis();
      if (this.B && (var1 >= 48 && var1 <= 57 || var1 == 42 || var1 == -7 || var1 == -8)) {
         f var8 = (f)this.b.elementAt(this.c);
         if (var1 != -7 && var1 != -8) {
            String var6 = var1 == 42 ? "@%&/()=+*" : e[var1 - 48];
            if (this.C == var1 && var3 - this.F < 1000L) {
               var8.d.setCharAt(this.E - 1, var6.charAt(++this.D % var6.length()));
               this.F = var3;
            } else {
               this.D = 0;
               if (var8.d.length() < var8.e) {
                  var8.d.insert(this.E++, var6.charAt(this.D % var6.length()));
                  this.C = var1;
                  this.F = var3;
               }
            }

            var8.d.setCharAt(0, Character.toUpperCase(var8.d.charAt(0)));

            for (int var7 = 1; var7 < var8.d.length(); var7++) {
               var8.d.setCharAt(var7, Character.toLowerCase(var8.d.charAt(var7)));
            }

            this.g = Math.max(this.g, var8.a());
            this.d(this.g + 2 + this.H);
            this.i = true;
         } else {
            if (this.E > 0) {
               var8.d.deleteCharAt(--this.E);
            }

            if (this.E == 0 && var8.d.length() > 0) {
               var8.d.setCharAt(0, Character.toUpperCase(var8.d.charAt(0)));
            }
         }
      } else if (this.B && var2 == 2 && this.E > 0) {
         this.F = 0L;
         this.E--;
      } else if (this.B && var2 == 5) {
         this.F = 0L;
         if (this.E < ((f)this.b.elementAt(this.c)).d.length()) {
            this.E++;
         }
      } else if (var2 != 6 && var2 != 1) {
         if (var2 != 8 && var2 != 3) {
            return false;
         }

         if (this.b.elementAt(this.c) instanceof f) {
            f var5;
            if (!(var5 = (f)this.b.elementAt(this.c)).c()) {
               if (var5.e != 0) {
                  if (this.B = !this.B) {
                     this.E = var5.d.length();
                     super.v = 400;
                     super.w.b();
                  } else {
                     super.v = Integer.MAX_VALUE;
                  }
               } else if (var5.i != null) {
                  var5.j = (var5.j + 1) % var5.i.length;
                  this.g = Math.max(this.g, var5.a());
                  this.d(this.g + 2 + this.H);
               } else {
                  super.w.b(this, this.c, this.b.elementAt(this.c));
               }
            }
         } else {
            super.w.b(this, this.c, this.b.elementAt(this.c));
         }
      } else {
         this.c = (this.c + this.b.size() + (var2 == 6 ? 1 : -1)) % this.b.size();
         this.B = false;
         super.v = Integer.MAX_VALUE;
      }

      return true;
   }

   public final f a(int var1) {
      return (f)this.b.elementAt(var1);
   }

   public final f f() {
      return (f)this.b.elementAt(this.c);
   }

   public final void a(Object var1) {
      if (var1 instanceof f) {
         var1 = ((f)var1).a;
      }

      for (int var2 = 0; var2 < this.b.size(); var2++) {
         Object var3;
         if ((var3 = this.b.elementAt(var2)) instanceof f) {
            if (((f)var3).a.equals(var1)) {
               this.b.removeElementAt(var2);
               this.b();
               return;
            }
         } else if (var3.equals(var1)) {
            this.b.removeElementAt(var2);
            this.b();
            return;
         }
      }
   }
}
