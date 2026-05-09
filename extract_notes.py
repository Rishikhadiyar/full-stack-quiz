import os
import glob
from pypdf import PdfReader
from collections import Counter
import re

folder_path = "django notes"
pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

all_text = ""
for file in pdf_files:
    try:
        reader = PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Basic keyword analysis to deduce knowledge
keywords = {
    "Function Based Views (FBV)": ["def ", "request", "render("],
    "Class Based Views (CBV)": ["class", "ListView", "DetailView", "TemplateView", "View"],
    "Django REST Framework (DRF)": ["rest_framework", "APIView", "ModelViewSet", "serializer"],
    "Forms & ModelForms": ["forms.Form", "forms.ModelForm", "cleaned_data"],
    "Templates": ["{%", "{{", "extends", "block", "include"],
    "ORM & Models": ["models.Model", "CharField", "QuerySet", "filter(", "objects.all()"],
    "Sessions & Cookies": ["request.session", "set_cookie", "get_cookie"],
    "Authentication": ["UserCreationForm", "authenticate", "login(", "logout(", "@login_required"],
    "JavaScript/Ajax/Fetch": ["fetch(", "ajax", "XMLHttpRequest", "axios"],
    "Admin Customization": ["admin.site.register", "admin.ModelAdmin"]
}

print("=== SCAN RESULTS ===")
print(f"Total PDFs Scanned: {len(pdf_files)}")
print(f"Total Characters Extracted: {len(all_text)}")

print("\n--- Knowledge Base Analysis ---")
lower_text = all_text.lower()
for concept, checks in keywords.items():
    score = sum(1 for check in checks if check.lower() in lower_text)
    if score > 0:
        print(f"- {concept}: Detected ({score}/{len(checks)} key patterns found)")
    else:
        print(f"- {concept}: Not Detected")

print("\n--- Summary Snippet ---")
# Print a bit of the text to see what kind of notes they are
words = all_text.split()
print(" ".join(words[:200]) + "...")
