package com.watAgame.eoe_town;

final class a implements Runnable {
   private final b e;
   private final int c;
   private boolean d;
   private final String b;
   private final String a;

   public a(b var1, int var2) {
      this.e = var1;
      this.c = var2;
      this.d = false;
      switch (this.c) {
         case 2:
            this.b = "battleping.pl";
            this.a = "";
            break;
         default:
            this.b = "ping.pl";
            this.a = "¦onlinestatus=";
      }

      if (!this.d) {
         this.d = true;
         new Thread(this).start();
      }
   }

   public final void run() {
      while (this.d) {
         try {
            short var1 = 10000;
            if (this.e.Y == 41) {
               var1 = 5000;
            } else if (this.c == 2) {
               var1 = 3000;
            }

            Thread.sleep(var1);
            if (!this.d) {
               return;
            }

            StringBuffer var2;
            (var2 = new StringBuffer(this.e.P)).append(this.b);
            new d(this.e, this.c == 2 ? 1 : 0, var2.toString(), this.c == 1 ? this.a + this.e.w() : this.a).join();
         } catch (Exception var4) {
            this.e.a("ping", var4, false);
         }
      }
   }

   public final void a() {
      this.d = false;
   }
}
