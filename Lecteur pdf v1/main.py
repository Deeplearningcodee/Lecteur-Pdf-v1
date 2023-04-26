from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QFileDialog, QToolBar
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QSize
from PIL.ImageQt import ImageQt


from PyQt5.QtCore import Qt
from pdf2image import convert_from_path
from io import BytesIO
from PyPDF2 import PdfReader  # Updated import statement
from PIL import Image
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("PDF Reader")

        # Set the window size and minimum size
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(400, 300)

        # Create a label widget
        self.label = QLabel(self)
        self.setCentralWidget(self.label)

        # Initialize the list of images and the current page index
        self.images = []
        self.current_page = 0

        # Create a menu bar
        menu_bar = self.menuBar()

        # Create a file menu and add it to the menu bar
        file_menu = menu_bar.addMenu("File")

        # Create an open action and add it to the file menu
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Create a toolbar
        toolbar = QToolBar("Navigation", self)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Create a "Show Previous Page" action and add it to the toolbar
        prev_page_action = QAction("Previous Page", self)
        prev_page_action.triggered.connect(self.show_previous_page)
        toolbar.addAction(prev_page_action)

        # Create a "Show Next Page" action and add it to the toolbar
        next_page_action = QAction("Next Page", self)
        next_page_action.triggered.connect(self.show_next_page)
        toolbar.addAction(next_page_action)
        next_page_action.setEnabled(False)

        # Store a reference to the toolbar for later use
        self.toolbar = toolbar

    def open_file(self):
        # Show the file dialog
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            # Get the selected file name
            file_name = file_dialog.selectedFiles()[0]

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

                # Display the first two images side by side
                if len(self.images) >= 2:
                    self.toolbar.actions()[1].setEnabled(True)
                    self.current_page = 0
                    self.display_page()


    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 2
            self.display_page()
            self.toolbar.actions()[1].setEnabled(True)
        if self.current_page == 0:
            self.toolbar.actions()[0].setEnabled(False)


    def show_next_page(self):
        if self.current_page < len(self.images) - 2:
            self.current_page += 2
            self.display_page()
            


    def display_page(self):
        # Get the current image and convert it to a QImage
        self.current_image = self.images[self.current_page]
        self.current_qimage = ImageQt(self.current_image.convert("RGBA"))

        # Combine images horizontally if there are more than one images in the list
        if len(self.images) > 1:
            # Get the next image and convert it to a QImage
            next_page = (self.current_page + 1) % len(self.images)
            self.next_image = self.images[next_page]
            self.next_qimage = ImageQt(self.next_image.convert("RGBA"))

            # Concatenate the images horizontally
            combined_image = Image.new(
                "RGBA", (self.current_image.width + self.next_image.width, max(self.current_image.height, self.next_image.height))
            )
            combined_image.paste(self.current_image, (0, 0))
            combined_image.paste(self.next_image, (self.current_image.width, 0))
            combined_qimage = ImageQt(combined_image)
        else:
            combined_qimage = self.current_qimage

        # Resize the image to fit the label widget
        label_size = self.label.size()
        scaled_image_size = combined_qimage.size().scaled(label_size, Qt.KeepAspectRatio)
        scaled_image = combined_qimage.scaled(scaled_image_size, Qt.KeepAspectRatio)

        # Convert the image to a pixmap and set it as the label's pixmap
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

            # Enable or disable the navigation buttons as appropriate
        if self.current_page == 0:
            self.toolbar.actions()[0].setEnabled(False)
        else:
            self.toolbar.actions()[0].setEnabled(True)
        if self.current_page == len(self.images) - 1:
            self.toolbar.actions()[1].setEnabled(False)
        else:
            self.toolbar.actions()[1].setEnabled(True)






    def resizeEvent(self, event):
        # Call the base class method
        super().resizeEvent(event)

        # Update the size of the displayed image
        self.update_image_size()

    def update_image_size(self):
        if self.images:
            # Get the size of the label widget
            label_size = self.label.size()

            # Calculate the width and height of each image
            num_images = len(self.images)
            image_width = label_size.width() // num_images
            image_height = label_size.height()

            # Combine the images horizontally
            combined_image = Image.new("RGBA", (label_size.width(), image_height))
            x_offset = 0
            for image in self.images:
                # Resize each image to fit the width and height of the label widget
                scaled_image = image.resize((image_width, image_height))

                # Paste the image onto the combined image
                combined_image.paste(scaled_image, (x_offset, 0))

                # Update the x offset for the next image
                x_offset += image_width

            # Convert the combined image to a QImage and resize it to fit the label widget
            qimage = ImageQt(combined_image.convert("RGBA"))
            scaled_qimage = qimage.scaled(label_size, Qt.KeepAspectRatio)

            # Convert the QImage to a QPixmap and set it as the label's pixmap
            pixmap = QPixmap.fromImage(scaled_qimage)
            self.label.setPixmap(pixmap)
        else:
            # If there are no images, clear the label's pixmap
            self.label.setPixmap(QPixmap())









if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
