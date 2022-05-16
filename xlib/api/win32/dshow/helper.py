from typing import List
from .. import ole32, uuids, strmif, wintypes, objidl, oaidl



def get_video_input_devices_names() -> List[str]:
    """
    returns a list of available names of VideoInputDevice's

    ole32 should be initialized before use
    """
    # based on https://docs.microsoft.com/ru-ru/windows/win32/directshow/selecting-a-capture-device

    names = []
    sys_dev_enum = strmif.ICreateDevEnum()
    if ole32.CoCreateInstance(uuids.CLSID_SystemDeviceEnum, None, ole32.CLSCTX.CLSCTX_INPROC_SERVER, strmif.ICreateDevEnum.IID, sys_dev_enum) == wintypes.ERROR.SUCCESS:
        pEnumCat = objidl.IEnumMoniker()

        if sys_dev_enum.CreateClassEnumerator(uuids.CLSID_VideoInputDeviceCategory, pEnumCat, 0) == wintypes.ERROR.SUCCESS:

            moniker = objidl.IMoniker()
            while pEnumCat.Next(1, moniker, None) == wintypes.ERROR.SUCCESS:
                name = 'unnamed'

                prop_bag = oaidl.IPropertyBag()
                if moniker.BindToStorage(None, None, oaidl.IPropertyBag.IID, prop_bag) == wintypes.ERROR.SUCCESS:
                    var = wintypes.VARIANT()

                    hr = prop_bag.Read(wintypes.LPCOLESTR('Description'), var, None )
                    if hr != wintypes.ERROR.SUCCESS:
                        hr = prop_bag.Read(wintypes.LPCOLESTR('FriendlyName'), var, None )
                    if hr == wintypes.ERROR.SUCCESS:
                        name = var.value.bstrVal.value
                    prop_bag.Release()
                names.append(name)

                moniker.Release()
            pEnumCat.Release()
        sys_dev_enum.Release()

    return names