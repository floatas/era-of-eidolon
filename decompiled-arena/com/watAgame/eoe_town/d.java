package com.watAgame.eoe_town;

import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.EOFException;
import java.io.IOException;
import java.io.OutputStream;
import javax.microedition.io.Connector;
import javax.microedition.io.HttpConnection;

final class d extends Thread {
   private int b = 0;
   private final String d;
   private String e;
   private final int i;
   private String h;
   private final b j;
   private static int a;
   private static String f;
   private static boolean c;
   private static final Object g = new Object();

   public d(b var1, int var2) {
      this.j = var1;
      this.i = var2;
      this.j.q = true;
      StringBuffer var3 = new StringBuffer(var1.P);
      StringBuffer var4 = new StringBuffer();
      switch (var2) {
         case 2:
            var3.append("login.pl");
            var4.append("¦key=");
            var4.append(var1.j);
            var4.append("¦productid=");
            var4.append("01020202");
            var4.append("¦build=");
            var4.append("5.3.3");
            var4.append("¦model=");
            var4.append("no40");
            break;
         case 3:
            var3.append("login.pl");
            var4.append("¦login=");
            var4.append(var1.bC);
            var4.append("¦pass=");
            var4.append(var1.ap);
            var4.append("¦productid=");
            var4.append("01020202");
            var4.append("¦build=");
            var4.append("5.3.3");
            var4.append("¦model=");
            var4.append("no40");
            break;
         case 4:
            var3.append("register.pl");
            var4.append("¦nickname=");
            var4.append(var1.bC);
            var4.append("¦reqpass=");
            var4.append(var1.ap);
            var4.append("¦productid=");
            var4.append("01020202");
            var4.append("¦build=");
            var4.append("5.3.3");
            var4.append("¦model=");
            var4.append("no40");
            break;
         case 5:
            var3.append("pay.pl");
            var4.append("¦amount=");
            var4.append(var1.n());
            break;
         case 6:
            var3.append("charselectchoose.pl");
            var4.append("¦charname=");
            var4.append(var1.K[var1.cu]);
            break;
         case 7:
            var3.append("charselectcreate.pl");
            var4.append("¦charname=");
            var4.append(var1.ca);
            var4.append("¦gender=");
            var4.append(var1.bP);
            break;
         case 8:
            var3.append("charselectdelete.pl");
            var4.append("¦charname=");
            var4.append(var1.B[var1.k]);
            break;
         case 9:
            var3.append("arenachflist.pl");
            break;
         case 10:
            var3.append("arenachran.pl");
            break;
         case 11:
            var3.append("invite.pl");
            var4.append("¦phoneno=");
            var4.append(var1.aH);
            var4.append("¦email=");
            var4.append(var1.aX);
            break;
         case 12:
            var3.append("betaentry.pl");
            break;
         case 13:
            var3.append("inbox.pl");
            break;
         case 14:
            var3.append("readmail.pl");
            var4.append("¦mailid=");
            var4.append(var1.aj);
            break;
         case 15:
            var3.append("mailflist.pl");
         case 16:
         case 54:
         case 57:
         case 58:
         case 59:
         case 62:
         default:
            break;
         case 17:
            var3.append("deletemail.pl");
            var4.append("¦mailid=");
            var4.append(var1.aj);
            break;
         case 18:
            var3.append("sendmail.pl");
            var4.append("¦receivername=");
            var4.append(var1.aJ);
            var4.append("¦mailbody=");
            var4.append(var1.ag);
            break;
         case 19:
            var3.append("ilistbuy.pl");
            var4.append("¦classID=");
            var4.append(var1.aE);
            break;
         case 20:
            var3.append("buyitem.pl");
            var4.append("¦genericID=");
            var4.append(var1.br[var1.cu][0]);
            break;
         case 21:
            var3.append("selllist.pl");
            break;
         case 22:
            var3.append("sellitem.pl");
            var4.append("¦genericID=");
            var4.append(var1.br[var1.cu][0]);
            break;
         case 23:
            var3.append("chalreceive.pl");
            var4.append("¦name=");
            var4.append(var1.o[2]);
            var1.bY = var1.o[2];
            var4.append("¦accept=");
            var4.append(var1.ao);
            break;
         case 24:
            var3.append("chalissue.pl");
            var4.append("¦name=");
            var4.append(var1.E);
            break;
         case 25:
            var3.append("boarddl.pl");
            break;
         case 26:
            var3.append("submit.pl");

            for (int var6 = 1; var6 <= var1.F.size(); var6++) {
               String[] var7 = (String[])var1.F.elementAt(var6 - 1);
               var4.append("¦t");
               var4.append(var6);
               var4.append("=");
               var4.append(var7[0]);
               var4.append("¦a");
               var4.append(var6);
               var4.append("=");
               var4.append(var7[1]);
               if (var7[2].length() > 0) {
                  var4.append("¦e");
                  var4.append(var6);
                  var4.append("=");
                  var4.append(var7[2]);
               }
            }
            break;
         case 27:
            var3.append("flee.pl");
            break;
         case 28:
            var3.append("fightresult.pl");
            break;
         case 29:
            var3.append("battlereport.pl");
            var4.append("¦type=");
            var4.append(var1.cu);
            break;
         case 30:
         case 31:
         case 32:
            var3.append("pmessages.pl");
            var4.append("¦idx=");
            var4.append(var2 - 30 + 1);
            var4.append("¦productid=");
            var4.append("01020202");
            break;
         case 33:
            var3.append("panimscripts.pl");
            var4.append("¦model=");
            var4.append("02");
            break;
         case 34:
            var3.append("version.pl");
            var4.append("¦client=");
            var4.append("02010502");
            var4.append("¦build=");
            var4.append("5.3.3");
            var4.append("¦model=");
            var4.append("no40");
            break;
         case 35:
            String[] var8 = var1.f;
            var3.append("incabil.pl");
            var4.append("¦str=");
            var4.append(var8[1]);
            var4.append("¦int=");
            var4.append(var8[2]);
            var4.append("¦dex=");
            var4.append(var8[3]);
            var4.append("¦tou=");
            var4.append(var8[4]);
            var4.append("¦wil=");
            var4.append(var8[5]);
            var4.append("¦spd=");
            var4.append(var8[6]);
            break;
         case 36:
            var3.append("customget.pl");
            var1.u = "0";
            break;
         case 37:
            var3.append("headlist.pl");
            var4.append("¦headid=");
            var4.append(var1.u);
            break;
         case 38:
            String[] var5 = var1.bV;
            var3.append("customupload.pl");
            var4.append("¦taunt1=");
            var4.append(var5[4]);
            var4.append("¦taunt2=");
            var4.append(var5[5]);
            var4.append("¦taunt3=");
            var4.append(var5[6]);
            var4.append("¦greeting=");
            var4.append(var5[0]);
            var4.append("¦victory=");
            var4.append(var5[1]);
            var4.append("¦loose=");
            var4.append(var5[2]);
            var4.append("¦headid=");
            var4.append(var1.u);
            break;
         case 39:
            var3.append("herostats.pl");
            break;
         case 40:
            var1.aE = 1;
         case 41:
            var3.append("herosksp.pl");
            var4.append("¦classID=");
            var4.append(var1.aE);
            break;
         case 42:
            var3.append("heroskspdelete.pl");
            var4.append("¦genericID=");
            var4.append(var1.br[var1.aP][0]);
            break;
         case 43:
            var3.append("equiplist.pl");
            var4.append("¦equipid=");
            var4.append(var1.aE);
            break;
         case 44:
            var3.append("equipdo.pl");
            var4.append("¦genericid=");
            var4.append(var1.br[var1.cu][0]);
            break;
         case 45:
            var3.append("friendadd.pl");
            var4.append("¦name=");
            var4.append(var1.A);
            break;
         case 46:
            var3.append("friendlist.pl");
            break;
         case 47:
            var3.append("friendremoved.pl");
            var4.append("¦name=");
            var4.append(var1.br[var1.cu][2]);
            break;
         case 48:
            var3.append("banlistadd.pl");
            var4.append("¦name=");
            var4.append(var1.A);
            break;
         case 49:
            var3.append("banlist.pl");
            break;
         case 50:
            var3.append("banlistremove.pl");
            var4.append("¦name=");
            var4.append(var1.br[var1.cu][2]);
            break;
         case 51:
            var3.append("friendadd.pl");
            var4.append("¦name=");
            var4.append(var1.bY);
            break;
         case 52:
            var3.append("getranklist.pl");
            var4.append("¦ranklistid=");
            var4.append(var1.cu);
            break;
         case 53:
            var3.append("wiseman.pl");
            var4.append("¦category=");
            var4.append(var1.cu);
            break;
         case 55:
            var3.append("arenachtlist.pl");
            break;
         case 56:
            var3.append("arenachslist.pl");
            break;
         case 60:
            var3.append("clanstats.pl");
            break;
         case 61:
            var3.append("clanhierarchy.pl");
            break;
         case 63:
            var3.append("claninvite.pl");
            var4.append("¦heroname=");
            var4.append(var1.by);
            break;
         case 64:
            var3.append("clancreate.pl");
            var4.append("¦clanname=");
            var4.append(var1.T);
            var4.append("¦clanshortname=");
            var4.append(var1.bl);
            break;
         case 65:
            var3.append("clanlist.pl");
            break;
         case 66:
            var3.append("clankick.pl");
            var4.append("¦heroidx=");
            var4.append(var1.cu);
            break;
         case 67:
            var3.append("myclan.pl");
            break;
         case 68:
            var3.append("clanjoin.pl");
            break;
         case 69:
            var3.append("clanedit.pl");
            break;
         case 70:
            var3.append("pgethead.pl");
            var4.append("¦headflag=");
            var4.append(var1.I);
            break;
         case 71:
            var3.append("clanreject.pl");
            break;
         case 72:
            var3.append("clanleave.pl");
      }

      this.d = var3.toString();
      this.e = var4.toString();
      this.start();
   }

   public d(b var1, int var2, String var3, String var4) {
      this.j = var1;
      this.i = var2;
      this.d = var3;
      this.e = var4;
      this.start();
   }

   public final void run() {
      synchronized (g) {
         if (f != null) {
            this.e = "¦id=" + f + this.e;
         } else if (this.i == 100) {
            return;
         }

         HttpConnection var2 = null;
         OutputStream var3 = null;
         DataInputStream var4 = null;

         while (this.b < 4) {
            try {
               (var2 = (HttpConnection)Connector.open(this.d, 3, true)).setRequestMethod("POST");
               if (this.d.indexOf("login.pl") >= 0 || this.i == 100 || this.i == 4) {
                  String var5;
                  if ((var5 = System.getProperty("microedition.platform")) == null) {
                     var5 = this.j.ab.getAppProperty("UA");
                  }

                  if (var5 == null) {
                     var5 = "no40";
                  }

                  var2.setRequestProperty("X-User-Agent", var5);
                  String var41;
                  if ((var41 = this.j.ab.getAppProperty("PID-CHKSUM")) != null) {
                     this.e = this.e + "¦pid=" + var41;
                  }
               }

               (var3 = var2.openOutputStream()).write(a(this.e));
               if (var2.getResponseCode() == 200) {
                  var4 = var2.openDataInputStream();
                  int var39;
                  if ((var39 = (int)var2.getLength()) > 0) {
                     byte[] var42 = new byte[var39];
                     var4.readFully(var42);
                     this.h = a(var42);
                  } else {
                     ByteArrayOutputStream var43 = new ByteArrayOutputStream();
                     byte[] var7 = new byte[1];

                     try {
                        while (true) {
                           var4.readFully(var7, 0, 1);
                           var43.write(var7[0]);
                        }
                     } catch (EOFException var33) {
                        this.h = a(var43.toByteArray());
                     }
                  }

                  c = true;
                  if (this.i == 100) {
                     return;
                  }

                  if (this.h.startsWith("¦")) {
                     this.h = this.h.substring(1);
                     if (this.h.equals("-2")) {
                        this.j.a("sto");
                        return;
                     }

                     int var44 = this.h.indexOf(166) + 1;
                     int var45 = this.h.indexOf(166, var44);
                     if (var44 > 0 && var45 > 0) {
                        f = this.h.substring(var44, var45);
                     }

                     try {
                        if (this.i != 0 && this.i != 1) {
                           this.j.a(this.i, this.h);
                           return;
                        }

                        this.j.b(this.i, this.h);
                     } catch (Throwable var34) {
                        this.j.a("net(" + (this.i != 0 && this.i != 1 ? "r" + this.i : "p") + ")", var34, false);
                     }

                     return;
                  }

                  if (this.b >= 3) {
                     this.j.a("rsp");
                     return;
                  }
               } else if (this.b >= 3) {
                  this.j.a(var2.getResponseCode() + " r" + this.i);
                  return;
               }
            } catch (SecurityException var35) {
               if (a++ >= 1) {
                  this.j.ab.destroyApp(true);
               }

               this.j.a("Please allow#GPRS-connection.#EoE only uses#0.1 MB per hour =#approx. EUR 0.30", 0, 0, 0L);
               return;
            } catch (Throwable var36) {
               if (this.b >= 3) {
                  if (this.i == 100) {
                     return;
                  }

                  if (c) {
                     String var6 = var36.getClass().getName();
                     this.j.a(var36.getMessage() == null ? var6.substring(var6.lastIndexOf(46) + 1) : var36.getMessage());
                     return;
                  }

                  this.j.a("Phone is not setup#to access internet#from Java game.#Please contact your#operator.", 0, 0, 0L);
                  return;
               }
            } finally {
               try {
                  if (var3 != null) {
                     var3.close();
                  }

                  if (var4 != null) {
                     var4.close();
                  }

                  if (var2 != null) {
                     var2.close();
                  }
               } catch (IOException var31) {
               }
            }

            if (++this.b < 4) {
               try {
                  System.gc();
                  int var40;
                  Thread.sleep(var40 = 1000 << this.b);
               } catch (InterruptedException var32) {
               }
            }
         }

         this.j.a("gup");
      }
   }

   public static final byte[] a(String var0) {
      ByteArrayOutputStream var1 = new ByteArrayOutputStream(var0.length());

      for (int var2 = 0; var2 < var0.length(); var2++) {
         char var3;
         if ((var3 = var0.charAt(var2)) <= 127) {
            var1.write(var3);
         } else if (var3 <= 2047) {
            var1.write(192 | var3 >> 6);
            var1.write(128 | var3 & 63);
         } else {
            var1.write(224 | var3 >> '\f');
            var1.write(128 | var3 >> 6 & 63);
            var1.write(128 | var3 & 63);
         }
      }

      return var1.toByteArray();
   }

   public static final String a(byte[] var0) {
      StringBuffer var1 = new StringBuffer();
      int var2 = 0;
      int var3 = -1;

      for (int var4 = 0; var4 < var0.length; var4++) {
         byte var5;
         if (((var5 = var0[var4]) & 192) == 128) {
            var2 = var2 << 6 | var5 & 63;
            if (--var3 == 0) {
               var1.append((char)var2);
            }
         } else if ((var5 & 128) == 0) {
            var1.append((char)var5);
         } else if ((var5 & 224) == 192) {
            var2 = var5 & 31;
            var3 = 1;
         } else if ((var5 & 240) == 224) {
            var2 = var5 & 15;
            var3 = 2;
         }
      }

      return var1.toString();
   }
}
