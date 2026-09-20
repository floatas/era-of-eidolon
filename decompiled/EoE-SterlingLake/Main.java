/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.microedition.lcdui.Display
 *  javax.microedition.lcdui.Displayable
 *  javax.microedition.lcdui.Form
 *  javax.microedition.midlet.MIDlet
 *  javax.microedition.midlet.MIDletStateChangeException
 */
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Form;
import javax.microedition.midlet.MIDlet;
import javax.microedition.midlet.MIDletStateChangeException;

public class Main
extends MIDlet {
    private i a;

    public final void startApp() throws MIDletStateChangeException {
        try {
            this.a = new i(this);
            Display.getDisplay((MIDlet)this).setCurrent((Displayable)this.a);
            return;
        }
        catch (Throwable throwable) {
            Form form = new Form("Error");
            form.append(throwable.getClass().getName());
            if (throwable.getMessage() != null) {
                form.append(throwable.getMessage());
            }
            Display.getDisplay((MIDlet)this).setCurrent((Displayable)form);
            return;
        }
    }

    public final void pauseApp() {
    }

    public final void destroyApp(boolean bl) throws MIDletStateChangeException {
        if (this.a != null) {
            this.a.a();
        }
    }
}

