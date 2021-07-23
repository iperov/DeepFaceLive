import io
import threading
import urllib.request
from pathlib import Path
from typing import Union


class ThreadFileDownloader:
    """
    FileDownloader using sub thread

     url            str

     savepath(None) str,Path


    Use .get_error() to check the error
    """

    def __init__(self, url, savepath : Union[str, Path] = None):
        if savepath is not None:
            savepath = Path(savepath)
            self._partpath = savepath.parent / ( savepath.name + '.part' )
        else:
            self._partpath = None
        self._savepath = savepath

        self._url = url
        self._error = None
        self._file_size = None
        self._file_size_dl = None
        self._bytes = None

        threading.Thread(target=self._thread, daemon=True).start()


    def get_progress(self) -> float:
        """
        return progress of downloading as [0.0...100.0] value
        where 100.0 mean download is completed
        """
        if self._file_size is None or self._file_size_dl is None:
            return 0.0

        return (self._file_size_dl / self._file_size) * 100.0

    def get_bytes(self) -> bytes:
        """
        return bytes of downloaded file if savepath is not defined
        """
        return self._bytes

    def get_error(self) -> Union[str, None]:
        """
        returns error string or None if no error
        """
        return self._error

    def _thread(self):
        try:
            url_req = urllib.request.urlopen(self._url)
            file_size = self._file_size = int( url_req.getheader('content-length') )
            self._file_size_dl = 0
            savepath = self._savepath
            partpath = self._partpath

            if partpath is not None:
                if partpath.exists():
                    partpath.unlink()
                f = open(partpath, 'wb')
            else:
                f = io.BytesIO()

            while url_req is not None:
                buffer = url_req.read(8192)
                if not buffer:
                    break

                f.write(buffer)

                new_file_size_dl = self._file_size_dl + len(buffer)

                if new_file_size_dl >= file_size:
                    if partpath is not None:
                        f.close()
                        if savepath.exists():
                            savepath.unlink()
                        partpath.rename(savepath)
                    else:
                        self._bytes = f.getvalue()
                        f.close()
                    url_req.close()
                    url_req = None

                self._file_size_dl = new_file_size_dl


        except Exception as e:
            self._error = str(e)
