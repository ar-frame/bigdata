from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QApplication, QWidget

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# pip install PyQt6
# pip install PyQt6-WebEngine
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

class CustomWebEnginePage(QWebEnginePage):
    """ Custom WebEnginePage to customize how we handle link navigation """
    # Store external windows.
    external_windows = []

    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            w = QWebEngineView()
            w.setUrl(url)
            w.show()

            # Keep reference to external window, so it isn't cleared up.
            self.external_windows.append(w)
            return False
        return super().acceptNavigationRequest(url,  _type, isMainFrame)

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.browser = QWebEngineView()
        # self.browser.setPage(CustomWebEnginePage(self))
        self.browser.setUrl(QUrl("http://localhost:3000/?account=dtest2"))
        self.setCentralWidget(self.browser)
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()