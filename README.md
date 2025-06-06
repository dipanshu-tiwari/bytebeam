# 🚀 ByteBeam

**ByteBeam** is a lightweight, blazing-fast CLI tool for **transferring files over a local network**. Whether you're on the same Wi-Fi or LAN, ByteBeam lets you send and receive files securely, without needing the internet or third-party tools.

---

## 🔧 Features

- ⚡ **Fast local transfers** — no cloud, just pure LAN speed
- 🔐 **Secure token-based access control**
- 🧠 **IP Filtering** - capable of recieving from a specific IP
- 🐧 **Linux-first** philosophy, perfect for terminal lovers

---

## 📦 Installation

### 📁 Using `pip`

```bash
pip install bytebeam
```

## 🖥️ Usage

### 📤 Sending a file

```bash
bytebeam -s file.txt -H <Local_IP_of_reciever> -p <port> -t <Auth_token>
```

### 📥 Receiving a file

```bash
bytebeam -r -p <port>
```

### ⚙️ Setting configuration

```bash
bytebeam-config --set-token 1234 --enable-token
```

### More usage

```bash
bytebeam --help
```

or

```bash
bytebeam-config --help
```

## 🔑 Command Line Options

Option	Description

```bash
--send / -s	Path of file to send
--recv / -r	Receive mode
--host / -H	IP address to bind
--port / -p	Port to listen/send
--token / -t Authentication token for secure transfer
--from / -f Only recieve from this IP address
--yes / -y Always accept incomming file
--no-overwrite Never overwite when duplicate of file found
--force Force overwrite when duplicate of file found
```

## 📂 Configuration of token

ByteBeam supports persistent settings to manage auth token on the reciever's end using a config file. This is managed by the bytebeam-config command. Config values are stored in:

```bash
~/.config/bytebeam/config.json
```

## 🙋 Author

    Dipanshu Tiwari
    📧 dipanshutiwari115@gmail.com

## 🪪 License

This project is licensed under the MIT License.
Feel free to use, modify, and distribute.

## 🌐 Coming Soon

    QR Code-based file sharing
    Cross-platform support (Windows/macOS)

Made with 💻 and ☕ in Linux.
