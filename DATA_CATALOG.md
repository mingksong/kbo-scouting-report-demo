# KBO Scouting Report - Data Catalog for Mobile UI

## Overview

이 문서는 KBO 스카우팅 리포트 데모 앱의 데이터 구조를 정의하고, AI-Stitch를 활용한 모바일 UI 생성을 위한 프롬프트 가이드를 제공합니다.

---

## 1. Mobile UI Prompt for AI-Stitch

### 1.1 App Concept

```
KBO 프로야구 선수 스카우팅 리포트 모바일 앱

핵심 기능:
- 타자/투수 검색 및 상세 리포트 조회
- 6각형 레이더 차트로 능력치 시각화
- 카테고리별 상세 지표 및 등급 표시
- 시즌별 성적 추이 그래프

디자인 컨셉:
- 스포츠 앱 특유의 다이나믹하고 깔끔한 UI
- 다크/라이트 모드 지원
- 카드 기반 레이아웃
- 색상 코딩된 등급 시스템 (20-80 스케일)
```

### 1.2 Screen Flow

```
[홈 화면]
    ├── [검색 바] → 선수 이름 입력 (2글자 이상)
    ├── [시즌 선택] → 2021-2025
    ├── [타자/투수 탭]
    └── [최근 조회 선수 목록]

[선수 상세 화면]
    ├── [헤더] → 선수 정보 + OVR 등급
    ├── [탭 1: 종합]
    │   ├── 레이더 차트
    │   ├── 카테고리별 점수
    │   ├── 시즌 성적
    │   └── 강점/약점
    ├── [탭 2: 상세 지표]
    │   └── 카테고리별 카드 (접기/펼치기)
    └── [탭 3: 분석/비교]
        ├── 시즌별 추이 그래프
        └── 리그 내 백분위 순위
```

### 1.3 UI Component Specifications

#### Grade Badge Component
```
등급 뱃지 색상 시스템:
- 80+ (엘리트): #9333EA (purple)
- 70-79 (플러스): #2563EB (blue)
- 60-69 (평균 이상): #16A34A (green)
- 50-59 (평균): #CA8A04 (yellow)
- 40-49 (평균 이하): #EA580C (orange)
- 20-39 (부족): #DC2626 (red)
```

#### Weight Badge Component
```
가중치 색상 (W-XX%):
- 35%+ (매우 중요): #DC2626 (red)
- 25-34% (중요): #EA580C (orange)
- 15-24% (보통): #2563EB (blue)
- 10-14% (낮음): #6B7280 (gray)
- <10% (매우 낮음): #9CA3AF (light gray)
```

#### Radar Chart
```
타자: 6각형 (컨택, 홈런 파워, 갭 파워, 선구안, 일관성, 클러치)
투수: 5각형 (제구력, 공격성, 효율성, 구위, 클러치)
범위: 20-80
색상: 타자 #3B82F6 (blue), 투수 #EF4444 (red)
```

---

## 2. Data Structure

### 2.1 Entity Relationship

```
┌─────────────────┐
│    Players      │
│  (선수 정보)     │
├─────────────────┤
│ pcode (PK)      │
│ name            │
│ team_name       │
│ position        │
│ phand (투구손)   │
│ stand (타격손)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Batter  │ │ Pitcher │
│   KPI   │ │   KPI   │
├─────────┤ ├─────────┤
│ 242 cols│ │ 172 cols│
│ 983 rows│ │1445 rows│
└─────────┘ └─────────┘
```

### 2.2 Data Volume

| Dataset | Columns | Rows | Size | Seasons |
|---------|---------|------|------|---------|
| Batter KPI | 242 | 983 | 0.57 MB | 2021-2025 |
| Pitcher KPI | 172 | 1,445 | 0.37 MB | 2021-2025 |
| Players | 9 | ~500 | 0.03 MB | - |

---

## 3. Batter Data Schema

### 3.1 Identification & Basic Info

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `batter_pcode` | int | 선수 고유 ID | 76290 |
| `player_name` | string | 선수 이름 | "김현수" |
| `team_name` | string | 소속팀 | "LG" |
| `season` | int | 시즌 연도 | 2024 |
| `batter_type` | string | 타자 유형 | "갭히터형" |

### 3.2 Overall & Category Grades (20-80 Scale)

| Field | Description | Mobile Display |
|-------|-------------|----------------|
| `overall_grade` | 종합 등급 (비가중치) | 헤더 OVR |
| `overall_grade_weighted` | 종합 등급 (가중치) | 헤더 OVR (우선) |
| `contact_grade_weighted` | 컨택 등급 | 레이더 차트 |
| `game_power_grade_weighted` | 홈런 파워 등급 | 레이더 차트 |
| `gap_power_grade_weighted` | 갭 파워 등급 | 레이더 차트 |
| `discipline_grade_weighted` | 선구안 등급 | 레이더 차트 |
| `consistency_grade_weighted` | 일관성 등급 | 레이더 차트 |
| `clutch_grade_weighted` | 클러치 등급 | 레이더 차트 |

### 3.3 Traditional Stats

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `batting_average` | float | 0-1 | 타율 (.296) |
| `on_base_percentage` | float | 0-1 | 출루율 (.375) |
| `slugging_percentage` | float | 0-1 | 장타율 (.430) |
| `ops` | float | 0-2 | OPS (.805) |
| `home_runs` | int | count | 홈런 수 |
| `rbis` | int | count | 타점 |
| `stolen_bases` | int | count | 도루 |
| `hits` | int | count | 안타 |
| `walks` | int | count | 볼넷 |
| `strikeouts` | int | count | 삼진 |

### 3.4 Category Metrics Detail

#### Contact (컨택)
| Field | Name | Weight | Unit | Data Format |
|-------|------|--------|------|-------------|
| `batting_average` | 타율 | 45% | - | 0-1 ratio |
| `strikeout_rate` | 삼진율 | 25% | % | 0-100 (already %) |
| `overall_contact_rate` | 전체 컨택률 | 8% | % | 0-100 |
| `two_strike_contact_rate` | 2스트라이크 컨택률 | 10% | % | 0-100 |
| `in_zone_contact_rate` | 존내 컨택률 | 7% | % | 0-100 |
| `foul_ball_rate` | 파울볼률 | 5% | % | 0-100 |

#### Game Power (홈런 파워)
| Field | Name | Weight | Unit | Data Format |
|-------|------|--------|------|-------------|
| `home_run_rate` | 홈런율 | 35% | % | 0-100 |
| `home_run_to_xbh_ratio` | 홈런/장타 비율 | 25% | % | 0-1 (×100 필요) |
| `isolated_power_hr` | ISO (홈런) | 25% | - | 0-1 ratio |
| `home_run_per_hit_rate` | 홈런/안타 비율 | 15% | % | 0-100 |

#### Gap Power (갭 파워)
| Field | Name | Weight | Unit | Data Format |
|-------|------|--------|------|-------------|
| `double_rate` | 2루타율 | 30% | % | 0-100 |
| `triple_rate` | 3루타율 | 5% | % | 0-100 |
| `isolated_power_gap` | ISO (갭) | 30% | - | 0-1 ratio |
| `gap_hit_rate` | 갭 히트율 | 20% | % | 0-100 |
| `double_to_single_ratio` | 2루타/1루타 비율 | 15% | - | ratio |

#### Discipline (선구안)
| Field | Name | Weight | Unit | Data Format |
|-------|------|--------|------|-------------|
| `walk_rate` | 볼넷율 | 35% | % | 0-100 |
| `chase_rate` | 체이스율 | 25% | % | 0-100 |
| `zone_swing_rate` | 존 스윙률 | 30% | % | 0-100 |
| `first_pitch_swing_rate` | 초구 스윙률 | 8% | % | 0-100 |
| `three_zero_discipline` | 3-0 규율 | 2% | % | 0-100 |

#### Consistency (일관성)
| Field | Name | Weight | Unit | Data Format |
|-------|------|--------|------|-------------|
| `monthly_variance` | 월별 분산 | 35% | - | decimal |
| `left_right_ops_diff` | 좌우 OPS 차이 | 30% | - | decimal |
| `fastball_contact_rate` | 직구 컨택률 | 15% | % | 0-100 |
| `breaking_contact_rate` | 변화구 컨택률 | 10% | % | 0-100 |
| `offspeed_contact_rate` | 체인지업 컨택률 | 10% | % | 0-100 |

#### Clutch (클러치)
| Field | Name | Weight | Unit | Data Format |
|-------|------|--------|------|-------------|
| `high_leverage_performance` | 고레버리지 성적 | 30% | - | 0-1 ratio |
| `risp_average` | 득점권 타율 | 25% | - | 0-1 ratio |
| `two_out_rbi_rate` | 2아웃 타점율 | 20% | % | 0-100 |
| `late_close_performance` | 후반 접전 성적 | 20% | - | 0-1 ratio |
| `bases_loaded_average` | 만루 타율 | 5% | - | 0-1 ratio |

### 3.5 Percentile Rankings

모든 주요 지표에 `_percentile` suffix가 붙은 0-100 백분위 값이 존재합니다.
예: `batting_average_percentile`, `home_run_rate_percentile`

---

## 4. Pitcher Data Schema

### 4.1 Identification & Basic Info

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `pitcher_pcode` | int | 선수 고유 ID | 64649 |
| `player_name` | string | 선수 이름 | "고우석" |
| `team_name` | string | 소속팀 | "LG" |
| `season` | int | 시즌 연도 | 2024 |
| `role_type` | string | 역할 | "마무리" |

### 4.2 Overall & Category Grades (20-80 Scale)

| Field | Description |
|-------|-------------|
| `overall_grade` | 종합 등급 |
| `control_grade` | 제구력 등급 |
| `aggression_grade` | 공격성 등급 |
| `efficiency_grade` | 효율성 등급 |
| `stuff_grade` | 구위 등급 |
| `clutch_grade` | 클러치 등급 |

### 4.3 Category Metrics Detail

#### Control (제구력)
| Field | Name | Weight | Unit |
|-------|------|--------|------|
| `first_pitch_strike_rate` | 초구 스트라이크율 | 25% | % (0-1) |
| `walk_avoidance_rate` | 볼넷 회피율 | 25% | % (0-1) |
| `three_ball_recovery_rate` | 3볼 회복률 | 20% | % (0-1) |
| `favorable_count_entry_rate` | 유리한 카운트 진입률 | 15% | % (0-1) |
| `main_pitch_control_rate` | 주구종 제구율 | 15% | % (0-1) |

#### Aggression (공격성)
| Field | Name | Weight | Unit |
|-------|------|--------|------|
| `two_strike_strikeout_rate` | 2스트라이크 삼진율 | 35% | % (0-1) |
| `early_strike_rate` | 초반 스트라이크율 | 25% | % (0-1) |
| `finishing_ability_rate` | 마무리 능력 | 25% | % (0-1) |
| `high_velocity_decision_rate` | 고속구 결정률 | 15% | % (0-1) |

#### Efficiency (효율성)
| Field | Name | Weight | Unit |
|-------|------|--------|------|
| `avg_pitches_per_batter` | 타자당 평균 투구수 | 40% | count |
| `count_efficiency_index` | 카운트 효율 지수 | 30% | index |
| `full_count_avoidance_rate` | 풀카운트 회피율 | 30% | % (0-1) |

#### Stuff (구위)
| Field | Name | Weight | Unit |
|-------|------|--------|------|
| `whiff_rate` | 헛스윙 유도율 | 30% | % (0-1) |
| `chase_rate` | 체이스율 | 25% | % (0-1) |
| `in_zone_whiff_rate` | 존내 헛스윙률 | 20% | % (0-1) |
| `unhittable_pitch_rate` | 언히터블 피치율 | 15% | % (0-1) |
| `avg_fastball_velocity` | 평균 패스트볼 구속 | 10% | km/h |

#### Clutch (클러치)
| Field | Name | Weight | Unit |
|-------|------|--------|------|
| `risp_out_rate` | 득점권 아웃률 | 25% | % (0-1) |
| `bases_loaded_escape_rate` | 만루 탈출률 | 20% | % (0-1) |
| `two_out_inning_end_rate` | 2아웃 이닝 종료율 | 20% | % (0-1) |
| `first_batter_out_rate` | 첫 타자 아웃률 | 20% | % (0-1) |
| `close_game_prevention_rate` | 접전 실점 방지율 | 10% | % (0-1) |
| `momentum_protection_rate` | 모멘텀 보호율 | 5% | % (0-1) |

---

## 5. Batter Type Classification

| Code | Korean | Description |
|------|--------|-------------|
| `FIVE_TOOL_PLAYER` | 5툴 플레이어 | 모든 능력치가 균형잡힌 올라운드 플레이어 |
| `COMPLETE_SLUGGER` | 완성형 슬러거 | 홈런과 갭 파워를 모두 갖춘 완성형 타자 |
| `HOME_RUN_KING` | 홈런왕 | 압도적인 홈런 파워를 보여주는 타자 |
| `SLUGGER` | 슬러거 | 강력한 파워와 준수한 컨택을 겸비한 중심 타자 |
| `CONTACT_MASTER` | 정교한 타격형 | 뛰어난 컨택과 선구안으로 출루를 책임지는 타자 |
| `TABLE_SETTER` | 테이블세터 | 탁월한 선구안과 컨택으로 득점 기회를 만드는 리드오프 |
| `BALANCED_POWER` | 균형 파워 | 홈런과 갭 파워가 균형을 이루는 타자 |
| `POWER_HITTER` | 파워 히터 | 장타력 중심의 공격적인 타자 |
| `FREE_SWINGER` | 프리스윙어 | 파워는 있지만 선구안이 부족한 공격적 타자 |
| `LINE_DRIVE_MACHINE` | 라인드라이브 머신 | 컨택과 갭 파워를 같이 갖춘 타자 |
| `CONTACT_SPECIALIST` | 컨택 스페셜리스트 | 높은 타율, 낮은 파워 |
| `PATIENT_HITTER` | 인내형 타자 | 볼넷 전문 선구안 특화 타자 |
| `CLUTCH_PERFORMER` | 클러치 히터 | 중요한 순간에 강한 타자 |
| `AVERAGE_HITTER` | 평균적인 타자 | 리그 평균 수준의 능력을 보유한 타자 |

---

## 6. Mobile UI Implementation Notes

### 6.1 Key UX Considerations

1. **검색 우선**: 홈 화면에서 즉시 검색 가능
2. **빠른 비교**: 좌우 스와이프로 카테고리 전환
3. **직관적 시각화**: 레이더 차트 + 색상 등급으로 즉시 파악
4. **오프라인 지원**: Parquet 데이터 (~1MB)는 로컬 캐싱 가능

### 6.2 Recommended Component Library

- **Chart**: `react-native-chart-kit` or `victory-native` for radar charts
- **Card**: Expandable/collapsible cards for metric categories
- **Badge**: Custom grade badges with color coding
- **Progress**: Horizontal progress bars for percentile rankings

### 6.3 Data Loading Strategy

```javascript
// 데이터 로딩 순서
1. 선수 기본 정보 (즉시)
2. 카테고리 등급 (레이더 차트)
3. 전통 지표 (요약)
4. 상세 지표 (탭 전환 시 lazy load)
```

### 6.4 Accessibility

- 등급 색상에 추가 텍스트 레이블 (색맹 대응)
- 차트에 대체 텍스트 제공
- 최소 터치 영역 44x44pt

---

## 7. API Endpoints (Reference)

현재 서비스는 Parquet 파일 기반이지만, 향후 API 구현 시 참고:

```
GET /api/batters/search?q={name}&season={year}
GET /api/batters/{pcode}?season={year}
GET /api/pitchers/search?q={name}&season={year}
GET /api/pitchers/{pcode}?season={year}
```

---

## 8. Sample Data for Testing

### Batter Sample (김현수, 2024)
```json
{
  "batter_pcode": 76290,
  "player_name": "김현수",
  "team_name": "LG",
  "season": 2024,
  "batter_type": "갭히터형",
  "overall_grade_weighted": 65,
  "category_grades": {
    "contact": 63,
    "game_power": 42,
    "gap_power": 72,
    "discipline": 45,
    "consistency": 55,
    "clutch": 50
  },
  "traditional_stats": {
    "batting_average": 0.296,
    "on_base_percentage": 0.375,
    "slugging_percentage": 0.430,
    "ops": 0.805,
    "home_runs": 10
  }
}
```

### Pitcher Sample (고우석, 2024)
```json
{
  "pitcher_pcode": 64649,
  "player_name": "고우석",
  "team_name": "LG",
  "season": 2024,
  "role_type": "마무리",
  "overall_grade": 68,
  "category_grades": {
    "control": 65,
    "aggression": 72,
    "efficiency": 60,
    "stuff": 70,
    "clutch": 68
  }
}
```

---

## Document Info

- **Created**: 2024-11-20
- **Version**: 1.0
- **Purpose**: AI-Stitch Mobile UI Generation
- **Data Source**: KBO Migration V2 Database (2021-2025)
