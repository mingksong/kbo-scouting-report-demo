"""
타자 스카우팅 리포트 페이지 - 전체 기능 구현
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

# 상위 디렉토리 추가
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import (
    get_batter_list, get_batter_data, get_team_color, load_batter_kpi
)

st.set_page_config(
    page_title="타자 스카우팅 리포트",
    page_icon="🏏",
    layout="wide"
)

# 등급 관련 함수
def get_grade_color(grade):
    if pd.isna(grade):
        return "#6B7280"
    grade = float(grade)
    if grade >= 80:
        return "#9333EA"  # purple
    elif grade >= 70:
        return "#2563EB"  # blue
    elif grade >= 60:
        return "#16A34A"  # green
    elif grade >= 50:
        return "#CA8A04"  # yellow
    elif grade >= 40:
        return "#EA580C"  # orange
    else:
        return "#DC2626"  # red

def get_grade_label(grade):
    if pd.isna(grade):
        return "N/A"
    grade = float(grade)
    if grade >= 80:
        return "엘리트"
    elif grade >= 70:
        return "플러스"
    elif grade >= 60:
        return "평균 이상"
    elif grade >= 50:
        return "평균"
    elif grade >= 40:
        return "평균 이하"
    else:
        return "부족"

def safe_float(val, default=0):
    try:
        if pd.isna(val):
            return default
        return float(val)
    except:
        return default

def safe_int(val, default=0):
    try:
        if pd.isna(val):
            return default
        return int(val)
    except:
        return default

# 타자 유형 정보
BATTER_TYPE_INFO = {
    'FIVE_TOOL_PLAYER': ('5툴 플레이어', '모든 능력치가 균형잡힌 올라운드 플레이어'),
    'COMPLETE_SLUGGER': ('완성형 슬러거', '홈런과 갭 파워를 모두 갖춘 완성형 타자'),
    'HOME_RUN_KING': ('홈런왕', '압도적인 홈런 파워를 보여주는 타자'),
    'SLUGGER': ('슬러거', '강력한 파워와 준수한 컨택을 겸비한 중심 타자'),
    'CONTACT_MASTER': ('정교한 타격형', '뛰어난 컨택과 선구안으로 출루를 책임지는 타자'),
    'TABLE_SETTER': ('테이블세터', '탁월한 선구안과 컨택으로 득점 기회를 만드는 리드오프'),
    'BALANCED_POWER': ('균형 파워', '홈런과 갭 파워가 균형을 이루는 타자'),
    'POWER_DISCIPLINE': ('파워 & 선구안형', '장타력과 볼넷을 겸비한 현대적 중심타자'),
    'POWER_HITTER': ('파워 히터', '장타력 중심의 공격적인 타자'),
    'FREE_SWINGER': ('프리스윙어', '파워는 있지만 선구안이 부족한 공격적 타자'),
    'LINE_DRIVE_MACHINE': ('라인드라이브 머신', '컨택과 갭 파워를 같이 갖춘 타자'),
    'CONTACT_SPECIALIST': ('컨택 스페셜리스트', '높은 타율, 낮은 파워'),
    'PATIENT_HITTER': ('인내형 타자', '볼넷 전문 선구안 특화 타자'),
    'CLUTCH_PERFORMER': ('클러치 히터', '중요한 순간에 강한 타자'),
    'CONSISTENT_PRODUCER': ('꾸준한 생산자', '기복 없이 안정적인 성적'),
    'BALANCED_HITTER': ('균형잡힌 타자', '컨택과 파워가 조화를 이루는 타자'),
    'AVERAGE_HITTER': ('평균적인 타자', '리그 평균 수준의 능력을 보유한 타자'),
    'BELOW_AVERAGE': ('평균 이하 타자', '백업 또는 성장이 필요한 타자'),
}

def get_batter_type_info(batter_type):
    return BATTER_TYPE_INFO.get(batter_type, (batter_type, '분류 정보 없음'))

st.title("🏏 타자 스카우팅 리포트")

# 사이드바 - 시즌 및 선수 선택
with st.sidebar:
    st.header("선수 선택")

    season = st.selectbox("시즌", [2025, 2024, 2023, 2022, 2021], index=0)

    # 타자 목록 가져오기
    batters = get_batter_list(season)

    if len(batters) == 0:
        st.warning(f"{season} 시즌 데이터가 없습니다.")
        st.stop()

    # 선수 선택
    batter_options = batters.apply(
        lambda x: f"{x['player_name']} ({x['team_name']})" if pd.notna(x['team_name']) else x['player_name'],
        axis=1
    ).tolist()

    selected_idx = st.selectbox(
        "타자 선택",
        range(len(batter_options)),
        format_func=lambda x: batter_options[x]
    )

    selected_batter = batters.iloc[selected_idx]
    batter_pcode = selected_batter['batter_pcode']

# 데이터 로드
data = get_batter_data(batter_pcode, season)

if data is None:
    st.error("선수 데이터를 찾을 수 없습니다.")
    st.stop()

# 헤더 정보
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown(f"### {data['player_name']}")
    team_name = data.get('team_name', 'N/A')
    if pd.isna(team_name):
        team_name = 'N/A'
    st.markdown(f"**{team_name}** | {season} 시즌")

with col2:
    overall = safe_float(data.get('overall_grade_weighted', data.get('overall_grade', 50)))
    st.metric("OVR", f"{overall:.0f}", delta=get_grade_label(overall))

with col3:
    batter_type = data.get('batter_type', 'N/A')
    if pd.isna(batter_type):
        batter_type = 'N/A'
    type_name, type_desc = get_batter_type_info(batter_type)
    st.metric("타자 유형", type_name)

st.divider()

# 탭 구성 (포지션 분석 제외)
tab1, tab2, tab3 = st.tabs(["종합", "상세 지표", "분석"])

# ============================================================================
# 종합 탭
# ============================================================================
with tab1:
    # 카테고리별 점수
    st.subheader("카테고리별 평가")

    # 카테고리 점수 추출 (6 카테고리)
    categories = {
        '컨택': safe_float(data.get('contact_grade_weighted', data.get('contact_grade', 50))),
        '홈런 파워': safe_float(data.get('game_power_grade_weighted', data.get('game_power_grade', 50))),
        '갭 파워': safe_float(data.get('gap_power_grade_weighted', data.get('gap_power_grade', 50))),
        '선구안': safe_float(data.get('discipline_grade_weighted', data.get('discipline_grade', 50))),
        '일관성': safe_float(data.get('consistency_grade_weighted', data.get('consistency_grade', 50))),
        '클러치': safe_float(data.get('clutch_grade_weighted', data.get('clutch_grade', 50))),
    }

    # 레이더 차트
    fig = go.Figure()

    categories_list = list(categories.keys())
    values = list(categories.values())
    values.append(values[0])  # 닫기 위해 첫 값 추가
    categories_list_closed = categories_list + [categories_list[0]]

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories_list_closed,
        fill='toself',
        name=data['player_name'],
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='rgb(59, 130, 246)', width=2)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[20, 80]
            )
        ),
        showlegend=False,
        height=400
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 카테고리별 점수 표시
        for cat, score in categories.items():
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.write(cat)
            with col_b:
                st.markdown(f"**{score:.0f}**")
            with col_c:
                st.markdown(f"<span style='color:{get_grade_color(score)}'>{get_grade_label(score)}</span>", unsafe_allow_html=True)

    st.divider()

    # 시즌 성적
    st.subheader("시즌 성적")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        avg = safe_float(data.get('batting_average', 0))
        st.metric("타율", f"{avg:.3f}" if avg else "N/A")

    with col2:
        obp = safe_float(data.get('on_base_percentage', 0))
        st.metric("출루율", f"{obp:.3f}" if obp else "N/A")

    with col3:
        slg = safe_float(data.get('slugging_percentage', 0))
        st.metric("장타율", f"{slg:.3f}" if slg else "N/A")

    with col4:
        ops = safe_float(data.get('ops', 0))
        st.metric("OPS", f"{ops:.3f}" if ops else "N/A")

    with col5:
        hr = safe_int(data.get('home_runs', 0))
        st.metric("홈런", f"{hr}" if hr else "N/A")

    # 추가 전통 지표
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        rbi = safe_int(data.get('rbis', 0))
        st.metric("타점", f"{rbi}")

    with col2:
        sb = safe_int(data.get('stolen_bases', 0))
        st.metric("도루", f"{sb}")

    with col3:
        hits = safe_int(data.get('hits', 0))
        st.metric("안타", f"{hits}")

    with col4:
        bb = safe_int(data.get('walks', 0))
        st.metric("볼넷", f"{bb}")

    with col5:
        so = safe_int(data.get('strikeouts', 0))
        st.metric("삼진", f"{so}")

    st.divider()

    # 강점과 약점
    st.subheader("강점 및 약점")

    # 자동 분석
    strengths = []
    weaknesses = []

    for cat, score in categories.items():
        if score >= 70:
            strengths.append(f"{cat}: {get_grade_label(score)} ({score:.0f})")
        elif score < 45:
            weaknesses.append(f"{cat}: {get_grade_label(score)} ({score:.0f})")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**강점**")
        if strengths:
            for s in strengths:
                st.markdown(f"✓ {s}")
        else:
            st.markdown("*특별히 우수한 영역 없음*")

    with col2:
        st.markdown("**약점**")
        if weaknesses:
            for w in weaknesses:
                st.markdown(f"✗ {w}")
        else:
            st.markdown("*특별히 부족한 영역 없음*")

# ============================================================================
# 상세 지표 탭
# ============================================================================
with tab2:
    st.subheader("카테고리별 상세 지표")

    # 컨택
    with st.expander("컨택", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("타율", f"{safe_float(data.get('batting_average', 0)):.3f}")
            st.metric("삼진율", f"{safe_float(data.get('strikeout_rate', 0))*100:.1f}%")
        with col2:
            st.metric("전체 컨택률", f"{safe_float(data.get('overall_contact_rate', 0))*100:.1f}%")
            st.metric("2스트라이크 컨택률", f"{safe_float(data.get('two_strike_contact_rate', 0))*100:.1f}%")
        with col3:
            st.metric("존내 컨택률", f"{safe_float(data.get('in_zone_contact_rate', 0))*100:.1f}%")
            st.metric("파울볼률", f"{safe_float(data.get('foul_ball_rate', 0))*100:.1f}%")

    # 홈런 파워
    with st.expander("홈런 파워", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("홈런율", f"{safe_float(data.get('home_run_rate', 0))*100:.1f}%")
            st.metric("홈런/장타 비율", f"{safe_float(data.get('home_run_to_xbh_ratio', 0))*100:.1f}%")
        with col2:
            st.metric("ISO (홈런)", f"{safe_float(data.get('isolated_power_hr', 0)):.3f}")
            st.metric("홈런/안타 비율", f"{safe_float(data.get('home_run_per_hit_rate', 0))*100:.1f}%")
        with col3:
            st.metric("홈런 수", f"{safe_int(data.get('home_runs', 0))}")

    # 갭 파워
    with st.expander("갭 파워", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("2루타율", f"{safe_float(data.get('double_rate', 0))*100:.1f}%")
            st.metric("3루타율", f"{safe_float(data.get('triple_rate', 0))*100:.1f}%")
        with col2:
            st.metric("ISO (갭)", f"{safe_float(data.get('isolated_power_gap', 0)):.3f}")
            st.metric("갭 히트율", f"{safe_float(data.get('gap_hit_rate', 0))*100:.1f}%")
        with col3:
            st.metric("2루타/1루타 비율", f"{safe_float(data.get('double_to_single_ratio', 0)):.2f}")

    # 선구안
    with st.expander("선구안", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("볼넷율", f"{safe_float(data.get('walk_rate', 0))*100:.1f}%")
            st.metric("체이스율", f"{safe_float(data.get('chase_rate', 0))*100:.1f}%")
        with col2:
            st.metric("존 스윙률", f"{safe_float(data.get('zone_swing_rate', 0))*100:.1f}%")
            st.metric("초구 스윙률", f"{safe_float(data.get('first_pitch_swing_rate', 0))*100:.1f}%")
        with col3:
            st.metric("3-0 규율", f"{safe_float(data.get('three_zero_discipline', 0))*100:.1f}%")

    # 일관성
    with st.expander("일관성", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("월별 분산", f"{safe_float(data.get('monthly_variance', 0)):.3f}")
            st.metric("좌우 OPS 차이", f"{safe_float(data.get('left_right_ops_diff', 0)):.3f}")
        with col2:
            st.metric("직구 컨택률", f"{safe_float(data.get('fastball_contact_rate', 0))*100:.1f}%")
            st.metric("변화구 컨택률", f"{safe_float(data.get('breaking_contact_rate', 0))*100:.1f}%")
        with col3:
            st.metric("체인지업 컨택률", f"{safe_float(data.get('offspeed_contact_rate', 0))*100:.1f}%")

    # 클러치
    with st.expander("클러치", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("고레버리지 성적", f"{safe_float(data.get('high_leverage_performance', 0)):.3f}")
            st.metric("득점권 타율", f"{safe_float(data.get('risp_average', 0)):.3f}")
        with col2:
            st.metric("2아웃 타점율", f"{safe_float(data.get('two_out_rbi_rate', 0))*100:.1f}%")
            st.metric("후반 접전 성적", f"{safe_float(data.get('late_close_performance', 0)):.3f}")
        with col3:
            st.metric("만루 타율", f"{safe_float(data.get('bases_loaded_average', 0)):.3f}")

# ============================================================================
# 분석 탭
# ============================================================================
with tab3:
    st.subheader("스카우팅 분석")

    # 타자 유형 분석
    batter_type = data.get('batter_type', 'AVERAGE_HITTER')
    if pd.isna(batter_type):
        batter_type = 'AVERAGE_HITTER'
    type_name, type_desc = get_batter_type_info(batter_type)

    st.markdown(f"### 타자 유형: {type_name}")
    st.markdown(f"*{type_desc}*")

    st.divider()

    # 시즌별 추이
    st.subheader("시즌별 추이")

    all_data = load_batter_kpi()
    player_history = all_data[all_data['batter_pcode'] == batter_pcode].sort_values('season')

    if len(player_history) > 1:
        fig = go.Figure()

        # OVR 추이
        ovr_values = player_history.apply(
            lambda x: safe_float(x.get('overall_grade_weighted', x.get('overall_grade', 50))),
            axis=1
        )

        fig.add_trace(go.Scatter(
            x=player_history['season'],
            y=ovr_values,
            mode='lines+markers',
            name='OVR',
            line=dict(color='#3B82F6', width=3)
        ))

        fig.update_layout(
            xaxis_title="시즌",
            yaxis_title="등급",
            yaxis=dict(range=[20, 80]),
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

        # 시즌별 주요 지표 테이블
        st.subheader("시즌별 주요 성적")

        season_stats = player_history[['season', 'batting_average', 'on_base_percentage',
                                        'slugging_percentage', 'ops', 'home_runs']].copy()
        season_stats.columns = ['시즌', '타율', '출루율', '장타율', 'OPS', '홈런']

        # 소수점 포맷팅
        for col in ['타율', '출루율', '장타율', 'OPS']:
            season_stats[col] = season_stats[col].apply(lambda x: f"{safe_float(x):.3f}")
        season_stats['홈런'] = season_stats['홈런'].apply(lambda x: f"{safe_int(x)}")

        st.dataframe(season_stats, hide_index=True, use_container_width=True)
    else:
        st.info("다른 시즌 데이터가 없습니다.")

    st.divider()

    # 리그 비교 (백분위)
    st.subheader("리그 내 백분위 순위")

    percentile_metrics = {
        '타율': safe_float(data.get('batting_average_percentile', 50)),
        '홈런율': safe_float(data.get('home_run_rate_percentile', 50)),
        '볼넷율': safe_float(data.get('walk_rate_percentile', 50)),
        '삼진율': safe_float(data.get('strikeout_rate_percentile', 50)),
        '득점권 타율': safe_float(data.get('risp_average_percentile', 50)),
    }

    for metric, percentile in percentile_metrics.items():
        col1, col2, col3 = st.columns([3, 6, 1])
        with col1:
            st.write(metric)
        with col2:
            st.progress(percentile / 100)
        with col3:
            st.write(f"{percentile:.0f}%")
