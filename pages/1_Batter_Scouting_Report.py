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
    get_batter_list, get_batter_data, get_team_color, load_batter_kpi, search_batters
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

    # 선수 이름 검색
    search_query = st.text_input("선수 이름 검색 (2글자 이상)", placeholder="예: 김현수")

    batter_pcode = None

    if len(search_query) >= 2:
        # 검색 결과
        search_results = search_batters(season, search_query)

        if len(search_results) == 0:
            st.warning(f"'{search_query}' 검색 결과가 없습니다.")
        else:
            # 검색 결과 선택
            options = search_results['display_name'].tolist()
            pcodes = search_results['batter_pcode'].tolist()

            selected_idx = st.selectbox(
                f"검색 결과 ({len(options)}명)",
                range(len(options)),
                format_func=lambda x: options[x]
            )

            batter_pcode = pcodes[selected_idx]
    else:
        st.info("선수 이름을 2글자 이상 입력하세요.")

if batter_pcode is None:
    st.info("사이드바에서 선수를 검색하세요.")
    st.stop()

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

    # 가중치 정보
    # unit: '' = 그대로, '%' = 이미 백분율(그대로 표시), '%*100' = 0-1 비율(×100 필요)
    METRIC_WEIGHTS = {
        'contact': {
            'batting_average': ('타율', 0.45, ''),
            'strikeout_rate': ('삼진율', 0.25, '%'),  # 이미 백분율
            'overall_contact_rate': ('전체 컨택률', 0.08, '%'),
            'two_strike_contact_rate': ('2스트라이크 컨택률', 0.10, '%'),
            'in_zone_contact_rate': ('존내 컨택률', 0.07, '%'),
            'foul_ball_rate': ('파울볼률', 0.05, '%'),
        },
        'game_power': {
            'home_run_rate': ('홈런율', 0.35, '%'),  # 이미 백분율
            'home_run_to_xbh_ratio': ('홈런/장타 비율', 0.25, '%*100'),  # 0-1 비율
            'isolated_power_hr': ('ISO (홈런)', 0.25, ''),
            'home_run_per_hit_rate': ('홈런/안타 비율', 0.15, '%'),  # 이미 백분율
        },
        'gap_power': {
            'double_rate': ('2루타율', 0.30, '%'),  # 이미 백분율
            'triple_rate': ('3루타율', 0.05, '%'),
            'isolated_power_gap': ('ISO (갭)', 0.30, ''),
            'gap_hit_rate': ('갭 히트율', 0.20, '%'),
            'double_to_single_ratio': ('2루타/1루타 비율', 0.15, ''),
        },
        'discipline': {
            'walk_rate': ('볼넷율', 0.35, '%'),  # 이미 백분율
            'chase_rate': ('체이스율', 0.25, '%'),
            'zone_swing_rate': ('존 스윙률', 0.30, '%'),
            'first_pitch_swing_rate': ('초구 스윙률', 0.08, '%'),
            'three_zero_discipline': ('3-0 규율', 0.02, '%'),
        },
        'consistency': {
            'monthly_variance': ('월별 분산', 0.35, ''),
            'left_right_ops_diff': ('좌우 OPS 차이', 0.30, ''),
            'fastball_contact_rate': ('직구 컨택률', 0.15, '%'),
            'breaking_contact_rate': ('변화구 컨택률', 0.10, '%'),
            'offspeed_contact_rate': ('체인지업 컨택률', 0.10, '%'),
        },
        'clutch': {
            'high_leverage_performance': ('고레버리지 성적', 0.30, ''),
            'risp_average': ('득점권 타율', 0.25, ''),
            'two_out_rbi_rate': ('2아웃 타점율', 0.20, '%'),
            'late_close_performance': ('후반 접전 성적', 0.20, ''),
            'bases_loaded_average': ('만루 타율', 0.05, ''),
        }
    }

    def get_weight_color(weight):
        """가중치에 따른 색상"""
        if weight >= 0.35:
            return "#DC2626"  # 빨강 (매우 중요)
        elif weight >= 0.25:
            return "#EA580C"  # 주황 (중요)
        elif weight >= 0.15:
            return "#2563EB"  # 파랑 (보통)
        elif weight >= 0.10:
            return "#6B7280"  # 회색 (낮음)
        else:
            return "#9CA3AF"  # 연회색 (매우 낮음)

    def render_category_card(category_name, category_key, grade_key, grade_weighted_key):
        """카테고리 카드 렌더링"""
        grade = safe_float(data.get(grade_weighted_key, data.get(grade_key, 50)))

        # 카테고리 헤더
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    border-radius: 12px; padding: 16px; margin-bottom: 8px;
                    border: 1px solid #e2e8f0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600;">{category_name}</h4>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: {get_grade_color(grade)}; color: white;
                                 padding: 4px 12px; border-radius: 20px; font-weight: bold;
                                 font-size: 0.9rem;">{grade:.0f}</span>
                    <span style="color: {get_grade_color(grade)}; font-size: 0.8rem;">
                        {get_grade_label(grade)}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 세부 지표
        metrics = METRIC_WEIGHTS.get(category_key, {})

        for key, info in metrics.items():
            name = info[0]
            weight = info[1]
            unit = info[2] if len(info) > 2 else ''

            # 값 포맷팅
            val = safe_float(data.get(key, 0))
            if unit == '%':
                # 이미 백분율 형태 (11.57 = 11.57%)
                formatted_val = f"{val:.1f}%"
            elif unit == '%*100':
                # 0-1 비율을 백분율로 변환 (0.174 → 17.4%)
                formatted_val = f"{val*100:.1f}%"
            elif unit == '':
                if 'average' in key or 'performance' in key or 'iso' in key.lower():
                    formatted_val = f"{val:.3f}"
                elif 'ratio' in key:
                    formatted_val = f"{val:.2f}"
                elif 'variance' in key or 'diff' in key:
                    formatted_val = f"{val:.3f}"
                else:
                    formatted_val = f"{val:.3f}"
            else:
                formatted_val = f"{val:.2f}"

            # 등급 (있으면)
            grade_col = f"{key}_grade"
            metric_grade = safe_float(data.get(grade_col, 0))

            col1, col2, col3, col4 = st.columns([4, 2, 2, 2])

            with col1:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 0.9rem;">{name}</span>
                    <span style="color: {get_weight_color(weight)}; font-size: 0.75rem; font-weight: 600;">
                        W-{int(weight*100)}%
                    </span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"<span style='font-family: monospace; font-weight: 500;'>{formatted_val}</span>",
                           unsafe_allow_html=True)

            with col3:
                if metric_grade > 0:
                    st.markdown(f"""
                    <span style="background: {get_grade_color(metric_grade)}; color: white;
                                 padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">
                        {metric_grade:.0f}
                    </span>
                    """, unsafe_allow_html=True)

            with col4:
                percentile_col = f"{key}_percentile"
                percentile = safe_float(data.get(percentile_col, 0))
                if percentile > 0:
                    st.markdown(f"<span style='font-size: 0.75rem; color: #6b7280;'>상위 {100-percentile:.0f}%</span>",
                               unsafe_allow_html=True)

        st.markdown("---")

    # 각 카테고리 렌더링
    render_category_card("컨택", "contact", "contact_grade", "contact_grade_weighted")
    render_category_card("홈런 파워", "game_power", "game_power_grade", "game_power_grade_weighted")
    render_category_card("갭 파워", "gap_power", "gap_power_grade", "gap_power_grade_weighted")
    render_category_card("선구안", "discipline", "discipline_grade", "discipline_grade_weighted")
    render_category_card("일관성", "consistency", "consistency_grade", "consistency_grade_weighted")
    render_category_card("클러치", "clutch", "clutch_grade", "clutch_grade_weighted")

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
