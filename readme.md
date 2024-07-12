# Video Downloader

Video Downloader is a Python-based desktop application that allows users to download videos from various online platforms using a simple graphical interface.

## Features

- User-friendly GUI for easy video downloading
- Support for multiple video URLs
- Customizable download path
- Real-time terminal output display
- Automatic cleanup of unwanted files
- Cross-platform compatibility (Windows, macOS, Linux)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository or download the source code:
   ```
   git clone https://github.com/yourusername/video-downloader.git
   cd video-downloader
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the Video Downloader application:

1. Navigate to the project directory in your terminal.
2. Run the following command:
   ```
   python main.py
   ```

3. The application window will open. Here's how to use it:
   - Enter the download path or use the "Browse" button to select a folder.
   - Enter one or more video URLs in the text area, each on a new line.
   - Click the "Download" button to start the download process.
   - The terminal output area will display the download progress and any messages.

## Project Structure

- `main.py`: The entry point of the application.
- `gui.py`: Contains the GUI setup and event handling.
- `downloader.py`: Handles the video downloading logic and file management.

## Dependencies

- tkinter: For the graphical user interface
- yt-dlp: For video downloading capabilities
- aria2c: As an external downloader for improved download speeds
- colorlog: For colored logging output

## Contributing

Contributions to the Video Downloader project are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the yt-dlp project for providing the core downloading functionality.
- Inspiration for this project came from the need for a simple, user-friendly video downloader.