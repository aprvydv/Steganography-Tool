SteganoPy: A Colorful Python Steganography Tool
A modern Python desktop app to hide text or files inside images, featuring a stylish PyQt5 GUI, drag-and-drop, image previews, and support for multiple popular image formats.

Features
Hide text or any file inside PNG, BMP, JPG, or JPEG images

Extract hidden text or files from stego images

Modern, colorful interface with theme stylesheet

Drag-and-drop image loading and file selection

Carrier image preview and max data capacity display

Progress bar and user-friendly error feedback

Built using PyQt5 and Pillow—runs on all major platforms

Screenshots
(Add screenshots of your app here by drag-dropping images into your README on GitHub, or linking with proper syntax:)

text
![Main Window Screenshot](ui/screenshot1.png)
![Stego Encode Example](ui/screenshot2.png)
Requirements
Python 3.x

PyQt5

Pillow

Install all requirements easily:

text
pip install -r requirements.txt
Usage
Clone this repository

text
git clone https://github.com/your-username/steganography-tool.git
cd steganography-tool
Install dependencies

text
pip install -r requirements.txt
Run the application

text
python main.py
How It Works
Hide text:

Select a cover image (PNG/BMP/JPG).

Choose “Text” mode, type your secret message, and click “Encode & Save.”

Save the resulting image—your message is now hidden inside!

Hide a file:

Select any file with “Choose File to Hide.”

Choose a cover image, switch to “File” mode, then click “Encode & Save.”

Extract hidden data:

Load the potentially stego image.

Click “Decode From Image.”

View or save the extracted text/file.

Project Structure
text
steganography-tool/
│  main.py           # PyQt5 GUI
│  strego.py         # Steganography core logic
│  requirements.txt
│  README.md
│  ui/               # Icons/screenshots (optional)
Customization
Want to change the color theme?
Edit the QSS string in main.py as explained in the code comments.

License
MIT License

Showcase your project: Star, fork, and share your own improvements!
If you have any questions or spot a bug, feel free to open an Issue or submit a Pull Request.