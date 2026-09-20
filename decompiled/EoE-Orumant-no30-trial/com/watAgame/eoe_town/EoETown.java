/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Command
 *  javax.microedition.lcdui.CommandListener
 *  javax.microedition.lcdui.Display
 *  javax.microedition.lcdui.Displayable
 *  javax.microedition.lcdui.Form
 *  javax.microedition.lcdui.Image
 *  javax.microedition.lcdui.Item
 *  javax.microedition.lcdui.List
 *  javax.microedition.lcdui.StringItem
 *  javax.microedition.lcdui.TextBox
 *  javax.microedition.midlet.MIDlet
 *  javax.microedition.rms.RecordStore
 *  javax.microedition.rms.RecordStoreException
 */
package com.watAgame.eoe_town;

import com.watAgame.eoe_town.b;
import java.util.Vector;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Form;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.Item;
import javax.microedition.lcdui.List;
import javax.microedition.lcdui.StringItem;
import javax.microedition.lcdui.TextBox;
import javax.microedition.midlet.MIDlet;
import javax.microedition.rms.RecordStore;
import javax.microedition.rms.RecordStoreException;

public class EoETown
extends MIDlet
implements CommandListener {
    private final Command l = new Command("Back", 2, 1);
    private final Command g = new Command("Reply", 8, 2);
    private final Command i = new Command("Read", 8, 1);
    private final Command h = new Command("Delete", 8, 2);
    private final Command o = new Command("Cancel", 3, 1);
    private final Command j = new Command("Send", 4, 1);
    private b n;
    private String c;
    private static final Image p = com.watAgame.eoe_town.b.a("read", true);
    private static final Image e = com.watAgame.eoe_town.b.a("unread", true);
    private List m;
    private List d;
    private TextBox q;
    private Form f = new Form("temp");
    private Displayable k;
    private int b;
    private final Form a;

    public EoETown() {
        new List("", 3, new String[]{"Read", "Reply", "Delete", "Town", "Back"}, null);
        this.a = new Form("Please wait");
    }

    public final void startApp() {
        this.a.append((Item)new StringItem("Please wait", ""));
        Displayable displayable = Display.getDisplay((MIDlet)this).getCurrent();
        if (displayable == null) {
            this.n = new b(this);
            Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.n);
            return;
        }
        Display.getDisplay((MIDlet)this).setCurrent(displayable);
    }

    protected final void pauseApp() {
    }

    protected final void destroyApp(boolean bl) {
        if (this.n.Z != null) {
            this.n.Z.a();
        }
        this.n.ay = null;
        if (bl) {
            this.notifyDestroyed();
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    protected static final String a(String string, int n) {
        String string2;
        RecordStore recordStore = null;
        recordStore = RecordStore.openRecordStore((String)string, (boolean)false);
        try {
            if (n == -1) {
                n = recordStore.getNumRecords();
            }
            string2 = new String(recordStore.getRecord(n), "UTF-8");
        }
        catch (Throwable throwable) {
            try {
                recordStore.closeRecordStore();
                throw throwable;
            }
            catch (Exception exception) {
                return "";
            }
        }
        recordStore.closeRecordStore();
        return string2;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    protected static final void a(String string, Vector vector) throws RecordStoreException {
        RecordStore recordStore = RecordStore.openRecordStore((String)string, (boolean)true);
        try {
            for (int i = 0; i < vector.size(); ++i) {
                byte[] byArray = com.watAgame.eoe_town.b.c((String)vector.elementAt(i));
                recordStore.addRecord(byArray, 0, byArray.length);
                if (i % 4 != 0) continue;
                Thread.yield();
            }
            return;
        }
        finally {
            recordStore.closeRecordStore();
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    protected static final void a(String string, String string2) throws RecordStoreException {
        RecordStore recordStore = RecordStore.openRecordStore((String)string, (boolean)true);
        try {
            byte[] byArray = com.watAgame.eoe_town.b.c(string2);
            recordStore.addRecord(byArray, 0, byArray.length);
            return;
        }
        finally {
            recordStore.closeRecordStore();
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    protected static final void a(String string) throws RecordStoreException {
        RecordStore recordStore = RecordStore.openRecordStore((String)string, (boolean)false);
        recordStore.closeRecordStore();
        try {
            RecordStore.deleteRecordStore((String)string);
            return;
        }
        finally {
            recordStore.closeRecordStore();
            RecordStore.deleteRecordStore((String)string);
        }
    }

    public final void commandAction(Command command, Displayable displayable) {
        if (!this.n.be) {
            return;
        }
        if (displayable == this.m) {
            this.b = this.m.getSelectedIndex();
            if (this.b >= 0) {
                this.n.ai = this.n.bx[this.b][2];
                this.c = this.m.getString(this.m.getSelectedIndex());
            }
            if (command == this.i || command == List.SELECT_COMMAND) {
                Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.a);
                this.f.setTitle("Please wait");
                while (this.f.size() > 0) {
                    this.f.delete(0);
                }
                this.n.b();
                return;
            }
            if (command == this.g) {
                this.n.aJ = this.m.getString(this.m.getSelectedIndex());
                this.a();
                return;
            }
            if (command == this.h) {
                this.n.h(this.b);
                this.m.delete(this.b);
                if (this.m.size() == 0) {
                    this.a(new String[0][0]);
                }
                Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.a);
                return;
            }
            if (command == this.l) {
                this.n.l();
                return;
            }
        } else if (displayable == this.q) {
            if (command == this.o) {
                Display.getDisplay((MIDlet)this).setCurrent(this.k);
                return;
            }
            if (command == this.j) {
                this.n.af = this.q.getString();
                this.n.s();
                return;
            }
        } else if (displayable == this.f) {
            if (command == this.l) {
                this.b();
                return;
            }
            if (command == this.g) {
                this.n.aJ = this.c;
                this.a();
                return;
            }
            if (command == this.h) {
                this.n.h(this.b);
                this.m.delete(this.b);
                Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.a);
                return;
            }
        } else if (displayable == this.d) {
            if (command == this.l) {
                this.n.l();
                return;
            }
            this.n.aJ = this.d.getString(this.d.getSelectedIndex());
            this.a();
        }
    }

    public final void a(String[][] stringArray) {
        Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.a);
        int n = 10;
        while (!this.a.isShown() && n-- > 0) {
            try {
                Thread.sleep(100L);
            }
            catch (InterruptedException interruptedException) {}
        }
        this.m = new List("Inbox", 3);
        if (stringArray.length > 0) {
            for (int i = 0; i < stringArray.length; ++i) {
                this.m.append(stringArray[i][0], stringArray[i][1].equals("1") ? p : e);
            }
            this.m.addCommand(this.i);
            this.m.addCommand(this.h);
            this.m.addCommand(this.g);
        }
        this.m.addCommand(this.l);
        this.m.setCommandListener((CommandListener)this);
        Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.m);
    }

    public final void a(String[] stringArray) {
        this.d = new List("Names", 3, stringArray, null);
        this.d.addCommand(this.l);
        this.d.setCommandListener((CommandListener)this);
        this.k = Display.getDisplay((MIDlet)this).getCurrent();
        Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.d);
    }

    final void b() {
        this.m.set(this.m.getSelectedIndex(), this.n.bx[this.m.getSelectedIndex()][0], p);
        this.k = Display.getDisplay((MIDlet)this).getCurrent();
        Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.m);
    }

    final void a() {
        this.q = new TextBox("To: ".concat(this.n.aJ), null, 120, 0);
        this.q.addCommand(this.j);
        this.q.addCommand(this.o);
        this.q.setCommandListener((CommandListener)this);
        this.k = Display.getDisplay((MIDlet)this).getCurrent();
        Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.q);
    }

    final void c() {
        this.n.be = true;
        this.f.setTitle(this.n.G);
        this.f.append("From: " + this.c + "\n");
        this.f.append(this.n.af);
        this.f.addCommand(this.h);
        this.f.addCommand(this.g);
        this.f.addCommand(this.l);
        this.f.setCommandListener((CommandListener)this);
        this.k = Display.getDisplay((MIDlet)this).getCurrent();
        Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.f);
    }
}

