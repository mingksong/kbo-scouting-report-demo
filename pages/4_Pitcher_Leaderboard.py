"""
KBO Pitcher Leaderboard - 투수 리더보드
정렬, 필터, 검색 기능을 제공하는 투수 순위표
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# 경로 설정
DATA_DIR = Path(__file__).parent.parent / "data"


def get_grade_color(grade):
    """등급에 따른 색상 반환"""
    if pd.isna(grade):
        return "#9CA3AF"
    grade = int(grade)
    if grade >= 80:
        return "#DC2626"  # Elite - Red
    elif grade >= 70:
        return "#7C3AED"  # Great - Purple
    elif grade >= 60:
        return "#2563EB"  # Above Average - Blue
    elif grade >= 50:
        return "#10B981"  # Average - Green
    elif grade >= 40:
        return "#F59E0B"  # Below Average - Yellow
    else:
        return "#9CA3AF"  # Poor - Gray


def get_role_display(role):
    """투수 역할 한글 표시"""
    role_map = {
        'Starter': '선발',
        'Closer': '마무리',
        'Setup': '셋업',
        'Middle': '중계',
        'Long': '롱릴리프',
        'Unknown': '미정',
        None: '미정'
    }
    return role_map.get(role, role or '미정')


def get_role_color(role):
    """투수 역할에 따른 색상"""
    role_colors = {
        'Starter': '#2563EB',    # Blue
        'Closer': '#DC2626',     # Red
        'Setup': '#7C3AED',      # Purple
        'Middle': '#10B981',     # Green
        'Long': '#F59E0B',       # Yellow
    }
    return role_colors.get(role, '#9CA3AF')


@st.cache_data
def load_data():
    """데이터 로드"""
    pitcher_kpi = pd.read_parquet(DATA_DIR / "pitcher_kpi.parquet")

    # 숫자형으로 변환
    numeric_cols = [
        'overall_grade', 'overall_percentile',
        'control_grade', 'aggression_grade', 'efficiency_grade',
        'stuff_grade', 'clutch_grade',
        'total_games', 'total_pitches', 'total_innings_pitched',
        'whiff_rate', 'chase_rate', 'first_pitch_strike_rate',
        'avg_pitches_per_batter', 'k_per_9'
    ]

    for col in numeric_cols:
        if col in pitcher_kpi.columns:
            pitcher_kpi[col] = pd.to_numeric(pitcher_kpi[col], errors='coerce')

    return pitcher_kpi


def main():
    st.set_page_config(
        page_title="투수 리더보드 - KBO Scouting",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 투수 리더보드")
    st.markdown("KBO 투수들의 종합 능력치 순위입니다.")

    # 데이터 로드
    pitcher_kpi = load_data()

    # 사이드바 필터
    st.sidebar.header("🔍 필터")

    # 시즌 선택
    seasons = sorted(pitcher_kpi['season'].unique(), reverse=True)
    selected_season = st.sidebar.selectbox(
        "시즌",
        seasons,
        index=0
    )

    # 최소 투구수 필터
    min_pitches = st.sidebar.slider(
        "최소 투구수",
        min_value=0,
        max_value=2000,
        value=100,
        step=50
    )

    # 팀 필터
    season_data = pitcher_kpi[pitcher_kpi['season'] == selected_season]
    teams = ['전체'] + sorted(season_data['team_name'].dropna().unique().tolist())
    selected_team = st.sidebar.selectbox("팀", teams)

    # 역할 필터
    roles = ['전체', '선발', '마무리', '셋업', '중계', '롱릴리프']
    role_map_reverse = {
        '전체': None,
        '선발': 'Starter',
        '마무리': 'Closer',
        '셋업': 'Setup',
        '중계': 'Middle',
        '롱릴리프': 'Long'
    }
    selected_role = st.sidebar.selectbox("역할", roles)

    # 정렬 기준
    sort_options = {
        '종합 (OVR)': 'overall_grade',
        '제구력': 'control_grade',
        '공격성': 'aggression_grade',
        '효율성': 'efficiency_grade',
        '구위': 'stuff_grade',
        '클러치': 'clutch_grade',
        '헛스윙 유도율': 'whiff_rate',
        '체이스율': 'chase_rate',
        '등판 수': 'total_games',
        '투구 수': 'total_pitches'
    }
    selected_sort = st.sidebar.selectbox("정렬 기준", list(sort_options.keys()))
    sort_column = sort_options[selected_sort]

    # 검색
    search_term = st.sidebar.text_input("선수 검색", placeholder="이름 입력...")

    # 데이터 필터링
    filtered_data = season_data.copy()

    # 최소 투구수 필터
    if 'total_pitches' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['total_pitches'] >= min_pitches]

    # 팀 필터
    if selected_team != '전체':
        filtered_data = filtered_data[filtered_data['team_name'] == selected_team]

    # 역할 필터
    if selected_role != '전체':
        role_value = role_map_reverse[selected_role]
        if 'pitcher_role' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['pitcher_role'] == role_value]

    # 검색 필터
    if search_term:
        filtered_data = filtered_data[
            filtered_data['player_name'].str.contains(search_term, case=False, na=False)
        ]

    # 정렬
    if sort_column in filtered_data.columns:
        filtered_data = filtered_data.sort_values(sort_column, ascending=False, na_position='last')

    # 순위 추가
    filtered_data = filtered_data.reset_index(drop=True)
    filtered_data['rank'] = range(1, len(filtered_data) + 1)

    # 통계 표시
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 투수", f"{len(filtered_data)}명")
    with col2:
        avg_ovr = filtered_data['overall_grade'].mean()
        st.metric("평균 OVR", f"{avg_ovr:.1f}" if pd.notna(avg_ovr) else "-")
    with col3:
        # 선발 투수 수
        starters = len(filtered_data[filtered_data.get('pitcher_role', '') == 'Starter']) if 'pitcher_role' in filtered_data.columns else 0
        st.metric("선발 투수", f"{starters}명")
    with col4:
        # 구원 투수 수
        relievers = len(filtered_data) - starters
        st.metric("구원 투수", f"{relievers}명")

    st.markdown("---")

    # 리더보드 테이블
    if len(filtered_data) == 0:
        st.warning("조건에 맞는 투수가 없습니다.")
    else:
        # 데이터 준비
        display_data = []
        for _, row in filtered_data.iterrows():
            pitcher_row = {
                '순위': int(row['rank']),
                '선수': row['player_name'],
                '팀': row['team_name'],
                '역할': get_role_display(row.get('pitcher_role')),
                'OVR': int(row['overall_grade']) if pd.notna(row.get('overall_grade')) else None,
                '제구': int(row['control_grade']) if pd.notna(row.get('control_grade')) else None,
                '공격성': int(row['aggression_grade']) if pd.notna(row.get('aggression_grade')) else None,
                '효율성': int(row['efficiency_grade']) if pd.notna(row.get('efficiency_grade')) else None,
                '구위': int(row['stuff_grade']) if pd.notna(row.get('stuff_grade')) else None,
                '클러치': int(row['clutch_grade']) if pd.notna(row.get('clutch_grade')) else None,
                '경기': int(row['total_games']) if pd.notna(row.get('total_games')) else "-",
                '투구수': int(row['total_pitches']) if pd.notna(row.get('total_pitches')) else "-",
            }

            # 선택적 지표
            if pd.notna(row.get('whiff_rate')):
                pitcher_row['헛스윙%'] = f"{row['whiff_rate']*100:.1f}" if row['whiff_rate'] < 1 else f"{row['whiff_rate']:.1f}"
            else:
                pitcher_row['헛스윙%'] = "-"

            display_data.append(pitcher_row)

        df_display = pd.DataFrame(display_data)

        # 스타일링 함수
        def style_grade(val):
            if pd.isna(val) or val is None:
                return ''
            try:
                grade = int(val)
                color = get_grade_color(grade)
                return f'color: {color}; font-weight: bold'
            except:
                return ''

        def style_role(val):
            role_reverse = {
                '선발': 'Starter',
                '마무리': 'Closer',
                '셋업': 'Setup',
                '중계': 'Middle',
                '롱릴리프': 'Long'
            }
            role_eng = role_reverse.get(val)
            if role_eng:
                color = get_role_color(role_eng)
                return f'color: {color}; font-weight: bold'
            return ''

        # 등급 컬럼에 스타일 적용
        grade_columns = ['OVR', '제구', '공격성', '효율성', '구위', '클러치']

        styled_df = df_display.style.applymap(
            style_grade,
            subset=grade_columns
        ).applymap(
            style_role,
            subset=['역할']
        )

        # 테이블 표시
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=600,
            hide_index=True
        )

        # 등급 범례
        st.markdown("---")

        col_legend1, col_legend2 = st.columns(2)

        with col_legend1:
            st.markdown("### 📖 등급 범례")
            legend_cols = st.columns(6)
            grades = [
                ("80+", "#DC2626", "Elite"),
                ("70-79", "#7C3AED", "Great"),
                ("60-69", "#2563EB", "Above Avg"),
                ("50-59", "#10B981", "Average"),
                ("40-49", "#F59E0B", "Below Avg"),
                ("20-39", "#9CA3AF", "Poor"),
            ]
            for i, (grade_range, color, label) in enumerate(grades):
                with legend_cols[i]:
                    st.markdown(
                        f'<div style="text-align: center;">'
                        f'<span style="color: {color}; font-weight: bold; font-size: 1.1em;">{grade_range}</span><br>'
                        f'<span style="font-size: 0.8em;">{label}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        with col_legend2:
            st.markdown("### 🎯 역할 범례")
            role_cols = st.columns(5)
            role_legend = [
                ("선발", "#2563EB"),
                ("마무리", "#DC2626"),
                ("셋업", "#7C3AED"),
                ("중계", "#10B981"),
                ("롱릴리프", "#F59E0B"),
            ]
            for i, (role_name, color) in enumerate(role_legend):
                with role_cols[i]:
                    st.markdown(
                        f'<div style="text-align: center;">'
                        f'<span style="color: {color}; font-weight: bold;">{role_name}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )


if __name__ == "__main__":
    main()
