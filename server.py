import http.server
import socketserver
import json
import urllib.parse
import html
import base64
import os
import uuid
import socket

# Store chat messages and images
messages = []
images = {}

# Server settings
HTTP_PORT = 8000

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't actually establish a connection
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

# Custom request handler
class ChatRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif parsed_path.path == '/messages':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(messages).encode())
        elif parsed_path.path == '/poll':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            last_message_id = int(parsed_path.query.split('=')[1])
            new_messages = messages[last_message_id:]
            self.wfile.write(json.dumps(new_messages).encode())
        elif parsed_path.path.startswith('/image/'):
            image_id = parsed_path.path.split('/')[-1]
            if image_id in images:
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()
                self.wfile.write(base64.b64decode(images[image_id]))
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        if self.path == '/send':
            message = json.loads(post_data.decode())
            messages.append(message)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        elif self.path == '/upload':
            data = json.loads(post_data.decode())
            image_data = data['image'].split(',')[1]  # Remove the "data:image/jpeg;base64," part
            image_id = str(uuid.uuid4())
            images[image_id] = image_data
            message = {
                "sender": data['sender'],
                "text": f"[Image] <a href='/image/{image_id}' target='_blank'>Click to view</a>",
                "timestamp": data['timestamp']
            }
            messages.append(message)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "image_id": image_id}).encode())
        else:
            self.send_error(404)

    def get_html(self):
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>chatING</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body, html {
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: 'Courier New', monospace;
            background-color: #000080;
            color: #FFFFFF;
            font-size: 14px;
        }
        #chat-container {
            display: flex;
            flex-direction: column;
            height: 100%;
            max-width: 100%;
            margin: 0 auto;
            border: 2px solid #C0C0C0;
        }
        #chat-header {
            background-color: #000080;
            color: #FFFFFF;
            padding: 10px;
            font-weight: bold;
            border-bottom: 2px solid #C0C0C0;
            font-size: 1.2em;
        }
        #chat-wrapper {
            flex: 1;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }
        #chat {
            padding: 10px;
            background-color: #000000;
            font-size: 1em;
        }
        #input-area {
            display: flex;
            padding: 10px;
            background-color: #000080;
            border-top: 2px solid #C0C0C0;
        }
        #messageInput, button, #imageInput + label {
            background-color: #000000;
            color: #FFFFFF;
            border: 1px solid #C0C0C0;
            padding: 10px;
            font-size: 1em;
        }
        #messageInput {
            flex: 1;
            min-width: 0;
            margin-right: 5px;
        }
        button, #imageInput + label {
            flex: 0 0 auto;
            width: auto;
            min-width: 50px;
            background-color: #C0C0C0;
            color: #000000;
            cursor: pointer;
            white-space: nowrap;
            text-align: center;
        }
        #imageInput {
            display: none;
        }
        .message {
            margin-bottom: 10px;
        }
        .timestamp {
            color: #808080;
        }
        .sender {
            color: #00FF00;
        }
        .text {
            color: #FFFFFF;
        }
        a {
            color: #00FFFF;
        }
        #username-modal {
            display: none;
            position: fixed;
            z-index: 1;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.4);
        }
        .modal-content {
            background-color: #000080;
            margin: 15% auto;
            padding: 20px;
            border: 1px solid #C0C0C0;
            width: 80%;
            max-width: 300px;
        }
        #username-input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            box-sizing: border-box;
        }
        #username-submit {
            width: 100%;
            padding: 10px;
            background-color: #C0C0C0;
            color: #000000;
            border: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="chat-container">
        <div id="chat-header">chatING</div>
        <div id="chat-wrapper">
            <div id="chat"></div>
        </div>
        <div id="input-area">
            <input type="text" id="messageInput" placeholder="Type your message...">
            <input type="file" id="imageInput" accept="image/*">
            <label for="imageInput">IMG</label>
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <div id="username-modal">
        <div class="modal-content">
            <h2>Enter your nickname:</h2>
            <input type="text" id="username-input" placeholder="Your nickname">
            <button id="username-submit">Set Nickname</button>
        </div>
    </div>

    <script>
        const chat = document.getElementById('chat');
        const chatWrapper = document.getElementById('chat-wrapper');
        const messageInput = document.getElementById('messageInput');
        const imageInput = document.getElementById('imageInput');
        const usernameModal = document.getElementById('username-modal');
        const usernameInput = document.getElementById('username-input');
        const usernameSubmit = document.getElementById('username-submit');
        let lastMessageId = -1;
        let username = localStorage.getItem('username');

        function showUsernameModal() {
            usernameModal.style.display = 'block';
        }

        function hideUsernameModal() {
            usernameModal.style.display = 'none';
        }

        function setUsername() {
            const newUsername = usernameInput.value.trim();
            if (newUsername) {
                username = newUsername;
                localStorage.setItem('username', username);
                hideUsernameModal();
                messageInput.focus();
            }
        }

        usernameSubmit.addEventListener('click', setUsername);
        usernameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                setUsername();
            }
        });

        if (!username) {
            showUsernameModal();
        }

        function addMessage(message) {
            const messageElement = document.createElement('div');
            messageElement.className = 'message';
            const time = new Date(message.timestamp);
            const timeStr = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            messageElement.innerHTML = `
                <span class="timestamp">[${timeStr}] </span>
                <span class="sender">&lt;${escapeHtml(message.sender)}&gt;</span>
                <span class="text"> ${message.text}</span>
            `;
            chat.appendChild(messageElement);
            chatWrapper.scrollTop = chatWrapper.scrollHeight;
        }

        function sendMessage() {
            const text = messageInput.value.trim();
            if (text && username) {
                const message = {
                    sender: username,
                    text: text,
                    timestamp: new Date().toISOString()
                };
                fetch('/send', {
                    method: 'POST',
                    body: JSON.stringify(message)
                }).then(() => {
                    messageInput.value = '';
                    messageInput.focus();
                });
            } else if (!username) {
                showUsernameModal();
            }
        }

        function sendImage(file) {
            if (!username) {
                showUsernameModal();
                return;
            }
            const reader = new FileReader();
            reader.onload = function(event) {
                const imageData = event.target.result;
                fetch('/upload', {
                    method: 'POST',
                    body: JSON.stringify({
                        sender: username,
                        image: imageData,
                        timestamp: new Date().toISOString()
                    })
                }).then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') {
                        console.log('Image uploaded successfully');
                    }
                });
            };
            reader.readAsDataURL(file);
        }

        function pollMessages() {
            fetch('/poll?last=' + lastMessageId)
                .then(response => response.json())
                .then(newMessages => {
                    newMessages.forEach(addMessage);
                    if (newMessages.length > 0) {
                        lastMessageId += newMessages.length;
                    }
                    setTimeout(pollMessages, 1000);
                });
        }

        function escapeHtml(unsafe) {
            return unsafe
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }

        // Load initial messages
        fetch('/messages')
            .then(response => response.json())
            .then(messages => {
                messages.forEach(addMessage);
                lastMessageId = messages.length - 1;
                pollMessages();
            });

        // Allow sending message with Enter key
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Handle image selection
        imageInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                sendImage(e.target.files[0]);
            }
        });

        // Set initial focus to message input
        messageInput.focus();

        // Adjust layout when keyboard appears/disappears
        window.addEventListener('resize', function() {
            chatWrapper.style.height = (window.innerHeight - 
                document.getElementById('chat-header').offsetHeight - 
                document.getElementById('input-area').offsetHeight) + 'px';
        });

        // Initial layout adjustment
        window.dispatchEvent(new Event('resize'));
    </script>
</body>
</html>
        '''

# Run the server
def run_server():
    port = HTTP_PORT
    handler = ChatRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server running on port {port}")
        print(f"Share this URL with your friends to join the chat: http://{get_ip_address()}:{HTTP_PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
