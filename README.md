# ESP32 BLE OTA CLI Tool

This project is a **Python-based BLE (Bluetooth Low Energy) OTA (Over-The-Air) firmware update tool** designed for **ESP32 (Espressif SoCs)**.

It allows firmware developers to:

* Upload firmware (`.bin`) files wirelessly
* Update one or multiple ESP32 devices in Single Execution
* Track update history
* Quickly test firmware builds from the terminal

The project is intentionally simple but modular, so it can later grow into:

* An API service (FastAPI)
* A production OTA system

## ⚙️ Installation

### Install all dependencies (recommended)

```bash
pip install -r requirements.txt
```

### Or install manually

```bash
pip install bleak rich PyYAML
```

---

## 📚 Libraries Used

### 1. bleak

* Used for **BLE communication**
* Handles scanning, connecting, reading, and writing GATT characteristics

### 2. rich

* Used for **terminal UI**
* Provides:

  * Progress bars
  * Colored output
  * Tables and summaries

### 3. PyYAML

* Used to **load configuration from YAML files**
* Makes the tool flexible for different firmware setups

---

## 📁 Required Files

### 1. `config.yaml`

Defines firmware and OTA behavior:

```yaml
ota:
  data_uuid: "00008020-0000-1000-8000-xxxxxxx" # Add your data UUID
  control_uuid: "00008022-0000-1000-8000-xxxxxxx" # Add your Control UUID 
  firmware_path: "main.bin" # Add the path of your .bin file
  version: "1.0.0" # Add version for logging

logging:
  history_file: "history.csv"
```

---

### 2. `devices.txt` (optional)

Comma-separated device names:

```
ESP32_A,ESP32_B
```

You can also pass device names directly via CLI (see below).

---

### 3. Firmware File

```
main.bin
```

---

### 4. `history.csv`

Stores OTA logs:

```
timestamp,device_name,version
```

---

## 🖥️ CLI Usage

Run the application using:

```bash
python main.py --config config.yaml --devices <value>
```

---

## 🔹 CLI Commands (Brief)

### 1. Update devices using file

```bash
python main.py --config config.yaml --devices devices.txt
```

---

### 2. Update devices manually

```bash
python main.py --config config.yaml --devices ESP32_A,ESP32_B
```

---

### 3. Update a single device

```bash
python main.py --config config.yaml --devices ESP32_A
```

---

### 4. Override firmware file

```bash
python main.py --config config.yaml --devices devices.txt --firmware test.bin
```

---

### 5. Show last updates (default 5)

```bash
python main.py --config config.yaml --history
```

---

### 6. Show last N updates (max 20)

```bash
python main.py --config config.yaml --history 10
```

---

## 🔁 OTA Workflow

For each device:

1. Scan BLE devices
2. Match device name
3. Connect to ESP32
4. Send OTA request
5. Wait for ACK
6. Transfer firmware in chunks
7. Send completion signal
8. Wait for final ACK
9. Log result

---

## 📊 CLI Output Features

* Live progress bars per device
* Color-coded status:

  * SUCCESS (green)
  * FAILED (red)
  * ERROR (red)
* Summary table after update

---

## ⚠️ Notes

* Device names must match BLE advertised names
* No leading spaces allowed in device names
* OTA protocol must match the ESP32 firmware implementation
* BLE stability affects performance

---


