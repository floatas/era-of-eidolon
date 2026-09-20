/*
 * Decompiled with CFR 0.152.
 */
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

    public f(String string, Object object) {
        this.a = string;
        this.k = object;
    }

    public f(String string, String string2, int n) {
        this.a = string;
        this.d = string2 == null ? new StringBuffer() : new StringBuffer(string2);
        this.e = n;
    }

    public f(String string) {
        this.a = string;
    }

    public f(DataInputStream dataInputStream) throws IOException {
        this.a = b.a(dataInputStream, dataInputStream.readUnsignedByte());
        if (this.a == null) {
            this.a = "";
        }
        this.b = b.a(dataInputStream, dataInputStream.readUnsignedByte());
        this.f = dataInputStream.readByte();
        this.g = dataInputStream.readUnsignedByte();
        this.c = b.a(dataInputStream, dataInputStream.readUnsignedByte());
        int n = dataInputStream.readUnsignedShort();
        if (n > 0) {
            this.k = new byte[n];
            dataInputStream.readFully((byte[])this.k);
        }
    }

    public f(String string, Object[][] objectArray) {
        this.a = string;
        this.i = objectArray;
    }

    public final int a() {
        this.h = this.f >= 0 ? 15 + f.a(this.a, true) : (this.e != 0 ? 5 + Math.max(f.a(this.a, true), f.a(this.d.toString(), true)) : (this.i != null ? 5 + Math.max(this.j >= 0 ? f.a(this.i[this.j][0].toString(), true) : 0, f.a(this.a, true)) : f.a(this.a, true)));
        if (this.c != null) {
            this.h = Math.max(this.h, f.a(this.c, true));
        }
        return this.h;
    }

    public static final int a(String string, boolean bl) {
        int n = 0;
        int n2 = 0;
        int n3 = 0;
        char c2 = '\u0000';
        while (n3 < string.length()) {
            while (n3 < string.length() && (c2 = string.charAt(n3)) > '\u000b') {
                ++n3;
            }
            n += e.r.substringWidth(string, n2, n3 - n2);
            n2 = n3;
            switch (c2) {
                case '\u000b': {
                    n += 10;
                    n2 = n3 += 2;
                    c2 = '\u0000';
                    break;
                }
                case '\u0004': {
                    if (bl) {
                        n += 6;
                    }
                }
                case '\u0001': 
                case '\u0002': 
                case '\u0003': 
                case '\u0007': {
                    n2 = ++n3;
                    break;
                }
                case '\u0006': {
                    n2 = n3 += 4;
                }
            }
        }
        return n;
    }

    public final String b() {
        if (this.b == null) {
            return this.a;
        }
        return this.b;
    }

    public final boolean c() {
        return (this.g & 8) != 0;
    }

    public final String d() {
        if (this.k == null) {
            return null;
        }
        return b.a((byte[])this.k, 0, ((byte[])this.k).length);
    }
}

