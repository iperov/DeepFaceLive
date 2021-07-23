from PyQt6.QtWidgets import *


class QXFileDialog(QFileDialog):
    def __init__(self, parent=None,
                       multi_files=False,
                       existing_only=False,
                       is_save=False,
                       filter=None,
                       accepted=None):

        super().__init__(parent=parent, filter=filter)
        self.setOption(QFileDialog.Option.DontUseNativeDialog)

        if is_save:
            self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        if multi_files:
            self.setFileMode(QFileDialog.FileMode.ExistingFiles)
        else:
            if existing_only:
                self.setFileMode(QFileDialog.FileMode.ExistingFile)
            else:
                self.setFileMode(QFileDialog.FileMode.AnyFile)

        if accepted is not None:
            self.accepted.connect(accepted)
