import random
import time
import streamlit as st

st.set_page_config(page_title="Tafels Avontuur", page_icon="🚀", layout="centered")
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#eef7ff,#fff4dc 55%,#f4eaff)}
.block-container{max-width:850px;padding-top:1.5rem}.hero{background:linear-gradient(120deg,#5b5ff0,#9b5de5);color:white;padding:24px;border-radius:24px;text-align:center;box-shadow:0 12px 30px #5b5ff038}.hero h1{margin:0;font-size:2.35rem}.hero p{margin:.5rem 0 0}.card{background:#ffffffe8;padding:18px;border-radius:22px;box-shadow:0 8px 24px #1e293b1a;margin:12px 0}.question{font-size:3.1rem;font-weight:850;color:#30345f;text-align:center;margin:12px 0}.badge{display:inline-block;background:#fff3b0;padding:7px 11px;border-radius:999px;margin:4px;font-weight:700}div.stButton>button,[data-testid="stFormSubmitButton"] button{border-radius:16px;font-weight:750;min-height:48px;border:0;background:#5b5ff0;color:white}[data-testid="stMetric"]{background:white;border-radius:18px;padding:12px;box-shadow:0 4px 14px #1e293b14}
</style>
""", unsafe_allow_html=True)

D={"started":False,"score":0,"streak":0,"best":0,"lives":3,"answered":0,"correct":0,"a":2,"b":2,"choices":[],"feedback":"","locked":False,"xp":0,"badges":set(),"start":None}
for k,v in D.items():
    if k not in st.session_state: st.session_state[k]=v.copy() if isinstance(v,set) else v

def new_question():
    a=random.choice(st.session_state.tables)
    b=random.randint(0,5 if st.session_state.level=="Rustig" else 10)
    right=a*b; opts={right}
    while len(opts)<4: opts.add(max(0,right+random.choice([-10,-5,-3,-2,-1,1,2,3,5,10])))
    st.session_state.a=a; st.session_state.b=b; st.session_state.choices=list(opts); random.shuffle(st.session_state.choices)
    st.session_state.feedback=""; st.session_state.locked=False

def check(value):
    if st.session_state.locked:return
    st.session_state.locked=True; st.session_state.answered+=1
    if value==st.session_state.a*st.session_state.b:
        bonus=min(st.session_state.streak,5)*2; st.session_state.streak+=1; st.session_state.correct+=1
        st.session_state.best=max(st.session_state.best,st.session_state.streak); st.session_state.score+=10+bonus; st.session_state.xp+=20+bonus
        st.session_state.feedback=f"✅ Juist! +{10+bonus} punten en +{20+bonus} XP"; st.balloons()
    else:
        st.session_state.streak=0; st.session_state.lives-=1
        st.session_state.feedback=f"💡 Bijna! Het juiste antwoord is {st.session_state.a*st.session_state.b}."
    if st.session_state.correct>=1:st.session_state.badges.add("🌟 Eerste ster")
    if st.session_state.streak>=5:st.session_state.badges.add("🔥 Reeks van 5")
    if st.session_state.correct>=10:st.session_state.badges.add("🧠 Tafelbrein")

def reset():
    for k,v in D.items():st.session_state[k]=v.copy() if isinstance(v,set) else v

st.markdown('<div class="hero"><h1>🚀 Tafels Avontuur</h1><p>Oefen de tafels en verzamel punten, XP en badges!</p></div>',unsafe_allow_html=True)
with st.sidebar:
    st.header("🎮 Spelinstellingen")
    tables=st.multiselect("Welke tafels wil je oefenen?",range(11),default=range(11),disabled=st.session_state.started)
    level=st.radio("Niveau",["Rustig","Normaal","Tijdchallenge"],disabled=st.session_state.started)
    answer_mode=st.radio("Hoe wil je antwoorden?",["Meerkeuze","Zelf invullen"],horizontal=True,disabled=st.session_state.started)
    rounds=st.slider("Aantal vragen",5,30,10,5,disabled=st.session_state.started)
    if st.button("🔄 Nieuw spel",use_container_width=True):reset();st.rerun()
    st.caption("Er wordt geen klassement of persoonlijke informatie opgeslagen.")

if not st.session_state.started:
    st.markdown('<div class="card"><h3>🪐 Jouw missie</h3><p>Kies je tafels, niveau en antwoordmethode. Bouw daarna een reeks juiste antwoorden op.</p></div>',unsafe_allow_html=True)
    if not tables:st.warning("Kies minstens één tafel.")
    if st.button("🚀 Start avontuur",use_container_width=True,disabled=not tables):
        st.session_state.started=True;st.session_state.tables=tables;st.session_state.level=level;st.session_state.answer_mode=answer_mode;st.session_state.rounds=rounds;st.session_state.start=time.time();new_question();st.rerun()
else:
    finished=st.session_state.answered>=st.session_state.rounds or st.session_state.lives<=0 or (st.session_state.level=="Tijdchallenge" and time.time()-st.session_state.start>=90)
    c1,c2,c3,c4=st.columns(4);c1.metric("⭐ Score",st.session_state.score);c2.metric("🔥 Reeks",st.session_state.streak);c3.metric("❤️ Levens",st.session_state.lives);c4.metric("⚡ XP",st.session_state.xp)
    st.progress(min(st.session_state.answered/st.session_state.rounds,1.0),text=f"Vraag {min(st.session_state.answered+1,st.session_state.rounds)} van {st.session_state.rounds}")
    if finished:
        pct=round(100*st.session_state.correct/max(1,st.session_state.answered));medal="🏆" if pct>=90 else "🌟" if pct>=70 else "💪"
        st.markdown(f'<div class="card" style="text-align:center"><div style="font-size:4rem">{medal}</div><h2>Missie voltooid!</h2><p><b>{st.session_state.correct} van {st.session_state.answered}</b> juist ({pct}%).</p><p>Beste reeks: <b>{st.session_state.best}</b></p></div>',unsafe_allow_html=True)
        if st.button("🔁 Speel opnieuw",use_container_width=True):reset();st.rerun()
    else:
        st.markdown(f'<div class="card"><div class="question">{st.session_state.a} × {st.session_state.b} = ?</div></div>',unsafe_allow_html=True)
        if st.session_state.answer_mode=="Meerkeuze":
            cols=st.columns(2)
            for i,ch in enumerate(st.session_state.choices):
                with cols[i%2]:st.button(str(ch),key=f"c{st.session_state.answered}_{ch}",use_container_width=True,on_click=check,args=(ch,),disabled=st.session_state.locked)
        else:
            with st.form(f"form_{st.session_state.answered}"):
                value=st.number_input("Vul je antwoord in",min_value=0,max_value=100,step=1,value=None,placeholder="Typ hier je antwoord",disabled=st.session_state.locked)
                sent=st.form_submit_button("Controleer antwoord ✅",use_container_width=True,disabled=st.session_state.locked)
                if sent:
                    if value is None:st.warning("Vul eerst een antwoord in.")
                    else:check(int(value));st.rerun()
        if st.session_state.feedback:
            (st.success if st.session_state.feedback.startswith("✅") else st.warning)(st.session_state.feedback)
            if st.button("Volgende vraag ➜",use_container_width=True):new_question();st.rerun()
        if st.session_state.badges:st.markdown(" ".join(f'<span class="badge">{x}</span>' for x in sorted(st.session_state.badges)),unsafe_allow_html=True)
