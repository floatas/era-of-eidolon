import java.io.IOException;
import java.util.Vector;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.media.Manager;
import javax.microedition.media.MediaException;
import javax.microedition.media.Player;
import javax.microedition.media.control.VolumeControl;
import javax.microedition.midlet.MIDlet;
import javax.microedition.rms.RecordStore;
import javax.microedition.rms.RecordStoreException;
import javax.microedition.rms.RecordStoreNotFoundException;

public final class i extends g {
   private Image g;
   private boolean h;
   private static final long i = System.currentTimeMillis() + 50000L;
   private String j;
   private Player k;
   private VolumeControl l;
   private int m = 0;

   public i(MIDlet var1) {
      super(var1, new e(0, 0, 50000));
      String var2;
      if ((var2 = System.getProperty("microedition.profiles")) != null && var2.indexOf("MIDP-2.0") >= 0) {
         this.f();
      }

      this.g = this.a("/splash.png");
      this.g();
      this.b("/avalonv5.mid");
   }

   private void f() {
      this.setFullScreenMode(true);
   }

   public final void a(Graphics var1, e var2) {
      e var3;
      if ((var3 = this.c()) != var2 && var3 instanceof d) {
         try {
            var3.a(var1, false);
         } catch (Exception var5) {
         }
      } else {
         Image var4 = this.g;
         var1.setColor(0);
         var1.fillRect(0, 0, 240, 320);
         if (var4 != null) {
            var1.drawImage(var4, 0, 0, 20);
         }
      }

      var2.a(var1, true);
   }

   public final void a(int var1, int var2, e var3) throws Exception {
      switch (var3.u) {
         case 0:
            this.h = false;
            boolean var4 = false;
            this.a(var3, false);
            return;
         case 10:
            if (var2 == 4) {
               ((d)var3).a.d = null;
               this.a(var3, 8, false);
               return;
            }
         default:
            if (var2 == 4) {
               this.b(var3);
            } else {
               this.repaint();
            }
      }
   }

   private void a(e var1, boolean var2) {
      synchronized (this) {
         if (this.g == null) {
            return;
         }

         this.g = null;
      }

      g.a(false);
      byte[] var4 = null;
      RecordStore var5 = null;

      try {
         var4 = (var5 = RecordStore.openRecordStore("key", false)).getRecord(1);
      } catch (RecordStoreNotFoundException var18) {
      } catch (RecordStoreException var19) {
      } finally {
         try {
            var5.closeRecordStore();
         } catch (Exception var17) {
         }
      }

      b var3 = new b(1, var1);
      if (var4 != null && !var2) {
         var3.a(1, var4);
      }

      var3.a(2, "1.1.0");
      var3.b(3, 1);
      var3.b(4, 4);
      var3.b(5, 2);
      var3.a(6, "s700");
      String var6;
      if ((var6 = System.getProperty("microedition.platform")) != null) {
         var3.a(7, var6);
      }

      String var7;
      if ((var7 = g.b.getAppProperty("INFO")) != null) {
         var3.a(8, var7);
      }

      this.a(var1, var3);
   }

   public final void a(e var1, int var2, Object var3) throws IOException {
      if (var3 != "Back" && (var3 != "Cancel" || var1.u == 23)) {
         c var4 = var1 instanceof c ? (c)var1 : null;
         f var5 = var3 instanceof f ? (f)var3 : null;
         b var6 = null;
         boolean var7 = false;
         switch (var1.u) {
            case 2:
               this.a(var1, var2 == 0 ? 4 : 3, false);
               break;
            case 3:
            case 4:
               (var6 = new b(var1.u == 3 ? 2 : 3, var1)).a(2, var4.a(0).d.toString());
               var6.a(3, var4.a(1).d.toString());
               break;
            case 5:
               if (var3 == "Create hero") {
                  this.a(var1, 6, false);
               } else if (var3 == "Delete hero") {
                  Vector var17;
                  (var17 = new Vector()).addElement("Cancel");

                  for (int var18 = 0; var18 < var4.b.size(); var18++) {
                     Object var24;
                     if ((var24 = var4.b.elementAt(var18)) instanceof f) {
                        var17.addElement(((f)var24).a);
                     }
                  }

                  String[] var19 = new String[var17.size()];
                  var17.copyInto(var19);
                  this.a(var1, new h(7, "Confirmation", "Select the hero you want to delete below.\nAction can not be undone!", var19), false);
               } else {
                  (var6 = new b(4, var1)).a(1, var5.b());
               }
               break;
            case 6:
               f var8;
               if ((var8 = var4.a(1)).j == -1) {
                  this.a(var1, new h(29, "Error", "Choose gender"), false);
                  return;
               }

               (var6 = new b(5, var1)).a(1, var4.a(0).d.toString());
               var6.b(2, (Integer)var8.i[var8.j][1]);
               break;
            case 7:
               if (var3 != "Cancel") {
                  (var6 = new b(6, var1)).a(1, (String)var3);
                  ((c)this.c(var1)).b.addElement("Create hero");
                  ((c)this.c(var1)).a(var3);
               }

               this.b(var1);
               break;
            case 8:
               e var9 = this.c();
               if (var3 != "Start game" && var3 != "Resume game") {
                  if (var3 == "Hero info") {
                     Vector var23 = a(new String[]{"Equipped items", "Spells", "Skills", "Hero sheet", "Back"});
                     if (var9 instanceof d) {
                        var23.insertElementAt("Quest items", 3);
                     }

                     this.a(var1, new c(9, "Hero info", var23), false);
                  } else if (var3 == "Quest log") {
                     if (var9 instanceof d) {
                        this.a(var1, new h(30, "Quest log", ((d)var9).h()), false);
                     }
                  } else if (var3 == "Save & exit") {
                     this.a(var1, new h(34, "Confirmation", "Save & exit game?", new String[]{"Save & exit", "Cancel"}), false);
                  } else if (var3 == "Credits") {
                     this.a(
                        var1,
                        new h(
                           30,
                           "Credits",
                           "\u0006ÿÿÿProducer:\n\u0007Henrik Riis\n\u0006ÿÿÿLead client code:\n\u0007Lars Engholm Johansen\n\u0006ÿÿÿLead server code:\n\u0007Brian Thorsbro\n\u0006ÿÿÿStory line:\n\u0007Thomas Laurfelt\n\u0006ÿÿÿArtwork:\n\u0007Robert Friis\nRiana Miller\n\u0006ÿÿÿQuality assurance:\n\u0007Mikkel Meisler\n\u0006ÿÿÿTools & portings:\n\u0007Morten Nobel-Jørgensen\nLars Engholm Johansen\n\u0006ÿÿÿMusic:\n\u0007Mario Barbosa\n\n\u0006ÿÿÿbrought to you:\n\u0007by pascha                                               "
                        ),
                        false
                     );
                  } else if (var3 == "Score info") {
                     (var6 = new b(20, var1)).b(1, 2);
                  } else if (var3 == "Rankings") {
                     (var6 = new b(26, var1)).b(1, 1);
                  } else if (var3 == "More games") {
                     (var6 = new b(7, var1)).b(1, 6660);
                  } else if (var3 == "Help") {
                     var6 = new b(27, var1);
                  } else if (var3.toString().startsWith("Sound")) {
                     this.m = (this.m + 25) % 125;
                     this.a(this.m);
                     this.h();
                     var4.b.setElementAt("Sound: " + this.m + "%", var2);
                     var4.b();
                  }
               } else if (!this.h) {
                  g.a(true);
                  (var6 = new b(8, var1)).b(1, 2);
                  var6.a(super.d);
                  var6.a(3, super.c);
               } else {
                  this.b(var1);
               }
               break;
            case 9:
               if (var3 == "Hero sheet") {
                  (var6 = new b(20, var1)).b(1, 1);
               } else if (var3 == "Equipped items") {
                  var6 = new b(21, var1);
               } else if (var3 == "Quest items") {
                  e var22;
                  if ((var22 = this.c()) instanceof d) {
                     Vector var28;
                     (var28 = ((d)var22).i()).addElement("Back");
                     this.a(var1, new c(22, "Quest items", var28), false);
                  }
               } else if (var3 == "Skills" || var3 == "Spells") {
                  (var6 = new b(25, var1)).b(1, var3 == "Skills" ? 9 : 13);
               }
            case 10:
            case 25:
            case 26:
            case 27:
            case 28:
            case 30:
            case 31:
            case 33:
            default:
               break;
            case 11:
               (var6 = new b(15, var1)).b(1, var2);
               break;
            case 12:
               this.a(var1, new h(13, var5.a, var5.d(), (var5.g & 32) == 0 ? new String[]{"Back", "Buy"} : null), false);
               break;
            case 13:
               c var29 = (c)this.c(var1);
               (var6 = new b(16, var1)).a(1, var29.f().b);
               break;
            case 14:
               e var21 = this.c();
               if (var2 == 6) {
                  if (var21 instanceof d) {
                     ((d)var21).f();
                  }
               } else {
                  this.a(var1, new h(15, "Confirmation", (String)var5.k, new String[]{"Add", "Cancel"}), false);
               }
               break;
            case 15:
               e var20 = this.c(var1);
               e var25 = this.c();
               if (var20 instanceof c && var25 instanceof d) {
                  this.b(var1);
                  ((d)var25).a(((c)var20).c);
               }
               break;
            case 16:
               (var6 = new b(22, var1)).a(1, ((f)var3).b);
               break;
            case 17:
               if (var2 == 0) {
                  (var6 = new b(23, var1)).a(1, var5.b);
                  c var27;
                  (var27 = (c)this.c(var1)).f().a = "";
                  var27.f().c = "Nothing equipped";
               } else {
                  this.a(var1, new h(18, var5.a, var5.d(), new String[]{"Back", "Equip", "Delete"}), false);
               }
               break;
            case 18:
            case 20:
               if (var3 == "Equip") {
                  c var26 = (c)this.c(var1);
                  (var6 = new b(23, var26)).a(1, var26.f().b);
               } else if (var3 == "Delete") {
                  this.a(
                     var1,
                     new h(21, "Confirmation", "Are you sure you want to delete this?\nAction can not be undone!", new String[]{"Cancel", "Delete"}),
                     false
                  );
                  break;
               }

               var1 = this.b(var1);
               break;
            case 19:
               this.a(var1, new h(20, var5.a, var5.d(), new String[]{"Back", "Delete"}), false);
               break;
            case 21:
               c var12;
               f var13 = (var12 = (c)this.c(this.c(var1))).f();
               f var31;
               if (var12.u == 17 && (var31 = ((c)this.c(var12)).f()).a.equals(var13.a)) {
                  var31.a = "";
                  var31.c = "Nothing equipped";
               }

               (var6 = new b(24, var1)).a(1, var13.b);
               var12.b.removeElementAt(var12.c);
               var12.b();
               this.b(this.b(var1));
               var1 = null;
               break;
            case 22:
               this.a(var1, new h(30, var5.a, ((d)this.c()).b(Integer.parseInt(var5.d()))), false);
               break;
            case 23:
               var6 = new b(18, var1);
               if (var3 == "Balance") {
                  var6.b(1, 1);
               }

               this.b(var1);
               break;
            case 24:
               if (var3 == "Accept") {
                  var6 = new b(19, var1);
               } else {
                  this.a(var1, new e(33, 1), false);
               }
               break;
            case 29:
               if (var3 == "Icon overview 2") {
                  (var6 = new b(7, var1)).b(1, 6659);
               } else if (var3 == "Icon overview 1") {
                  var6 = new b(28, var1);
               } else {
                  String var14;
                  if ((var14 = var5.d()) != null) {
                     this.a(var1, new h(30, var5.a, var14), false);
                  }
               }
               break;
            case 32:
               e var10;
               if ((var10 = this.c()) instanceof d) {
                  this.b(var1);
                  d var11;
                  (var11 = (d)var10).a(var5.k);
                  var11.b();
               }
               break;
            case 34:
               if (var3 != "Cancel") {
                  if (this.c() instanceof d) {
                     var6 = new b(9, var1);
                     ((d)this.c()).d(var6);
                  }

                  var7 = true;
               } else {
                  this.b(var1);
               }
               break;
            case 35:
               e var30;
               if (var3 == "Continue" && (var30 = this.c()) instanceof d) {
                  this.b(var1);
                  this.d();
                  d var32;
                  (var32 = (d)var30).g();
               }
               break;
            case 36:
               e var15;
               if ((var15 = this.c()) instanceof d) {
                  d var16;
                  (var16 = (d)var15).a(var16.e, var16.f = var2 == 0);
               }

               this.b(var1);
               this.d();
         }

         if (var6 != null) {
            this.a(var1, var6);
         }

         if (var7) {
            this.a(var1, new e(33, 1), false);
         }
      } else {
         this.b(var1);
      }
   }

   private void a(e var1, int var2, boolean var3) {
      switch (var2) {
         case 3:
         case 4:
            this.a(
               var1,
               new c(
                  var2,
                  var2 == 3 ? "Please login" : "Please register",
                  a(new Object[]{new f("Type login", null, 14), new f("Type password", null, 14), "Continue", "Back"})
               ),
               var3
            );
            return;
         case 6:
            this.a(
               var1,
               new c(
                  var2,
                  "Create hero",
                  a(
                     new Object[]{
                        new f("Hero name", null, 14),
                        new f("Choose gender", new Object[][]{{"Male", new Integer(1)}, {"Female", new Integer(2)}}),
                        "Create hero",
                        "Cancel"
                     }
                  )
               ),
               var3
            );
            return;
         case 8:
            Vector var4 = a(new Object[]{"Hero info", "Score info", "Rankings", "Help", "More games", "Credits", "Save & exit"});
            if (var1 instanceof d) {
               var4.insertElementAt("Resume game", 0);
               var4.insertElementAt("Quest log", 4);
            } else {
               var4.insertElementAt("Start game", 0);
            }

            var4.insertElementAt("Sound: " + this.m + "%", var4.size() - 1);
            this.a(var1, new c(var2, "Main menu", var4), var3);
         case 5:
         case 7:
      }
   }

   public final void a(e var1, b var2, Throwable var3) throws Exception {
      if (var3 != null) {
         this.a("net(" + var2.u + ")", var1, "Network error", var3, false);
      } else {
         Object var4 = null;
         switch (var2.u) {
            case 1:
            case 2:
            case 19:
               byte[] var16;
               if ((var2.c == 1 || var2.c == 5) && (var16 = (byte[])var2.d.get(new Integer(21))) != null) {
                  RecordStore var25 = RecordStore.openRecordStore("key", true);

                  try {
                     if (var25.getNumRecords() == 0) {
                        var25.addRecord(var16, 0, var16.length);
                     } else {
                        var25.setRecord(1, var16, 0, var16.length);
                     }
                  } finally {
                     try {
                        var25.closeRecordStore();
                     } catch (RecordStoreException var13) {
                     }
                  }
               }

               switch (var2.c) {
                  case 1:
                     Vector var17;
                     if ((var17 = var2.a(20)).size() == 0) {
                        this.a(var1, 6, true);
                        return;
                     }

                     if (var17.size() < 2) {
                        var17.addElement("Create hero");
                     }

                     var17.addElement("Delete hero");
                     this.a(null, new c(5, "Select hero", var17), true);
                     return;
                  case 2:
                     this.a(null, new h(2, null, var2.c(21), new String[]{"New user", "Existing user"}), true);
                     return;
                  case 3:
                  default:
                     return;
                  case 4:
                     this.a(var1, new e(33, 1), false);
                     return;
                  case 5:
                     this.a(var1, new h(24, null, var2.c(22), new String[]{"Accept", "Decline"}), false);
                     return;
               }
            case 3:
               switch (var2.c) {
                  case 1:
                     var2.u = 2;
                     this.a(var1, var2, var3);
                     return;
                  default:
                     return;
               }
            case 4:
            case 18:
               switch (var2.c) {
                  case 1:
                     this.a(var1, 8, false);
                     return;
                  case 2:
                     this.a(var1, new h(23, null, var2.c(20), new String[]{"Balance", "Cancel"}), false);
                     return;
                  default:
                     return;
               }
            case 5:
               switch (var2.c) {
                  case 1:
                     this.a(var1, 8, false);
                     this.b(var1);
                     break;
                  case 2:
                     String var15;
                     if ((var15 = var2.c(20)) != null && var1 instanceof c) {
                        StringBuffer var24;
                        (var24 = ((c)var1).a(0).d).setLength(0);
                        var24.append(var15);
                     }
               }
            case 6:
            case 7:
            case 10:
            case 14:
            case 24:
            default:
               break;
            case 8:
               switch (var2.c) {
                  case 1:
                  case 2:
                     byte[][] var23;
                     if ((var23 = (byte[][])super.d.get(new Integer(256))) == null) {
                        var23 = g.b(this.c(1, 0, null));
                     }

                     byte[][] var27;
                     if ((var27 = (byte[][])super.d.get(new Integer(2304))) == null) {
                        var27 = g.b(this.c(9, 0, null));
                     }

                     this.a(var1, new d(10, 240, 290, var23, var27, var2, var2.c == 2), true);
                     this.h = true;
                     return;
                  case 3:
                  default:
                     return;
               }
            case 11:
               if (var1 instanceof d) {
                  ((d)var1).c(var2);
               }
               break;
            case 12:
               if (var1 instanceof d) {
                  if (var2.i) {
                     ((d)var1).b(var2);
                  } else {
                     ((d)var1).a(var2);
                  }
               }
               break;
            case 13:
               if (var1 instanceof d) {
                  ((d)var1).e(var2);
               }
               break;
            case 15:
            case 25:
               Vector var22;
               (var22 = var2.a(20)).addElement("Back");
               this.a(var1, new c(var2.u == 15 ? 12 : 19, var2.c(21), var22), false);
               break;
            case 16:
               c var21;
               (var21 = (c)this.c(var1)).b.removeElement(var21.f());
               var21.b();
               var21.b(var2.c(21));
            case 9:
               this.b(var1);
               break;
            case 17:
               this.a(var1, new e(33, 1), false);
               break;
            case 20:
               this.a(var1, new h(30, var2.c(23), var2.c(20)), false);
               break;
            case 21:
               Vector var5;
               (var5 = var2.a(20)).addElement("Back");
               this.a(var1, new c(16, "Equipped items", var5), false);
               break;
            case 22:
               Vector var20;
               (var20 = var2.a(20)).addElement("Back");
               c var26;
               (var26 = new c(17, var2.c(21), var20)).c = var2.b(22);
               this.a(var1, var26, false);
               break;
            case 23:
               c var19;
               if (var2.c == 1 && (var19 = (c)var1).c != 0) {
                  c var7 = (c)this.c(var1);
                  f var8;
                  (var8 = (f)var19.b.elementAt(var19.c)).b = var7.f().b;
                  var7.b.setElementAt(var8, var7.c);
               }

               this.b(var1);
               break;
            case 26:
            case 28:
               Vector var18;
               (var18 = var2.a(20)).addElement("Back");
               this.a(var1, new c(29, var2.c(21), var18), false);
               break;
            case 27:
               Vector var6;
               (var6 = var2.a(20)).addElement("Icon overview 1");
               var6.addElement("Icon overview 2");
               var6.addElement("Back");
               this.a(var1, new c(29, var2.c(21), var6), false);
         }
      }
   }

   public final int a(e var1) {
      if (this.g != null && var1.t > i && !this.h) {
         this.a(var1, false);
      }

      e.a(true);
      return 3000;
   }

   public final void a(String var1, e var2, String var3, Throwable var4, boolean var5) {
      String var6 = "";
      if (var4 != null) {
         String var7;
         if ((var6 = (var7 = var4.toString()).substring(var7.lastIndexOf(46, var7.indexOf(58)) + 1)).startsWith("Run")) {
            var6 = var4.getMessage();
         }

         if (var4 instanceof IOException) {
            var6 = "";
            var1 = "Problem with your operator" + (var4.getMessage() == null ? "" : ":\n" + var4.getMessage());
         } else {
            var6 = var6 + "\n\n";
         }
      }

      h var9 = new h(0, var3 == null ? "Error" : var3, var1 + "\n\n" + var6 + "s" + var2.u + " v" + g.b.getAppProperty("MIDlet-Version"));
      if (var5) {
         this.a(var2, var9);
      } else {
         this.a(var2, var9, false);
      }
   }

   public static final Vector a(Object[] var0) {
      Vector var1 = new Vector(var0.length);

      for (int var2 = 0; var2 < var0.length; var2++) {
         var1.addElement(var0[var2]);
      }

      return var1;
   }

   private void g() {
      this.m = 50;
      Object var1 = null;
      RecordStore var2 = null;

      try {
         var1 = (var2 = RecordStore.openRecordStore("vol", false)).getRecord(1);
         this.m = (int)((Object[])var1)[0];
         return;
      } catch (RecordStoreNotFoundException var14) {
         return;
      } catch (RecordStoreException var15) {
      } finally {
         try {
            var2.closeRecordStore();
         } catch (Exception var13) {
         }
      }
   }

   private void h() {
      RecordStore var1 = null;

      try {
         var1 = RecordStore.openRecordStore("vol", true);
         byte[] var2 = new byte[]{(byte)this.m};
         if (var1.getNumRecords() == 0) {
            var1.addRecord(var2, 0, var2.length);
         } else {
            var1.setRecord(1, var2, 0, var2.length);
         }

         return;
      } catch (Exception var11) {
      } finally {
         try {
            var1.closeRecordStore();
         } catch (Exception var10) {
         }
      }
   }

   private void b(String var1) {
      try {
         if (this.j != var1) {
            this.j = var1;
            if (this.k != null) {
               this.k.close();
            }

            if (var1 != null) {
               this.k = Manager.createPlayer(this.getClass().getResourceAsStream(var1), "audio/midi");
               this.k.setLoopCount(-1);
               if (this.m > 0) {
                  this.i();
               }
            }
         }
      } catch (Exception var3) {
      }
   }

   private void i() throws MediaException {
      if (this.k.getState() != 400) {
         this.k.start();
      }

      this.l = (VolumeControl)this.k.getControl("VolumeControl");
      if (this.l != null) {
         this.l.setLevel(this.m);
      }
   }

   private void a(int var1) {
      if (this.k != null) {
         try {
            if (var1 > 0) {
               this.i();
            } else {
               this.k.stop();
            }

            return;
         } catch (Exception var3) {
         }
      }
   }

   static {
      Font.getFont(0, 0, 8);
   }
}
