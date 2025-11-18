"""
KBO 스카우팅 리포트 데모 - Streamlit 앱
"""

import streamlit as st

st.set_page_config(
    page_title="KBO 스카우팅 리포트",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메인 페이지
st.title("⚾ KBO 스카우팅 리포트 데모")

st.markdown("""
### 2021-2025 KBO 정규시즌 선수 분석 시스템

이 앱은 KBO 리그 선수들의 상세한 스카우팅 리포트를 제공합니다.

#### 주요 기능

- **타자 스카우팅 리포트**: 컨택, 파워, 선구안, 일관성, 클러치 등 7개 카테고리 분석
- **투수 스카우팅 리포트**: 제구력, 공격성, 효율성, 구위, 클러치 등 5개 카테고리 분석

#### 데이터 기간
- 2021년 ~ 2025년 정규시즌 데이터

#### 사용 방법
1. 왼쪽 사이드바에서 원하는 리포트 유형을 선택하세요
2. 시즌과 선수를 선택하면 상세 스카우팅 리포트가 표시됩니다

---

*이 앱은 데모 목적으로 제작되었습니다.*
""")

# 데이터 로드 상태 확인
from utils.data_loader import load_batter_kpi, load_pitcher_kpi

try:
    batter_df = load_batter_kpi()
    pitcher_df = load_pitcher_kpi()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("타자 데이터", f"{len(batter_df):,} rows")
    with col2:
        st.metric("투수 데이터", f"{len(pitcher_df):,} rows")
    with col3:
        st.metric("시즌 범위", "2021-2025")

except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
