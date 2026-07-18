# -*- coding: utf-8 -*-
"""통영 아웃리치 식사팀 가이드
   구글 시트 공개 CSV 읽기 버전 — API 키 불필요!
"""
import base64
import csv
import io
import urllib.request
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ─────────────────────── 페이지 설정 ───────────────────────
st.set_page_config(
    page_title="통영 아웃리치 식사팀",
    page_icon="🍚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  header[data-testid="stHeader"]{display:none}
  #MainMenu, footer{visibility:hidden}
  .block-container{padding:0 !important;max-width:100% !important}
  [data-testid="stAppViewContainer"]{background:#f6efdd}
  iframe{display:block;margin:0 auto}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent

# ─────────────────────── 구글 시트 설정 ───────────────────────
SPREADSHEET_ID = "13Pb6eBYSsGoK4cpXhSeGGKKdRXvBaG_Q8SoQB9wcUeg"
SHEET_NAME = "meals"
CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
    f"/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
)

# 담당자 · 준비재료 입력용 구글폼 링크 (폼 생성 후 이 값만 채우면 자동으로 버튼이 활성화됨)
MEAL_FORM_EMBED_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdJaiAH29MG_AihiZfKYuvJBBto4CxnPf0KOw7Gh5NMThC11g/viewform?embedded=true"
# 폼 응답이 쌓이는 스프레드시트 (담당자·준비재료를 요일 카드에 자동으로 합쳐 보여줄 때 사용)
FORM_RESPONSE_SHEET_ID = "1acelubO2of-IFVZOahqnbZp6p4Lfd2p8OIf4ECTMdGo"
FORM_RESPONSE_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{FORM_RESPONSE_SHEET_ID}/gviz/tq?tqx=out:csv"
)

# ─────────────────────── 데이터 로드 ───────────────────────
@st.cache_data(ttl=60)
def load_all_data():
    """구글 시트 하나에서 식단(식단)과 기타사항(기타)을 함께 읽어옵니다."""
    try:
        req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(raw))

        meal_data  = {}
        extra_data = {}

        for row in reader:
            kind = row.get("구분", "").strip()

            if kind == "식단":
                day       = row.get("요일/분류", "").strip()
                meal_type = row.get("식사종류", "").strip()
                if not day or not meal_type:
                    continue
                if day not in meal_data:
                    meal_data[day] = {}
                meal_data[day][meal_type] = {
                    "dish": row.get("메뉴/내용", "").strip(),
                    "memo": row.get("메모/비고", "").strip(),
                    "time": row.get("시간", "").strip(),
                    "owner": row.get("담당자", "").strip(),
                    "ingredients": row.get("준비재료및수량", "").strip(),
                }

            elif kind == "기타":
                category = row.get("요일/분류", "").strip()
                content  = row.get("메뉴/내용", "").strip() or row.get("식사종류", "").strip()
                note     = row.get("메모/비고", "").strip()
                if not category or not content:
                    continue
                if category not in extra_data:
                    extra_data[category] = []
                extra_data[category].append((content, note))

        meal_data = meal_data if meal_data else get_default_data()
        meal_data = apply_form_responses(meal_data)
        return (
            meal_data,
            extra_data if extra_data else get_default_extra(),
        )
    except Exception:
        return apply_form_responses(get_default_data()), get_default_extra()

def apply_form_responses(meal_data):
    """구글폼 응답(담당자·준비재료)을 해당 요일·끼니 카드에 합쳐 넣습니다."""
    try:
        req = urllib.request.Request(FORM_RESPONSE_CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(raw))
        for row in reader:
            day       = row.get("요일", "").strip()
            meal_type = row.get("식사종류", "").strip()
            owner     = row.get("담당자 이름", "").strip()
            ingredients = row.get("준비재료 및 수량", "").strip()
            if day in meal_data and meal_type in meal_data[day]:
                if owner:
                    meal_data[day][meal_type]["owner"] = owner
                if ingredients:
                    meal_data[day][meal_type]["ingredients"] = ingredients
    except Exception:
        pass
    return meal_data

def get_default_extra():
    return {
        "아침 공통 메뉴": [
            ("바나나 · 삶은계란 · 시리얼 · 우유 · 식빵 · 잼 · 컵라면", ""),
            ("커피 알아보기 (철수 형)", "확인완료"),
        ],
        "상시 반찬": [("김치 · 단무지 · 김", "")],
        "상시 간식": [
            ("초콜릿 · 비타민젤리 · 말랑카우 · 마이쮸 · 자유시간", "상시구비품"),
            ("타먹는 커피 · 디카페인 · 얼음", "상시구비품"),
        ],
        "밥 담당": [("오재화 — 수요일 체크", "담당")],
        "준비물": [
            ("온수통", "우리들교회 대여가능"),
            ("아이스박스", "우리들교회 대여가능 / 통영에서도 준비"),
            ("들통", "준비됨"),
            ("버너", "준비됨"),
            ("요리기구", "숙소에서 챙겨가면 됨"),
            ("웍", "찾아보시는 중"),
            ("냄비 · 도마 · 볼", "숙소에서 챙겨가면 됨"),
            ("밥솥 — 숙소 2개 + 교회 1개 (10인용 2개 / 20인용 1개)", "숙소"),
        ],
    }

def get_default_data():
    return {
        "수요일": {
            "저녁": {"dish": "떡만두국", "memo": "간단한거", "time": "18:00", "owner": "현호",
                     "ingredients": "만두 00봉지, 떡국떡 00봉지, 파 00단, 사골육수 00g봉지, 후추"},
            "야식": {"dish": "수박 · 방울토마토 등 과일 · 과자", "memo": "간단한거", "time": "", "owner": "", "ingredients": ""},
        },
        "목요일": {
            "아침": {"dish": "조식 & 새벽 큐티", "memo": "바나나·삶은계란·시리얼·우유·식빵·잼·컵라면", "time": "07:00", "owner": "", "ingredients": ""},
            "점심": {"dish": "소불고기 덮밥 + 오이냉국", "memo": "든든한거(육류)", "time": "", "owner": "설희", "ingredients": ""},
            "간식": {"dish": "화채 + 아이스크림", "memo": "시원한거", "time": "14:00–16:00", "owner": "", "ingredients": ""},
            "저녁": {"dish": "보쌈 + 빔국수 + 쌈", "memo": "든든한거+시원한거", "time": "", "owner": "재화형님", "ingredients": ""},
            "야식": {"dish": "떡볶이 세트", "memo": "직접 만들기", "time": "", "owner": "미정", "ingredients": ""},
        },
        "금요일": {
            "아침": {"dish": "조식 & 새벽 큐티", "memo": "전날 저녁 방으로 미리 배달", "time": "07:00", "owner": "", "ingredients": ""},
            "오전": {"dish": "노방전도", "memo": "공원 전체 행사 · 다과 지참", "time": "", "owner": "", "ingredients": ""},
            "점심": {"dish": "가정식 백반 (계란말이+김치찌개+제육볶음+기타반찬)", "memo": "백반", "time": "", "owner": "현호", "ingredients": ""},
            "저녁": {"dish": "외식 (식당)", "memo": "외식 및 카페", "time": "", "owner": "", "ingredients": ""},
        },
        "토요일": {
            "아침": {"dish": "조식 & 새벽 큐티", "memo": "숙소 비품 및 잔여 식자재 활용", "time": "07:00", "owner": "", "ingredients": ""},
            "점심": {"dish": "외식 (식당)", "memo": "장소·메뉴 선정 · 식사 후 행사 마무리", "time": "", "owner": "", "ingredients": ""},
        },
    }

# ─────────────────────── 아이콘 ───────────────────────
MEAL_ICONS = {
    "아침": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4"/></svg>',
    "점심": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3v7M5 3v4.5a2 2 0 0 0 4 0V3M7 10v11"/><path d="M17 3c-1.7 0-3 2-3 5s1 4 2 4v9"/></svg>',
    "오전": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="13" cy="4.5" r="1.8"/><path d="M11 8.5 9 13l2.5 1.5L13 21M13 11l3 1.5M9 13l-2 5M13 11l-1-2.5"/></svg>',
    "간식": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 9h15l-1.3 9a2 2 0 0 1-2 1.7H7.8a2 2 0 0 1-2-1.7z"/><path d="M9 12.5h.01M12 14.5h.01M15 12h.01M12 6.5c0-1 1.5-1.5 1.5-2.5"/></svg>',
    "저녁": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 10h14v6a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z"/><path d="M3 10h18M8 10V8.5M16 10V8.5M9.5 5.5c.6-1 2.4-1 3 0M12.5 4c.6-1 2.4-1 3 0"/></svg>',
    "야식": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 11h17a8.5 8.5 0 0 1-17 0z"/><path d="M2.5 11h19M9 7.5c-.5-1 .5-2 0-3M13 7.5c-.5-1 .5-2 0-3M16.5 18l1.5 1.5"/></svg>',
}
MEAL_ORDER = ["아침", "오전", "점심", "간식", "저녁", "야식"]

# ─────────────────────── HTML 유틸 ───────────────────────
def b64(path, mime):
    try:
        data = (ROOT / path).read_bytes()
        return f"data:{mime};base64," + base64.b64encode(data).decode()
    except Exception:
        return ""

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ─────────────────────── 요일 탭 HTML (식단 내 이동) ───────────────────────
DAY_TAB_HTML = """
<div class="daytab-bar">
  <span class="daytab" onclick="show('wed','meal')" data-day="wed">수</span>
  <span class="daytab" onclick="show('thu','meal')" data-day="thu">목</span>
  <span class="daytab" onclick="show('fri','meal')" data-day="fri">금</span>
  <span class="daytab" onclick="show('sat','meal')" data-day="sat">토</span>
  <span class="daytab" onclick="show('extra','extra')" data-day="extra">기타</span>
</div>"""

def build_day_section(day_id, day_label, subtitle, color_var, meals):
    cards = ""
    for mt in MEAL_ORDER:
        if mt not in meals:
            continue
        info = meals[mt]
        icon = MEAL_ICONS.get(mt, MEAL_ICONS["저녁"])
        time_badge = f'<span class="mt">{esc(info["time"])}</span>' if info.get("time") else ""
        warm = " warm" if mt == "야식" else ""
        owner_val = info.get("owner", "").strip()
        owner_tag = (
            f'<div class="owner">담당 · {esc(owner_val)}</div>' if owner_val
            else '<div class="owner owner-empty">담당 미정</div>'
        )
        ing_val = info.get("ingredients", "").strip()
        ingredients_block = (
            f'<div class="ingredients"><b>준비재료</b>{esc(ing_val)}</div>' if ing_val
            else '<div class="ingredients ingredients-empty"><b>준비재료</b>아직 입력되지 않았어요</div>'
        )
        cards += f"""
<div class="mcard" style="--c:var({color_var})">
  <div class="mhead">
    <span class="mi">{icon}</span>
    <span class="ml">{mt}</span>{time_badge}
  </div>
  <div class="inner{warm}">
    <span class="dish">{esc(info.get("dish",""))}</span>
    <div class="memo">{esc(info.get("memo",""))}</div>
    {owner_tag}
  </div>
  {ingredients_block}
</div>"""

    return f"""<section id="page-{day_id}" class="page-sec" style="--c:var({color_var})">
  {DAY_TAB_HTML}
  <div class="page">
    <div class="dayhead"><div class="dt">{day_label}</div><div class="ds">{subtitle}</div></div>
    {cards}
    <div class="foot">통영 물댄동산교회 위드공동체 · 2026 여름 아웃리치</div>
  </div>
</section>"""

# ─────────────────────── 메인 HTML 빌드 ───────────────────────
def build_extra_section(extra_data):
    """기타사항 섹션 HTML을 동적으로 생성합니다."""
    CATEGORY_ORDER = ["아침 공통 메뉴", "상시 반찬", "상시 간식", "밥 담당", "준비물"]
    all_categories = CATEGORY_ORDER + [c for c in extra_data if c not in CATEGORY_ORDER]

    sections_html = ""
    for category in all_categories:
        if category not in extra_data:
            continue
        items = extra_data[category]
        rows = ""
        for content, note in items:
            tag = f'<span class="info-tag">{esc(note)}</span>' if note else ""
            rows += f"<li>{tag}{esc(content)}</li>"
        sections_html += f"""
    <div class="info-section">
      <h3>{esc(category)}</h3>
      <ul class="info-list">{rows}</ul>
    </div>"""

    return f"""<section id="page-extra" class="page-sec">
  <div class="page">
    <div class="dayhead" style="--c:#7c6fe8">
      <div class="dt" style="color:#7c6fe8;font-size:30px">기타사항</div>
      <div class="ds">준비물 · 상시 구비품 · 기타 안내</div>
    </div>
    {sections_html}
    <div class="foot">통영 물댄동산교회 위드공동체 · 2026 여름 아웃리치</div>
  </div>
</section>"""

def build_html(meal_data, sheet_url, extra_data=None):
    if extra_data is None:
        extra_data = get_default_extra()
    poster = b64("assets/poster.png", "image/png")
    team   = b64("assets/team.jpg",   "image/jpeg")

    wed_html = build_day_section("wed", "수요일", "하루를 열며 차분히 시작해요.",          "--wed", meal_data.get("수요일", {}))
    thu_html = build_day_section("thu", "목요일", "메인 사역일 — 든든하게 채워요.",        "--thu", meal_data.get("목요일", {}))
    fri_html = build_day_section("fri", "금요일", "일정을 확인하고 은혜로운 하루 보내세요.", "--fri", meal_data.get("금요일", {}))
    sat_html = build_day_section("sat", "토요일", "잘 마무리하고 평안히 돌아가요.",        "--sat", meal_data.get("토요일", {}))

    if MEAL_FORM_EMBED_URL:
        form_response_url = f"https://docs.google.com/spreadsheets/d/{FORM_RESPONSE_SHEET_ID}/edit"
        my_meal_btn = f'''<div style="display:flex;justify-content:center;gap:8px">
      <div onclick="toggleMealForm()"
       style="display:inline-flex;align-items:center;white-space:nowrap;
              gap:6px;background:#fff;color:var(--primary);
              border:1.5px solid var(--primary);border-radius:999px;padding:10px 16px;font-size:13px;
              font-weight:700;cursor:pointer;-webkit-tap-highlight-color:transparent">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">
          <path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>
        </svg>
        내 담당 끼니 입력하기
      </div>
      <a href="{form_response_url}" target="_blank"
         style="display:inline-flex;align-items:center;white-space:nowrap;
                gap:6px;background:#fff;color:var(--ink-soft);
                border:1.5px solid var(--line);border-radius:999px;padding:10px 14px;font-size:13px;
                font-weight:700;text-decoration:none;-webkit-tap-highlight-color:transparent">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">
          <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>
        </svg>
        제출 현황 보기
      </a>
    </div>
    <div style="text-align:center;font-size:11px;color:#7d8278;margin-top:8px">
      마지막 제출이 최종본이 돼요 — 부분만 적지 말고 재료 전체를 다시 적어주세요.
    </div>
    <div id="myform-wrap" style="display:none;margin-top:14px;text-align:left">
      <iframe id="myform-iframe" style="width:100%;height:820px;border:none;border-radius:16px;
              box-shadow:0 4px 20px rgba(27,28,28,.07)" loading="lazy"></iframe>
    </div>'''
    else:
        my_meal_btn = '''<div style="display:inline-block;background:var(--card-low);color:var(--muted);
         border-radius:999px;padding:10px 20px;font-size:12.5px;font-weight:700">
      내 담당 끼니 입력 폼 준비 중
    </div>'''

    sheet_btn = f"""
<div style="text-align:center;padding:14px 20px 0">
  {my_meal_btn}
</div>
<div style="text-align:center;padding:10px 20px 0">
  <a href="{sheet_url}" target="_blank"
     style="display:inline-flex;align-items:center;gap:8px;background:#4e6448;color:#fff;
            border-radius:999px;padding:11px 20px;font-size:13px;font-weight:700;
            text-decoration:none;box-shadow:0 4px 14px rgba(78,100,72,.3)">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
    </svg>
    팀장 전용 · 메뉴 전체 수정 (구글 시트)
  </a>
  <div style="font-size:11px;color:#7d8278;margin-top:6px">수정 후 1분 이내 자동 반영</div>
</div>
<div style="text-align:center;padding:20px 20px 4px">
  <div style="display:inline-block;background:#fff;border-radius:16px;padding:16px;
              box-shadow:0 4px 20px rgba(27,28,28,.07);border:1px solid var(--line)">
    <img
      src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&margin=6&data=https://ttmeal.streamlit.app"
      alt="앱 QR코드"
      style="width:160px;height:160px;display:block;border-radius:6px"
    >
    <div style="margin-top:10px;font-size:13px;font-weight:800;color:var(--ink);
                display:flex;align-items:center;justify-content:center;gap:5px">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--primary)"
           stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="5" y="2" width="14" height="20" rx="2"/>
        <path d="M12 18h.01"/>
      </svg>
      식단팀 앱 바로가기
    </div>
    <div style="font-size:11px;color:var(--muted);margin-top:3px">카메라로 찍으면 바로 접속돼요</div>
  </div>
</div>""" if sheet_url else ""

    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800;900&family=Plus+Jakarta+Sans:wght@600;700&display=swap" rel="stylesheet">
<style>
:root{{
  --surface:#fdf8ee;--card:#ffffff;--inner:#e8f3e4;--inner-warm:#fdecd6;
  --primary:#4e6448;--primary-dim:#a9c2a0;
  --ink:#29281f;--ink-soft:#55564a;--muted:#8a8c78;--line:#ece3cf;
  --wed:#2fa8e8;--thu:#4cc26a;--fri:#ff8a4c;--sat:#ffc233;
  --r-md:.9rem;--r-lg:1.25rem;--r-xl:1.75rem;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:var(--surface)}}
body{{font-family:'Noto Sans KR','Plus Jakarta Sans',sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased}}
.app{{max-width:430px;margin:0 auto;min-height:100vh;background:var(--surface);padding-bottom:108px}}
a{{text-decoration:none;color:inherit}}

/* 탑바 */
.topbar{{display:flex;align-items:center;gap:8px;padding:16px 20px 14px;border-bottom:1px solid var(--line);background:var(--surface);position:sticky;top:0;z-index:20}}
.topbar .hb{{width:34px;height:34px;color:var(--primary);flex:none;cursor:pointer}}
.topbar .hb svg{{width:24px;height:24px}}
.topbar h1{{flex:1;text-align:center;font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:21px;color:var(--primary);letter-spacing:-.01em;margin-right:34px}}

.page{{padding:20px 20px 8px}}

/* 홈 */
.hero{{border-radius:var(--r-xl);overflow:hidden;box-shadow:0 8px 30px rgba(78,100,72,.16);margin-bottom:10px}}
.hero img{{display:block;width:100%}}
.welcome{{text-align:center;margin:14px 4px 16px;color:var(--ink-soft);font-size:15px;line-height:1.55}}
.welcome b{{display:block;font-size:18px;color:var(--primary);font-weight:800;margin-bottom:4px}}

/* ── 홈: 수목금토+기타 한 줄 타일 ── */
.day-row{{display:flex;gap:6px;margin-bottom:10px}}
.day-tile{{flex:1;min-width:0;background:var(--card);border-radius:var(--r-lg);padding:14px 3px 10px;
  box-shadow:0 6px 18px rgba(27,28,28,.07);display:flex;flex-direction:column;
  align-items:center;gap:7px;border:1px solid var(--line);cursor:pointer;
  transition:transform .12s;-webkit-tap-highlight-color:transparent}}
.day-tile:active{{transform:scale(.95)}}
.day-tile .di{{width:30px;height:30px;border-radius:.65rem;flex:none;
  background:color-mix(in srgb, var(--c) 16%, #fff);color:var(--c);
  display:flex;align-items:center;justify-content:center}}
.day-tile .di svg{{width:16px;height:16px}}
.day-tile .dl{{font-size:14px;font-weight:800;color:var(--ink)}}
.day-tile .ds{{font-size:9.5px;color:var(--muted);text-align:center;line-height:1.25;word-break:keep-all}}

/* 팀 타일 */
.tile-wide{{width:100%;background:var(--primary);color:#fff;border-radius:999px;
  padding:16px 20px;display:flex;align-items:center;justify-content:center;gap:10px;
  box-shadow:0 6px 22px rgba(78,100,72,.28);cursor:pointer;margin-bottom:4px;
  -webkit-tap-highlight-color:transparent;transition:transform .12s}}
.tile-wide:active{{transform:scale(.98)}}
.tile-wide .ti{{width:22px;height:22px;color:#fff}}
.tile-wide .ti svg{{width:22px;height:22px}}
.tile-wide .tl{{color:#fff;font-size:16px;font-weight:700}}

/* 요일 내 식단 탭 바 */
.daytab-bar{{display:flex;background:#fff;border-bottom:1px solid var(--line);
  position:sticky;top:57px;z-index:19;gap:0}}
.daytab{{flex:1;text-align:center;padding:10px 0;font-size:15px;font-weight:800;
  color:var(--muted);cursor:pointer;border-bottom:3px solid transparent;
  transition:color .15s,border-color .15s;-webkit-tap-highlight-color:transparent}}
.daytab.active{{color:var(--c,var(--primary));border-bottom-color:var(--c,var(--primary))}}

/* 식단 카드 */
.dayhead{{text-align:center;padding:16px 0 16px}}
.dayhead .dt{{font-size:36px;font-weight:900;color:var(--c);letter-spacing:-.02em}}
.dayhead .ds{{font-size:14px;color:var(--muted);margin-top:4px}}
.mcard{{background:var(--card);border-radius:var(--r-xl);padding:18px;margin-bottom:14px;border:1px solid var(--line);border-top:5px solid var(--c);box-shadow:0 6px 22px rgba(27,28,28,.06)}}
.mhead{{display:flex;align-items:center;gap:9px;margin-bottom:11px}}
.mhead .mi{{width:24px;height:24px;color:var(--c);flex:none}}
.mhead .mi svg{{width:24px;height:24px}}
.mhead .ml{{font-size:17px;font-weight:800;color:var(--ink);flex:1}}
.mhead .mt{{font-family:'Plus Jakarta Sans',sans-serif;font-size:11px;font-weight:700;letter-spacing:.04em;color:var(--ink-soft);background:var(--inner);padding:4px 10px;border-radius:999px}}
.inner{{background:var(--inner);border-radius:var(--r-md);padding:13px 15px}}
.inner.warm{{background:var(--inner-warm)}}
.inner .dish{{font-size:16px;font-weight:800;color:var(--ink)}}
.inner .memo{{font-size:13px;color:var(--ink-soft);line-height:1.55;margin-top:4px}}
.owner{{margin-top:8px;display:inline-block;font-size:11px;font-weight:800;color:var(--primary);
  background:var(--primary-soft);padding:3px 10px;border-radius:999px}}
.owner-empty{{color:var(--muted);background:var(--card-low)}}
.ingredients{{margin-top:10px;padding:9px 12px;background:var(--card-low);border-radius:var(--r-md);
  font-size:12px;color:var(--ink-soft);line-height:1.6}}
.ingredients b{{display:block;font-size:11px;font-weight:800;color:var(--ink);margin-bottom:2px}}
.ingredients-empty{{color:var(--muted);font-style:italic}}
.ingredients-empty b{{color:var(--muted)}}

/* 기타사항 */
.info-section{{background:var(--card);border-radius:var(--r-xl);padding:18px;margin-bottom:14px;border:1px solid var(--line);box-shadow:0 6px 22px rgba(27,28,28,.06)}}
.info-section h3{{font-size:15px;font-weight:800;color:var(--primary);margin-bottom:10px;display:flex;align-items:center;gap:6px}}
.info-list{{list-style:none;padding:0}}
.info-list li{{font-size:13.5px;color:var(--ink-soft);line-height:1.6;padding:3px 0;border-bottom:1px solid var(--line)}}
.info-list li:last-child{{border-bottom:none}}
.info-tag{{display:inline-block;background:var(--inner);border-radius:999px;padding:2px 8px;font-size:11px;font-weight:700;color:var(--muted);margin-right:6px}}

/* 팀 */
.teamphoto{{width:100%;border-radius:var(--r-lg);display:block;box-shadow:0 6px 22px rgba(27,28,28,.08);margin-bottom:22px}}
.archcard{{background:var(--card);border-radius:var(--r-xl);padding:34px 24px 26px;text-align:center;border-top:5px solid var(--primary);box-shadow:0 6px 24px rgba(27,28,28,.07);margin-bottom:20px}}
.archcard .cross{{width:28px;height:28px;color:#caa24a;margin:0 auto 8px}}
.archcard h2{{font-size:22px;font-weight:900;color:var(--ink);margin-bottom:18px}}
.prayers{{list-style:none;text-align:left;counter-reset:p}}
.prayers li{{display:flex;gap:10px;margin-bottom:14px;font-size:14.5px;line-height:1.5;color:var(--ink-soft)}}
.prayers li::before{{counter-increment:p;content:counter(p) ".";font-weight:800;color:var(--primary);flex:none;min-width:16px}}
.support{{background:var(--card);border-radius:var(--r-xl);padding:22px;text-align:center;border:1px solid var(--line);box-shadow:0 6px 22px rgba(27,28,28,.06)}}
.support h3{{font-size:17px;font-weight:800;margin-bottom:8px}}
.support .acc{{font-size:17px;font-weight:700;color:var(--ink)}}
.support .nm{{font-size:14px;color:var(--ink-soft);margin-top:2px}}
.support .pd{{font-size:13px;color:var(--muted);margin-top:6px}}

.foot{{text-align:center;font-size:12px;color:var(--muted);padding:20px 20px 8px;line-height:1.5}}

/* 하단 탭바 */
.tabbar{{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);width:calc(100% - 32px);max-width:398px;background:#fff;border:1px solid var(--line);border-radius:999px;display:flex;justify-content:space-around;padding:9px 8px calc(9px + env(safe-area-inset-bottom));box-shadow:0 10px 30px rgba(27,28,28,.12);z-index:30}}
.tab{{display:flex;flex-direction:column;align-items:center;gap:3px;color:var(--muted);font-size:11px;font-weight:600;padding:6px 14px;border-radius:999px;cursor:pointer;-webkit-tap-highlight-color:transparent}}
.tab svg{{width:22px;height:22px}}
.tab.active{{color:#fff;background:var(--primary)}}
.page-sec{{display:none}}
</style></head>
<body><div class="app">

<div class="topbar">
  <span class="hb" onclick="show('home')">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V20h14V9.5"/></svg>
  </span>
  <h1>2026 Outreach</h1>
</div>

<!-- ══ 홈 ══ -->
<section id="page-home" class="page-sec">
  <div class="page">
    <div class="hero"><img src="{poster}" alt="2026 통영 아웃리치 포스터"></div>

    <div class="tile-wide" onclick="show('team','people')">
      <span class="ti"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="8.5" r="2.4"/><path d="M16 14.2A4.6 4.6 0 0 1 20.5 19"/></svg></span>
      <span class="tl">팀 소개 &amp; 기도제목</span>
    </div>

    <div class="welcome"><b>식사팀 가이드</b>요일을 눌러 그날의 식단을 확인하세요.</div>

    <!-- 수목금토 한 줄 -->
    <div class="day-row">
      <div class="day-tile" style="--c:var(--wed)" onclick="show('wed','meal')">
        <span class="di"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 10h14v6a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z"/><path d="M3 10h18M8 10V8.5M16 10V8.5M9.5 5.5c.6-1 2.4-1 3 0M12.5 4c.6-1 2.4-1 3 0"/></svg></span>
        <span class="dl">수</span>
      </div>
      <div class="day-tile" style="--c:var(--thu)" onclick="show('thu','meal')">
        <span class="di"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4"/></svg></span>
        <span class="dl">목</span>
      </div>
      <div class="day-tile" style="--c:var(--fri)" onclick="show('fri','meal')">
        <span class="di"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="13" cy="4.5" r="1.8"/><path d="M11 8.5 9 13l2.5 1.5L13 21M13 11l3 1.5M9 13l-2 5M13 11l-1-2.5"/></svg></span>
        <span class="dl">금</span>
      </div>
      <div class="day-tile" style="--c:var(--sat)" onclick="show('sat','meal')">
        <span class="di"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9h16l-1 11H5z"/><path d="M4 9 5.5 4h13L20 9M9 9V4.5M15 9V4.5"/></svg></span>
        <span class="dl">토</span>
      </div>
      <div class="day-tile" style="--c:#7c6fe8" onclick="show('extra','extra')">
        <span class="di"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2.5"/><path d="M9 9h6M9 12h6M9 15h4"/></svg></span>
        <span class="dl">기타</span>
      </div>
    </div>

    {sheet_btn}
    <div class="foot">통영 물댄동산교회 위드공동체 · 2026 여름 아웃리치</div>
  </div>
</section>

<!-- ══ 요일 섹션들 ══ -->
{wed_html}
{thu_html}
{fri_html}
{sat_html}

<!-- ══ 팀 소개 & 기도제목 ══ -->
<section id="page-team" class="page-sec">
  <div class="page">
    <img class="teamphoto" src="{team}" alt="식사팀 단체사진">
    <div class="archcard" id="prayer">
      <div class="cross"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M10.4 2h3.2v5.4H19v3.2h-5.4V22h-3.2V10.6H5V7.4h5.4z"/></svg></div>
      <h2>기도제목</h2>
      <ol class="prayers">
        <li>통영 땅에 회개와 부흥의 역사가 임하기를</li>
        <li>팀원들이 각자의 은사로 한 영혼을 살리는 사명 감당하기를</li>
        <li>성령 안에서 팀원들이 한 팀으로 연합하기를</li>
        <li>준비하는 모든 사역으로 구속사의 말씀이 전해지기를</li>
        <li>팀원 각자가 소망하는 영역에서 하나님의 음성 듣기를</li>
      </ol>
    </div>
    <div class="support">
      <h3>후원계좌</h3>
      <div class="acc">카카오뱅크 3333-261-292139</div>
      <div class="nm">(예금주 이은주)</div>
      <div class="pd">기간 2026.07.29 ~ 08.01</div>
      <div style="margin-top:16px">
        <img
          src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&margin=8&data=%EC%B9%B4%EC%B9%B4%EC%98%A4%EB%B1%85%ED%81%AC+3333-261-292139+%EC%98%88%EA%B8%88%EC%A3%BC+%EC%9D%B4%EC%9D%80%EC%A3%BC"
          alt="후원계좌 QR코드"
          style="width:160px;height:160px;border-radius:12px;border:1px solid var(--line)"
        >
        <div style="font-size:11px;color:var(--muted);margin-top:6px">QR 스캔 후 계좌번호를 확인하세요</div>
      </div>
    </div>
    <div class="foot">통영 물댄동산교회 위드공동체 · 2026 여름 아웃리치</div>
  </div>
</section>

{build_extra_section(extra_data)}


<!-- ══ 하단 탭바 ══ -->
<nav class="tabbar">
  <span class="tab" data-tab="cal"    onclick="show('home','cal')">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="16" rx="2.5"/><path d="M4 9h16M9 3v3M15 3v3"/></svg><span>일정</span>
  </span>
  <span class="tab" data-tab="meal"   onclick="show('wed','meal')">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3v7M5 3v4.5a2 2 0 0 0 4 0V3M7 10v11"/><path d="M17 3c-1.7 0-3 2-3 5s1 4 2 4v9"/></svg><span>식단</span>
  </span>
  <span class="tab" data-tab="extra"  onclick="show('extra','extra')">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2.5"/><path d="M9 9h6M9 12h6M9 15h4"/></svg><span>기타</span>
  </span>
  <span class="tab" data-tab="people" onclick="show('team','people')">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="8.5" r="2.4"/><path d="M16 14.2A4.6 4.6 0 0 1 20.5 19"/></svg><span>팀 정보</span>
  </span>
</nav>

</div>
<script>
var DAY_COLOR = {{wed:'var(--wed)',thu:'var(--thu)',fri:'var(--fri)',sat:'var(--sat)'}};

function toggleMealForm(){{
  var wrap = document.getElementById('myform-wrap');
  var ifr = document.getElementById('myform-iframe');
  if(!wrap) return;
  var opening = wrap.style.display === 'none';
  if(opening){{
    if(!ifr.src) ifr.src = {MEAL_FORM_EMBED_URL!r};
    wrap.style.display = 'block';
    setTimeout(function(){{ wrap.scrollIntoView({{behavior:'smooth', block:'start'}}); }}, 50);
  }} else {{
    wrap.style.display = 'none';
  }}
}}

function defaultTab(p){{
  if(p==='home') return 'cal';
  if(p==='team') return 'people';
  if(p==='extra') return 'extra';
  return 'meal';
}}

function show(page, tab){{
  document.querySelectorAll('.page-sec').forEach(function(s){{
    s.style.display = (s.id==='page-'+page) ? 'block' : 'none';
  }});
  var t = tab || defaultTab(page);
  document.querySelectorAll('.tab').forEach(function(el){{
    el.classList.toggle('active', el.dataset.tab===t);
  }});

  // 현재 페이지의 요일 탭바만 활성화 · 색상 적용 (섹션마다 탭바가 각각 있음)
  var daytabBar = document.querySelector('#page-'+page+' .daytab-bar');
  if(daytabBar){{
    daytabBar.querySelectorAll('.daytab').forEach(function(el){{
      el.classList.toggle('active', el.dataset.day===page);
    }});
    if(DAY_COLOR[page]) daytabBar.style.setProperty('--c', DAY_COLOR[page]);
  }}

  window.scrollTo(0,0);
}}
show('home');
</script>
</body></html>"""

# ─────────────────────── 메인 ───────────────────────
def main():
    meal_data, extra_data = load_all_data()
    sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit"
    html = build_html(meal_data, sheet_url, extra_data)
    components.html(html, height=900, scrolling=True)

if __name__ == "__main__":
    main()
