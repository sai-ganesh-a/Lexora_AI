# Lexora AI

Lexora AI is a document chat application. You upload your PDF, DOCX, or TXT files and then ask questions about them. The AI reads through your documents and answers based on what is actually in the files. It does not make things up from outside. The idea is simple. Instead of reading a whole document yourself you just upload it and ask whatever you want to know.

## What it can do

You can upload multiple documents inside a project workspace. After uploading you can ask questions and the system finds the relevant part of the document and gives you an answer. You can also click a button to get a full summary of any document. Chat history is saved so when you come back your previous conversation is still there. You can clear it anytime.

## Tech Stack

- Flask for the backend
- SQLite for storing user data and chat history
- ChromaDB for storing document vectors
- Google Gemini for embeddings and generating answers
- PyMuPDF for reading PDF files
- python-docx for reading DOCX files
- Tailwind CSS for the frontend styling

## How to run this locally

First make sure Python is installed. Then follow these steps.

Clone the repo and go into the folder.

```bash
git clone https://github.com/yourusername/lexora-ai
cd lexora-ai
```

Create a virtual environment and activate it.

```bash
python -m venv venv
venv\Scripts\activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root folder. You can copy from the example file.

```bash
cp .env.example .env
```

Open the `.env` file and put your actual Gemini API key and a secret key.

```env
SECRET_KEY=anyrandomstring
GEMINI_API_KEY=your_gemini_api_key
```

Now run the app.

```bash
python app.py
```

Open your browser and go to `http://127.0.0.1:5000`

## How to use

When you open the app for the first time it will ask you to register. Create an account and log in. After login create a new project from the dashboard. Then go inside the project and upload a document. Wait for it to finish processing. Once the status shows ready you can start asking questions in the chat box on the right side. To get a summary of a document click the small document icon next to it. To delete a document click the trash icon. It will remove the file and also clear its data from the search index. To clear chat history click the Clear History button at the top of the chat panel.

## Project Structure

```text
Lexora AI/
app/
  models/         database models
  routes/         flask blueprints
  services/       document processing and AI logic
  templates/      HTML pages
docs/             project documentation files
uploads/          uploaded files stored here
chroma_db/        vector database stored here
instance/         sqlite database stored here
app.py            entry point
config.py         configuration
requirements.txt  python dependencies
.env.example      environment variable template
```

## Notes

The uploads folder and chroma db folder are created automatically when you run the app. You do not need to create them manually. The app runs in debug mode by default. If you deploy this somewhere turn off debug mode in app.py. If you see any database errors delete the database.db file inside the instance folder and restart. It will create a fresh one.

## License

This project is built for academic and learning purposes.
