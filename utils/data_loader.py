"""
데이터 로딩 유틸리티
"""

import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

@st.cache_data
def load_batter_kpi():
    """타자 KPI 데이터 로드"""
    return pd.read_parquet(DATA_DIR / "batter_kpi.parquet")

@st.cache_data
def load_pitcher_kpi():
    """투수 KPI 데이터 로드"""
    return pd.read_parquet(DATA_DIR / "pitcher_kpi.parquet")

@st.cache_data
def load_players():
    """선수 정보 로드"""
    return pd.read_parquet(DATA_DIR / "players.parquet")

@st.cache_data
def load_teams():
    """팀 정보 로드"""
    return pd.read_parquet(DATA_DIR / "teams.parquet")

def get_batter_list(season: int):
    """특정 시즌의 타자 목록"""
    df = load_batter_kpi()
    batters = df[df['season'] == season][['batter_pcode', 'player_name', 'team_name']].drop_duplicates()
    return batters.sort_values('player_name')

def get_pitcher_list(season: int):
    """특정 시즌의 투수 목록"""
    df = load_pitcher_kpi()
    pitchers = df[df['season'] == season][['pitcher_pcode', 'player_name', 'team_name']].drop_duplicates()
    return pitchers.sort_values('player_name')

def search_batters(season: int, query: str):
    """타자 검색 (2글자 이상)"""
    if len(query) < 2:
        return pd.DataFrame()

    df = load_batter_kpi()
    players = load_players()

    # 시즌 필터링
    batters = df[df['season'] == season][['batter_pcode', 'player_name', 'team_name']].drop_duplicates()

    # 이름 검색
    results = batters[batters['player_name'].str.contains(query, na=False)]

    # 선수 정보(투타) 조인
    results = results.merge(
        players[['pcode', 'phand', 'stand']],
        left_on='batter_pcode',
        right_on='pcode',
        how='left'
    )

    # 투타 정보로 표시 이름 생성 (동명이인 구분)
    def make_display_name(row):
        name = row['player_name']
        phand = row.get('phand', '')
        stand = row.get('stand', '')

        if pd.notna(phand) and pd.notna(stand):
            hand_info = f"{phand}투{stand}타"
            return f"{name} ({hand_info})"
        return name

    results['display_name'] = results.apply(make_display_name, axis=1)

    return results.sort_values('player_name')

def search_pitchers(season: int, query: str):
    """투수 검색 (2글자 이상)"""
    if len(query) < 2:
        return pd.DataFrame()

    df = load_pitcher_kpi()
    players = load_players()

    # 시즌 필터링
    pitchers = df[df['season'] == season][['pitcher_pcode', 'player_name', 'team_name']].drop_duplicates()

    # 이름 검색
    results = pitchers[pitchers['player_name'].str.contains(query, na=False)]

    # 선수 정보(투타) 조인
    results = results.merge(
        players[['pcode', 'phand', 'stand']],
        left_on='pitcher_pcode',
        right_on='pcode',
        how='left'
    )

    # 투타 정보로 표시 이름 생성 (동명이인 구분)
    def make_display_name(row):
        name = row['player_name']
        phand = row.get('phand', '')
        stand = row.get('stand', '')

        if pd.notna(phand) and pd.notna(stand):
            hand_info = f"{phand}투{stand}타"
            return f"{name} ({hand_info})"
        return name

    results['display_name'] = results.apply(make_display_name, axis=1)

    return results.sort_values('player_name')

def get_batter_data(batter_pcode: str, season: int):
    """특정 타자의 KPI 데이터"""
    df = load_batter_kpi()
    data = df[(df['batter_pcode'] == batter_pcode) & (df['season'] == season)]
    if len(data) == 0:
        return None
    return data.iloc[0]

def get_pitcher_data(pitcher_pcode: str, season: int):
    """특정 투수의 KPI 데이터"""
    df = load_pitcher_kpi()
    data = df[(df['pitcher_pcode'] == pitcher_pcode) & (df['season'] == season)]
    if len(data) == 0:
        return None
    return data.iloc[0]

# 팀 색상 매핑
TEAM_COLORS = {
    'KIA': '#EA0029',
    'SSG': '#CE0E2D',
    'LG': '#C30452',
    'KT': '#000000',
    'NC': '#315288',
    '두산': '#131230',
    '삼성': '#074CA1',
    '롯데': '#041E42',
    '한화': '#FF6600',
    '키움': '#570514'
}

def get_team_color(team_name: str) -> str:
    """팀 색상 반환"""
    return TEAM_COLORS.get(team_name, '#6B7280')
