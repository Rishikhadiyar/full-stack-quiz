import requests
import html
import time

print("Getting a fresh token...")
token_res = requests.get("https://opentdb.com/api_token.php?command=request").json()
token = token_res['token']
print(f"Token: {token}")

all_questions = []
categories = [18, 18, 18, 11, 17]  # Mix: Computer Science (18), Entertainment(11), Science(17)

print("Fetching questions...")
for i, cat in enumerate(categories):
    print(f"  Fetching batch {i+1}/5...")
    res = requests.get(
        f"https://opentdb.com/api.php?amount=30&category={cat}&type=multiple&token={token}"
    )
    data = res.json()
    print(f"  Response code: {data['response_code']}, Got: {len(data.get('results', []))} questions")
    
    if data['response_code'] == 0:
        batch = []
        for item in data['results']:
            batch.append({
                "question": html.unescape(item['question']),
                "correct_answer": html.unescape(item['correct_answer']),
                "incorrect_answers": [html.unescape(ans) for ans in item['incorrect_answers']]
            })
        all_questions.append(batch)
    else:
        print(f"  WARNING: Batch {i+1} failed with code {data['response_code']}")
        all_questions.append([])  # keep placeholder
    
    time.sleep(6)  # OpenTDB rate limit: 1 request per 5 seconds

print(f"\nSummary:")
for i, s in enumerate(all_questions):
    print(f"  Set {i+1}: {len(s)} questions")

# Only write if we have valid data
if all(len(s) == 30 for s in all_questions):
    with open("quiz/questions.py", "w", encoding="utf-8") as f:
        f.write("QUIZ_SETS = " + repr(all_questions) + "\n")
    print("\nSaved all 5 sets of 30 questions to quiz/questions.py!")
else:
    print("\nERROR: Not all sets have 30 questions. File NOT saved.")
    print("Please run this script again after a few minutes.")
