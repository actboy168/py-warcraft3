import Image
import ImageFile
import struct

'''
const int MAX_NR_OF_BLP_MIP_MAPS = 16;

struct BLP_HEADER
{
    uint32_t MagicNumber;
    uint32_t Compression;
    uint32_t Flags;
    uint32_t Width;
    uint32_t Height;
    uint32_t PictureType;
    uint32_t PictureSubType;
    uint32_t Offset[MAX_NR_OF_BLP_MIP_MAPS];
    uint32_t Size[MAX_NR_OF_BLP_MIP_MAPS];
};
'''

_BLP1 = 0x31504C42
_BLP_HEADER_SIZE = 156
_BLP_PALETTE_SIZE = 1024

def ReadUInt32(data, offset):
    return struct.unpack('<I', data[offset:offset+4])[0]

def MipMap(data, index):
    return ReadUInt32(data, 28+index*4), ReadUInt32(data, 92+index*4)

def LoadCompressed(data):
    JpegHeaderSize = ReadUInt32(data, _BLP_HEADER_SIZE)
    Offset, Size = MipMap(data, 0)
    parser = ImageFile.Parser()
    parser.feed(data[_BLP_HEADER_SIZE+4:_BLP_HEADER_SIZE+4+JpegHeaderSize])
    parser.feed(data[Offset:Offset+Size])
    img = parser.close().convert('RGB')
    r, g, b = img.split()
    return Image.merge("RGB", (b, g, r))

def LoadUncompressed(Width, Height, PictureType, data):
    palette = data[_BLP_HEADER_SIZE:_BLP_HEADER_SIZE+_BLP_PALETTE_SIZE]
    data    = data[_BLP_HEADER_SIZE+_BLP_PALETTE_SIZE:]
    size    = Width * Height
    pixel   = ""

    if PictureType == 3 or PictureType == 4:
        for index in range(0, size):
            p = 4 * ord(data[index])
            pixel += palette[p+2]
            pixel += palette[p+1]
            pixel += palette[p+0]
            pixel += data[size+index] # alpha
    elif PictureType == 5:
        for index in range(0, size):
            p = 4 * ord(data[index])
            pixel += palette[p+2]
            pixel += palette[p+1]
            pixel += palette[p+0]
            pixel += chr(0xFF - ord(palette[p+3])) # alpha
    else:
        return None

    return Image.fromstring("RGB", (Width, Height), pixel, "raw", "RGBX", 0, 1)


def Reader(data):
    if (len(data) < _BLP_HEADER_SIZE):
        return None

    MagicNumber, Compression, _, Width, Height, PictureType, _ = struct.unpack('<7I', data[0:28])

    if (_BLP1 != MagicNumber):
        return None

    if (Compression == 0):
        return LoadCompressed(data)
    elif (Compression == 1):
        return LoadUncompressed(Width, Height, PictureType, data)
    else:
        return None

def Convert(src, dst):
    try:
        img = Reader(open(src, 'rb').read())
        if img is not None:
            img.save(dst)
            return True
    except:
        pass
    return False
