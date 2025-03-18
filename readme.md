# EPScribe

EPScribe is a simple and efficient GUI-based tool for converting vector image files between SVG to EPS and EPS to PDF formats. Built with PyQt5, it supports both single-file conversion and batch processing from a folder. It work efficiently in case of multiple file using parallel processing.
## Features

* **SVG to EPS** and **EPS to PDF** conversions
* **Parallel Processing** for faster batch conversions
* Intuitive and user-friendly **Graphical Interface**
* Support for both **File Mode** and **Directory Mode**
* Error logging and status messages
* Easily convert SVG files from PowerPoint to EPS for seamless use in TeX projects which helps to conserve the vector properties of the image.

## Requirements

If you're using the `.exe` version, no additional installations are required. Simply download and run the executable.

For Python users, ensure the following are installed:

- Python 3.8+
- PyQt5
- CairoSVG (for SVG to EPS conversion)
- Ghostscript or `epstopdf` (for EPS to PDF conversion)

### Install Required Packages

```bash
pip install pyqt5 cairosvg
```

For the `.exe` version, Ghostscript is bundled, so no additional installation is necessary. Note that `epstopdf` comes with MiKTeX, so ensure it is installed if required. Python users should ensure **Ghostscript** or **epstopdf** is installed and available in your system's `PATH`.

## Usage

### Running the Script (Python)

1. Run the script:
   ```bash
   python EPScribe.py
   ```
2. Select the conversion type: **SVG to EPS** or **EPS to PDF**.

### Running the Executable (Windows)

1. Download the `.exe` file from the releases section.
2. Double-click the executable to launch EPScribe.
3. Follow the same steps for conversion as in the Python version.
   **SVG to EPS** or **EPS to PDF**.
4. Choose the input mode:
   - **File** for single file conversion
   - **Directory** for batch processing
5. Browse and set the input and output paths.
6. Set the number of parallel processes (default is your CPU count).
7. Click **Convert** and monitor progress in the log panel.

### Example: Converting PowerPoint Graphics to EPS for TeX  

1. In PowerPoint, create your desired graphic.  
2. Save the graphic as an **SVG file**:  
   - Go to **File** → **Save As** → Choose **SVG (.svg)** as the format.  
3. Open EPScribe and select **SVG to EPS** conversion.  
4. Choose the saved SVG file as the input.  
5. Select an output directory and click **Convert**.  
6. The resulting EPS file is now ready for use in TeX documents.  


## Troubleshooting

- Ensure `cairosvg` is installed for SVG to EPS conversion.
- Confirm Ghostscript (`gs`) or `epstopdf` is installed for EPS to PDF conversion.
- Provide valid input and output paths.

### For `.exe` Users

- If the application doesn't launch, ensure your antivirus software is not blocking it.
- Check for missing DLLs. Some systems may require installing Microsoft Visual C++ Redistributable.
- Run the executable as an administrator if permission issues occur.

## License

This project is licensed under the MIT License.

## Contribution

Feel free to submit issues and pull requests to improve EPScribe! If you encounter any issues, please report them to help me enhance the experience. free to submit issues and pull requests to improve EPScribe!

