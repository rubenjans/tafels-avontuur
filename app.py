import io, random, time
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor

st.set_page_config(page_title='Rekenavontuur',page_icon='🧮',layout='centered')
st.markdown('''<style>.stApp{background:linear-gradient(135deg,#eef7ff,#fff4dc,#f4eaff)}.block-container{max-width:900px}.hero{background:linear-gradient(120deg,#5b5ff0,#9b5de5);color:white;padding:24px;border-radius:24px;text-align:center}.card{background:#fffffff0;padding:20px;border-radius:22px;box-shadow:0 8px 24px #1e293b1a;margin:14px 0}.question{font-size:3rem;font-weight:850;text-align:center;color:#30345f}.timer{text-align:center;font-weight:800;background:#fff3b0;padding:10px;border-radius:14px}div.stButton>button,[data-testid="stFormSubmitButton"] button{border-radius:16px;min-height:50px;font-weight:750}.fire{position:fixed;inset:0;pointer-events:none;z-index:9999}.spark{position:absolute;width:8px;height:8px;left:50%;top:35%;border-radius:50%;animation:b 1.8s infinite;box-shadow:0 -90px #f33,64px -64px #fd3,90px 0 #0c8,64px 64px #29f,0 90px #95e,-64px 64px #f80,-90px 0 #f38,-64px -64px #0dd}@keyframes b{0%{transform:scale(.05);opacity:1}100%{transform:scale(1.8);opacity:0}}@media(max-width:600px){.question{font-size:2.5rem}.hero h1{font-size:1.7rem}}</style>''',unsafe_allow_html=True)

D={'screen':'home','started':False,'finished':False,'score':0,'streak':0,'best':0,'lives':3,'answered':0,'correct':0,'wrong':0,'missed':0,'locked':False,'feedback':'','xp':0,'start':0,'end':0}
for k,v in D.items():
    if k not in st.session_state: st.session_state[k]=v

def reset(keep=True):
    screen=st.session_state.screen if keep else 'home'
    for k,v in D.items(): st.session_state[k]=v
    st.session_state.screen=screen

def exercise(kind,limit=10,operation='Combinatie',tables=None):
    if kind=='tafels':
        a=random.choice(tables); b=random.randint(0,10); op='×'; ans=a*b; cap=100
    else:
        op=random.choice(['+','−']) if operation=='Combinatie' else ('+' if operation=='Sommen' else '−'); cap=limit
        if op=='+': a=random.randint(0,limit); b=random.randint(0,limit-a); ans=a+b
        else: a=random.randint(0,limit); b=random.randint(0,a); ans=a-b
    return a,b,op,ans,cap

def newq():
    a,b,op,ans,cap=exercise(st.session_state.kind,st.session_state.get('limit',10),st.session_state.get('operation','Combinatie'),st.session_state.get('tables',list(range(11))))
    opts={ans}
    while len(opts)<4: opts.add(max(0,min(cap,ans+random.choice([-10,-5,-3,-2,-1,1,2,3,5,10]))))
    st.session_state.a=a;st.session_state.b=b;st.session_state.op=op;st.session_state.ans=ans;st.session_state.opts=list(opts);random.shuffle(st.session_state.opts);st.session_state.locked=False;st.session_state.feedback=''
    if st.session_state.level=='Met tijdsklok': st.session_state.deadline=time.time()+st.session_state.seconds

def finish(msg):
    st.session_state.finished=True;st.session_state.end=time.time();st.session_state.msg=msg

def answer(x):
    if st.session_state.locked:return
    test=st.session_state.level=='Toetsniveau';st.session_state.locked=True;st.session_state.answered+=1
    if x==st.session_state.ans:
        st.session_state.correct+=1;st.session_state.streak+=1;st.session_state.best=max(st.session_state.best,st.session_state.streak)
        if not test:st.session_state.score+=10;st.session_state.xp+=20;st.session_state.feedback='✅ Juist!'
    else:
        st.session_state.wrong+=1;st.session_state.streak=0
        if not test:st.session_state.lives-=1;st.session_state.feedback=f'💡 Het juiste antwoord is {st.session_state.ans}.'
    if test:
        if st.session_state.answered>=100:finish('Alle 100 oefeningen zijn ingevuld.')
        else:newq()
    elif st.session_state.answered>=st.session_state.rounds or st.session_state.lives<=0:finish('De reeks is voltooid.')

def make_pdf(kind,count,limit,operation,tables):
    data=[exercise(kind,limit,operation,tables)[:4] for _ in range(count)]
    buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=A4); W,H=A4
    per_page=40; cols=4; rows=10; margin=42; top=H-92; colw=(W-2*margin)/cols; normal=34; gap=52
    for start in range(0,len(data),per_page):
        c.setFillColor(HexColor('#4f46e5'));c.setFont('Helvetica-Bold',18);c.drawString(margin,H-48,'Rekenoefeningen')
        c.setFillColor(HexColor('#333333'));c.setFont('Helvetica',10);c.drawString(margin,H-67,'Naam: ________________________________    Datum: _______________')
        for i,(a,b,op,ans) in enumerate(data[start:start+per_page]):
            col=i//rows; row=i%rows; y=top-row*normal-(gap-normal if row>=5 else 0); x=margin+col*colw
            c.setFont('Helvetica',12);c.drawString(x,y,f'{start+i+1}.  {a} {op} {b} = .....')
        c.setFont('Helvetica',8);c.setFillColor(HexColor('#777777'));c.drawRightString(W-margin,24,f'Blad {start//per_page+1}')
        c.showPage()
    c.save();buf.seek(0);return buf.getvalue()

# HOME
if st.session_state.screen=='home':
    st.markdown('<div class="hero"><h1>🧮 Rekenavontuur</h1><p>Wat wil je vandaag doen?</p></div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a:
        st.markdown('<div class="card"><h2>➕➖ Sommen</h2><p>Optellen en aftrekken.</p></div>',unsafe_allow_html=True)
        if st.button('Sommen oefenen',use_container_width=True):st.session_state.screen='game';st.session_state.kind='sommen';st.rerun()
    with b:
        st.markdown('<div class="card"><h2>✖️ Tafels</h2><p>Maaltafels van 0 tot 10.</p></div>',unsafe_allow_html=True)
        if st.button('Tafels oefenen',use_container_width=True):st.session_state.screen='game';st.session_state.kind='tafels';st.rerun()
    with c:
        st.markdown('<div class="card"><h2>🖨️ Afdrukken</h2><p>Maak een werkblad als PDF.</p></div>',unsafe_allow_html=True)
        if st.button('Werkblad maken',use_container_width=True):st.session_state.screen='print';st.rerun()
    st.stop()

if st.sidebar.button('🏠 Startscherm',use_container_width=True):reset(False);st.rerun()

# PRINT SCREEN
if st.session_state.screen=='print':
    st.markdown('<div class="hero"><h1>🖨️ Werkblad maken</h1><p>Stel een afdrukbaar oefenblad samen.</p></div>',unsafe_allow_html=True)
    kind_label=st.radio('Welke oefeningen?',['Sommen','Tafels'],horizontal=True);kind=kind_label.lower()
    count=st.slider('Aantal oefeningen',10,100,40,5)
    if kind=='sommen':
        r=st.radio('Getallenbereik',['0–10','0–20','0–50','0–100'],horizontal=True);limit=int(r.split('–')[1]);operation=st.radio('Bewerkingen',['Sommen','Verschillen','Combinatie'],horizontal=True);tables=list(range(11))
    else:
        tables=st.multiselect('Welke tafels?',list(range(11)),default=list(range(11)));limit=100;operation='Combinatie'
    st.info('Het PDF-werkblad gebruikt 4 kolommen. Na elke 5 rijen staat extra witruimte. Elke oefening eindigt met vijf puntjes.')
    if kind=='tafels' and not tables:st.warning('Kies minstens één tafel.')
    else:
        pdf=make_pdf(kind,count,limit,operation,tables)
        st.download_button('📄 Download werkblad als PDF',pdf,'rekenoefeningen.pdf','application/pdf',use_container_width=True)
    st.stop()

# GAME SETUP
st.markdown(f'<div class="hero"><h1>{"✖️ Tafels" if st.session_state.kind=="tafels" else "➕➖ Sommen"}</h1><p>Kies je instellingen en start.</p></div>',unsafe_allow_html=True)
if not st.session_state.started:
    if st.session_state.kind=='tafels': tables=st.multiselect('Welke tafels?',range(11),default=range(11))
    else:
        r=st.radio('Getallenbereik',['0–10','0–20','0–50','0–100'],horizontal=True);limit=int(r.split('–')[1]);operation=st.radio('Bewerkingen',['Sommen','Verschillen','Combinatie'],horizontal=True)
    level=st.radio('Niveau',['Gewoon','Met tijdsklok','Toetsniveau'],horizontal=True)
    mode='Zelf invullen' if level=='Toetsniveau' else st.radio('Antwoorden',['Meerkeuze','Zelf invullen'],horizontal=True)
    rounds=100 if level=='Toetsniveau' else st.slider('Aantal oefeningen',5,30,10,5)
    seconds=st.slider('Seconden per oefening',3,30,10) if level=='Met tijdsklok' else 0
    valid=st.session_state.kind!='tafels' or bool(tables)
    if st.button('🚀 Start',use_container_width=True,disabled=not valid):
        st.session_state.started=True;st.session_state.level=level;st.session_state.mode=mode;st.session_state.rounds=rounds;st.session_state.seconds=seconds;st.session_state.start=time.time()
        if st.session_state.kind=='tafels':st.session_state.tables=tables
        else:st.session_state.limit=limit;st.session_state.operation=operation
        if level=='Toetsniveau':st.session_state.test_deadline=time.time()+600
        newq();st.rerun()
else:
    @st.fragment(run_every=1)
    def panel():
        if not st.session_state.finished:
            if st.session_state.level=='Toetsniveau' and time.time()>=st.session_state.test_deadline:finish('De 10 minuten zijn verstreken.');st.rerun()
            if st.session_state.level=='Met tijdsklok' and time.time()>=st.session_state.deadline:
                st.session_state.answered+=1;st.session_state.missed+=1
                if st.session_state.answered>=st.session_state.rounds:finish('De reeks is voltooid.')
                else:newq()
                st.rerun()
        if st.session_state.finished:
            st.markdown('<div class="fire"><span class="spark"></span></div>',unsafe_allow_html=True);pct=round(100*st.session_state.correct/max(1,st.session_state.answered));elapsed=st.session_state.end-st.session_state.start
            st.markdown(f'<div class="card" style="text-align:center"><h1>🏆 Resultaat: {pct}%</h1><p>{st.session_state.msg}</p><p>Tijd: {int(elapsed)//60:02d}:{int(elapsed)%60:02d}</p></div>',unsafe_allow_html=True)
            st.write(f'✅ {st.session_state.correct} juist · ❌ {st.session_state.wrong} fout · ⏭️ {st.session_state.missed} onbeantwoord')
            if st.button('🔁 Opnieuw',use_container_width=True):reset(True);st.rerun()
            return
        if st.session_state.level=='Met tijdsklok':st.markdown(f'<div class="timer">⏱️ {max(0,int(st.session_state.deadline-time.time()))} seconden</div>',unsafe_allow_html=True)
        if st.session_state.level=='Toetsniveau':st.markdown(f'<div class="timer">⏱️ {int(max(0,st.session_state.test_deadline-time.time()))//60:02d}:{int(max(0,st.session_state.test_deadline-time.time()))%60:02d}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="card question">{st.session_state.a} {st.session_state.op} {st.session_state.b} = ?</div>',unsafe_allow_html=True)
        if st.session_state.mode=='Meerkeuze':
            cols=st.columns(2)
            for i,x in enumerate(st.session_state.opts):
                with cols[i%2]:st.button(str(x),key=f'{st.session_state.answered}-{x}',use_container_width=True,on_click=answer,args=(x,),disabled=st.session_state.locked)
        else:
            with st.form(f'f{st.session_state.answered}'):
                x=st.number_input('Antwoord',min_value=0,max_value=100,value=None,step=1);go=st.form_submit_button('Bevestig',use_container_width=True)
                if go and x is not None:answer(int(x));st.rerun()
        if st.session_state.level!='Toetsniveau' and st.session_state.feedback:
            (st.success if st.session_state.feedback.startswith('✅') else st.warning)(st.session_state.feedback)
            if st.button('Volgende ➜',use_container_width=True):newq();st.rerun()
        st.divider()
        if st.session_state.level=='Toetsniveau':st.progress(st.session_state.answered/100,text=f'{st.session_state.answered}/100')
        else:
            c1,c2,c3,c4=st.columns(4);c1.metric('⭐',st.session_state.score);c2.metric('🔥',st.session_state.streak);c3.metric('❤️',st.session_state.lives);c4.metric('⚡',st.session_state.xp);st.progress(st.session_state.answered/st.session_state.rounds)
    panel()
