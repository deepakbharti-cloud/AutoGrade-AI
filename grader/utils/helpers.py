import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether
)
from huggingface_hub import InferenceClient

from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

try:
    from django.conf import settings
    TWILIO_SID    = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    TWILIO_TOKEN  = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    TWILIO_NUM    = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
except Exception:
    TWILIO_SID = TWILIO_TOKEN = TWILIO_NUM = ''

C_BLUE   = colors.HexColor("#1A56DB")
C_GREEN  = colors.HexColor("#057A55")
C_AMBER  = colors.HexColor("#B45309")
C_RED    = colors.HexColor("#C81E1E")
C_LGRAY  = colors.HexColor("#F3F4F6")
C_BORDER = colors.HexColor("#E5E7EB")
C_TEXT   = colors.HexColor("#111827")
C_MUTED  = colors.HexColor("#6B7280")


def _mark_color(obtained, maximum):
    r = obtained / maximum if maximum else 0
    if r >= 0.8: return C_GREEN
    if r >= 0.5: return C_AMBER
    return C_RED


def _grade(pct):
    if pct >= 90: return "A+", C_GREEN
    if pct >= 80: return "A",  C_GREEN
    if pct >= 70: return "B+", C_BLUE
    if pct >= 60: return "B",  C_BLUE
    if pct >= 50: return "C",  C_AMBER
    return "F", C_RED


def generate_result_pdf(submission, output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    bdr = C_BORDER

    def make_table(data, col_widths, has_header=True):
        t = Table(data, colWidths=col_widths)
        style = [
            ('FONTNAME',      (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE',      (0,0), (-1,-1), 9),
            ('GRID',          (0,0), (-1,-1), 0.4, bdr),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ]
        if has_header:
            style += [
                ('BACKGROUND', (0,0), (-1,0), C_BLUE),
                ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ]
        for i in range(1 if has_header else 0, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0,i), (-1,i), C_LGRAY))
        t.setStyle(TableStyle(style))
        return t

    story  = []
    student = submission.student
    paper   = submission.paper
    results = submission.results.all()
    pct     = submission.percentage
    grade, gc = _grade(pct)

    #HEADER
    story.append(Paragraph(
        '<font name="Helvetica-Bold" size="20" color="#1A56DB">AutoGrade AI</font>',
        ParagraphStyle("hdr", alignment=TA_CENTER, spaceAfter=4)
    ))
    story.append(Paragraph(
        f'<font size="11" color="#6B7280">Result Report — {paper.subject} | {paper.class_name}</font>',
        ParagraphStyle("sub", alignment=TA_CENTER, spaceAfter=10)
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=12))

    #STUDENT INFO
    story.append(Paragraph(
        '<font name="Helvetica-Bold" size="11" color="#111827">Student information</font>',
        ParagraphStyle("sh", spaceAfter=6)
    ))
    exam_date = submission.submitted_at.strftime("%d %B %Y")
    paper_code = f"{paper.subject[:3].upper()}-{student.class_name}-{submission.submitted_at.year}"
    info_data = [
        ["Student name", student.name,        "Subject",   paper.subject],
        ["Roll number",  student.roll_number,  "Class",     student.class_name],
        ["Phone",        student.phone or "—", "Exam date", exam_date],
        ["Teacher",      paper.teacher.get_full_name() or paper.teacher.username,
         "Paper code",   paper_code],
    ]
    story.append(make_table(info_data, [3.2*cm, 5.3*cm, 3.2*cm, 5.3*cm], has_header=False))
    story.append(Spacer(1, 14))

    #SCORE SUMMARY
    story.append(Paragraph(
        '<font name="Helvetica-Bold" size="11" color="#111827">Score summary</font>',
        ParagraphStyle("sh2", spaceAfter=6)
    ))
    score_data = [
        [
            Paragraph(f'<font name="Helvetica-Bold" size="24" color="#111827">{submission.total_marks_obtained}/{paper.total_marks}</font>',
                      ParagraphStyle("sv", alignment=TA_CENTER)),
            Paragraph(f'<font name="Helvetica-Bold" size="24" color="#1A56DB">{pct}%</font>',
                      ParagraphStyle("pv", alignment=TA_CENTER)),
            Paragraph(f'<font name="Helvetica-Bold" size="28" color="{gc.hexval()}">{grade}</font>',
                      ParagraphStyle("gv", alignment=TA_CENTER)),
            Paragraph(f'<font name="Helvetica-Bold" size="14" color="{(C_GREEN if pct >= 33 else C_RED).hexval()}">{"Pass" if pct >= 33 else "Fail"}</font>',
                      ParagraphStyle("rv", alignment=TA_CENTER)),
        ],
        [
            Paragraph('<font size="9" color="#6B7280">Total score</font>',  ParagraphStyle("l1", alignment=TA_CENTER)),
            Paragraph('<font size="9" color="#6B7280">Percentage</font>',   ParagraphStyle("l2", alignment=TA_CENTER)),
            Paragraph('<font size="9" color="#6B7280">Grade</font>',        ParagraphStyle("l3", alignment=TA_CENTER)),
            Paragraph('<font size="9" color="#6B7280">Result</font>',       ParagraphStyle("l4", alignment=TA_CENTER)),
        ],
    ]
    st = Table(score_data, colWidths=[4.25*cm]*4)
    st.setStyle(TableStyle([
        ('BOX',          (0,0), (-1,-1), 0.5, bdr),
        ('INNERGRID',    (0,0), (-1,-1), 0.5, bdr),
        ('BACKGROUND',   (0,0), (-1,-1), colors.white),
        ('TOPPADDING',   (0,0), (-1,-1), 10),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(st)
    story.append(Spacer(1, 14))

    #QUESTION-WISE MARKS
    story.append(Paragraph(
        '<font name="Helvetica-Bold" size="11" color="#111827">Question-wise marks</font>',
        ParagraphStyle("sh3", spaceAfter=6)
    ))
    q_data = [["Q#", "Type", "Question", "Max", "Given"]]
    for r in results:
        mc = _mark_color(r.final_marks, r.question.max_marks)
        mx = int(r.question.max_marks) if r.question.max_marks == int(r.question.max_marks) else r.question.max_marks
        q_data.append([
            f"Q{r.question.question_no}",
            r.question.get_q_type_display(),
            r.question.question_text[:65] + ("..." if len(r.question.question_text) > 65 else ""),
            str(mx),
            Paragraph(f'<font name="Helvetica-Bold" color="{mc.hexval()}">{r.final_marks}</font>',
                      ParagraphStyle("mk", alignment=TA_CENTER))
        ])
    story.append(make_table(q_data, [1.2*cm, 2.4*cm, 10.1*cm, 1.4*cm, 1.4*cm]))
    story.append(Spacer(1, 14))

    #AI FEEDBACK
    story.append(Paragraph(
        '<font name="Helvetica-Bold" size="11" color="#111827">AI feedback — question wise</font>',
        ParagraphStyle("sh4", spaceAfter=6)
    ))
    for r in results:
        found_list   = r.kw_found_list()
        missing_list = r.kw_missing_list()
        block = []

        block.append(Paragraph(
            f'<font name="Helvetica-Bold" size="10" color="#111827">Q{r.question.question_no} ({r.question.get_q_type_display()}):</font>'
            f' <font size="10" color="#111827">{r.question.question_text}</font>',
            ParagraphStyle("qh", fontSize=10, leading=14, spaceAfter=4)
        ))

        if r.question.q_type != 'mcq':
            if found_list:
                block.append(Paragraph(
                    "Keywords found: " + "  ".join(
                        [f'<font color="{C_GREEN.hexval()}">+ {kw}</font>' for kw in found_list]
                    ),
                    ParagraphStyle("kwf", fontSize=8.5, leftIndent=8, leading=13, spaceAfter=2)
                ))
            if missing_list:
                block.append(Paragraph(
                    "Keywords missing: " + "  ".join(
                        [f'<font color="{C_RED.hexval()}">- {kw}</font>' for kw in missing_list]
                    ),
                    ParagraphStyle("kwm", fontSize=8.5, leftIndent=8, leading=13, spaceAfter=2)
                ))

        """if r.ai_feedback:
            block.append(Paragraph(
                f'<font name="Helvetica-Oblique" size="9" color="#1E40AF">AI feedback: {r.ai_feedback}</font>',
                ParagraphStyle("fb", fontSize=9, leftIndent=8, leading=13)
            ))"""

        wrap = Table([[block]], colWidths=[17*cm])
        wrap.setStyle(TableStyle([
            ('BOX',          (0,0), (-1,-1), 0.5, bdr),
            ('BACKGROUND',   (0,0), (-1,-1), colors.white),
            ('TOPPADDING',   (0,0), (-1,-1), 8),
            ('BOTTOMPADDING',(0,0), (-1,-1), 6),
            ('LEFTPADDING',  (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(KeepTogether([wrap, Spacer(1, 6)]))

    #FOOTER
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=bdr, spaceAfter=6))
    story.append(Paragraph(
        f'Generated on {datetime.now().strftime("%d %B %Y, %I:%M %p")}  |  AutoGrade AI',
        ParagraphStyle("ft", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)
    ))

    doc.build(story)
    return output_path


#WhatsApp

def send_whatsapp_result(submission):
    if not TWILIO_SID or not TWILIO_TOKEN:
        return False, "Twilio credentials not configured in .env"
    if not submission.student.phone:
        return False, "Student ka phone number register nahi hai"
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        grade = submission.grade()
        emoji = "🎉" if submission.percentage >= 60 else "📚"
        body = (
            f"*AutoGrade AI — Result*\n\n"
            f"Student: {submission.student.name}\n"
            f"Subject: {submission.paper.subject}\n"
            f"Score: {submission.total_marks_obtained}/{submission.paper.total_marks}\n"
            f"Percentage: {submission.percentage}%\n"
            f"Grade: {grade}\n\n"
            f"{emoji} {'Congratulations!' if submission.percentage >= 60 else 'Keep practicing!'}\n\n"
            f"— {submission.paper.teacher.get_full_name() or 'Your Teacher'}\n"
            f"AutoGrade AI"
        )
        client.messages.create(from_=TWILIO_NUM, to=f'whatsapp:+91{submission.student.phone}', body=body)
        submission.whatsapp_sent = True
        submission.save()
        return True, "WhatsApp message sent successfully!"
    except Exception as e:
        return False, f"WhatsApp error: {str(e)[:150]}"
client = InferenceClient(api_key=os.getenv("HF_API_KEY"))

"""def grade_answer(answer_text):
    
    College demo ke liye simple evaluation function.
    Hugging Face ke free GPT-2 model ka use karta hai.
    
    result = client.text_generation(
        prompt=f"Evaluate this answer: {answer_text}",
        model="gpt2",   # free model
        max_new_tokens=50
    )
    return result"""
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()
client = InferenceClient(api_key=os.getenv("HF_API_KEY"))

def grade_answer(answer_text, model="google/flan-t5-small"):
    """
    College demo ke liye evaluation function.
    Model ke type ke hisaab se text_generation ya chat_completion call karega.
    """
    if "flan" in model.lower():   # text-generation models
        result = client.text_generation(
            prompt=f"Evaluate this answer: {answer_text}",
            model=model,
            max_new_tokens=50
        )
    else:   # conversational models (Mistral, Llama)
        result = client.chat_completion(
            model=model,
            messages=[{"role": "user", "content": f"Evaluate this answer: {answer_text}"}],
            max_tokens=50
        )
    return result

