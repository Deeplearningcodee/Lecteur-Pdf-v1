from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QFileDialog, QToolBar, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QTextEdit, QPushButton, QMessageBox, QTabBar,QStatusBar,QComboBox
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QBrush, QColor,QIcon
from PyQt5.QtCore import QSize, Qt, QRect, QPoint,QEvent
from PIL.ImageQt import ImageQt
from pdf2image import convert_from_path
from io import BytesIO
from PyPDF2 import PdfReader
from PIL import Image
import os
from pdfviewer import PdfViewer
import pytesseract
from PIL import Image
from PyQt5.QtWidgets import QPushButton
from text_extraction import extract_text_from_image


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        
        # Set the window title
        self.setWindowTitle("PDF Reader")

        # Set the window size and minimum size
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(400, 300)

        # Create a QVBoxLayout for the central widget
        central_widget = QWidget(self)
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Create a tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.remove_tab)
        self.tab_widget.setVisible(False)
        central_layout.addWidget(self.tab_widget)

        # Create an "Open" button
        self.open_button = QPushButton(self)
        self.open_button.setIcon(QIcon("folder.png"))
        self.open_button.setIconSize(QSize(50, 50))
        self.open_button.clicked.connect(self.open_file)
        central_layout.addWidget(self.open_button, alignment=Qt.AlignCenter)



  



        # Initialize the toolbar_created flag
        self.toolbar_created = False



    def extract_text(self):
        # Show the file dialog
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            # Get the selected file name
            image_path = file_dialog.selectedFiles()[0]

            # Open the image and extract the text
            image = Image.open(image_path)
            text = extract_text_from_image(image)

            # Display the extracted text in a QMessageBox
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Extracted Text")
            msg_box.setText(text)
            msg_box.exec_()



        # Add these new methods to the MainWindow class
    def switch_to_single_mode(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            current_tab.set_mode("single")

    def switch_to_book_mode(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            current_tab.set_mode("book")

    # Create a method to create the toolbar
    def create_toolbar(self):
        toolbar = self.addToolBar("Toolbar")

        open_action = QAction(QIcon("folder.png"), "Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)


        single_mode_action = QAction("Single Mode", self)
        single_mode_action.triggered.connect(self.switch_to_single_mode)
        toolbar.addAction(single_mode_action)

        book_mode_action = QAction("Book Mode", self)
        book_mode_action.triggered.connect(self.switch_to_book_mode)
        toolbar.addAction(book_mode_action)



    def remove_tab(self, index):
        # Get the widget at the specified index and remove it from the tab widget
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        widget.deleteLater()  # Free up the memory used by the widget


    def open_file(self):
        # Show the file dialog
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            # Get the selected file name
            file_name = file_dialog.selectedFiles()[0]

            # Create a new PdfViewer and add it to a new tab
            pdf_viewer = PdfViewer()
            pdf_viewer.open_file(file_name)
            self.tab_widget.addTab(pdf_viewer, os.path.basename(file_name))

            # Hide the "Open" button and show the tab widget
            self.open_button.setVisible(False)
            self.tab_widget.setVisible(True)

            # Create the toolbar only if it hasn't been created before
            if not self.toolbar_created:
                self.create_toolbar()
                self.toolbar_created = True     



    def keyPressEvent(self, event):
        current_tab = self.tab_widget.currentWidget()

        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_U:
                current_tab.increase_pages_displayed()
            elif event.key() == Qt.Key_D:
                current_tab.decrease_pages_displayed()
            elif event.key() == Qt.Key_O:
                self.open_file()
        elif event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            if event.key() == Qt.Key_U:
                current_tab.rows += 1
                current_tab.pages_displayed = current_tab.cols * current_tab.rows
                current_tab.display_page()
            elif event.key() == Qt.Key_D:
                if current_tab.rows > 1:
                    current_tab.rows -= 1
                    current_tab.pages_displayed = current_tab.cols * current_tab.rows
                    current_tab.display_page()

 





if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()