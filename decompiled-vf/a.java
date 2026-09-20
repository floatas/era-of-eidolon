import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public class a extends e {
   public static Image j;
   private static Image x;
   public int k;
   public int l;
   public int m;
   public int n;
   public String o;
   public int p;
   public final int q;
   private int y;
   private int z;
   private int A;

   public a(int var1, String var2) {
      super(var1);
      this.o = var2;
      this.q = var2 == null ? 0 : e.s + 1;
   }

   public a(int var1, String var2, int var3, int var4) {
      this(var1, var2);
      this.y = var3;
      this.z = var4;
   }

   public final void d(int var1) {
      this.A = var1;
      this.b(this.o);
      this.k = Math.max(0, 240 - this.m >> 1);
   }

   public final void b(String var1) {
      this.o = var1;
      if (var1 != null) {
         this.m = Math.max(this.A, e.r.stringWidth(var1) + 1);
      } else {
         this.m = this.A;
      }
   }

   public final void d(int var1, int var2) {
      this.p = var2 == 0 ? 0 : var2 + 1;
      this.n = Math.min(320 - this.q - var2 - 2, var1);
      if (this.y != 0) {
         this.n = Math.min(this.n, this.z - this.y - this.q - 2);
         this.l = (this.z - this.y - this.n - this.q >> 1) + this.q + this.y;
      } else {
         this.l = (320 - this.n - this.q - var2 >> 1) + this.q;
      }
   }

   public final void a(Graphics var1) {
      var1.setFont(e.r);
      if (x == null) {
         x = super.w.a("/menu.png");
      }

      int var2 = this.k;

      do {
         int var3 = Math.min(x.getWidth(), this.m + this.k - var2);
         e.a(var1, x, 0, 0, var3, x.getHeight(), 0, var2, this.l - this.q - 9, 20);
         e.a(var1, x, 0, 0, var3, x.getHeight(), 0, var2, this.l + this.n + this.p, 20);
      } while ((var2 += x.getWidth()) < this.m + this.k);

      var1.setClip(0, 0, 240, 320);
      var1.setColor(5263424);
      var1.drawRect(this.k - 2, this.l - this.q - 1 - 9, this.m + 3, this.n + 1 + 18 + this.q + this.p);
      var1.setColor(11369747);
      var1.drawLine(this.k - 1, this.l - this.q - 9, this.k - 1, this.l + this.n + 9 + this.p - 1);
      var1.drawLine(this.k + this.m, this.l - this.q - 9, this.k + this.m, this.l + this.n + 9 + this.p - 1);
      if (this.q > 0) {
         var1.setColor(8610337);
         var1.fillRect(this.k, this.l - this.q, this.m, this.q);
         var1.setColor(16173378);
         var1.drawString(this.o, this.k + (this.m - 1 >> 1) + 1, 0 + this.l - this.q, 17);
         var1.setColor(11369747);
         var1.drawLine(this.k, this.l - 1, this.k + this.m, this.l - 1);
      }

      if (this.p > 0) {
         var1.setColor(11369747);
         var1.drawLine(this.k, this.l + this.n, this.k + this.m, this.l + this.n);
      }
   }
}
