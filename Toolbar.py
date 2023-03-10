import os
from PySide6.QtWidgets import QToolBar, QStyle, QSizePolicy, QMessageBox, QLabel, QSlider, QHBoxLayout, QVBoxLayout, QWidget, QCheckBox, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap, QKeySequence
import cv2
import numpy as np


class FilterToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOrientation(Qt.Vertical)

        self.blocked = True
        # Create HSV sliders
        self.create_buttons()
        self.create_hsv_sliders()
        self.create_persistent_checkbox()

        # Positioning setup
        self.setMovable(False)

    def create_persistent_checkbox(self):
        self.persist_checkbox = QCheckBox('Persist Filter')
        self.persist_checkbox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.persist_checkbox.setStyleSheet(
            "QCheckBox::indicator { subcontrol-origin: left; }")
        self.persist_checkbox.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.addWidget(self.persist_checkbox)

    def create_buttons(self):
        # Delete Button
        btn_delete = QPushButton()
        btn_delete_icon = self.style().standardIcon(QStyle.SP_DialogDiscardButton)

        btn_delete.setIcon(btn_delete_icon)
        btn_delete.setToolTip('Delete image (Del)')
        btn_delete.setStatusTip('Delete image')
        btn_delete.setShortcut(QKeySequence('del'))
        btn_delete.clicked.connect(self.delete_image)
        btn_delete.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Forward Image Button
        self.btn_forwards = QPushButton()
        btn_forwards_icon = self.style().standardIcon(QStyle.SP_ArrowForward)
        self.btn_forwards.setIcon(btn_forwards_icon)
        self.btn_forwards.setToolTip('Next image (Right Arrow)')
        self.btn_forwards.setStatusTip('Next image')
        self.btn_forwards.setShortcut(QKeySequence(Qt.Key_Right))
        self.btn_forwards.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_forwards.clicked.connect(self.next_image)

        # Backward Image Button
        self.btn_backwards = QPushButton()
        btn_backwards_icon = self.style().standardIcon(QStyle.SP_ArrowBack)
        self.btn_backwards.setIcon(btn_backwards_icon)
        self.btn_backwards.setToolTip('Previous image (Left Arrow)')
        self.btn_backwards.setStatusTip('Previous image')
        self.btn_backwards.setShortcut(QKeySequence(Qt.Key_Left))
        self.btn_backwards.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_backwards.clicked.connect(self.prev_image)

        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_delete)
        button_layout.addWidget(self.btn_backwards)
        button_layout.addWidget(self.btn_forwards)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        self.addWidget(button_widget)

    def next_image(self):
        if self.parent().current_index < len(self.parent().image_files) - 1:
            self.parent().current_index = self.parent().current_index + 1
        self.parent().show_image()

    def update_buttons(self):
        num_images = len(self.parent().image_files)
        current_index = self.parent().current_index

        # Disable btn_backward if current index is first image
        if current_index == 0:
            self.btn_backwards.setEnabled(False)
        else:
            self.btn_backwards.setEnabled(True)

        # Disable btn_forward if current index is last image
        if current_index == num_images - 1:
            self.btn_forwards.setEnabled(False)
        else:
            self.btn_forwards.setEnabled(True)

    def prev_image(self):
        if self.parent().current_index >= 0:
            self.parent().current_index = self.parent().current_index - 1
        self.parent().show_image()

    def delete_image(self):
        confirm = QMessageBox.question(
            self, 'Confirmar Deleção', 'Você tem certeza que deseja deletar o arquivo atual?', QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            index = self.parent().current_index
            filepath = self.parent().image_files[index]

            if len(self.parent().image_files) > 1:
                if index == 0:
                    self.next_image()
                    self.parent().current_index = 0
                elif index == len(self.parent().image_files) - 1:
                    self.prev_image()

            else:
                self.parent().current_index = -1

            self.parent().image_files.remove(filepath)
            self.parent().show_image()
            # os.remove(filepath)

            self.update_buttons()

    def create_hsv_sliders(self):
        # Add title to the top of the vertical layout
        title_layout = QHBoxLayout()
        title = QLabel("Hue Saturation Value", self)
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)

        # Create labels for sliders

        self.hue_label = QLabel(f"H: 0")
        self.saturation_label = QLabel("S: 0")
        self.value_label = QLabel("V: 0")

        # Create sliders
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.hue_slider.setRange(0, 179)
        self.hue_slider.setValue(0)

        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.saturation_slider.setRange(0, 255)
        self.saturation_slider.setValue(0)

        self.value_slider = QSlider(Qt.Horizontal)
        self.value_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.value_slider.setRange(0, 255)
        self.value_slider.setValue(0)

        # Connect signals
        self.hue_slider.valueChanged.connect(self.apply_hsv_filter)
        self.saturation_slider.valueChanged.connect(self.apply_hsv_filter)
        self.value_slider.valueChanged.connect(self.apply_hsv_filter)

        self.hue_slider.valueChanged.connect(self.update_slider_labels)
        self.saturation_slider.valueChanged.connect(self.update_slider_labels)
        self.value_slider.valueChanged.connect(self.update_slider_labels)

        # Create layouts for labels and sliders
        hue_layout = QHBoxLayout()
        hue_layout.addWidget(self.hue_label)
        hue_layout.addWidget(self.hue_slider)

        saturation_layout = QHBoxLayout()
        saturation_layout.addWidget(self.saturation_label)
        saturation_layout.addWidget(self.saturation_slider)

        value_layout = QHBoxLayout()
        value_layout.addWidget(self.value_label)
        value_layout.addWidget(self.value_slider)

        # Create widget to hold layouts
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(title_layout)
        layout.addLayout(hue_layout)
        layout.addLayout(saturation_layout)
        layout.addLayout(value_layout)
        widget.setLayout(layout)

        # Add widget to toolbar
        self.addWidget(widget)

    def update_slider_labels(self):
        self.hue_label.setText(f"H: {self.hue_slider.value()}")
        self.saturation_label.setText(f"S: {self.saturation_slider.value()}")
        self.value_label.setText(f"V: {self.value_slider.value()}")

    def reset_sliders(self):
        self.hue_slider.setValue(0)
        self.value_slider.setValue(0)
        self.saturation_slider.setValue(0)

    def apply_hsv_filter(self):
        # Apply the HSV filter to the current image
        if self.parent().current_image is not None:
            hue = self.hue_slider.value()
            saturation = self.saturation_slider.value()
            value = self.value_slider.value()

            hsv_image = cv2.cvtColor(
                self.parent().current_image, cv2.COLOR_BGR2HSV)
            hsv_image[:, :, 0] = (hsv_image[:, :, 0] + hue) % 180
            hsv_image[:, :, 1] = np.clip(
                hsv_image[:, :, 1] + saturation, 0, 255)
            hsv_image[:, :, 2] = np.clip(hsv_image[:, :, 2] + value, 0, 255)

            bgr_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

            # Update the image in the MainWindow
            img_height, img_width, img_dim = bgr_image.shape
            bytes_per_line = img_dim * img_width
            qimage = QImage(bgr_image.data, img_width, img_height,
                            bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            self.parent().label.setPixmap(pixmap)
