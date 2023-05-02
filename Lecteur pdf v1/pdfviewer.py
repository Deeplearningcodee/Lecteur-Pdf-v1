from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,QMessageBox,QScrollArea,QComboBox,QToolBar,QGraphicsView,QGraphicsScene
from PyQt5.QtGui import QPixmap, QImage,QPainter,QBrush,QColor
from PyQt5.QtCore import Qt, pyqtSignal
from PIL.ImageQt import ImageQt
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from PIL import Image
from PyQt5.QtWidgets import QPushButton,QLineEdit
from text_extraction import extract_text_from_image
from PyQt5.QtWidgets import QPlainTextEdit
from PIL import ImageChops,ImageOps







class PdfViewer(QWidget):
   

    def __init__(self):
        super().__init__()

        self.mode = "single"  # Default mode is single
        self.zoom_level = 1.0

        # Replace the QLabel with a QGraphicsView
        self.view = QGraphicsView(self)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)

        # Create a QGraphicsScene
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        # Create a scroll area and add the QGraphicsView widget to it
        self.scroll_area = QScrollArea(self)
        self.scroll_area.wheelEvent = self.zoom

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidget(self.view)

        self.comments = QTextEdit(self)
        self.comments.setMaximumWidth(300)  # Limit the width of the QTextEdit widget
        self.save_comment_button = QPushButton("Save Comment", self)
        self.save_comment_button.clicked.connect(self.save_comment)

        # Initialize the list of images and the current page index
        self.images = []
        self.current_page = 0
        self.pages_displayed = 2  # Initialize pages_displayed attribute

        self.cols = 2  # Initialize columns attribute
        self.rows = 2  # Initialize rows attribute

        # Create next and previous page buttons
        self.next_page_button = QPushButton("Next Page", self)
        self.next_page_button.clicked.connect(self.next_page)
        self.prev_page_button = QPushButton("Previous Page", self)
        self.prev_page_button.clicked.connect(self.previous_page)

        # Extract text button
        self.extract_text_button = QPushButton("Extract Text from Images", self)
        self.extract_text_button.clicked.connect(self.extract_text_from_images)

        # Create zoom in and zoom out buttons
        self.zoom_in_button = QPushButton("+", self)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button = QPushButton("-", self)
        self.zoom_out_button.clicked.connect(self.zoom_out)

        # Replace the zoom_combo definition with a QLineEdit
        self.zoom_input = QLineEdit(self)
        self.zoom_input.setText("100%")
        self.zoom_input.setFixedWidth(50)
        self.zoom_input.editingFinished.connect(self.change_zoom)


        # Add zoom buttons and combo box to the layout
        zoom_controls_layout = QHBoxLayout()
        zoom_controls_layout.addWidget(self.zoom_out_button)
        zoom_controls_layout.addWidget(self.zoom_in_button)
        zoom_controls_layout.addWidget(self.zoom_input)

        





        # Set layout
        main_layout = QHBoxLayout()

        pdf_layout = QVBoxLayout()
        pdf_layout.addWidget(self.scroll_area)
        pdf_layout.addWidget(self.prev_page_button)
        pdf_layout.addWidget(self.next_page_button)
        pdf_layout.insertLayout(2, zoom_controls_layout)  # Insert the zoom controls layout below the scroll area

        main_layout.addLayout(pdf_layout)

        comments_layout = QVBoxLayout()
        comments_layout.addWidget(self.comments)
        comments_layout.addWidget(self.save_comment_button)
        comments_layout.addWidget(self.extract_text_button)
        main_layout.addLayout(comments_layout)

        self.setLayout(main_layout)

    def zoom_in(self):
        if self.zoom_level < 5.0:  # Set maximum zoom level to 500%
            self.zoom_level *= 1.1  # Increase zoom level by 10%
            self.update_zoom_text()
            self.display_page()

    def zoom_out(self):
        if self.zoom_level > 0.2:  # Set minimum zoom level to 20%
            self.zoom_level /= 1.1  # Decrease zoom level by 10%
            self.update_zoom_text()
            self.display_page()

    def update_zoom_text(self):
        # Update the text in the QLineEdit
        zoom_percentage = round(self.zoom_level * 100)
        self.zoom_input.blockSignals(True)
        self.zoom_input.setText(f"{zoom_percentage}%")
        self.zoom_input.blockSignals(False)

    def change_zoom(self):
        zoom_text = self.zoom_input.text()
        if not zoom_text.endswith("%"):
            return

        try:
            zoom_percentage = int(zoom_text.strip("%"))
            if 20 <= zoom_percentage <= 500:
                self.zoom_level = zoom_percentage / 100
                self.display_page()
            else:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid Zoom Value", "Please enter a valid zoom value between 20% and 500%.")
            self.update_zoom_text()




    def zoom(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def find_text_bounding_box(self, image):
        image_gray = image.convert('L')
        image_bw = image_gray.point(lambda x: 0 if x < 128 else 255, '1')
        image_bbox = ImageChops.invert(image_bw).getbbox()
        return image_bbox

    
    def extract_text_from_images(self):
        if not self.images:
            return

        extracted_text = ""
        for i in range(self.current_page, min(self.current_page + self.pages_displayed, len(self.images))):
            image = self.images[i]
            text = extract_text_from_image(image)
            extracted_text += text + "\n--- Page break ---\n"

        # Create a QMessageBox with a QPlainTextEdit widget
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Extracted Text")

        plain_text_edit = QPlainTextEdit()
        plain_text_edit.setPlainText(extracted_text)
        plain_text_edit.setReadOnly(True)
        plain_text_edit.setFixedSize(600, 400)  # Set the size of the widget

        msg_box.layout().addWidget(plain_text_edit, 0, QMessageBox.ActionRole)
        msg_box.exec_()

    def extract_text_from_image(image):
        text = pytesseract.image_to_string(image)
        return text


        
    def next_page(self):
        if self.current_page < len(self.images) - self.pages_displayed:
            self.current_page += self.pages_displayed
            self.zoom_level = 1.0  # Reset the zoom level
            self.display_page()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= self.pages_displayed
            if self.current_page < 0:
                self.current_page = 0
            self.zoom_level = 1.0  # Reset the zoom level
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
        self.view.setBackgroundBrush(QColor(200, 200, 200))

        if not self.images:
            self.scene.clear()
            return

        combined_img = None

        if self.mode == "single":
            for i in range(self.current_page, min(self.current_page + self.pages_displayed, len(self.images))):
                img = self.images[i]
                

                if combined_img is None:
                    combined_img = img
                else:
                    combined_img = self.concatenate_images_vertically(combined_img, img)
        elif self.mode == "book":
            for i in range(self.current_page, min(self.current_page + self.pages_displayed, len(self.images)), 2):
                img = self.images[i]
                if i + 1 < len(self.images):
                    img = self.concatenate_images(img, self.images[i + 1])

                if combined_img is None:
                    combined_img = img
                else:
                    combined_img = self.concatenate_images_vertically(combined_img, img)

        combined_qimage = ImageQt(combined_img.convert("RGBA"))

        # Resize the image to fit the label widget and apply the zoom level
        view_size = self.view.size()
        scaled_image_size = combined_qimage.size().scaled(view_size * self.zoom_level, Qt.KeepAspectRatio)
        scaled_image = combined_qimage.scaled(scaled_image_size, Qt.KeepAspectRatio)

        # Convert the image to a pixmap
        pixmap = QPixmap.fromImage(scaled_image)

        # Clear the QGraphicsScene and add the QPixmap to the QGraphicsScene
        self.scene.clear()
        pixmap_item = self.scene.addPixmap(pixmap)

        # Update the QGraphicsView's viewport
        self.view.setSceneRect(pixmap_item.boundingRect())

        h_space = max(0, (self.scroll_area.width() - pixmap.width()) // 2)
        v_space = max(0, (self.scroll_area.height() - pixmap.height()) // 2)
        self.view.setViewportMargins(0, v_space, 0, v_space) 

        # Set the background color of the QGraphicsView to a light gray
        self.view.setBackgroundBrush(QColor(240, 240, 240))  # Add this line
        self.view.setRenderHint(QPainter.Antialiasing)  # Add this line


    def remove_white_margins(image):
        return ImageOps.crop(image, border=1)  # border=1 removes a 1-pixel wide border from all sides



    def set_mode(self, mode):
        if mode in ["single", "book"]:
            self.mode = mode
            self.display_page()

    def concatenate_images(self, img1, img2):
        gap = 5  # Define the gap size
        combined_image = Image.new(
            "RGBA",
            (img1.width + img2.width + gap, max(img1.height, img2.height)),
        )
        combined_image.paste(img1, (0, 0))
        combined_image.paste(img2, (img1.width + gap, 0))
        return combined_image

    def concatenate_images_vertically(self, img1, img2):
        gap = 5  # Define the gap size
        max_width = max(img1.width, img2.width)
        combined_image = Image.new(
            "RGBA",
            (max_width, img1.height + img2.height + gap),
        )
        combined_image.paste(img1, ((max_width - img1.width) // 2, 0))
        combined_image.paste(img2, ((max_width - img2.width) // 2, img1.height + gap))
        return combined_image


    def resizeEvent(self, event):
        # Call the base class method
        super().resizeEvent(event)

        # Update the size of the displayed image
        self.display_page()

    

    def increase_pages_displayed(self):
        if self.mode == "single":
            self.pages_displayed += 1
        elif self.mode == "book":
            self.cols += 1
            self.pages_displayed = self.cols * self.rows
        self.display_page()

    def decrease_pages_displayed(self):
        if self.pages_displayed > 1:
            if self.mode == "single":
                self.pages_displayed -= 1
            elif self.mode == "book":
                self.cols -= 1
                self.pages_displayed = self.cols * self.rows
            self.display_page()

    