# chatING

chatING is a simple, retro-style chat application that runs on a local network. It allows users to send text messages and images in a shared chat room, providing a nostalgic chatting experience reminiscent of early internet chat rooms.

## Features

- Text messaging
- Image sharing
- Retro-style interface
- Cross-platform compatibility (works on desktop and mobile browsers)
- Local network chat (no internet required)

## Requirements

- Python 3.6 or higher

## Installation

### On Laptop/Desktop

1. Clone this repository:
   ```
   git clone https://github.com/qSharpy/chatING.git
   cd chatING
   ```

2. No additional installation is required if you have Python 3.6+ installed.

### On Android (using Termux)

1. Install Termux from the Google Play Store or F-Droid.

2. Open Termux and install the required packages:
   ```
   pkg install python git
   ```

3. Clone the repository:
   ```
   git clone https://github.com/qSharpy/chatING.git
   cd chatING
   ```

## Usage

### Starting the Server

1. Navigate to the chatING directory.

2. Run the Python script:
   ```
   python server.py
   ```

3. The server will start, and you'll see a message with the URL to access the chat.

### Joining the Chat

1. On the device running the server, open a web browser and go to:
   ```
   http://localhost:8000
   ```

2. On other devices on the same local network, open a web browser and go to:
   ```
   http://<server-ip-address>:8000
   ```
   Replace `<server-ip-address>` with the IP address shown in the server's console output.

3. Enter a nickname when prompted, and start chatting!

## Notes

- The chat is only accessible on your local network. It's not accessible from the internet unless you set up port forwarding (not recommended for security reasons).
- All messages and images are stored in memory and will be lost when the server is stopped.
- This application is intended for educational purposes and local use only. It doesn't implement security features required for public deployment.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Inspired by the classic chat rooms of the early internet era.
- Built with Python and vanilla JavaScript.

Enjoy your retro chatting experience with chatING!
