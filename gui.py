import sys
import os
import cv2
from PySide6.QtGui import QImage, QPixmap, QAction
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtWidgets import QApplication, QLabel, QRubberBand, QMainWindow, QFileDialog, QMenu


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image = None

        # Cria uma janela principal com um rótulo para exibir a imagem
        self.setWindowTitle('JairView')
        self.label = QLabel(self)
        self.setCentralWidget(self.label)
        self.resize(800, 600)
        self.statusBar = self.statusBar()
        self.dimensionLabel = QLabel()
        self.statusBar.addPermanentWidget(self.dimensionLabel)

        # Conecta sinais de teclas de seta ao método de navegação de imagem
        self.keyPressEvent = self.navigate_image

        # Cria o MenuBar
        self._createMenuBar()
        self.crop_rect = QRect()
        self.mouse_pos = QPoint()

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.label)

    def _createMenuBar(self):
        menuBar = self.menuBar()

        # File Menu
        file_menu = menuBar.addMenu(
            "&Arquivo")

        open_menu = file_menu.addMenu('Abrir...')

        open_dir_action = QAction('Abrir Diretório', self)
        open_dir_action.triggered.connect(self.open_directory)
        open_menu.addAction(open_dir_action)

        open_pic_action = QAction('Abrir Imagem', self)
        open_pic_action.triggered.connect(self.open_image)
        open_menu.addAction(open_pic_action)

        file_menu.addSeparator()

        exit_action = QAction('Sair', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Crop Button
        crop_action = QAction('Crop', self)
        crop_action.triggered.connect(self.start_cropping)

        # Add menus to menu bar
        menuBar.addMenu(file_menu)
        menuBar.addAction(crop_action)

    def start_cropping(self):
        img_area = self.label.pixmap().rect()
        img_area.moveCenter(self.label.rect().center())
        self.rubber_band.setGeometry(img_area)
        self.rubber_band.setStyleSheet(
            "border: 3px solid black; background-color: rgba(0,0,0,0)")

        self.rubber_band.show()

    def open_directory(self):
        # Abre um diálogo para selecionar um diretório
        dir_name = QFileDialog.getExistingDirectory(self, 'Abrir Diretório')

        # Carrega todas as imagens do diretório e armazena em uma lista
        if dir_name:
            self.image_files = [os.path.join(dir_name, f) for f in os.listdir(dir_name)
                                if os.path.isfile(os.path.join(dir_name, f))
                                and f.lower().endswith(('.png', '.jpeg', '.jpg', '.bmp'))]
            if not self.image_files:
                self.label.setText('Nenhuma imagem encontrada no diretório')
                self.label.setAlignment(Qt.AlignCenter)
                self.current_index = -1
            else:
                self.current_index = 0
                self.show_image(self.current_index)

    def open_image(self):
        # Abre um diálogo para selecionar uma imagem
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Abrir Imagem', '', 'Imagens (*.png *.jpeg *.jpg *.bmp)')

        # Carrega a imagem e exibe na interface
        if file_name:
            self.image_files = [file_name]
            self.current_index = 0
            self.show_image(self.current_index)

    def update_rubberband(self):
        img_area = self.label.pixmap().rect()
        img_area.moveCenter(self.label.rect().center())
        self.rubber_band.setGeometry(img_area)

    def show_image(self, index):
        # Exibe a imagem na posição especificada na lista de imagens
        if index < 0:
            index = 0
        elif index >= len(self.image_files):
            index = len(self.image_files) - 1
        self.current_index = index
        image_file = self.image_files[self.current_index]
        self.current_image = cv2.imread(image_file, cv2.IMREAD_COLOR)

        if self.current_image is None:
            self.label.setText('Erro ao carregar imagem')
        else:
            # Atualiza barra de status com as dimensões da imagem
            img_height, img_width, img_dim = self.current_image.shape
            bytes_per_line = img_dim * img_width
            qimage = QImage(self.current_image.data,
                            img_width,
                            img_height,
                            bytes_per_line,
                            QImage.Format.Format_RGB888)
            self.pixmap = QPixmap.fromImage(qimage)
            self.label.setPixmap(self.pixmap)

            self.update_rubberband()

            # Centraliza a imagem na interface
            self.label.setAlignment(Qt.AlignCenter)
            self.setWindowTitle(f'JairView - {os.path.basename(image_file)}')

            self.dimensionLabel.setText(
                f'Width: {img_width}, Height: {img_height}, Channels: {img_dim}')

    def navigate_image(self, event):
        # Navega para a imagem anterior ou próxima ao pressionar as setas do teclado
        self.rubber_band.destroy()

        if event.key() == Qt.Key_Left:
            self.show_image(self.current_index - 1)
        elif event.key() == Qt.Key_Right:
            self.show_image(self.current_index + 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec())
