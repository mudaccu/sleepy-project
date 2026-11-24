"""
app.py  -  Step 8: Frontend  (cozy night theme)
Run:  py -m streamlit run app.py
Flow: inputs -> model -> prediction -> tips
"""
import json
import random
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Moonrest · Sleep Predictor", page_icon="🌙", layout="centered")


# ---------------------------------------------------------------- helpers
def html(block: str):
    """Render raw HTML. Strips indentation + blank lines so markdown doesn't break it."""
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)


@st.cache_resource
def load():
    model = joblib.load("sleep_model.joblib")
    with open("form_schema.json") as f:
        schema = json.load(f)
    return model, schema


def star_field(n, seed, size):
    rnd = random.Random(seed)
    return ", ".join(
        f"{rnd.randint(0, 2000)}px {rnd.randint(0, 2000)}px rgba(255,255,255,{rnd.uniform(.35, .95):.2f})"
        for _ in range(n))


def bedtime_options():
    """Half-hour steps from 8:00 PM to 4:00 AM -> {label: hour as float}."""
    opts = {}
    for i in range(17):
        h = (20 + i * 0.5) % 24
        hh, mm = int(h), "30" if h % 1 else "00"
        label = f"{(hh % 12) or 12}:{mm} {'PM' if 12 <= hh < 24 else 'AM'}"
        opts[label] = h
    return opts


model, schema = load()

# ---------------------------------------------------------------- styles
STARS_S, STARS_M, STARS_L = star_field(260, 1, 1), star_field(90, 2, 2), star_field(35, 3, 3)

html(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Nunito:wght@400;600;700;800&display=swap');
:root {{
  --night-1:#0B0F2A; --night-2:#161C4A; --night-3:#2A2462;
  --lav:#B9A7FF; --lav-soft:rgba(185,167,255,.16); --moon:#FFE6A7;
  --ink:#ECE8FF; --ink-dim:#A9A4D6; --card:rgba(27,33,82,.55); --line:rgba(185,167,255,.22);
  --good:#9FE7C9; --mid:#FFD88A; --low:#FFA3B5;
}}
html, body, [data-testid="stAppViewContainer"], .stApp {{
  font-family:'Nunito', system-ui, sans-serif; color:var(--ink);
}}
.stApp {{
  background: radial-gradient(1200px 600px at 80% -10%, #3B2F7A 0%, transparent 60%),
              radial-gradient(900px 500px at -10% 30%, #1E2A6B 0%, transparent 55%),
              linear-gradient(180deg, var(--night-1) 0%, var(--night-2) 55%, var(--night-3) 100%);
  background-attachment: fixed;
}}
[data-testid="stHeader"] {{ background: transparent; }}
footer, #MainMenu {{ visibility:hidden; }}
.block-container {{ padding-top:2.2rem; padding-bottom:4rem; max-width:760px; position:relative; z-index:1; }}

/* ---------- star layers ---------- */
.sky {{ position:fixed; inset:0; pointer-events:none; z-index:0; overflow:hidden; }}
.sky i {{ position:absolute; top:0; left:0; border-radius:50%; display:block; }}
.sky .s1 {{ width:1px; height:1px; box-shadow:{STARS_S}; animation:twinkle 6s ease-in-out infinite; }}
.sky .s2 {{ width:2px; height:2px; box-shadow:{STARS_M}; animation:twinkle 9s ease-in-out infinite 1.5s; }}
.sky .s3 {{ width:3px; height:3px; box-shadow:{STARS_L}; animation:twinkle 12s ease-in-out infinite 3s; filter:blur(.3px); }}
.sky .shoot {{ width:120px; height:1.5px; top:12%; left:70%;
  background:linear-gradient(90deg, rgba(255,255,255,.9), transparent);
  transform:rotate(-18deg); opacity:0; animation:shoot 11s ease-in 4s infinite; border-radius:2px; }}
@keyframes twinkle {{ 0%,100% {{opacity:.55}} 50% {{opacity:1}} }}
@keyframes shoot {{ 0% {{opacity:0; transform:translate(0,0) rotate(-18deg)}} 3% {{opacity:1}}
  10% {{opacity:0; transform:translate(-420px,140px) rotate(-18deg)}} 100% {{opacity:0}} }}
@keyframes float {{ 0%,100% {{transform:translateY(0)}} 50% {{transform:translateY(-8px)}} }}
@keyframes drift {{ 0% {{transform:translateX(-6%)}} 100% {{transform:translateX(6%)}} }}
@keyframes zz {{ 0% {{opacity:0; transform:translate(0,0) scale(.7)}} 30% {{opacity:1}}
  100% {{opacity:0; transform:translate(18px,-34px) scale(1.1)}} }}
@keyframes rise {{ from {{opacity:0; transform:translateY(14px)}} to {{opacity:1; transform:none}} }}

/* ---------- hero ---------- */
.hero {{ position:relative; text-align:center; padding:8px 0 6px; }}
.hero .moon {{ width:132px; height:132px; margin:0 auto; animation:float 7s ease-in-out infinite;
  filter:drop-shadow(0 0 28px rgba(255,230,167,.45)); }}
.hero .zz span {{ position:absolute; font-family:'Fraunces', serif; color:var(--lav); font-weight:700;
  animation:zz 4.5s ease-out infinite; }}
.hero h1 {{ font-family:'Fraunces', Georgia, serif !important; font-weight:700; font-size:2.6rem !important;
  letter-spacing:-.5px; margin:.4rem 0 .2rem !important; color:var(--ink) !important; padding:0 !important; }}
.hero h1 em {{ font-style:normal; color:var(--moon); }}
.hero p {{ color:var(--ink-dim); font-size:1.05rem; margin:0 auto; max-width:460px; }}
.clouds {{ position:relative; height:46px; margin:10px 0 4px; opacity:.9; filter:blur(.6px); }}
.clouds svg {{ position:absolute; animation:drift 14s ease-in-out infinite alternate; }}

/* ---------- section titles ---------- */
.sec {{ display:flex; align-items:center; gap:10px; margin:1.1rem 0 .3rem; }}
.sec .ic {{ width:34px; height:34px; border-radius:11px; display:grid; place-items:center;
  background:var(--lav-soft); border:1px solid var(--line); font-size:1.05rem; }}
.sec h3 {{ font-family:'Fraunces', serif !important; font-size:1.25rem !important; margin:0 !important;
  padding:0 !important; color:var(--ink) !important; font-weight:600; }}
.sec small {{ color:var(--ink-dim); margin-left:auto; font-size:.85rem; }}

/* ---------- the form card ---------- */
[data-testid="stForm"] {{ background:var(--card); border:1px solid var(--line) !important;
  border-radius:24px; padding:1.4rem 1.5rem 1.2rem; backdrop-filter:blur(14px);
  box-shadow:0 20px 60px rgba(5,6,25,.45), inset 0 1px 0 rgba(255,255,255,.06); }}
[data-testid="stWidgetLabel"] p {{ font-weight:700; color:var(--ink) !important; font-size:.95rem; }}
[data-testid="stSlider"] {{ padding:.15rem .2rem .3rem; }}
[data-testid="stSlider"] [role="group"] div:has(+ div + input),
[data-testid="stSlider"] [role="group"] div:has(> input) {{ box-shadow:0 0 0 5px rgba(185,167,255,.18), 0 0 16px rgba(185,167,255,.6); }}
[data-testid="stSliderThumbValue"], [data-testid="stSliderThumbValue"] p {{ color:var(--moon) !important;
  font-weight:800 !important; font-family:'Nunito', sans-serif !important; }}
[data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{ color:var(--ink-dim) !important; }}
[data-baseweb="select"] > div {{ background:rgba(14,19,48,.7) !important; border:1px solid var(--line) !important;
  border-radius:14px !important; }}
.hint {{ color:var(--ink-dim); font-size:.82rem; margin:-.55rem 0 .6rem .2rem; }}

/* submit button */
[data-testid="stElementContainer"]:has([data-testid="stFormSubmitButton"]),
[data-testid="stFormSubmitButton"] {{ width:100% !important; }}
[data-testid="stFormSubmitButton"] button {{ width:100% !important; border:none !important; border-radius:16px !important;
  padding:.85rem 1rem !important; font-family:'Nunito'; font-weight:800 !important; font-size:1.05rem !important;
  color:#1B1640 !important; letter-spacing:.2px;
  background:linear-gradient(135deg, #FFE6A7 0%, #D9C6FF 55%, #B9A7FF 100%) !important;
  box-shadow:0 10px 30px rgba(185,167,255,.35); transition:transform .15s ease, box-shadow .15s ease; }}
[data-testid="stFormSubmitButton"] button:hover {{ transform:translateY(-2px);
  box-shadow:0 14px 38px rgba(255,230,167,.4); }}
[data-testid="stFormSubmitButton"] button p {{ font-weight:800 !important; font-size:1.05rem !important; }}

/* ---------- result ---------- */
.result {{ margin-top:1.6rem; background:var(--card); border:1px solid var(--line); border-radius:26px;
  padding:1.6rem; backdrop-filter:blur(14px); animation:rise .6s ease both;
  box-shadow:0 20px 60px rgba(5,6,25,.45); }}
.result .top {{ display:flex; gap:1.4rem; align-items:center; flex-wrap:wrap; }}
.ring {{ position:relative; width:150px; height:150px; flex:none; }}
.ring .num {{ position:absolute; inset:0; display:grid; place-items:center; text-align:center; }}
.ring .num b {{ font-family:'Fraunces', serif; font-size:2.6rem; line-height:1; color:var(--ink); }}
.ring .num span {{ display:block; color:var(--ink-dim); font-size:.85rem; margin-top:2px; }}
.mood {{ flex:1; min-width:220px; }}
.mood .tag {{ display:inline-block; padding:.28rem .75rem; border-radius:999px; font-weight:800; font-size:.8rem;
  letter-spacing:.6px; text-transform:uppercase; }}
.mood h2 {{ font-family:'Fraunces', serif !important; font-size:1.7rem !important; margin:.45rem 0 .3rem !important;
  padding:0 !important; color:var(--ink) !important; }}
.mood p {{ color:var(--ink-dim); margin:0; }}
.mood .art {{ float:right; width:84px; height:84px; margin:-6px -4px 0 8px; animation:float 6s ease-in-out infinite; }}

.chips {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin:1.3rem 0 .4rem; }}
.chip {{ border:1px solid var(--line); border-radius:16px; padding:.7rem .75rem; background:rgba(14,19,48,.55); }}
.chip .k {{ color:var(--ink-dim); font-size:.75rem; font-weight:700; text-transform:uppercase; letter-spacing:.5px; }}
.chip .v {{ font-weight:800; font-size:1.05rem; margin:.15rem 0; }}
.chip .d {{ display:inline-flex; align-items:center; gap:6px; font-size:.78rem; font-weight:700; }}
.chip .d::before {{ content:""; width:8px; height:8px; border-radius:50%; background:currentColor; }}
.ok {{ color:var(--good); }} .warn {{ color:var(--low); }}

.tips-h {{ font-family:'Fraunces', serif; font-size:1.2rem; margin:1.1rem 0 .6rem; color:var(--ink); }}
.tip {{ display:flex; gap:14px; align-items:flex-start; padding:.9rem 1rem; border-radius:18px;
  background:linear-gradient(135deg, rgba(185,167,255,.13), rgba(255,230,167,.06));
  border:1px solid var(--line); margin-bottom:10px; animation:rise .5s ease both; }}
.tip .ti {{ width:42px; height:42px; flex:none; border-radius:13px; display:grid; place-items:center;
  background:rgba(14,19,48,.7); font-size:1.3rem; }}
.tip b {{ display:block; color:var(--ink); }}
.tip span {{ color:var(--ink-dim); font-size:.92rem; }}

.foot {{ text-align:center; color:var(--ink-dim); font-size:.8rem; margin-top:2rem; opacity:.8; line-height:1.6; }}

@media (max-width: 640px) {{
  .hero h1 {{ font-size:2rem !important; }}
  .chips {{ grid-template-columns:repeat(2, 1fr); }}
  .ring {{ margin:0 auto; }}
  .result .top {{ justify-content:center; text-align:center; }}
  .mood .art {{ display:none; }}
  [data-testid="stForm"] {{ padding:1.1rem 1rem; }}
}}
@media (prefers-reduced-motion: reduce) {{
  * {{ animation:none !important; transition:none !important; }}
}}
</style>
<div class="sky"><i class="s1"></i><i class="s2"></i><i class="s3"></i><i class="shoot"></i></div>
""")

# ---------------------------------------------------------------- hero
html("""
<div class="hero">
  <div style="position:relative; width:132px; margin:0 auto;">
    <svg class="moon" viewBox="0 0 120 120" aria-hidden="true">
      <defs>
        <radialGradient id="mg" cx="40%" cy="35%" r="70%">
          <stop offset="0%" stop-color="#FFF6D6"/><stop offset="70%" stop-color="#FFE3A0"/>
          <stop offset="100%" stop-color="#F2C97A"/>
        </radialGradient>
        <mask id="cm"><rect width="120" height="120" fill="#fff"/><circle cx="80" cy="44" r="40" fill="#000"/></mask>
      </defs>
      <circle cx="60" cy="60" r="44" fill="url(#mg)" mask="url(#cm)"/>
      <circle cx="38" cy="66" r="5" fill="#E8BE6E" opacity=".55" mask="url(#cm)"/>
      <circle cx="30" cy="48" r="3" fill="#E8BE6E" opacity=".5" mask="url(#cm)"/>
      <circle cx="46" cy="86" r="3.5" fill="#E8BE6E" opacity=".45" mask="url(#cm)"/>
      <path d="M30 70 q6 5 12 0" stroke="#7A5A2E" stroke-width="2.6" fill="none" stroke-linecap="round"/>
      <path d="M40 80 q5 4 10 0" stroke="#7A5A2E" stroke-width="2.2" fill="none" stroke-linecap="round" opacity=".7"/>
    </svg>
    <div class="zz">
      <span style="right:-6px; top:6px; font-size:1.3rem;">z</span>
      <span style="right:-18px; top:-6px; font-size:1rem; animation-delay:1.5s;">z</span>
      <span style="right:-28px; top:-18px; font-size:.8rem; animation-delay:3s;">z</span>
    </div>
  </div>
  <h1>Moon<em>rest</em></h1>
  <p>Tell us about your day, and we'll predict how well you'll sleep tonight.</p>
  <div class="clouds">
    <svg style="left:4%; top:6px;" width="150" height="40" viewBox="0 0 150 40"><path d="M20 34 a14 14 0 0 1 6-26 a20 20 0 0 1 36-2 a16 16 0 0 1 28 10 a12 12 0 0 1 2 18 z" fill="#8E84E0" opacity=".22"/></svg>
    <svg style="right:6%; top:0; animation-duration:18s;" width="190" height="46" viewBox="0 0 190 46"><path d="M24 40 a16 16 0 0 1 8-30 a24 24 0 0 1 44-4 a20 20 0 0 1 36 10 a16 16 0 0 1 6 24 z" fill="#8E84E0" opacity=".18"/></svg>
  </div>
</div>
""")

# ---------------------------------------------------------------- form
inp = schema["inputs"]
bed_opts = bedtime_options()
user = {}

with st.form("habits", border=False):
    html('<div class="sec"><div class="ic">🧸</div><h3>About you</h3><small>the basics</small></div>')
    c1, c2, c3 = st.columns([1.1, 1, 1])
    user["Age"] = c1.slider("Age", inp["Age"]["min"], inp["Age"]["max"], inp["Age"]["default"])
    user["Gender"] = c2.selectbox("Gender", inp["Gender"]["options"])
    user["University_Year"] = c3.selectbox("University year", inp["University_Year"]["options"])

    html('<div class="sec"><div class="ic">☀️</div><h3>Your day</h3><small>be honest 🙂</small></div>')
    c1, c2 = st.columns(2)
    user["Screen_Time"] = c1.slider("📱 Screen time (hours)", float(inp["Screen_Time"]["min"]),
                                    float(inp["Screen_Time"]["max"]), 2.5, 0.1)
    user["Caffeine_Intake"] = c2.slider("☕ Caffeine drinks", int(inp["Caffeine_Intake"]["min"]),
                                        int(inp["Caffeine_Intake"]["max"]), 2)
    user["Physical_Activity"] = c1.slider("🏃 Exercise (minutes)", 0, int(inp["Physical_Activity"]["max"]), 45, 5)
    user["Study_Hours"] = c2.slider("📚 Study hours", 0.0, float(inp["Study_Hours"]["max"]), 6.0, 0.5)

    html('<div class="sec"><div class="ic">🛏️</div><h3>Tonight</h3><small>when will you sleep?</small></div>')
    bed_label = st.select_slider("Planned bedtime", options=list(bed_opts), value="11:00 PM")
    user["Weekday_Sleep_Start"] = bed_opts[bed_label]

    st.write("")
    submitted = st.form_submit_button("✨  Predict my sleep")

# ---------------------------------------------------------------- result
if submitted:
    score = float(model.predict(pd.DataFrame([user]))[0])
    score = max(1.0, min(10.0, score))
    pct = score / 10
    circ = 2 * 3.14159 * 62

    if score < 5:
        color, tag, title, msg = "var(--low)", "Restless night", "A rough night ahead", \
            "Tonight might be a bit restless. A few small changes could help."
        art = """<svg class="art" viewBox="0 0 90 90"><path d="M18 64 a14 14 0 0 1 4-27 a20 20 0 0 1 38-4 a15 15 0 0 1 14 24 a10 10 0 0 1-4 7 z" fill="#C9BFFF" opacity=".85"/>
        <path d="M34 70 l-4 10 M48 70 l-4 10 M62 70 l-4 10" stroke="#9FB6FF" stroke-width="3" stroke-linecap="round"/>
        <circle cx="38" cy="50" r="2.6" fill="#2A2462"/><circle cx="54" cy="50" r="2.6" fill="#2A2462"/>
        <path d="M40 58 q6 -4 12 0" stroke="#2A2462" stroke-width="2.2" fill="none" stroke-linecap="round"/></svg>"""
    elif score < 8:
        color, tag, title, msg = "var(--mid)", "Okay-ish", "A decent night's rest", \
            "You'll probably sleep okay. A little tweak could make it great."
        art = """<svg class="art" viewBox="0 0 90 90"><circle cx="50" cy="36" r="22" fill="#FFE3A0"/>
        <path d="M14 70 a13 13 0 0 1 4-25 a19 19 0 0 1 36-4 a14 14 0 0 1 14 22 a9 9 0 0 1-3 7 z" fill="#C9BFFF" opacity=".9"/>
        <path d="M30 58 q5 4 10 0 M46 58 q5 4 10 0" stroke="#2A2462" stroke-width="2.2" fill="none" stroke-linecap="round"/></svg>"""
    else:
        color, tag, title, msg = "var(--good)", "Sweet dreams", "Cozy, deep sleep", \
            "Your habits set you up for a restful night. Sweet dreams!"
        art = """<svg class="art" viewBox="0 0 90 90"><path d="M58 14 a32 32 0 1 0 22 44 a26 26 0 1 1 -22 -44 z" fill="#FFE3A0"/>
        <path d="M36 50 q5 4 10 0" stroke="#7A5A2E" stroke-width="2.4" fill="none" stroke-linecap="round"/>
        <text x="62" y="30" fill="#B9A7FF" font-family="Georgia" font-weight="700" font-size="14">z</text>
        <text x="72" y="18" fill="#B9A7FF" font-family="Georgia" font-weight="700" font-size="10">z</text></svg>"""

    # habit chips
    def chip(k, v, good):
        cls, txt = ("ok", "Good") if good else ("warn", "Watch")
        return f'<div class="chip"><div class="k">{k}</div><div class="v">{v}</div><div class="d {cls}">{txt}</div></div>'

    late = 1 <= user["Weekday_Sleep_Start"] < 5
    chips = "".join([
        chip("Screen", f'{user["Screen_Time"]:.1f} h', user["Screen_Time"] <= 3),
        chip("Caffeine", f'{user["Caffeine_Intake"]} cups', user["Caffeine_Intake"] < 3),
        chip("Exercise", f'{user["Physical_Activity"]} min', user["Physical_Activity"] >= 30),
        chip("Bedtime", bed_label, not late),
    ])

    # tips (rule-based)
    tips = []
    if user["Screen_Time"] > 3:
        tips.append(("📱", "Put the phone down a little earlier",
                     "Try a screen-free hour before bed. Dim, warm light helps your body wind down."))
    if user["Physical_Activity"] < 30:
        tips.append(("🌿", "Move a little more",
                     "Even a 30-minute walk in the day can make sleep deeper."))
    if user["Caffeine_Intake"] >= 3:
        tips.append(("🍵", "Swap one coffee for herbal tea",
                     "Caffeine can stay in your body for hours. Keep it to the morning."))
    if late:
        tips.append(("🛏️", "Head to bed a bit earlier",
                     "Aim to be in bed before midnight, and keep the same time on most days."))
    if not tips:
        if score < 5:
            tips.append(("🌙", "Your habits look good",
                         "Screen time, caffeine, exercise and bedtime are all fine. The low score comes from other factors in the data."))
        else:
            tips.append(("💜", "Keep doing what you're doing",
                         "Your habits look healthy. A cozy, dark, quiet room will do the rest."))

    tips_html = "".join(
        f'<div class="tip" style="animation-delay:{.1 + i * .08:.2f}s"><div class="ti">{ic}</div>'
        f'<div><b>{t}</b><span>{d}</span></div></div>'
        for i, (ic, t, d) in enumerate(tips))

    html(f"""
    <div class="result">
      <div class="top">
        <div class="ring">
          <svg viewBox="0 0 150 150" width="150" height="150">
            <circle cx="75" cy="75" r="62" stroke="rgba(185,167,255,.15)" stroke-width="12" fill="none"/>
            <circle cx="75" cy="75" r="62" stroke="{color}" stroke-width="12" fill="none" stroke-linecap="round"
              stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ * (1 - pct):.1f}" transform="rotate(-90 75 75)"
              style="filter:drop-shadow(0 0 8px {color});"/>
          </svg>
          <div class="num"><div><b>{score:.1f}</b><span>out of 10</span></div></div>
        </div>
        <div class="mood">
          {art}
          <span class="tag" style="background:color-mix(in srgb, {color} 18%, transparent); color:{color};">{tag}</span>
          <h2>{title}</h2>
          <p>{msg}</p>
        </div>
      </div>
      <div class="chips">{chips}</div>
      <div class="tips-h">Little things for tonight</div>
      {tips_html}
    </div>
    """)

# ---------------------------------------------------------------- footer
html(f"""
<div class="foot">
  Model: {schema['model']} · Test MAE: {schema['test_mae']}<br>
  Trained on synthetic data for learning purposes. Tips are simple rules, not medical advice.
</div>
""")
