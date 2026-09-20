/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Font
 *  javax.microedition.lcdui.Graphics
 *  javax.microedition.lcdui.Image
 *  javax.microedition.media.Manager
 *  javax.microedition.media.MediaException
 *  javax.microedition.media.Player
 *  javax.microedition.media.control.VolumeControl
 *  javax.microedition.midlet.MIDlet
 *  javax.microedition.rms.RecordStore
 *  javax.microedition.rms.RecordStoreException
 *  javax.microedition.rms.RecordStoreNotFoundException
 */
import java.io.IOException;
import java.io.InputStream;
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

public final class i
extends g {
    private Image g;
    private boolean h;
    private static final long i;
    private String j;
    private Player k;
    private VolumeControl l;
    private int m = 0;

    public i(MIDlet mIDlet) {
        super(mIDlet, new e(0, 0, 50000));
        String string = System.getProperty("microedition.profiles");
        if (string != null && string.indexOf("MIDP-2.0") >= 0) {
            this.f();
        }
        this.g = this.a("/splash.png");
        this.g();
        this.b("/avalonv5.mid");
    }

    private void f() {
        this.setFullScreenMode(true);
    }

    public final void a(Graphics graphics, e e2) {
        e e3 = this.c();
        if (e3 != e2 && e3 instanceof d) {
            try {
                e3.a(graphics, false);
            }
            catch (Exception exception) {}
        } else {
            Image image = this.g;
            graphics.setColor(0);
            graphics.fillRect(0, 0, 240, 320);
            if (image != null) {
                graphics.drawImage(image, 0, 0, 20);
            }
        }
        e2.a(graphics, true);
    }

    public final void a(int n, int n2, e e2) throws Exception {
        switch (e2.u) {
            case 0: {
                this.h = false;
                boolean bl = false;
                this.a(e2, false);
                return;
            }
            case 10: {
                if (n2 != 4) break;
                ((d)e2).a.d = null;
                this.a(e2, 8, false);
                return;
            }
        }
        if (n2 == 4) {
            this.b(e2);
            return;
        }
        this.repaint();
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     * Unable to fully structure code
     */
    private void a(e var1_1, boolean var2_2) {
        block21: {
            var3_3 = this;
            synchronized (var3_3) {
                if (this.g == null) {
                    return;
                }
                this.g = null;
            }
            g.a(false);
            var4_5 = null;
            var5_6 = null;
            var5_6 = RecordStore.openRecordStore((String)"key", (boolean)false);
            var4_5 = var5_6.getRecord(1);
            try {
                var5_6.closeRecordStore();
            }
            catch (Exception v0) {}
            break block21;
            catch (RecordStoreNotFoundException v1) {
                ** try [egrp 3[TRYBLOCK] [9 : 68->69)] { 
lbl23:
                // 1 sources

                try {
                    var5_6.closeRecordStore();
                }
                catch (Exception v2) {}
            }
            catch (RecordStoreException v3) {
                ** try [egrp 5[TRYBLOCK] [10 : 81->82)] { 
lbl-1000:
                // 3 sources

                {
                    catch (Throwable var7_7) {
                        try {
                            var5_6.closeRecordStore();
                        }
                        catch (Exception v4) {}
                        throw var7_7;
                    }
                }
lbl36:
                // 1 sources

                try {
                    var5_6.closeRecordStore();
                }
                catch (Exception v5) {}
            }
        }
        var3_3 = new b(1, var1_1);
        if (var4_5 != null && !var2_2) {
            var3_3.a(1, var4_5);
        }
        var3_3.a(2, "1.1.1");
        var3_3.b(3, 1);
        var3_3.b(4, 5);
        var3_3.b(5, 2);
        var3_3.a(6, "s700");
        var6_9 = System.getProperty("microedition.platform");
        if (var6_9 != null) {
            var3_3.a(7, var6_9);
        }
        if ((var7_8 = g.b.getAppProperty("INFO")) != null) {
            var3_3.a(8, var7_8);
        }
        this.a(var1_1, (b)var3_3);
    }

    public final void a(e e2, int n, Object object) throws IOException {
        if (object == "Back" || object == "Cancel" && e2.u != 23) {
            this.b(e2);
            return;
        }
        c c2 = e2 instanceof c ? (c)e2 : null;
        f f2 = object instanceof f ? (f)object : null;
        b b2 = null;
        boolean bl = false;
        switch (e2.u) {
            case 2: {
                this.a(e2, n == 0 ? 4 : 3, false);
                break;
            }
            case 3: 
            case 4: {
                b2 = new b(e2.u == 3 ? 2 : 3, e2);
                b2.a(2, c2.a((int)0).d.toString());
                b2.a(3, c2.a((int)1).d.toString());
                break;
            }
            case 5: {
                if (object == "Create hero") {
                    this.a(e2, 6, false);
                    break;
                }
                if (object == "Delete hero") {
                    Vector<String> vector = new Vector<String>();
                    vector.addElement("Cancel");
                    for (int k = 0; k < c2.b.size(); ++k) {
                        Object e3 = c2.b.elementAt(k);
                        if (!(e3 instanceof f)) continue;
                        vector.addElement(((f)e3).a);
                    }
                    Object[] objectArray = new String[vector.size()];
                    vector.copyInto(objectArray);
                    this.a(e2, new h(7, "Confirmation", "Select the hero you want to delete below.\nAction can not be undone!", (String[])objectArray), false);
                    break;
                }
                b2 = new b(4, e2);
                b2.a(1, f2.b());
                break;
            }
            case 6: {
                f f3 = c2.a(1);
                if (f3.j == -1) {
                    this.a(e2, new h(29, "Error", "Choose gender"), false);
                    return;
                }
                b2 = new b(5, e2);
                b2.a(1, c2.a((int)0).d.toString());
                b2.b(2, (Integer)f3.i[f3.j][1]);
                break;
            }
            case 7: {
                if (object != "Cancel") {
                    b2 = new b(6, e2);
                    b2.a(1, (String)object);
                    ((c)this.c((e)e2)).b.addElement("Create hero");
                    ((c)this.c(e2)).a(object);
                }
                this.b(e2);
                break;
            }
            case 34: {
                if (object != "Cancel") {
                    if (this.c() instanceof d) {
                        b2 = new b(9, e2);
                        ((d)this.c()).d(b2);
                    }
                    bl = true;
                    break;
                }
                this.b(e2);
                break;
            }
            case 8: {
                e e4 = this.c();
                if (object == "Start game" || object == "Resume game") {
                    if (!this.h) {
                        g.a(true);
                        b2 = new b(8, e2);
                        b2.b(1, 2);
                        b2.a(this.d);
                        b2.a(3, this.c);
                        break;
                    }
                    this.b(e2);
                    break;
                }
                if (object == "Hero info") {
                    Vector vector = i.a(new String[]{"Equipped items", "Spells", "Skills", "Hero sheet", "Back"});
                    if (e4 instanceof d) {
                        vector.insertElementAt("Quest items", 3);
                    }
                    this.a(e2, new c(9, "Hero info", vector), false);
                    break;
                }
                if (object == "Quest log") {
                    if (!(e4 instanceof d)) break;
                    this.a(e2, new h(30, "Quest log", ((d)e4).h()), false);
                    break;
                }
                if (object == "Save & exit") {
                    this.a(e2, new h(34, "Confirmation", "Save & exit game?", new String[]{"Save & exit", "Cancel"}), false);
                    break;
                }
                if (object == "Credits") {
                    this.a(e2, new h(30, "Credits", "\u0006\u00ff\u00ff\u00ffCopyright:\u0007\nwatAgame ApS\n\u0006\u00ff\u00ff\u00ffProducer:\u0007\nHenrik Riis\n\u0006\u00ff\u00ff\u00ffLead client code:\u0007\nLars Engholm Johansen\n\u0006\u00ff\u00ff\u00ffLead server code:\u0007\nBrian Thorsbro\n\u0006\u00ff\u00ff\u00ffStory line:\u0007\nThomas Laurfelt\n\u0006\u00ff\u00ff\u00ffArtwork:\u0007\nRobert Friis\nRiana Miller\n\u0006\u00ff\u00ff\u00ffQuality assurance:\u0007\nMikkel Meisler\n\u0006\u00ff\u00ff\u00ffTools & portings:\u0007\nMorten Nobel-J\u00f8rgensen\nLars Engholm Johansen\n\u0006\u00ff\u00ff\u00ffMusic:\u0007\nMario Barbosa\n\n\u0006\u00ff\u00ff\u00ffbrought to you:\n\u0007by pascha                                                "), false);
                    break;
                }
                if (object == "Score info") {
                    b2 = new b(20, e2);
                    b2.b(1, 2);
                    break;
                }
                if (object == "Rankings") {
                    b2 = new b(26, e2);
                    b2.b(1, 1);
                    break;
                }
                if (object == "More games") {
                    b2 = new b(7, e2);
                    b2.b(1, 6660);
                    break;
                }
                if (object == "Help") {
                    b2 = new b(27, e2);
                    break;
                }
                if (!object.toString().startsWith("Sound")) break;
                this.m = (this.m + 25) % 125;
                this.a(this.m);
                this.h();
                c2.b.setElementAt("Sound: " + this.m + "%", n);
                c2.b();
                break;
            }
            case 32: {
                e e5 = this.c();
                if (!(e5 instanceof d)) break;
                this.b(e2);
                d d2 = (d)e5;
                d2.a(f2.k);
                d2.b();
                break;
            }
            case 14: {
                e e6 = this.c();
                if (n == 6) {
                    if (!(e6 instanceof d)) break;
                    ((d)e6).f();
                    break;
                }
                this.a(e2, new h(15, "Confirmation", (String)f2.k, new String[]{"Add", "Cancel"}), false);
                break;
            }
            case 15: {
                e e7 = this.c(e2);
                e e8 = this.c();
                if (!(e7 instanceof c) || !(e8 instanceof d)) break;
                this.b(e2);
                ((d)e8).a(((c)e7).c);
                break;
            }
            case 9: {
                if (object == "Hero sheet") {
                    b2 = new b(20, e2);
                    b2.b(1, 1);
                    break;
                }
                if (object == "Equipped items") {
                    b2 = new b(21, e2);
                    break;
                }
                if (object == "Quest items") {
                    e e9 = this.c();
                    if (!(e9 instanceof d)) break;
                    Vector vector = ((d)e9).i();
                    vector.addElement("Back");
                    this.a(e2, new c(22, "Quest items", vector), false);
                    break;
                }
                if (object != "Skills" && object != "Spells") break;
                b2 = new b(25, e2);
                b2.b(1, object == "Skills" ? 9 : 13);
                break;
            }
            case 16: {
                b2 = new b(22, e2);
                b2.a(1, ((f)object).b);
                break;
            }
            case 17: {
                if (n == 0) {
                    b2 = new b(23, e2);
                    b2.a(1, f2.b);
                    c c3 = (c)this.c(e2);
                    ((c)this.c(e2)).f().a = "";
                    c3.f().c = "Nothing equipped";
                    break;
                }
                this.a(e2, new h(18, f2.a, f2.d(), new String[]{"Back", "Equip", "Delete"}), false);
                break;
            }
            case 18: 
            case 20: {
                if (object == "Equip") {
                    c c4 = (c)this.c(e2);
                    b2 = new b(23, c4);
                    b2.a(1, c4.f().b);
                } else if (object == "Delete") {
                    this.a(e2, new h(21, "Confirmation", "Are you sure you want to delete this?\nAction can not be undone!", new String[]{"Cancel", "Delete"}), false);
                    break;
                }
                e2 = this.b(e2);
                break;
            }
            case 21: {
                c c5 = (c)this.c(this.c(e2));
                f f4 = c5.f();
                if (c5.u == 17) {
                    c c6 = (c)this.c(c5);
                    f f5 = c6.f();
                    if (f5.a.equals(f4.a)) {
                        f5.a = "";
                        f5.c = "Nothing equipped";
                    }
                }
                b2 = new b(24, e2);
                b2.a(1, f4.b);
                c5.b.removeElementAt(c5.c);
                c5.b();
                this.b(this.b(e2));
                e2 = null;
                break;
            }
            case 29: {
                if (object == "Icon overview 2") {
                    b2 = new b(7, e2);
                    b2.b(1, 6659);
                    break;
                }
                if (object == "Icon overview 1") {
                    b2 = new b(28, e2);
                    break;
                }
                String string = f2.d();
                if (string == null) break;
                this.a(e2, new h(30, f2.a, string), false);
                break;
            }
            case 22: {
                this.a(e2, new h(30, f2.a, ((d)this.c()).b(Integer.parseInt(f2.d()))), false);
                break;
            }
            case 19: {
                this.a(e2, new h(20, f2.a, f2.d(), new String[]{"Back", "Delete"}), false);
                break;
            }
            case 11: {
                b2 = new b(15, e2);
                b2.b(1, n);
                break;
            }
            case 12: {
                String[] stringArray;
                String string = f2.a;
                String string2 = f2.d();
                if ((f2.g & 0x20) == 0) {
                    String[] stringArray2 = new String[2];
                    stringArray2[0] = "Back";
                    stringArray = stringArray2;
                    stringArray2[1] = "Buy";
                } else {
                    stringArray = null;
                }
                this.a(e2, new h(13, string, string2, stringArray), false);
                break;
            }
            case 13: {
                c c7 = (c)this.c(e2);
                b2 = new b(16, e2);
                b2.a(1, c7.f().b);
                break;
            }
            case 35: {
                e e10;
                if (object != "Continue" || !((e10 = this.c()) instanceof d)) break;
                this.b(e2);
                this.d();
                d d3 = (d)e10;
                d3.g();
                break;
            }
            case 23: {
                b2 = new b(18, e2);
                if (object == "Balance") {
                    b2.b(1, 1);
                }
                this.b(e2);
                break;
            }
            case 24: {
                if (object == "Accept") {
                    b2 = new b(19, e2);
                    break;
                }
                this.a(e2, new e(33, 1), false);
                break;
            }
            case 36: {
                e e11 = this.c();
                if (e11 instanceof d) {
                    d d4 = (d)e11;
                    d4.f = n == 0;
                    d4.a(d4.e, d4.f);
                }
                this.b(e2);
                this.d();
            }
        }
        if (b2 != null) {
            this.a(e2, b2);
        }
        if (bl) {
            this.a(e2, new e(33, 1), false);
        }
    }

    private void a(e e2, int n, boolean bl) {
        switch (n) {
            case 3: 
            case 4: {
                this.a(e2, new c(n, n == 3 ? "Please login" : "Please register", i.a(new Object[]{new f("Type login", null, 14), new f("Type password", null, 14), "Continue", "Back"})), bl);
                return;
            }
            case 6: {
                this.a(e2, new c(n, "Create hero", i.a(new Object[]{new f("Hero name", null, 14), new f("Choose gender", new Object[][]{{"Male", new Integer(1)}, {"Female", new Integer(2)}}), "Create hero", "Cancel"})), bl);
                return;
            }
            case 8: {
                Vector vector = i.a(new Object[]{"Hero info", "Score info", "Rankings", "Help", "More games", "Credits", "Save & exit"});
                if (e2 instanceof d) {
                    vector.insertElementAt("Resume game", 0);
                    vector.insertElementAt("Quest log", 4);
                } else {
                    vector.insertElementAt("Start game", 0);
                }
                vector.insertElementAt("Sound: " + this.m + "%", vector.size() - 1);
                this.a(e2, new c(n, "Main menu", vector), bl);
            }
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     * Unable to fully structure code
     */
    public final void a(e var1_1, b var2_2, Throwable var3_3) throws Exception {
        block54: {
            if (var3_3 != null) break block54;
            var4_4 = null;
            switch (var2_2.u) {
                case 1: 
                case 2: 
                case 19: {
                    if (var2_2.c != 1 && var2_2.c != 5 || (var5_5 = (byte[])var2_2.d.get(new Integer(21))) == null) ** GOTO lbl24
                    var6_8 = RecordStore.openRecordStore((String)"key", (boolean)true);
                    try {
                        if (var6_8.getNumRecords() != 0) ** GOTO lbl12
                        var6_8.addRecord((byte[])var5_5, 0, ((Object)var5_5).length);
                        ** GOTO lbl19
lbl12:
                        // 1 sources

                        var6_8.setRecord(1, (byte[])var5_5, 0, ((Object)var5_5).length);
                    }
                    catch (Throwable var8_16) {
                        try {
                            var6_8.closeRecordStore();
                        }
                        catch (RecordStoreException v0) {}
                        throw var8_16;
                    }
lbl19:
                    // 2 sources

                    try {
                        var6_8.closeRecordStore();
                    }
                    catch (RecordStoreException v1) {}
lbl24:
                    // 3 sources

                    switch (var2_2.c) {
                        case 1: {
                            v2 = var2_2.a(20);
                            var5_5 = v2;
                            if (v2.size() == 0) {
                                this.a(var1_1, 6, true);
                                return;
                            }
                            if (var5_5.size() < 2) {
                                var5_5.addElement("Create hero");
                            }
                            var5_5.addElement("Delete hero");
                            this.a(null, new c(5, "Select hero", (Vector)var5_5), true);
                            break;
                        }
                        case 2: {
                            this.a(null, new h(2, null, var2_2.c(21), new String[]{"New user", "Existing user"}), true);
                            break;
                        }
                        case 3: {
                            break;
                        }
                        case 4: {
                            this.a(var1_1, new e(33, 1), false);
                            break;
                        }
                        case 5: {
                            this.a(var1_1, new h(24, null, var2_2.c(22), new String[]{"Accept", "Decline"}), false);
                        }
                    }
                    break;
                }
                case 3: {
                    switch (var2_2.c) {
                        case 1: {
                            var2_2.u = 2;
                            this.a(var1_1, var2_2, var3_3);
                        }
                    }
                    break;
                }
                case 5: {
                    switch (var2_2.c) {
                        case 1: {
                            this.a(var1_1, 8, false);
                            this.b(var1_1);
                            break;
                        }
                        case 2: {
                            var5_6 = var2_2.c(20);
                            if (var5_6 == null || !(var1_1 instanceof c)) break;
                            var6_9 = ((c)var1_1).a((int)0).d;
                            var6_9.setLength(0);
                            var6_9.append(var5_6);
                        }
                    }
                    break;
                }
                case 4: 
                case 18: {
                    switch (var2_2.c) {
                        case 1: {
                            this.a(var1_1, 8, false);
                            break;
                        }
                        case 2: {
                            this.a(var1_1, new h(23, null, var2_2.c(20), new String[]{"Balance", "Cancel"}), false);
                        }
                    }
                    break;
                }
                case 20: {
                    this.a(var1_1, new h(30, var2_2.c(23), var2_2.c(20)), false);
                    break;
                }
                case 21: {
                    var5_7 = var2_2.a(20);
                    var5_7.addElement("Back");
                    this.a(var1_1, new c(16, "Equipped items", var5_7), false);
                    break;
                }
                case 22: {
                    var6_10 = var2_2.a(20);
                    var6_10.addElement("Back");
                    var7_18 = new c(17, var2_2.c(21), var6_10);
                    new c(17, var2_2.c(21), var6_10).c = var2_2.b(22);
                    this.a(var1_1, var7_18, false);
                    break;
                }
                case 23: {
                    if (var2_2.c == 1) {
                        var6_11 = (c)var1_1;
                        if (var6_11.c != 0) {
                            var7_19 = (c)this.c(var1_1);
                            var8_17 = (f)var6_11.b.elementAt(var6_11.c);
                            ((f)var6_11.b.elementAt(var6_11.c)).b = var7_19.f().b;
                            var7_19.b.setElementAt(var8_17, var7_19.c);
                        }
                    }
                    this.b(var1_1);
                    break;
                }
                case 15: 
                case 25: {
                    var6_12 = var2_2.a(20);
                    var6_12.addElement("Back");
                    this.a(var1_1, new c(var2_2.u == 15 ? 12 : 19, var2_2.c(21), var6_12), false);
                    break;
                }
                case 27: {
                    var6_13 = var2_2.a(20);
                    var6_13.addElement("Icon overview 1");
                    var6_13.addElement("Icon overview 2");
                    var6_13.addElement("Back");
                    this.a(var1_1, new c(29, var2_2.c(21), var6_13), false);
                    break;
                }
                case 26: 
                case 28: {
                    var6_14 = var2_2.a(20);
                    var6_14.addElement("Back");
                    this.a(var1_1, new c(29, var2_2.c(21), var6_14), false);
                    break;
                }
                case 8: {
                    switch (var2_2.c) {
                        case 1: 
                        case 2: {
                            var6_15 = (byte[][])this.d.get(new Integer(256));
                            if (var6_15 == null) {
                                var6_15 = g.b(this.c(1, 0, null));
                            }
                            if ((var7_20 = (byte[][])this.d.get(new Integer(2304))) == null) {
                                var7_20 = g.b(this.c(9, 0, null));
                            }
                            this.a(var1_1, new d(10, 240, 290, var6_15, var7_20, var2_2, var2_2.c == 2), true);
                            this.h = true;
                        }
                    }
                    break;
                }
                case 12: {
                    if (!(var1_1 instanceof d)) break;
                    if (var2_2.i) {
                        ((d)var1_1).b(var2_2);
                        break;
                    }
                    ((d)var1_1).a(var2_2);
                    break;
                }
                case 13: {
                    if (!(var1_1 instanceof d)) break;
                    ((d)var1_1).e(var2_2);
                    break;
                }
                case 11: {
                    if (!(var1_1 instanceof d)) break;
                    ((d)var1_1).c(var2_2);
                    break;
                }
                case 16: {
                    this.b(this.c(var1_1));
                    this.b(var1_1);
                    break;
                }
                case 9: {
                    this.b(var1_1);
                    break;
                }
                case 17: {
                    this.a(var1_1, new e(33, 1), false);
                }
            }
            return;
        }
        this.a("net(" + var2_2.u + ")", var1_1, "Network error", var3_3, false);
    }

    public final int a(e e2) {
        if (this.g != null && e2.t > i && !this.h) {
            this.a(e2, false);
        }
        e.a(true);
        return 3000;
    }

    public final void a(String string, e e2, String string2, Throwable throwable, boolean bl) {
        Object object;
        String string3 = "";
        if (throwable != null) {
            object = throwable.toString();
            string3 = ((String)object).substring(((String)object).lastIndexOf(46, ((String)object).indexOf(58)) + 1);
            if (string3.startsWith("Run")) {
                string3 = throwable.getMessage();
            }
            if (throwable instanceof IOException) {
                string3 = "";
                string = "Problem with your operator" + (throwable.getMessage() == null ? "" : ":\n" + throwable.getMessage());
            } else {
                string3 = string3 + "\n\n";
            }
        }
        object = new h(0, string2 == null ? "Error" : string2, string + "\n\n" + string3 + "s" + e2.u + " v" + g.b.getAppProperty("MIDlet-Version"));
        if (bl) {
            this.a(e2, (e)object);
            return;
        }
        this.a(e2, (e)object, false);
    }

    public static final Vector a(Object[] objectArray) {
        Vector<Object> vector = new Vector<Object>(objectArray.length);
        for (int k = 0; k < objectArray.length; ++k) {
            vector.addElement(objectArray[k]);
        }
        return vector;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     * Unable to fully structure code
     */
    private void g() {
        this.m = 50;
        var1_1 = null;
        var2_2 = null;
        var2_2 = RecordStore.openRecordStore((String)"vol", (boolean)false);
        var1_1 = var2_2.getRecord(1);
        this.m = var1_1[0];
        try {
            var2_2.closeRecordStore();
            return;
        }
        catch (Exception v0) {
            return;
        }
        catch (RecordStoreNotFoundException v1) {
            ** try [egrp 2[TRYBLOCK] [6 : 37->38)] { 
lbl15:
            // 1 sources

            try {
                var2_2.closeRecordStore();
                return;
            }
            catch (Exception v2) {
                return;
            }
        }
        catch (RecordStoreException v3) {
            ** try [egrp 4[TRYBLOCK] [7 : 45->46)] { 
lbl-1000:
            // 3 sources

            {
                catch (Throwable var4_3) {
                    try {
                        var2_2.closeRecordStore();
                    }
                    catch (Exception v4) {}
                    throw var4_3;
                }
            }
lbl28:
            // 1 sources

            try {
                var2_2.closeRecordStore();
                return;
            }
            catch (Exception v5) {
                return;
            }
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     * Loose catch block
     */
    private void h() {
        RecordStore recordStore;
        block11: {
            recordStore = null;
            recordStore = RecordStore.openRecordStore((String)"vol", (boolean)true);
            byte[] byArray = new byte[]{(byte)this.m};
            if (recordStore.getNumRecords() == 0) {
                recordStore.addRecord(byArray, 0, byArray.length);
                break block11;
            }
            recordStore.setRecord(1, byArray, 0, byArray.length);
        }
        try {
            recordStore.closeRecordStore();
            return;
        }
        catch (Exception exception) {
            return;
        }
        catch (Exception exception) {
            try {}
            catch (Throwable throwable) {
                try {
                    recordStore.closeRecordStore();
                }
                catch (Exception exception2) {}
                throw throwable;
            }
            try {
                recordStore.closeRecordStore();
                return;
            }
            catch (Exception exception3) {
                return;
            }
        }
    }

    private void b(String string) {
        try {
            if (this.j == string) {
                return;
            }
            this.j = string;
            if (this.k != null) {
                this.k.close();
            }
            if (string != null) {
                this.k = Manager.createPlayer((InputStream)this.getClass().getResourceAsStream(string), (String)"audio/midi");
                this.k.setLoopCount(-1);
                if (this.m > 0) {
                    this.i();
                }
            }
            return;
        }
        catch (Exception exception) {
            return;
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

    private void a(int n) {
        if (this.k != null) {
            try {
                if (n > 0) {
                    this.i();
                } else {
                    this.k.stop();
                }
                return;
            }
            catch (Exception exception) {}
        }
    }

    static {
        Font.getFont((int)0, (int)0, (int)8);
        i = System.currentTimeMillis() + 50000L;
    }
}

