from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QFileDialog, QToolBar, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QTextEdit, QPushButton, QMessageBox, QTabBar,QStatusBar,QComboBox,QLineEdit,QMenu,QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QBrush, QColor,QIcon
from PyQt5.QtCore import QSize, Qt, QRect, QPoint,QEvent
from pdf2image import convert_from_path
from pdf2docx import Converter
from docx2pdf import convert

from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

from PyPDF2 import PdfReader
from PIL import Image
import os
from pdfviewer import PdfViewer
from PIL import Image
from PyQt5.QtWidgets import QPushButton
from PyPDF2 import PdfReader, PdfWriter,PdfMerger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


       
        self.setWindowTitle("Lecteur PDF")

        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(400, 300)

        central_widget = QWidget(self)
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.remove_tab)
        self.tab_widget.setVisible(False)
        central_layout.addWidget(self.tab_widget)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(10) 

        self.open_button = QPushButton(self)
        self.open_button.setIcon(QIcon("assets/folder.png"))
        self.open_button.setIconSize(QSize(50, 50))
        self.open_button.clicked.connect(self.open_file)
        button_layout.addWidget(self.open_button)

        self.drop_label = QLabel(self)
        self.drop_label.setText("ou déposez vos fichiers")
        self.drop_label.setAlignment(Qt.AlignCenter) 
        button_layout.addWidget(self.drop_label)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        central_layout.addWidget(button_widget, alignment=Qt.AlignCenter)

        self.setAcceptDrops(True)

        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("Fichier")
        self.open_action = QAction("Ouvrir Ctrl+O", self)
        self.open_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_action)
        
        self.close_action = QAction("Fermer Tab", self)
        self.close_action.triggered.connect(self.remove_tab)
        self.file_menu.addAction(self.close_action)

        self.quit_action = QAction("Quitter Ctrl+Q", self)
        self.quit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.quit_action)


        self.tools_menu = self.menu_bar.addMenu("Outils")

        convert_to_pdf_menu = QMenu("CONVERTIR EN PDF", self)

        self.word_to_pdf_action = QAction("Convert Word to PDF", self)
        self.word_to_pdf_action.triggered.connect(self.word_to_pdf)
        convert_to_pdf_menu.addAction(self.word_to_pdf_action)

        self.jpg_to_pdf_action = QAction("Convert JPG to PDF", self)
        self.jpg_to_pdf_action.triggered.connect(self.jpg_to_pdf)
        convert_to_pdf_menu.addAction(self.jpg_to_pdf_action)
        self.tools_menu.addMenu(convert_to_pdf_menu)

    

        convert_from_pdf_menu = QMenu("CONVERTIR DEPUIS PDF", self)

        self.pdf_to_jpg_action = QAction("Convert PDF to JPG", self)
        self.pdf_to_jpg_action.triggered.connect(self.pdf_to_jpg)
        convert_from_pdf_menu.addAction(self.pdf_to_jpg_action)

        self.pdf_to_word_action = QAction("Convert PDF to Word", self)
        self.pdf_to_word_action.triggered.connect(self.pdf_to_word)
        convert_from_pdf_menu.addAction(self.pdf_to_word_action)
        self.tools_menu.addMenu(convert_from_pdf_menu)

        self.pdf_to_html_action = QAction("Convert PDF to HTML", self)
        self.pdf_to_html_action.triggered.connect(self.pdf_to_html)
        convert_from_pdf_menu.addAction(self.pdf_to_html_action)
        self.tools_menu.addMenu(convert_from_pdf_menu)

        self.delete_pages_action = QAction("Supprimer les pages", self)
        self.delete_pages_action.triggered.connect(self.delete_pages)
        self.tools_menu.addAction(self.delete_pages_action)

        self.split_pages_action = QAction("Diviser les pages", self)
        self.split_pages_action.triggered.connect(self.split_pages)
        self.tools_menu.addAction(self.split_pages_action)

        self.merge_pdf_action = QAction("Fusionner les PDF", self)
        self.merge_pdf_action.triggered.connect(self.merge_pdf)
        self.tools_menu.addAction(self.merge_pdf_action)
        

        
        self.view_menu = self.menu_bar.addMenu("Vue")
        self.single_view_action = QAction('Une Page', self)
        self.single_view_action.triggered.connect(lambda: self.switch_to_single_mode())
        self.view_menu.addAction(self.single_view_action)

        self.book_view_action = QAction('Deux Pages', self)
        self.book_view_action.triggered.connect(lambda: self.switch_to_book_mode())
        self.view_menu.addAction(self.book_view_action)

        self.help_menu = self.menu_bar.addMenu("Aide")
        self.help_action = QAction("Raccourcis clavier", self)
        self.help_action.triggered.connect(self.display_keybinds)
        self.help_menu.addAction(self.help_action)


    def merge_pdf(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if file_dialog.exec_():
            file_names = file_dialog.selectedFiles()

            merger = PdfMerger()

            for file_name in file_names:
                merger.append(file_name)

            output_file = "merged.pdf"

            with open(output_file, "wb") as output_pdf:
                merger.write(output_pdf)

            msg_box = QMessageBox()
            msg_box.setText("Fusion terminée")
            msg_box.exec_()

    def split_pages(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]

            page_numbers, ok = QInputDialog.getText(
                self,
                "Diviser les pages",
                "Entrez le numéro de la page ou les pages à diviser (par ex. '2' ou '2-4'):"
            )
            if ok:
                pdf_file = PdfReader(file_name)

                output = PdfWriter()

                page_numbers_to_extract = self.parse_page_numbers(page_numbers)

                for i in range(len(pdf_file.pages)):
                    if (i + 1) in page_numbers_to_extract:
                        output.add_page(pdf_file.pages[i])
                        new_file_name = os.path.splitext(file_name)[0] + f"_{i+1}.pdf"
                        with open(new_file_name, "wb") as output_pdf:
                            output.write(output_pdf)
                        
                msg_box = QMessageBox()
                msg_box.setText("Extraction terminée")
                msg_box.exec_()


    def delete_pages(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]

            page_numbers, ok = QInputDialog.getText(
                self,
                "Supprimer les pages",
                "Entrez le numéro de la page ou les pages à supprimer (par ex. '2' ou '2-4'):"
            )

            if ok:
                pdf_file = PdfReader(file_name)

                output = PdfWriter()

                page_numbers_to_delete = self.parse_page_numbers(page_numbers)

                for i in range(len(pdf_file.pages)):
                    if (i + 1) not in page_numbers_to_delete:
                        output.add_page(pdf_file.pages[i])

                new_file_name = os.path.splitext(file_name)[0] + "_modified.pdf"
                with open(new_file_name, "wb") as output_pdf:
                    output.write(output_pdf)

                msg_box = QMessageBox()
                msg_box.setText("Suppression terminée")
                msg_box.exec_()

    def parse_page_numbers(self, page_numbers):

        page_numbers_to_delete = set()

        entries = page_numbers.split(",")

        for entry in entries:
            if "-" in entry:
                start, end = entry.split("-")

                page_numbers_to_delete.update(range(int(start), int(end)+1))
            else:
                page_numbers_to_delete.add(int(entry))

        return page_numbers_to_delete


    def pdf_to_html(self):
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("PDF files (*.pdf)")
            file_dialog.setFileMode(QFileDialog.ExistingFile)

            if file_dialog.exec_():
                file_name = file_dialog.selectedFiles()[0]

                

                output_file = f"{os.path.splitext(file_name)[0]}.html"

                laparams = LAParams()
                resource_manager = PDFResourceManager()
                with open(output_file, 'wb') as output:
                    converter = HTMLConverter(resource_manager, output, laparams=laparams)
                    interpreter = PDFPageInterpreter(resource_manager, converter)

                    with open(file_name, 'rb') as pdf_file:
                        for page in PDFPage.get_pages(pdf_file, check_extractable=True):
                            interpreter.process_page(page)

                    converter.close()

                msg_box = QMessageBox()
                msg_box.setText("Conversion terminée")
                msg_box.exec_()

    def word_to_pdf(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Word files (*.docx)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]

            convert(file_name, f"{os.path.splitext(file_name)[0]}.pdf")

            msg_box = QMessageBox()
            msg_box.setText("Conversion terminée")
            msg_box.exec_()


    def jpg_to_pdf(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("JPEG files (*.jpg *.jpeg)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]

            image = Image.open(file_name)

            image.convert('RGB').save(f"{os.path.splitext(file_name)[0]}.pdf")

            msg_box = QMessageBox()
            msg_box.setText("Conversion terminée")
            msg_box.exec_()

    def display_keybinds(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Raccourcis clavier")
        msg_box.setText(
            "Ctrl+O: Ouvrir un fichier\n"
            "Ctrl+U: Augmenter les pages affichées\n"
            "Ctrl+D: Diminuer les pages affichées\n"
            "Ctrl+S: Sauvegarder le commentaire\n"
            "Ctrl+Q: Quitter\n"
            "Ctrl+Shift+U: Augmenter les rangées affichées\n"
            "Ctrl+Shift+D: Diminuer les rangées affichées\n"
            "F11: Page précédente\n"
            "F12: Page suivante\n"
        )
        msg_box.exec_()


    def pdf_to_jpg(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]

            images = convert_from_path(file_name)

            for i, image in enumerate(images):
                image.save(f"{file_name}_{i}.jpg", "JPEG")

            
            msg_box = QMessageBox()
            msg_box.setText("Conversion terminée")
            msg_box.exec_()

    def pdf_to_word(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]

            cv = Converter(file_name)
            cv.convert(f"{os.path.splitext(file_name)[0]}.docx", start=0, end=None)
            cv.close()

            msg_box = QMessageBox()
            msg_box.setText("Conversion terminée")
            msg_box.exec_()

    
    

        


    def switch_to_single_mode(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            current_tab.switch_to_single_mode()

    def switch_to_book_mode(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            current_tab.switch_to_book_mode()


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
      
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.pdf'):
                pdf_viewer = PdfViewer(self)
                pdf_viewer.open_file(file_path)
                self.tab_widget.addTab(pdf_viewer, os.path.basename(file_path))
                self.open_button.setVisible(False)
                self.tab_widget.setVisible(True)
            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setWindowTitle("File type error")
                msg_box.setText(f"The file {os.path.basename(file_path)} is not a PDF.")
                msg_box.exec_()

    def remove_tab(self, index):
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        widget.deleteLater() 



    def open_file(self,tab_index=None):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]

            pdf_viewer = PdfViewer(self)
            pdf_viewer.open_file(file_name)
            if tab_index is None:
                self.tab_widget.addTab(pdf_viewer, os.path.basename(file_name))

            else:
                self.tab_widget.insertTab(tab_index, pdf_viewer, os.path.basename(file_name))
                

            self.open_button.setVisible(False)
            self.tab_widget.setVisible(True)

    


           



    def keyPressEvent(self, event):
        current_tab = self.tab_widget.currentWidget()

        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_U:
                current_tab.increase_pages_displayed()
            elif event.key() == Qt.Key_D:
                current_tab.decrease_pages_displayed()
            elif event.key() == Qt.Key_O:
                self.open_file()
            elif event.key() == Qt.Key_S:  
                current_tab.save_comment() 
            elif event.key() == Qt.Key_Q:
                self.close()
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

        elif event.key() == Qt.Key_F11:
            current_tab.previous_page()
        elif event.key() == Qt.Key_F12:
            current_tab.next_page()





if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

