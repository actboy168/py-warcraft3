# -*- coding: cp936 -*-

import ctypes

# MpqOpenArchiveForUpdate flags
MOAU_CREATE_NEW          = 0x00 #If archive does not exist, it will be created. If it exists, the function will fail
MOAU_CREATE_ALWAYS       = 0x08 #Will always create a new archive
MOAU_OPEN_EXISTING       = 0x04 #If archive exists, it will be opened. If it does not exist, the function will fail
MOAU_OPEN_ALWAYS         = 0x20 #If archive exists, it will be opened. If it does not exist, it will be created
MOAU_READ_ONLY           = 0x10 #Must be used with MOAU_OPEN_EXISTING. Archive will be opened without write access
MOAU_MAINTAIN_ATTRIBUTES = 0x02 #Will be used in a future version to create the (attributes) file
MOAU_MAINTAIN_LISTFILE   = 0x01 #Creates and maintains a list of files in archive when they are added, replaced, or deleted

# MpqAddFileToArchive flags
MAFA_EXISTS              = 0x80000000 #This flag will be added if not present
MAFA_UNKNOWN40000000     = 0x40000000 #Unknown flag
MAFA_MODCRYPTKEY         = 0x00020000 #Used with MAFA_ENCRYPT. Uses an encryption key based on file position and size
MAFA_ENCRYPT             = 0x00010000 #Encrypts the file. The file is still accessible when using this, so the use of this has depreciated
MAFA_COMPRESS            = 0x00000200 #File is to be compressed when added. This is used for most of the compression methods
MAFA_COMPRESS2           = 0x00000100 #File is compressed with standard compression only (was used in Diablo 1)
MAFA_REPLACE_EXISTING    = 0x00000001 #If file already exists, it will be replaced

class _MODULE:
    def __init__(self, path):
        self.module = ctypes.windll.LoadLibrary(path)
        self.MpqOpenArchiveForUpdate = self.module.MpqOpenArchiveForUpdate
        self.MpqCloseUpdatedArchive  = self.module.MpqCloseUpdatedArchive
        self.MpqAddFileFromBuffer    = self.module.MpqAddFileFromBuffer
        self.MpqCompactArchive       = self.module.MpqCompactArchive
        self.MpqInitialize           = self.module.MpqInitialize
        self.MpqInitialize()

    def OpenArchive(self, path, flags = 0):
        return self.MpqOpenArchiveForUpdate(path, flags, 0)

    def CloseArchive(self, hArchive):
        return self.MpqCloseUpdatedArchive(hArchive, 0)

    def CompactArchive(self, hArchive):
        return self.MpqCompactArchive(hArchive, 0)

    def AddFileFromBuffer(self, hArchive, buf, filename, flags = 0):
        return self.MpqAddFileFromBuffer(hArchive, buf, len(buf), filename, flags)

class _ARCHIVE:
    def __init__(self, archive, mod):
        self.__archive = archive
        self.__mod     = mod
        
    def __del__(self):
        self.__mod.CompactArchive(self.__archive)
        self.__mod.CloseArchive(self.__archive)
        
    def AddFile(self, filename, buf, flags = 0):
        return self.__mod.AddFileFromBuffer(self.__archive, buf, filename, flags)
    
class _SFMPQ:
    def __init__(self, path):
        self.__archives = []
        self.__mod = _MODULE(path)
        
    def __del__(self):
        for k in self.__archives:
            del k
            
    def OpenArchive(self, path, flags = 0):
        hArchive = self.__mod.OpenArchive(path, flags)
        if hArchive != -1:
            archive = _ARCHIVE(hArchive, self.__mod)
            self.__archives.append(archive)
            return archive
        else:
            return None


def Open(path):
    return _SFMPQ(path)

sfmpq = Open('./sfmpq.dll')
archive = sfmpq.OpenArchive('综合——UI测试地图1.19.w3x', MOAU_OPEN_EXISTING)
print archive
if archive is not None:
    archive.AddFile('t.txt', '1234', MAFA_REPLACE_EXISTING | MAFA_COMPRESS)
del sfmpq

