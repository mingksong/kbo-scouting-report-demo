"""
KBO Batter Leaderboard - 타자 리더보드
정렬, 필터, 검색 기능을 제공하는 타자 순위표
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


def format_grade(grade):
    """등급 포맷팅 (색상 포함 HTML)"""
    if pd.isna(grade):
        return "-"
    grade = int(grade)
    color = get_grade_color(grade)
    return f'<span style="color: {color}; font-weight: bold;">{grade}</span>'


@st.cache_data
def load_data():
    """데이터 로드"""
    batter_kpi = pd.read_parquet(DATA_DIR / "batter_kpi.parquet")

    # 숫자형으로 변환
    numeric_cols = [
        'overall_grade', 'overall_grade_weighted',
        'contact_grade', 'contact_grade_weighted',
        'game_power_grade', 'game_power_grade_weighted',
        'gap_power_grade', 'gap_power_grade_weighted',
        'discipline_grade', 'discipline_grade_weighted',
        'consistency_grade', 'consistency_grade_weighted',
        'clutch_grade', 'clutch_grade_weighted',
        'batting_average', 'on_base_percentage', 'slugging_percentage', 'ops',
        'home_runs', 'rbi', 'plate_appearances'
    ]

    for col in numeric_cols:
        if col in batter_kpi.columns:
            batter_kpi[col] = pd.to_numeric(batter_kpi[col], errors='coerce')

    return batter_kpi


def get_batter_type_display(batter_type):
    """타자 유형 한글 표시"""
    type_map = {
        'FIVE_TOOL_PLAYER': '5툴 플레이어',
        'COMPLETE_SLUGGER': '완성형 슬러거',
        'HOME_RUN_KING': '홈런왕',
        'CONTACT_MASTER': '타격 장인',
        'TABLE_SETTER': '테이블세터',
        'BALANCED_POWER': '균형 파워',
        'POWER_DISCIPLINE': '인내형 파워',
        'PURE_POWER': '순수 파워',
        'GAP_SPECIALIST': '갭 스페셜리스트',
        'LINE_DRIVE_MACHINE': '라인드라이브 머신',
        'CONTACT_SPECIALIST': '컨택 스페셜리스트',
        'PATIENT_HITTER': '인내형 타자',
        'CLUTCH_PERFORMER': '클러치 히터',
        'CONSISTENT_PRODUCER': '꾸준한 생산자',
        'BALANCED_HITTER': '균형형 타자',
        'POTENTIAL_POWER': '잠재형 파워',
        'POTENTIAL_CONTACT': '잠재형 컨택',
        'ROLE_PLAYER': '역할 선수',
        'AVERAGE_HITTER': '평균 타자',
        'BELOW_AVERAGE': '평균 이하'
    }
    return type_map.get(batter_type, batter_type or '미분류')


def main():
    st.set_page_config(
        page_title="타자 리더보드 - KBO Scouting",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 타자 리더보드")
    st.markdown("KBO 타자들의 종합 능력치 순위입니다.")

    # 데이터 로드
    batter_kpi = load_data()

    # 사이드바 필터
    st.sidebar.header("🔍 필터")

    # 시즌 선택
    seasons = sorted(batter_kpi['season'].unique(), reverse=True)
    selected_season = st.sidebar.selectbox(
        "시즌",
        seasons,
        index=0
    )

    # 최소 타석 필터
    min_pa = st.sidebar.slider(
        "최소 타석",
        min_value=0,
        max_value=500,
        value=50,
        step=10
    )

    # 팀 필터
    season_data = batter_kpi[batter_kpi['season'] == selected_season]
    teams = ['전체'] + sorted(season_data['team_name'].dropna().unique().tolist())
    selected_team = st.sidebar.selectbox("팀", teams)

    # 정렬 기준
    sort_options = {
        '종합 (OVR)': 'overall_grade_weighted',
        '컨택': 'contact_grade_weighted',
        '홈런 파워': 'game_power_grade_weighted',
        '갭 파워': 'gap_power_grade_weighted',
        '선구안': 'discipline_grade_weighted',
        '일관성': 'consistency_grade_weighted',
        '클러치': 'clutch_grade_weighted',
        'OPS': 'ops',
        '타율': 'batting_average',
        '홈런': 'home_runs'
    }
    selected_sort = st.sidebar.selectbox("정렬 기준", list(sort_options.keys()))
    sort_column = sort_options[selected_sort]

    # 검색
    search_term = st.sidebar.text_input("선수 검색", placeholder="이름 입력...")

    # 데이터 필터링
    filtered_data = season_data.copy()

    # 최소 타석 필터
    if 'plate_appearances' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['plate_appearances'] >= min_pa]

    # 팀 필터
    if selected_team != '전체':
        filtered_data = filtered_data[filtered_data['team_name'] == selected_team]

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
        st.metric("총 선수", f"{len(filtered_data)}명")
    with col2:
        avg_ovr = filtered_data['overall_grade_weighted'].mean()
        if pd.notna(avg_ovr):
            st.metric("평균 OVR", f"{avg_ovr:.1f}")
        else:
            avg_ovr = filtered_data['overall_grade'].mean()
            st.metric("평균 OVR", f"{avg_ovr:.1f}" if pd.notna(avg_ovr) else "-")
    with col3:
        avg_ops = filtered_data['ops'].mean()
        st.metric("평균 OPS", f"{avg_ops:.3f}" if pd.notna(avg_ops) else "-")
    with col4:
        total_hr = filtered_data['home_runs'].sum()
        st.metric("총 홈런", f"{int(total_hr)}개" if pd.notna(total_hr) else "-")

    st.markdown("---")

    # 리더보드 테이블
    if len(filtered_data) == 0:
        st.warning("조건에 맞는 선수가 없습니다.")
    else:
        # 표시할 컬럼 선택
        display_cols = ['rank', 'player_name', 'team_name']

        # 능력치 등급 컬럼
        grade_cols = [
            ('overall_grade_weighted', 'overall_grade', 'OVR'),
            ('contact_grade_weighted', 'contact_grade', '컨택'),
            ('game_power_grade_weighted', 'game_power_grade', '홈런'),
            ('gap_power_grade_weighted', 'gap_power_grade', '갭'),
            ('discipline_grade_weighted', 'discipline_grade', '선구안'),
            ('consistency_grade_weighted', 'consistency_grade', '일관성'),
            ('clutch_grade_weighted', 'clutch_grade', '클러치'),
        ]

        # 전통 지표 컬럼
        stat_cols = [
            ('batting_average', '타율'),
            ('ops', 'OPS'),
            ('home_runs', 'HR'),
            ('plate_appearances', 'PA'),
        ]

        # 데이터 준비
        display_data = []
        for _, row in filtered_data.iterrows():
            player_row = {
                '순위': int(row['rank']),
                '선수': row['player_name'],
                '팀': row['team_name'],
            }

            # 등급 추가
            for weighted_col, base_col, display_name in grade_cols:
                value = row.get(weighted_col)
                if pd.isna(value):
                    value = row.get(base_col)
                player_row[display_name] = int(value) if pd.notna(value) else None

            # 전통 지표 추가
            player_row['타율'] = f"{row['batting_average']:.3f}" if pd.notna(row.get('batting_average')) else "-"
            player_row['OPS'] = f"{row['ops']:.3f}" if pd.notna(row.get('ops')) else "-"
            player_row['HR'] = int(row['home_runs']) if pd.notna(row.get('home_runs')) else "-"
            player_row['PA'] = int(row['plate_appearances']) if pd.notna(row.get('plate_appearances')) else "-"

            display_data.append(player_row)

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

        # 등급 컬럼에 스타일 적용
        grade_columns = ['OVR', '컨택', '홈런', '갭', '선구안', '일관성', '클러치']

        styled_df = df_display.style.applymap(
            style_grade,
            subset=grade_columns
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
                    f'<span style="color: {color}; font-weight: bold; font-size: 1.2em;">{grade_range}</span><br>'
                    f'<span style="font-size: 0.9em;">{label}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )


if __name__ == "__main__":
    main()
