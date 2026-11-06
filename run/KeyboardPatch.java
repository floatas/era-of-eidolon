import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

import org.objectweb.asm.ClassAdapter;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Label;
import org.objectweb.asm.MethodAdapter;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;

/**
 * Teach the online phone jars to take a desktop keyboard.
 *
 * The text boxes only accept phone keys 0-9, star, and the clear key, and
 * they force the first character up and the rest down. This adds a path that
 * inserts the key that was actually pressed, and makes Escape a back key
 * instead of a delete key. Originals in jars/ are not modified; play-card.sh
 * and play-town.sh run this on the copy in run/.
 */
public class KeyboardPatch implements Opcodes {
    // Screens where the left soft key only leaves the text box. 71, 73, and 80
    // send the form on that key when the box is not empty, so Escape uses the
    // empty-box exit instead of pretending to be confirm.
    static final int[] TEXT_SCREENS = {12, 31, 59, 60, 83, 84, 112};

    static final class Card {
        final String method;
        final String editing;
        final String rows;
        final String index;
        final String cursor;
        final String row;
        final String buffer;
        final String max;
        final String width;
        final String widthMethod;
        final String pad;
        final String dirty;

        Card(String method, String editing, String rows, String index, String cursor,
             String row, String buffer, String max, String width, String widthMethod,
             String pad, String dirty) {
            this.method = method;
            this.editing = editing;
            this.rows = rows;
            this.index = index;
            this.cursor = cursor;
            this.row = row;
            this.buffer = buffer;
            this.max = max;
            this.width = width;
            this.widthMethod = widthMethod;
            this.pad = pad;
            this.dirty = dirty;
        }
    }

    static final class Town {
        final String buffer;
        final String pending;
        final String max;
        final String last;
        final String timer;
        final String screen;

        Town(String buffer, String pending, String max, String last, String timer, String screen) {
            this.buffer = buffer;
            this.pending = pending;
            this.max = max;
            this.last = last;
            this.timer = timer;
            this.screen = screen;
        }
    }

    static Card cardFor(String name) {
        if ("c".equals(name)) {
            return new Card("a", "y", "a", "b", "B", "i", "d", "e", "v", "a", "E", "x");
        }
        if ("d".equals(name)) {
            return new Card("b", "c", "j", "d", "D", "j", "c", "b", "n", "c", "e", "w");
        }
        return null;
    }

    static Town townFor(String name) {
        if ("com/watAgame/eoe_town/b".equals(name)) {
            return new Town("ak", "bB", "D", "bk", "aO", "i");
        }
        if ("b".equals(name)) {
            return new Town("aj", "bA", "D", "bj", "aN", "j");
        }
        return null;
    }

    public static byte[] patch(byte[] in) {
        ClassReader cr = new ClassReader(in);
        String name = cr.getClassName();
        Card card = cardFor(name);
        Town town = townFor(name);
        if (card == null && town == null) {
            return null;
        }
        // Poker’s canvas is also named d. Only the form that still has the
        // phone keypad table ("abc2") is a text box.
        if (!contains(in, new byte[] {'a', 'b', 'c', '2'})) {
            return null;
        }
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
        Adapter adapter = new Adapter(cw, name, card, town);
        cr.accept(adapter, 0);
        if (!adapter.rewrote) {
            return null;
        }
        return cw.toByteArray();
    }

    static boolean contains(byte[] hay, byte[] needle) {
        outer:
        for (int i = 0; i + needle.length <= hay.length; i++) {
            for (int j = 0; j < needle.length; j++) {
                if (hay[i + j] != needle[j]) {
                    continue outer;
                }
            }
            return true;
        }
        return false;
    }

    static final class Adapter extends ClassAdapter {
        final String owner;
        final Card card;
        final Town town;
        boolean rewrote;

        Adapter(ClassVisitor cv, String owner, Card card, Town town) {
            super(cv);
            this.owner = owner;
            this.card = card;
            this.town = town;
        }

        public MethodVisitor visitMethod(int access, String name, String desc,
                                          String sig, String[] ex) {
            MethodVisitor mv = super.visitMethod(access, name, desc, sig, ex);
            if (card != null && name.equals(card.method) && "(II)Z".equals(desc)) {
                rewrote = true;
                return new CardKeys(mv, owner, card);
            }
            if (town != null && "a".equals(name) && "(IZ)V".equals(desc)) {
                rewrote = true;
                return new TownKeys(mv, owner, town);
            }
            if (town != null && "keyPressed".equals(name) && "(I)V".equals(desc)) {
                rewrote = true;
                return new TownEscape(mv, owner, town.screen);
            }
            return mv;
        }

        public void visitEnd() {
            if (card != null && rewrote) {
                emitType(cv, owner, card);
            }
            super.visitEnd();
        }
    }

    /** Insert the pressed character while a card-game text row is open. */
    static void emitType(ClassVisitor cv, String owner, Card c) {
        MethodVisitor mv = cv.visitMethod(ACC_PRIVATE, "kbType", "(I)Z", null, null);
        mv.visitCode();
        Label out = new Label();
        Label del = new Label();
        Label typed = new Label();
        Label full = new Label();
        mv.visitVarInsn(ALOAD, 0);
        mv.visitFieldInsn(GETFIELD, owner, c.editing, "Z");
        mv.visitJumpInsn(IFEQ, out);
        mv.visitVarInsn(ILOAD, 1);
        mv.visitIntInsn(BIPUSH, 8);
        mv.visitJumpInsn(IF_ICMPEQ, del);
        mv.visitVarInsn(ILOAD, 1);
        mv.visitIntInsn(BIPUSH, -8);
        mv.visitJumpInsn(IF_ICMPNE, typed);
        mv.visitLabel(del);
        row(mv, owner, c);
        mv.visitVarInsn(ALOAD, 0);
        mv.visitFieldInsn(GETFIELD, owner, c.cursor, "I");
        Label swallowed = new Label();
        mv.visitJumpInsn(IFLE, swallowed);
        mv.visitVarInsn(ALOAD, 0);
        mv.visitInsn(DUP);
        mv.visitFieldInsn(GETFIELD, owner, c.cursor, "I");
        mv.visitInsn(ICONST_1);
        mv.visitInsn(ISUB);
        mv.visitFieldInsn(PUTFIELD, owner, c.cursor, "I");
        mv.visitVarInsn(ALOAD, 2);
        mv.visitFieldInsn(GETFIELD, c.row, c.buffer, "Ljava/lang/StringBuffer;");
        mv.visitVarInsn(ALOAD, 0);
        mv.visitFieldInsn(GETFIELD, owner, c.cursor, "I");
        mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuffer", "deleteCharAt",
                "(I)Ljava/lang/StringBuffer;");
        mv.visitInsn(POP);
        mv.visitLabel(swallowed);
        mv.visitInsn(ICONST_1);
        mv.visitInsn(IRETURN);
        mv.visitLabel(typed);
        mv.visitVarInsn(ILOAD, 1);
        mv.visitIntInsn(BIPUSH, 32);
        mv.visitJumpInsn(IF_ICMPLT, out);
        mv.visitVarInsn(ILOAD, 1);
        mv.visitIntInsn(BIPUSH, 126);
        mv.visitJumpInsn(IF_ICMPGT, out);
        row(mv, owner, c);
        mv.visitVarInsn(ALOAD, 2);
        mv.visitFieldInsn(GETFIELD, c.row, c.buffer, "Ljava/lang/StringBuffer;");
        mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuffer", "length", "()I");
        mv.visitVarInsn(ALOAD, 2);
        mv.visitFieldInsn(GETFIELD, c.row, c.max, "I");
        mv.visitJumpInsn(IF_ICMPGE, full);
        mv.visitVarInsn(ALOAD, 2);
        mv.visitFieldInsn(GETFIELD, c.row, c.buffer, "Ljava/lang/StringBuffer;");
        mv.visitVarInsn(ALOAD, 0);
        mv.visitFieldInsn(GETFIELD, owner, c.cursor, "I");
        mv.visitVarInsn(ILOAD, 1);
        mv.visitInsn(I2C);
        mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuffer", "insert",
                "(IC)Ljava/lang/StringBuffer;");
        mv.visitInsn(POP);
        mv.visitVarInsn(ALOAD, 0);
        mv.visitInsn(DUP);
        mv.visitFieldInsn(GETFIELD, owner, c.cursor, "I");
        mv.visitInsn(ICONST_1);
        mv.visitInsn(IADD);
        mv.visitFieldInsn(PUTFIELD, owner, c.cursor, "I");
        mv.visitVarInsn(ALOAD, 0);
        mv.visitVarInsn(ALOAD, 0);
        mv.visitFieldInsn(GETFIELD, owner, c.width, "I");
        mv.visitVarInsn(ALOAD, 2);
        mv.visitMethodInsn(INVOKEVIRTUAL, c.row, c.widthMethod, "()I");
        mv.visitMethodInsn(INVOKESTATIC, "java/lang/Math", "max", "(II)I");
        mv.visitFieldInsn(PUTFIELD, owner, c.width, "I");
        mv.visitVarInsn(ALOAD, 0);
        mv.visitVarInsn(ALOAD, 0);
        mv.visitFieldInsn(GETFIELD, owner, c.width, "I");
        mv.visitInsn(ICONST_2);
        mv.visitInsn(IADD);
        mv.visitVarInsn(ALOAD, 0);
        mv.visitFieldInsn(GETFIELD, owner, c.pad, "I");
        mv.visitInsn(IADD);
        mv.visitMethodInsn(INVOKEVIRTUAL, owner, "b", "(I)V");
        mv.visitVarInsn(ALOAD, 0);
        mv.visitInsn(ICONST_1);
        mv.visitFieldInsn(PUTFIELD, owner, c.dirty, "Z");
        mv.visitLabel(full);
        mv.visitInsn(ICONST_1);
        mv.visitInsn(IRETURN);
        mv.visitLabel(out);
        mv.visitInsn(ICONST_0);
        mv.visitInsn(IRETURN);
        mv.visitMaxs(4, 3);
        mv.visitEnd();
    }

    static void row(MethodVisitor mv, String owner, Card c) {
        mv.visitVarInsn(ALOAD, 0);
        mv.visitFieldInsn(GETFIELD, owner, c.rows, "Ljava/util/Vector;");
        mv.visitVarInsn(ALOAD, 0);
        mv.visitFieldInsn(GETFIELD, owner, c.index, "I");
        mv.visitMethodInsn(INVOKEVIRTUAL, "java/util/Vector", "elementAt", "(I)Ljava/lang/Object;");
        mv.visitTypeInsn(CHECKCAST, c.row);
        mv.visitVarInsn(ASTORE, 2);
    }

    static final class CardKeys extends MethodAdapter {
        final String owner;
        final Card card;

        CardKeys(MethodVisitor mv, String owner, Card card) {
            super(mv);
            this.owner = owner;
            this.card = card;
        }

        public void visitCode() {
            super.visitCode();
            mv.visitVarInsn(ALOAD, 0);
            mv.visitVarInsn(ILOAD, 1);
            mv.visitMethodInsn(INVOKESPECIAL, owner, "kbType", "(I)Z");
            Label cont = new Label();
            mv.visitJumpInsn(IFEQ, cont);
            mv.visitInsn(ICONST_1);
            mv.visitInsn(IRETURN);
            mv.visitLabel(cont);
        }

        public void visitIntInsn(int opcode, int operand) {
            // -7 is the right soft key. While a field is open the phone used
            // it as backspace, so Escape could not leave the screen.
            if (opcode == BIPUSH && operand == -7) {
                operand = -100;
            }
            super.visitIntInsn(opcode, operand);
        }
    }

    /** Letters go straight into the town buffer. Escape no longer deletes. */
    static final class TownKeys extends MethodAdapter {
        final String owner;
        final Town town;

        TownKeys(MethodVisitor mv, String owner, Town town) {
            super(mv);
            this.owner = owner;
            this.town = town;
        }

        public void visitCode() {
            super.visitCode();
            Label del = new Label();
            Label notDel = new Label();
            Label delBuf = new Label();
            Label delDone = new Label();
            Label notChar = new Label();
            Label noPend = new Label();
            Label typed = new Label();
            Label original = new Label();
            mv.visitVarInsn(ILOAD, 1);
            mv.visitIntInsn(BIPUSH, 8);
            mv.visitJumpInsn(IF_ICMPEQ, del);
            mv.visitVarInsn(ILOAD, 1);
            mv.visitIntInsn(BIPUSH, -8);
            mv.visitJumpInsn(IF_ICMPNE, notDel);
            mv.visitLabel(del);
            // A pending multi-tap character is not in the buffer yet.
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.pending, "C");
            mv.visitJumpInsn(IFLE, delBuf);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitInsn(ICONST_0);
            mv.visitFieldInsn(PUTFIELD, owner, town.pending, "C");
            mv.visitInsn(RETURN);
            mv.visitLabel(delBuf);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.buffer, "Ljava/lang/StringBuffer;");
            mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuffer", "length", "()I");
            mv.visitJumpInsn(IFLE, delDone);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.buffer, "Ljava/lang/StringBuffer;");
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.buffer, "Ljava/lang/StringBuffer;");
            mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuffer", "length", "()I");
            mv.visitInsn(ICONST_1);
            mv.visitInsn(ISUB);
            mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuffer", "deleteCharAt",
                    "(I)Ljava/lang/StringBuffer;");
            mv.visitInsn(POP);
            mv.visitLabel(delDone);
            mv.visitInsn(RETURN);
            mv.visitLabel(notDel);
            mv.visitVarInsn(ILOAD, 1);
            mv.visitIntInsn(BIPUSH, 32);
            mv.visitJumpInsn(IF_ICMPLT, notChar);
            mv.visitVarInsn(ILOAD, 1);
            mv.visitIntInsn(BIPUSH, 126);
            mv.visitJumpInsn(IF_ICMPGT, notChar);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.pending, "C");
            mv.visitJumpInsn(IFLE, noPend);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.buffer, "Ljava/lang/StringBuffer;");
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.pending, "C");
            mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuffer", "append",
                    "(C)Ljava/lang/StringBuffer;");
            mv.visitInsn(POP);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitInsn(ICONST_0);
            mv.visitFieldInsn(PUTFIELD, owner, town.pending, "C");
            mv.visitLabel(noPend);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.buffer, "Ljava/lang/StringBuffer;");
            mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuffer", "length", "()I");
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.max, "I");
            mv.visitJumpInsn(IF_ICMPGE, typed);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, town.buffer, "Ljava/lang/StringBuffer;");
            mv.visitVarInsn(ILOAD, 1);
            mv.visitInsn(I2C);
            mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuffer", "append",
                    "(C)Ljava/lang/StringBuffer;");
            mv.visitInsn(POP);
            mv.visitLabel(typed);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitInsn(ICONST_0);
            mv.visitFieldInsn(PUTFIELD, owner, town.last, "I");
            mv.visitVarInsn(ALOAD, 0);
            mv.visitInsn(ICONST_0);
            mv.visitFieldInsn(PUTFIELD, owner, town.timer, "I");
            mv.visitInsn(RETURN);
            mv.visitLabel(notChar);
            mv.visitVarInsn(ILOAD, 1);
            mv.visitIntInsn(BIPUSH, -7);
            mv.visitJumpInsn(IF_ICMPNE, original);
            mv.visitInsn(RETURN);
            mv.visitLabel(original);
        }
    }

    /**
     * On a nickname or password screen, Escape takes the same exit the left
     * soft key already uses. Everywhere else it stays the back key.
     */
    static final class TownEscape extends MethodAdapter {
        final String owner;
        final String screen;

        TownEscape(MethodVisitor mv, String owner, String screen) {
            super(mv);
            this.owner = owner;
            this.screen = screen;
        }

        public void visitCode() {
            super.visitCode();
            Label skip = new Label();
            Label set = new Label();
            Label back70 = new Label();
            Label back79 = new Label();
            mv.visitVarInsn(ILOAD, 1);
            mv.visitIntInsn(BIPUSH, -7);
            mv.visitJumpInsn(IF_ICMPNE, skip);
            mv.visitVarInsn(ALOAD, 0);
            mv.visitFieldInsn(GETFIELD, owner, "Y", "I");
            mv.visitVarInsn(ISTORE, 2);
            for (int id : TEXT_SCREENS) {
                mv.visitVarInsn(ILOAD, 2);
                mv.visitIntInsn(BIPUSH, id);
                mv.visitJumpInsn(IF_ICMPEQ, set);
            }
            mv.visitVarInsn(ILOAD, 2);
            mv.visitIntInsn(BIPUSH, 71);
            mv.visitJumpInsn(IF_ICMPEQ, back70);
            mv.visitVarInsn(ILOAD, 2);
            mv.visitIntInsn(BIPUSH, 73);
            mv.visitJumpInsn(IF_ICMPEQ, back70);
            mv.visitVarInsn(ILOAD, 2);
            mv.visitIntInsn(BIPUSH, 80);
            mv.visitJumpInsn(IF_ICMPEQ, back79);
            mv.visitJumpInsn(GOTO, skip);
            mv.visitLabel(set);
            mv.visitIntInsn(BIPUSH, -6);
            mv.visitVarInsn(ISTORE, 1);
            mv.visitJumpInsn(GOTO, skip);
            mv.visitLabel(back70);
            leave(70);
            mv.visitLabel(back79);
            leave(79);
            mv.visitLabel(skip);
        }

        void leave(int id) {
            mv.visitVarInsn(ALOAD, 0);
            mv.visitIntInsn(BIPUSH, id);
            mv.visitMethodInsn(INVOKEVIRTUAL, owner, screen, "(I)V");
            mv.visitInsn(RETURN);
        }
    }

    public static int patchJar(File jar) throws Exception {
        File tmp = new File(jar.getParentFile(), jar.getName() + ".kbd-tmp");
        int n = 0;
        List<String> names = new ArrayList<String>();
        ZipFile in = new ZipFile(jar);
        try {
            ZipOutputStream out = new ZipOutputStream(new FileOutputStream(tmp));
            try {
                Enumeration<? extends ZipEntry> entries = in.entries();
                while (entries.hasMoreElements()) {
                    ZipEntry e = entries.nextElement();
                    byte[] data = read(in.getInputStream(e));
                    byte[] patched = null;
                    if (e.getName().endsWith(".class")) {
                        try {
                            patched = patch(data);
                        } catch (RuntimeException ex) {
                            throw new RuntimeException(e.getName() + ": " + ex.getMessage(), ex);
                        }
                    }
                    ZipEntry w = new ZipEntry(e.getName());
                    w.setTime(e.getTime());
                    out.putNextEntry(w);
                    out.write(patched != null ? patched : data);
                    out.closeEntry();
                    if (patched != null) {
                        n++;
                        names.add(e.getName());
                    }
                }
            } finally {
                out.close();
            }
        } finally {
            in.close();
        }
        if (n == 0) {
            tmp.delete();
            throw new IllegalStateException("no text form in " + jar);
        }
        if (!tmp.renameTo(jar)) {
            // Windows-style replace, and a same-directory rename that lost the race.
            copy(tmp, jar);
            tmp.delete();
        }
        System.out.println("keyboard " + jar.getName() + ": " + names);
        return n;
    }

    static byte[] read(InputStream in) throws Exception {
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        byte[] b = new byte[8192];
        int k;
        while ((k = in.read(b)) >= 0) {
            buf.write(b, 0, k);
        }
        in.close();
        return buf.toByteArray();
    }

    static void copy(File from, File to) throws Exception {
        InputStream in = new java.io.FileInputStream(from);
        try {
            FileOutputStream out = new FileOutputStream(to);
            try {
                byte[] b = new byte[8192];
                int k;
                while ((k = in.read(b)) >= 0) {
                    out.write(b, 0, k);
                }
            } finally {
                out.close();
            }
        } finally {
            in.close();
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length == 3 && "--class".equals(args[0])) {
            byte[] in = read(new java.io.FileInputStream(args[1]));
            byte[] out = patch(in);
            if (out == null) {
                throw new IllegalStateException("not a text form: " + args[1]);
            }
            FileOutputStream w = new FileOutputStream(args[2]);
            try {
                w.write(out);
            } finally {
                w.close();
            }
            System.out.println("keyboard class " + args[2]);
            return;
        }
        if (args.length != 1) {
            System.err.println("usage: KeyboardPatch JAR");
            System.exit(2);
        }
        int n = patchJar(new File(args[0]));
        if (n < 1) {
            System.exit(1);
        }
    }
}
