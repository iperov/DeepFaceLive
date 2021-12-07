from pathlib import Path

from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QPathEditCSWPaths(QCSWControl):
    def __init__(self, csw_path : lib_csw.Paths.Client, reflect_state_widgets=None):
        """
        Implements lib_csw.Paths control as LineEdit with Button to manage the Path
        """
        if not isinstance(csw_path, lib_csw.Paths.Client):
            raise ValueError('csw_path must be an instance of Paths.Client')

        self._csw_path = csw_path
        self._dlg = None

        csw_path.call_on_config(self.on_csw_config)
        csw_path.call_on_paths(self._on_csw_paths)

        lineedit = self._lineedit = qtx.QXLineEdit(font=QXFontDB.get_fixedwidth_font(),
                                                   placeholder_text='...',
                                                   size_policy=('expanding', 'fixed'),
                                                   editingFinished=self.on_lineedit_editingFinished)

        btn_open = self._btn_open = qtx.QXPushButton(image=QXImageDB.folder_open_outline(color='light gray'),
                                                     tooltip_text='Open',
                                                     released=self._on_btn_open_released,
                                                     fixed_size=(24,22) )

        btn_reveal = self._btn_reveal = qtx.QXPushButton(image=QXImageDB.eye_outline(color='light gray'),
                                                         tooltip_text='Reveal in explorer',
                                                         released=self._on_btn_reveal_released,
                                                         fixed_size=(24,22) )

        btn_erase = self._btn_erase = qtx.QXPushButton(image=QXImageDB.close_outline(color='light gray'),
                                                       tooltip_text='Erase',
                                                       released=self._on_btn_erase_released,
                                                       fixed_size=(24,22) )
        super().__init__(csw_control=csw_path, reflect_state_widgets=reflect_state_widgets,
                         layout=qtx.QXHBoxLayout([lineedit, 2, btn_open, btn_reveal, btn_erase]) )

    def on_csw_config(self, cfg : lib_csw.Paths.Config):
        type = cfg.get_type()
        caption = cfg.get_caption()
        if caption is None:
            caption = ""
        suffixes = cfg.get_suffixes()
        is_save = cfg.is_save()

        file_filter = None
        if suffixes is not None:
            file_filter = f"{caption} ({' '.join(['*'+suf for suf in suffixes])})"

        if type == lib_csw.Paths.Config.Type.ANY_FILE:
            self._dlg = qtx.QXFileDialog(self,
                                            filter=file_filter,
                                            existing_only=False,
                                            is_save=is_save,
                                            accepted=self._on_dlg_accepted)
        elif type == lib_csw.Paths.Config.Type.EXISTING_FILE:
            self._dlg = qtx.QXFileDialog(self,
                                            filter=file_filter,
                                            existing_only=True,
                                            is_save=is_save,
                                            accepted=self._on_dlg_accepted)

        elif type == lib_csw.Paths.Config.Type.EXISTING_FILES:
            self._dlg = qtx.QXFileDialog(self,
                                            multi_files=True,
                                            existing_only=True,
                                            filter=file_filter,
                                            accepted=self._on_dlg_accepted)
        elif type == lib_csw.Paths.Config.Type.DIRECTORY:
            directory = cfg.get_directory_path()
            if directory is not None:
                directory = str(directory)
            self._dlg = qtx.QXDirDialog(self, caption=caption, directory=directory, accepted=self._on_dlg_accepted)

    def _on_dlg_accepted(self):
        self._lineedit.setText( self._dlg.selectedFiles()[0] )
        self._lineedit.editingFinished.emit()

    def _on_csw_paths(self, paths, prev_paths):
        if len(paths) == 0:
            text = None
        elif len(paths) == 1:
            text = str(paths[0])
        else:
            raise NotImplementedError()

        with qtx.BlockSignals(self._lineedit):
            self._lineedit.setText(text)

    def _on_btn_erase_released(self):
        self._csw_path.set_paths(None)


    def _on_btn_open_released(self):
        if self._dlg is not None:
            self._dlg.open()
        else:
            print('lib_csw.Paths.Config was not initialized.')


    def _on_btn_reveal_released(self):
        dirpath = self._lineedit.text()
        if dirpath is not None and len(dirpath) != 0:
            dirpath = Path(dirpath)
            if dirpath.is_file():
                dirpath = dirpath.parent

            qtx.QDesktopServices.openUrl( qtx.QUrl.fromLocalFile(str(dirpath)) )

    def on_lineedit_editingFinished(self):
        text = self._lineedit.text()
        if len(text) == 0:
            text = None
        self._csw_path.set_paths( text )
