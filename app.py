import random
import time
import streamlit as st

st.set_page_config(page_title="Tafels Avontuur", page_icon="🚀", layout="centered")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#eef7ff 0%,#fff4dc 50%,#f4eaff 100%);}
.block-container {max-width: 850px; padding-top: 1.5rem;}
.hero {background:linear-gradient(120deg,#5b5ff0,#9b5de5); color:white; padding:24px; border-radius:24px; text-align:center; box-shadow:0 12px 30px rgba(91,95,240,.22)}
.hero h1 {margin:0; font-size:2.35rem}.hero p {margin:.5rem 0 0; font-size:1.08rem}
.card {background:rgba(255,255,255,.88); border:2px solid rgba(255,255,255,.8); padding:18px; border-radius:22px; box-shadow:0 8px 24px rgba(30,41,59,.10); margin:12px 0}
.question {font-size:3.1rem; font-weight:850; color:#30345f; text-align:center; margin:12px 0}
.stat {text-align:center; background:white; padding:12px 6px; border-radius:18px; box-shadow:0 4px 14px rgba(30,41,59,.08)}
.small {color:#596275;font-size:.92rem}.badge {display:inline-block;background:#fff3b0;padding:7px 11px;border-radius:999px;margin:4px;font-weight:700}
div.stButton > button {border-radius:16px; font-weight:750; min-height:48px; border:0; background:#5b5ff0; color:white;}
div.stButton > button:hover {background:#4145d5;color:white;border:0}
[data-testid="stMetric"] {background:white;border-radius:18px;padding:12px;box-shadow:0 4px 14px rgba(30,41,59,.08)}
</style>
""", unsafe_allow_html=True)

DEFAULTS={"started":False,"score":0,"streak":0,"best_streak":0,"lives":3,"answered":0,"correct":0,
          "a":2,"b":2,"choices":[],"feedback":"","locked":False,"xp":0,"badges":set(),"start_time":None}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v.copy() if isinstance(v,set) else v

def new_question():
    tables=st.session_state.selected_tables
    mode=st.session_state.mode
    a=random.choice(tables)
    b=random.randint(0,10)
    if mode=="Rustig": b=random.randint(0,5)
    answer=a*b
    wrong={answer}
    while len(wrong)<4:
        wrong.add(max(0,answer+random.choice([-10,-5,-3,-2,-1,1,2,3,5,10])))
    choices=list(wrong); random.shuffle(choices)
    st.session_state.a,st.session_state.b,st.session_state.choices=a,b,choices
    st.session_state.feedback=""; st.session_state.locked=False

def award_badges():
    if st.session_state.correct>=1: st.session_state.badges.add("🌟 Eerste ster")
    if st.session_state.streak>=5: st.session_state.badges.add("🔥 Reeks van 5")
    if st.session_state.correct>=10: st.session_state.badges.add("🧠 Tafelbrein")
    if st.session_state.xp>=200: st.session_state.badges.add("🚀 Ruimtereiziger")

def answer(choice):
    if st.session_state.locked: return
    st.session_state.locked=True; st.session_state.answered+=1
    if choice==st.session_state.a*st.session_state.b:
        bonus=min(st.session_state.streak,5)*2
        st.session_state.streak+=1; st.session_state.correct+=1
        st.session_state.best_streak=max(st.session_state.best_streak,st.session_state.streak)
        st.session_state.score+=10+bonus; st.session_state.xp+=20+bonus
        st.session_state.feedback=f"✅ Juist! +{10+bonus} punten en +{20+bonus} XP"
        st.balloons()
    else:
        right=st.session_state.a*st.session_state.b
        st.session_state.streak=0; st.session_state.lives-=1
        st.session_state.feedback=f"💡 Bijna! Het juiste antwoord is {right}."
    award_badges()

def reset_game():
    keep_tables=st.session_state.get("selected_tables",list(range(0,11)))
    keep_mode=st.session_state.get("mode","Normaal")
    for k,v in DEFAULTS.items(): st.session_state[k]=v.copy() if isinstance(v,set) else v
    st.session_state.selected_tables=keep_tables; st.session_state.mode=keep_mode

st.markdown('<div class="hero"><h1>🚀 Tafels Avontuur</h1><p>Oefen de tafels van 0 tot en met 10 en verzamel sterren, XP en badges!</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.header("🎮 Spelinstellingen")
    tables=st.multiselect("Welke tafels wil je oefenen?",list(range(0,11)),default=list(range(0,11)),disabled=st.session_state.started)
    mode=st.radio("Niveau",["Rustig","Normaal","Tijdchallenge"],horizontal=False,disabled=st.session_state.started,
                  help="Rustig: tweede getal 0–5. Normaal: 0–10. Tijdchallenge: speel tegen de tijd.")
    rounds=st.slider("Aantal vragen",5,30,10,5,disabled=st.session_state.started)
    if st.button("🔄 Nieuw spel",use_container_width=True): reset_game(); st.rerun()
    st.caption("Er wordt geen klassement of persoonlijke informatie opgeslagen.")

if not st.session_state.started:
    st.markdown("""<div class="card"><h3>🪐 Jouw missie</h3><p>Beantwoord de vragen, bouw een reeks juiste antwoorden op en ontgrendel badges. Je speelt alleen tegen jezelf.</p><p class="small">Tip: kies eerst enkele tafels om gericht te oefenen.</p></div>""",unsafe_allow_html=True)
    if not tables: st.warning("Kies minstens één tafel in de zijbalk.")
    if st.button("🚀 Start avontuur",use_container_width=True,disabled=not tables):
        st.session_state.started=True; st.session_state.selected_tables=tables; st.session_state.mode=mode; st.session_state.rounds=rounds; st.session_state.start_time=time.time(); new_question(); st.rerun()
else:
    finished=st.session_state.answered>=st.session_state.rounds or st.session_state.lives<=0
    if st.session_state.mode=="Tijdchallenge" and time.time()-st.session_state.start_time>=90: finished=True
    c1,c2,c3,c4=st.columns(4)
    c1.metric("⭐ Score",st.session_state.score); c2.metric("🔥 Reeks",st.session_state.streak); c3.metric("❤️ Levens",st.session_state.lives); c4.metric("⚡ XP",st.session_state.xp)
    progress=min(st.session_state.answered/st.session_state.rounds,1.0)
    st.progress(progress,text=f"Vraag {min(st.session_state.answered+1,st.session_state.rounds)} van {st.session_state.rounds}")
    if finished:
        pct=round(100*st.session_state.correct/max(st.session_state.answered,1))
        medal="🏆" if pct>=90 else "🌟" if pct>=70 else "💪"
        st.markdown(f'<div class="card" style="text-align:center"><div style="font-size:4rem">{medal}</div><h2>Missie voltooid!</h2><p>Je had <b>{st.session_state.correct} van {st.session_state.answered}</b> juist ({pct}%).</p><p>Beste reeks: <b>{st.session_state.best_streak}</b> · Totaal XP: <b>{st.session_state.xp}</b></p></div>',unsafe_allow_html=True)
        if st.session_state.badges:
            st.subheader("Jouw badges")
            st.markdown(" ".join(f'<span class="badge">{b}</span>' for b in sorted(st.session_state.badges)),unsafe_allow_html=True)
        if st.button("🔁 Speel opnieuw",use_container_width=True): reset_game(); st.rerun()
    else:
        if st.session_state.mode=="Tijdchallenge":
            remaining=max(0,90-int(time.time()-st.session_state.start_time)); st.info(f"⏱️ Nog ongeveer {remaining} seconden. Klik na elke vraag vlot door.")
        st.markdown(f'<div class="card"><div class="small" style="text-align:center">Los op</div><div class="question">{st.session_state.a} × {st.session_state.b} = ?</div></div>',unsafe_allow_html=True)
        cols=st.columns(2)
        for i,ch in enumerate(st.session_state.choices):
            with cols[i%2]: st.button(str(ch),key=f"choice_{st.session_state.answered}_{ch}",use_container_width=True,on_click=answer,args=(ch,),disabled=st.session_state.locked)
        if st.session_state.feedback:
            if st.session_state.feedback.startswith("✅"): st.success(st.session_state.feedback)
            else: st.warning(st.session_state.feedback)
            if st.button("Volgende vraag ➜",use_container_width=True): new_question(); st.rerun()
        if st.session_state.badges:
            st.markdown(" ".join(f'<span class="badge">{b}</span>' for b in sorted(st.session_state.badges)),unsafe_allow_html=True)
