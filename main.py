from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import anthropic
import tempfile
import os
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
converter = DocumentConverter()

@app.get("/")
def health_check():
    return {"status": "roaster is alive 🔥"}

@app.post("/roast")
async def roast_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Sirf PDF chalega bhai!"}
    
    contents = await file.read()
    
    if len(contents) > 2 * 1024 * 1024:
        return {"error": "2MB se bada resume?! Novel likh de bhai!"}
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    result = converter.convert(tmp_path)
    resume_text = result.document.export_to_markdown()
    os.unlink(tmp_path)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""You are a savage but hilarious Indian career counselor who roasts resumes section by section. You love throwing in hindi slangs like 'bhondu', 'career-paglu', 'jugaadu', 'chapri', 'arre bhai' to make it spicy.

For each section of the resume, give:
- A rating out of 10
- A one line savage joke about it, use hindi slangs liberally
- One actual genuine feedback (because you're not completely heartless)

End with an overall "Hire or Fire" verdict with a funny reason in hindi slang.

Resume:
{resume_text}"""
            }
        ]
    )

    return {"roast": message.content[0].text}