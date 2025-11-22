from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import json
import os
from google import genai
from datetime import datetime, timedelta, timezone
import re

# Load API key
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def home(request):
    return render(request, "index.html")


# -------------------- AI TEXT RESPONSE --------------------
@csrf_exempt
def get_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        # -------- TIME FIX (IST) --------
        IST = timezone(timedelta(hours=5, minutes=30))
        current_ist_time = datetime.now(IST).strftime("%d-%m-%Y %I:%M %p")

        final_prompt = (
            f"Current IST date & time: {current_ist_time}\n"
            f"User message: {user_message}\n"
            "If user asks about date/time, answer in IST."
        )

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[{"parts": [{"text": final_prompt}]}]
            )

            reply = response.candidates[0].content.parts[0].text

            # Clean markdown
            reply = re.sub(r"[*_`#>-]", "", reply)

        except Exception as e:
            reply = f"Sorry, something went wrong 😔 ({str(e)})"

        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "Invalid request"}, status=400)


# -------------------- FILE / IMAGE UPLOAD --------------------
@csrf_exempt
def upload_file(request):
    if request.method == "POST":
        if "file" not in request.FILES:
            return JsonResponse({"error": "No file found"}, status=400)

        file = request.FILES["file"]

        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)

        return JsonResponse({
            "status": "success",
            "file_url": file_url
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
