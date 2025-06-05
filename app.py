from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from azure.ai.formrecognizer import DocumentAnalysisClient, FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from datetime import datetime, timedelta
from azure.data.tables import TableServiceClient
import uuid
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Azure Credentials
# Blob Storage
blob_connection_string = os.getenv("ENTER_YOUR_BLOB_CONNECTION_STRING_HERE")
container_name = os.getenv("ENTER_YOUR_CONTAINER_NAME_HERE")

blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Azure Table Storage
table_service_client = TableServiceClient.from_connection_string(blob_connection_string)
table_name = os.getenv("ENTER_YOUR_TABLE_NAME_HERE")
table_client = table_service_client.create_table_if_not_exists(table_name=table_name)

def calculate_match_percentage(skills_str, keywords):
    if not skills_str:
        return 0
    match_count = sum(1 for keyword in keywords if keyword.lower() in skills_str.lower())
    return int((match_count / len(keywords)) * 100)

# Form Recognizer
form_recognizer_endpoint = os.getenv("ENTER_YOUR_DOCUMENT_INTELLIGENCE_ENDPOINT_HERE")
form_recognizer_key = os.getenv("ENTER_YOUR_DOC_INTELLIGENCE_KEY_HERE")

document_analysis_client = DocumentAnalysisClient(
    endpoint=form_recognizer_endpoint,
    credential=AzureKeyCredential(form_recognizer_key)
)


#Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file = request.files['resume']
        filename = file.filename

        # Upload to Azure Blob
        blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
        blob_client.upload_blob(file, overwrite=True, content_settings=ContentSettings(content_type='application/pdf'))

        # Generate SAS token for file
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=container_name,
            blob_name=filename,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{filename}?{sas_token}"

        # Read file again for Form Recognizer
        file.stream.seek(0)
        doc_bytes = file.read()

        # Analyze with Custom Trained Model
        doc_client = DocumentAnalysisClient(
            endpoint=form_recognizer_endpoint,
            credential=AzureKeyCredential(form_recognizer_key)
        )

        poller = doc_client.begin_analyze_document(model_id="resume-training", document=doc_bytes)
        result = poller.result()

        extracted_data = {}
        if result.documents:
            for name, field in result.documents[0].fields.items():
                extracted_data[name] = field.value if field.value else "Not found"

        # Calculate match percentage
        keywords = ['MongoDB', 'Express', 'React', 'Node.js', 'Python', 'Java']
        skills = extracted_data.get("Skills", "")
        match_percent = calculate_match_percentage(skills, keywords)

        # Save to Azure Table
        entity = {
            'PartitionKey': 'Resume',
            'RowKey': str(uuid.uuid4()),
            'Name': extracted_data.get("Name", "Unknown"),
            'Email': extracted_data.get("Email", "N/A"),
            'Skills': skills,
            'Experience': extracted_data.get("Experience", "N/A"),
            'MatchPercentage': match_percent,
            'BlobUrl': blob_url
        }
        table_client.create_entity(entity=entity)

        return jsonify({
            "message": "File uploaded and analyzed successfully.",
            "blob_url": blob_url,
            "extracted_data": extracted_data,
            "match_percentage": match_percent
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    

@app.route('/ranked-resumes', methods=['GET'])
def get_ranked_resumes():
    try:
        entities = table_client.list_entities()
        resume_list = sorted(entities, key=lambda x: int(x['MatchPercentage']), reverse=True)

        ranked_data = []
        for resume in resume_list:
            ranked_data.append({
                'name': resume.get('Name', 'Unknown'),
                'email': resume.get('Email', ''),
                'skills': resume.get('Skills', ''),
                'experience': resume.get('Experience', ''),
                'match': resume.get('MatchPercentage', 0),
                'url': resume.get('BlobUrl', '#')
            })

        return jsonify(ranked_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)