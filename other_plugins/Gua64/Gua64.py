gua = (
    '䷁䷖䷇䷓䷏䷢䷬䷋'
    '䷎䷳䷦䷴䷽䷷䷞䷠'
    '䷆䷃䷜䷺䷧䷿䷮䷅'
    '䷭䷑䷯䷸䷟䷱䷛䷫'
    '䷗䷚䷂䷩䷲䷔䷐䷘'
    '䷣䷕䷾䷤䷶䷝䷰䷌'
    '䷒䷨䷻䷼䷵䷥䷹䷉'
    '䷊䷙䷄䷈䷡䷍䷪䷀'
)

from_bytes = int.from_bytes


def encode(s):
    """Encode the bytes-like object s using gua64 and return a bytes object.
    """
    encoded = bytearray()
    for i in range(0, len(s), 3):
        c = from_bytes(s[i: i + 3], 'big')
        if len(s[i: i + 3]) == 3:
            encoded += gua[c >> 18].encode()
            encoded += gua[(c >> 12) & 0x3f].encode()
            encoded += gua[(c >> 6) & 0x3f].encode()
            encoded += gua[c & 0x3f].encode()
            continue
        if len(s[i: i + 3]) == 2:
            encoded += gua[c >> 10].encode()
            encoded += gua[c >> 4 & 0x3f].encode()
            encoded += gua[(c & 0xf) << 2].encode()
            encoded += '☯'.encode()
            continue
        if len(s[i: i + 3]) == 1:
            encoded += gua[c >> 2].encode()
            encoded += gua[(c & 0x3) << 4].encode()
            encoded += '☯'.encode() * 2
    return bytes(encoded)


def decode(s):
    """Decode the bytes-like object s using gua64 and return a bytes object.
    """
    encoded = []
    gua64dict = {v: k for k, v in enumerate(gua)}
    for i in range(0, len(s), 3):
        if s[i: i + 3].decode() == '☯':
            encoded.append(0)
            continue
        encoded.append(gua64dict[s[i: i + 3].decode()])
    b = bytearray(encoded)
    encoded = []
    for i in range(0, len(b), 4):
        c = from_bytes(b[i: i + 4], 'big')
        if len(b[i: i + 4]) == 4:
            encoded.append(c >> 24 << 2 | (c >> 20 & 0x3))
            if (c >> 16 & 0xf) << 4 | (c >> 10 & 0xf) != 0:
                encoded.append((c >> 16 & 0xf) << 4 | (c >> 10 & 0xf))
            if (c >> 8 & 0x3) << 6 | (c & 0x3f) != 0:
                encoded.append((c >> 8 & 0x3) << 6 | (c & 0x3f))
    return bytes(encoded)


if __name__ == '__main__':
    r = encode('hello，世界'.encode())
    print(r.decode())

    r = decode('䷯䷬䷿䷶䷸䷬䷀䷌䷌䷎䷼䷲䷰䷳䷸䷘䷔䷭䷒☯'.encode())
    print(r.decode())
