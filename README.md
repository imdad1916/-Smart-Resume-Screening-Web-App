
# Smart Resume Screening Web App

A powerful web application that streamlines the hiring process by automating resume filtering, data extraction, and candidate ranking based on job description relevance.

---

## Features

- Upload resumes in PDF format
- Automatically extract key information (skills, education, experience)
- Match resumes to job descriptions using keyword-based scoring
- Ranks candidates by **match percentage**
- Visual match percentage bar
- Smooth user experience with:
  - Loading animations
  - Toast notifications
  - Responsive layout for all screen sizes

---

## Tech Stack

### Frontend
- HTML, CSS, JavaScript

### Backend
- Python (Flask)

### Azure Cloud Services
- **Azure Blob Storage**: Store uploaded resumes securely
- **Azure Document Intelligence (Custom Model)**: Extract structured data from resumes
- **Azure Table Storage**: Store candidate data and match scores
- **Azure App Service**: Host and deploy the web app

---

## Setup & Run Locally

### Prerequisites
- Python 3.8+
- Azure Account (with access to Document Intelligence and Table Storage)
- Flask, Azure SDK packages

### Clone the Repository
```bash
git clone https://github.com/your-username/resume-screener.git
cd resume-screener
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure Environment Variables
Inside `.env` file and add your Azure credentials:
```
AZURE_FORM_RECOGNIZER_ENDPOINT=your_endpoint_here
AZURE_FORM_RECOGNIZER_KEY=your_key_here
AZURE_STORAGE_CONNECTION_STRING=your_blob_connection_string
AZURE_TABLE_NAME=your_table_name
```

### Run the Application
```bash
python app.py
```

App will be accessible at `http://127.0.0.1:5000/`

---

## Folder Structure

```
resume-screener/
│
├── static/                  # CSS, JS files
├── templates/               # HTML templates      
├── app.py                   # Main Flask app
└── requirements.txt
```

---

## Future Improvements

- Add user login/authentication
- Enable multi-job role support
- Integrate ML-based semantic matching (e.g., with BERT)
- Visual analytics dashboard for recruiters

---

## Contributions

Feel free to open issues or submit pull requests to improve the project!

---
#   - S m a r t - R e s u m e - S c r e e n i n g - W e b - A p p  
 