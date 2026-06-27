# -*- coding: utf-8 -*-
"""통영 아웃리치 식사팀 가이드 — Sacred Table 디자인 시스템 정적 사이트 생성기"""
import os, shutil

ROOT = "/home/claude/MEAL"
os.makedirs(ROOT, exist_ok=True)

# ---------------- ICONS (thin-stroke, currentColor) ----------------
IC = {
"home":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V20h14V9.5"/></svg>',
"sun":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4"/></svg>',
"walk":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="13" cy="4.5" r="1.8"/><path d="M11 8.5 9 13l2.5 1.5L13 21M13 11l3 1.5M9 13l-2 5M13 11l-1-2.5"/></svg>',
"fork":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3v7M5 3v4.5a2 2 0 0 0 4 0V3M7 10v11"/><path d="M17 3c-1.7 0-3 2-3 5s1 4 2 4v9"/></svg>',
"pot":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 10h14v6a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z"/><path d="M3 10h18M8 10V8.5M16 10V8.5M9.5 5.5c.6-1 2.4-1 3 0M12.5 4c.6-1 2.4-1 3 0"/></svg>',
"bowl":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 11h17a8.5 8.5 0 0 1-17 0z"/><path d="M2.5 11h19M9 7.5c-.5-1 .5-2 0-3M13 7.5c-.5-1 .5-2 0-3M16.5 18l1.5 1.5"/></svg>',
"punch":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 9h15l-1.3 9a2 2 0 0 1-2 1.7H7.8a2 2 0 0 1-2-1.7z"/><path d="M9 12.5h.01M12 14.5h.01M15 12h.01M12 6.5c0-1 1.5-1.5 1.5-2.5"/></svg>',
"fruit":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8c-3 0-5 2-5 5.5S9.5 21 12 21s5-4 5-7.5S15 8 12 8z"/><path d="M12 8c0-2 1-3.5 3-4M12 8c-.5-1-2-1.5-3-1.2"/></svg>',
"store":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9h16l-1 11H5z" /><path d="M4 9 5.5 4h13L20 9M9 9V4.5M15 9V4.5"/></svg>',
"cal":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="16" rx="2.5"/><path d="M4 9h16M9 3v3M15 3v3"/></svg>',
"people":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="8.5" r="2.4"/><path d="M16 14.2A4.6 4.6 0 0 1 20.5 19"/></svg>',
"arch":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 21V11a7 7 0 0 1 14 0v10"/><path d="M5 21h14M12 3.5V6M10.5 5h3"/></svg>',
"cross":'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10.4 2h3.2v5.4H19v3.2h-5.4V22h-3.2V10.6H5V7.4h5.4z"/></svg>',
}

# ---------------- CSS ----------------
CSS = """
:root{
  --surface:#fbf9f8; --card:#ffffff; --card-low:#f6f4f3;
  --inner:#edeceb; --inner-warm:#e7e6da;
  --primary:#4e6448; --primary-dim:#a9c2a0; --primary-soft:#e7eee2;
  --ink:#1b1c1c; --ink-soft:#434841; --muted:#7d8278; --line:#e8e6e4;
  --wed:#5b89b0; --thu:#6a9b4f; --fri:#e07a3c; --sat:#dca22c;
  --r-md:.75rem; --r-lg:1rem; --r-xl:1.5rem;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#e9e6e3}
body{font-family:'Noto Sans KR','Plus Jakarta Sans',sans-serif;color:var(--ink);
  -webkit-font-smoothing:antialiased}
.app{max-width:430px;margin:0 auto;min-height:100vh;background:var(--surface);
  position:relative;padding-bottom:92px;overflow:hidden}
a{text-decoration:none;color:inherit}

/* top bar */
.topbar{display:flex;align-items:center;gap:8px;padding:16px 20px 14px;
  border-bottom:1px solid var(--line);background:var(--surface);
  position:sticky;top:0;z-index:20}
.topbar .hb{width:34px;height:34px;color:var(--primary);flex:none}
.topbar .hb svg{width:24px;height:24px}
.topbar h1{flex:1;text-align:center;font-family:'Plus Jakarta Sans',sans-serif;
  font-weight:700;font-size:21px;color:var(--primary);letter-spacing:-.01em;
  margin-right:34px}

.page{padding:20px 24px 8px}

/* ---- HOME ---- */
.hero{position:relative;border-radius:var(--r-xl);overflow:hidden;
  box-shadow:0 8px 30px rgba(78,100,72,.16);margin-bottom:6px}
.hero img{display:block;width:100%}
.welcome{text-align:center;margin:18px 4px 20px;color:var(--ink-soft);
  font-size:15px;line-height:1.55}
.welcome b{display:block;font-size:18px;color:var(--primary);font-weight:800;
  margin-bottom:4px}
.grid{display:flex;flex-wrap:wrap;gap:14px}
.tile{width:calc(50% - 7px);background:var(--card);border-radius:var(--r-xl);
  padding:20px 16px 16px;box-shadow:0 4px 20px rgba(27,28,28,.05);display:flex;
  flex-direction:column;align-items:center;gap:10px;border-top:4px solid var(--c);
  min-height:128px;justify-content:center;transition:transform .12s}
.tile:active{transform:scale(.97)}
.tile .ti{width:40px;height:40px;color:var(--c)}
.tile .ti svg{width:40px;height:40px}
.tile .tl{font-size:18px;font-weight:800;color:var(--ink)}
.tile .ts{font-size:12px;color:var(--muted);text-align:center;line-height:1.4}
.tile-wide{width:100%;background:var(--primary);color:#fff;flex-direction:row;
  gap:12px;border-top:none;min-height:auto;padding:18px 20px;justify-content:center;
  box-shadow:0 6px 22px rgba(78,100,72,.28)}
.tile-wide .ti{width:26px;height:26px;color:#fff}
.tile-wide .ti svg{width:26px;height:26px}
.tile-wide .tl{color:#fff;font-size:17px}

/* ---- DAY ---- */
.dayhead{text-align:center;padding:8px 0 18px}
.dayhead .dt{font-size:38px;font-weight:900;color:var(--c);letter-spacing:-.02em}
.dayhead .ds{font-size:15px;color:var(--muted);margin-top:4px}
.mcard{background:var(--card);border-radius:var(--r-lg);padding:16px;margin-bottom:16px;
  border-top:5px solid var(--c);box-shadow:0 4px 20px rgba(27,28,28,.05)}
.mhead{display:flex;align-items:center;gap:9px;margin-bottom:11px}
.mhead .mi{width:24px;height:24px;color:var(--c);flex:none}
.mhead .mi svg{width:24px;height:24px}
.mhead .ml{font-size:18px;font-weight:800;color:var(--ink);flex:1}
.mhead .mt{font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;font-weight:700;
  letter-spacing:.04em;color:var(--ink-soft);background:var(--inner);
  padding:5px 11px;border-radius:999px}
.inner{background:var(--inner);border-radius:var(--r-md);padding:14px 16px}
.inner.warm{background:var(--inner-warm)}
.inner .dish{font-size:17px;font-weight:800;color:var(--ink)}
.inner .memo{font-size:13.5px;color:var(--ink-soft);line-height:1.55;margin-top:5px}
.inner.center{text-align:center}
.inner.center .dish{display:block}

/* ---- TEAM ---- */
.teamphoto{width:100%;border-radius:var(--r-lg);display:block;
  box-shadow:0 6px 22px rgba(27,28,28,.08);margin-bottom:26px}
.archcard{background:var(--card);border-radius:46% 46% var(--r-lg) var(--r-lg)
  / 22% 22% var(--r-lg) var(--r-lg);padding:42px 26px 30px;text-align:center;
  box-shadow:0 4px 24px rgba(27,28,28,.06);margin-bottom:24px}
.archcard .cross{width:30px;height:30px;color:#caa24a;margin:0 auto 8px}
.archcard .cross svg{width:30px;height:30px}
.archcard h2{font-size:24px;font-weight:900;color:var(--ink);margin-bottom:22px}
.prayers{list-style:none;text-align:left;counter-reset:p}
.prayers li{display:flex;gap:12px;margin-bottom:16px;font-size:15px;line-height:1.5;
  color:var(--ink-soft)}
.prayers li::before{counter-increment:p;content:counter(p) ".";font-weight:800;
  color:var(--primary);flex:none;min-width:16px}
.support{background:var(--card);border-radius:var(--r-lg);padding:22px;text-align:center;
  box-shadow:0 4px 20px rgba(27,28,28,.05)}
.support h3{font-size:18px;font-weight:800;margin-bottom:10px}
.support .acc{font-size:18px;font-weight:700;color:var(--ink)}
.support .nm{font-size:15px;color:var(--ink-soft);margin-top:2px}
.support .pd{font-size:14px;color:var(--muted);margin-top:8px}

.foot{text-align:center;font-size:12.5px;color:var(--muted);padding:24px 20px 10px;
  line-height:1.5}

/* ---- bottom nav ---- */
.tabbar{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;
  max-width:430px;background:#fff;border-top:1px solid var(--line);
  display:flex;justify-content:space-around;padding:9px 8px
  calc(9px + env(safe-area-inset-bottom));z-index:30}
.tab{display:flex;flex-direction:column;align-items:center;gap:3px;color:var(--muted);
  font-size:11px;font-weight:600;padding:6px 14px;border-radius:999px}
.tab svg{width:23px;height:23px}
.tab.active{color:#fff;background:var(--primary)}
"""

# ---------------- HTML helpers ----------------
HEAD = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800;900&family=Plus+Jakarta+Sans:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head><body><div class="app">"""

def topbar():
    return f'<div class="topbar"><a class="hb" href="index.html">{IC["home"]}</a><h1>2026 Outreach</h1></div>'

def tabbar(active):
    items=[("index.html","cal","일정","schedule"),
           ("wed.html","fork","식단","meal"),
           ("team.html","people","팀 정보","team"),
           ("team.html#prayer","arch","기도","prayer")]
    h='<nav class="tabbar">'
    for href,ic,label,key in items:
        cls="tab active" if key==active else "tab"
        h+=f'<a class="{cls}" href="{href}">{IC[ic]}<span>{label}</span></a>'
    return h+'</nav>'

FOOT='<div class="foot">통영 물댄동산교회 위드공동체 · 2026 여름 아웃리치</div>'
END='</div></body></html>'

# ---------------- DATA ----------------
DAYS = {
"wed":{"name":"수요일","color":"var(--wed)","sub":"하루를 열며 차분히 시작해요.","meals":[
   {"ic":"pot","label":"저녁","time":"18:00","dish":"떡만둣국","memo":"영화언니 · 들통 대량 조리 (수·목 메뉴는 자유 운영)"},
   {"ic":"fruit","label":"야식","dish":"과일 · 과자","memo":"배달 없이 자체 간식으로 진행"},
]},
"thu":{"name":"목요일","color":"var(--thu)","sub":"메인 사역일 — 든든하게 채워요.","meals":[
   {"ic":"sun","label":"아침","time":"07:00","dish":"조식 & 새벽 큐티","memo":"바나나·계란·시리얼·식빵·잼·예비 컵라면 / 전날 저녁 방으로 미리 제공, 자율 식사하며 큐티"},
   {"ic":"fork","label":"점심","dish":"자유 메뉴","memo":"메인 사역 준비 및 지원 체계 확인"},
   {"ic":"punch","label":"간식","time":"14:00–16:00","dish":"화채","memo":"공원 전체 행사 외부 지원 · 외부 화구 2개(팀장님 먼저) · 붕어빵 아이스크림 완비"},
   {"ic":"pot","label":"저녁","dish":"푸짐한 저녁 식사","memo":"내부 인덕션 1개 + 외부 화구 활용 · 간단한 데코레이션"},
   {"ic":"bowl","label":"야식","dish":"배달","memo":"간식비 한도 내 사용 후 영수증 별도 첨부"},
]},
"fri":{"name":"금요일","color":"var(--fri)","sub":"일정을 확인하고 은혜로운 하루 보내세요.","meals":[
   {"ic":"sun","label":"아침","time":"07:00","dish":"조식 & 새벽 큐티","memo":"전날 저녁 방으로 미리 배달 · 간단히 먹고 일과 시작"},
   {"ic":"walk","label":"오전","dish":"노방전도","memo":"공원 전체 행사 · 다과 지참(사탕·초콜릿·차·음료)"},
   {"ic":"fork","label":"점심","dish":"자유 메뉴","memo":"숙소 내 구비 식자재 활용"},
   {"ic":"store","label":"저녁","dish":"외식 (식당)","memo":"식당 장소 및 메뉴 선정 완료 필요"},
   {"ic":"bowl","label":"야식","dish":"배달","memo":"간식비 한도 내 사용 후 영수증 별도 첨부"},
]},
"sat":{"name":"토요일","color":"var(--sat)","sub":"잘 마무리하고 평안히 돌아가요.","meals":[
   {"ic":"sun","label":"아침","time":"07:00","dish":"조식 & 새벽 큐티","memo":"숙소 비품 및 잔여 식자재 활용"},
   {"ic":"store","label":"점심","dish":"외식 (식당)","memo":"장소·메뉴 선정 · 식사 후 행사 마무리"},
]},
}

def render_day(key):
    d=DAYS[key]
    cards=""
    for m in d["meals"]:
        time=f'<span class="mt">{m["time"]}</span>' if m.get("time") else ""
        memo=f'<div class="memo">{m["memo"]}</div>' if m.get("memo") else ""
        center="" if m.get("memo") else " center"
        warm=" warm" if m["label"] in ("야식",) else ""
        cards+=f'''<div class="mcard" style="--c:{d['color']}">
  <div class="mhead"><span class="mi">{IC[m['ic']]}</span><span class="ml">{m['label']}</span>{time}</div>
  <div class="inner{warm}{center}"><span class="dish">{m['dish']}</span>{memo}</div>
</div>'''
    body=f'''{HEAD.format(title=d['name']+" · 2026 Outreach")}
{topbar()}
<div class="page" style="--c:{d['color']}">
  <div class="dayhead"><div class="dt">{d['name']}</div><div class="ds">{d['sub']}</div></div>
  {cards}
  {FOOT}
</div>
{tabbar('meal' if key=='wed' else ('schedule' if False else 'meal'))}
{END}'''
    open(f"{ROOT}/{key}.html","w").write(body)

# ---------------- HOME ----------------
def render_home():
    tiles=""
    summ={"wed":"떡만둣국 · 야식","thu":"메인 사역일","fri":"노방전도 · 외식","sat":"마무리 · 외식"}
    icon={"wed":"pot","thu":"sun","fri":"walk","sat":"store"}
    for k in ["wed","thu","fri","sat"]:
        d=DAYS[k]
        tiles+=f'''<a class="tile" style="--c:{d['color']}" href="{k}.html">
   <span class="ti">{IC[icon[k]]}</span><span class="tl">{d['name']}</span>
   <span class="ts">{summ[k]}</span></a>'''
    body=f'''{HEAD.format(title="통영 아웃리치 식사팀 가이드")}
{topbar()}
<div class="page">
  <div class="hero"><img src="assets/poster.png" alt="2026 통영 아웃리치 포스터 — 돌이켜 나아가라"></div>
  <div class="welcome"><b>식사팀 가이드</b>요일을 눌러 그날의 식단과 일정을 확인하세요.</div>
  <div class="grid">
    {tiles}
    <a class="tile tile-wide" href="team.html"><span class="ti">{IC['people']}</span><span class="tl">팀 소개 & 기도제목</span></a>
  </div>
  {FOOT}
</div>
{tabbar('schedule')}
{END}'''
    open(f"{ROOT}/index.html","w").write(body)

# ---------------- TEAM ----------------
def render_team():
    prayers=["통영 땅에 회개와 부흥의 역사가 임하기를",
             "팀원들이 각자의 은사로 한 영혼을 살리는 사명 감당하기를",
             "성령 안에서 팀원들이 한 팀으로 연합하기를",
             "준비하는 모든 사역으로 구속사의 말씀이 전해지기를",
             "팀원 각자가 소망하는 영역에서 하나님의 음성 듣기를"]
    li="".join(f"<li>{p}</li>" for p in prayers)
    body=f'''{HEAD.format(title="팀 소개 & 기도제목 · 2026 Outreach")}
{topbar()}
<div class="page">
  <img class="teamphoto" src="assets/team.jpg" alt="2026 통영 아웃리치 식사팀 단체사진">
  <div class="archcard" id="prayer">
    <div class="cross">{IC['cross']}</div>
    <h2>기도제목</h2>
    <ol class="prayers">{li}</ol>
  </div>
  <div class="support">
    <h3>후원계좌</h3>
    <div class="acc">카카오뱅크 3333-261-292139</div>
    <div class="nm">(예금주 이은주)</div>
    <div class="pd">기간 2026.07.29 ~ 08.01</div>
  </div>
  {FOOT}
</div>
{tabbar('team')}
{END}'''
    open(f"{ROOT}/team.html","w").write(body)

# ---------------- BUILD ----------------
open(f"{ROOT}/assets/style.css","w").write(CSS)
render_home()
for k in DAYS: render_day(k)
render_team()
print("built:", sorted(os.listdir(ROOT)))
