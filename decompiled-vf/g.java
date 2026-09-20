import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Hashtable;
import java.util.Stack;
import java.util.Vector;
import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.midlet.MIDlet;

public abstract class g extends Canvas implements Runnable {
   public final Stack a = new Stack();
   public static MIDlet b;
   private e g;
   private e h;
   private volatile boolean i = true;
   private final Thread j = new Thread(this);
   private final boolean k;
   private Image l;
   private Graphics m;
   public final byte[] c;
   public Hashtable d = new Hashtable();
   public Hashtable e = new Hashtable();
   public final Hashtable f = new Hashtable();

   public g(MIDlet var1, e var2) {
      this.c = this.b(0, 0, null);
      b = var1;
      this.h = this.g = var2;
      this.h.w = this;
      this.k = this.isDoubleBuffered();
      this.j.start();
   }

   public final void paint(Graphics var1) {
      try {
         if (!this.k) {
            if (this.l == null) {
               this.l = Image.createImage(this.getWidth(), this.getHeight());
               this.m = this.l.getGraphics();
            }

            this.a(this.m, this.h);
            var1.drawImage(this.l, 0, 0, 20);
         } else {
            this.a(var1, this.h);
         }
      } catch (Throwable var5) {
         try {
            this.a(var1, this.h);
         } catch (Throwable var4) {
            this.a("paint", this.h, null, var4, true);
            this.d();
         }
      }
   }

   public final void keyPressed(int var1) {
      int var2 = 0;
      if (var1 == -6) {
         var2 = 3;
      } else if (var1 == -7) {
         var2 = 4;
      } else if (var1 == -11) {
         var2 = 4;
      } else if (var1 == -10) {
         var2 = -10;
      } else if (var1 == -8) {
         var2 = -8;
      } else {
         try {
            var2 = this.getGameAction(var1);
         } catch (IllegalArgumentException var6) {
         }
      }

      try {
         if (this.h.a(var1, var2)) {
            this.h.e();
         } else {
            try {
               this.a(var1, var2, this.h);
            } catch (Throwable var4) {
               this.a("key(" + var1 + ")", this.h, null, var4, false);
            }
         }
      } catch (Throwable var5) {
         this.a("key_s(" + var1 + ")", this.h, null, var5, false);
      }

      this.d();
   }

   public final void keyReleased(int var1) {
      int var2 = this.getGameAction(var1);
      this.h.c(var1, var2);
   }

   public final void run() {
      while (this.i) {
         long var3;
         this.h.t = var3 = System.currentTimeMillis();

         try {
            this.h.a();
         } catch (Throwable var10) {
            this.a("run_s", this.h, null, var10, false);
            this.d();
         }

         long var1;
         try {
            int var5 = this.a(this.h);
            var1 = Math.min(this.h.v, var5) - System.currentTimeMillis() + var3;
         } catch (Throwable var9) {
            this.a("run", this.h, null, var9, false);
            this.d();
            var1 = 0L;
         }

         if (var1 > 0L) {
            try {
               synchronized (this) {
                  this.wait(var1);
               }
            } catch (InterruptedException var8) {
            }
         } else {
            Thread.yield();
         }
      }
   }

   public final void a() {
      this.i = false;
      this.b();
      b.notifyDestroyed();
   }

   public final synchronized void b() {
      this.notifyAll();
   }

   public final void a(e var1, b var2) {
      var2.w = this;
      this.a(var1, var2, false);
      var2.b();
      this.d();
   }

   public final void b(e var1, b var2, Throwable var3) {
      try {
         this.a(var1, var2, var3);
      } catch (Throwable var5) {
         this.a("resp(" + var2.u + ")", var1, null, var5, false);
      }

      this.b(var2);
   }

   public final void b(e var1, int var2, Object var3) {
      try {
         this.a(var1, var2, var3);
      } catch (Throwable var5) {
         this.a("menu", var1, null, var5, false);
      }
   }

   public static final void a(boolean var0) {
      try {
         System.gc();
         Thread.sleep(300L);
         if (var0) {
            System.gc();
            Thread.sleep(500L);
         }
      } catch (InterruptedException var2) {
      }
   }

   public final void a(e var1, e var2, boolean var3) {
      synchronized (this.a) {
         var2.w = this;
         if (var1 != null && var1 != this.g) {
            int var5;
            if ((var5 = this.a.indexOf(var1)) >= 0) {
               this.a.insertElementAt(var2, var5 + 1);

               while (var3 && var5-- >= 0) {
                  this.a.removeElementAt(0);
               }
            } else {
               if (this.g != null) {
                  this.a.push(this.g);
               }

               this.g = var2;
            }
         } else {
            if (this.g != null) {
               this.a.push(this.g);
            }

            this.g = var2;
            if (var3) {
               this.a.removeAllElements();
            }
         }
      }
   }

   public final e b(e var1) {
      synchronized (this.a) {
         if (var1 != this.g && var1 != null) {
            this.a.removeElement(var1);
         } else if (!this.a.isEmpty()) {
            this.g = (e)this.a.pop();
         }
      }

      return this.g;
   }

   public final void a(e var1, e var2) {
      synchronized (this.a) {
         var2.w = this;
         if (var1 == this.g) {
            this.g = var2;
         } else {
            int var4;
            if ((var4 = this.a.indexOf(var1)) >= 0) {
               this.a.setElementAt(var2, var4);
            }
         }
      }
   }

   public final e c() {
      return this.a.isEmpty() ? this.h : (e)this.a.firstElement();
   }

   public final e c(e var1) {
      if (var1 == this.h && !this.a.isEmpty()) {
         return (e)this.a.peek();
      }

      int var2;
      return (var2 = this.a.indexOf(var1)) > 0 ? (e)this.a.elementAt(var2 - 1) : var1;
   }

   public final void d() {
      if (this.h != this.g && this.g != null) {
         this.h.d();
         this.h = this.g;
         this.h.c();
         this.b();
         this.repaint();
      }
   }

   public abstract void a(e var1, b var2, Throwable var3) throws IOException, Exception;

   public abstract void a(Graphics var1, e var2);

   public abstract void a(int var1, int var2, e var3) throws IOException, Exception;

   public abstract void a(e var1, int var2, Object var3) throws IOException;

   public abstract int a(e var1);

   public abstract void a(String var1, e var2, String var3, Throwable var4, boolean var5);

   public final Image a(String var1) {
      try {
         return Image.createImage(var1);
      } catch (IOException var3) {
         throw new RuntimeException("Unable to read resource '" + var1 + "'");
      }
   }

   private Object a(int var1, int var2) {
      Integer var3 = new Integer((var1 & 0xFF) << 8 | var2 & 0xFF);
      Object var4;
      if ((var4 = this.d.get(var3)) != null) {
         this.e.put(var3, var4);
      }

      return var4;
   }

   public final Image a(int var1, int var2, Vector var3) {
      Object var4;
      if ((var4 = this.a(var1, var2)) instanceof Image) {
         return (Image)var4;
      }

      byte[] var5;
      if ((var5 = (byte[])var4) != null) {
         return Image.createImage(var5, 0, var5.length);
      }

      try {
         Image var6 = Image.createImage("/" + var1 + Integer.toHexString(var2));
         this.a(var1, var2, var6);
         return var6;
      } catch (IOException var7) {
         d(var1, var2, var3);
         return null;
      }
   }

   public final byte[] b(int var1, int var2, Vector var3) {
      byte[] var4;
      if ((var4 = (byte[])this.a(var1, var2)) != null) {
         return var4;
      }

      String var5 = "/" + var1 + Integer.toHexString(var2);
      InputStream var6;
      if ((var6 = this.getClass().getResourceAsStream(var5)) != null) {
         try {
            ByteArrayOutputStream var7 = new ByteArrayOutputStream();

            int var8;
            while ((var8 = var6.read()) >= 0) {
               var7.write(var8);
            }

            var4 = var7.toByteArray();
            this.a(var1, var2, var4);
            return var4;
         } catch (IOException var18) {
            throw new RuntimeException("Unable to read resource '" + var5 + "'");
         } finally {
            try {
               var6.close();
            } catch (IOException var17) {
            }
         }
      } else {
         d(var1, var2, var3);
         return null;
      }
   }

   public final Hashtable a(int var1, Vector var2) {
      Hashtable var3;
      if ((var3 = (Hashtable)this.a(11, var1)) != null) {
         return var3;
      }

      String var4 = "/11" + Integer.toHexString(var1);
      InputStream var5;
      if ((var5 = this.getClass().getResourceAsStream(var4)) != null) {
         try {
            Hashtable var7 = a(new DataInputStream(var5));
            this.a(11, var1, var7);
            return var7;
         } catch (IOException var17) {
            throw new RuntimeException("Unable to read resource '" + var4 + "'");
         } finally {
            try {
               var5.close();
            } catch (IOException var16) {
            }
         }
      } else {
         d(11, var1, var2);
         return null;
      }
   }

   public final DataInputStream c(int var1, int var2, Vector var3) {
      InputStream var4;
      if ((var4 = this.getClass().getResourceAsStream("/" + var1 + Integer.toHexString(var2))) == null) {
         byte[] var5;
         if ((var5 = this.b(var1, var2, var3)) == null) {
            return null;
         }

         var4 = new ByteArrayInputStream(var5);
      }

      return var4 == null ? null : new DataInputStream(var4);
   }

   public final Hashtable b(int var1, Vector var2) {
      Hashtable var3;
      if ((var3 = (Hashtable)this.a(3, var1)) != null) {
         return var3;
      }

      byte[] var4;
      if ((var4 = this.b(3, var1, var2)) != null) {
         try {
            var3 = this.a(new DataInputStream(new ByteArrayInputStream(var4)), var4.length, false);
            this.a(3, var1, var3);
            return var3;
         } catch (IOException var6) {
         }
      }

      return null;
   }

   public final void e() {
      byte[] var1;
      if ((var1 = this.b(10, 0, null)) != null) {
         try {
            this.a(new DataInputStream(new ByteArrayInputStream(var1)), var1.length, true);
            return;
         } catch (IOException var3) {
         }
      }
   }

   public static final void d(int var0, int var1, Vector var2) {
      Integer var3 = new Integer((var0 & 0xFF) << 8 | var1 & 0xFF);
      if (!var2.contains(var3)) {
         var2.addElement(var3);
      }
   }

   public final Hashtable a(DataInputStream var1, int var2, boolean var3) throws IOException {
      Hashtable var4 = var3 ? this.f : new Hashtable();

      while (var2 > 0) {
         Integer var5 = new Integer(var1.readUnsignedShort());
         int var6 = var1.readUnsignedShort();
         var4.put(var5, b.a(var1, var6));
         var2 -= var6 + 2 + 2;
      }

      return var4;
   }

   public static final Hashtable a(DataInputStream var0) throws IOException {
      Hashtable var1 = new Hashtable();
      int var2 = var0.readUnsignedByte();

      while (var2-- > 0) {
         int var3 = var0.readUnsignedByte();
         byte[] var4 = new byte[var0.readUnsignedByte()];
         var0.readFully(var4);
         var1.put(new Integer(var3), var4);
      }

      return var1;
   }

   public static final byte[][] b(DataInputStream var0) throws IOException {
      byte[][] var2 = new byte[var0.readUnsignedByte()][];

      for (int var3 = 0; var3 < var2.length; var3++) {
         int var4 = var0.readUnsignedByte();
         var2[var3] = new byte[var4];
         var0.readFully(var2[var3]);
      }

      return var2;
   }

   public final void a(int var1, int var2, Object var3) {
      Integer var4 = new Integer((var1 & 0xFF) << 8 | var2 & 0xFF);
      this.d.put(var4, var3);
      this.e.put(var4, var3);
   }
}
