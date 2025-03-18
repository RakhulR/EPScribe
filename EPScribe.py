import os
import subprocess
import threading
import shutil
import concurrent.futures
from pathlib import Path
import cairosvg

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QRadioButton, QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QMessageBox, QButtonGroup
)
from PyQt5.QtCore import QObject, pyqtSignal

def get_ghostscript_path():
    # If running from a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # prioritize sytem ghostscript
        gs_path = shutil.which('gs')
        if gs_path is not None:
            return gs_path
        else:
            return os.path.join(sys._MEIPASS, 'ghostscript', 'gswin64c.exe')
    else:
        # If running as a regular Python script
        return shutil.which('gs')
        # return r"D:\Ghostscript\App\bin\gswin64c.exe"
        # return str(Path(os.path.join('.', 'ghostscript', 'gswin64c.exe')).absolute())
    
class LogEmitter(QObject):
    log_signal = pyqtSignal(str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPScribe")
        self.logEmitter = LogEmitter()
        self.logEmitter.log_signal.connect(self.append_log)
        self.initUI()

    def initUI(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Conversion Type
        conv_layout = QHBoxLayout()
        conv_label = QLabel("Conversion Type:")
        self.conv_combo = QComboBox()
        self.conv_combo.addItems(["SVG to EPS", "EPS to PDF"])
        conv_layout.addWidget(conv_label)
        conv_layout.addWidget(self.conv_combo)
        layout.addLayout(conv_layout)

        # Input Mode (File or Directory)
        input_mode_layout = QHBoxLayout()
        input_mode_label = QLabel("Input Mode:")
        self.input_file_radio = QRadioButton("File")
        self.input_file_radio.setChecked(True)
        self.input_dir_radio = QRadioButton("Directory")
        self.input_mode_group = QButtonGroup(self)
        self.input_mode_group.addButton(self.input_file_radio)
        self.input_mode_group.addButton(self.input_dir_radio)
        # Connect toggled signals to update output mode accordingly
        self.input_file_radio.toggled.connect(self.update_output_mode_state)
        self.input_dir_radio.toggled.connect(self.update_output_mode_state)
        input_mode_layout.addWidget(input_mode_label)
        input_mode_layout.addWidget(self.input_file_radio)
        input_mode_layout.addWidget(self.input_dir_radio)
        layout.addLayout(input_mode_layout)

        # Input Path
        input_path_layout = QHBoxLayout()
        input_path_label = QLabel("Input Path:")
        self.input_line = QLineEdit()
        self.input_browse_button = QPushButton("Browse")
        self.input_browse_button.clicked.connect(self.browse_input)
        input_path_layout.addWidget(input_path_label)
        input_path_layout.addWidget(self.input_line)
        input_path_layout.addWidget(self.input_browse_button)
        layout.addLayout(input_path_layout)

        # Output Mode (File or Directory)
        output_mode_layout = QHBoxLayout()
        output_mode_label = QLabel("Output Mode:")
        self.output_file_radio = QRadioButton("File")
        self.output_file_radio.setChecked(True)
        self.output_dir_radio = QRadioButton("Directory")
        self.output_mode_group = QButtonGroup(self)
        self.output_mode_group.addButton(self.output_file_radio)
        self.output_mode_group.addButton(self.output_dir_radio)
        output_mode_layout.addWidget(output_mode_label)
        output_mode_layout.addWidget(self.output_file_radio)
        output_mode_layout.addWidget(self.output_dir_radio)
        layout.addLayout(output_mode_layout)

        # Output Path
        output_path_layout = QHBoxLayout()
        output_path_label = QLabel("Output Path:")
        self.output_line = QLineEdit()
        self.output_browse_button = QPushButton("Browse")
        self.output_browse_button.clicked.connect(self.browse_output)
        output_path_layout.addWidget(output_path_label)
        output_path_layout.addWidget(self.output_line)
        output_path_layout.addWidget(self.output_browse_button)
        layout.addLayout(output_path_layout)

        # Parallel Processes
        parallel_layout = QHBoxLayout()
        parallel_label = QLabel("Parallel Processes:")
        self.parallel_line = QLineEdit(str(os.cpu_count() or 1))
        parallel_layout.addWidget(parallel_label)
        parallel_layout.addWidget(self.parallel_line)
        layout.addLayout(parallel_layout)

        # Convert Button
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_button)

        # Log Display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

    def update_output_mode_state(self):
        # When input mode is Directory, force output mode to Directory
        if self.input_dir_radio.isChecked():
            self.output_file_radio.setEnabled(False)
            self.output_dir_radio.setChecked(True)
        else:
            self.output_file_radio.setEnabled(True)

    def browse_input(self):
        if self.input_file_radio.isChecked():
            conv_type = self.conv_combo.currentText()
            if conv_type == "SVG to EPS":
                filter_str = "SVG Files (*.svg);;All Files (*)"
            else:
                filter_str = "EPS Files (*.eps);;All Files (*)"
            path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", filter_str)
        else:
            path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if path:
            self.input_line.setText(path)

    def browse_output(self):
        # If input mode is Directory, output must be a directory.
        if self.input_dir_radio.isChecked():
            path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        else:
            # If input is a file, let user choose file or directory based on output mode radio.
            if self.output_file_radio.isChecked():
                conv_type = self.conv_combo.currentText()
                if conv_type == "SVG to EPS":
                    default_ext = ".eps"
                    filter_str = "EPS Files (*" + default_ext + ");;All Files (*)"
                else:
                    default_ext = ".pdf"
                    filter_str = "PDF Files (*" + default_ext + ");;All Files (*)"
                path, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", filter_str)
            else:
                path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_line.setText(path)

    def append_log(self, message):
        self.log_text.append(message)

    def process_file(self, file: Path, dest_file: Path, conversion_type: str):
        base_msg = f"Converting {file.name} -> {dest_file.name}: "
        if conversion_type == "SVG to EPS":
            try:
                cairosvg.svg2eps(url=str(file), write_to=str(dest_file))
                return True, base_msg + "Conversion successful."
            except Exception as e:
                return False, base_msg + f"Error: {str(e)}"
        else:
            try:
                epstopdf_exe = shutil.which("epstopdf")
                if epstopdf_exe is not None:
                    subprocess.run([epstopdf_exe, str(file), f"--outfile={str(dest_file)}"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    gs_exe = get_ghostscript_path()
                    if gs_exe is not None:
                        subprocess.run([gs_exe, "-dNOPAUSE", "-dBATCH", "-dEPSCrop", "-sDEVICE=pdfwrite",
                                        f"-sOutputFile={str(dest_file)}", str(file)], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        return False, base_msg + "Neither Ghostscript (gs) nor epstopdf is available."
                return True, base_msg + "Conversion successful."
            except Exception as e:
                return False, base_msg + f"Error: {str(e)}"

    def start_conversion(self):
        self.log_text.clear()
        input_path_str = self.input_line.text().strip()
        output_path_str = self.output_line.text().strip()

        if not input_path_str or not output_path_str:
            QMessageBox.critical(self, "Error", "Please specify both input and output paths.")
            return

        input_path = Path(input_path_str)
        conversion_type = self.conv_combo.currentText()
        input_mode = "Directory" if self.input_dir_radio.isChecked() else "File"
        # If input is a directory, force output mode to directory.
        if input_mode == "Directory":
            output_mode = "Directory"
        else:
            output_mode = "Directory" if self.output_dir_radio.isChecked() else "File"

        if not input_path.exists():
            QMessageBox.critical(self, "Error", f"Input path '{input_path}' does not exist.")
            return

        output_path = Path(output_path_str)
        if output_mode == "Directory":
            if not output_path.exists():
                try:
                    output_path.mkdir(parents=True, exist_ok=True)
                    self.logEmitter.log_signal.emit(f"Output directory created: {output_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not create output directory: {e}")
                    return
        else:
            if not output_path.parent.exists():
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    self.logEmitter.log_signal.emit(f"Output file directory created: {output_path.parent}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not create output file directory: {e}")
                    return

        self.convert_button.setEnabled(False)

        def conversion_task():
            try:
                if input_mode == "Directory":
                    if conversion_type == "SVG to EPS":
                        file_ext = ".svg"
                        new_ext = ".eps"
                    else:
                        file_ext = ".eps"
                        new_ext = ".pdf"
                    files = [f for f in input_path.glob(f"*{file_ext}") if f.is_file()]
                    if not files:
                        self.logEmitter.log_signal.emit(f"No '{file_ext}' files found in '{input_path}'.")
                        return

                    total = len(files)
                    success_count = 0
                    try:
                        max_workers = int(self.parallel_line.text())
                    except Exception:
                        max_workers = os.cpu_count() or 1

                    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                        future_to_file = {
                            executor.submit(self.process_file, file, output_path / (file.stem + new_ext), conversion_type): file
                            for file in files
                        }
                        for future in concurrent.futures.as_completed(future_to_file):
                            try:
                                success, msg = future.result()
                            except Exception as exc:
                                success = False
                                msg = f"Unexpected error: {exc}"
                            if success:
                                success_count += 1
                            self.logEmitter.log_signal.emit(msg)
                    self.logEmitter.log_signal.emit(f"\nProcess complete: {success_count}/{total} conversions successful.")
                else:
                    # In file mode, if output is a directory, use input file's stem + new extension.
                    if conversion_type == "SVG to EPS":
                        dest_file = (output_path / (input_path.stem + ".eps")) if output_mode == "Directory" else output_path
                    else:
                        dest_file = (output_path / (input_path.stem + ".pdf")) if output_mode == "Directory" else output_path
                    success, msg = self.process_file(input_path, dest_file, conversion_type)
                    self.logEmitter.log_signal.emit(msg)
            finally:
                self.convert_button.setEnabled(True)

        threading.Thread(target=conversion_task, daemon=True).start()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec_())
