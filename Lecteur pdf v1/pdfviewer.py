from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,QMessageBox,QScrollArea,QComboBox,QToolBar,QGraphicsView,QGraphicsScene,QGraphicsTextItem,QAction
from PyQt5.QtGui import QPixmap, QImage,QPainter,QBrush,QColor,QIcon
from PyQt5.QtCore import Qt, pyqtSignal,QPointF,QRectF,QSize
from PIL.ImageQt import ImageQt
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from PIL import Image
from PIL import Image
from PyQt5.QtWidgets import QPushButton,QLineEdit
from PyQt5.QtWidgets import QPlainTextEdit
from PIL import ImageChops,ImageOps
import fitz  # PyMuPDF



class PdfViewer(QWidget):
   

    def __init__(self,main_window):
        super().__init__()
        self.document = None
        self.links = []
        self.main_window = main_window 
        main_window.drop_label.setVisible(False)
        self.mode = "single"  # Default mode is single
        self.zoom_level = 1.0

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
        self.save_comment_button = QPushButton("Enregistrer le commentaire", self)
        self.save_comment_button.clicked.connect(self.save_comment)

        # Initialize the list of images and the current page index
        self.images = []
        self.current_page = 0
        self.pages_displayed = 2  # Initialize pages_displayed attribute

        self.cols = 2  # Initialize columns attribute
        self.rows = 2  # Initialize rows attribute
        
        

        

        

        


        self.extract_current_text_button = QPushButton("Extraire le texte des pages actuelles", self)
        self.extract_current_text_button.clicked.connect(self.extract_text_current_pages)
  

        # Replace the zoom_combo definition with a QLineEdit
        self.zoom_input = QLineEdit(self)
        self.zoom_input.setText("100%")
        self.zoom_input.setFixedWidth(50)
        self.zoom_input.editingFinished.connect(self.change_zoom)

    

      
        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(32, 32))


        toolbar.addAction(QIcon("assets/folder.png"),"Ouvrir", self.open_new_tab)
        toolbar.addSeparator()
        toolbar.addAction(QIcon("assets/single.png"), "Une Page", self.switch_to_single_mode )
        toolbar.addAction(QIcon("assets/book.png"), "Deux Pages", self.switch_to_book_mode)
        toolbar.addSeparator()
        toolbar.addAction(QIcon("assets/plus.png"), "Augmenter les pages affichées", self.increase_pages_displayed)
        toolbar.addAction(QIcon("assets/moins.png"), "Diminuer les pages affichées", self.decrease_pages_displayed)
        toolbar.addSeparator()
        toolbar.addAction(QIcon("assets/uparrow.png"), "Page suivante", self.next_page)
        toolbar.addAction(QIcon("assets/downarrow.png"), "Page précédente", self.previous_page)
        toolbar.addSeparator()
        toolbar.addAction(QIcon("assets/zoom-in.png"), "Agrandir", self.zoom_in)
        toolbar.addAction(QIcon("assets/zoom-out.png"), "Dézoomer", self.zoom_out)
        toolbar.addWidget(self.zoom_input)


        # Set layout
        main_layout = QHBoxLayout()

        pdf_layout = QVBoxLayout()
        pdf_layout.addWidget(toolbar)
        pdf_layout.addWidget(self.scroll_area)


        main_layout.addLayout(pdf_layout)
        

        comments_layout = QVBoxLayout()
        comments_layout.addWidget(self.comments)
        comments_layout.addWidget(self.save_comment_button)
        comments_layout.addWidget(self.extract_current_text_button)

        
        main_layout.addLayout(comments_layout)

        self.setLayout(main_layout)

    

    def open_new_tab(self):
        current_tab_index = self.main_window.tab_widget.currentIndex()
        self.main_window.open_file(tab_index=current_tab_index + 1)



    def switch_to_single_mode(self):
        if self.mode == "book":
            self.mode = "single"
            self.display_page()

    def switch_to_book_mode(self):
        if self.mode == "single":
            self.mode = "book"
            self.display_page()
        

    def zoom_in(self):
        if self.zoom_level < 5.0:  
            self.zoom_level *= 1.1  
            self.update_zoom_text()
            self.display_page()

    def zoom_out(self):
        if self.zoom_level > 0.2:  
            self.zoom_level /= 1.1  
            self.update_zoom_text()
            self.display_page()

    def update_zoom_text(self):
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
            QMessageBox.warning(self, "Valeur de zoom non valide", "Veuillez entrer une valeur de zoom valide entre 20 % et 500 %.")
            self.update_zoom_text()




    def zoom(self, event):
        
        if event.angleDelta().y() > 1:
            self.zoom_in()
        else:
            self.zoom_out()

    def find_text_bounding_box(self, image):
        image_gray = image.convert('L')
        image_bw = image_gray.point(lambda x: 0 if x < 128 else 255, '1')
        image_bbox = ImageChops.invert(image_bw).getbbox()
        return image_bbox


    def extract_text_current_pages(self):
        start_page = self.current_page
        end_page = min(self.current_page + self.pages_displayed, len(self.texts))
        extracted_text = "\n--- Page break ---\n".join(self.texts[start_page:end_page])

        msg_box = QMessageBox()
        msg_box.setWindowTitle("Texte extrait")
        plain_text_edit = QPlainTextEdit()
        plain_text_edit.setPlainText(extracted_text)
        plain_text_edit.setReadOnly(True)
        plain_text_edit.setFixedSize(600, 400)  

        msg_box.layout().addWidget(plain_text_edit, 0, QMessageBox.ActionRole)
        msg_box.exec_()

        
    def next_page(self):
        if self.current_page < len(self.images) - self.pages_displayed:
            self.current_page += self.pages_displayed
            self.zoom_level = 1.0  
            self.display_page()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= self.pages_displayed
            if self.current_page < 0:
                self.current_page = 0
            self.zoom_level = 1.0  
            self.display_page()

    def save_comment(self):
        file_name = self.parent().parent().tabText(self.parent().parent().currentIndex()).replace(".pdf", "_pdf.txt")

        with open(file_name, "w") as file:
            file.write(self.comments.toPlainText())
        msg_box = QMessageBox()
        msg_box.setText("commentaire enregistré.")
        msg_box.exec_()
        self.comments.clear() 

   
    def open_file(self, file_name):
            self.document = fitz.open(file_name)
            num_pages = len(self.document)

            self.images = []
            self.texts = []  
            for page_num in range(0, num_pages):
                page = self.document.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2,2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                self.images.append(img)

                text = page.get_text("text")  
                self.texts.append(text)  

           

            if self.images:
                self.current_page = 0
                self.display_page()

          


    
    def display_page(self):

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

        view_size = self.view.size()
        scaled_image_size = combined_qimage.size().scaled(view_size * self.zoom_level, Qt.KeepAspectRatio)
        scaled_image = combined_qimage.scaled(scaled_image_size, Qt.KeepAspectRatio,Qt.SmoothTransformation)

        pixmap = QPixmap.fromImage(scaled_image)

        self.scene.clear()
        pixmap_item = self.scene.addPixmap(pixmap)

        self.view.setSceneRect(pixmap_item.boundingRect())

        h_space = max(0, (self.scroll_area.width() - pixmap.width()) // 2)
        v_space = max(0, (self.scroll_area.height() - pixmap.height()) // 2)
        self.view.setViewportMargins(0, v_space, 0, v_space) 

        self.view.setBackgroundBrush(QColor(240, 240, 240)) 
        self.view.setRenderHint(QPainter.Antialiasing)  

       


    def remove_white_margins(image):
        return ImageOps.crop(image, border=1)  



    def set_mode(self, mode):
        if mode in ["single", "book"]:
            self.mode = mode
            self.display_page()

    def concatenate_images(self, img1, img2):
        gap = 5  
        combined_image = Image.new(
            "RGBA",
            (img1.width + img2.width + gap, max(img1.height, img2.height)),
        )
        combined_image.paste(img1, (0, 0))
        combined_image.paste(img2, (img1.width + gap, 0))
        return combined_image

    def concatenate_images_vertically(self, img1, img2):
        gap = 5  
        max_width = max(img1.width, img2.width)
        combined_image = Image.new(
            "RGBA",
            (max_width, img1.height + img2.height + gap),
        )
        combined_image.paste(img1, ((max_width - img1.width) // 2, 0))
        combined_image.paste(img2, ((max_width - img2.width) // 2, img1.height + gap))
        return combined_image


    def resizeEvent(self, event):
       
        super().resizeEvent(event)

        
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




