import json

with open('tayaariapp/generated_questions_1200_clean.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'Total questions: {len(data)}')
    q = data[0]
    print(f'Question ID: {q["id"]}')
    print(f'Options type: {type(q["options"])}')
    print(f'Options: {json.dumps(q["options"], indent=2)[:500]}')
    print(f'CorrectAnswer: {q["correctAnswer"]}')