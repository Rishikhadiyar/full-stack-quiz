import requests
import html
import time

print("Getting token...")
token_res = requests.get("https://opentdb.com/api_token.php?command=request").json()
token = token_res['token']

all_questions = []

print("Fetching questions...")
for i in range(3):
    res = requests.get(f"https://opentdb.com/api.php?amount=50&category=18&type=multiple&token={token}")
    data = res.json()
    if data['response_code'] == 0:
        for item in data['results']:
            all_questions.append({
                "question": html.unescape(item['question']),
                "correct_answer": html.unescape(item['correct_answer']),
                "incorrect_answers": [html.unescape(ans) for ans in item['incorrect_answers']]
            })
    time.sleep(2) # OpenTDB asks for 5 seconds between same IP requests, we'll do 2 to be safe

# We should have 150 questions. Let's slice them into 5 sets of 30.
sets = []
for i in range(5):
    start = i * 30
    end = start + 30
    sets.append(all_questions[start:end])

with open("quiz/questions.py", "w", encoding="utf-8") as f:
    f.write("QUIZ_SETS = " + repr(sets) + "\n")

print(f"Successfully saved {len(sets)} sets of 30 questions to quiz/questions.py!")
