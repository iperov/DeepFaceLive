from ctypes import POINTER, c_void_p
from ..wintypes import (GUID, DWORD, IUnknown, CLSID, interface, HRESULT, REFIID, BOOL, ULARGE_INTEGER)

@interface
class IStream(IUnknown):  #ISequentialStream
    IID = GUID('0000000c-0000-0000-c000-000000000046')


@interface
class IPersist(IUnknown):
    def GetClassID(self, pClassID : POINTER(CLSID) ) -> HRESULT: ...
    IID = GUID('0000010c-0000-0000-c000-000000000046')

@interface
class IPersistStream(IPersist):
    def IsDirty(self) -> HRESULT: ...
    def Load(self, pStm : IStream) -> HRESULT: ...
    def Save(self, pStm : IStream, fClearDirty : BOOL) -> HRESULT: ...
    def GetSizeMax(self, pcbSize : POINTER(ULARGE_INTEGER) ) -> HRESULT: ...
    IID = GUID('00000109-0000-0000-c000-000000000046')

@interface
class IMoniker(IPersistStream):

    def BindToObject(self,
        pbc : c_void_p, #IBindCtx
        pmkToLeft : IUnknown, #IMoniker,
        riidResult : REFIID,
        ppvResult : POINTER(c_void_p))  -> HRESULT: ...

    def BindToStorage(self,
        pbc : c_void_p, #IBindCtx
        pmkToLeft : IUnknown, #IMoniker,
        riid : REFIID,
        ppvObj : POINTER(c_void_p))  -> HRESULT: ...

    # virtual HRESULT STDMETHODCALLTYPE Reduce(
    #     IBindCtx *pbc,
    #     DWORD dwReduceHowFar,
    #     IMoniker **ppmkToLeft,
    #     IMoniker **ppmkReduced) = 0;

    # virtual HRESULT STDMETHODCALLTYPE ComposeWith(
    #     IMoniker *pmkRight,
    #     WINBOOL fOnlyIfNotGeneric,
    #     IMoniker **ppmkComposite) = 0;

    # virtual HRESULT STDMETHODCALLTYPE Enum(
    #     WINBOOL fForward,
    #     IEnumMoniker **ppenumMoniker) = 0;

    # virtual HRESULT STDMETHODCALLTYPE IsEqual(
    #     IMoniker *pmkOtherMoniker) = 0;

    # virtual HRESULT STDMETHODCALLTYPE Hash(
    #     DWORD *pdwHash) = 0;

    # virtual HRESULT STDMETHODCALLTYPE IsRunning(
    #     IBindCtx *pbc,
    #     IMoniker *pmkToLeft,
    #     IMoniker *pmkNewlyRunning) = 0;

    # virtual HRESULT STDMETHODCALLTYPE GetTimeOfLastChange(
    #     IBindCtx *pbc,
    #     IMoniker *pmkToLeft,
    #     FILETIME *pFileTime) = 0;

    # virtual HRESULT STDMETHODCALLTYPE Inverse(
    #     IMoniker **ppmk) = 0;

    # virtual HRESULT STDMETHODCALLTYPE CommonPrefixWith(
    #     IMoniker *pmkOther,
    #     IMoniker **ppmkPrefix) = 0;

    # virtual HRESULT STDMETHODCALLTYPE RelativePathTo(
    #     IMoniker *pmkOther,
    #     IMoniker **ppmkRelPath) = 0;

    # virtual HRESULT STDMETHODCALLTYPE GetDisplayName(
    #     IBindCtx *pbc,
    #     IMoniker *pmkToLeft,
    #     LPOLESTR *ppszDisplayName) = 0;

    # virtual HRESULT STDMETHODCALLTYPE ParseDisplayName(
    #     IBindCtx *pbc,
    #     IMoniker *pmkToLeft,
    #     LPOLESTR pszDisplayName,
    #     ULONG *pchEaten,
    #     IMoniker **ppmkOut) = 0;

    # virtual HRESULT STDMETHODCALLTYPE IsSystemMoniker(
    #     DWORD *pdwMksys) = 0;

    IID = GUID('0000000f-0000-0000-c000-000000000046')


@interface
class IEnumMoniker(IUnknown):
    #def CreateClassEnumerator(refiid : REFIID, enumMoniker : POINTER(IEnumMoniker), flags : DWORD ) -> HRESULT: ...

    def Next(self, celt : DWORD, rgelt : POINTER(IMoniker), pceltFetched : POINTER(DWORD)) -> HRESULT: ...

    #virtual HRESULT STDMETHODCALLTYPE Skip(ULONG celt) = 0;
    #virtual HRESULT STDMETHODCALLTYPE Reset() = 0;
    #virtual HRESULT STDMETHODCALLTYPE Clone(IEnumMoniker **ppenum) = 0;

    IID = GUID('00000102-0000-0000-C000-000000000046')
