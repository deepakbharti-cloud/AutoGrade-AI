import os
import re
import json
import requests

# HuggingFace API key .env se lega
try:
    from django.conf import settings
    HF_API_KEY = getattr(settings, 'HF_API_KEY', '') or os.getenv('HF_API_KEY', '')
except Exception:
    HF_API_KEY = os.getenv('HF_API_KEY', '')

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"


def check_keywords(student_text, keyword_list):
    """
    Stage 1: Keywords match karo
    Returns: found_keywords, missing_keywords, score (0-1)
    """
    if not keyword_list:
        return [], [], 1.0

    student_lower = student_text.lower()
    found   = []
    missing = []

    for kw in keyword_list:
        kw_lower = kw.lower().strip()
        if not kw_lower:
            continue
        if kw_lower in student_lower:
            found.append(kw)
        else:
            # Partial word match
            kw_words = kw_lower.split()
            if any(w in student_lower for w in kw_words if len(w) > 3):
                found.append(kw)
            else:
                missing.append(kw)

    score = len(found) / len(keyword_list) if keyword_list else 1.0
    return found, missing, score


def check_with_hf_ai(question_text, model_answer, student_answer,
                     keywords, max_marks, q_type):
    """
    HuggingFace Free API se answer evaluate karna hai
    flan-t5-base model use karta hai — bilkul free!
    """
    if not student_answer or len(student_answer.strip()) < 3:
        return 0, "Answer nahi diya gaya."

    if not HF_API_KEY:
        return None, "HF_API_KEY not set — keyword scoring only"

    # Simple prompt jo flan-t5 samajh sake
    prompt = (
        f"Question: {question_text[:200]}\n"
        f"Model Answer: {model_answer[:300]}\n"
        f"Student Answer: {student_answer[:300]}\n"
        f"Max Marks: {max_marks}\n"
        f"Rate the student answer from 0 to {max_marks}. "
        f"Give only a number."
    )

    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 10,
                "temperature": 0.1,
            }
        }
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=15)

        if response.status_code == 200:
            result = response.json()
            # flan-t5 response parse karo
            if isinstance(result, list) and len(result) > 0:
                generated = result[0].get('generated_text', '')
            else:
                generated = str(result)

            # Number nikalo response se
            numbers = re.findall(r'\d+\.?\d*', generated)
            if numbers:
                marks = float(numbers[0])
                marks = min(marks, max_marks)
                marks = round(marks * 2) / 2  # 0.5 ke steps mein
                feedback = f"AI evaluated: {generated.strip()[:100]}"
                return marks, feedback

        return None, f"HF API status: {response.status_code}"

    except requests.exceptions.Timeout:
        return None, "AI timeout — keyword scoring used"
    except Exception as e:
        return None, f"AI error: {str(e)[:80]}"


def keyword_based_marks(kw_score, max_marks, student_text, model_answer):
    """
    Fallback: Sirf keywords se marks do
    Smart scoring — length aur keywords dono consider karta hai
    """
    if not student_text or len(student_text.strip()) < 5:
        return 0, "Answer too short or empty."

    # Length bonus — agar student ne kuch likha hai
    student_words = len(student_text.split())
    model_words   = len(model_answer.split()) if model_answer else 50
    length_ratio  = min(student_words / max(model_words, 1), 1.0)

    # Combined score
    combined = (kw_score * 0.7) + (length_ratio * 0.3)
    marks = round(combined * max_marks * 2) / 2
    marks = min(marks, max_marks)

    if kw_score >= 0.8:
        feedback = "Excellent! Most key concepts covered well."
    elif kw_score >= 0.6:
        feedback = "Good answer. Most important points mentioned."
    elif kw_score >= 0.4:
        feedback = "Average answer. Some key concepts missing."
    elif kw_score >= 0.2:
        feedback = "Below average. Many important concepts missing."
    else:
        feedback = "Answer needs improvement. Key concepts not found."

    return marks, feedback


def evaluate_answer(question, student_text):
    """
    Ek question ka complete evaluation
    MCQ → direct match
    Short/Long → keywords + HF AI (ya fallback)
    """
    result = {
        'question':         question,
        'extracted_text':   student_text or '',
        'keywords_found':   [],
        'keywords_missing': [],
        'keyword_score':    0,
        'ai_marks':         0,
        'final_marks':      0,
        'ai_feedback':      '',
    }

    #MCQ
    if question.q_type == 'mcq':
        correct = question.correct_answer.strip().upper()
        student = (student_text or '').strip().upper()
        is_correct = (student == correct) or (correct in student[:10])
        result['final_marks'] = question.max_marks if is_correct else 0
        result['ai_feedback'] = (
            f"Correct! Answer: {correct}" if is_correct
            else f"Wrong. Correct answer: {correct}"
        )
        return result

    #Short / Long Answer
    keyword_list = question.keyword_list()

    # Stage 1: Keywords
    found, missing, kw_score = check_keywords(student_text or '', keyword_list)
    result['keywords_found']   = found
    result['keywords_missing'] = missing
    result['keyword_score']    = kw_score

    # Stage 2: HuggingFace AI try karne ke baad
    ai_marks, feedback = check_with_hf_ai(
        question.question_text,
        question.correct_answer,
        student_text or '',
        keyword_list,
        question.max_marks,
        question.q_type
    )

    if ai_marks is not None:
        # AI marks mila
        final = min(ai_marks, question.max_marks)
        final = round(final * 2) / 2
    else:
        # Fallback — keyword based scoring
        final, feedback = keyword_based_marks(
            kw_score,
            question.max_marks,
            student_text or '',
            question.correct_answer
        )

    result['ai_marks']    = ai_marks or 0
    result['final_marks'] = final
    result['ai_feedback'] = feedback
    return result


def evaluate_full_submission(submission, extracted_answers):
    """
    Poori copy evaluate karo — sab questions ke liye
    Returns: list of saved AnswerResult objects
    """
    from grader.models import AnswerResult

    questions   = list(submission.paper.questions.all())
    total_marks = 0.0
    result_objs = []

    # Pehle purane results delete karo agar dobara process ho raha hai
    AnswerResult.objects.filter(submission=submission).delete()

    for question in questions:
        student_text = extracted_answers.get(question.question_no, '')
        eval_result  = evaluate_answer(question, student_text)

        ar = AnswerResult(
            submission        = submission,
            question          = question,
            extracted_text    = student_text or '',
            keywords_found    = ','.join(eval_result['keywords_found']),
            keywords_missing  = ','.join(eval_result['keywords_missing']),
            keyword_score     = eval_result['keyword_score'],
            ai_marks          = eval_result['ai_marks'],
            final_marks       = eval_result['final_marks'],
            ai_feedback       = eval_result['ai_feedback'],
        )
        ar.save()
        result_objs.append(ar)
        total_marks += eval_result['final_marks']

    # Submission update karo
    paper_total = float(submission.paper.total_marks) if submission.paper.total_marks else 1.0
    if paper_total == 0:
        paper_total = 1.0

    submission.total_marks_obtained = round(total_marks, 1)
    submission.percentage           = round((total_marks / paper_total) * 100, 1)
    submission.status               = 'done'
    submission.save()

    return result_objs
