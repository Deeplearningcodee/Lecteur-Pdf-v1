from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal
from PIL.ImageQt import ImageQt
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from PIL import Image
from PyQt5.QtWidgets import QPushButton
from text_extraction import extract_text_from_image
from PyQt5.QtWidgets import QPlainTextEdit




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

        # Create next and previous page buttons
        self.next_page_button = QPushButton("Next Page", self)
        self.next_page_button.clicked.connect(self.next_page)
        self.prev_page_button = QPushButton("Previous Page", self)
        self.prev_page_button.clicked.connect(self.previous_page)

        
        #extract text button
        self.extract_text_button = QPushButton("Extract Text from Images", self)
        self.extract_text_button.clicked.connect(self.extract_text_from_images)
        

        # Set layout
        main_layout = QHBoxLayout()

        pdf_layout = QVBoxLayout()
        pdf_layout.addWidget(self.label)
        pdf_layout.addWidget(self.prev_page_button)
        pdf_layout.addWidget(self.next_page_button)
        main_layout.addLayout(pdf_layout)

        comments_layout = QVBoxLayout()
        comments_layout.addWidget(self.comments)
        comments_layout.addWidget(self.save_comment_button)
        comments_layout.addWidget(self.extract_text_button)
        main_layout.addLayout(comments_layout)

        self.setLayout(main_layout)

    
    def extract_text_from_images(self):
        # Get the current image
        if not self.images:
            return

        image = self.images[self.current_page]

        # Extract text from the image
        text = extract_text_from_image(image)

        # Create a QMessageBox with a QPlainTextEdit widget
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Extracted Text")

        plain_text_edit = QPlainTextEdit()
        plain_text_edit.setPlainText(text)
        plain_text_edit.setReadOnly(True)
        plain_text_edit.setFixedSize(600, 400)  # Set the size of the widget

        msg_box.layout().addWidget(plain_text_edit, 0, QMessageBox.ActionRole)
        msg_box.exec_()

    def extract_text_from_image(image):
        text = pytesseract.image_to_string(image)
        return text


        
    def next_page(self):
        if self.current_page < len(self.images) - 1:
            self.current_page += 1
            self.display_page()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def save_comment(self):
        # Get the file name of the PDF associated with this tab and replace the extension with "_pdf.txt"
        file_name = self.parent().parent().tabText(self.parent().parent().currentIndex()).replace(".pdf", "_pdf.txt")

        # Save the contents of the QTextEdit widget to a file
        with open(file_name, "w") as file:
            file.write(self.comments.toPlainText())
        msg_box = QMessageBox()
        msg_box.setText("Comment saved.")
        msg_box.exec_()
        self.comments.clear() 


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

