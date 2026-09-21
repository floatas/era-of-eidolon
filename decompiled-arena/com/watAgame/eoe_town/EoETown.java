package com.watAgame.eoe_town;

import java.util.Vector;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Form;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.List;
import javax.microedition.lcdui.StringItem;
import javax.microedition.lcdui.TextBox;
import javax.microedition.midlet.MIDlet;
import javax.microedition.rms.RecordStore;
import javax.microedition.rms.RecordStoreException;

public class EoETown extends MIDlet implements CommandListener {
   private final Command n = new Command("Back", 2, 1);
   private final Command h = new Command("Reply", 8, 2);
   private final Command j = new Command("Read", 8, 1);
   private final Command i = new Command("Delete", 8, 2);
   private final Command q = new Command("Cancel", 3, 1);
   private final Command k = new Command("Send", 4, 1);
   private b p;
   private String d;
   private static final Image r = a("read", true);
   private static final Image f = a("unread", true);
   private List o;
   private List e;
   private TextBox s;
   private Form g = new Form(null);
   private Displayable m;
   private int c;
   private final Form a;
   protected Image b;
   private static final String[] l = new String[]{
      "- Installing game -#Welcome to the World#of Eidolon. U are no#rookie anymore & U",
      "- Installed 20% -#have already proven#your worth as a great#Hero.",
      "- Installed 40% -#Queen Furyana#therefore gladly#welcomes U to#Dagonar, the",
      "- Installed 60% -#capital of her region.#Here U can improve#even more &",
      "- Installed 80% -#acquire more#advanced skills,#spells & items. Good#luck!"
   };

   public EoETown() {
      new List("", 3, new String[]{"Read", "Reply", "Delete", "Town", "Back"}, null);
      this.a = new Form("Please wait");
   }

   public final void startApp() {
      this.a.append(new StringItem("Please wait", ""));
      Displayable var1;
      if ((var1 = Display.getDisplay(this).getCurrent()) == null) {
         this.p = new b(this);
         Display.getDisplay(this).setCurrent(this.p);
      } else {
         Display.getDisplay(this).setCurrent(var1);
      }
   }

   protected final void pauseApp() {
   }

   protected final void destroyApp(boolean var1) {
      if (this.p.Z != null) {
         this.p.Z.a();
      }

      this.p.az = null;
      if (var1) {
         this.notifyDestroyed();
      }
   }

   protected static final String a(String var0, int var1) {
      RecordStore var2 = null;

      try {
         var2 = RecordStore.openRecordStore(var0, false);

         try {
            if (var1 == -1) {
               var1 = var2.getNumRecords();
            }

            byte[] var3;
            return (var3 = var2.getRecord(var1)) == null ? "" : com.watAgame.eoe_town.d.a(var3);
         } finally {
            try {
               var2.closeRecordStore();
            } catch (RecordStoreException var13) {
            }
         }
      } catch (RecordStoreException var15) {
         return "";
      }
   }

   protected static final void a(String var0, Vector var1) throws RecordStoreException {
      RecordStore var2 = RecordStore.openRecordStore(var0, true);
      Object var3 = null;
      boolean var4 = false;

      try {
         for (int var5 = 0; var5 < var1.size(); var5++) {
            byte[] var6 = com.watAgame.eoe_town.d.a((String)var1.elementAt(var5));
            var2.addRecord(var6, 0, var6.length);
            if (var5 % 4 == 0) {
               Thread.yield();
            }
         }
      } finally {
         try {
            var2.closeRecordStore();
         } catch (RecordStoreException var12) {
         }
      }
   }

   protected static final void a(String var0, String var1) throws RecordStoreException {
      RecordStore var2 = RecordStore.openRecordStore(var0, true);

      try {
         byte[] var3 = com.watAgame.eoe_town.d.a(var1);
         var2.addRecord(var3, 0, var3.length);
      } finally {
         try {
            var2.closeRecordStore();
         } catch (RecordStoreException var9) {
         }
      }
   }

   protected static final void a(String var0) throws RecordStoreException {
      RecordStore var1;
      (var1 = RecordStore.openRecordStore(var0, false)).closeRecordStore();

      try {
         RecordStore.deleteRecordStore(var0);
      } finally {
         var1.closeRecordStore();
         RecordStore.deleteRecordStore(var0);
      }
   }

   public final void commandAction(Command var1, Displayable var2) {
      if (this.p.bc) {
         if (var2 == this.o) {
            this.c = this.o.getSelectedIndex();
            if (this.c >= 0) {
               this.p.aj = this.p.bv[this.c][2];
               this.d = this.o.getString(this.o.getSelectedIndex());
            }

            if (var1 == this.j || var1 == List.SELECT_COMMAND) {
               Display.getDisplay(this).setCurrent(this.a);
               this.g.setTitle("Please wait");

               while (this.g.size() > 0) {
                  this.g.delete(0);
               }

               this.p.b();
               return;
            }

            if (var1 == this.h) {
               this.p.aJ = this.o.getString(this.o.getSelectedIndex());
               this.a();
               return;
            }

            if (var1 == this.i) {
               this.p.h(this.c);
               this.o.delete(this.c);
               if (this.o.size() == 0) {
                  this.a(new String[0][0]);
               }

               Display.getDisplay(this).setCurrent(this.a);
               return;
            }

            if (var1 == this.n) {
               this.p.k();
               return;
            }
         } else if (var2 == this.s) {
            if (var1 == this.q) {
               Display.getDisplay(this).setCurrent(this.m);
               return;
            }

            if (var1 == this.k) {
               this.p.ag = this.s.getString();
               this.p.s();
               return;
            }
         } else if (var2 == this.g) {
            if (var1 == this.n) {
               this.b();
               return;
            }

            if (var1 == this.h) {
               this.p.aJ = this.d;
               this.a();
               return;
            }

            if (var1 == this.i) {
               this.p.h(this.c);
               this.o.delete(this.c);
               Display.getDisplay(this).setCurrent(this.a);
               return;
            }
         } else if (var2 == this.e) {
            if (var1 == this.n) {
               this.p.k();
               return;
            }

            this.p.aJ = this.e.getString(this.e.getSelectedIndex());
            this.a();
         }
      }
   }

   public final void a(String[][] var1) {
      Display.getDisplay(this).setCurrent(this.a);
      int var2 = 10;

      while (!this.a.isShown() && var2-- > 0) {
         try {
            Thread.sleep(100L);
         } catch (InterruptedException var4) {
         }
      }

      this.o = new List("Inbox", 3);
      if (var1.length > 0) {
         for (int var3 = 0; var3 < var1.length; var3++) {
            this.o.append(var1[var3][0], var1[var3][1].equals("1") ? r : f);
         }

         this.o.addCommand(this.j);
         this.o.addCommand(this.i);
         this.o.addCommand(this.h);
      }

      this.o.addCommand(this.n);
      this.o.setCommandListener(this);
      Display.getDisplay(this).setCurrent(this.o);
   }

   public final void a(String[] var1) {
      this.e = new List("Names", 3, var1, null);
      this.e.addCommand(this.n);
      this.e.setCommandListener(this);
      this.m = Display.getDisplay(this).getCurrent();
      Display.getDisplay(this).setCurrent(this.e);
   }

   final void b() {
      this.o.set(this.o.getSelectedIndex(), this.p.bv[this.o.getSelectedIndex()][0], r);
      this.m = Display.getDisplay(this).getCurrent();
      Display.getDisplay(this).setCurrent(this.o);
   }

   final void a() {
      this.s = new TextBox("To: ".concat(this.p.aJ), null, 120, 0);
      this.s.addCommand(this.k);
      this.s.addCommand(this.q);
      this.s.setCommandListener(this);
      this.m = Display.getDisplay(this).getCurrent();
      Display.getDisplay(this).setCurrent(this.s);
   }

   final void c() {
      this.p.bc = true;
      this.g.setTitle(this.p.G);
      this.g.append("From: " + this.d + "\n");
      this.g.append(this.p.ag);
      this.g.addCommand(this.i);
      this.g.addCommand(this.h);
      this.g.addCommand(this.n);
      this.g.setCommandListener(this);
      this.m = Display.getDisplay(this).getCurrent();
      Display.getDisplay(this).setCurrent(this.g);
   }

   static final Image a(String var0, boolean var1) {
      for (int var2 = 5; var2 > 0; var2--) {
         try {
            System.gc();
            Thread.sleep(200L);
            return Image.createImage("/" + var0 + ".png");
         } catch (Throwable var4) {
            if (var0.equals("unread")) {
               return a("mail", true);
            }
         }
      }

      return var1 ? Image.createImage(100, 1) : null;
   }

   public static final String[] b(String var0) {
      Vector var1 = new Vector();
      int var2 = 0;

      int var3;
      while ((var3 = var0.indexOf(35, var2)) != -1) {
         var1.addElement(var0.substring(var2, var3));
         var2 = var3 + 1;
      }

      var1.addElement(var0.substring(var2));
      String[] var5 = new String[var1.size()];

      for (int var4 = 0; var4 < var1.size(); var4++) {
         var5[var4] = (String)var1.elementAt(var4);
      }

      return var5;
   }

   public static final void a(Graphics var0, int var1, int var2, int var3, int var4, int var5, int var6) {
      int var7 = var4 * (var3 - 7) / var6;
      int var8 = var5 * (var3 - 7) / var6;
      var0.setColor(8421504);
      var0.fillRect(var1, var2 + 4 + var7, 5, var8);
      var0.setColor(0);
      var0.drawLine(var1 + 2, var2, var1 + 2, var2);
      var0.drawLine(var1 + 1, var2 + 1, var1 + 3, var2 + 1);
      var0.drawLine(var1, var2 + 2, var1 + 4, var2 + 2);
      int var9 = var2 + var3;
      var0.drawLine(var1, var9 - 3, var1 + 4, var9 - 3);
      var0.drawLine(var1 + 1, var9 - 2, var1 + 3, var9 - 2);
      var0.drawLine(var1 + 2, var9 - 1, var1 + 2, var9 - 1);
   }

   public static final void a(Graphics var0) {
      boolean var1 = false;
      var0.setColor(7255290);
      var0.fillRect(0, 0, 128, 128);
      var0.setColor(0);
      var0.setFont(com.watAgame.eoe_town.b.at);
      int var2 = com.watAgame.eoe_town.b.at.getHeight() + 4;
      int var3 = com.watAgame.eoe_town.b.cn.getHeight() + 4;
      int var4 = (var2 << 1) + (var3 << 2);
      int var5 = 128 - var4 >> 1;
      var0.drawString("©watAgame 2004", 64, var5, 17);
      var5 += var3;
      var0.setFont(com.watAgame.eoe_town.b.cn);
      int var7;
      var0.drawString("All rights reserved.", 64, var7 = var5 + var3, 17);
      var0.drawString("Era of Eidolon™", 64, var5 = var7 + var3, 17);
      int var9;
      var0.drawString("is a trademark", 64, var9 = var5 + var3, 17);
      var0.drawString("of watAgame ApS.", 64, var9 + var3, 17);
   }

   public final void a(Graphics var1, int var2) {
      if (this.b == null) {
         this.b = a("logo", true);
      }

      var1.drawImage(this.b, 0, 0, 20);
      if (var2 >= 0) {
         Font var3 = com.watAgame.eoe_town.b.cn;
         var1.setFont(var3);
         int var4;
         var4 = (var4 = var3.getHeight()) + (var4 >> 2);
         String[] var5 = b(l[var2 % 5]);
         int var6 = 102;

         for (int var7 = 0; var7 < var5.length; var7++) {
            var6 = Math.max(var6, var3.stringWidth(var5[var7]) + 5);
         }

         int var10 = var4 * l.length + 5;
         var1.setColor(16777130);
         var1.fillRect(128 - var6 >> 1, 128 - var10 >> 1, var6, var10);
         var1.setColor(0);
         var1.drawRect(128 - var6 >> 1, 128 - var10 >> 1, var6, var10);

         for (int var8 = 0; var8 < var5.length; var8++) {
            var1.setColor(var8 == 0 ? 255 : 0);
            var1.drawString(var5[var8], 64, (128 - var10 >> 1) + var8 * var4 + 3, 17);
         }
      }
   }

   static final int a(int var0) {
      int var1 = 0;
      int var2 = var0 >= 65536 ? 1073741824 : 16384;

      do {
         int var3 = var1 + var2;
         if (var0 >= var3) {
            var0 -= var3;
            var1 = var3 + var2;
         }

         var1 >>= 1;
      } while ((var2 >>= 2) != 0);

      return var1;
   }
}
