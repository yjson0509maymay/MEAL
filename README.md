# 통영 아웃리치 식사팀 가이드

2026 여름 통영 아웃리치 식사팀을 위한 모바일 안내 사이트입니다.
요일별 식단·일정, 팀 소개, 기도제목, 후원계좌를 한눈에 볼 수 있습니다.

스티치(Stitch)의 **Sacred Table 디자인 시스템**을 그대로 구현한 정적 사이트라
별도 서버나 백엔드 없이 GitHub Pages로 바로 배포됩니다.

## 구성

| 파일 | 화면 |
|---|---|
| `index.html` | 홈(표지 + 요일 버튼 + 팀 버튼) |
| `wed.html` / `thu.html` / `fri.html` / `sat.html` | 요일별 일정·식단 |
| `team.html` | 단체사진 + 기도제목 + 후원계좌 |
| `assets/style.css` | 디자인 시스템(색·폰트·카드) |
| `assets/poster.png`, `assets/team.jpg` | 포스터·단체사진 |
| `build_app.py` | 페이지 자동 생성 스크립트(내용 수정용) |

## 배포 (GitHub Pages)

```bash
git clone https://github.com/yjson0509maymay/MEAL.git
# 이 폴더의 파일을 전부 복사해 넣은 뒤
git add .
git commit -m "식사팀 가이드 사이트"
git push
```

그다음 GitHub 저장소에서:
1. **Settings → Pages**
2. **Source: Deploy from a branch**
3. **Branch: main / (root)** 선택 후 Save
4. 잠시 후 `https://yjson0509maymay.github.io/MEAL/` 에서 열립니다.

## 내용 수정

- **간단 수정:** 각 `.html` 파일의 글자를 직접 고쳐도 됩니다.
- **자동 생성:** `build_app.py` 안의 `DAYS` 데이터를 고치고
  `python3 build_app.py` 를 실행하면 모든 페이지가 다시 생성됩니다.

## 음식 사진 추가하기

지금은 메뉴를 아이콘(일러스트)으로 표시합니다. 실제 사진을 넣고 싶다면
`assets/` 에 사진을 넣고(파일명은 서로 다르게!) 해당 요일 카드에 이미지를
추가하면 됩니다. 필요하면 도와드릴게요.

---

## (대안) Streamlit Community Cloud 배포

스트림릿으로 띄우려면 아래 파일이 저장소에 있어야 합니다(이미 포함됨):
`streamlit_app.py`, `app_embedded.html`, `requirements.txt`, `assets/`.

배포 화면 입력값:
- **Repository:** `yjson0509maymay/MEAL`
- **Branch:** `main`  ← `master` 아님! (GitHub 저장소 상단 브랜치 드롭다운에서 실제 이름 확인)
- **Main file path:** `streamlit_app.py`
- **App URL:** 원하는 주소(예: 잡아둔 도메인 그대로)

> 푸시가 끝난 뒤에야 폼의 빨간 오류가 사라집니다(파일이 저장소에 있어야 인식).
> 앱 높이를 바꾸려면 `streamlit_app.py`의 `height=880` 숫자만 조절하세요.
