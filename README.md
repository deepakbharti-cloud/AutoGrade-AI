<div align="center">

<img src="assets/banner.svg" alt="AutoGrade AI" width="100%"/>

<br/>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-Backend-092E20?logo=django&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?logo=opencv&logoColor=white)
![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-flan--t5-FFD21E)
![Twilio](https://img.shields.io/badge/Twilio-Notifications-F22F46?logo=twilio&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)

**Upload an answer sheet. Get a graded report. No manual checking.**

[Source Code](https://github.com/deepakbharti-cloud/AutoGrade-AI) · [Report an Issue](https://github.com/deepakbharti-cloud/AutoGrade-AI/issues) · [Developer](#developer)

</div>

---

<div align="center">

### 🧭 Quick Navigation

<sub>Click any button to jump to that section</sub>

<p>
<a href="#overview"><img src="https://img.shields.io/badge/Overview-0ea5e9?style=for-the-badge" alt="Overview"/></a>
<a href="#features"><img src="https://img.shields.io/badge/Features-3b82f6?style=for-the-badge" alt="Features"/></a>
<a href="#how-it-works"><img src="https://img.shields.io/badge/How%20It%20Works-6366f1?style=for-the-badge" alt="How It Works"/></a>
<a href="#workflow"><img src="https://img.shields.io/badge/Workflow-8b5cf6?style=for-the-badge" alt="Workflow"/></a>
<a href="#tech-stack"><img src="https://img.shields.io/badge/Tech%20Stack-a855f7?style=for-the-badge" alt="Tech Stack"/></a>
</p>
<p>
<a href="#getting-started"><img src="https://img.shields.io/badge/Getting%20Started-a855f7?style=for-the-badge" alt="Getting Started"/></a>
<a href="#roadmap"><img src="https://img.shields.io/badge/Roadmap-8b5cf6?style=for-the-badge" alt="Roadmap"/></a>
<a href="#team"><img src="https://img.shields.io/badge/Team-6366f1?style=for-the-badge" alt="Team"/></a>
<a href="#contributing"><img src="https://img.shields.io/badge/Contributing-3b82f6?style=for-the-badge" alt="Contributing"/></a>
<a href="#developer"><img src="https://img.shields.io/badge/Developer-0ea5e9?style=for-the-badge" alt="Developer"/></a>
</p>

</div>

---

<a id="overview"></a>

## 📖 Overview

Grading answer sheets by hand is slow, repetitive and inconsistent from one evaluator to the next. **AutoGrade AI** automates the process. It takes a scanned answer sheet, cleans up the image, reads the text with OCR, evaluates the answers with a language model, and produces a graded PDF report.

It is a team project built with **Django**, with image processing, OCR and NLP working together in one pipeline.

---

<a id="features"></a>

## ✨ Features

| | Feature | What it does |
|---|---|---|
| 🖼️ | **Image preprocessing** | Cleans scanned sheets with OpenCV (noise, contrast, alignment) before text extraction |
| 🔍 | **OCR extraction** | Reads answer text using Tesseract / EasyOCR |
| 🧠 | **AI evaluation** | Scores answers with a HuggingFace flan-t5 model |
| 📄 | **PDF reports** | Generates a result report with ReportLab |
| 📲 | **Notifications** | Sends results through Twilio |
| 🔐 | **Django backend** | Handles uploads, users and result storage |

---

<a id="how-it-works"></a>

## 🔁 How It Works

<div align="center">
<img src="assets/pipeline.svg" alt="AutoGrade AI pipeline" width="100%"/>
</div>

1. **Upload:** the evaluator uploads a scanned answer sheet.
2. **Preprocess:** OpenCV cleans and normalises the image so the text is easier to read.
3. **Extract text:** OCR converts the image into text.
4. **Evaluate:** the language model compares the extracted answer with the expected answer and assigns marks.
5. **Report:** a PDF report is generated and the result can be sent out via Twilio.

---

<a id="workflow"></a>

## 🧭 Workflow

<div align="center">
<img src="assets/workflow.svg" alt="AutoGrade AI workflow diagram" width="100%"/>
</div>

| Step | Lane | What happens |
|:---:|---|---|
| 1 | 👤 Evaluator | Uploads the scanned answer sheet |
| 2 | 🟣 Django backend | Validates the file and stores it |
| 3 | 🟢 AI engine | OpenCV cleans and normalises the image |
| 4 | 🟢 AI engine | OCR converts the image into text |
| 5 | 🟢 AI engine | The flan-t5 model evaluates the answers and produces marks |
| 6 | 🟣 Django backend | Saves the marks in the database |
| 7 | 🟣 Django backend | Builds the PDF report (ReportLab) and sends an alert (Twilio) |
| 8 | 👤 Evaluator | Views the result and receives the alert |

<details>
<summary><b>🔬 See the detailed flowchart</b></summary>

```mermaid
flowchart TD
    A([👤 Evaluator]) --> B[Upload scanned answer sheet]
    B --> C[Django backend<br/>validates and stores the file]

    subgraph IMG ["🖼️ Image Processing (OpenCV)"]
        D[Clean image<br/>noise, contrast, alignment]
    end

    subgraph OCR ["🔍 Text Extraction"]
        E[Tesseract / EasyOCR<br/>image to text]
        F[Split text into<br/>individual answers]
        E --> F
    end

    subgraph AI ["🧠 Evaluation (flan-t5)"]
        G[Load question and<br/>expected answer]
        H[Model compares<br/>student answer with expected]
        I[Assign marks]
        G --> H --> I
    end

    C --> D --> E
    F --> G
    I --> J[(Save result<br/>in database)]
    J --> K[Generate PDF report<br/>ReportLab]
    K --> L[📲 Send result via Twilio]
    K --> M([📄 Download report])

    classDef user fill:#0ea5e9,stroke:#0369a1,color:#fff
    classDef out fill:#22c55e,stroke:#15803d,color:#fff
    class A user
    class L,M out
```

</details>

---

<a id="tech-stack"></a>

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3 | Core development |
| Backend | Django | Web framework, routing, admin, storage |
| Image processing | OpenCV | Preprocessing of scanned sheets |
| OCR | Tesseract / EasyOCR | Text extraction |
| NLP | HuggingFace Transformers (flan-t5) | Answer evaluation |
| Reports | ReportLab | PDF result generation |
| Messaging | Twilio | Result notifications |
| Version control | Git & GitHub | Source management |

---

<a id="getting-started"></a>

## ⚙️ Getting Started

### Prerequisites

- Python 3.10+
- Git
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on your system (needed for the Tesseract path)
- A [Twilio](https://www.twilio.com/) account (only if you want notifications)

### 1. Clone the repository

```bash
git clone https://github.com/deepakbharti-cloud/AutoGrade-AI.git
cd AutoGrade-AI
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> The flan-t5 model is downloaded from HuggingFace on the first run, so the first evaluation takes longer.

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
```

> Never commit `.env` or any real credentials to GitHub.

### 5. Run migrations and start the server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

<a id="roadmap"></a>

## 🗺️ Roadmap

- [x] Answer sheet upload and preprocessing
- [x] OCR text extraction
- [x] AI-based answer evaluation
- [x] PDF report generation
- [x] Twilio notifications
- [ ] REST API with **Django REST Framework**
- [ ] Support for handwritten answers with better OCR accuracy
- [ ] Teacher dashboard with class-wide analytics
- [ ] Docker setup and cloud deployment

---

<a id="team"></a>

## 👥 Team

AutoGrade AI was built by a 6-member team.

| Member | Role |
|---|---|
| **Deepak Bharti** | DIP Engineer (digital image processing) |
<!-- Add the remaining team members here, one row each:
| Name | Role |
-->

---

<a id="contributing"></a>

## 🤝 Contributing

Suggestions and improvements are welcome.

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes
4. Push and open a Pull Request

---

<a id="developer"></a>

## 👨‍💻 Developer

**Deepak Bharti**

- 🌐 Portfolio: [deepakbharti.github.io](https://deepakbharti.github.io)
- 🐙 GitHub: [@deepakbharti-cloud](https://github.com/deepakbharti-cloud)
- 💼 LinkedIn: [Deepak Bharti](https://www.linkedin.com/in/deepak-bharti-ab7622315)

---

<div align="center">

Built with Python, Django and a lot of OCR · ⭐ Star the repo if you like it!

</div>
