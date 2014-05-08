import ctypes

class _MODULE:
    def __init__(self, path):
        self.module = ctypes.windll.LoadLibrary(path)
        self.SFileOpenArchive    = self.module[266]
        self.SFileCloseArchive   = self.module[252]
        self.SFileFileExists     = self.module[288]
        self.SFileLoadFile       = self.module[279]
        self.SFileUnloadFile     = self.module[280]
        self.SFileDestroy        = self.module[262]
        self.SFileDestroy()

    def OpenArchive(self, path, priority = 0, flags = 0):
        hMpq = ctypes.c_ulong()
        if (self.SFileOpenArchive(path, priority, flags, ctypes.byref(hMpq))):
            return hMpq.value
        else:
            return None
    
    def CloseArchive(self, hArchive):
        self.SFileCloseArchive(hArchive)

    def LoadFile(self, path, mode = 0):
        pBuf  = ctypes.c_void_p()
        nSize = ctypes.c_ulong()
        if (self.SFileLoadFile(path, ctypes.byref(pBuf), ctypes.byref(nSize), 0, mode)):
            data = ctypes.cast(pBuf, ctypes.POINTER(ctypes.c_ubyte * nSize.value))
            byteData = ''.join(map(chr, data.contents))
            return byteData, nSize.value
        else:
            return None, None
    
    def UnloadFile(self, buf):
        self.SFileUnloadFile(buf)
        
    def FileExists(self, path):
        return self.SFileFileExists(path)

class _BUFFER:
    def __init__(self, data, size, release_proc):
        self.__release_proc = release_proc
        self.data  = data
        self.size  = size
        
    def __del__(self):
        self.__release_proc(self.data)
        
class _STORM:
    def __init__(self, path):
        self.__archives = []
        self.__mod = _MODULE(path)
        
    def __del__(self):
        for k in self.__archives:
            self.__mod.CloseArchive(k)

    def OpenArchive(self, path, priority = 0, flags = 0):
        hMpq = self.__mod.OpenArchive(path, priority, flags)
        if hMpq is not None:
            self.__archives.append(hMpq)
            return True
        else:
            return False
        
    def LoadFile(self, path, mode = 0):
        buf, size = self.__mod.LoadFile(path, mode)
        if (buf is not None) and (size is not None):
	    return _BUFFER(buf, size, self.__mod.UnloadFile)
	else:
	    return None
        
    def FileExists(self, path):
        return self.__mod.FileExists(path)

def Open(path):
    return _STORM(path)




