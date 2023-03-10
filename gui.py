import sys
import os
import cv2
from PySide6.QtGui import QImage, QPixmap, QAction, QIcon
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog

from Toolbar import FilterToolBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_files = []
        self.current_image = None
        self.current_index = 0

        # Cria uma janela principal com um rótulo para exibir a imagem
        self.setWindowTitle('JairView')
        self.label = QLabel(self)
        self.setCentralWidget(self.label)
        self.resize(800, 600)
        self.statusBar = self.statusBar()
        self.dimensionLabel = QLabel()
        self.statusBar.addPermanentWidget(self.dimensionLabel)

        # Cria o MenuBar
        self._createMenuBar()

        # Cria Toolbar Lateral
        self.filter_toolbar = FilterToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.filter_toolbar)
        self.filter_toolbar.setVisible(False)

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

        # Add menus to menu bar
        menuBar.addMenu(file_menu)

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
                self.show_image()
        self.enable_toolbar()

    def open_image(self):
        # Abre um diálogo para selecionar uma imagem
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Abrir Imagem', '', 'Imagens (*.png *.jpeg *.jpg *.bmp)')

        # Carrega a imagem e exibe na interface
        if file_name:
            self.image_files = [file_name]
            self.current_index = 0
            self.show_image()
            self.enable_toolbar()

    def show_image(self):
        # Exibe a imagem na posição especificada na lista de imagens

        if self.current_index == -1:
            self.label.setText('Nenhuma imagem encontrada.')
            return
        elif self.current_index >= len(self.image_files):
            self.current_index = len(self.image_files) - 1

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

            if self.filter_toolbar.persist_checkbox.isChecked():
                self.filter_toolbar.apply_hsv_filter()
            else:
                self.filter_toolbar.reset_sliders()

            # Centraliza a imagem na interface
            self.label.setAlignment(Qt.AlignCenter)
            self.setWindowTitle(
                f'JairView - {os.path.basename(image_file)} = [{self.current_index + 1}/{len(self.image_files)}]')

            self.dimensionLabel.setText(
                f'Width: {img_width}, Height: {img_height}, Channels: {img_dim}')
            self.filter_toolbar.update_buttons()

    def enable_toolbar(self):
        self.filter_toolbar.setVisible(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec())
