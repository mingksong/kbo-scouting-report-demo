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
