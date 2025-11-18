# KBO 스카우팅 리포트 데모

2021-2025 KBO 정규시즌 선수 분석 시스템 데모 버전

## 기능

### 타자 스카우팅 리포트
- 6개 카테고리 분석: 컨택, 홈런 파워, 갭 파워, 선구안, 일관성, 클러치
- 레이더 차트 시각화
- 상세 지표 (30+ metrics)
- 시즌별 추이 분석
- 리그 내 백분위 순위

### 투수 스카우팅 리포트
- 5개 카테고리 분석: 제구력, 공격성, 효율성, 구위, 클러치
- 레이더 차트 시각화
- 상세 지표 (85+ metrics)
- 시즌별 추이 분석
- 리그 내 백분위 순위

## 데이터

- **기간**: 2021-2025 정규시즌
- **타자**: 983명 (시즌별)
- **투수**: 1,445명 (시즌별)
- **포맷**: Parquet (in-memory)

## 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py --server.port 41000
```

## Streamlit Cloud 배포

1. GitHub 레포지토리에 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 에서 새 앱 생성
3. 레포지토리 선택 및 배포

## 기술 스택

- **프레임워크**: Streamlit
- **데이터**: Pandas, PyArrow
- **시각화**: Plotly
- **데이터 포맷**: Parquet (snappy 압축)

## 데이터 크기

- `batter_kpi.parquet`: ~0.6 MB
- `pitcher_kpi.parquet`: ~0.4 MB
- `players.parquet`: ~0.03 MB
- `teams.parquet`: ~0.003 MB

**총합**: ~1 MB (Streamlit Cloud 무료 티어에 적합)

---

*이 앱은 데모 목적으로 제작되었습니다.*
