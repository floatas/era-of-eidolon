"""Era of Eidolon gen-2 wire codec.

Derived from decompiled-vf/b.java (Vineflower) — see ../protocol/PROTOCOL.md.

Request  = bare concatenation of TLV chunks, no header, no count.
           Opcode lives in the URL path (<opcode>.pl).
Response = u16 magic(0xBABE), u8 status, u8 pad, i32 bytecount,
           u16 chunkcount, then that many TLV chunks.

TLV chunk = u8 tag, u8 type, u16 length, <length bytes>
Type 1 = int (length 1/2/4 -> byte/short/int, signed)
Type 2,3 = string (hand-rolled UTF-8, no BOM, no length prefix)
Type 4 = 'f' structure
Type 5 = resource push: u16 key, then payload; key>>8 = restype, key&0xFF = id
other = raw bytes
"""

import struct

MAGIC = 0xBABE

T_INT, T_STR, T_STR2, T_STRUCT, T_RES = 1, 2, 3, 4, 5


def enc_utf8(s):
    """The client's own encoder (b.java:448). Plain UTF-8 for the BMP."""
    out = bytearray()
    for ch in s:
        c = ord(ch)
        if c <= 0x7F:
            out.append(c)
        elif c <= 0x7FF:
            out += bytes([0xC0 | (c >> 6), 0x80 | (c & 0x3F)])
        else:
            out += bytes([0xE0 | (c >> 12), 0x80 | ((c >> 6) & 0x3F), 0x80 | (c & 0x3F)])
    return bytes(out)


def dec_utf8(b):
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("latin-1")


def parse_chunks(buf):
    """Parse a bare TLV stream. Returns [(tag, type, raw), ...]."""
    chunks, i, n = [], 0, len(buf)
    while i + 4 <= n:
        tag, typ = buf[i], buf[i + 1]
        ln = struct.unpack_from(">H", buf, i + 2)[0]
        i += 4
        if i + ln > n:
            chunks.append((tag, typ, buf[i:]))
            break
        chunks.append((tag, typ, buf[i:i + ln]))
        i += ln
    return chunks


def decode_value(typ, raw):
    """Best-effort human rendering of a chunk payload."""
    if typ == T_INT:
        if len(raw) == 1:
            return struct.unpack(">b", raw)[0]
        if len(raw) == 2:
            return struct.unpack(">h", raw)[0]
        if len(raw) == 4:
            return struct.unpack(">i", raw)[0]
        return int.from_bytes(raw, "big", signed=True)
    if typ in (T_STR, T_STR2):
        return dec_utf8(raw)
    if typ == T_RES and len(raw) >= 2:
        key = struct.unpack_from(">H", raw)[0]
        return f"<res type={key >> 8} id=0x{key & 0xFF:02x} {len(raw) - 2}B>"
    return raw


def fmt_chunks(chunks):
    out = []
    for tag, typ, raw in chunks:
        v = decode_value(typ, raw)
        if isinstance(v, bytes):
            v = v.hex() if len(v) <= 24 else v[:24].hex() + f"...({len(raw)}B)"
        elif isinstance(v, str):
            v = repr(v)
        out.append(f"    tag={tag:<3} type={typ} len={len(raw):<5} {v}")
    return "\n".join(out) if out else "    (no chunks)"


# ---------- response building ----------

def chunk_int(tag, value):
    if -128 <= value < 128:
        return bytes([tag, T_INT]) + struct.pack(">Hb", 1, value)
    if -32768 <= value < 32768:
        return bytes([tag, T_INT]) + struct.pack(">Hh", 2, value)
    return bytes([tag, T_INT]) + struct.pack(">Hi", 4, value)


def chunk_str(tag, value, typ=T_STR):
    b = enc_utf8(value)
    return bytes([tag, typ]) + struct.pack(">H", len(b)) + b


def chunk_raw(tag, typ, payload):
    return bytes([tag, typ]) + struct.pack(">H", len(payload)) + payload


def chunk_session(blob):
    """Tag 0 -> stored by the client as B and echoed on every later request."""
    return chunk_raw(0, 0, blob)


def build_response(status=1, chunks=(), bytecount=0):
    """status: client requires != 0, else it reports 'Second login detected!'"""
    body = b"".join(chunks)
    head = struct.pack(">HBBiH", MAGIC, status & 0xFF, 0, bytecount, len(chunks))
    return head + body
