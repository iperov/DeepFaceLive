import argparse
import os
import shutil
import ssl
import subprocess
import time
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List


class WindowsFolderBuilder:
    """
    Builds stand-alone portable all-in-one python folder for Windows with the project from scratch.
    """

    # Constants
    URL_PIP     = r'https://bootstrap.pypa.io/get-pip.py'
    URL_VSCODE  = r'https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-archive'
    URL_FFMPEG  = r'https://github.com/GyanD/codexffmpeg/releases/download/4.4/ffmpeg-4.4-full_build.zip'
    URL_7ZIP    = r'https://github.com/iperov/DeepFaceLive/releases/download/7za/7za.zip'
    URL_MSVC    = r'https://github.com/iperov/DeepFaceLive/releases/download/msvc/msvc.zip'

    URLS_PYTHON = {'3.7.9' : r'https://www.python.org/ftp/python/3.7.9/python-3.7.9-embed-amd64.zip',
                   '3.8.10' : r'https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip',
                   }

    DIRNAME_INTERNAL = '_internal'
    DIRNAME_INTERNAL_CUDA = 'CUDA'
    DIRNAME_INTERNAL_PYTHON = 'python'
    DIRNAME_INTERNAL_FFMPEG = 'ffmpeg'
    DIRNAME_LOCALENV = '_z'
    DIRNAME_TEMP = 't'
    DIRNAME_USERPROFILE = 'u'
    DIRNAME_APPDATA = 'AppData'
    DIRNAME_LOCAL = 'Local'
    DIRNAME_ROAMING = 'Roaming'
    DIRNAME_DESKTOP = 'Desktop'
    DIRNAME_INTERNAL_VSCODE = 'VSCode'

    def __init__(self,  release_path : Path,
                        cache_path : Path,
                        python_ver : str,
                        clear_release_path : bool = True,
                ):
        super().__init__()
        self.release_path = release_path
        self.python_ver = python_ver
        self.cache_path = cache_path
        self.download_cache_path = cache_path / '_dl_cache'
        self.pip_cache_path = cache_path / '_pip_cache'

        if clear_release_path:
            if release_path.exists():
                print('Removing existing directory.')
                shutil.rmtree(release_path)
            while release_path.exists():
                time.sleep(0.1)
            release_path.mkdir(parents=True)

        self._validate_env()
        self._install_internal()
        self._install_python()

    def copyfiletree(self, src, dst):
        shutil.copytree(src, dst)

    def copyfile(self, src, dst):
        shutil.copyfile(src, dst)

    def download_file(self, url, savepath : Path, progress_bar=True, use_cached=True):
        """
        Download the file or use cached and save to savepath
        """
        urlpath = Path(url)

        if progress_bar:
            print(f'Downloading {url}')

        f = None
        while True:
            try:
                url_request = urllib.request.urlopen(url, context=ssl._create_unverified_context())
                url_size = int( url_request.getheader('content-length') )

                if use_cached:
                    cached_filepath = self.download_cache_path / urlpath.name
                    if cached_filepath.exists():
                        if url_size == cached_filepath.stat().st_size:
                            print(f'Using cached {cached_filepath}')
                            break
                        else:
                            print('Cached file size mismatch. Downloading from url.')
                else:
                    cached_filepath = savepath

                cached_filepath.parent.mkdir(parents=True, exist_ok=True)

                file_size_dl = 0
                f = open(cached_filepath, 'wb')
                while True:
                    buffer = url_request.read(8192)
                    if not buffer:
                        break

                    f.write(buffer)

                    file_size_dl += len(buffer)

                    if progress_bar:
                        print(f'Downloading {file_size_dl} / {url_size}', end='\r')

            except:
                print(f'Unable to download {url}')
                raise
            break

        if f is not None:
            f.close()

        if use_cached:
            shutil.copy2(cached_filepath, savepath)

    def rmdir(self, path):
        os.system('del /F /S /Q "{}" > nul'.format(str(path)))
        os.system('rmdir /S /Q "{}"'.format(str(path)))


    def rmdir_in_all_subdirs(self, path, subdirname):
        for root, dirs, files in os.walk( str(path), topdown=False):
            if subdirname in dirs:
                self.rmdir( Path(root) / subdirname )


    def get_release_path(self): return self.release_path
    def get_internal_path(self): return self.internal_path

    def _validate_env(self):
        env = os.environ.copy()

        self.internal_path = self.release_path / self.DIRNAME_INTERNAL
        self.internal_path.mkdir(exist_ok=True, parents=True)

        self.local_env_path = self.internal_path / self.DIRNAME_LOCALENV
        self.local_env_path.mkdir(exist_ok=True, parents=True)

        self.temp_path = self.local_env_path / self.DIRNAME_TEMP
        self.temp_path.mkdir(exist_ok=True, parents=True)

        self.userprofile_path = self.local_env_path / self.DIRNAME_USERPROFILE
        self.userprofile_path.mkdir(exist_ok=True, parents=True)

        self.desktop_path = self.userprofile_path / self.DIRNAME_DESKTOP
        self.desktop_path.mkdir(exist_ok=True, parents=True)

        self.localappdata_path = self.userprofile_path / self.DIRNAME_APPDATA / self.DIRNAME_LOCAL
        self.localappdata_path.mkdir(exist_ok=True, parents=True)

        self.appdata_path = self.userprofile_path / self.DIRNAME_APPDATA / self.DIRNAME_ROAMING
        self.appdata_path.mkdir(exist_ok=True, parents=True)

        self.python_path = self.internal_path / self.DIRNAME_INTERNAL_PYTHON
        self.python_path.mkdir(exist_ok=True, parents=True)

        self.python_site_packages_path = self.python_path / 'Lib' / 'site-packages'
        self.python_site_packages_path.mkdir(exist_ok=True, parents=True)

        self.cuda_path = self.internal_path / self.DIRNAME_INTERNAL_CUDA
        self.cuda_path.mkdir(exist_ok=True, parents=True)

        self.cuda_bin_path = self.cuda_path / 'bin'
        self.cuda_bin_path.mkdir(exist_ok=True, parents=True)

        self.vscode_path = self.internal_path / self.DIRNAME_INTERNAL_VSCODE
        self.ffmpeg_path = self.internal_path / self.DIRNAME_INTERNAL_FFMPEG

        self._7zip_path = self.temp_path / '7zip'


        env['INTERNAL']     = str(self.internal_path)
        env['LOCALENV']     = str(self.local_env_path)
        env['TMP']          = \
        env['TEMP']         = str(self.temp_path)
        env['HOME']         = \
        env['HOMEPATH']     = \
        env['USERPROFILE']  = str(self.userprofile_path)
        env['DESKTOP']      = str(self.desktop_path)
        env['LOCALAPPDATA'] = str(self.localappdata_path)
        env['APPDATA']      = str(self.appdata_path)
        env['PYTHONHOME']   = ''
        env['PYTHONPATH']   = ''
        env['PYTHON_PATH']  = str(self.python_path)
        env['PYTHONEXECUTABLE']  = \
        env['PYTHON_EXECUTABLE'] = \
        env['PYTHON_BIN_PATH']   = str(self.python_path / 'python.exe')
        env['PYTHONWEXECUTABLE'] = \
        env['PYTHON_WEXECUTABLE'] = str(self.python_path / 'pythonw.exe')
        env['PYTHON_LIB_PATH']    = str(self.python_path / 'Lib' / 'site-packages')
        env['CUDA_PATH']    = str(self.cuda_path)
        env['PATH']   = f"{str(self.cuda_path)};{str(self.python_path)};{str(self.python_path / 'Scripts')};{env['PATH']}"

        if self.pip_cache_path is not None:
            env['PIP_CACHE_DIR'] = str(self.pip_cache_path)

        self.env = env

    def _install_internal(self):

        (self.internal_path / 'setenv.bat').write_text(
fr"""@echo off
SET INTERNAL=%~dp0
SET INTERNAL=%INTERNAL:~0,-1%
SET LOCALENV=%INTERNAL%\{self.DIRNAME_LOCALENV}
SET TMP=%LOCALENV%\{self.DIRNAME_TEMP}
SET TEMP=%TMP%
SET HOME=%LOCALENV%\{self.DIRNAME_USERPROFILE}
SET HOMEPATH=%HOME%
SET USERPROFILE=%HOME%
SET DESKTOP=%HOME%\{self.DIRNAME_DESKTOP}
SET LOCALAPPDATA=%USERPROFILE%\{self.DIRNAME_APPDATA}\{self.DIRNAME_LOCAL}
SET APPDATA=%USERPROFILE%\{self.DIRNAME_APPDATA}\{self.DIRNAME_ROAMING}

SET PYTHONHOME=
SET PYTHONPATH=
SET PYTHON_PATH=%INTERNAL%\python
SET PYTHONEXECUTABLE=%PYTHON_PATH%\python.exe
SET PYTHON_EXECUTABLE=%PYTHONEXECUTABLE%
SET PYTHONWEXECUTABLE=%PYTHON_PATH%\pythonw.exe
SET PYTHONW_EXECUTABLE=%PYTHONWEXECUTABLE%
SET PYTHON_BIN_PATH=%PYTHONEXECUTABLE%
SET PYTHON_LIB_PATH=%PYTHON_PATH%\Lib\site-packages
SET CUDA_PATH=%INTERNAL%\CUDA
SET CUDA_BIN_PATH=%CUDA_PATH%\bin
SET QT_QPA_PLATFORM_PLUGIN_PATH=%PYTHON_LIB_PATH%\PyQT6\Qt6\Plugins\platforms

SET PATH=%INTERNAL%\ffmpeg;%PYTHON_PATH%;%CUDA_BIN_PATH%;%PYTHON_PATH%\Scripts;%PATH%
""")
        self.clearenv_bat_path = self.internal_path / 'clearenv.bat'
        self.clearenv_bat_path.write_text(
fr"""@echo off
cd /D %~dp0
call setenv.bat
rmdir %LOCALENV% /s /q
mkdir %LOCALENV%
mkdir %TEMP%
mkdir %USERPROFILE%
mkdir %DESKTOP%
mkdir %LOCALAPPDATA%
mkdir %APPDATA%
""")
        (self.internal_path / 'python_console.bat').write_text(
fr"""
@echo off
cd /D %~dp0
call setenv.bat
cd python
cmd
""")

    def _install_python(self):
        python_url = self.URLS_PYTHON.get(self.python_ver, None)
        if python_url is None:
            raise Exception(f'No python URL defined for {self.python_ver}')

        print (f"Installing python {self.python_ver} to {self.python_path}\n")

        python_dl_path = self.python_path / f'python-{self.python_ver}.zip'

        if not python_dl_path.exists():
            self.download_file(python_url, python_dl_path)

        with zipfile.ZipFile(python_dl_path, 'r') as zip_ref:
            zip_ref.extractall(self.python_path)

        python_dl_path.unlink()

        # Remove _pth file
        for pth_file in self.python_path.glob("*._pth"):
            pth_file.unlink()

        print('Installing MS VC dlls.')

        self.download_and_unzip(self.URL_MSVC, self.python_path)

        print ("Installing pip.\n")

        python_pip_path = self.python_path / 'get-pip.py'

        self.download_file(self.URL_PIP, python_pip_path)

        subprocess.Popen(args='python.exe get-pip.py', cwd=str(self.python_path), shell=True, env=self.env).wait()
        python_pip_path.unlink()

    def _get_7zip_bin_path(self):
        if not self._7zip_path.exists():
            self.download_and_unzip(self.URL_7ZIP, self._7zip_path)
        return self._7zip_path / '7za.exe'

    def cleanup(self):
        print ('Cleanup.\n')
        subprocess.Popen(args=str(self.clearenv_bat_path), shell=True).wait()
        self.rmdir_in_all_subdirs (self.release_path, '__pycache__')

    def pack_sfx_release(self, archive_name):
        archiver_path = self._get_7zip_bin_path()
        archive_path = self.release_path.parent / (archive_name+'.exe')

        subprocess.Popen(args='"%s" a -t7z -sfx7z.sfx -m0=LZMA2 -mx9 -mtm=off -mmt=8 "%s" "%s"' % ( \
                                str(archiver_path),
                                str(archive_path),
                                str(self.release_path)  ),
                            shell=True).wait()

    def download_and_unzip(self, url, unzip_dirpath, only_files_list : List =None):
        """
        Download and unzip entire content to unzip_dirpath

         only_files_list(None)  if specified
                                only first match of these files
                                will be extracted to unzip_dirpath without folder structure
        """
        unzip_dirpath.mkdir(parents=True, exist_ok=True)

        tmp_zippath = unzip_dirpath / '__dl.zip'

        self.download_file(url, tmp_zippath)

        with zipfile.ZipFile(tmp_zippath, 'r') as zip_ref:
            for entry in zip_ref.filelist:

                if only_files_list is not None:
                    if not entry.is_dir():
                        entry_filepath = Path( entry.filename )
                        if entry_filepath.name in only_files_list:
                            only_files_list.remove(entry_filepath.name)
                            (unzip_dirpath / entry_filepath.name).write_bytes ( zip_ref.read(entry) )
                else:
                    entry_outpath = unzip_dirpath / Path(entry.filename)

                    if entry.is_dir():
                        entry_outpath.mkdir(parents=True, exist_ok=True)
                    else:
                        entry_outpath.write_bytes ( zip_ref.read(entry) )

        tmp_zippath.unlink()

    def install_pip_package(self, pkg_name):
        subprocess.Popen(args=f'python.exe -m pip install {pkg_name}', cwd=str(self.python_path), shell=True, env=self.env).wait()

    def run_python(self, argsline, cwd=None):
        if cwd is None:
            cwd = self.python_path
        subprocess.Popen(args=f'python.exe {argsline}', cwd=str(cwd), shell=True, env=self.env).wait()

    def install_ffmpeg_binaries(self):
        print('Installing ffmpeg binaries.')
        self.ffmpeg_path.mkdir(exist_ok=True, parents=True)
        self.download_and_unzip(self.URL_FFMPEG, self.ffmpeg_path, only_files_list=['ffmpeg.exe', 'ffprobe.exe'] )

    def install_vscode(self, project_internal_dir : str = None):
        """
        Installs vscode
        """
        print('Installing VSCode.\n')

        self.vscode_path.mkdir(exist_ok=True, parents=True)
        vscode_zip_path = self.vscode_path / 'VSCode.zip'
        self.download_file(self.URL_VSCODE, vscode_zip_path, use_cached=False)
        with zipfile.ZipFile(vscode_zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.vscode_path)
        vscode_zip_path.unlink()

        # Create bat
        (self.internal_path  / 'vscode.bat').write_text(
fr"""@echo off
cd /D %~dp0
call setenv.bat
start "" /D "%~dp0" "%INTERNAL%\{self.DIRNAME_INTERNAL_VSCODE}\Code.exe" --disable-workspace-trust "project.code-workspace"
""")

        # Enable portable mode in VSCode
        (self.vscode_path / 'data').mkdir(exist_ok=True)

        # Create vscode project
        if project_internal_dir is None:
            project_internal_dir = '.'

        (self.internal_path / 'project.code-workspace').write_text (
fr'''{{
	"folders": [
		{{
			"path": "{project_internal_dir}"
		}}
	],
	"settings": {{
        "workbench.colorTheme": "Visual Studio Light",
        "diffEditor.ignoreTrimWhitespace": true,
        "workbench.sideBar.location": "right",
        "breadcrumbs.enabled": false,
        "editor.renderWhitespace": "none",
        "editor.minimap.enabled": false,
        "workbench.activityBar.visible": true,
        "window.menuBarVisibility": "default",
        "editor.fastScrollSensitivity": 10,
        "editor.mouseWheelScrollSensitivity": 2,
        "window.zoomLevel": 0,
        "extensions.ignoreRecommendations": true,
        "debug.showBreakpointsInOverviewRuler": true,
        "python.linting.pylintEnabled": false,
        "python.linting.enabled": false,
        "python.linting.pylamaEnabled": false,
        "python.linting.pydocstyleEnabled": false,
        "python.defaultInterpreterPath": "${{env:PYTHON_EXECUTABLE}}",
        "telemetry.enableTelemetry": false,
		"workbench.editor.tabCloseButton": "off",
		"workbench.editor.tabSizing": "shrink",
		"workbench.editor.highlightModifiedTabs": true,
        "workbench.enableExperiments": false,
		"editor.mouseWheelScrollSensitivity": 3,
		"editor.folding": false,
		"editor.glyphMargin": false,
		"files.exclude": {{
			"**/__pycache__": true,
			"**/.github": true,
			"**/.vscode": true,
			"**/*.dat": true,
			"**/*.h5": true,
            "**/*.npy": true
		}},
		"editor.quickSuggestions": {{"other": false,"comments": false,"strings": false}},
			"editor.trimAutoWhitespace": false,
			"python.linting.pylintArgs": ["--disable=import-error"],
            "python.linting.enabled": false,
            "editor.lightbulb.enabled": false,
            "python.languageServer": "Pylance"
	}}
}}
''')
        subprocess.Popen(args=f'bin\code.cmd --disable-workspace-trust --install-extension ms-python.python', cwd=self.vscode_path, shell=True, env=self.env).wait()
        subprocess.Popen(args=f'bin\code.cmd --disable-workspace-trust --install-extension ms-python.vscode-pylance', cwd=self.vscode_path, shell=True, env=self.env).wait()
        subprocess.Popen(args=f'bin\code.cmd --disable-workspace-trust --install-extension searking.preview-vscode', cwd=self.vscode_path, shell=True, env=self.env).wait()

    def create_run_python_script(self, script_name : str, internal_relative_path : str, args_str : str):

        (self.release_path / script_name).write_text(
fr"""@echo off
cd /D %~dp0
call {self.DIRNAME_INTERNAL}\setenv.bat
"%PYTHONEXECUTABLE%" {self.DIRNAME_INTERNAL}\{internal_relative_path} {args_str}
pause
""")

    def create_internal_run_python_script(self, script_name : str, internal_relative_path : str, args_str : str):

        (self.internal_path / script_name).write_text(
fr"""@echo off
cd /D %~dp0
call setenv.bat
"%PYTHONEXECUTABLE%" {internal_relative_path} {args_str}
pause
""")


def build_deepfacelive_windows(release_dir, cache_dir, python_ver='3.8.10', backend='cuda'):

    builder = WindowsFolderBuilder(release_path=Path(release_dir),
                                   cache_path=Path(cache_dir),
                                   python_ver=python_ver,
                                   clear_release_path=True)

    # PIP INSTALLATIONS

    builder.install_pip_package('numpy==1.21.6')
    builder.install_pip_package('h5py')
    builder.install_pip_package('numexpr')
    builder.install_pip_package('protobuf==3.20.1')
    builder.install_pip_package('opencv-python==4.8.0.74')
    builder.install_pip_package('opencv-contrib-python==4.8.0.74')
    builder.install_pip_package('pyqt6==6.5.1')
    builder.install_pip_package('onnx==1.14.0')

    if backend == 'cuda':
        #builder.install_pip_package('torch==1.10.0+cu113 torchvision==0.11.1+cu113 -f https://download.pytorch.org/whl/torch_stable.html')
        #builder.install_pip_package('torch==1.11.0+cu115 torchvision==0.12.0+cu115 -f https://download.pytorch.org/whl/torch_stable.html')
        builder.install_pip_package('torch==1.13.1+cu117 torchvision==0.14.1+cu117 -f https://download.pytorch.org/whl/torch_stable.html')
        
        builder.install_pip_package('onnxruntime-gpu==1.15.1')
    elif backend == 'directml':
        builder.install_pip_package('onnxruntime-directml==1.15.1')

    builder.install_ffmpeg_binaries()

    #

    if backend == 'cuda':
        print('Moving CUDA dlls from Torch to shared directory')
        cuda_bin_path = builder.cuda_bin_path
        torch_lib_path = builder.python_site_packages_path / 'torch' / 'lib'

        for cu_file in torch_lib_path.glob("**/cu*64*.dll"):
            target = cuda_bin_path / cu_file.name
            print (f'Moving {target}')
            shutil.move (str(cu_file), str(target) )

        for file in torch_lib_path.glob("**/nvrtc*.dll"):
            target = cuda_bin_path / file.name
            print (f'Moving {target}')
            shutil.move (str(file), str(target) )

        for file in torch_lib_path.glob("**/zlibwapi.dll"):
            target = cuda_bin_path / file.name
            print (f'Copying {target}')
            shutil.copy (str(file), str(target) )
            
    deepfacelive_path = builder.get_internal_path() / 'DeepFaceLive'

    print('Copying DeepFaceLive repository.')
    builder.copyfiletree(Path(__file__).parent.parent.parent, deepfacelive_path)
    builder.rmdir_in_all_subdirs(deepfacelive_path, '.git')

    release_path = builder.get_release_path()
    userdata_path = release_path / 'userdata'
    userdata_path.mkdir(parents=True, exist_ok=True)

    dfm_models_path = userdata_path / 'dfm_models'
    dfm_models_path.mkdir(parents=True, exist_ok=True)

    print('Copying samples.')
    shutil.copytree( str(Path(__file__).parent.parent / 'samples'), str(userdata_path / 'samples') )

    print('Copying animatables.')
    shutil.copytree( str(Path(__file__).parent.parent / 'animatables'), str(userdata_path / 'animatables') )

    if backend == 'cuda':
        builder.create_run_python_script('DeepFaceLive.bat', 'DeepFaceLive\\main.py', 'run DeepFaceLive --userdata-dir="%~dp0userdata"')
    elif backend == 'directml':
        builder.create_run_python_script('DeepFaceLive.bat', 'DeepFaceLive\\main.py', 'run DeepFaceLive --userdata-dir="%~dp0userdata" --no-cuda')

    builder.create_internal_run_python_script('build DeepFaceLive NVIDIA.bat',    'DeepFaceLive\\build\\windows\\WindowsBuilder.py', '--build-type dfl-windows --release-dir Builds\DeepFaceLive_NVIDIA --cache-dir _cache --backend cuda')
    builder.create_internal_run_python_script('build DeepFaceLive DirectX12.bat', 'DeepFaceLive\\build\\windows\\WindowsBuilder.py', '--build-type dfl-windows --release-dir Builds\DeepFaceLive_DirectX12 --cache-dir _cache --backend directml')

    builder.run_python('main.py dev merge_large_files --delete-parts', cwd=deepfacelive_path)
    
    builder.install_vscode(project_internal_dir='DeepFaceLive')
    
    builder.cleanup()

    if backend == 'cuda':
        build_name = f'DeepFaceLive_NVIDIA_build_{datetime.now().strftime("%m_%d_%Y")}'
    elif backend == 'directml':
        build_name = f'DeepFaceLive_DirectX12_build_{datetime.now().strftime("%m_%d_%Y")}'
    builder.pack_sfx_release(build_name)

class fixPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--build-type', required=True, choices=['dfl-windows'])
    p.add_argument('--release-dir', action=fixPathAction, default=None)
    p.add_argument('--cache-dir', action=fixPathAction, default=None)
    p.add_argument('--python-ver', default="3.8.10")
    p.add_argument('--backend', choices=['cuda', 'directml'], default='cuda')

    args = p.parse_args()

    if args.build_type == 'dfl-windows':
        build_deepfacelive_windows(release_dir=args.release_dir,
                                   cache_dir=args.cache_dir,
                                   python_ver=args.python_ver,
                                   backend=args.backend)



