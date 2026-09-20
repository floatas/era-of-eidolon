import java.io.DataInputStream;
import java.io.IOException;

public final class f {
   public String a;
   public String b;
   public String c;
   public StringBuffer d;
   public int e;
   public int f = -1;
   public int g;
   public int h;
   public Object[][] i;
   public int j = -1;
   public Object k;

   public f(String var1, Object var2) {
      this.a = var1;
      this.k = var2;
   }

   public f(String var1, String var2, int var3) {
      this.a = var1;
      this.d = var2 == null ? new StringBuffer() : new StringBuffer(var2);
      this.e = var3;
   }

   public f(String var1) {
      this.a = var1;
   }

   public f(DataInputStream var1) throws IOException {
      this.a = b.a(var1, var1.readUnsignedByte());
      if (this.a == null) {
         this.a = "";
      }

      this.b = b.a(var1, var1.readUnsignedByte());
      this.f = var1.readByte();
      this.g = var1.readUnsignedByte();
      this.c = b.a(var1, var1.readUnsignedByte());
      int var2;
      if ((var2 = var1.readUnsignedShort()) > 0) {
         this.k = new byte[var2];
         var1.readFully((byte[])this.k);
      }
   }

   public f(String var1, Object[][] var2) {
      this.a = var1;
      this.i = var2;
   }

   public final int a() {
      if (this.f >= 0) {
         this.h = 15 + a(this.a, true);
      } else if (this.e != 0) {
         this.h = 5 + Math.max(a(this.a, true), a(this.d.toString(), true));
      } else if (this.i != null) {
         this.h = 5 + Math.max(this.j >= 0 ? a(this.i[this.j][0].toString(), true) : 0, a(this.a, true));
      } else {
         this.h = a(this.a, true);
      }

      if (this.c != null) {
         this.h = Math.max(this.h, a(this.c, true));
      }

      return this.h;
   }

   public static final int a(String var0, boolean var1) {
      int var2 = 0;
      int var3 = 0;
      int var4 = 0;
      byte var5 = 0;

      while (var4 < var0.length()) {
         while (var4 < var0.length() && (var6 = var0.charAt(var4)) > 11) {
            var4++;
         }

         var2 += e.r.substringWidth(var0, var3, var4 - var3);
         var3 = var4;
         switch (var6) {
            case '\u0004':
               if (var1) {
                  var2 += 6;
               }
            case '\u0001':
            case '\u0002':
            case '\u0003':
            case '\u0007':
               var3 = ++var4;
            case '\u0005':
            case '\b':
            case '\t':
            case '\n':
            default:
               break;
            case '\u0006':
               var3 = var4 += 4;
               break;
            case '\u000b':
               var2 += 10;
               var3 = var4 += 2;
               var5 = 0;
         }
      }

      return var2;
   }

   public final String b() {
      return this.b == null ? this.a : this.b;
   }

   public final boolean c() {
      return (this.g & 8) != 0;
   }

   public final String d() {
      return this.k == null ? null : b.a((byte[])this.k, 0, ((byte[])this.k).length);
   }
}
