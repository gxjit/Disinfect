# Disinfect

**Disinfect** is a Python utility to safely disarm and disinfect potentially malicious PDF files using PDFiD and GhostScript.

## Features
* **Disarm:** Safely disable potentially harmful active content (like JavaScript, auto-launch actions, etc.) in a PDF using `pdfid`.
* **Disinfect:** Fully neutralize the PDF by "printing" and downsampling it using `GhostScript`, converting active elements into flat, safe representations.

## Prerequisites
To run this tool, ensure you have the following installed on your system:
* **Python 3.x**
* **GhostScript** (Must be installed and accessible in your system's PATH)

*(Note: `pdfid` is included directly in the repository).*

## Usage

Run the script from the command line by specifying the target directory and your desired action (disarm or disinfect).

```bash
python Disinfect.py [-h] -d DIR (-a | -i)
```

### Arguments:
* `-h, --help`: Show the help message and exit.
* `-d DIR, --dir DIR`: The directory path containing the PDF files you want to process.
* `-a, --disarm`: Disarm the PDF files using `pdfid -d`.
* `-i, --disinfect`: Disinfect the PDF files by printing and downsampling them using GhostScript.

### Examples:

**To disarm all PDFs in a folder:**
```bash
python Disinfect.py -d /path/to/pdf/folder -a
```

**To disinfect all PDFs in a folder:**
```bash
python Disinfect.py -d /path/to/pdf/folder -i
```

## License
This project is licensed under the [MIT License](LICENSE).
