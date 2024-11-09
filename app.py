import os
import sys
import config
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QFileDialog, QWidget, QRadioButton, QButtonGroup, QHBoxLayout, QFrame, QTextEdit
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from main import main, is_connected

class Rx2GanttApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rx2Gantt - Desktop Application")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f9f9f9;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QPushButton {
                font-size: 14px;
                color: white;
                background-color: #4CAF50;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QRadioButton {
                font-size: 14px;
                color: #333333;
            }
            QTextEdit {
                font-size: 14px;
                color: #333333;
                background-color: #ffffff;
                border: 1px solid #cccccc;
                padding: 8px;
                border-radius: 6px;
            }
        """)

        # Central Widget
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # File and Folder Selection
        self.file_label = QLabel("No file or folder selected")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file_label)

        select_buttons_layout = QHBoxLayout()
        self.select_file_btn = QPushButton("Select File")
        self.select_file_btn.clicked.connect(self.select_file)
        select_buttons_layout.addWidget(self.select_file_btn)

        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        select_buttons_layout.addWidget(self.select_folder_btn)
        self.layout.addLayout(select_buttons_layout)

        # Separator Line
        self.add_separator()

        # Processing Mode Selection
        self.mode_label = QLabel("Select what to generate:")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.mode_label)

        mode_buttons_layout = QHBoxLayout()
        self.gantt_radio = QRadioButton("Gantt Chart Only")
        self.summary_radio = QRadioButton("Summary CSV Only")
        self.both_radio = QRadioButton("Both Gantt Chart and Summary CSV")
        self.both_radio.setChecked(True)  # Default selection

        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.gantt_radio)
        self.mode_group.addButton(self.summary_radio)
        self.mode_group.addButton(self.both_radio)

        mode_buttons_layout.addWidget(self.gantt_radio)
        mode_buttons_layout.addWidget(self.summary_radio)
        mode_buttons_layout.addWidget(self.both_radio)
        self.layout.addLayout(mode_buttons_layout)

        # Separator Line
        self.add_separator()

        # Process Button
        self.process_btn = QPushButton("Process")
        self.process_btn.clicked.connect(self.process_input)
        self.layout.addWidget(self.process_btn)

        # Feedback Panel
        self.feedback_panel = QTextEdit()
        self.feedback_panel.setReadOnly(True)
        self.feedback_panel.setPlaceholderText("Processing feedback will appear here...")
        self.layout.addWidget(self.feedback_panel)

        # Result Buttons
        result_buttons_layout = QHBoxLayout()
        self.view_gantt_btn = QPushButton("View Gantt Chart")
        self.view_gantt_btn.clicked.connect(self.view_gantt_chart)
        self.view_gantt_btn.setEnabled(False)
        result_buttons_layout.addWidget(self.view_gantt_btn)

        self.view_csv_btn = QPushButton("View Summary CSV")
        self.view_csv_btn.clicked.connect(self.view_summary_csv)
        self.view_csv_btn.setEnabled(False)
        result_buttons_layout.addWidget(self.view_csv_btn)
        self.layout.addLayout(result_buttons_layout)

        # Gantt Chart Preview
        self.image_label = QLabel("Gantt chart will appear here after processing.")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Set Central Widget
        self.setCentralWidget(self.central_widget)

        # Initialize Variables
        self.file_path = None
        self.output_gantt_path = None
        self.output_csv_path = None

    def add_separator(self):
        """Adds a horizontal separator line to the layout."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

    def append_feedback(self, message):
        """Append a message to the feedback panel."""
        self.feedback_panel.append(message)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            config.INPUT_PATH = folder_path
            config.MODE = "folder"
            self.file_label.setText(f"Selected Folder: {os.path.basename(folder_path)}")
        else:
            self.file_label.setText("No folder selected")

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            config.INPUT_PATH = file_path
            config.MODE = "single"
            self.file_label.setText(f"Selected File: {os.path.basename(file_path)}")
        else:
            self.file_label.setText("No file selected")

    def process_input(self):
        if not config.INPUT_PATH:
            self.file_label.setText("Please select a file or folder first!")
            return

        # Determine the selected mode
        generate_gantt = self.gantt_radio.isChecked() or self.both_radio.isChecked()
        generate_summary = self.summary_radio.isChecked() or self.both_radio.isChecked()

        try:
            # Check for internet connectivity
            is_online = is_connected()
            mode_message = "Online mode: Drug classifications will be fetched." if is_online else "Offline mode: Generating Gantt chart only."
            self.append_feedback(mode_message)

            # Call the processing logic
            saved_directories = main(generate_gantt=generate_gantt, generate_summary=generate_summary)

            # Show saved directories
            if saved_directories:
                directories_message = "Files were saved in the following directories:\n"
                directories_message += "\n".join(saved_directories)
                self.append_feedback(directories_message)

            # Update UI for single mode
            if config.MODE == "single":
                if generate_gantt:
                    self.output_gantt_path = os.path.join(
                        os.path.dirname(config.INPUT_PATH),
                        "gantt",
                        os.path.basename(config.INPUT_PATH).replace(".pdf", "_gantt.png")
                    )
                    if os.path.exists(self.output_gantt_path):
                        self.view_gantt_btn.setEnabled(True)
                        pixmap = QPixmap(self.output_gantt_path)
                        self.image_label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio))
                    else:
                        self.append_feedback("Gantt chart not found. Check output path.")

                if generate_summary:
                    self.output_csv_path = os.path.join(
                        os.path.dirname(config.INPUT_PATH),
                        "summary",
                        os.path.basename(config.INPUT_PATH).replace(".pdf", "_summary.csv")
                    )
                    if os.path.exists(self.output_csv_path):
                        self.view_csv_btn.setEnabled(True)

            # Update status for folder processing
            if config.MODE == "folder":
                self.image_label.setText("Folder processed successfully. Gantt charts and summaries saved.")

        except Exception as e:
            self.append_feedback(f"Error: {str(e)}")

    def view_gantt_chart(self):
        if self.output_gantt_path and os.path.exists(self.output_gantt_path):
            os.system(f'open "{self.output_gantt_path}"' if sys.platform == "darwin" else f'start "{self.output_gantt_path}"')
        else:
            self.append_feedback("Error: Gantt chart not found!")

    def view_summary_csv(self):
        if self.output_csv_path and os.path.exists(self.output_csv_path):
            os.system(f'open "{self.output_csv_path}"' if sys.platform == "darwin" else f'start "{self.output_csv_path}"')
        else:
            self.append_feedback("Error: Summary CSV not found!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Rx2GanttApp()
    window.show()
    sys.exit(app.exec_())
