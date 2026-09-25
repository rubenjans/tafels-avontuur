import io
import random
import time

import streamlit as st
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Rekenavontuur", page_icon="🧮", layout="centered")
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#eef7ff,#fff4dc,#f4eaff)}
.block-container{max-width:920px;padding-top:1.2rem}.hero{background:linear-gradient(120deg,#5b5ff0,#9b5de5);color:white;padding:24px;border-radius:24px;text-align:center}.hero h1{margin:0}.card{background:#fffffff0;padding:20px;border-radius:22px;box-shadow:0 8px 24px #1e293b1a;margin:14px 0}.question{font-size:3rem;font-weight:850;text-align:center;color:#30345f}.timer{text-align:center;font-weight:800;background:#fff3b0;padding:10px;border-radius:14px}div.stButton>button,[data-testid="stFormSubmitButton"] button{border-radius:16px;min-height:50px;font-weight:750}.fire{position:fixed;inset:0;pointer-events:none;z-index:9999}.spark{position:absolute;width:8px;height:8px;left:50%;top:35%;border-radius:50%;animation:b 1.8s infinite;box-shadow:0 -90px #f33,64px -64px #fd3,90px 0 #0c8,64px 64px #29f,0 90px #95e,-64px 64px #f80,-90px 0 #f38,-64px -64px #0dd}@keyframes b{0%{transform:scale(.05);opacity:1}100%{transform:scale(1.8);opacity:0}}@media(max-width:600px){.question{font-size:2.5rem}.hero h1{font-size:1.7rem}}
</style>
""", unsafe_allow_html=True)

DEFAULTS={"screen":"home","started":False,"finished":False,"score":0,"streak":0,"best":0,"lives":3,"xp":0,"answered":0,"correct":0,"wrong":0,"missed":0,"locked":False,"feedback":"","start":0.0,"end":0.0}
for key,value in DEFAULTS.items():
    if key not in st.session_state: st.session_state[key]=value

def reset(keep_screen=True):
    screen=st.session_state.screen if keep_screen else "home"
    for key,value in DEFAULTS.items(): st.session_state[key]=value
    st.session_state.screen=screen

def create_exercise(kind,limit=10,operation="Combinatie",tables=None):
    if kind=="tafels":
        a=random.choice(tables); b=random.randint(0,10)
        return a,b,"×",a*b,100
    operator=random.choice(["+","−"]) if operation=="Combinatie" else ("+" if operation=="Sommen" else "−")
    if operator=="+":
        a=random.randint(0,limit); b=random.randint(0,limit-a); answer=a+b
    else:
        a=random.randint(0,limit); b=random.randint(0,a); answer=a-b
    return a,b,operator,answer,limit

def new_question():
    a,b,operator,answer,cap=create_exercise(st.session_state.kind,st.session_state.get("limit",10),st.session_state.get("operation","Combinatie"),st.session_state.get("tables",list(range(11))))
    choices={answer}
    while len(choices)<4: choices.add(max(0,min(cap,answer+random.choice([-10,-5,-3,-2,-1,1,2,3,5,10]))))
    st.session_state.a=a; st.session_state.b=b; st.session_state.operator=operator; st.session_state.answer=answer
    st.session_state.choices=list(choices); random.shuffle(st.session_state.choices)
    st.session_state.locked=False; st.session_state.feedback=""
    if st.session_state.level=="Met tijdsklok": st.session_state.deadline=time.time()+st.session_state.seconds

def finish(message):
    if not st.session_state.finished:
        st.session_state.finished=True; st.session_state.end=time.time(); st.session_state.end_message=message

def submit_answer(value):
    if st.session_state.locked or st.session_state.finished: return
    test=st.session_state.level=="Toetsniveau"; st.session_state.locked=True; st.session_state.answered+=1
    if value==st.session_state.answer:
        st.session_state.correct+=1; st.session_state.streak+=1; st.session_state.best=max(st.session_state.best,st.session_state.streak)
        if not test: st.session_state.score+=10; st.session_state.xp+=20; st.session_state.feedback="✅ Juist!"
    else:
        st.session_state.wrong+=1; st.session_state.streak=0
        if not test: st.session_state.lives-=1; st.session_state.feedback=f"💡 Het juiste antwoord is {st.session_state.answer}."
    if test:
        if st.session_state.answered>=100: finish("Alle 100 oefeningen zijn ingevuld.")
        else: new_question()
    elif st.session_state.answered>=st.session_state.rounds or st.session_state.lives<=0: finish("De reeks is voltooid.")

def pdf_operator(operator):
    return "x" if operator=="×" else "-" if operator=="−" else operator

def make_worksheet_pdf(kind,count,limit,operation,tables):
    """Maak maximaal 100 oefeningen op exact één A4 in 4 kolommen x 5 groep-rijen.

    Elke groep bevat 5 oefeningen. Bij 100 oefeningen zijn er dus 20 groepen:
    4 kolommen x 5 groep-rijen x 5 oefeningen = 100 oefeningen.
    """
    exercises=[create_exercise(kind,limit,operation,tables)[:4] for _ in range(count)]
    output=io.BytesIO(); pdf=canvas.Canvas(output,pagesize=A4); width,height=A4

    margin_x=27
    header_bottom=height-91
    footer_top=27
    columns=4
    group_rows=5
    exercises_per_group=5
    gutter=13
    content_width=width-2*margin_x
    column_width=(content_width-(columns-1)*gutter)/columns
    grid_top=header_bottom-10
    grid_bottom=footer_top+11
    grid_height=grid_top-grid_bottom
    group_height=grid_height/group_rows
    line_height=group_height/exercises_per_group

    title="Werkblad tafels" if kind=="tafels" else "Werkblad sommen en verschillen"
    subtitle=("Tafels: "+", ".join(str(t) for t in tables)) if kind=="tafels" else f"Bereik 0-{limit} | {operation}"

    pdf.setFillColor(HexColor("#4F46E5")); pdf.roundRect(margin_x,height-68,width-2*margin_x,36,8,fill=1,stroke=0)
    pdf.setFillColor(HexColor("#FFFFFF")); pdf.setFont("Helvetica-Bold",16); pdf.drawString(margin_x+12,height-50,title)
    pdf.setFont("Helvetica",7.5); pdf.drawRightString(width-margin_x-12,height-50,subtitle)
    pdf.setFillColor(HexColor("#25253A")); pdf.setFont("Helvetica",9)
    pdf.drawString(margin_x,height-82,"Naam: ______________________________")
    pdf.drawRightString(width-margin_x,height-82,"Datum: ____ / ____ / ______")

    # 20 groepvakken: 4 kolommen en 5 rijen. Geen nummering en geen opsommingstekens.
    for group_index in range(20):
        start=group_index*exercises_per_group
        group=exercises[start:start+exercises_per_group]
        if not group: break
        column=group_index%columns
        group_row=group_index//columns
        x=margin_x+column*(column_width+gutter)
        group_top=grid_top-group_row*group_height

        # Subtiele scheiding tussen groepen, met witruimte aan alle zijden.
        pdf.setStrokeColor(HexColor("#E1E1EE")); pdf.setLineWidth(0.45)
        if group_row>0: pdf.line(x,group_top+2,x+column_width,group_top+2)

        for local_index,(a,b,operator,_answer) in enumerate(group):
            y=group_top-(local_index+0.72)*line_height
            pdf.setFillColor(HexColor("#202238")); pdf.setFont("Helvetica-Bold",10.5)
            pdf.drawString(x+3,y,f"{a} {pdf_operator(operator)} {b} = ..")

    # Lichte verticale scheiding tussen de vier kolommen.
    for column in range(1,columns):
        x=margin_x+column*column_width+(column-0.5)*gutter
        pdf.setStrokeColor(HexColor("#E1E1EE")); pdf.setLineWidth(0.45); pdf.line(x,grid_bottom,x,grid_top)

    pdf.setStrokeColor(HexColor("#D9D9E8")); pdf.line(margin_x,footer_top,width-margin_x,footer_top)
    pdf.setFillColor(HexColor("#77778C")); pdf.setFont("Helvetica",7.5)
    pdf.drawString(margin_x,15,f"{count} oefeningen | 4 kolommen | groepen van 5")
    pdf.drawRightString(width-margin_x,15,"Score: ______ / ______")
    pdf.showPage(); pdf.save(); output.seek(0)
    return output.getvalue()

# STARTSCHERM
if st.session_state.screen=="home":
    st.markdown('<div class="hero"><h1>🧮 Rekenavontuur</h1><p>Wat wil je vandaag doen?</p></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown('<div class="card"><h2>➕➖ Sommen</h2><p>Optellen en aftrekken.</p></div>',unsafe_allow_html=True)
        if st.button("Sommen oefenen",use_container_width=True): st.session_state.screen="game"; st.session_state.kind="sommen"; st.rerun()
    with c2:
        st.markdown('<div class="card"><h2>✖️ Tafels</h2><p>Maaltafels van 0 tot 10.</p></div>',unsafe_allow_html=True)
        if st.button("Tafels oefenen",use_container_width=True): st.session_state.screen="game"; st.session_state.kind="tafels"; st.rerun()
    with c3:
        st.markdown('<div class="card"><h2>🖨️ Afdrukken</h2><p>Maak een PDF-werkblad.</p></div>',unsafe_allow_html=True)
        if st.button("Werkblad maken",use_container_width=True): st.session_state.screen="print"; st.rerun()
    st.stop()

if st.sidebar.button("🏠 Startscherm",use_container_width=True): reset(False); st.rerun()

# PRINTSCHERM
if st.session_state.screen=="print":
    st.markdown('<div class="hero"><h1>🖨️ Werkblad maken</h1><p>Tot 100 oefeningen op één A4.</p></div>',unsafe_allow_html=True)
    kind_label=st.radio("Welke oefeningen?",["Sommen","Tafels"],horizontal=True); kind=kind_label.lower()
    count=st.slider("Aantal oefeningen",10,100,100,5)
    if kind=="sommen":
        range_label=st.radio("Getallenbereik",["0–10","0–20","0–50","0–100"],horizontal=True)
        limit=int(range_label.split("–")[1]); operation=st.radio("Bewerkingen",["Sommen","Verschillen","Combinatie"],horizontal=True); tables=list(range(11))
    else:
        tables=st.multiselect("Welke tafels?",list(range(11)),default=list(range(11))); limit=100; operation="Combinatie"
    st.markdown('<div class="card"><b>Nieuwe afdrukindeling</b><br>Maximaal 100 oefeningen op één A4, zonder nummering of opsommingstekens. De oefeningen staan in 4 kolommen en 5 groep-rijen. Elke groep bevat 5 oefeningen. Na het gelijkheidsteken staan twee puntjes.</div>',unsafe_allow_html=True)
    if kind=="tafels" and not tables: st.warning("Kies minstens één tafel.")
    else:
        worksheet=make_worksheet_pdf(kind,count,limit,operation,tables)
        st.download_button("📄 Download het werkblad als PDF",worksheet,"rekenwerkblad.pdf","application/pdf",use_container_width=True)
    st.stop()

# SPELINSTELLINGEN
st.markdown(f'<div class="hero"><h1>{"✖️ Tafels" if st.session_state.kind=="tafels" else "➕➖ Sommen"}</h1><p>Kies je instellingen en start.</p></div>',unsafe_allow_html=True)
if not st.session_state.started:
    if st.session_state.kind=="tafels": tables=st.multiselect("Welke tafels?",range(11),default=range(11))
    else:
        range_label=st.radio("Getallenbereik",["0–10","0–20","0–50","0–100"],horizontal=True); limit=int(range_label.split("–")[1]); operation=st.radio("Bewerkingen",["Sommen","Verschillen","Combinatie"],horizontal=True)
    level=st.radio("Niveau",["Gewoon","Met tijdsklok","Toetsniveau"],horizontal=True)
    mode="Zelf invullen" if level=="Toetsniveau" else st.radio("Antwoorden",["Meerkeuze","Zelf invullen"],horizontal=True)
    rounds=100 if level=="Toetsniveau" else st.slider("Aantal oefeningen",5,30,10,5)
    seconds=st.slider("Seconden per oefening",3,30,10) if level=="Met tijdsklok" else 0
    valid=st.session_state.kind!="tafels" or bool(tables)
    if st.button("🚀 Start",use_container_width=True,disabled=not valid):
        st.session_state.started=True; st.session_state.level=level; st.session_state.mode=mode; st.session_state.rounds=rounds; st.session_state.seconds=seconds; st.session_state.start=time.time()
        if st.session_state.kind=="tafels": st.session_state.tables=tables
        else: st.session_state.limit=limit; st.session_state.operation=operation
        if level=="Toetsniveau": st.session_state.test_deadline=time.time()+600
        new_question(); st.rerun()
else:
    @st.fragment(run_every=1)
    def game_panel():
        if not st.session_state.finished:
            if st.session_state.level=="Toetsniveau" and time.time()>=st.session_state.test_deadline: finish("De 10 minuten zijn verstreken."); st.rerun()
            if st.session_state.level=="Met tijdsklok" and time.time()>=st.session_state.deadline:
                st.session_state.answered+=1; st.session_state.missed+=1
                if st.session_state.answered>=st.session_state.rounds: finish("De reeks is voltooid.")
                else: new_question()
                st.rerun()
        if st.session_state.finished:
            st.markdown('<div class="fire"><span class="spark"></span></div>',unsafe_allow_html=True)
            percentage=round(100*st.session_state.correct/max(1,st.session_state.answered)); elapsed=st.session_state.end-st.session_state.start
            st.markdown(f'<div class="card" style="text-align:center"><h1>🏆 Resultaat: {percentage}%</h1><p>{st.session_state.end_message}</p><p>Tijd: {int(elapsed)//60:02d}:{int(elapsed)%60:02d}</p></div>',unsafe_allow_html=True)
            st.write(f'✅ {st.session_state.correct} juist · ❌ {st.session_state.wrong} fout · ⏭️ {st.session_state.missed} onbeantwoord')
            if st.button("🔁 Opnieuw",use_container_width=True): reset(True); st.rerun()
            return
        if st.session_state.level=="Met tijdsklok": st.markdown(f'<div class="timer">⏱️ {max(0,int(st.session_state.deadline-time.time()))} seconden</div>',unsafe_allow_html=True)
        if st.session_state.level=="Toetsniveau":
            remaining=int(max(0,st.session_state.test_deadline-time.time())); st.markdown(f'<div class="timer">⏱️ {remaining//60:02d}:{remaining%60:02d}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="card question">{st.session_state.a} {st.session_state.operator} {st.session_state.b} = ?</div>',unsafe_allow_html=True)
        if st.session_state.mode=="Meerkeuze":
            columns=st.columns(2)
            for index,choice in enumerate(st.session_state.choices):
                with columns[index%2]: st.button(str(choice),key=f'{st.session_state.answered}-{choice}',use_container_width=True,on_click=submit_answer,args=(choice,),disabled=st.session_state.locked)
        else:
            with st.form(f'answer-{st.session_state.answered}'):
                value=st.number_input("Antwoord",min_value=0,max_value=100,value=None,step=1); submitted=st.form_submit_button("Bevestig",use_container_width=True)
                if submitted and value is not None: submit_answer(int(value)); st.rerun()
        if st.session_state.level!="Toetsniveau" and st.session_state.feedback:
            (st.success if st.session_state.feedback.startswith("✅") else st.warning)(st.session_state.feedback)
            if st.button("Volgende ➜",use_container_width=True): new_question(); st.rerun()
        st.divider()
        if st.session_state.level=="Toetsniveau": st.progress(st.session_state.answered/100,text=f'{st.session_state.answered}/100')
        else:
            c1,c2,c3,c4=st.columns(4); c1.metric("⭐",st.session_state.score); c2.metric("🔥",st.session_state.streak); c3.metric("❤️",st.session_state.lives); c4.metric("⚡",st.session_state.xp); st.progress(st.session_state.answered/st.session_state.rounds)
    game_panel()
