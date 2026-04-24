AutoGrade AI
> AI-Powered Automated Answer Sheet Grading System
C.S.J.M Govt. Polytechnic, Ambedkar Nagar | Diploma CSE 2023-26
---
Project Overview
AutoGrade AI is an intelligent system that automatically evaluates handwritten answer sheets using Digital Image Processing (DIP), OCR, and AI. It supports MCQ, Short Answer, and Long Answer question types.
Team Members
Name	Role	Module
Akriti Bharshiv (TL)	Team Lead	Project management, integration
Deepak Bharti	DIP Engineer	OpenCV pipeline, segmentation
Adarsh Yadav	OCR & Database	Tesseract, EasyOCR, MySQL
Shivangi Yadav	Frontend Dev	Bootstrap UI, templates
Utkarsh Singh	AI Module	HuggingFace evaluator
Saurabh Maurya	Testing & Docs	Testing, report, README
Features
Home page with Teacher and Student portal
DIP pipeline: denoise, skew fix, threshold, segmentation
OCR: Tesseract + EasyOCR dual engine
AI evaluation: keyword matching + HuggingFace flan-t5
Teacher dashboard with class analytics and charts
PDF result generation with AutoGrade AI branding
WhatsApp result delivery via Twilio API
Excel export (.xlsx) and bulk PDF ZIP download
Student portal: roll number + phone based result check
Tech Stack
Backend: Python 3.10, Django 4.2.7
Database: MySQL 8.0 (via XAMPP)
DIP: OpenCV 4.8, NumPy
OCR: Tesseract 5.0, EasyOCR 1.7
AI: HuggingFace flan-t5 (free inference API)
PDF: ReportLab 4.0
WhatsApp: Twilio API
Excel: openpyxl
Frontend: Bootstrap 5.3, Bootstrap Icons
Installation
Prerequisites
Python 3.10+
XAMPP (for MySQL)
Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
Git
Step 1 — Clone repository
```bash
git clone https://github.com/deepakbharti-cloud/autograde-ai.git
cd autograde-ai
```
Step 2 — Virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```
Step 3 — MySQL database
Start XAMPP → Start MySQL → Open phpMyAdmin → Create database:
```sql
CREATE DATABASE autograde_ai CHARACTER SET utf8mb4;
```
Step 4 — Configure .env
```
DB_NAME=autograde_ai
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=your-secret-key-here
HF_API_KEY=your-huggingface-api-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```
Step 5 — Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
Step 6 — Start server
```bash
python manage.py runserver
```
Open: http://127.0.0.1:8000
Project Structure
```
autograde_ai/
├── autograde_core/          Django project settings
├── grader/                  Main application
│   ├── dip/pipeline.py      OpenCV DIP processing
│   ├── ocr/extractor.py     Tesseract + EasyOCR
│   ├── ai_checker/          HuggingFace AI evaluation
│   ├── utils/helpers.py     PDF + WhatsApp
│   ├── views.py             All views
│   ├── models.py            Database models
│   ├── urls.py              URL routing
│   └── templates/grader/    HTML templates
├── manage.py
├── requirements.txt
└── .env
```
Usage
Login at http://127.0.0.1:8000/login/
Create Question Paper → Add questions with keywords
Add Students with roll numbers
Upload Copy → Select paper + student + images → Process
View Result → Download PDF → Send WhatsApp
View Analytics at /analytics/
Export Excel at /export/excel/
Student portal at /student-portal/
API Keys (Free)
HuggingFace: https://huggingface.co/settings/tokens (free)
Twilio sandbox: https://www.twilio.com/try-twilio (free trial)
License
Academic project — C.S.J.M Govt. Polytechnic Ambedkar Nagar, 2023-26
