from PyQt6.QtWidgets import *


class QXDirDialog(QFileDialog):
    def __init__(self, parent=None, caption : str = None, directory : str = None, accepted=None):
        super().__init__(parent=parent, directory=directory)
        self.setOption(QFileDialog.Option.DontUseNativeDialog)
        self.setOption(QFileDialog.Option.ShowDirsOnly, True)
        self.setFileMode(QFileDialog.FileMode.Directory)
        if caption is not None:
            self.setWindowTitle(caption)
        if accepted is not None:
            self.accepted.connect(accepted)

