# Installing LaTeX for PDF Generation

HugPDF now uses LaTeX for professional PDF generation. You need to install a TeX distribution on your system.

## Windows Installation

### Option 1: MiKTeX (Recommended for Windows)

1. **Download MiKTeX**:
   - Visit: https://miktex.org/download
   - Download the installer for Windows

2. **Install MiKTeX**:
   - Run the installer
   - Choose "Install MiKTeX for all users" (recommended)
   - Select installation directory (default is fine)
   - Choose "Yes" for "Install missing packages on-the-fly"

3. **Verify Installation**:
   ```powershell
   pdflatex --version
   ```

### Option 2: TeX Live

1. **Download TeX Live**:
   - Visit: https://www.tug.org/texlive/acquire-netinstall.html
   - Download `install-tl-windows.exe`

2. **Install TeX Live**:
   - Run the installer
   - Follow the installation wizard
   - This is a larger installation (~7GB) but more comprehensive

3. **Verify Installation**:
   ```powershell
   pdflatex --version
   ```

## After Installation

1. **Restart your terminal** to ensure the PATH is updated
2. **Restart the backend server** (stop and run `.\start-backend.ps1` again)
3. **Test PDF generation** by creating a document in the app

## Troubleshooting

- If `pdflatex` is not found, add the installation directory to your PATH:
  - MiKTeX: `C:\Program Files\MiKTeX\miktex\bin\x64`
  - TeX Live: `C:\texlive\2024\bin\win64`

- If you get package errors, MiKTeX will automatically download missing packages on first use
