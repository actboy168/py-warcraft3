import struct

def _GetString(str, beg):
    offset = str.find('\0', beg) + 1
    return offset, str[beg:offset]

class _W3IMP:
    def __init__(self, buf):
        self.__files = []
        self.Load(buf)
        
    def Load(self, buf):
        self.__v, self.__n = struct.unpack('<LL', buf[:8])
        offset = 8
        for i in range(0, self.__n):
            file_type = struct.unpack('<B', buf[offset:offset+1])
            offset = offset + 1
            offset, file_name = _GetString(buf, offset)
            self.__files.append([file_type, file_name])
            
    def Save(self, buf):
        buf = ''
        self.__n = len(self.__files)
        buf += struct.pack('<LL', self.__v, self.__n)
        for k in self.__files:
            print str(k[0]) + ' ' + k[1]
            buf += struct.pack('<B', k[0])
            buf += k[1]
            
    def Add(self, file_type, file_name):
        self.__files.append([file_type, file_name])
            
buf = open('war3map.imp', 'rb').read()
print buf
war3map_imp = _W3IMP(buf)

