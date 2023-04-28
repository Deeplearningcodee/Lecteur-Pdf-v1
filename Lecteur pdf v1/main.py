from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QFileDialog, QToolBar, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QTextEdit, QPushButton, QMessageBox, QTabBar
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import QSize, Qt, QRect, QPoint
from PIL.ImageQt import ImageQt
from pdf2image import convert_from_path
from io import BytesIO
from PyPDF2 import PdfReader
from PIL import Image
import os


class PdfViewer(QWidget):
    def __init__(self):
        super().__init__()

           # Create a label widget for the PDF pages and a QTextEdit widget for comments
        self.label = QLabel(self)
        self.comments = QTextEdit(self)
        self.comments.setMaximumWidth(300)  # Limit the width of the QTextEdit widget
        self.save_comment_button = QPushButton("Save Comment", self)
        self.save_comment_button.clicked.connect(self.save_comment)

        # Initialize the list of images and the current page index
        self.images = []
        self.current_page = 0
        self.pages_displayed = 2  # Initialize pages_displayed attribute

        # Set layout
        main_layout = QHBoxLayout()

        pdf_layout = QVBoxLayout()
        pdf_layout.addWidget(self.label)
        main_layout.addLayout(pdf_layout)

        comments_layout = QVBoxLayout()
        comments_layout.addWidget(self.comments)
        comments_layout.addWidget(self.save_comment_button)
        main_layout.addLayout(comments_layout)

        self.setLayout(main_layout)

    
    def save_comment(self):
        # Get the file name of the PDF associated with this tab and replace the extension with "_pdf.txt"
        file_name = self.parent().parent().tabText(self.parent().parent().currentIndex()).replace(".pdf", "_pdf.txt")

        # Save the contents of the QTextEdit widget to a file
        with open(file_name, "w") as file:
            file.write(self.comments.toPlainText())
        msg_box = QMessageBox()
        msg_box.setText("Comment saved.")
        msg_box.exec_()


    def open_file(self, file_name):
        # Read the PDF file and convert its pages to images
        with open(file_name, "rb") as file:
            pdf_reader = PdfReader(file)
            num_pages = len(pdf_reader.pages)
            print(f"The PDF file contains {num_pages} pages.")

            # Load each page as a separate image and append it to the list
            self.images = []
            for page_num in range(1, num_pages+1):
                images = convert_from_path(file_name, first_page=page_num, last_page=page_num)
                self.images.extend(images)

            # Display the first page
            if self.images:
                self.current_page = 0
                self.display_page()

    def display_page(self):
        if not self.images:
            self.label.setPixmap(QPixmap())
            return

        # Get the current image and convert it to a QImage
        self.current_image = self.images[self.current_page]
        self.current_qimage = ImageQt(self.current_image.convert("RGBA"))

        # Combine images side by side
        combined_image = self.current_image.copy()
        for i in range(1, self.pages_displayed):
            if self.current_page + i < len(self.images):
                next_image = self.images[self.current_page + i]
                combined_image = self.concatenate_images(combined_image, next_image)

        combined_qimage = ImageQt(combined_image.convert("RGBA"))

        # Resize the image to fit the label widget
        label_size = self.label.size()
        scaled_image_size = combined_qimage.size().scaled(label_size, Qt.KeepAspectRatio)
        scaled_image = combined_qimage.scaled(scaled_image_size, Qt.KeepAspectRatio)

        # Convert the image to a pixmap and set it as the label's pixmap
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

    def concatenate_images(self, img1, img2):
        combined_image = Image.new(
            "RGBA",
            (img1.width + img2.width, max(img1.height, img2.height)),
        )
        combined_image.paste(img1, (0, 0))
        combined_image.paste(img2, (img1.width, 0))
        return combined_image


    def resizeEvent(self, event):
        # Call the base class method
        super().resizeEvent(event)

        # Update the size of the displayed image
        self.display_page()

    def increase_pages_displayed(self):
        self.pages_displayed += 1
        self.display_page()

    def decrease_pages_displayed(self):
        if self.pages_displayed > 1:
            self.pages_displayed -= 1
            self.display_page()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("PDF Reader")

        # Set the window size and minimum size
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(400, 300)
      

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)  # Enable the close button
        self.tab_widget.tabCloseRequested.connect(self.remove_tab)  # Connect the signal to a function
        self.setCentralWidget(self.tab_widget)
        

        # Create a menu bar
        menu_bar = self.menuBar()

        # Create a file menu and add it to the menu bar
        file_menu = menu_bar.addMenu("File")

        # Create an open action and add it to the file menu
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

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

            


    def keyPressEvent(self, event):
        current_tab = self.tab_widget.currentWidget()

        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_U:
                current_tab.increase_pages_displayed()
            elif event.key() == Qt.Key_D:
                current_tab.decrease_pages_displayed()
            elif event.key() == Qt.Key_O:
                self.open_file()





if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()