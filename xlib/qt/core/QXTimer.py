from PyQt6.QtCore import *


class QXTimer(QTimer):

    def __init__(self, interval=None, timeout=None, single_shot=False, start=False):
        super().__init__()

        if interval is not None:
            self.setInterval(interval)

        if timeout is not None:
            self.timeout.connect(timeout)

        if single_shot:
            self.setSingleShot(True)

        if start:
            self.start()
