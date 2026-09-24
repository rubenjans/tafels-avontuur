import io
import math
import random
import time

import streamlit as st
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Rekenavontuur", page_icon="🧮", layout="centered")

st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#eef7ff,#fff4dc 55%,#f4eaff)}
.block-container{max-width:920px;padding-top:1.2rem}.hero{background:linear-gradient(120deg,#5b5ff0,#9b5de5);color:white;padding:24px;border-radius:24px;text-align:center;box-shadow:0 12px 30px #5b5ff038}.hero h1{margin:0;font-size:2.25rem}.hero p{margin:.5rem 0 0}.card{background:#fffffff0;padding:20px;border-radius:22px;box-shadow:0 8px 24px #1e293b1a;margin:14px 0}.question{font-size:3rem;font-weight:850;text-align:center;color:#30345f}.timer{text-align:center;font-weight:800;background:#fff3b0;padding:10px;border-radius:14px}div.stButton>button,[data-testid="stFormSubmitButton"] button{border-radius:16px;min-height:50px;font-weight:750}.fire{position:fixed;inset:0;pointer-events:none;z-index:9999}.spark{position:absolute;width:8px;height:8px;left:50%;top:35%;border-radius:50%;animation:b 1.8s infinite;box-shadow:0 -90px #f33,64px -64px #fd3,90px 0 #0c8,64px 64px #29f,0 90px #95e,-64px 64px #f80,-90px 0 #f38,-64px -64px #0dd}@keyframes b{0%{transform:scale(.05);opacity:1}100%{transform:scale(1.8);opacity:0}}@media(max-width:600px){.question{font-size:2.5rem}.hero h1{font-size:1.7rem}}
</style>
""", unsafe_allow_html=True)

DEFAULTS = {
    "screen": "home", "started": False, "finished": False,
    "score": 0, "streak": 0, "best": 0, "lives": 3, "xp": 0,
    "answered": 0, "correct": 0, "wrong": 0, "missed": 0,
    "locked": False, "feedback": "", "start": 0.0, "end": 0.0,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset(keep_screen=True):
    screen = st.session_state.screen if keep_screen else "home"
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.session_state.screen = screen


def create_exercise(kind, limit=10, operation="Combinatie", tables=None):
    if kind == "tafels":
        a = random.choice(tables)
        b = random.randint(0, 10)
        return a, b, "×", a * b, 100

    operator = random.choice(["+", "−"]) if operation == "Combinatie" else ("+" if operation == "Sommen" else "−")
    if operator == "+":
        a = random.randint(0, limit)
        b = random.randint(0, limit - a)
        answer = a + b
    else:
        a = random.randint(0, limit)
        b = random.randint(0, a)
        answer = a - b
    return a, b, operator, answer, limit


def new_question():
    a, b, operator, answer, cap = create_exercise(
        st.session_state.kind,
        st.session_state.get("limit", 10),
        st.session_state.get("operation", "Combinatie"),
        st.session_state.get("tables", list(range(11))),
    )
    choices = {answer}
    while len(choices) < 4:
        choices.add(max(0, min(cap, answer + random.choice([-10, -5, -3, -2, -1, 1, 2, 3, 5, 10]))))
    st.session_state.a, st.session_state.b = a, b
    st.session_state.operator, st.session_state.answer = operator, answer
    st.session_state.choices = list(choices)
    random.shuffle(st.session_state.choices)
    st.session_state.locked = False
    st.session_state.feedback = ""
    if st.session_state.level == "Met tijdsklok":
        st.session_state.deadline = time.time() + st.session_state.seconds


def finish(message):
    if not st.session_state.finished:
        st.session_state.finished = True
        st.session_state.end = time.time()
        st.session_state.end_message = message


def submit_answer(value):
    if st.session_state.locked or st.session_state.finished:
        return
    test = st.session_state.level == "Toetsniveau"
    st.session_state.locked = True
    st.session_state.answered += 1
    if value == st.session_state.answer:
        st.session_state.correct += 1
        st.session_state.streak += 1
        st.session_state.best = max(st.session_state.best, st.session_state.streak)
        if not test:
            st.session_state.score += 10
            st.session_state.xp += 20
            st.session_state.feedback = "✅ Juist!"
    else:
        st.session_state.wrong += 1
        st.session_state.streak = 0
        if not test:
            st.session_state.lives -= 1
            st.session_state.feedback = f"💡 Het juiste antwoord is {st.session_state.answer}."
    if test:
        if st.session_state.answered >= 100:
            finish("Alle 100 oefeningen zijn ingevuld.")
        else:
            new_question()
    elif st.session_state.answered >= st.session_state.rounds or st.session_state.lives <= 0:
        finish("De reeks is voltooid.")


def pdf_operator(operator):
    return "x" if operator == "×" else "-" if operator == "−" else operator


def make_worksheet_pdf(kind, count, limit, operation, tables, include_answers=False):
    exercises = [create_exercise(kind, limit, operation, tables)[:4] for _ in range(count)]
    output = io.BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    page_width, page_height = A4

    # 4 columns x 10 exercises, visually grouped as 5 + 5.
    exercises_per_page = 40
    columns = 4
    rows_per_column = 10
    margin_x = 34
    gutter = 15
    content_width = page_width - (2 * margin_x)
    column_width = (content_width - (columns - 1) * gutter) / columns
    first_y = page_height - 138
    row_step = 31
    group_gap = 23

    total_pages = math.ceil(len(exercises) / exercises_per_page)
    title = "Werkblad tafels" if kind == "tafels" else "Werkblad sommen en verschillen"
    subtitle = (
        "Tafels: " + ", ".join(str(t) for t in tables)
        if kind == "tafels"
        else f"Bereik: 0-{limit}  |  Oefeningen: {operation.lower()}"
    )

    for page_index, start in enumerate(range(0, len(exercises), exercises_per_page), start=1):
        page_data = exercises[start:start + exercises_per_page]

        # Header band
        pdf.setFillColor(HexColor("#4F46E5"))
        pdf.roundRect(margin_x, page_height - 82, page_width - 2 * margin_x, 46, 10, fill=1, stroke=0)
        pdf.setFillColor(HexColor("#FFFFFF"))
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(margin_x + 16, page_height - 58, title)
        pdf.setFont("Helvetica", 8.5)
        pdf.drawRightString(page_width - margin_x - 16, page_height - 58, subtitle)

        # Student fields
        pdf.setFillColor(HexColor("#22223B"))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(margin_x, page_height - 104, "Naam: __________________________________")
        pdf.drawRightString(page_width - margin_x, page_height - 104, "Datum: ____ / ____ / ______")
        pdf.setStrokeColor(HexColor("#D9D9E8"))
        pdf.line(margin_x, page_height - 116, page_width - margin_x, page_height - 116)

        # Soft column guides and exercise text
        for col in range(columns):
            x = margin_x + col * (column_width + gutter)
            if col > 0:
                guide_x = x - gutter / 2
                pdf.setStrokeColor(HexColor("#E7E7F2"))
                pdf.setLineWidth(0.6)
                pdf.line(guide_x, 73, guide_x, page_height - 127)

        for local_index, (a, b, operator, answer) in enumerate(page_data):
            column = local_index // rows_per_column
            row = local_index % rows_per_column
            x = margin_x + column * (column_width + gutter)
            y = first_y - row * row_step - (group_gap if row >= 5 else 0)
            number = start + local_index + 1

            if row == 5:
                pdf.setStrokeColor(HexColor("#CFCFE5"))
                pdf.setDash(2, 3)
                pdf.line(x, y + 21, x + column_width, y + 21)
                pdf.setDash()

            pdf.setFillColor(HexColor("#5B5F75"))
            pdf.setFont("Helvetica", 8)
            pdf.drawString(x, y + 3, f"{number}.")
            pdf.setFillColor(HexColor("#202238"))
            pdf.setFont("Helvetica-Bold", 12)
            expression = f"{a} {pdf_operator(operator)} {b} = ....."
            pdf.drawString(x + 18, y, expression)

        # Footer
        pdf.setStrokeColor(HexColor("#D9D9E8"))
        pdf.line(margin_x, 52, page_width - margin_x, 52)
        pdf.setFillColor(HexColor("#77778C"))
        pdf.setFont("Helvetica", 8)
        pdf.drawString(margin_x, 37, f"{count} oefeningen | 4 kolommen | extra witruimte na 5 rijen")
        pdf.drawRightString(page_width - margin_x, 37, f"Pagina {page_index} van {total_pages}")
        pdf.showPage()

    if include_answers:
        pdf.setFillColor(HexColor("#4F46E5"))
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(42, page_height - 52, "Antwoordsleutel")
        pdf.setFillColor(HexColor("#22223B"))
        pdf.setFont("Helvetica", 10)
        y = page_height - 82
        x_positions = [42, 180, 318, 456]
        for index, (_, _, _, answer) in enumerate(exercises):
            col = index % 4
            if col == 0 and index > 0:
                y -= 20
            if y < 45:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = page_height - 52
            pdf.drawString(x_positions[col], y, f"{index + 1}. {answer}")
        pdf.showPage()

    pdf.save()
    output.seek(0)
    return output.getvalue()


# Start screen
if st.session_state.screen == "home":
    st.markdown('<div class="hero"><h1>🧮 Rekenavontuur</h1><p>Wat wil je vandaag doen?</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card"><h2>➕➖ Sommen</h2><p>Optellen en aftrekken.</p></div>', unsafe_allow_html=True)
        if st.button("Sommen oefenen", use_container_width=True):
            st.session_state.screen, st.session_state.kind = "game", "sommen"; st.rerun()
    with col2:
        st.markdown('<div class="card"><h2>✖️ Tafels</h2><p>Maaltafels van 0 tot 10.</p></div>', unsafe_allow_html=True)
        if st.button("Tafels oefenen", use_container_width=True):
            st.session_state.screen, st.session_state.kind = "game", "tafels"; st.rerun()
    with col3:
        st.markdown('<div class="card"><h2>🖨️ Afdrukken</h2><p>Maak een PDF-werkblad.</p></div>', unsafe_allow_html=True)
        if st.button("Werkblad maken", use_container_width=True):
            st.session_state.screen = "print"; st.rerun()
    st.stop()

if st.sidebar.button("🏠 Startscherm", use_container_width=True):
    reset(False); st.rerun()

# Print screen
if st.session_state.screen == "print":
    st.markdown('<div class="hero"><h1>🖨️ Werkblad maken</h1><p>Stel een verzorgd A4-oefenblad samen.</p></div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        kind_label = st.radio("Welke oefeningen?", ["Sommen", "Tafels"], horizontal=True)
        kind = kind_label.lower()
        count = st.slider("Aantal oefeningen", 10, 100, 40, 5)
    with right:
        include_answers = st.checkbox("Voeg antwoordsleutel toe", value=False)

    if kind == "sommen":
        range_label = st.radio("Getallenbereik", ["0–10", "0–20", "0–50", "0–100"], horizontal=True)
        limit = int(range_label.split("–")[1])
        operation = st.radio("Bewerkingen", ["Sommen", "Verschillen", "Combinatie"], horizontal=True)
        tables = list(range(11))
    else:
        tables = st.multiselect("Welke tafels?", list(range(11)), default=list(range(11)))
        limit, operation = 100, "Combinatie"

    pages = math.ceil(count / 40)
    st.markdown(f'''<div class="card"><b>Afdrukindeling</b><br>
    • A4 staand, {pages} werkbladpagina{'s' if pages != 1 else ''}<br>
    • 4 kolommen met maximaal 10 oefeningen per kolom<br>
    • extra witruimte en een subtiele scheidingslijn na elke 5 rijen<br>
    • vijf puntjes bij elke oefening voor het antwoord<br>
    • ruimte voor naam en datum</div>''', unsafe_allow_html=True)

    if kind == "tafels" and not tables:
        st.warning("Kies minstens één tafel.")
    else:
        worksheet = make_worksheet_pdf(kind, count, limit, operation, tables, include_answers)
        st.download_button(
            "📄 Download het werkblad als PDF",
            worksheet,
            "rekenwerkblad.pdf",
            "application/pdf",
            use_container_width=True,
        )
    st.stop()

# Game setup and game
st.markdown(f'<div class="hero"><h1>{"✖️ Tafels" if st.session_state.kind == "tafels" else "➕➖ Sommen"}</h1><p>Kies je instellingen en start.</p></div>', unsafe_allow_html=True)
if not st.session_state.started:
    if st.session_state.kind == "tafels":
        tables = st.multiselect("Welke tafels?", range(11), default=range(11))
    else:
        range_label = st.radio("Getallenbereik", ["0–10", "0–20", "0–50", "0–100"], horizontal=True)
        limit = int(range_label.split("–")[1])
        operation = st.radio("Bewerkingen", ["Sommen", "Verschillen", "Combinatie"], horizontal=True)
    level = st.radio("Niveau", ["Gewoon", "Met tijdsklok", "Toetsniveau"], horizontal=True)
    mode = "Zelf invullen" if level == "Toetsniveau" else st.radio("Antwoorden", ["Meerkeuze", "Zelf invullen"], horizontal=True)
    rounds = 100 if level == "Toetsniveau" else st.slider("Aantal oefeningen", 5, 30, 10, 5)
    seconds = st.slider("Seconden per oefening", 3, 30, 10) if level == "Met tijdsklok" else 0
    valid = st.session_state.kind != "tafels" or bool(tables)
    if st.button("🚀 Start", use_container_width=True, disabled=not valid):
        st.session_state.started = True
        st.session_state.level, st.session_state.mode = level, mode
        st.session_state.rounds, st.session_state.seconds = rounds, seconds
        st.session_state.start = time.time()
        if st.session_state.kind == "tafels":
            st.session_state.tables = tables
        else:
            st.session_state.limit, st.session_state.operation = limit, operation
        if level == "Toetsniveau":
            st.session_state.test_deadline = time.time() + 600
        new_question(); st.rerun()
else:
    @st.fragment(run_every=1)
    def game_panel():
        if not st.session_state.finished:
            if st.session_state.level == "Toetsniveau" and time.time() >= st.session_state.test_deadline:
                finish("De 10 minuten zijn verstreken."); st.rerun()
            if st.session_state.level == "Met tijdsklok" and time.time() >= st.session_state.deadline:
                st.session_state.answered += 1; st.session_state.missed += 1
                if st.session_state.answered >= st.session_state.rounds:
                    finish("De reeks is voltooid.")
                else:
                    new_question()
                st.rerun()
        if st.session_state.finished:
            st.markdown('<div class="fire"><span class="spark"></span></div>', unsafe_allow_html=True)
            percentage = round(100 * st.session_state.correct / max(1, st.session_state.answered))
            elapsed = st.session_state.end - st.session_state.start
            st.markdown(f'<div class="card" style="text-align:center"><h1>🏆 Resultaat: {percentage}%</h1><p>{st.session_state.end_message}</p><p>Tijd: {int(elapsed)//60:02d}:{int(elapsed)%60:02d}</p></div>', unsafe_allow_html=True)
            st.write(f'✅ {st.session_state.correct} juist · ❌ {st.session_state.wrong} fout · ⏭️ {st.session_state.missed} onbeantwoord')
            if st.button("🔁 Opnieuw", use_container_width=True):
                reset(True); st.rerun()
            return
        if st.session_state.level == "Met tijdsklok":
            st.markdown(f'<div class="timer">⏱️ {max(0, int(st.session_state.deadline-time.time()))} seconden</div>', unsafe_allow_html=True)
        if st.session_state.level == "Toetsniveau":
            remaining = int(max(0, st.session_state.test_deadline-time.time()))
            st.markdown(f'<div class="timer">⏱️ {remaining//60:02d}:{remaining%60:02d}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card question">{st.session_state.a} {st.session_state.operator} {st.session_state.b} = ?</div>', unsafe_allow_html=True)
        if st.session_state.mode == "Meerkeuze":
            columns = st.columns(2)
            for index, choice in enumerate(st.session_state.choices):
                with columns[index % 2]:
                    st.button(str(choice), key=f'{st.session_state.answered}-{choice}', use_container_width=True, on_click=submit_answer, args=(choice,), disabled=st.session_state.locked)
        else:
            with st.form(f'answer-{st.session_state.answered}'):
                value = st.number_input("Antwoord", min_value=0, max_value=100, value=None, step=1)
                submitted = st.form_submit_button("Bevestig", use_container_width=True)
                if submitted and value is not None:
                    submit_answer(int(value)); st.rerun()
        if st.session_state.level != "Toetsniveau" and st.session_state.feedback:
            (st.success if st.session_state.feedback.startswith("✅") else st.warning)(st.session_state.feedback)
            if st.button("Volgende ➜", use_container_width=True):
                new_question(); st.rerun()
        st.divider()
        if st.session_state.level == "Toetsniveau":
            st.progress(st.session_state.answered / 100, text=f'{st.session_state.answered}/100')
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("⭐", st.session_state.score); c2.metric("🔥", st.session_state.streak)
            c3.metric("❤️", st.session_state.lives); c4.metric("⚡", st.session_state.xp)
            st.progress(st.session_state.answered / st.session_state.rounds)
    game_panel()
