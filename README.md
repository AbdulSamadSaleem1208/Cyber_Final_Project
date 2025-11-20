Alright — here’s a **clean, professional, university-safe README** written exactly for your project structure and tools.

You can copy-paste this into your **README.md** directly.

---

# **Cyber Security Multi-Tool (Educational Pentesting Toolkit)**

A modular Python toolkit built for **authorized security assessments**, **university labs**, and **CTF-style environments**.
This project contains multiple tools combined into a single framework, along with evidence logging and a Streamlit GUI.

---

## 🚨 **Legal & Ethical Notice**

This toolkit is built **strictly for educational use** under **written authorization** from instructors.
Do **NOT** use it on real systems, networks, or organizations without explicit legal permission.

---

## 📦 **Features**

### 🔍 **1. Port Scanner**

* Fast TCP scanning
* Custom port ranges (`--ports 1-2000`)
* Saves JSON reports
* Logs all activity in `/evidence/`

### 🌐 **2. Footprinting Tool**

* Basic domain recon
* Extracts subdomains, IPs, and headers
* Saves structured JSON evidence

### 📡 **3. Packet Capture (PCAP)**

* Uses **Npcap** on Windows
* Captures live packets (`--capture <seconds>`)
* Saves `.pcap` file into evidence

### 🔐 **4. Hash Authentication Tester**

* Secure password hashing
* Verifies user-entered passwords
* SHA-256 log files saved automatically

### 💣 **5. Stress Test Tool**

* Safe HTTP load generation
* Suitable for **local lab hosts only**

### 📝 **6. Automated Reporting**

* Generates report manifests
* SHA-256 integrity files
* Creates complete evidence bundles

### 🎛️ **7. Streamlit GUI**

Run everything visually:

```
streamlit run streamlit_app.py
```

---

## 🗂 **Project Structure**

```
Cyber_Final_Project/
│
├── src/
│   ├── scanner.py
│   ├── footprint.py
│   ├── stress.py
│   ├── pcap.py
│   ├── reporting.py
│   ├── auth_test.py
│   ├── logger.py
│   ├── config.py
│   └── evidence/
│
├── evidence/         # Logs, json reports, pcap, screenshots
├── streamlit_app.py  # GUI frontend
├── requirements.txt
├── consent.txt       # Written scope / approved targets
├── identity.txt      # Student details
└── README.md
```

---

## ⚙️ **Installation**

### 1️⃣ Create Virtual Environment

```
python -m venv venv
```

### 2️⃣ Activate venv

**Windows:**

```
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Install Npcap (for packet capture)

Download from:
[https://npcap.com](https://npcap.com)
Select: **WinPcap API-compatible Mode**

---

## ▶️ **Running Tools**

### 📌 Port Scanner

```
python src/scanner.py --target 127.0.0.1 --ports 1-2000
```

### 📌 Footprint Tool

```
python src/footprint.py --domain example.com
```

### 📌 Packet Capture

```
python src/pcap.py --capture 5
```

### 📌 Stress Test

```
python src/stress.py --url http://127.0.0.1:8000 --threads 5
```

### 📌 Authentication Test

```
python src/auth_test.py
```

### 📌 Streamlit GUI

```
streamlit run streamlit_app.py
```

---

## 🧾 Evidence Storage

All logs, JSON files, screenshots, hashes, pcaps, and reports are saved in:

```
/evidence/
```

Every run generates timestamped SHA-256 integrity files.

---

## 🤝 Credits

* Built by **Abdul Samad, Izza-Asif and Hashir-Jafry**
* Supervised by **Dr. Usama Arshad**
* Submitted for **University Cyber Security Final Project (2025)**

---


✅ a shorter README
Just tell me!
