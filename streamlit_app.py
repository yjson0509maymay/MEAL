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

# 팀장 전용 작업 시트 (앱 데이터와는 별개 — 수정해도 앱에 자동 반영되지 않음)
TEAM_LEADER_SHEET_ID = "1GkvF5xchfYbH1yQ015_zEdmd5O7YDdCa"

# 아침 커피 주문 폼 (요일마다 별도 폼, 이름 + 음료 선택, 담당: 철수)
DRINK_FORMS = {
    "2026-07-30": {
        "label": "목요일",
        "meal_time": "아침",
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSemTAu8pNeHGfKh5nGNOJkuO9b8Nxb5wAdZCRHz2gU1ZyXXMA/viewform",
        "sheet_id": "1XY2UNd08vbBkEkSmJmbOSYpvDxh92-PUB-4Z2DMpegE",
    },
    "2026-07-31": {
        "label": "금요일",
        "meal_time": "아침",
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfPXwgLA-oNKbPKKIn1zO-MhmVVd2Y426iZAyq69cFvYLHnVA/viewform",
        "sheet_id": "1cpx_1ppncSNWl8tDbTPVD4tY9in14BDL0sl4ajVblGo",
    },
    "2026-08-01": {
        "label": "토요일",
        "meal_time": "아침",
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSc5WElJPctXq_geTIYHmmabQ9_rBtg2RdDCKbAgD5tWjIr9nQ/viewform",
        "sheet_id": "1hLnGdBE1bEDU7a_xnMH-y2GfVnXZisz4vsq1wcvuJJY",
    },
}

def find_drink_form(day_label):
    for entry in DRINK_FORMS.values():
        if entry["label"] == day_label:
            return entry
    return None

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
                owner    = row.get("담당자", "").strip()
                if not category or not content:
                    continue
                if category not in extra_data:
                    extra_data[category] = []
                extra_data[category].append((content, note, owner))

        meal_data = meal_data if meal_data else get_default_data()
        return (
            meal_data,
            extra_data if extra_data else get_default_extra(),
        )
    except Exception:
        return get_default_data(), get_default_extra()

def get_default_extra():
    return {
        "아침 공통 메뉴": [
            ("바나나 · 삶은계란 · 시리얼 · 우유 · 식빵 · 잼 · 컵라면 (목/금/토 3일 공용)", "", ""),
            ("배달커피 (아침 대체) 15잔 · 3일", "", "철수"),
        ],
        "공용 식재료": [
            ("쌀 10kg, 김치 5kg, 단무지 2팩, 김 30봉, 계란 30구, 파 2단, 양파 2kg, 다진마늘 500g, "
             "후추 1통, 참기름 1병, 볶음참깨 200g, 간장 1병, 고추장 1통, 고춧가루 1봉, 육수용코인 1통",
             "", ""),
        ],
        "상시 간식": [
            ("초콜릿 · 비타민젤리 · 말랑카우 · 마이쭈 · 자유시간 · 사탕", "상시구비품", ""),
            ("믹스커피 100개입 · 블랙커피 100개입", "상시구비품", ""),
        ],
        "밥 담당": [("수요일 체크", "", "오재화")],
        "준비물": [
            ("온수통", "우리들교회 대여가능", ""),
            ("아이스박스", "우리들교회 대여가능 / 통영에서도 준비", ""),
            ("들통", "준비됨", ""),
            ("버너", "준비됨", ""),
            ("요리기구", "숙소에서 챙겨가면 됨", ""),
            ("웍", "찾아보시는 중", ""),
            ("냄비 · 도마 · 볼", "숙소에서 챙겨가면 됨", ""),
            ("밥솥 — 숙소 2개 + 교회 1개 (10인용 2개 / 20인용 1개)", "숙소", ""),
            ("종이컵 100개 · 요리용 장갑 · 포크", "", ""),
        ],
    }

def get_default_data():
    return {
        "수요일": {
            "저녁": {"dish": "떡만두국", "memo": "간단한거 (30인분)", "time": "18:00", "owner": "현호",
                     "ingredients": "떡 4kg, 만두 3kg, 계란 15개, 파 2단, 육수팩 1봉"},
            "야식": {"dish": "수박 · 방울토마토 · 과자", "memo": "간단다과", "time": "", "owner": "",
                     "ingredients": "수박 4통, 방울토마토 3통, 과자 15개, 군것질거리"},
        },
        "목요일": {
            "아침": {"dish": "조식 & 새벽 큐티", "memo": "바나나·삶은계란·시리얼·우유·식빵·잼·컵라면 (목/금/토 3일 공용)", "time": "07:00",
                     "owner": "", "ingredients": ""},
            "점심": {"dish": "닭갈비덮밥 + 미소된장국", "memo": "든든한거(육류) (30인분)", "time": "", "owner": "설희",
                     "ingredients": "닭다리살정육 6kg, 양파 2kg, 냉동고구마 2kg, 대파 1kg, 깻잎 5묶음, 세척당근 3kg, 닭갈비소스 2kg, 소불고기양념 500g, 다진마늘 200g, 후추 2큰술, 카레가루 3큰술, 참기름 500ml, 볶음참깨 100g, 미소된장국 24인분"},
            "간식": {"dish": "수박화채 + 아이스크림", "memo": "시원한거", "time": "14:00–16:00", "owner": "",
                     "ingredients": "화채용수박 3통, 밀키스/사이다 3개, 얼음, 후르츠칵테일 2통, 아이스크림 30개, 황도 3통"},
            "저녁": {"dish": "보쌈 + 비빔면 + 쌈", "memo": "든든한거+시원한거 (35인분)", "time": "", "owner": "재화형님",
                     "ingredients": "돼지고기 9kg, 쌈무, 씸장, 새우젓, 양파(수육용) 1kg, 사과(수육용) 3개, 생강(수육용) 200g, 마늘(수육용) 500g, 파(수육용) 1단, 막국수면 9개, 비빔고추장, 메밀소바장국"},
            "야식": {"dish": "떡볶이 세트", "memo": "직접 만들기", "time": "", "owner": "미정",
                     "ingredients": "떡볶이떡 1.5kg, 고춧가루(집에서 가져감), 청정원 순창 1kg, 대파 1kg, 오뎅 10장, 비비고 김말이 500g, 꼬치어묵"},
        },
        "금요일": {
            "아침": {"dish": "조식 & 새벽 큐티", "memo": "전날 저녁 방으로 미리 배달 (목/금/토 3일 공용)", "time": "07:00",
                     "owner": "", "ingredients": ""},
            "오전": {"dish": "노방전도", "memo": "공원 전체 행사 · 다과 지참", "time": "", "owner": "", "ingredients": ""},
            "점심": {"dish": "가정식 백반", "memo": "김치찌개+계란말이+제육볶음+기타반찬 (30인분)", "time": "", "owner": "현호",
                     "ingredients": "제육용 고기 6kg, 찌개용 고기 2kg, 김치 5kg, 두부 3모, 계란 30개, 제육양념 1통"},
            "저녁": {"dish": "외식 (식당)", "memo": "외식 및 카페 (개인 부담)", "time": "", "owner": "", "ingredients": ""},
        },
        "토요일": {
            "아침": {"dish": "조식 & 새벽 큐티", "memo": "숙소 비품 및 잔여 식자재 활용 (목/금/토 3일 공용)", "time": "07:00",
                     "owner": "", "ingredients": ""},
            "점심": {"dish": "외식 (식당)", "memo": "장소·메뉴 선정 · 식사 후 행사 마무리 (개인 부담)", "time": "", "owner": "", "ingredients": ""},
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

# ─────────────────────── 일정 타임라인 (26년 통영TT 최종 타임 테이블) ───────────────────────
# (시간, 설명, 이 시간에 해당하는 식사종류 — 있으면 타임라인에 메뉴가 같이 표시됨)
DAY_SCHEDULE = {
    "수요일": [
        ("06:00–08:00", "/////", None),
        ("08:00–13:00", "8:30분 종합운동장 2번출구 출발 · 휴게소 점심식사 · 14:00 교회도착", None),
        ("14:00–17:00", "도착예배/OT · 예배/데코: 홍보 및 행사안내 부착 · 식사: 식사준비", None),
        ("18:00", "저녁식사", "저녁"),
        ("19:00–21:00", "큐티콘서트 1일차 (19:30-21:30)", None),
        ("22:00–23:00", "피드백 나눔", None),
        ("0:00", "교회이동 및 취침", None),
    ],
    "목요일": [
        ("06:00–08:00", "1. 아침식사(~08:00까지) · 2. ZOOM큐티(07:00시작/해당자만) · 3. 교회로 9시까지 출발", "아침"),
        ("09:00", "아침큐티(교회)", None),
        ("10:00–11:00", "오전사역 · 팀별사역준비", None),
        ("12:00", "점심식사", "점심"),
        ("13:00–17:00", "예배/데코: 오이소사역 · 식사: 식사 준비", None),
        ("18:00", "저녁식사", "저녁"),
        ("19:00–21:00", "큐티콘서트 2일차 (19:30-21:30)", None),
        ("22:00–23:00", "피드백나눔", None),
        ("0:00", "교회이동 및 취침", None),
    ],
    "금요일": [
        ("06:00–08:00", "1. 아침식사(~08:00까지) · 2. ZOOM큐티(07:00시작/해당자만) · 3. 교회로 9시까지 출발", "아침"),
        ("09:00", "아침큐티(교회)", None),
        ("10:00–11:00", "예배: 노방전도 · 데코: 사랑방/교회데코 · 식사: 식사준비", "오전"),
        ("12:00", "점심식사", "점심"),
        ("13:00–17:00", "동피랑마을 및 시장탐방 · 바닷가 구경", None),
        ("18:00", "저녁식사(외식)", "저녁"),
        ("19:00–21:00", "카페 피드백나눔", None),
        ("22:00–23:00", "미비된 활동 정리", None),
        ("0:00", "교회이동 및 취침", None),
    ],
    "토요일": [
        ("06:00–07:00", "1. 아침식사(~08:00까지) · 2. 교회로 8:30까지 짐 다들고 교회로 이동", "아침"),
        ("09:00", "8:30-9:30 아침큐티", None),
        ("10:00–12:00", "통영요트투어", None),
        ("13:00", "점심식사", "점심"),
        ("14:00–21:00", "서울로이동 · 19:00경 종합운동장 하차예정", None),
        ("22:00–23:00", "///", None),
    ],
}

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
    drink = find_drink_form(day_label)
    drink_icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M17 9h2a2 2 0 0 1 0 4h-2"/></svg>'
    drink_badge = ""
    if day_label == "수요일":
        drink_badge = f'''<span class="drink-badge drink-badge-disabled">
      {drink_icon}
      커피 주문은 내일 아침부터
    </span>'''
    elif drink:
        drink_badge = f'''<a class="drink-badge" style="--c:var({color_var})" href="{drink['form_url']}" target="_blank">
      {drink_icon}
      커피 주문
    </a>'''
    tl_rows = ""
    used_meals = set()
    for t, text, meal_key in DAY_SCHEDULE.get(day_label, []):
        meal_tag = ""
        if meal_key and meal_key in meals:
            info = meals[meal_key]
            dish = info.get("dish", "").strip()
            if dish:
                owner_val = info.get("owner", "").strip()
                owner_txt = f' · 담당 {esc(owner_val)}' if owner_val else ""
                meal_tag = f'<div class="tl-meal">{esc(meal_key)}: {esc(dish)}{owner_txt}</div>'
                used_meals.add(meal_key)
        tl_rows += f'''<div class="tl-item">
      <div class="tl-time">{esc(t)}</div>
      <div class="tl-text">{esc(text)}</div>
      {meal_tag}
    </div>'''
    timeline_block = f"""
<div class="tl-wrap" style="--c:var({color_var})">
  <div class="tl-title">일정</div>
  <div class="timeline">{tl_rows}</div>
</div>""" if tl_rows else ""

    cards = ""
    for mt in MEAL_ORDER:
        if mt not in meals or mt in used_meals:
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

    shop_rows = ""
    for mt in MEAL_ORDER:
        if mt not in meals:
            continue
        ing_val = meals[mt].get("ingredients", "").strip()
        if ing_val:
            dish_val = meals[mt].get("dish", "").strip()
            label = f"{mt}: {dish_val}" if dish_val else mt
            shop_rows += f'<li><b>{esc(label)}</b>{esc(ing_val)}</li>'
    if shop_rows:
        shopping_box = f"""
<div class="shopbox" style="--c:var({color_var})">
  <div class="shop-title">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6h15l-1.5 9h-12z"/><path d="M6 6 5 3H2"/><circle cx="9" cy="20" r="1.4"/><circle cx="17" cy="20" r="1.4"/></svg>
    오늘 장보기
  </div>
  <ul class="shop-list">{shop_rows}</ul>
</div>"""
    else:
        shopping_box = f"""
<div class="shopbox shopbox-empty" style="--c:var({color_var})">
  <div class="shop-title">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6h15l-1.5 9h-12z"/><path d="M6 6 5 3H2"/><circle cx="9" cy="20" r="1.4"/><circle cx="17" cy="20" r="1.4"/></svg>
    오늘 장보기
  </div>
  <div class="shop-empty-msg">아직 등록된 준비재료가 없어요</div>
</div>"""

    return f"""<section id="page-{day_id}" class="page-sec" style="--c:var({color_var})">
  {DAY_TAB_HTML}
  <div class="page">
    <div class="dayhead">
      <div class="dayhead-row"><div class="dt">{day_label}</div>{drink_badge}</div>
      <div class="ds">{subtitle}</div>
    </div>
    {shopping_box}
    {timeline_block}
    {cards}
    <div class="foot">통영 물댄동산교회 위드공동체 · 2026 여름 아웃리치</div>
  </div>
</section>"""

# ─────────────────────── 메인 HTML 빌드 ───────────────────────
def build_extra_section(extra_data):
    """기타사항 섹션 HTML을 동적으로 생성합니다."""
    CATEGORY_ORDER = ["아침 공통 메뉴", "공용 식재료", "상시 간식", "밥 담당", "준비물"]
    all_categories = CATEGORY_ORDER + [c for c in extra_data if c not in CATEGORY_ORDER]

    sections_html = ""
    for category in all_categories:
        if category not in extra_data:
            continue
        items = extra_data[category]
        rows = ""
        for content, note, owner in items:
            tags = f'<span class="info-tag">{esc(note)}</span>' if note else ""
            if owner:
                tags += f'<span class="info-tag" style="background:var(--primary);color:#fff">담당 · {esc(owner)}</span>'
            rows += f"<li>{tags}{esc(content)}</li>"
        sections_html += f"""
    <div class="info-section">
      <h3>{esc(category)}</h3>
      <ul class="info-list">{rows}</ul>
    </div>"""

    return f"""<section id="page-extra" class="page-sec" style="--c:#7c6fe8">
  {DAY_TAB_HTML}
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
    poster   = b64("assets/poster.png",   "image/png")
    team     = b64("assets/team.jpg",     "image/jpeg")
    schedule = b64("assets/schedule.png", "image/png")

    wed_html = build_day_section("wed", "수요일", "하루를 열며 차분히 시작해요.",          "--wed", meal_data.get("수요일", {}))
    thu_html = build_day_section("thu", "목요일", "메인 사역일 — 든든하게 채워요.",        "--thu", meal_data.get("목요일", {}))
    fri_html = build_day_section("fri", "금요일", "일정을 확인하고 은혜로운 하루 보내세요.", "--fri", meal_data.get("금요일", {}))
    sat_html = build_day_section("sat", "토요일", "잘 마무리하고 평안히 돌아가요.",        "--sat", meal_data.get("토요일", {}))

    data_sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit"

    sheet_btn = f"""
<div style="display:flex;gap:10px;padding:14px 20px 0">
  <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:6px">
    <a href="{sheet_url}" target="_blank"
       style="display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;gap:6px;
              background:#4e6448;color:#fff;border-radius:999px;padding:9px 14px;font-size:12.5px;font-weight:700;
              text-decoration:none;box-shadow:0 4px 14px rgba(78,100,72,.3);width:100%">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
      식사팀 시트
    </a>
    <div style="font-size:10.5px;color:#8a6416;text-align:center;line-height:1.4">수정해도 앱엔<br>반영 안 돼요</div>
  </div>
  <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:6px">
    <a href="{data_sheet_url}" target="_blank"
       style="display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;gap:6px;
              background:#fff;color:var(--ink-soft);border:1.5px solid var(--line);border-radius:999px;
              padding:9px 14px;font-size:12.5px;font-weight:700;text-decoration:none;
              -webkit-tap-highlight-color:transparent;width:100%">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="flex:none">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
      앱 데이터 시트 수정
    </a>
    <div style="font-size:10.5px;color:#4e6448;text-align:center;line-height:1.4">수정 후 최대 1분 내<br>자동 반영돼요</div>
  </div>
</div>
<div style="text-align:center;padding:20px 20px 4px">
  <div style="display:inline-block;background:#fff;border-radius:14px;padding:12px;
              box-shadow:0 4px 20px rgba(27,28,28,.07);border:1px solid var(--line)">
    <a href="https://ttmeal.streamlit.app" target="_blank" style="display:block;text-decoration:none;-webkit-tap-highlight-color:transparent;cursor:pointer">
      <img
        src="https://api.qrserver.com/v1/create-qr-code/?size=110x110&margin=6&data=https://ttmeal.streamlit.app"
        alt="앱 QR코드"
        style="width:110px;height:110px;display:block;border-radius:6px;margin:0 auto"
      >
    </a>
    <div style="margin-top:8px;font-size:12px;font-weight:800;color:var(--ink);
                display:flex;align-items:center;justify-content:center;gap:5px">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--primary)"
           stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="5" y="2" width="14" height="20" rx="2"/>
        <path d="M12 18h.01"/>
      </svg>
      식사팀 가이드 앱
    </div>
    <div style="font-size:10.5px;color:var(--muted);margin-top:3px">카메라로 찍으면 바로 접속돼요</div>
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
.hero{{position:relative;border-radius:var(--r-xl);overflow:hidden;box-shadow:0 8px 30px rgba(78,100,72,.16);margin-bottom:10px}}
.hero img{{display:block;width:100%}}
#hero-poster{{cursor:zoom-in;-webkit-user-drag:none;-webkit-touch-callout:none;
  -webkit-tap-highlight-color:transparent;user-select:none}}
.hero-hint{{position:absolute;left:50%;bottom:14px;transform:translateX(-50%);
  background:rgba(27,28,28,.62);color:#fff;font-size:11.5px;font-weight:700;
  padding:6px 14px;border-radius:999px;display:flex;align-items:center;gap:5px;
  cursor:pointer;-webkit-tap-highlight-color:transparent}}
.sched-bar{{display:flex;align-items:center;justify-content:space-between;gap:8px;
  background:var(--primary);color:#fff;padding:10px 14px;font-size:12px;font-weight:800}}
.sched-close{{background:rgba(255,255,255,.2);border-radius:999px;padding:4px 10px;
  font-size:11px;font-weight:700;cursor:pointer;white-space:nowrap;-webkit-tap-highlight-color:transparent}}
.sched-viewport{{position:relative;overflow:hidden;touch-action:none;background:#fff;aspect-ratio:788/722}}
.sched-viewport img{{position:absolute;top:0;left:0;width:100%;transform-origin:0 0;
  -webkit-user-select:none;user-select:none;-webkit-user-drag:none;pointer-events:none}}
.sched-hint{{text-align:center;font-size:10.5px;color:var(--muted);padding:6px 0;background:#fff}}
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
.dayhead-row{{display:flex;align-items:center;justify-content:center;gap:8px}}
.dayhead .dt{{font-size:36px;font-weight:900;color:var(--c);letter-spacing:-.02em}}
.dayhead .ds{{font-size:14px;color:var(--muted);margin-top:4px}}
.drink-badge{{display:inline-flex;align-items:center;gap:4px;font-size:12px;font-weight:800;
  color:#fff;background:var(--c);border-radius:999px;box-shadow:0 3px 10px rgba(27,28,28,.18);
  padding:5px 12px;text-decoration:none;white-space:nowrap;-webkit-tap-highlight-color:transparent}}
.drink-badge-disabled{{color:var(--muted);background:var(--card-low);box-shadow:none;
  border:1px solid var(--line);cursor:default}}

/* 오늘 장보기 */
.shopbox{{background:var(--card);border-radius:var(--r-xl);padding:16px 18px;margin-bottom:16px;
  border:1px solid var(--line);border-top:5px solid var(--c);box-shadow:0 6px 22px rgba(27,28,28,.06)}}
.shop-title{{display:flex;align-items:center;gap:7px;font-size:15px;font-weight:800;color:var(--c);
  margin-bottom:10px}}
.shop-list{{list-style:none;margin:0;padding:0}}
.shop-list li{{font-size:13px;color:var(--ink-soft);line-height:1.6;padding:7px 0;
  border-bottom:1px solid var(--line)}}
.shop-list li:last-child{{border-bottom:none;padding-bottom:0}}
.shop-list li b{{display:block;font-size:12px;font-weight:800;color:var(--ink);margin-bottom:1px}}
.shopbox-empty .shop-empty-msg{{font-size:12.5px;color:var(--muted);font-style:italic}}

/* 일정 타임라인 */
.tl-wrap{{background:var(--card);border-radius:var(--r-xl);padding:16px 18px;margin-bottom:16px;
  border:1px solid var(--line);box-shadow:0 6px 22px rgba(27,28,28,.06)}}
.tl-title{{font-size:15px;font-weight:800;color:var(--ink);margin-bottom:12px}}
.timeline{{position:relative;padding-left:16px}}
.timeline::before{{content:'';position:absolute;left:3px;top:5px;bottom:5px;width:2px;background:var(--line)}}
.tl-item{{position:relative;padding-bottom:14px}}
.tl-item:last-child{{padding-bottom:0}}
.tl-item::before{{content:'';position:absolute;left:-16px;top:3px;width:8px;height:8px;
  border-radius:50%;background:var(--c);box-shadow:0 0 0 2px var(--card)}}
.tl-time{{font-size:11.5px;font-weight:800;color:var(--c)}}
.tl-text{{font-size:13px;color:var(--ink-soft);line-height:1.5;margin-top:2px}}
.tl-meal{{display:inline-block;margin-top:6px;font-size:12px;font-weight:800;color:var(--c);
  background:var(--card-low);border-radius:999px;padding:4px 11px}}

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

    <div class="hero">
      <img id="hero-poster" src="{poster}" alt="2026 통영 아웃리치 포스터" onclick="showSchedule()" draggable="false">
      <div id="hero-hint" class="hero-hint" onclick="showSchedule()">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="16" rx="2.5"/><path d="M4 9h16M9 3v3M15 3v3"/></svg>
        눌러서 일정표 보기
      </div>
      <div id="hero-schedule-wrap" style="display:none">
        <div class="sched-bar">
          <span>26년 통영 TT 최종 타임 테이블</span>
          <span class="sched-close" onclick="hideSchedule()">✕ 포스터로</span>
        </div>
        <div id="sched-viewport" class="sched-viewport">
          <img id="sched-img" src="{schedule}" alt="26년 통영 TT 최종 타임 테이블">
        </div>
        <div class="sched-hint">두 손가락으로 확대·축소, 한 손가락으로 이동</div>
      </div>
    </div>

    <div class="tile-wide" onclick="show('team','people')">
      <span class="ti"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="8.5" r="2.4"/><path d="M16 14.2A4.6 4.6 0 0 1 20.5 19"/></svg></span>
      <span class="tl">팀 소개 &amp; 기도제목</span>
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
var DAY_COLOR = {{wed:'var(--wed)',thu:'var(--thu)',fri:'var(--fri)',sat:'var(--sat)',extra:'#7c6fe8'}};

var schedState = {{scale:1, tx:0, ty:0}};

function schedApply(){{
  var img = document.getElementById('sched-img');
  if(img) img.style.transform = 'translate('+schedState.tx+'px,'+schedState.ty+'px) scale('+schedState.scale+')';
}}

function schedDist(a,b){{
  return Math.hypot(a.x-b.x, a.y-b.y);
}}

(function(){{
  var vp = document.getElementById('sched-viewport');
  if(!vp) return;
  var startDist=0, startScale=1, dragging=false, lastX=0, lastY=0;

  vp.addEventListener('touchstart', function(e){{
    if(e.touches.length===2){{
      dragging=false;
      var a={{x:e.touches[0].clientX,y:e.touches[0].clientY}};
      var b={{x:e.touches[1].clientX,y:e.touches[1].clientY}};
      startDist = schedDist(a,b);
      startScale = schedState.scale;
    }} else if(e.touches.length===1){{
      dragging=true;
      lastX=e.touches[0].clientX; lastY=e.touches[0].clientY;
    }}
  }}, {{passive:true}});

  vp.addEventListener('touchmove', function(e){{
    if(e.touches.length===2){{
      e.preventDefault();
      var a={{x:e.touches[0].clientX,y:e.touches[0].clientY}};
      var b={{x:e.touches[1].clientX,y:e.touches[1].clientY}};
      var d = schedDist(a,b);
      schedState.scale = Math.min(4, Math.max(1, startScale * (d/startDist)));
      if(schedState.scale<=1){{ schedState.tx=0; schedState.ty=0; }}
      schedApply();
    }} else if(e.touches.length===1 && dragging && schedState.scale>1){{
      e.preventDefault();
      var dx = e.touches[0].clientX - lastX;
      var dy = e.touches[0].clientY - lastY;
      lastX = e.touches[0].clientX; lastY = e.touches[0].clientY;
      schedState.tx += dx; schedState.ty += dy;
      schedApply();
    }}
  }}, {{passive:false}});

  vp.addEventListener('touchend', function(e){{
    if(e.touches.length===0) dragging=false;
  }});
}})();

function showSchedule(){{
  document.getElementById('hero-poster').style.display = 'none';
  document.getElementById('hero-hint').style.display = 'none';
  document.getElementById('hero-schedule-wrap').style.display = 'block';
}}
function hideSchedule(){{
  schedState = {{scale:1, tx:0, ty:0}};
  schedApply();
  document.getElementById('hero-schedule-wrap').style.display = 'none';
  document.getElementById('hero-poster').style.display = 'block';
  document.getElementById('hero-hint').style.display = 'flex';
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
    sheet_url = f"https://docs.google.com/spreadsheets/d/{TEAM_LEADER_SHEET_ID}/edit"
    html = build_html(meal_data, sheet_url, extra_data)
    components.html(html, height=900, scrolling=True)

if __name__ == "__main__":
    main()
