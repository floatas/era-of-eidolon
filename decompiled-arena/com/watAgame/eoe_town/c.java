package com.watAgame.eoe_town;

import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;

public final class c {
   private final String[] d;
   public final int e;
   public int c;
   public final long a;
   public boolean b = false;

   public c(String[] var1, int var2, int var3, long var4) {
      this.d = var1;
      this.e = var2;
      this.c = var3;
      this.a = var4;
   }

   public final void a(Graphics var1) {
      Font var2;
      int var3 = (var2 = var1.getFont()).getHeight() + 1;
      int var4 = 102;

      for (int var5 = 0; var5 < this.d.length; var5++) {
         var4 = Math.max(var4, var2.stringWidth(this.d[var5]) + 5);
      }

      int var9 = var3 * this.d.length + 5;
      String var6 = null;
      if (this.e == 2) {
         var6 = "Challenge       Back";
         var9 += var3;
      } else if (this.e == 3) {
         var6 = "Fight          Decline";
         var9 += var3;
      }

      if (var6 != null) {
         var4 = Math.max(var4, var2.stringWidth(var6));
      }

      int var7 = 128 - var9 >> 1;
      switch (this.e) {
         case 11:
            var1.setColor(12648384);
            break;
         case 12:
            var1.setColor(16756912);
            break;
         default:
            var1.setColor(16777130);
      }

      var1.fillRect(128 - var4 >> 1, var7, var4, var9);
      var1.setColor(0);
      var1.drawRect(128 - var4 >> 1, var7, var4, var9);

      for (int var8 = 0; var8 < this.d.length; var8++) {
         var1.setColor(var8 != 0 || this.e != 2 && this.e != 3 ? 0 : 255);
         var1.drawString(this.d[var8], 64, var7 + var8 * var3 + 3, 17);
      }

      if (var6 != null) {
         var1.setColor(16711680);
         var1.drawString(var6, 64, var7 + this.d.length * var3 + 3, 17);
      }
   }
}
