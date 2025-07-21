# Django + Ninja REST API 서버

## 📁 프로젝트 구조 소개
Django를 API 서버로만 사용하는 구조로 구성되어 있으며, 도메인 단위로 앱을 분리해 유지보수성과 확장성을 고려하기
```
django-server/
├── apps/
│   ├── api/            # NinjaAPI 인스턴스 및 전체 라우터 통합
│   ├── users/          # 사용자 도메인 (회원가입, 로그인, 인증 등)
│   └── ...             # 기능별 앱 추가 가능
├── config/             # Django 설정 모듈
│   ├── settings.py
│   └── urls.py
├── manage.py
└── .venv/              # Python 가상환경 (git에 포함 안됨)
```

## ⚙️ 개발 환경 세팅

1. 레포 클론
```bash
git clone https://github.com/CAPStone-CAPS/django-server.git
cd django-server
```

2. 가상환경 + 패키지 설치
```bash
uv sync
.venv\Scripts\activate           # Windows
# source .venv/bin/activate     # macOS/Linux
```

## 📘 API 문서 자동 생성
Ninja에서 Swagger UI 문서가 자동 제공됨
로컬 주소 실행 시 주소: 
> http://127.0.0.1:8000/api/docs


## 협업 규칙
- `main` 브랜치에서 직접 작업하지 않고, `feat/`, `fix/`, `chore/` 등 기능별 브랜치를 생성합니다.
- PR 생성 후 CI 검사를 통과하면 `main` 브랜치에 머지합니다.
- 커밋 메시지는 `태그: 내용` 구조로 작성하며, PR 및 이슈 제목도 동일한 형식을 따릅니다.
- 환경변수는 노션에 기록하며, 업데이트 될때마다 빠르게 알려줍시다!
