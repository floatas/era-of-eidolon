#!/usr/bin/env python3
"""Repack a MIDlet with extra manifest attributes.

FreeJ2ME reads app properties from META-INF/MANIFEST.MF only — it never parses
the .jad — so the `Relay` property has to live in the manifest. Everything else
in the jar is copied byte-for-byte; originals in ../jars/ are never touched.

    python3 mkjar.py ../jars/EoE-ShiradsForge.jar EoE-ShiradsForge.jar \
        Relay=http://127.0.0.1:8080/ INFO=preservation
"""

import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "server"))
from layout import TYPE2, TURNS, rewrite_type2  # noqa: E402
from layout import rewrite_strings as rewrite_texts, text_patches  # noqa: E402
from tiers import RECYCLE_PERCENT  # noqa: E402

MANIFEST = "META-INF/MANIFEST.MF"

# The item screen's button is also the word the phone compares, so the label
# and the check have to change together. "Delete hero" is a different string
# and stays. The confirmation is the item one only.
TEXT_FIXES = {
    "Delete": "Recycle",
    "Are you sure you want to delete this?\nAction can not be undone!":
        f"Recycle this?\nYou get {RECYCLE_PERCENT}% of its price back.",
}


def _skip_pool(data):
    if len(data) < 10 or data[:4] != b"\xca\xfe\xba\xbe":
        return None
    count = int.from_bytes(data[8:10], "big")
    pos = 10
    index = 1
    while index < count:
        tag = data[pos]
        if tag == 1:
            length = int.from_bytes(data[pos + 1:pos + 3], "big")
            pos += 3 + length
            index += 1
        elif tag in (7, 8, 16, 19, 20):
            pos += 3
            index += 1
        elif tag == 15:
            pos += 4
            index += 1
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            pos += 5
            index += 1
        elif tag in (5, 6):
            pos += 9
            index += 2
        else:
            return None
    return pos


def _utf8_at(data, index):
    """Constant-pool Utf8 by 1-based index. None if the pool cannot be read."""
    count = int.from_bytes(data[8:10], "big")
    pos = 10
    i = 1
    while i < count:
        tag = data[pos]
        if tag == 1:
            length = int.from_bytes(data[pos + 1:pos + 3], "big")
            raw = data[pos + 3:pos + 3 + length]
            if i == index:
                return raw.decode("utf-8", "replace")
            pos += 3 + length
            i += 1
        elif tag in (7, 8, 16, 19, 20):
            pos += 3
            i += 1
        elif tag == 15:
            pos += 4
            i += 1
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            pos += 5
            i += 1
        elif tag in (5, 6):
            pos += 9
            i += 2
        else:
            return None
    return None


def ping_map_loads(data):
    """Tell the server the room every time a map finishes loading.

    k() only writes home when art is missing. A map already in the jar
    changes on the phone and the companion never hears. The fast path, just
    before it returns, now sends opcode 31 with the same location block a
    fight would. The request is not stored in field p, so the loader does
    not wait and does not call itself again.
    """
    pool_end = _skip_pool(data)
    if pool_end is None:
        return data
    pos = pool_end
    pos += 2 + 2 + 2  # access, this, super
    interfaces = int.from_bytes(data[pos:pos + 2], "big")
    pos += 2 + interfaces * 2
    fields = int.from_bytes(data[pos:pos + 2], "big")
    pos += 2
    for _ in range(fields):
        pos += 6
        attrs = int.from_bytes(data[pos:pos + 2], "big")
        pos += 2
        for _a in range(attrs):
            alen = int.from_bytes(data[pos + 2:pos + 6], "big")
            pos += 6 + alen
    methods = int.from_bytes(data[pos:pos + 2], "big")
    pos += 2
    for _ in range(methods):
        name = _utf8_at(data, int.from_bytes(data[pos + 2:pos + 4], "big"))
        desc = _utf8_at(data, int.from_bytes(data[pos + 4:pos + 6], "big"))
        pos += 6
        attr_count_at = pos
        attrs = int.from_bytes(data[pos:pos + 2], "big")
        pos += 2
        if name != "k" or desc != "()V":
            for _a in range(attrs):
                alen = int.from_bytes(data[pos + 2:pos + 6], "big")
                pos += 6 + alen
            continue
        for _a in range(attrs):
            aname = _utf8_at(data, int.from_bytes(data[pos:pos + 2], "big"))
            alen = int.from_bytes(data[pos + 2:pos + 6], "big")
            body = data[pos + 6:pos + 6 + alen]
            if aname != "Code":
                pos += 6 + alen
                continue
            max_stack = int.from_bytes(body[0:2], "big")
            code_len = int.from_bytes(body[4:8], "big")
            code = bytearray(body[8:8 + code_len])
            # aload_0 is 0x2A. The loader already builds
            # new b; dup; bipush 10; aload_0; invokespecial.
            mark = bytes([0x59, 0x10, 0x0A, 0x2A, 0xB7])
            at = code.find(mark)
            if at < 3 or code[at - 3] != 0xBB or code[-1] != 0xB1:
                return data
            new_idx = code[at - 2:at]
            init_idx = code[at + 5:at + 7]
            # After that constructor the method calls d(Lb) then g.a(Le, Lb).
            # d's invokevirtual is the one whose bytes match the later call
            # on field p: aload_0, aload_0, getfield, invokevirtual.
            call = code.find(bytes([0x2A, 0x2A, 0xB4]), at)
            if call < 0:
                return data
            d_idx = code[call + 6:call + 8]
            # getfield w is the next getfield after that d() call.
            wf = code.find(bytes([0xB4]), call + 8)
            if wf < 0:
                return data
            w_idx = code[wf + 1:wf + 3]
            send = code.find(bytes([0xB6]), wf)
            if send < 0:
                return data
            send_idx = code[send + 1:send + 3]
            # Same request as a fight's location block, opcode 31, and not
            # stored in field p. Local 1 is the resource list, dead by now.
            ping = bytes([
                0x2A,                          # aload_0
                0xBB, new_idx[0], new_idx[1],  # new b
                0x59,                          # dup
                0x10, 31,                      # bipush 31
                0x2A,                          # aload_0
                0xB7, init_idx[0], init_idx[1],
                0x4C,                          # astore_1
                0x2A, 0x2B,                    # aload_0, aload_1
                0xB6, d_idx[0], d_idx[1],      # d(Lb)  tag 11 = the room
                0x2A,                          # aload_0
                0xB4, w_idx[0], w_idx[1],      # getfield w
                0x2A, 0x2B,                    # aload_0, aload_1
                0xB6, send_idx[0], send_idx[1],
            ])
            code = code[:-1] + bytearray(ping) + bytes([0xB1])
            if max_stack < 4:
                body = (4).to_bytes(2, "big") + body[2:]
            new_body = (body[:4] + len(code).to_bytes(4, "big") + bytes(code)
                        + body[8 + code_len:])
            new_attr = (data[pos:pos + 2] + len(new_body).to_bytes(4, "big")
                        + new_body)
            return data[:pos] + new_attr + data[pos + 6 + alen:]
        return data
    return data


def rewrite_strings(data, mapping):
    """Replace exact Java Utf8 constants. Indices stay put, so longer text is safe."""
    if len(data) < 10 or data[:4] != b"\xca\xfe\xba\xbe":
        return data
    count = int.from_bytes(data[8:10], "big")
    pos = 10
    out = [data[:10]]
    index = 1
    changed = False
    while index < count:
        tag = data[pos]
        if tag == 1:
            length = int.from_bytes(data[pos + 1:pos + 3], "big")
            raw = data[pos + 3:pos + 3 + length]
            pos += 3 + length
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = None
            if text in mapping:
                raw = mapping[text].encode("utf-8")
                changed = True
            out.append(b"\x01" + len(raw).to_bytes(2, "big") + raw)
            index += 1
        elif tag in (7, 8, 16, 19, 20):
            out.append(data[pos:pos + 3])
            pos += 3
            index += 1
        elif tag in (15,):
            out.append(data[pos:pos + 4])
            pos += 4
            index += 1
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            out.append(data[pos:pos + 5])
            pos += 5
            index += 1
        elif tag in (5, 6):
            out.append(data[pos:pos + 9])
            pos += 9
            index += 2
        else:
            return data
    if not changed:
        return data
    return b"".join(out) + data[pos:]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    src, dst, kvs = sys.argv[1], sys.argv[2], sys.argv[3:]
    extra = dict(kv.split("=", 1) for kv in kvs)

    with zipfile.ZipFile(src) as zin:
        names = zin.namelist()
        if MANIFEST not in names:
            print(f"no {MANIFEST} in {src}")
            return 1
        mf = zin.read(MANIFEST).decode("utf-8", "replace")

        # drop any existing copies of the keys we are setting, keep the rest
        keep = [ln for ln in mf.splitlines()
                if ln.strip() and ln.split(":", 1)[0].strip() not in extra]
        for k, v in extra.items():
            keep.append(f"{k}: {v}")
        new_mf = "\r\n".join(keep) + "\r\n\r\n"

        forge = "ShiradsForge" in os.path.basename(src)
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                data = new_mf.encode("utf-8") if n == MANIFEST else zin.read(n)
                if forge and n in text_patches():
                    data = rewrite_texts(data, text_patches()[n])
                if forge and n in TYPE2.values():
                    loc = next(k for k, v in TYPE2.items() if v == n)
                    data, _ = rewrite_type2(data, TURNS[loc], bridge=(loc == 12))
                if n.endswith(".class"):
                    data = rewrite_strings(data, TEXT_FIXES)
                if n == "d.class":
                    data = ping_map_loads(data)
                zout.writestr(zin.getinfo(n), data)

    print(f"{dst}: set " + ", ".join(f"{k}={v}" for k, v in extra.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
