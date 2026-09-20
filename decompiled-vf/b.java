import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Random;
import java.util.Vector;
import javax.microedition.io.Connector;
import javax.microedition.io.HttpConnection;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public final class b extends a implements Runnable {
   public static String a = "prod";
   public Thread b;
   private int x;
   private static int y;
   private e z;
   private boolean A = true;
   private static byte[] B;
   private ByteArrayOutputStream C;
   private DataOutputStream D;
   public int c;
   public Hashtable d;
   private static int E;
   private static int F;
   private static int G = 5;
   private static int H = 5;
   private static int I = -1;
   private static int J;
   private static int K = -1;
   private static String L;
   private final int M;
   private int N = 0;
   private Random O = new Random();
   public static String e = "";
   public static String f = "";
   public static String g = "";
   public static int h;
   public boolean i;

   public b(int var1, e var2) {
      super(var1, "Loading...");
      this.z = var2;
      this.d(Math.min(236, 124));
      if (I == -1) {
         I = (super.m - 10) / 2;
      }

      this.d(65, 0);
      this.M = super.n - 3 - (super.n - 3 + 3 - 1) % 5;
      super.v = 150;
      this.b = new Thread(this);
      this.C = new ByteArrayOutputStream();
      this.D = new DataOutputStream(this.C);
      this.d = new Hashtable();
      this.b(255, y++);
   }

   public final void a(Graphics var1, boolean var2) {
      this.a(var1);
      var1.setColor(0);
      var1.fillRect(super.k, super.l, super.m, super.n);
      var1.setColor(16173378);
      if (this.x == 0) {
         var1.drawString("Data used:", super.k + (super.m >> 1), 0 + super.l + 2, 17);
      } else {
         var1.drawString("Retry no: " + this.x, super.k + (super.m >> 1), 0 + super.l + 2, 17);
      }

      if (J / 10485 != K) {
         K = J / 10485;
         StringBuffer var3;
         (var3 = new StringBuffer()).append(K);

         while (var3.length() < 3) {
            var3.insert(0, '0');
         }

         var3.insert(var3.length() - 2, '.');
         var3.append(" MB");
         L = var3.toString();
      }

      var1.drawString(L, super.k + (super.m >> 1), 0 + super.l + 2 + e.s, 17);
      var1.setColor(16645016);
      var1.fillRect(super.k + E, super.l + F, 3, 3);
      var1.setColor(16173378);
      var1.drawLine(super.k + I, super.l + this.M, super.k + I + 10, super.l + this.M);
   }

   public final void a() {
      I = Math.min(super.m - 10 - 1, Math.max(0, I + this.N));
      int var1 = E + G;
      int var2 = F + H;
      if (var1 <= 0) {
         G = -G;
         var1 = Math.max(1, Math.abs(var1));
      }

      int var3 = super.m - 2;
      if (var1 + 3 >= var3) {
         G = -G;
         var1 -= var1 + 3 - var3;
      }

      if (var2 + 3 == this.M && var1 + 3 - 1 >= I && var1 - 1 <= I + 10) {
         H = -H;
         G = G + this.O.nextInt() % 2;
      }

      if (var2 >= super.n - 3 && H > 0) {
         var2 = 5;
      }

      if (var2 == 0) {
         H = -H;
      }

      F = var2;
      E = var1;
      this.e();
   }

   public final boolean a(int var1, int var2) {
      if (var2 == 2) {
         this.N = -6;
      }

      if (var2 == 5) {
         this.N = 6;
      }

      return true;
   }

   public final void run() {
      HttpConnection var1 = null;
      DataOutputStream var2 = null;
      DataInputStream var3 = null;
      String var4 = "http://" + a + "4.eraofeidolon.com/2/" + super.u + ".pl";
      String var5;
      boolean var6;
      if (var6 = (var5 = g.b.getAppProperty("Relay")) == null) {
         var5 = var4;
      }

      while (this.A) {
         Vector var7 = new Vector();

         try {
            (var1 = (HttpConnection)Connector.open(var5, 3, true)).setRequestMethod("POST");
            if (!var6) {
               var1.setRequestProperty("X-relay-url", var4);
            }

            var2 = var1.openDataOutputStream();
            if (B != null) {
               var2.writeByte(0);
               var2.writeByte(0);
               var2.writeShort(B.length);
               var2.write(B);
               J = J + 4 + B.length;
            }

            var2.write(this.C.toByteArray());
            J = J + this.C.size();
            int var8;
            if ((var8 = var1.getResponseCode()) != 200) {
               throw new IOException("rc" + var8);
            }

            if ((var3 = var1.openDataInputStream()).readUnsignedShort() != 47806) {
               throw new IOException("Magic number");
            }

            this.c = var3.readUnsignedByte();
            var3.readUnsignedByte();
            J = J + var3.readInt();
            int var42 = var3.readUnsignedShort();

            for (int var43 = 0; var43 < var42; var43++) {
               int var11;
               Object var14;
               var11 = var3.readUnsignedByte();
               int var12 = var3.readUnsignedByte();
               int var13 = var3.readUnsignedShort();
               label332:
               switch (var12) {
                  case 1:
                     switch (var13) {
                        case 1:
                           var14 = new Integer(var3.readByte());
                           break label332;
                        case 2:
                           var14 = new Integer(var3.readShort());
                           break label332;
                        case 3:
                        default:
                           throw new IOException("ChnkLen:" + var13);
                        case 4:
                           var14 = new Integer(var3.readInt());
                           break label332;
                     }
                  case 2:
                  case 3:
                     if ((var14 = a(var3, var13)) == null) {
                        var14 = "";
                     }
                     break;
                  case 4:
                     var14 = new f(var3);
                     break;
                  case 5:
                     int var15;
                     switch ((var15 = var3.readUnsignedShort()) >> 8) {
                        case 1:
                        case 9:
                           byte[][] var16 = g.b(var3);
                           super.w.d.put(new Integer(var15), var16);
                           continue;
                        case 2:
                        case 4:
                        case 6:
                        case 8:
                        default:
                           byte[] var19 = new byte[var13 - 2];
                           var3.readFully(var19);
                           super.w.a(var15 >> 8, var15 & 0xFF, var19);
                           continue;
                        case 3:
                           super.w.a(3, var15 & 0xFF, super.w.a(var3, var13 - 2, false));
                           continue;
                        case 5:
                        case 7:
                           byte[] var17 = new byte[var13 - 2];
                           var3.readFully(var17);
                           Image var18 = Image.createImage(var17, 0, var17.length);
                           super.w.a(var15 >> 8, var15 & 0xFF, var18);
                           g.a(true);
                           continue;
                        case 10:
                           super.w.a(var3, var13 - 2, true);
                           continue;
                        case 11:
                           super.w.a(11, var15 & 0xFF, g.a(var3));
                           continue;
                     }
                  default:
                     var14 = new byte[var13];
                     var3.readFully((byte[])var14);
               }

               if (var14 != null) {
                  switch (var11) {
                     case 0:
                        B = (byte[])var14;
                        break;
                     case 1:
                        var7.addElement(new h(30, null, var14.toString()));
                        break;
                     case 2:
                        super.w.a(this.z, new h(30, null, var14.toString()), false);
                        break;
                     case 3:
                     default:
                        Integer var45 = new Integer(var11);
                        Object var46;
                        if ((var46 = this.d.get(var45)) instanceof Vector) {
                           ((Vector)var46).addElement(var14);
                        } else if (var46 != null) {
                           Vector var47;
                           (var47 = new Vector()).addElement(var46);
                           var47.addElement(var14);
                           this.d.put(var45, var47);
                        } else {
                           this.d.put(var45, var14);
                        }
                        break;
                     case 4:
                        f = var14.toString();
                        break;
                     case 5:
                        h = (Integer)var14;
                        break;
                     case 6:
                        e = var14.toString();
                        break;
                     case 7:
                        g = var14.toString();
                  }
               }
            }

            if (this.A) {
               if (this.c != 0) {
                  super.w.b(this.z, this, null);
               } else {
                  if (var7.size() == 0) {
                     super.w.a("Second login detected! You can only be logged in from one device at a time", this.z, null, null, false);
                  }

                  super.w.a(this.z, new e(33, 1), false);
                  super.w.b(this);
               }

               for (int var44 = 0; var44 < var7.size(); var44++) {
                  super.w.a(this.z, (e)var7.elementAt(var44), false);
               }
            }

            return;
         } catch (SecurityException var38) {
            super.w
               .a(this, new h(31, null, "Please allow GPRS-connection.\nGame uses less than 1 MB of data per hour. Data usage can be tracked in game."), false);
            super.w.a(this, new e(33, 1), false);
            return;
         } catch (IOException var39) {
            if (++this.x <= 3 && !"rc500".equals(var39.getMessage())) {
               synchronized (this) {
                  try {
                     g.a(false);
                     int var10 = 1000 << this.x;
                     this.wait(var10);
                  } catch (Exception var36) {
                  }
               }

               this.d.clear();
               continue;
            }

            super.w.b(this.z, this, var39);
            e var9 = (e)super.w.a.elementAt(super.w.a.size() - 1);
            super.w.a(var9, new e(33, 1), false);
         } catch (Throwable var40) {
            super.w.b(this.z, this, var40);
            return;
         } finally {
            super.w.d();

            try {
               if (var3 != null) {
                  var3.close();
               }

               if (var2 != null) {
                  var2.close();
               }

               if (var1 != null) {
                  var1.close();
               }
            } catch (IOException var35) {
            }
         }

         return;
      }
   }

   public final void b() {
      this.D = null;
      this.b.start();
   }

   public final void b(int var1, int var2) {
      try {
         this.D.writeByte(var1);
         this.D.writeByte(1);
         if (var2 > -129 && var2 < 128) {
            this.D.writeShort(1);
            this.D.writeByte(var2);
         } else if (var2 > -32769 && var2 < 32768) {
            this.D.writeShort(2);
            this.D.writeShort(var2);
         } else {
            this.D.writeShort(4);
            this.D.writeInt(var2);
         }
      } catch (IOException var4) {
      }
   }

   public final void a(int var1, String var2) {
      try {
         this.D.writeByte(var1);
         this.D.writeByte(2);
         this.D.writeShort(a(var2));
         a(this.D, var2);
      } catch (IOException var4) {
      }
   }

   public final void a(int var1, byte[] var2) {
      try {
         this.D.writeByte(var1);
         this.D.writeByte(0);
         this.D.writeShort(var2.length);
         this.D.write(var2);
      } catch (IOException var4) {
      }
   }

   public final void a(Hashtable var1) {
      try {
         this.D.writeByte(2);
         this.D.writeByte(0);
         this.D.writeShort(var1.size() << 1);
         Enumeration var2 = var1.keys();

         while (var2.hasMoreElements()) {
            short var3 = ((Integer)var2.nextElement()).shortValue();
            this.D.writeShort(var3);
         }
      } catch (IOException var4) {
      }
   }

   public final Vector a(int var1) {
      Object var2;
      if ((var2 = this.d.get(new Integer(var1))) instanceof Vector) {
         return (Vector)var2;
      }

      Vector var3 = new Vector();
      if (var2 != null) {
         var3.addElement(var2);
      }

      return var3;
   }

   public final int b(int var1) {
      Object var2;
      return (var2 = this.d.get(new Integer(var1))) == null ? 0 : (Integer)var2;
   }

   public final String c(int var1) {
      return (String)this.d.get(new Integer(var1));
   }

   public static final void a(OutputStream var0, String var1) throws IOException {
      for (int var2 = 0; var2 < var1.length(); var2++) {
         char var3;
         if ((var3 = var1.charAt(var2)) <= 127) {
            var0.write(var3);
         } else if (var3 <= 2047) {
            var0.write(192 | var3 >> 6);
            var0.write(128 | var3 & 63);
         } else {
            var0.write(224 | var3 >> '\f');
            var0.write(128 | var3 >> 6 & 63);
            var0.write(128 | var3 & 63);
         }
      }
   }

   public static final int a(String var0) {
      int var1 = 0;

      for (int var2 = 0; var2 < var0.length(); var2++) {
         char var3;
         if ((var3 = var0.charAt(var2)) <= 127) {
            var1++;
         } else if (var3 <= 2047) {
            var1 += 2;
         } else {
            var1 += 3;
         }
      }

      return var1;
   }

   public static final String a(InputStream var0, int var1) throws IOException {
      if (var1 == 0) {
         return null;
      }

      StringBuffer var2 = new StringBuffer();
      int var3 = 0;
      int var4 = -1;

      for (int var5 = 0; var5 < var1; var5++) {
         int var6;
         if ((var6 = var0.read()) == -1) {
            throw new EOFException();
         }

         if ((var6 & 192) == 128) {
            var3 = var3 << 6 | var6 & 63;
            if (--var4 == 0) {
               var2.append((char)var3);
            }
         } else if ((var6 & 128) == 0) {
            var2.append((char)var6);
         } else if ((var6 & 224) == 192) {
            var3 = var6 & 31;
            var4 = 1;
         } else {
            if ((var6 & 240) != 224) {
               throw new IllegalArgumentException("utf8");
            }

            var3 = var6 & 15;
            var4 = 2;
         }
      }

      return var2.toString();
   }

   public static final String a(byte[] var0, int var1, int var2) {
      try {
         return a(new ByteArrayInputStream(var0, var1, var2), var2);
      } catch (IOException var4) {
         return null;
      }
   }

   public final void c(int var1, int var2) {
      this.N = 0;
   }
}
