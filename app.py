import random
import time
import streamlit as st

st.set_page_config(page_title="Tafels Avontuur", page_icon="🚀", layout="centered")
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#eef7ff,#fff4dc 55%,#f4eaff)}
.block-container{max-width:900px;padding-top:1.3rem}.hero{background:linear-gradient(120deg,#5b5ff0,#9b5de5);color:white;padding:24px;border-radius:24px;text-align:center;box-shadow:0 12px 30px #5b5ff038}.hero h1{margin:0;font-size:2.35rem}.hero p{margin:.5rem 0 0}.card{background:#ffffffe8;padding:18px;border-radius:22px;box-shadow:0 8px 24px #1e293b1a;margin:12px 0}.question{font-size:3.1rem;font-weight:850;color:#30345f;text-align:center;margin:12px 0}.badge{display:inline-block;background:#fff3b0;padding:7px 11px;border-radius:999px;margin:4px;font-weight:700}.timer{font-size:1.2rem;font-weight:800;text-align:center;padding:10px;border-radius:14px;background:#fff3b0;color:#6b4f00;margin:8px 0}.stats-title{text-align:center;color:#596275;font-size:.9rem;margin-top:.2rem}div.stButton>button,[data-testid="stFormSubmitButton"] button{border-radius:16px;font-weight:750;min-height:48px;border:0;background:#5b5ff0;color:white}[data-testid="stMetric"]{background:white;border-radius:18px;padding:10px;box-shadow:0 4px 14px #1e293b14}.fireworks{position:fixed;inset:0;pointer-events:none;z-index:9999;overflow:hidden}.firework{position:absolute;width:8px;height:8px;border-radius:50%;animation:burst 1.8s ease-out infinite;box-shadow:0 -70px #ff4d6d,49px -49px #ffd166,70px 0 #06d6a0,49px 49px #4cc9f0,0 70px #9b5de5,-49px 49px #ff9f1c,-70px 0 #f72585,-49px -49px #00f5d4}.f1{left:20%;top:35%}.f2{left:50%;top:22%;animation-delay:.55s}.f3{left:78%;top:38%;animation-delay:1.05s}.f4{left:35%;top:60%;animation-delay:1.35s}@keyframes burst{0%{transform:scale(.05);opacity:1}65%{transform:scale(1.35);opacity:1}100%{transform:scale(1.8);opacity:0}}@media(max-width:600px){.block-container{padding:.7rem}.hero{padding:16px}.hero h1{font-size:1.8rem}.question{font-size:2.7rem}[data-testid="stMetric"]{padding:7px}}
</style>
""", unsafe_allow_html=True)

DEFAULTS={"started":False,"finished":False,"score":0,"streak":0,"best":0,"lives":3,"answered":0,"correct":0,"wrong":0,"timed_out":0,"a":2,"b":2,"choices":[],"feedback":"","locked":False,"xp":0,"badges":set(),"game_start":None,"finished_at":None,"deadline":None,"end_reason":""}
for key,value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key]=value.copy() if isinstance(value,set) else value

def reset_game():
    for key,value in DEFAULTS.items():
        st.session_state[key]=value.copy() if isinstance(value,set) else value

def new_question():
    a=random.choice(st.session_state.tables); b=random.randint(0,10); right=a*b; options={right}
    while len(options)<4:
        options.add(max(0,right+random.choice([-10,-5,-3,-2,-1,1,2,3,5,10])))
    st.session_state.a=a; st.session_state.b=b; st.session_state.choices=list(options)
    random.shuffle(st.session_state.choices)
    st.session_state.feedback=""; st.session_state.locked=False
    if st.session_state.level=="Met tijdsklok":
        st.session_state.deadline=time.time()+st.session_state.seconds_per_sum

def finish(reason):
    if not st.session_state.finished:
        st.session_state.finished=True; st.session_state.finished_at=time.time()
        st.session_state.end_reason=reason; st.session_state.deadline=None

def update_badges():
    if st.session_state.correct>=1: st.session_state.badges.add("🌟 Eerste ster")
    if st.session_state.streak>=5: st.session_state.badges.add("🔥 Reeks van 5")
    if st.session_state.correct>=10: st.session_state.badges.add("🧠 Tafelbrein")

def process_answer(value):
    if st.session_state.locked or st.session_state.finished: return
    test=st.session_state.level=="Toetsniveau"
    st.session_state.locked=True; st.session_state.answered+=1
    if value==st.session_state.a*st.session_state.b:
        st.session_state.correct+=1; st.session_state.streak+=1
        st.session_state.best=max(st.session_state.best,st.session_state.streak)
        if not test:
            bonus=min(st.session_state.streak-1,5)*2
            st.session_state.score+=10+bonus; st.session_state.xp+=20+bonus
            st.session_state.feedback=f"✅ Juist! +{10+bonus} punten en +{20+bonus} XP"
            update_badges()
    else:
        st.session_state.wrong+=1; st.session_state.streak=0
        if not test:
            st.session_state.lives-=1
            st.session_state.feedback=f"💡 Bijna! Het juiste antwoord is {st.session_state.a*st.session_state.b}."
    if test:
        finish("Alle 100 rekensommen zijn ingevuld.") if st.session_state.answered>=100 else new_question()
    elif st.session_state.answered>=st.session_state.rounds or st.session_state.lives<=0:
        finish("De oefenreeks is voltooid.")

def skip_timed_question():
    st.session_state.answered+=1; st.session_state.timed_out+=1; st.session_state.streak=0
    finish("De oefenreeks is voltooid.") if st.session_state.answered>=st.session_state.rounds else new_question()

def format_time(seconds):
    seconds=max(0,int(seconds)); return f"{seconds//60:02d}:{seconds%60:02d}"

def fireworks():
    st.markdown('<div class="fireworks"><span class="firework f1"></span><span class="firework f2"></span><span class="firework f3"></span><span class="firework f4"></span></div>',unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🚀 Tafels Avontuur</h1><p>Oefen de tafels van 0 tot en met 10 op jouw niveau.</p></div>',unsafe_allow_html=True)
with st.sidebar:
    st.header("🎮 Spelinstellingen")
    tables=st.multiselect("Welke tafels wil je oefenen?",list(range(11)),default=list(range(11)),disabled=st.session_state.started)
    level=st.radio("Niveau",["Gewoon","Met tijdsklok","Toetsniveau"],disabled=st.session_state.started)
    if level!="Toetsniveau":
        answer_mode=st.radio("Hoe wil je antwoorden?",["Meerkeuze","Zelf invullen"],horizontal=True,disabled=st.session_state.started)
        rounds=st.slider("Aantal vragen",5,30,10,5,disabled=st.session_state.started)
    else:
        answer_mode="Zelf invullen"; rounds=100
        st.info("📝 Toets: 100 rekensommen, 10 minuten, alleen zelf invullen en geen tussentijdse feedback.")
    seconds_per_sum=st.slider("Seconden per rekensom",3,30,10,1,disabled=st.session_state.started) if level=="Met tijdsklok" else None
    if st.button("🔄 Nieuw spel",use_container_width=True): reset_game(); st.rerun()
    st.caption("Er wordt geen klassement of persoonlijke informatie opgeslagen.")

if not st.session_state.started:
    st.markdown('<div class="card"><h3>🪐 Kies je uitdaging</h3><p><b>Gewoon:</b> oefenen zonder klok.<br><b>Met tijdsklok:</b> kies de tijd per rekensom.<br><b>Toetsniveau:</b> 100 invulvragen in maximaal 10 minuten, zonder tussentijdse feedback.</p></div>',unsafe_allow_html=True)
    if not tables: st.warning("Kies minstens één tafel.")
    if st.button("🚀 Start avontuur",use_container_width=True,disabled=not tables):
        st.session_state.started=True; st.session_state.tables=tables; st.session_state.level=level
        st.session_state.answer_mode=answer_mode; st.session_state.rounds=rounds
        st.session_state.seconds_per_sum=seconds_per_sum; st.session_state.game_start=time.time()
        if level=="Toetsniveau": st.session_state.test_deadline=time.time()+600
        new_question(); st.rerun()
else:
    @st.fragment(run_every=1)
    def game_panel():
        if not st.session_state.finished:
            now=time.time()
            if st.session_state.level=="Toetsniveau" and now>=st.session_state.test_deadline:
                finish("De 10 minuten zijn verstreken."); st.rerun()
            if st.session_state.level=="Met tijdsklok" and now>=st.session_state.deadline:
                skip_timed_question(); st.rerun()

        if st.session_state.finished:
            fireworks()
            total=st.session_state.answered; percentage=round(100*st.session_state.correct/max(1,total),1)
            elapsed=st.session_state.finished_at-st.session_state.game_start
            medal="🏆" if percentage>=90 else "🌟" if percentage>=70 else "💪"
            st.markdown(f'<div class="card" style="text-align:center"><div style="font-size:4rem">{medal}</div><h2>Resultaat</h2><p>{st.session_state.end_reason}</p><h1>{percentage}%</h1><p>Benodigde tijd: <b>{format_time(elapsed)}</b></p></div>',unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns(4)
            c1.metric("✅ Juist",st.session_state.correct); c2.metric("❌ Fout",st.session_state.wrong)
            c3.metric("⏭️ Geen antwoord",st.session_state.timed_out); c4.metric("⏱️ Tijd",format_time(elapsed))
            if st.session_state.level!="Toetsniveau":
                st.info(f"Score: {st.session_state.score} punten · Beste reeks: {st.session_state.best} · XP: {st.session_state.xp}")
            if st.button("🔁 Opnieuw spelen",use_container_width=True): reset_game(); st.rerun()
            return

        # Bovenaan staan alleen de essentiële tijdsgegevens.
        if st.session_state.level=="Toetsniveau":
            st.markdown(f'<div class="timer">⏱️ Toetstijd resterend: {format_time(st.session_state.test_deadline-time.time())}</div>',unsafe_allow_html=True)
        elif st.session_state.level=="Met tijdsklok":
            st.markdown(f'<div class="timer">⏱️ Nog {max(0,int(st.session_state.deadline-time.time()))} seconden</div>',unsafe_allow_html=True)

        # De oefening en antwoorden staan zo hoog mogelijk op smartphones.
        st.markdown(f'<div class="card"><div class="question">{st.session_state.a} × {st.session_state.b} = ?</div></div>',unsafe_allow_html=True)
        if st.session_state.answer_mode=="Meerkeuze":
            columns=st.columns(2)
            for index,choice in enumerate(st.session_state.choices):
                with columns[index%2]:
                    st.button(str(choice),key=f"c{st.session_state.answered}_{choice}",use_container_width=True,on_click=process_answer,args=(choice,),disabled=st.session_state.locked)
        else:
            with st.form(f"form_{st.session_state.answered}",clear_on_submit=True):
                value=st.number_input("Vul je antwoord in",min_value=0,max_value=100,step=1,value=None,placeholder="Typ hier je antwoord",disabled=st.session_state.locked)
                submitted=st.form_submit_button("Bevestig antwoord ✅" if st.session_state.level=="Toetsniveau" else "Controleer antwoord ✅",use_container_width=True,disabled=st.session_state.locked)
                if submitted:
                    if value is None: st.warning("Vul eerst een antwoord in.")
                    else: process_answer(int(value)); st.rerun()

        if st.session_state.level!="Toetsniveau" and st.session_state.feedback:
            (st.success if st.session_state.feedback.startswith("✅") else st.warning)(st.session_state.feedback)
            if st.button("Volgende vraag ➜",use_container_width=True): new_question(); st.rerun()
            if st.session_state.badges:
                st.markdown(" ".join(f'<span class="badge">{badge}</span>' for badge in sorted(st.session_state.badges)),unsafe_allow_html=True)

        # Statistieken en voortgang staan bewust onderaan voor een betere mobiele layout.
        st.divider()
        st.markdown('<div class="stats-title">Jouw voortgang</div>',unsafe_allow_html=True)
        if st.session_state.level=="Toetsniveau":
            c1,c2,c3=st.columns(3)
            c1.metric("Vraag",f"{min(st.session_state.answered+1,100)}/100")
            c2.metric("Ingevuld",st.session_state.answered)
            c3.metric("Resterend",100-st.session_state.answered)
            st.progress(st.session_state.answered/100)
        else:
            c1,c2,c3,c4=st.columns(4)
            c1.metric("⭐ Score",st.session_state.score); c2.metric("🔥 Reeks",st.session_state.streak)
            c3.metric("❤️ Levens",st.session_state.lives); c4.metric("⚡ XP",st.session_state.xp)
            st.progress(st.session_state.answered/st.session_state.rounds,text=f"{st.session_state.answered}/{st.session_state.rounds} vragen afgewerkt")

    game_panel()
