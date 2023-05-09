import time

from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# pip install PyQt6
# pip install PyQt6-WebEngine
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget

import cfg


class CustomWebEnginePage(QWebEnginePage):
    """ Custom WebEnginePage to customize how we handle link navigation """
    # Store external windows.
    external_windows = []

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            w = QWebEngineView()
            w.setUrl(url)
            w.show()

            # Keep reference to external window, so it isn't cleared up.
            self.external_windows.append(w)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)


# Subclass QMainWindow to customize your application's main window
class BroswerWindow(QWidget):
    def __init__(self, title, account, path):
        super().__init__()
        self.setWindowTitle(title)
        self.browser = QWebEngineView()
        # self.browser.setPage(CustomWebEnginePage(self))
        servercfg = cfg.getCfg().get('set', 'localwebserver')
        host = servercfg.split(':')[0]
        port = servercfg.split(':')[1]
        url = "http://" + host + ":" + port + "/" + path + "/?account=" + account + "&tm=" + str(time.time())
        print('load url', url)
        self.browser.setUrl(QUrl(url))
        # self.setCentralWidget(self.browser)

        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BroswerWindow('aabbcc', 'dtest2')
    window.show()
    app.exec()
