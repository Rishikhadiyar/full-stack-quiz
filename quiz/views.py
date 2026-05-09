import random
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import QuizAttempt
from .questions import QUIZ_SETS

def index(request):
    """ Landing page to start the quiz """
    return render(request, 'quiz/index.html')

def start_quiz(request):
    """ Loads a random set of 30 questions and creates a new QuizAttempt """
    try:
        # Pick a random set out of the 5 available
        selected_set = random.choice(QUIZ_SETS)
        
        # Load and shuffle questions for this specific attempt
        questions = []
        for item in selected_set:
            incorrect = item['incorrect_answers']
            assert isinstance(incorrect, list)
            options = incorrect + [item['correct_answer']]
            random.shuffle(options)
            
            questions.append({
                'question': item['question'],
                'correct_answer': item['correct_answer'],
                'options': options
            })
            
        # Create a new quiz attempt in the database
        attempt = QuizAttempt.objects.create(
            questions_data=questions,
            score=0,
            current_index=0,
            # Pre-allocate tracking data for all 30 questions
            user_answers=[{'selected_answer': None, 'is_marked': False} for _ in range(len(questions))]
        )
        
        return redirect('play_quiz', attempt_id=attempt.id, question_index=0)
        
    except Exception as e:
        return render(request, 'quiz/error.html', {'message': str(e)})

def play_quiz(request, attempt_id, question_index):
    """ Displays the current question and the exam palette """
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    if question_index >= len(attempt.questions_data):
        return redirect('quiz_result', attempt_id=attempt.id)
        
    current_q = attempt.questions_data[question_index]
    
    # Backward compatibility for old attempts
    if not attempt.user_answers or len(attempt.user_answers) < len(attempt.questions_data):
        attempt.user_answers = [{'selected_answer': None, 'is_marked': False} for _ in range(len(attempt.questions_data))]
        attempt.save()
        
    current_ans = attempt.user_answers[question_index]
    
    # Build palette tracking details for rendering colors
    palette = []
    for i, ans in enumerate(attempt.user_answers):
        status = 'not_answered'
        if type(ans) is dict:
            if ans.get('is_marked', False):
                status = 'marked_answered' if ans.get('selected_answer') else 'marked'
            elif ans.get('selected_answer'):
                status = 'answered'
            
        palette.append({
            'number': i + 1,
            'index': i,
            'status': status
        })
    
    context = {
        'attempt': attempt,
        'question': current_q,
        'current_ans': current_ans.get('selected_answer') if type(current_ans) is dict else None,
        'question_index': question_index,
        'question_number': question_index + 1,
        'total_questions': len(attempt.questions_data),
        'palette': palette
    }
    return render(request, 'quiz/play.html', context)

def submit_answer(request, attempt_id, question_index):
    """ Handles Save & Next, Mark for Review, and Clear Response actions """
    if request.method == 'POST':
        attempt = get_object_or_404(QuizAttempt, id=attempt_id)
        action = request.POST.get('action')
        selected_answer = request.POST.get('answer')
        
        answers = attempt.user_answers
        ans_data = answers[question_index]
        
        if action == 'clear':
            ans_data['selected_answer'] = None
            ans_data['is_marked'] = False
            attempt.user_answers = answers
            attempt.save()
            # Stay on the same page for clear
            return redirect('play_quiz', attempt_id=attempt.id, question_index=question_index)
            
        if action == 'mark_review':
            if selected_answer:
                ans_data['selected_answer'] = selected_answer
            ans_data['is_marked'] = True
        elif action == 'save_next':
            if selected_answer:
                ans_data['selected_answer'] = selected_answer
                ans_data['is_marked'] = False
                
        attempt.user_answers = answers
        attempt.save()
        
        # Move to the next question automatically
        next_index = question_index + 1
        if next_index >= len(attempt.questions_data):
            # If on last question, just stay on it or go to result. 
            # We'll stay on it so they can use the submit button in palette.
            return redirect('play_quiz', attempt_id=attempt.id, question_index=question_index)
            
        return redirect('play_quiz', attempt_id=attempt.id, question_index=next_index)
        
    return redirect('index')

def quiz_result(request, attempt_id):
    """ Displays the final score and review sheet """
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    # Calculate score dynamically
    score = 0
    review_data = []
    
    for i, ans in enumerate(attempt.user_answers):
        q_data = attempt.questions_data[i]
        
        if type(ans) is dict and 'is_correct' not in ans:
            # Modern model structure
            sel = ans.get('selected_answer')
            is_correct = (sel == q_data['correct_answer'])
            if is_correct:
                score += 1
                
            review_data.append({
                'number': i + 1,
                'question': q_data['question'],
                'selected_answer': sel if sel else "Not Answered",
                'correct_answer': q_data['correct_answer'],
                'is_correct': is_correct
            })
        else:
            # Fallback for older attempts
            score += 1 if ans.get('is_correct') else 0
            review_data.append(ans)
            
    attempt.score = score
    attempt.save()
    
    # Pagination: 10 items per page
    paginator = Paginator(review_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'score': score,
        'total': len(attempt.questions_data),
        'page_obj': page_obj
    }
    return render(request, 'quiz/result.html', context)

def quit_quiz(request, attempt_id, question_index):
    """ Confirmation page when user wants to quit/submit """
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    answered_count = sum(1 for ans in attempt.user_answers if type(ans) is dict and ans.get('selected_answer'))
    return render(request, 'quiz/quit.html', {
        'attempt': attempt, 
        'question_index': question_index, 
        'answered_count': answered_count
    })
