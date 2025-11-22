#!/usr/bin/env python3
"""
KBO 스카우팅 데이터 JSON 내보내기 스크립트
Parquet 데이터를 모바일 앱용 JSON 단일 파일로 변환

Usage:
    python export_all_data_to_json.py
    python export_all_data_to_json.py --compress  # gzip 압축
"""

import pandas as pd
import json
import gzip
from pathlib import Path
from datetime import datetime
import argparse

# 경로 설정
DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "export"

# 팀 정보
TEAMS = {
    'KIA': {'name': 'KIA 타이거즈', 'color': '#EA0029', 'short': 'KIA'},
    'SSG': {'name': 'SSG 랜더스', 'color': '#CE0E2D', 'short': 'SSG'},
    'LG': {'name': 'LG 트윈스', 'color': '#C30452', 'short': 'LG'},
    'KT': {'name': 'KT 위즈', 'color': '#000000', 'short': 'KT'},
    'NC': {'name': 'NC 다이노스', 'color': '#315288', 'short': 'NC'},
    '두산': {'name': '두산 베어스', 'color': '#131230', 'short': '두산'},
    '삼성': {'name': '삼성 라이온즈', 'color': '#074CA1', 'short': '삼성'},
    '롯데': {'name': '롯데 자이언츠', 'color': '#041E42', 'short': '롯데'},
    '한화': {'name': '한화 이글스', 'color': '#FF6600', 'short': '한화'},
    '키움': {'name': '키움 히어로즈', 'color': '#570514', 'short': '키움'}
}


def load_parquet_data():
    """Parquet 데이터 로드"""
    print("Loading Parquet files...")

    batter_kpi = pd.read_parquet(DATA_DIR / "batter_kpi.parquet")
    pitcher_kpi = pd.read_parquet(DATA_DIR / "pitcher_kpi.parquet")
    players = pd.read_parquet(DATA_DIR / "players.parquet")
    teams = pd.read_parquet(DATA_DIR / "teams.parquet")

    print(f"  Batters: {len(batter_kpi)} records")
    print(f"  Pitchers: {len(pitcher_kpi)} records")
    print(f"  Players: {len(players)} records")

    return batter_kpi, pitcher_kpi, players, teams


def build_batter_index(batter_kpi: pd.DataFrame, players: pd.DataFrame) -> dict:
    """타자 인덱스 생성"""
    index = {}

    # 선수별 시즌 그룹화
    batter_seasons = batter_kpi.groupby('batter_pcode')['season'].apply(list).to_dict()

    for pcode, seasons in batter_seasons.items():
        # 최신 시즌 데이터 가져오기
        latest = batter_kpi[
            (batter_kpi['batter_pcode'] == pcode) &
            (batter_kpi['season'] == max(seasons))
        ].iloc[0]

        # 선수 정보 조회
        player_info = players[players['pcode'] == pcode]
        hand_info = ""
        if not player_info.empty:
            p = player_info.iloc[0]
            phand = p.get('phand', '')
            stand = p.get('stand', '')
            if pd.notna(phand) and pd.notna(stand):
                hand_info = f"{phand}투{stand}타"

        index[pcode] = {
            "name": latest.get('player_name', 'Unknown'),
            "team": latest.get('team_name', 'Unknown'),
            "position": latest.get('primary_position_name', 'Unknown'),
            "hand": hand_info,
            "seasons": sorted(seasons)
        }

    return index


def build_pitcher_index(pitcher_kpi: pd.DataFrame, players: pd.DataFrame) -> dict:
    """투수 인덱스 생성"""
    index = {}

    # 선수별 시즌 그룹화
    pitcher_seasons = pitcher_kpi.groupby('pitcher_pcode')['season'].apply(list).to_dict()

    for pcode, seasons in pitcher_seasons.items():
        # 최신 시즌 데이터 가져오기
        latest = pitcher_kpi[
            (pitcher_kpi['pitcher_pcode'] == pcode) &
            (pitcher_kpi['season'] == max(seasons))
        ].iloc[0]

        # 선수 정보 조회
        player_info = players[players['pcode'] == pcode]
        hand_info = ""
        if not player_info.empty:
            p = player_info.iloc[0]
            phand = p.get('phand', '')
            stand = p.get('stand', '')
            if pd.notna(phand) and pd.notna(stand):
                hand_info = f"{phand}투{stand}타"

        index[pcode] = {
            "name": latest.get('player_name', 'Unknown'),
            "team": latest.get('team_name', 'Unknown'),
            "position": "투수",
            "hand": hand_info,
            "role": latest.get('pitcher_role', 'Unknown'),
            "seasons": sorted(seasons)
        }

    return index


def build_batter_kpi_data(batter_kpi: pd.DataFrame) -> dict:
    """타자 KPI 데이터 구성"""
    kpi_data = {}

    # 타자 메트릭 정의
    metric_definitions = {
        'contact': [
            ('batting_average', '타율', 0.45),
            ('strikeout_rate', '삼진율', 0.25),
            ('overall_contact_rate', '전체 컨택률', 0.08),
            ('in_zone_contact_rate', '존 내 컨택률', 0.07),
            ('chase_contact_rate', '체이스 컨택률', 0.05),
            ('two_strike_contact_rate', '2S 컨택률', 0.05),
            ('swing_miss_rate', '스윙 앤 미스율', 0.05),
        ],
        'game_power': [
            ('home_run_rate', '홈런율', 0.35),
            ('home_run_to_xbh_ratio', '홈런/장타 비율', 0.25),
            ('isolated_power_hr', '홈런 ISO', 0.20),
            ('home_run_per_hit_rate', '홈런/안타 비율', 0.20),
        ],
        'gap_power': [
            ('double_rate', '2루타율', 0.30),
            ('triple_rate', '3루타율', 0.15),
            ('isolated_power_gap', '갭 ISO', 0.25),
            ('gap_hit_rate', '갭 히트율', 0.15),
            ('double_to_single_ratio', '2루타/단타 비율', 0.15),
        ],
        'discipline': [
            ('walk_rate', '볼넷율', 0.35),
            ('chase_rate', '체이스율', 0.25),
            ('first_pitch_selectivity', '초구 선택력', 0.15),
            ('two_strike_approach', '2S 접근', 0.15),
            ('called_strike_rate', '루킹 스트라이크율', 0.10),
        ],
        'consistency': [
            ('monthly_variance', '월별 편차', 0.35),
            ('platoon_split_stability', '좌우 안정성', 0.25),
            ('count_balance', '카운트 균형', 0.20),
            ('inning_evenness', '이닝별 균일성', 0.20),
        ],
        'clutch': [
            ('high_leverage_performance', '높은 중요도 성과', 0.35),
            ('risp_woba', '득점권 wOBA', 0.30),
            ('close_game_performance', '접전 성적', 0.20),
            ('two_out_performance', '2아웃 성적', 0.15),
        ],
    }

    for season in batter_kpi['season'].unique():
        season_str = str(int(season))
        kpi_data[season_str] = {}

        season_df = batter_kpi[batter_kpi['season'] == season]

        for _, row in season_df.iterrows():
            pcode = row['batter_pcode']

            # 기본 정보
            player_data = {
                "overall_grade": safe_int(row.get('overall_grade')),
                "overall_grade_weighted": safe_int(row.get('overall_grade_weighted')),
                "category_scores": {
                    "contact": safe_int(row.get('contact_grade_weighted', row.get('contact_grade'))),
                    "game_power": safe_int(row.get('game_power_grade_weighted', row.get('game_power_grade'))),
                    "gap_power": safe_int(row.get('gap_power_grade_weighted', row.get('gap_power_grade'))),
                    "discipline": safe_int(row.get('discipline_grade_weighted', row.get('discipline_grade'))),
                    "consistency": safe_int(row.get('consistency_grade_weighted', row.get('consistency_grade'))),
                    "clutch": safe_int(row.get('clutch_grade_weighted', row.get('clutch_grade'))),
                },
                "traditional_stats": {
                    "batting_average": safe_float(row.get('batting_average'), 3),
                    "on_base_percentage": safe_float(row.get('on_base_percentage'), 3),
                    "slugging_percentage": safe_float(row.get('slugging_percentage'), 3),
                    "ops": safe_float(row.get('ops'), 3),
                    "home_runs": safe_int(row.get('home_runs')),
                    "rbis": safe_int(row.get('rbi')),
                    "plate_appearances": safe_int(row.get('plate_appearances')),
                },
                "metrics": {}
            }

            # 카테고리별 메트릭
            for category, metrics in metric_definitions.items():
                player_data["metrics"][category] = []
                for key, name, weight in metrics:
                    value = row.get(key)
                    grade = row.get(f'{key}_grade')

                    if pd.notna(value):
                        player_data["metrics"][category].append({
                            "key": key,
                            "name": name,
                            "value": safe_float(value, 3),
                            "grade": safe_int(grade),
                            "weight": weight
                        })

            kpi_data[season_str][pcode] = player_data

    return kpi_data


def build_pitcher_kpi_data(pitcher_kpi: pd.DataFrame) -> dict:
    """투수 KPI 데이터 구성"""
    kpi_data = {}

    # 투수 메트릭 정의
    metric_definitions = {
        'control': [
            ('first_pitch_strike_rate', '초구 스트라이크율', 0.25),
            ('three_ball_recovery_rate', '3볼 회복률', 0.20),
            ('walk_avoidance_rate', '볼넷 회피율', 0.20),
            ('main_pitch_control_rate', '주구종 제구율', 0.20),
            ('favorable_count_entry_rate', '유리한 카운트 진입률', 0.15),
        ],
        'aggression': [
            ('early_strike_rate', '조기 스트라이크 유도율', 0.30),
            ('finishing_ability_rate', '마무리 능력', 0.30),
            ('two_strike_strikeout_rate', '2스트라이크 삼진율', 0.25),
            ('high_velocity_decision_rate', '고속구 결정력', 0.15),
        ],
        'efficiency': [
            ('avg_pitches_per_batter', '타자당 평균 투구수', 0.25),
            ('quick_resolution_rate', '빠른 해결율', 0.25),
            ('first_batter_out_rate', '첫 타자 아웃률', 0.20),
            ('five_pitch_out_rate', '5구 이내 아웃률', 0.15),
            ('efficient_inning_rate', '효율적 이닝 비율', 0.15),
        ],
        'stuff': [
            ('whiff_rate', '헛스윙 유도율', 0.30),
            ('chase_rate', '체이스율', 0.20),
            ('in_zone_whiff_rate', '존내 헛스윙률', 0.20),
            ('unhittable_pitch_rate', '언히터블 피치율', 0.15),
            ('avg_fastball_velocity', '평균 구속', 0.15),
        ],
        'clutch': [
            ('risp_out_rate', '득점권 아웃률', 0.30),
            ('two_out_inning_end_rate', '2아웃 이닝 종료율', 0.25),
            ('bases_loaded_escape_rate', '만루 탈출률', 0.25),
            ('three_up_three_down_rate', '삼자범퇴 비율', 0.20),
        ],
    }

    for season in pitcher_kpi['season'].unique():
        season_str = str(int(season))
        kpi_data[season_str] = {}

        season_df = pitcher_kpi[pitcher_kpi['season'] == season]

        for _, row in season_df.iterrows():
            pcode = row['pitcher_pcode']

            # 기본 정보
            player_data = {
                "overall_grade": safe_int(row.get('overall_grade')),
                "pitcher_role": row.get('pitcher_role', 'Unknown'),
                "category_scores": {
                    "control": safe_int(row.get('control_grade')),
                    "aggression": safe_int(row.get('aggression_grade')),
                    "efficiency": safe_int(row.get('efficiency_grade')),
                    "stuff": safe_int(row.get('stuff_grade')),
                    "clutch": safe_int(row.get('clutch_grade')),
                },
                "traditional_stats": {
                    "total_games": safe_int(row.get('total_games')),
                    "total_pitches": safe_int(row.get('total_pitches')),
                    "total_innings_pitched": safe_float(row.get('total_innings_pitched'), 1),
                },
                "metrics": {}
            }

            # 카테고리별 메트릭
            for category, metrics in metric_definitions.items():
                player_data["metrics"][category] = []
                for key, name, weight in metrics:
                    value = row.get(key)
                    grade = row.get(f'{key}_grade')

                    if pd.notna(value):
                        player_data["metrics"][category].append({
                            "key": key,
                            "name": name,
                            "value": safe_float(value, 3),
                            "grade": safe_int(grade),
                            "weight": weight
                        })

            kpi_data[season_str][pcode] = player_data

    return kpi_data


def safe_col_mean(df, col_name):
    """안전하게 컬럼 평균 계산 (문자열 타입 처리)"""
    if col_name not in df.columns:
        return None
    try:
        return pd.to_numeric(df[col_name], errors='coerce').mean()
    except:
        return None


def build_team_comparison(batter_kpi: pd.DataFrame, pitcher_kpi: pd.DataFrame) -> dict:
    """팀 비교 데이터 구성"""
    comparison = {}

    for season in batter_kpi['season'].unique():
        season_str = str(int(season))
        comparison[season_str] = {"batters": {}, "pitchers": {}}

        # 타자 팀 비교
        batter_season = batter_kpi[batter_kpi['season'] == season]
        for team in batter_season['team_name'].dropna().unique():
            team_data = batter_season[batter_season['team_name'] == team]

            comparison[season_str]["batters"][team] = {
                "avg_overall": safe_float(safe_col_mean(team_data, 'overall_grade_weighted'), 1) or safe_float(safe_col_mean(team_data, 'overall_grade'), 1),
                "avg_contact": safe_float(safe_col_mean(team_data, 'contact_grade_weighted'), 1) or safe_float(safe_col_mean(team_data, 'contact_grade'), 1),
                "avg_game_power": safe_float(safe_col_mean(team_data, 'game_power_grade_weighted'), 1) or safe_float(safe_col_mean(team_data, 'game_power_grade'), 1),
                "avg_gap_power": safe_float(safe_col_mean(team_data, 'gap_power_grade_weighted'), 1) or safe_float(safe_col_mean(team_data, 'gap_power_grade'), 1),
                "avg_discipline": safe_float(safe_col_mean(team_data, 'discipline_grade_weighted'), 1) or safe_float(safe_col_mean(team_data, 'discipline_grade'), 1),
                "avg_clutch": safe_float(safe_col_mean(team_data, 'clutch_grade_weighted'), 1) or safe_float(safe_col_mean(team_data, 'clutch_grade'), 1),
                "player_count": len(team_data)
            }

        # 투수 팀 비교
        pitcher_season = pitcher_kpi[pitcher_kpi['season'] == season]
        for team in pitcher_season['team_name'].dropna().unique():
            team_data = pitcher_season[pitcher_season['team_name'] == team]

            comparison[season_str]["pitchers"][team] = {
                "avg_overall": safe_float(safe_col_mean(team_data, 'overall_grade'), 1),
                "avg_control": safe_float(safe_col_mean(team_data, 'control_grade'), 1),
                "avg_aggression": safe_float(safe_col_mean(team_data, 'aggression_grade'), 1),
                "avg_efficiency": safe_float(safe_col_mean(team_data, 'efficiency_grade'), 1),
                "avg_stuff": safe_float(safe_col_mean(team_data, 'stuff_grade'), 1),
                "avg_clutch": safe_float(safe_col_mean(team_data, 'clutch_grade'), 1),
                "player_count": len(team_data)
            }

    return comparison


def safe_nlargest(df, n, col_name, id_col):
    """안전하게 상위 n개 추출 (문자열 타입 처리)"""
    if col_name not in df.columns:
        return []
    try:
        df_copy = df.copy()
        df_copy[col_name] = pd.to_numeric(df_copy[col_name], errors='coerce')
        return df_copy.nlargest(n, col_name)[id_col].tolist()
    except:
        return []


def build_leaderboards(batter_kpi: pd.DataFrame, pitcher_kpi: pd.DataFrame) -> dict:
    """리더보드 데이터 구성"""
    leaderboards = {"batters": {}, "pitchers": {}}

    for season in batter_kpi['season'].unique():
        season_str = str(int(season))
        batter_season = batter_kpi[batter_kpi['season'] == season].copy()

        # 타자 리더보드
        leaderboards["batters"][season_str] = {
            "by_overall": safe_nlargest(batter_season, 100, 'overall_grade', 'batter_pcode'),
            "by_contact": safe_nlargest(batter_season, 100, 'contact_grade', 'batter_pcode'),
            "by_discipline": safe_nlargest(batter_season, 100, 'discipline_grade', 'batter_pcode'),
        }

    for season in pitcher_kpi['season'].unique():
        season_str = str(int(season))
        pitcher_season = pitcher_kpi[pitcher_kpi['season'] == season].copy()

        # 투수 리더보드
        leaderboards["pitchers"][season_str] = {
            "by_overall": safe_nlargest(pitcher_season, 100, 'overall_grade', 'pitcher_pcode'),
            "by_control": safe_nlargest(pitcher_season, 100, 'control_grade', 'pitcher_pcode'),
            "by_stuff": safe_nlargest(pitcher_season, 100, 'stuff_grade', 'pitcher_pcode'),
        }

    return leaderboards


def safe_float(value, decimals=3):
    """안전하게 float 변환"""
    if pd.isna(value):
        return None
    try:
        return round(float(value), decimals)
    except:
        return None


def safe_int(value):
    """안전하게 int 변환"""
    if pd.isna(value):
        return None
    try:
        return int(value)
    except:
        return None


def export_to_json(compress: bool = False):
    """JSON 파일로 내보내기"""

    # 데이터 로드
    batter_kpi, pitcher_kpi, players, teams = load_parquet_data()

    # 시즌 목록
    all_seasons = sorted(set(
        list(batter_kpi['season'].unique()) +
        list(pitcher_kpi['season'].unique())
    ))

    print("\nBuilding JSON structure...")

    # JSON 구조 생성
    data = {
        "metadata": {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "seasons": [int(s) for s in all_seasons],
            "data_period": "2021-04-03 ~ 2025-10-04"
        },
        "teams": TEAMS,
        "batters": {
            "index": build_batter_index(batter_kpi, players),
            "kpi": build_batter_kpi_data(batter_kpi)
        },
        "pitchers": {
            "index": build_pitcher_index(pitcher_kpi, players),
            "kpi": build_pitcher_kpi_data(pitcher_kpi)
        },
        "team_comparison": build_team_comparison(batter_kpi, pitcher_kpi),
        "leaderboards": build_leaderboards(batter_kpi, pitcher_kpi)
    }

    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(exist_ok=True)

    # JSON 저장
    if compress:
        output_path = OUTPUT_DIR / "kbo_scouting_data.json.gz"
        print(f"\nSaving compressed JSON to {output_path}...")
        with gzip.open(output_path, 'wt', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    else:
        output_path = OUTPUT_DIR / "kbo_scouting_data.json"
        print(f"\nSaving JSON to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 축소 버전도 생성
    output_min_path = OUTPUT_DIR / "kbo_scouting_data.min.json"
    print(f"Saving minified JSON to {output_min_path}...")
    with open(output_min_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    # 파일 크기 출력
    if compress:
        size = output_path.stat().st_size / 1024 / 1024
        print(f"\nCompressed size: {size:.2f} MB")
    else:
        size = output_path.stat().st_size / 1024 / 1024
        print(f"\nFull JSON size: {size:.2f} MB")

    min_size = output_min_path.stat().st_size / 1024 / 1024
    print(f"Minified JSON size: {min_size:.2f} MB")

    # 통계 출력
    print(f"\n=== Export Statistics ===")
    print(f"Batters: {len(data['batters']['index'])} players")
    print(f"Pitchers: {len(data['pitchers']['index'])} players")
    print(f"Seasons: {data['metadata']['seasons']}")
    print(f"Teams: {len(data['teams'])}")

    print(f"\nExport completed successfully!")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export KBO scouting data to JSON")
    parser.add_argument("--compress", action="store_true", help="Compress output with gzip")
    args = parser.parse_args()

    export_to_json(compress=args.compress)
