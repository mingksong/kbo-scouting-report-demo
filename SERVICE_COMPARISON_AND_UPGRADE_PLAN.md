# KBO 스카우팅 리포트: 원본 서비스 vs 데모 앱 비교 및 업그레이드 계획

## 📊 현재 상태 요약

### 원본 서비스 (localhost:13002)
- **프론트엔드**: React + TypeScript + Vite
- **백엔드 API**: FastAPI (포트 19000)
- **데이터베이스**: PostgreSQL (kbo_migration_v2)
- **캐싱**: Redis

### 데모 앱 (Streamlit Cloud)
- **프레임워크**: Streamlit
- **데이터**: Parquet 파일 (~1MB)
- **호스팅**: Streamlit Cloud

---

## 🔍 기능 비교 매트릭스

### 타자 스카우팅 리포트 (Batters)

| 기능 | 원본 서비스 | 데모 앱 | 차이점 |
|------|------------|---------|--------|
| **개인 리포트** | ✅ 전체 구현 | ✅ 기본 구현 | 원본: 7카테고리(주루 포함), 데모: 6카테고리 |
| **레이더 차트** | ✅ 6-sided | ✅ 6-sided | 동일 |
| **리더보드** | ✅ 필터/정렬/페이지네이션 | ❌ 미구현 | 원본: 상세한 필터링 기능 |
| **팀 비교** | ✅ 레이더 차트 + 역할 분류 | ❌ 미구현 | 원본: 8가지 역할 분류 |
| **포지션 분석** | ✅ 히트맵/희소성/탑플레이어 | ❌ 미구현 | 원본: 3가지 분석 뷰 |
| **시즌 추이** | ✅ 차트 | ✅ 기본 표 | 원본: 인터랙티브 차트 |
| **선수 검색** | ✅ 실시간 검색 | ✅ 동명이인 구분 | 동일 수준 |

### 투수 스카우팅 리포트 (Pitchers)

| 기능 | 원본 서비스 | 데모 앱 | 차이점 |
|------|------------|---------|--------|
| **개인 리포트** | ✅ 85개 지표 | ✅ 기본 구현 | 원본: 5카테고리 상세 메트릭 |
| **레이더 차트** | ✅ 5-sided | ✅ 5-sided | 동일 |
| **리더보드** | ✅ 역할별 필터 | ❌ 미구현 | 원본: 선발/구원 분리 |
| **팀 비교** | ✅ 투수진 분석 | ❌ 미구현 | 원본: 역할별 인원 분포 |
| **역할 분석** | ✅ 5가지 역할 분류 | ❌ 미구현 | Ace/Starter/Closer/Setup/Middle/Long |
| **상세 메트릭** | ✅ 카테고리별 세부 지표 | ✅ 가중치 표시 | 원본: 샘플 사이즈 포함 |

---

## 🏗️ 원본 서비스 상세 구조

### React 컴포넌트 구조

```
frontend/src/pages/v2/scouting-report/
├── batters/
│   ├── BatterScoutingReport.tsx (메인 라우터)
│   │   └── Routes: comprehensive, individual, leaderboard,
│   │               team-comparison, position-analysis, position-view
│   ├── ComprehensiveReport.tsx (개인 상세 리포트)
│   ├── BatterList.tsx (리더보드)
│   ├── TeamComparison.tsx (팀 비교 - 8가지 역할 분류)
│   │   └── Roles: regular, platoon, backup, fringe,
│   │              prospect, veteran, minor, rookie
│   ├── PositionAnalysis.tsx (포지션 분석)
│   └── components/
│       ├── PositionHeatmap.tsx
│       ├── PositionScarcity.tsx
│       └── TopPlayerCards.tsx
│
└── pitchers/
    ├── PitcherScoutingReport.tsx (메인 라우터)
    │   └── Routes: comprehensive, leaderboard, team-comparison, role-analysis
    ├── ComprehensiveReport.tsx (개인 상세 리포트)
    ├── LeaderboardView.tsx (리더보드)
    ├── TeamComparison.tsx (팀 비교)
    └── RoleAnalysis.tsx (역할 분석)
        └── Roles: starter, closer, setup, middle, long
```

### API 엔드포인트 (포트 19000)

#### 타자 API (`/api/kpi/v2/`)
```
GET /scouting-report/batter/{batter_id}?season={season}
    → BatterScoutingResponse (개인 리포트)

GET /batters?season={season}&team={team}&position={position}
         &min_pa={min_pa}&sort_by={sort}&order={order}&page={page}&limit={limit}
    → BattersListResponse (리더보드)

GET /batters/by-team/{team_code}?season={season}
    → 팀별 타자 목록

GET /batters/stats?season={season}&metric={metric}
    → 리그 통계

GET /batters/team-comparison?season={season}
    → 팀별 비교 데이터

GET /positions/heatmap?season={season}&min_pa={min_pa}
    → 포지션별 히트맵 데이터

GET /positions/scarcity?season={season}&min_pa={min_pa}
    → 포지션 희소성 분석

GET /positions/top-players?season={season}&min_pa={min_pa}&top_n={top_n}
    → 포지션별 탑 플레이어
```

#### 투수 API (`/api/kpi/v2/` 및 `/api/pitch-count/`)
```
GET /metrics/{pitcher_id}?season={season}
    → 85개 전체 메트릭

GET /scouting-report/{pitcher_id}?season={season}
    → 스카우팅 리포트 (분석 텍스트 포함)

GET /kpi-leaderboard/all-pitchers?season={season}&min_pitches={min}
    &team={team}&role_filter={role}&sort_by={sort}&sort_order={order}
    → 전체 투수 리더보드

GET /kpi-leaderboard/top-performers?season={season}&category={cat}&limit={n}
    → 카테고리별 상위 투수

GET /leaderboard/by-role?season={season}&role_type={role}
    &team={team}&min_games={min}&sort_by={sort}&sort_order={order}
    → 역할별 리더보드
```

---

## 📦 JSON 단일 파일 구조 설계

모바일 앱 개발을 위한 오프라인 데이터 구조:

```json
{
  "metadata": {
    "version": "1.0.0",
    "generated_at": "2025-11-22T00:00:00Z",
    "seasons": [2021, 2022, 2023, 2024, 2025],
    "data_period": "2021-04-03 ~ 2025-10-04"
  },

  "teams": {
    "KIA": {"name": "KIA 타이거즈", "color": "#EA0029", "short": "KIA"},
    "SSG": {"name": "SSG 랜더스", "color": "#CE0E2D", "short": "SSG"},
    // ... 10개 팀
  },

  "batters": {
    "index": {
      // pcode → 선수 정보 매핑
      "67629": {
        "name": "디아즈",
        "team": "키움",
        "position": "1루수",
        "hand": "우투우타",
        "seasons": [2025]
      }
    },
    "kpi": {
      // season → pcode → KPI 데이터
      "2025": {
        "67629": {
          "overall_grade": 72,
          "overall_grade_weighted": 70,
          "category_scores": {
            "contact": 65,
            "game_power": 78,
            "gap_power": 55,
            "discipline": 62,
            "baserunning": 45,
            "consistency": 58,
            "clutch": 68
          },
          "traditional_stats": {
            "batting_average": 0.312,
            "ops": 0.945,
            "home_runs": 28,
            "rbis": 95,
            "plate_appearances": 520
          },
          "metrics": {
            "contact": [
              {"key": "batting_average", "value": 0.312, "grade": 65, "weight": 0.45},
              {"key": "strikeout_rate", "value": 18.5, "grade": 58, "weight": 0.25}
              // ...
            ],
            "game_power": [...],
            "gap_power": [...],
            "discipline": [...],
            "baserunning": [...],
            "consistency": [...],
            "clutch": [...]
          }
        }
      }
    }
  },

  "pitchers": {
    "index": {
      "52001": {
        "name": "소형준",
        "team": "삼성",
        "position": "투수",
        "hand": "우투우타",
        "role": "Starter",
        "seasons": [2024, 2025]
      }
    },
    "kpi": {
      "2025": {
        "52001": {
          "overall_grade": 68,
          "pitcher_role": "Starter",
          "category_scores": {
            "control": 72,
            "aggression": 65,
            "efficiency": 58,
            "stuff": 70,
            "clutch": 62
          },
          "traditional_stats": {
            "era": 3.45,
            "wins": 12,
            "losses": 6,
            "innings_pitched": 165.2,
            "strikeouts": 142
          },
          "metrics": {
            "control": [...],
            "aggression": [...],
            "efficiency": [...],
            "stuff": [...],
            "clutch": [...]
          }
        }
      }
    }
  },

  "team_comparison": {
    "2025": {
      "batters": {
        "KIA": {
          "avg_overall": 58.5,
          "avg_contact": 62.3,
          "avg_game_power": 55.1,
          "avg_gap_power": 54.8,
          "avg_discipline": 57.2,
          "avg_clutch": 56.9,
          "role_distribution": {
            "regular": 8,
            "platoon": 4,
            "backup": 3,
            "fringe": 2
          }
        }
        // ... 10개 팀
      },
      "pitchers": {
        "KIA": {
          "avg_overall": 55.2,
          "avg_control": 58.1,
          "avg_aggression": 54.3,
          "avg_efficiency": 52.8,
          "avg_stuff": 56.9,
          "role_distribution": {
            "starter": 5,
            "closer": 1,
            "setup": 2,
            "middle": 4,
            "long": 3
          }
        }
      }
    }
  },

  "position_analysis": {
    "2025": {
      "heatmap": {
        "포수": {"overall": 52.3, "contact": 48.5, "game_power": 55.2, ...},
        "1루수": {"overall": 58.7, "contact": 55.1, "game_power": 65.3, ...},
        // ... 9개 포지션
      },
      "scarcity": {
        "포수": {"total": 15, "elite": 2, "quality": 5, "scarcity_index": 18.5},
        "유격수": {"total": 12, "elite": 1, "quality": 3, "scarcity_index": 12.3},
        // ...
      },
      "top_players": {
        "포수": [
          {"pcode": "12345", "name": "강민호", "team": "삼성", "overall": 72},
          // top 3
        ],
        // ... 9개 포지션
      }
    }
  },

  "leaderboards": {
    "batters": {
      "2025": {
        "by_overall": ["67629", "12345", "54321", ...],  // pcode 순서
        "by_contact": [...],
        "by_power": [...],
        "by_discipline": [...]
      }
    },
    "pitchers": {
      "2025": {
        "by_overall": [...],
        "by_control": [...],
        "by_stuff": [...],
        "starters": [...],
        "relievers": [...]
      }
    }
  }
}
```

---

## 🚀 업그레이드 계획

### Phase 1: 리더보드 추가 (우선순위: 높음)
**예상 소요: 1일**

1. **타자 리더보드** (`3_Batter_Leaderboard.py`)
   - 정렬 옵션: OVR, Contact, Power, Discipline 등
   - 필터: 시즌, 팀, 포지션, 최소 타석
   - 페이지네이션

2. **투수 리더보드** (`4_Pitcher_Leaderboard.py`)
   - 정렬 옵션: OVR, Control, Stuff, Efficiency 등
   - 필터: 시즌, 팀, 역할(선발/구원)

### Phase 2: 팀 비교 기능 (우선순위: 중간)
**예상 소요: 1.5일**

1. **타자 팀 비교** (`5_Team_Comparison_Batters.py`)
   - 10개 팀 레이더 차트 비교
   - 역할별 인원 분포

2. **투수 팀 비교** (`6_Team_Comparison_Pitchers.py`)
   - 투수진 능력 비교
   - 선발/불펜 분포

### Phase 3: 포지션/역할 분석 (우선순위: 낮음)
**예상 소요: 2일**

1. **포지션 분석** (`7_Position_Analysis.py`)
   - 포지션별 히트맵
   - 희소성 분석
   - 포지션별 탑 3

2. **투수 역할 분석** (`8_Pitcher_Role_Analysis.py`)
   - 역할별 평균 능력치
   - 역할 분포

### Phase 4: JSON 데이터 내보내기 (우선순위: 높음)
**예상 소요: 0.5일**

1. **데이터 추출 스크립트** (`export_all_data.py`)
   - PostgreSQL → JSON 변환
   - 압축 옵션 (gzip)

2. **JSON 파일 생성**
   - `kbo_scouting_data.json` (~5-10MB)
   - `kbo_scouting_data.min.json` (~2-3MB, minified)

---

## 📱 모바일 앱 데이터 활용 가이드

### JSON 로드 예시 (Kotlin/Android)
```kotlin
data class KBOScoutingData(
    val metadata: Metadata,
    val teams: Map<String, Team>,
    val batters: BatterData,
    val pitchers: PitcherData,
    val teamComparison: Map<String, TeamComparisonData>,
    val positionAnalysis: Map<String, PositionData>,
    val leaderboards: LeaderboardData
)

// 로드 및 캐싱
val data = Gson().fromJson(jsonString, KBOScoutingData::class.java)
```

### JSON 로드 예시 (Swift/iOS)
```swift
struct KBOScoutingData: Codable {
    let metadata: Metadata
    let teams: [String: Team]
    let batters: BatterData
    let pitchers: PitcherData
    let teamComparison: [String: TeamComparisonData]
    let positionAnalysis: [String: PositionData]
    let leaderboards: LeaderboardData
}

// 로드
let data = try JSONDecoder().decode(KBOScoutingData.self, from: jsonData)
```

---

## 📊 데이터 크기 예상

| 항목 | 레코드 수 | 예상 크기 |
|------|----------|----------|
| 타자 인덱스 | ~500명 | 50KB |
| 타자 KPI (5시즌) | ~2,000 | 2MB |
| 투수 인덱스 | ~400명 | 40KB |
| 투수 KPI (5시즌) | ~1,500 | 1.5MB |
| 팀 비교 (5시즌) | 50 | 100KB |
| 포지션 분석 (5시즌) | 45 | 80KB |
| 리더보드 (5시즌) | 10 | 30KB |
| **총합** | | **~4MB** |
| **압축 후** | | **~1MB** |

---

## ✅ 즉시 실행 가능한 작업

1. **JSON 데이터 내보내기 스크립트 작성**
   - 현재 Parquet 데이터 → JSON 변환

2. **리더보드 페이지 추가**
   - 기존 데이터로 즉시 구현 가능

3. **데모 앱 배포 확인**
   - Streamlit Cloud 정상 동작 확인

---

## 🔗 참고 문서

- [DATA_CATALOG.md](./DATA_CATALOG.md) - 현재 데모 앱 데이터 구조
- [AI_STITCH_PROMPT.md](./AI_STITCH_PROMPT.md) - 모바일 UI 디자인 프롬프트
- 원본 React 컴포넌트: `frontend/src/pages/v2/scouting-report/`
- 원본 API 라우터: `api_sabermetrics_server/routers/`
