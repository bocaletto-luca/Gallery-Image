# Author: Bocaletto Luca
# Gallery Image in Python with GUI Qt6
# Galleria di Immagini in Python con GUI Qt6
# Import delle librerie necessarie
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSlider, QListWidget, QListWidgetItem, QHBoxLayout, QMessageBox
from PySide6.QtGui import QPixmap, QImage, Qt, QTransform, QIcon
from PIL import Image
from pathlib import Path
from PySide6.QtCore import QSize

# Definizione della classe principale dell'applicazione
class ImageGallery(QMainWindow):
    def __init__(self, default_directory):
        super().__init__()

        # Impostazioni della finestra principale
        self.setWindowTitle("Galleria di Immagini")
        self.setGeometry(100, 100, 1024, 768)

        # Inizializzazione delle variabili
        self.image_list = []
        self.current_index = 0

        # Creazione del widget centrale
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principale
        self.layout = QVBoxLayout(self.central_widget)

        # Elemento grafico per l'immagine principale
        self.image_label = QGraphicsPixmapItem()

        # Vista grafica per l'immagine principale
        self.graphics_view = QGraphicsView(self)
        self.layout.addWidget(self.graphics_view)

        # Scene per l'immagine principale
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.scene.addItem(self.image_label)

        # Layout orizzontale per i pulsanti
        button_layout = QHBoxLayout()

        # Pulsanti per l'immagine
        self.previous_button = QPushButton("Indietro", self)
        self.previous_button.clicked.connect(self.show_previous_image)
        button_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("Avanti", self)
        self.next_button.clicked.connect(self.show_next_image)
        button_layout.addWidget(self.next_button)

        self.browse_button = QPushButton("Sfoglia", self)
        self.browse_button.clicked.connect(self.browse_images)
        button_layout.addWidget(self.browse_button)

        # Pulsante "About"
        self.about_button = QPushButton("About", self)
        self.about_button.clicked.connect(self.show_about_dialog)
        button_layout.addWidget(self.about_button)

        # Barra per lo zoom
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.zoom_image)
        button_layout.addWidget(self.zoom_slider)

        self.layout.addLayout(button_layout)

        # Slide show con miniature
        self.thumbnail_list = QListWidget(self)
        self.thumbnail_list.setMaximumHeight(220)
        self.thumbnail_list.setViewMode(QListWidget.IconMode)
        self.thumbnail_list.setIconSize(QSize(200, 200))
        self.thumbnail_list.setGridSize(QSize(220, 220))
        self.thumbnail_list.setLayoutMode(QListWidget.Batched)
        self.thumbnail_list.itemClicked.connect(self.thumbnail_clicked)
        self.layout.addWidget(self.thumbnail_list)

        # Utilizza la directory home come directory di default
        self.load_images_from_directory(default_directory)

    # Funzione per sfogliare le immagini in una directory
    def browse_images(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        dialog = QFileDialog(self, "Scegli una directory con immagini", options=options)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if dialog.exec():
            directory = dialog.selectedFiles()[0]
            self.load_images_from_directory(directory)

    # Funzione per caricare le immagini da una directory
    def load_images_from_directory(self, directory):
        self.image_list = [os.path.join(directory, filename) for filename in os.listdir(directory) if
                           filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]

        # Pulisci la lista delle miniature
        self.thumbnail_list.clear()

        if self.image_list:
            self.current_index = 0
            self.show_image(self.current_index)

            # Aggiungi le miniature alla lista
            for image_path in self.image_list:
                image = Image.open(image_path)
                image = self.rotate_image(image)  # Ruota l'immagine se necessario

                # Crea la miniatura a partire dall'immagine ruotata
                thumbnail = image.copy()
                thumbnail.thumbnail((200, 200), Image.LANCZOS)  # Utilizza LANCZOS per l'antialiasing

                # Converte la miniatura in un formato compatibile con QPixmap
                thumbnail_qimage = self.pillow_to_qimage(thumbnail)
                thumbnail_pixmap = QPixmap.fromImage(thumbnail_qimage)

                item = QListWidgetItem(QIcon(thumbnail_pixmap), "")
                self.thumbnail_list.addItem(item)
        else:
            self.image_label.setPixmap(QPixmap())

    # Funzione per mostrare un'immagine in base all'indice
    def show_image(self, index):
        if 0 <= index < len(self.image_list):
            image_path = self.image_list[index]

            image = Image.open(image_path)
            image = self.rotate_image(image)  # Ruota l'immagine se necessario

            qimage = self.pillow_to_qimage(image)
            pixmap = QPixmap.fromImage(qimage)

            self.image_label.setPixmap(pixmap)
            self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
            self.graphics_view.setScene(self.scene)
            self.graphics_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    # Funzione per ruotare un'immagine in base all'orientamento Exif
    def rotate_image(self, image):
        try:
            exif = image._getexif()
            if exif:
                orientation = exif.get(0x0112)
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass
        return image

    # Funzione per convertire un'immagine da formato Pillow a QImage
    def pillow_to_qimage(self, image):
        if image.mode == "RGB":
            image = image.convert("RGBA")

        width, height = image.size
        image_data = image.tobytes("raw", "RGBA")

        return QImage(image_data, width, height, QImage.Format_RGBA8888)

    # Funzione per mostrare l'immagine precedente
    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image(self.current_index)

    # Funzione per mostrare l'immagine successiva
    def show_next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.show_image(self.current_index)

    # Funzione per gestire lo zoom dell'immagine
    def zoom_image(self):
        zoom_factor = self.zoom_slider.value() / 100.0
        self.graphics_view.setTransform(QTransform.fromScale(zoom_factor, zoom_factor))

    # Funzione per gestire il click su una miniatura
    def thumbnail_clicked(self, item):
        index = self.thumbnail_list.indexFromItem(item).row()
        self.show_image(index)

    # Funzione per mostrare il dialog "About"
    def show_about_dialog(self):
        about_text = "Galleria di Immagini Versione 1.0\n\n" \
                     "Applicazione per visualizzare e sfogliare immagini da una directory.\n" \
                     "Realizzata con Python con GUI Qt6.\n\n" \
                     "2023 Bocaletto Luca Aka Elektronoide"

        QMessageBox.about(self, "About", about_text)

# Blocco principale di esecuzione dell'applicazione
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Utilizza la directory home come directory di default
    default_directory = str(Path.home())

    gallery = ImageGallery(default_directory)
    gallery.show()
    sys.exit(app.exec())
