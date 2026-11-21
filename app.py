# -*- coding: utf-8 -*-
"""내 안에 숨어 있는 동물은? — 한 파일로 실행하는 동물 성격 테스트.

설치: python -m pip install "streamlit>=1.58"
실행: python -m streamlit run app.py

Streamlit 외에 직접 설치할 패키지나 별도 이미지 파일은 없습니다.
아래의 P는 '계획형', F는 '즉흥형'이며 실제 MBTI의 약자와는 다릅니다.
"""

from itertools import product

import streamlit as st


# 웹앱 접속 비밀번호 확인
if "password_ok" not in st.session_state:
    st.session_state.password_ok = False

if not st.session_state.password_ok:
    st.title("🐾 내 안에 숨어 있는 동물은?")

    password = st.text_input(
        "접속 비밀번호를 입력해주세요.",
        type="password"
    )

    if st.button("입장하기"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.password_ok = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")

    st.stop()

# 1. 성향 정의: 양수이면 앞 글자, 음수이면 뒤 글자에 가까운 답변입니다.
# 질문 수가 다른 성향을 비교할 때는 합계 대신 평균(-2~+2)을 사용합니다.
DIMENSIONS = {
    "social": {"name": "사회적 성향", "letters": ("E", "I"),
               "labels": ("외향형", "내향형")},
    "action": {"name": "행동 방식", "letters": ("P", "F"),
               "labels": ("계획형", "즉흥형")},
    "judgment": {"name": "판단 방식", "letters": ("L", "M"),
                 "labels": ("이성형", "감성형")},
    "lifestyle": {"name": "생활 성향", "letters": ("S", "A"),
                  "labels": ("안정형", "모험형")},
}


# 2. 질문 데이터: 각 선택지는 (화면에 표시할 문장, 점수)로 구성합니다.
# +2: 앞 성향이 강함, +1: 앞 성향에 조금 가까움
# -1: 뒤 성향에 조금 가까움, -2: 뒤 성향이 강함
# 선택지 순서를 섞어 항상 첫 번째 답변만 고르는 경향을 줄였습니다.
# 한 질문은 한 성향에만 점수를 주므로 네 성향을 독립적으로 조합할 수 있습니다.
QUESTIONS = [
    {"dimension": "social", "emoji": "🎉", "title": "친구의 생일 모임에 도착했어요.",
     "scene": "아는 사람은 생일인 친구 한 명뿐! 케이크 옆에 선 나는?",
     "options": [
         ("옆 사람에게 먼저 말을 걸어요. '친구랑 어떻게 알게 됐어요?'", 2),
         ("익숙한 친구 옆에 있다가, 말을 걸어 주면 편하게 대화해요.", -1),
         ("주변 대화를 듣다가 공감되는 이야기가 나오면 슬쩍 끼어요.", 1),
         ("조용한 자리에 앉아 구경해요. 새로운 사람과 대화는 천천히!", -2),
     ]},
    {"dimension": "action", "emoji": "🧳", "title": "다음 주말에 짧은 여행을 가기로 했어요.",
     "scene": "숙소는 예약 완료! 이제 여행 일정을 정할 시간이에요.",
     "options": [
         ("도착해서 끌리는 곳으로 가요. 길을 잃어도 그것도 여행!", -2),
         ("이동 시간까지 넣어서 일정을 짜요. 지도에 저장도 완료!", 2),
         ("큰 일정만 정하고, 카페나 식당은 그날 기분에 맡겨요.", 1),
         ("가고 싶은 곳 몇 개만 저장해요. 순서는 현장에서 생각해요.", -1),
     ]},
    {"dimension": "judgment", "emoji": "☕", "title": "친구가 카페 아르바이트에서 실수했대요.",
     "scene": "'오늘 주문을 잘못 받아서 너무 속상해...'라는 메시지가 왔어요.",
     "options": [
         ("'많이 당황했겠다.' 먼저 마음을 달래 주고 이야기를 들어요.", -2),
         ("어디서 헷갈렸는지 물어보고, 다음에 쓸 확인 방법을 같이 찾아요.", 2),
         ("상황을 차근차근 물어보고, 실수를 줄일 방법을 제안해요.", 1),
         ("속상한 마음을 들어 준 다음, 친구가 원하면 해결책도 생각해요.", -1),
     ]},
    {"dimension": "lifestyle", "emoji": "🍜", "title": "점심을 먹으러 식당가에 왔어요.",
     "scene": "늘 가던 맛집 옆에 처음 보는 나라의 음식점이 생겼네요!",
     "options": [
         ("익숙한 맛집에 가되, 안 먹어 본 사이드 메뉴를 하나 시켜요.", 1),
         ("처음 보는 음식점으로 직진! 낯선 메뉴도 일단 도전해요.", -2),
         ("메뉴와 후기를 조금 살펴보고, 새 음식점에 들어가 봐요.", -1),
         ("오늘도 늘 먹던 메뉴요. 검증된 한 끼가 가장 든든해요.", 2),
     ]},
    {"dimension": "social", "emoji": "🔋", "title": "정신없이 바빴던 한 주가 끝났어요.",
     "scene": "드디어 금요일 저녁! 에너지가 바닥난 나의 충전 방법은?",
     "options": [
         ("혼자 좋아하는 영상을 보며 쉬어요. 오늘은 연락도 잠시 조용히!", -2),
         ("친구들을 불러 모아요. 만나서 수다 떨면 기운이 돌아와요.", 2),
         ("먼저 혼자 쉬고, 여유가 생기면 친한 친구에게 연락해요.", -1),
         ("가까운 친구와 밥 먹으며 일주일 이야기를 나눠요.", 1),
     ]},
    {"dimension": "action", "emoji": "🛒", "title": "마트에서 일주일치 장을 보려고 해요.",
     "scene": "카트를 잡는 순간, 할인 안내 방송이 들려옵니다!",
     "options": [
         ("필요한 품목은 정해 뒀어요. 할인 상품은 예산 안에서 추가해요.", 1),
         ("일단 둘러봐요. 오늘 먹고 싶은 걸 발견하면 메뉴를 정해요.", -2),
         ("식단과 수량을 적은 목록을 확인하며 순서대로 담아요.", 2),
         ("꼭 필요한 것 두어 개만 기억하고 나머지는 보면서 골라요.", -1),
     ]},
    {"dimension": "judgment", "emoji": "🎬", "title": "친구들과 주말에 볼 영화를 고르고 있어요.",
     "scene": "후기가 좋은 영화와 친구가 정말 보고 싶어 하는 영화가 달라요.",
     "options": [
         ("평점과 상영 시간을 먼저 비교하고, 친구 의견도 들어 봐요.", 1),
         ("친구가 기대하는 마음이 우선! 그 영화를 함께 보자고 해요.", -2),
         ("모두에게 편한 시간과 후기 등을 표로 비교해 가장 나은 걸 골라요.", 2),
         ("누가 어떤 영화를 왜 보고 싶은지 듣고, 마음이 가는 쪽을 골라요.", -1),
     ]},
    {"dimension": "lifestyle", "emoji": "🎨", "title": "주말에 취미 수업을 하나 들어 보려고 해요.",
     "scene": "익숙한 취미 수업과 완전히 낯선 체험 수업이 동시에 열렸어요.",
     "options": [
         ("해 본 적 없는 체험을 골라요. 조금 낯설어야 더 설레죠!", -2),
         ("즐거울 걸 아는 익숙한 취미요. 편하게 몰입하고 싶어요.", 2),
         ("익숙한 취미에서 새로운 기법을 배우는 수업을 골라요.", 1),
         ("처음 해 보는 체험의 입문반을 골라 가볍게 도전해요.", -1),
     ]},
    {"dimension": "social", "emoji": "📚", "title": "새로운 독서 모임에 처음 참여했어요.",
     "scene": "진행자가 '이 책 읽고 어떤 생각이 드셨어요?'라고 묻네요.",
     "options": [
         ("다른 사람 이야기를 들으며 생각을 정리한 뒤, 질문받으면 말해요.", -1),
         ("제가 먼저 말해 볼게요! 감상을 나누며 대화를 시작해요.", 2),
         ("오늘은 주로 듣고, 떠오른 생각은 혼자 메모해 둬요.", -2),
         ("누군가 이야기를 꺼내면 제 감상도 자연스럽게 보태요.", 1),
     ]},
    {"dimension": "action", "emoji": "📝", "title": "2주 뒤 제출할 작은 과제가 생겼어요.",
     "scene": "아직 시간은 넉넉하지만, 언젠가는 시작해야 하겠죠?",
     "options": [
         ("아이디어가 떠오르는 날 바로 시작해요. 작업 순서는 그때그때!", -2),
         ("마감 전 중간 목표를 정해 두고, 세부 순서는 유연하게 바꿔요.", 1),
         ("생각나는 부분부터 해요. 일정은 진행 상황을 보면서 맞춰요.", -1),
         ("오늘 할 일부터 제출 전 점검까지 날짜별로 나눠 둬요.", 2),
     ]},
]


# 3. 16가지 동물 결과: 사용자가 제시한 유형 이름과 기본 설명을 유지합니다.
# 장점, 단점, 숨겨진 성격, 한마디는 재미있는 결과 화면을 위한 창작 설명입니다.
ANIMALS = {
    "EPLS": {
        "emoji": "🦁", "name": "타고난 리더 사자",
        "description": "자신감이 넘치고 계획적으로 행동하며, 어려운 상황에서도 적극적으로 문제를 해결하는 유형",
        "strength": "해야 할 일을 정리하고 사람들을 이끌어요. 갑작스러운 문제 앞에서도 중심을 잘 잡아요.",
        "weakness": "내가 세운 기준이 확실해서 다른 사람의 느린 속도를 답답하게 느낄 수 있어요.",
        "hidden": "씩씩해 보여도 '덕분에 잘됐어'라는 한마디를 오래 기억해요.",
        "quote": "일단 나만 따라와. 예약도, 일정표도 다 준비했어!",
    },
    "EPLA": {
        "emoji": "🐺", "name": "목표를 향해 달리는 늑대",
        "description": "목표가 뚜렷하고 새로운 도전을 즐기며, 계획을 세워 적극적으로 실행하는 유형",
        "strength": "도전할 목표를 찾으면 구체적인 계획으로 옮겨요. 함께하는 사람에게도 의욕을 나눠 줘요.",
        "weakness": "목표에 집중하다 보면 휴식 시간이나 주변 사람의 컨디션을 놓칠 수 있어요.",
        "hidden": "도전만 좋아하는 것 같아도, 함께 끝까지 가 줄 동료를 은근히 기다려요.",
        "quote": "새로운 길이네? 좋아, 지도부터 만들자!",
    },
    "EPMS": {
        "emoji": "🐧", "name": "다정한 약속 지킴이 펭귄",
        "description": "사람들과 어울리는 것을 좋아하고, 약속과 인간관계를 소중하게 생각하는 유형",
        "strength": "약속을 잘 지키고 작은 변화도 세심하게 알아봐요. 모임을 편안하게 만드는 재주가 있어요.",
        "weakness": "모두를 챙기다가 내 시간과 체력을 뒤로 미루기 쉬워요.",
        "hidden": "'나도 누가 챙겨 줬으면...' 하는 마음을 가끔 조용히 품고 있어요.",
        "quote": "우리 몇 시에 만나? 네가 좋아하는 간식도 챙길게!",
    },
    "EPMA": {
        "emoji": "🐬", "name": "공감하는 탐험가 돌고래",
        "description": "다른 사람의 감정을 잘 이해하고, 새로운 경험을 함께 즐기는 것을 좋아하는 유형",
        "strength": "새로운 활동을 준비하면서도 함께하는 사람의 마음을 살펴요. 낯선 곳에서도 좋은 분위기를 만들어요.",
        "weakness": "재미도 분위기도 모두 챙기려다가 혼자 바빠질 수 있어요.",
        "hidden": "함께 웃는 시간이 좋지만, 가끔은 아무도 챙기지 않고 쉬고 싶어요.",
        "quote": "처음 가는 곳인데 같이 갈래? 네 취향도 찾아봤어!",
    },
    "EFLS": {
        "emoji": "🦝", "name": "임기응변의 달인 너구리",
        "description": "상황에 빠르게 적응하고 현실적인 방법으로 문제를 해결하는 유형",
        "strength": "예상 밖의 상황에서도 지금 가능한 해결책을 빨리 찾아요. 사람들과 실용적인 아이디어를 잘 나눠요.",
        "weakness": "당장 해결하는 데 집중해서 장기적인 준비를 미룰 때가 있어요.",
        "hidden": "즉흥적으로 움직여도 마음속에는 실패 확률을 줄이는 나만의 기준이 있어요.",
        "quote": "괜찮아, 지금 있는 걸로 해결할 수 있어!",
    },
    "EFLA": {
        "emoji": "🦊", "name": "기회를 놓치지 않는 여우",
        "description": "눈치가 빠르고 호기심이 많으며, 새로운 기회를 발견하면 적극적으로 도전하는 유형",
        "strength": "변화를 빠르게 읽고 기회를 행동으로 연결해요. 막히면 다른 방법을 찾는 속도도 빨라요.",
        "weakness": "새로운 기회가 계속 보여서 시작한 일을 끝내기 전에 관심이 옮겨 갈 수 있어요.",
        "hidden": "가볍게 도전하는 듯해도 속으로는 이득과 가능성을 빠르게 계산해요.",
        "quote": "잠깐, 이거 재밌겠는데? 일단 해 보고 판단하자!",
    },
    "EFMS": {
        "emoji": "🐶", "name": "긍정 에너지 강아지",
        "description": "밝고 친근한 성격으로 주변 사람들에게 즐거움을 주고, 친밀한 관계를 중요하게 생각하는 유형",
        "strength": "상대가 편하게 다가오도록 분위기를 풀어 줘요. 소소한 일상에서도 함께 즐길 거리를 잘 찾아요.",
        "weakness": "거절하기 어려워서 피곤한 날에도 약속을 잡아 버릴 수 있어요.",
        "hidden": "항상 밝아 보여도 친한 사람의 무심한 말에 생각보다 오래 마음을 쓰곤 해요.",
        "quote": "너랑 있으면 편의점 앞도 우리만의 핫플이지!",
    },
    "EFMA": {
        "emoji": "🦦", "name": "호기심 넘치는 수달",
        "description": "새로운 사람과 경험을 좋아하고, 재미있는 일이 생기면 가장 먼저 참여하는 유형",
        "strength": "처음 만난 사람과도 금방 즐거움을 나눠요. 새로운 경험을 특별한 추억으로 만드는 힘이 있어요.",
        "weakness": "재미있는 제안을 다 받아들이다 보면 일정과 체력이 동시에 바빠져요.",
        "hidden": "웃긴 이야기 뒤에는 '우리 모두 즐거웠으면 좋겠다'는 마음이 있어요.",
        "quote": "저기 뭐 하는 거야? 모르겠지만 우리도 가 보자!",
    },
    "IPLS": {
        "emoji": "🦉", "name": "차분한 분석가 부엉이",
        "description": "혼자 깊이 생각하는 것을 좋아하고, 신중하게 계획을 세워 행동하는 유형",
        "strength": "정보를 꼼꼼하게 비교하고 차분히 판단해요. 맡은 일을 꾸준하고 안정적으로 마무리해요.",
        "weakness": "충분히 확인하고 싶어서 결정을 내리는 데 시간이 오래 걸릴 수 있어요.",
        "hidden": "조용한 얼굴 뒤에서 혼자만 아는 농담과 관찰 기록이 쌓이고 있어요.",
        "quote": "잠깐만, 비교표에 한 줄만 더 추가하고 결정할게.",
    },
    "IPLA": {
        "emoji": "🐿️", "name": "준비된 탐험가 다람쥐",
        "description": "새로운 것에 관심이 많지만 충분히 조사하고 준비한 뒤 도전하는 유형",
        "strength": "호기심과 준비성을 함께 갖췄어요. 낯선 도전도 자료를 모으고 연습하면서 현실로 만들어요.",
        "weakness": "준비가 완벽해야 시작할 수 있다고 느껴 좋은 기회를 늦게 잡을 수 있어요.",
        "hidden": "조심스러워 보여도 마음속 도전 목록은 생각보다 아주 길어요.",
        "quote": "모험 좋아해. 준비물 목록은 세 장이지만!",
    },
    "IPMS": {
        "emoji": "🐻", "name": "따뜻한 수호자 곰",
        "description": "조용하고 신중하지만 소중한 사람들을 세심하게 챙기고 책임감 있게 행동하는 유형",
        "strength": "작은 약속도 기억하고 가까운 사람에게 믿음을 줘요. 말보다 꾸준한 행동으로 마음을 표현해요.",
        "weakness": "내가 참으면 된다고 생각하며 속상한 마음을 쌓아 둘 수 있어요.",
        "hidden": "듬직한 모습 뒤에 혼자만의 포근한 공간과 귀여운 취향을 숨겨 두었어요.",
        "quote": "말은 안 했지만, 네가 좋아하는 건 기억하고 있었어.",
    },
    "IPMA": {
        "emoji": "🐰", "name": "섬세한 꿈꾸는 토끼",
        "description": "감수성이 풍부하고 새로운 경험을 꿈꾸며, 자신만의 속도로 차근차근 준비하는 유형",
        "strength": "새로운 경험에 의미를 담고 세심하게 준비해요. 작은 감정과 분위기를 잘 알아차려요.",
        "weakness": "생각과 걱정이 많아지면 첫걸음을 떼기 전에 지칠 수 있어요.",
        "hidden": "조용해 보여도 혼자 상상한 미래에는 이미 여러 번 여행을 다녀왔어요.",
        "quote": "아직 출발은 안 했는데, 여행 일기 첫 장은 써 놨어.",
    },
    "IFLS": {
        "emoji": "🐼", "name": "느긋한 관찰자 판다",
        "description": "조용하고 여유로운 생활을 좋아하며, 불필요한 일에는 에너지를 쓰지 않는 유형",
        "strength": "상황을 담담하게 보고 꼭 필요한 일에 힘을 써요. 복잡한 일도 단순하게 정리하는 편이에요.",
        "weakness": "급하지 않은 일은 계속 뒤로 미루거나 관심 없는 일에 반응이 적을 수 있어요.",
        "hidden": "아무 생각 없어 보여도 주변 상황은 이미 꽤 정확하게 파악하고 있어요.",
        "quote": "가만히 있는 게 아니라 에너지를 효율적으로 쓰는 중이야.",
    },
    "IFLA": {
        "emoji": "🐱", "name": "자유로운 독립가 고양이",
        "description": "혼자만의 시간을 좋아하고, 다른 사람의 시선보다 자신의 호기심과 판단을 따르는 유형",
        "strength": "스스로 판단하고 새로운 방법을 시험해요. 혼자서도 관심 있는 일을 깊이 파고들 수 있어요.",
        "weakness": "내 방식이 편해서 주변과 진행 상황을 공유하는 일을 잊을 수 있어요.",
        "hidden": "혼자가 좋지만 내 취향을 알아주는 사람에게는 은근히 자주 다가가요.",
        "quote": "어디 가냐고? 나도 아직 몰라. 궁금한 쪽으로 가는 중!",
    },
    "IFMS": {
        "emoji": "🦥", "name": "느긋한 힐링러 나무늘보",
        "description": "편안하고 평화로운 생활을 좋아하며, 자신의 속도에 맞춰 여유롭게 행동하는 유형",
        "strength": "주변 사람을 편안하게 해 주고 작은 행복을 잘 느껴요. 감정을 서두르지 않고 받아들여요.",
        "weakness": "불편한 대화나 변화를 미루다 보면 해결해야 할 일이 쌓일 수 있어요.",
        "hidden": "느긋해 보여도 좋아하는 사람의 기분 변화에는 누구보다 민감해요.",
        "quote": "급한 일 아니면, 차 한 잔 마시고 생각해 볼까?",
    },
    "IFMA": {
        "emoji": "🦋", "name": "자유로운 상상가 나비",
        "description": "상상력이 풍부하고 자유로운 분위기를 좋아하며, 새로운 경험에서 영감을 얻는 유형",
        "strength": "익숙한 풍경에서도 새로운 느낌과 아이디어를 찾아요. 내 마음에 맞는 방식으로 경험을 넓혀 가요.",
        "weakness": "기분과 영감에 따라 움직이다 보면 마무리나 시간 관리가 어려울 수 있어요.",
        "hidden": "자유로워 보여도 내 마음을 편하게 내려놓을 작은 보금자리를 소중히 여겨요.",
        "quote": "산책만 하려 했는데, 새 취미와 아이디어 세 개를 주워 왔어!",
    },
}


# 4. 점수 계산은 화면 코드와 분리해 답변과 결과의 연결을 확인하기 쉽게 합니다.
def is_valid_answer(answer):
    # 0번 선택지도 유효합니다. if answer처럼 쓰면 0을 미응답으로 오해합니다.
    return type(answer) is int and 0 <= answer < 4


def analyze_answers(answers):
    """모든 답변을 검증하고 (4글자 유형 코드, 성향별 분석)을 반환합니다."""
    if len(answers) != len(QUESTIONS) or not all(map(is_valid_answer, answers)):
        raise ValueError("10개 질문에 모두 답해야 동물 친구를 만날 수 있어요.")

    scores = {key: [] for key in DIMENSIONS}
    for question, answer in zip(QUESTIONS, answers):
        scores[question["dimension"]].append(question["options"][answer][1])

    code = ""
    analysis = {}
    for key, dimension in DIMENSIONS.items():
        values = scores[key]
        average = sum(values) / len(values)
        tied = sum(values) == 0

        # 동점이면 절댓값이 가장 큰 응답(가장 강한 선택)을 우선합니다.
        # 강도까지 같으면 먼저 등장한 질문의 응답을 우선합니다.
        # max는 동률일 때 처음 나온 값을 반환하므로 판정이 항상 일정합니다.
        deciding_score = max(values, key=abs) if tied else average
        winner_index = 0 if deciding_score > 0 else 1
        letter = dimension["letters"][winner_index]
        code += letter

        # 평균 -2~+2를 0~100의 경향 지수로 변환합니다.
        # 예: 평균 +2 -> 앞 성향 100, 평균 0 -> 양쪽 50, 평균 -2 -> 앞 성향 0.
        # 이것은 응답에 따른 표시용 지수이며 성격일 확률이나 진단 정확도가 아닙니다.
        left_percent = round((average + 2) / 4 * 100, 1)
        analysis[key] = {
            "average": average, "letter": letter,
            "label": dimension["labels"][winner_index], "tied": tied,
            "left_percent": left_percent, "right_percent": round(100 - left_percent, 1),
        }
    return code, analysis


def get_matches(code):
    """세 성향은 같고 한 성향은 다른 두 유형을 재미있는 짝꿍으로 제안합니다."""
    # 사회적 성향이 다른 짝꿍: 다른 성향은 같아 대화의 바탕이 비슷합니다.
    social_buddy = ("I" if code[0] == "E" else "E") + code[1:]
    # 생활 성향이 다른 짝꿍: 익숙함과 새로움 사이에서 서로 아이디어를 더합니다.
    lifestyle_buddy = code[:3] + ("A" if code[3] == "S" else "S")
    social_reason = (
        "당신이 대화의 문을 열면, 이 친구는 차분히 이야기를 받아 줘요. "
        "나머지 세 성향은 같아서 함께할 때 익숙한 구석도 많아요!"
        if code[0] == "E" else
        "이 친구가 대화의 문을 열어 주면, 당신은 편하게 이야기를 이어 가요. "
        "나머지 세 성향은 같아서 둘만의 리듬도 찾기 좋아요!"
    )
    lifestyle_reason = (
        "당신이 편안한 베이스캠프를 만들면, 이 친구는 새로운 코스를 가져와요. "
        "다른 세 성향은 같으니 도전의 속도도 함께 맞춰 봐요!"
        if code[3] == "S" else
        "당신이 새로운 코스를 찾으면, 이 친구는 든든한 베이스캠프가 되어 줘요. "
        "다른 세 성향은 같아서 모험 뒤에 쉴 방법도 잘 통할 거예요!"
    )
    return [(social_buddy, "대화의 짝꿍", social_reason),
            (lifestyle_buddy, "주말의 짝꿍", lifestyle_reason)]


def validate_data():
    """실행 시 질문 구성, 점수, 16종 결과 연결을 가볍게 검사합니다."""
    expected = {"social": 3, "action": 3, "judgment": 2, "lifestyle": 2}
    assert len(QUESTIONS) == 10, "질문은 10개여야 합니다."
    for key, count in expected.items():
        assert sum(q["dimension"] == key for q in QUESTIONS) == count
    for question in QUESTIONS:
        assert len(question["options"]) == 4
        assert sorted(option[1] for option in question["options"]) == [-2, -1, 1, 2]
    possible_codes = {"".join(parts) for parts in product("EI", "PF", "LM", "SA")}
    assert set(ANIMALS) == possible_codes, "16가지 유형이 모두 등록되어야 합니다."

    # 각 목표 유형에 대해 해당 방향의 가장 강한 답을 넣어 실제 결과를 확인합니다.
    # 한 질문이 한 성향만 측정하므로 이 검사는 모든 16종의 도달 가능성을 보장합니다.
    for target in possible_codes:
        desired_scores = {
            key: 2 if target[i] == dimension["letters"][0] else -2
            for i, (key, dimension) in enumerate(DIMENSIONS.items())
        }
        answers = [next(i for i, option in enumerate(q["options"])
                        if option[1] == desired_scores[q["dimension"]])
                   for q in QUESTIONS]
        assert analyze_answers(answers)[0] == target
        assert all(buddy in ANIMALS and buddy != target
                   for buddy, _, _ in get_matches(target))


# 5. 화면 상태: answers는 위젯 상태와 별도로 보관합니다.
# 한 질문씩 표시하면 숨겨진 라디오 위젯의 상태가 정리될 수 있으므로,
# answers에 저장된 선택지를 다시 불러와 이전 답변을 확실하게 복원합니다.
def initialize_state():
    defaults = {"page": "welcome", "question_index": 0,
                "answers": [None] * len(QUESTIONS)}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_answer(index, widget_key):
    answers = st.session_state.answers.copy()
    answers[index] = st.session_state[widget_key]
    st.session_state.answers = answers


def reset_test():
    # 재검사에서는 저장된 답변과 라디오 선택을 함께 지웁니다.
    for key in list(st.session_state):
        if key.startswith("answer_"):
            del st.session_state[key]
    st.session_state.answers = [None] * len(QUESTIONS)
    st.session_state.question_index = 0
    st.session_state.page = "welcome"


def apply_style():
    # 기본 위젯을 유지하고 배경, 버튼, 카드 색상만 파스텔톤으로 조정합니다.
    st.markdown("""
    <style>
    .stApp { background: #fff6fa; color: #493746; }
    .block-container { max-width: 800px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: #71485f !important; letter-spacing: -0.03em; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        border-color: #f1d9e5 !important; border-radius: 22px !important;
    }
    [data-testid="stRadio"] label {
        background: #fffafd; color: #493746; border-radius: 12px;
        padding: 0.5rem; margin-bottom: 0.3rem;
    }
    [data-testid="stRadio"] input { accent-color: #c14d80; }
    .stButton > button {
        border-radius: 14px; border: 1px solid #eac6d7;
        background: #fffafd; color: #63384f; min-height: 3rem;
    }
    .stButton > button[kind="primary"] {
        background: #b94778; border-color: #b94778; color: white;
    }
    .stButton > button:hover { border-color: #b94778; }
    [data-testid="stProgress"] [role="progressbar"] > div > div {
        background-color: #d9719f;
    }
    .hero { text-align: center; padding: 1.8rem 1rem; border-radius: 24px;
            background: linear-gradient(140deg, #ffe4ef, #eee8ff, #e7f5ef);
            margin-bottom: 1.1rem; }
    .hero h1 { font-size: clamp(1.9rem, 5vw, 2.7rem); margin: 0.5rem 0; }
    .hero h2 { font-size: clamp(1.6rem, 5vw, 2.2rem); }
    .animal { font-size: 6rem; line-height: 1.35; }
    .badge { display: inline-block; background: #ffffffcc; color: #69435a;
             padding: 0.4rem 1rem; border-radius: 99px; font-weight: 700; }
    .hero p { color: #604657; line-height: 1.8; }
    </style>
    """, unsafe_allow_html=True)


def show_rules():
    with st.expander("🔎 점수는 어떻게 계산하나요?"):
        st.write("사회적 성향 3문항, 행동 방식 3문항, 판단 방식 2문항, 생활 성향 2문항이에요.")
        st.write("각 선택지에 +2, +1, -1, -2 중 하나를 부여해요. "
                 "양수는 E, P, L, S, 음수는 I, F, M, A 방향이에요.")
        st.write("성향마다 질문 수가 달라서 해당 성향의 평균을 사용해요. "
                 "평균이 양수이면 앞 성향, 음수이면 뒤 성향으로 정해요.")
        st.write("평균이 0이면 가장 강하게 선택한 응답을 우선해요. "
                 "그 강도도 같으면 해당 성향에서 먼저 나온 질문의 응답을 따라요.")
        st.write("그래프는 평균(-2~+2)을 0~100으로 바꾼 경향 지수예요. "
                 "앞 성향 지수 = (평균 + 2) ÷ 4 × 100, 뒤 성향 지수 = 100 - 앞 성향 지수예요.")
        st.caption("이 테스트만의 분류 기준이에요. P는 계획형, F는 즉흥형으로 사용해요.")


def show_welcome():
    st.markdown("""
    <div class="hero">
        <div style="font-size: 3rem;">🐻 🦊 🐧 🐱</div>
        <span class="badge">10개의 질문으로 만나는 나의 동물 친구</span>
        <h1>내 안에 숨어 있는 동물은?</h1>
        <p>계획표를 챙기는 사자일까, 호기심을 따라가는 수달일까?<br>
        평소의 나와 가장 가까운 행동을 골라 주세요.</p>
    </div>
    """, unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("🐾 나를 알아보는 작은 산책")
        st.write("⏱️ 약 2~3분이면 끝나요.")
        st.write("💌 정답은 없어요. '이게 바로 나지!' 싶은 답을 골라 주세요.")
        st.write("↩️ 이전 질문으로 돌아가 답을 바꿀 수 있어요.")
        st.write("🎁 16가지 동물 중 나와 닮은 친구와 잘 맞는 짝꿍을 만나요.")
    if st.button("🐾 내 동물 찾으러 가기", key="start", type="primary", width="stretch"):
        st.session_state.page = "quiz"
        st.rerun()
    show_rules()
    st.caption("가볍게 즐기는 성격 놀이예요. 실제 MBTI 검사나 전문 심리 검사는 아니에요.")


def show_question():
    index = st.session_state.question_index
    question = QUESTIONS[index]
    answers = st.session_state.answers
    answered_count = sum(is_valid_answer(answer) for answer in answers)

    st.title("🐾 내 안의 동물을 찾는 중")
    st.progress(answered_count / len(QUESTIONS),
                text=f"응답 완료 {answered_count} / {len(QUESTIONS)} | {answered_count * 10}%")
    st.caption(f"현재 {index + 1}번째 질문이에요. 가장 가까운 행동 하나를 골라 주세요.")

    widget_key = f"answer_{index}"
    if widget_key not in st.session_state:
        st.session_state[widget_key] = answers[index]

    with st.container(border=True):
        st.subheader(f"{question['emoji']} Q{index + 1}. {question['title']}")
        st.write(question["scene"])
        st.radio(
            "이 상황에서 나는?", options=list(range(4)), index=None,
            format_func=lambda option: question["options"][option][0],
            key=widget_key, on_change=save_answer, args=(index, widget_key),
        )

    current_answered = is_valid_answer(st.session_state.answers[index])
    left, right = st.columns(2)
    with left:
        if st.button("← 이전 질문", key="previous", disabled=index == 0, width="stretch"):
            st.session_state.question_index -= 1
            st.rerun()
    with right:
        if index < len(QUESTIONS) - 1:
            if st.button("다음 질문 →", key="next", type="primary",
                         disabled=not current_answered, width="stretch"):
                st.session_state.question_index += 1
                st.rerun()
        else:
            all_answered = all(map(is_valid_answer, st.session_state.answers))
            if st.button("🎁 내 동물 확인하기", key="finish", type="primary",
                         disabled=not all_answered, width="stretch"):
                # 버튼 비활성화와 별개로, 실제 계산 함수에서도 완전 응답을 검증합니다.
                analyze_answers(st.session_state.answers)
                st.session_state.page = "result"
                st.rerun()
    if not current_answered:
        st.info("☝️ 답을 하나 골라 주시면 다음으로 이동할 수 있어요.")
    st.button("처음부터 다시 하기", key="restart_quiz", on_click=reset_test)


def show_chart(analysis):
    # Streamlit에 포함된 차트 기능을 사용하므로 추가 그래프 패키지가 필요 없습니다.
    # 성향별 한 줄에 두 막대를 쌓아서 합계가 항상 100이 되도록 표시합니다.
    rows = []
    for key, dimension in DIMENSIONS.items():
        labels = [f"{label}({letter})" for label, letter
                  in zip(dimension["labels"], dimension["letters"])]
        row_name = f"{labels[0]} ↔ {labels[1]}"
        for order, (label, value_key) in enumerate(zip(labels, ["left_percent", "right_percent"])):
            rows.append({"영역": row_name, "성향": label,
                         "방향": "앞 성향" if order == 0 else "뒤 성향",
                         "지수": analysis[key][value_key], "순서": order})

    st.vega_lite_chart(spec={
        "data": {"values": rows},
        "height": 250,
        "mark": {"type": "bar", "height": 28, "cornerRadius": 5},
        "encoding": {
            "y": {"field": "영역", "type": "nominal", "title": None,
                  "sort": list(dict.fromkeys(row["영역"] for row in rows)),
                  "axis": {"labelLimit": 210, "labelFontSize": 12}},
            "x": {"field": "지수", "type": "quantitative", "stack": "zero",
                  "title": "응답에 따른 경향 지수", "scale": {"domain": [0, 100]},
                  "axis": {"values": [0, 25, 50, 75, 100]}},
            "color": {"field": "방향", "type": "nominal",
                      "scale": {"domain": ["앞 성향", "뒤 성향"],
                                "range": ["#d96b9b", "#b4a6e5"]},
                      "legend": {"orient": "bottom", "title": None}},
            "order": {"field": "순서", "type": "quantitative", "sort": "ascending"},
            "tooltip": [{"field": "성향", "type": "nominal"},
                        {"field": "지수", "type": "quantitative", "format": ".1f"}],
        },
        "config": {"background": "#fff6fa", "view": {"stroke": None},
                   "axis": {"labelColor": "#604657", "titleColor": "#604657",
                            "gridColor": "#eedee7"}},
    }, width="stretch")

    # 모바일에서도 정확한 수치를 읽을 수 있도록 그래프 아래에 함께 적어 줍니다.
    for key, dimension in DIMENSIONS.items():
        result = analysis[key]
        left, right = dimension["labels"]
        st.write(f"**{dimension['name']}**: {left} {result['left_percent']:.1f}% / "
                 f"{right} {result['right_percent']:.1f}% → **{result['label']}({result['letter']})**")
        if result["tied"]:
            st.caption("양쪽이 50:50이에요. 가장 강한 응답을 우선하고, "
                       "강도도 같으면 먼저 답한 질문을 기준으로 유형을 정했어요.")
    st.caption("위 비율은 답변을 보기 쉽게 바꾼 경향 지수이며, 성격일 확률이나 검사 정확도를 뜻하지 않아요.")


def show_result():
    # 결과를 따로 고정 저장하지 않고 최신 답변에서 다시 계산합니다.
    # 결과 화면으로 잘못 이동했어도 미응답이 있으면 계산을 중단합니다.
    try:
        code, analysis = analyze_answers(st.session_state.answers)
    except ValueError:
        st.warning("아직 답하지 않은 질문이 있어요. 모든 질문을 마치면 결과를 볼 수 있어요.")
        if st.button("답하지 않은 질문으로 가기", key="resume"):
            st.session_state.question_index = next(
                (i for i, answer in enumerate(st.session_state.answers)
                 if not is_valid_answer(answer)), 0)
            st.session_state.page = "quiz"
            st.rerun()
        return

    animal = ANIMALS[code]
    trait_text = " + ".join(analysis[key]["label"] for key in DIMENSIONS)
    st.progress(1.0, text="10 / 10 응답 완료! 내 안의 동물을 찾았어요.")
    st.markdown(f"""
    <div class="hero">
        <span class="badge">내 안에 숨어 있던 동물은 {code}</span>
        <div class="animal">{animal['emoji']}</div>
        <h2>{animal['name']}</h2>
        <p>{trait_text}</p>
        <p>{animal['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("💌 나를 조금 더 들여다보면")
        st.markdown(f"**✨ 장점**  \n{animal['strength']}")
        st.markdown(f"**🌱 단점과 조심할 점**  \n{animal['weakness']}")
        st.markdown(f"**🫣 숨겨진 성격**  \n{animal['hidden']}")
        st.info(f"💬 나의 한마디: “{animal['quote']}”")

    with st.container(border=True):
        st.subheader("🎨 네 가지 성향 한눈에 보기")
        show_chart(analysis)

    st.subheader("🤝 나와 잘 맞는 동물 친구")
    for buddy_code, title, reason in get_matches(code):
        buddy = ANIMALS[buddy_code]
        with st.container(border=True):
            st.markdown(f"**{buddy['emoji']} {title}: {buddy['name']} ({buddy_code})**")
            st.write(reason)
    st.caption("짝꿍 추천은 성향의 공통점과 차이를 바탕으로 만든 재미있는 설정이에요.")

    left, right = st.columns(2)
    with left:
        if st.button("↩️ 답변 돌아보기", key="review", width="stretch"):
            st.session_state.question_index = 0
            st.session_state.page = "quiz"
            st.rerun()
    with right:
        st.button("🔄 다시 검사하기", key="retry", type="primary",
                  width="stretch", on_click=reset_test)

    with st.expander("📋 내가 고른 답변 확인하기"):
        for index, (question, answer) in enumerate(zip(QUESTIONS, st.session_state.answers)):
            st.markdown(f"**Q{index + 1}. {question['title']}**")
            st.write(question["options"][answer][0])
    show_rules()


def main():
    st.set_page_config(page_title="내 안에 숨어 있는 동물은?", page_icon="🐾", layout="centered")
    validate_data()
    initialize_state()
    apply_style()
    if st.session_state.page == "welcome":
        show_welcome()
    elif st.session_state.page == "quiz":
        show_question()
    else:
        show_result()
    st.divider()
    st.caption("🐾 오늘의 나와 닮은 동물 친구를 만나는 시간 | 재미로 즐기는 성격 테스트")


if __name__ == "__main__":
    main()
