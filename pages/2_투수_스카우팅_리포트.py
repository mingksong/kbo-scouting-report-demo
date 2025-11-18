"""
투수 스카우팅 리포트 페이지 - 전체 기능 구현 (역할별 분석 탭 제외)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

# 상위 디렉토리 추가
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import (
    get_pitcher_list, get_pitcher_data, get_team_color, load_pitcher_kpi
)

st.set_page_config(
    page_title="투수 스카우팅 리포트",
    page_icon="⚾",
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

st.title("⚾ 투수 스카우팅 리포트")

# 사이드바 - 시즌 및 선수 선택
with st.sidebar:
    st.header("선수 선택")

    season = st.selectbox("시즌", [2025, 2024, 2023, 2022, 2021], index=0)

    # 투수 목록 가져오기
    pitchers = get_pitcher_list(season)

    if len(pitchers) == 0:
        st.warning(f"{season} 시즌 데이터가 없습니다.")
        st.stop()

    # 선수 선택
    pitcher_options = pitchers.apply(
        lambda x: f"{x['player_name']} ({x['team_name']})" if pd.notna(x['team_name']) else x['player_name'],
        axis=1
    ).tolist()

    selected_idx = st.selectbox(
        "투수 선택",
        range(len(pitcher_options)),
        format_func=lambda x: pitcher_options[x]
    )

    selected_pitcher = pitchers.iloc[selected_idx]
    pitcher_pcode = selected_pitcher['pitcher_pcode']

# 데이터 로드
data = get_pitcher_data(pitcher_pcode, season)

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
    overall = safe_float(data.get('overall_grade', 50))
    st.metric("OVR", f"{overall:.0f}", delta=get_grade_label(overall))

with col3:
    role = data.get('role_type', data.get('pitcher_role', 'N/A'))
    if pd.isna(role):
        role = 'N/A'
    st.metric("역할", role)

st.divider()

# 탭 구성 (역할별 분석 제외)
tab1, tab2, tab3 = st.tabs(["개요", "전체 지표", "리그 비교"])

# ============================================================================
# 개요 탭
# ============================================================================
with tab1:
    # 카테고리별 점수
    st.subheader("카테고리별 평가")

    # 카테고리 점수 추출 (5 카테고리)
    categories = {
        '제구력': safe_float(data.get('control_grade', 50)),
        '공격성': safe_float(data.get('aggression_grade', 50)),
        '효율성': safe_float(data.get('efficiency_grade', 50)),
        '구위': safe_float(data.get('stuff_grade', 50)),
        '클러치': safe_float(data.get('clutch_grade', 50)),
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
        fillcolor='rgba(239, 68, 68, 0.3)',
        line=dict(color='rgb(239, 68, 68)', width=2)
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

    st.divider()

    # 스카우팅 분석
    st.subheader("스카우팅 분석")

    # 제구력 분석
    control_score = safe_float(data.get('control_grade', 50))
    if control_score >= 70:
        control_analysis = "뛰어난 제구력을 보유. 초구 스트라이크율과 볼넷 회피율이 리그 상위권."
    elif control_score >= 50:
        control_analysis = "평균적인 제구력. 카운트 관리 능력 개선 필요."
    else:
        control_analysis = "제구력 개선 필요. 특히 3볼 상황에서의 회복률이 낮음."

    # 구위 분석
    stuff_score = safe_float(data.get('stuff_grade', 50))
    if stuff_score >= 70:
        stuff_analysis = "압도적인 구위. 헛스윙 유도 능력이 뛰어나고 평균 구속도 리그 상위권."
    elif stuff_score >= 50:
        stuff_analysis = "평균적인 구위. 변화구 효과성 향상 필요."
    else:
        stuff_analysis = "구위 강화 필요. 특히 스윙 앤 미스 유도 능력 개선 필요."

    # 효율성 분석
    efficiency_score = safe_float(data.get('efficiency_grade', 50))
    if efficiency_score >= 70:
        efficiency_analysis = "매우 효율적인 투구. 적은 투구수로 아웃카운트 확보."
    elif efficiency_score >= 50:
        efficiency_analysis = "평균적인 투구 효율성. 초구 승부 능력 향상 여지 있음."
    else:
        efficiency_analysis = "투구 효율성 개선 필요. 타자당 투구수가 많음."

    st.markdown(f"**제구력**: {control_analysis}")
    st.markdown(f"**구위**: {stuff_analysis}")
    st.markdown(f"**효율성**: {efficiency_analysis}")

# ============================================================================
# 전체 지표 탭
# ============================================================================
with tab2:
    st.subheader("카테고리별 상세 지표")

    # 제구력
    with st.expander("제구력 (Control)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("초구 스트라이크율", f"{safe_float(data.get('first_pitch_strike_rate', 0))*100:.1f}%")
            st.metric("볼넷 회피율", f"{safe_float(data.get('walk_avoidance_rate', 0))*100:.1f}%")
        with col2:
            st.metric("3볼 회복률", f"{safe_float(data.get('three_ball_recovery_rate', 0))*100:.1f}%")
            st.metric("유리한 카운트 진입률", f"{safe_float(data.get('favorable_count_entry_rate', 0))*100:.1f}%")
        with col3:
            st.metric("주구종 제구율", f"{safe_float(data.get('main_pitch_control_rate', 0))*100:.1f}%")

    # 공격성
    with st.expander("공격성 (Aggression)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("2스트라이크 삼진율", f"{safe_float(data.get('two_strike_strikeout_rate', 0))*100:.1f}%")
            st.metric("초반 스트라이크율", f"{safe_float(data.get('early_strike_rate', 0))*100:.1f}%")
        with col2:
            st.metric("마무리 능력", f"{safe_float(data.get('finishing_ability_rate', 0))*100:.1f}%")
            st.metric("고속구 결정률", f"{safe_float(data.get('high_velocity_decision_rate', 0))*100:.1f}%")

    # 효율성
    with st.expander("효율성 (Efficiency)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("타자당 평균 투구수", f"{safe_float(data.get('avg_pitches_per_batter', 0)):.1f}")
            st.metric("카운트 효율 지수", f"{safe_float(data.get('count_efficiency_index', 0)):.2f}")
        with col2:
            st.metric("풀카운트 회피율", f"{safe_float(data.get('full_count_avoidance_rate', 0))*100:.1f}%")
            st.metric("빠른 해결율", f"{safe_float(data.get('quick_resolution_rate', 0))*100:.1f}%")
        with col3:
            st.metric("이닝당 투구수", f"{safe_float(data.get('pitches_per_inning', 0)):.1f}")

    # 구위
    with st.expander("구위 (Stuff)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("헛스윙 유도율", f"{safe_float(data.get('whiff_rate', 0))*100:.1f}%")
            st.metric("체이스율", f"{safe_float(data.get('chase_rate', 0))*100:.1f}%")
        with col2:
            st.metric("존내 헛스윙률", f"{safe_float(data.get('in_zone_whiff_rate', 0))*100:.1f}%")
            st.metric("언히터블 피치율", f"{safe_float(data.get('unhittable_pitch_rate', 0))*100:.1f}%")
        with col3:
            avg_velocity = safe_float(data.get('avg_fastball_velocity', 0))
            st.metric("평균 패스트볼 구속", f"{avg_velocity:.1f} km/h" if avg_velocity else "N/A")

    # 클러치
    with st.expander("클러치 (Clutch)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("득점권 아웃률", f"{safe_float(data.get('risp_out_rate', 0))*100:.1f}%")
            st.metric("만루 탈출률", f"{safe_float(data.get('bases_loaded_escape_rate', 0))*100:.1f}%")
        with col2:
            st.metric("2아웃 이닝 종료율", f"{safe_float(data.get('two_out_inning_end_rate', 0))*100:.1f}%")
            st.metric("첫 타자 아웃률", f"{safe_float(data.get('first_batter_out_rate', 0))*100:.1f}%")
        with col3:
            st.metric("삼자범퇴 비율", f"{safe_float(data.get('three_up_three_down_rate', 0))*100:.1f}%")

# ============================================================================
# 리그 비교 탭
# ============================================================================
with tab3:
    st.subheader("리그 내 백분위 순위")

    # 주요 지표 백분위
    percentile_metrics = {
        '초구 스트라이크율': safe_float(data.get('first_pitch_strike_rate_percentile', 50)),
        '헛스윙 유도율': safe_float(data.get('whiff_rate_percentile', 50)),
        '체이스율': safe_float(data.get('chase_rate_percentile', 50)),
        '타자당 투구수': safe_float(data.get('avg_pitches_per_batter_percentile', 50)),
        '득점권 아웃률': safe_float(data.get('risp_out_rate_percentile', 50)),
        '평균 구속': safe_float(data.get('avg_fastball_velocity_percentile', 50)),
    }

    for metric, percentile in percentile_metrics.items():
        col1, col2, col3 = st.columns([3, 6, 1])
        with col1:
            st.write(metric)
        with col2:
            st.progress(percentile / 100)
        with col3:
            st.write(f"{percentile:.0f}%")

    st.divider()

    # 시즌별 추이
    st.subheader("시즌별 추이")

    all_data = load_pitcher_kpi()
    player_history = all_data[all_data['pitcher_pcode'] == pitcher_pcode].sort_values('season')

    if len(player_history) > 1:
        fig = go.Figure()

        # OVR 추이
        ovr_values = player_history['overall_grade'].apply(lambda x: safe_float(x, 50))

        fig.add_trace(go.Scatter(
            x=player_history['season'],
            y=ovr_values,
            mode='lines+markers',
            name='OVR',
            line=dict(color='#EF4444', width=3)
        ))

        fig.update_layout(
            xaxis_title="시즌",
            yaxis_title="등급",
            yaxis=dict(range=[20, 80]),
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

        # 시즌별 카테고리 점수 테이블
        st.subheader("시즌별 카테고리 점수")

        season_stats = player_history[['season', 'control_grade', 'aggression_grade',
                                        'efficiency_grade', 'stuff_grade', 'clutch_grade',
                                        'overall_grade']].copy()
        season_stats.columns = ['시즌', '제구력', '공격성', '효율성', '구위', '클러치', 'OVR']

        # 정수 포맷팅
        for col in ['제구력', '공격성', '효율성', '구위', '클러치', 'OVR']:
            season_stats[col] = season_stats[col].apply(lambda x: f"{safe_int(x)}")

        st.dataframe(season_stats, hide_index=True, use_container_width=True)
    else:
        st.info("다른 시즌 데이터가 없습니다.")
