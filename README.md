# PIXXGEN GUI QT

X-ray 장비 제어를 위한 GUI 애플리케이션입니다.

## 주요 기능

- X-ray 장비 원격 제어
- 스테핑 모터 제어
- DC 모터 제어
- 콜리메이터 제어
- TCP/IP 기반 원격 제어 인터페이스
- 레이저 다이오드 제어
- 하드웨어 상태 모니터링

## 시스템 요구사항

- Python 3.7 이상
- PyQt5
- Raspberry Pi (테스트된 버전: Raspberry Pi 4)
- 리눅스 운영체제 (테스트된 버전: Raspberry Pi OS)

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/k2hcis03/pixxgen_gui_qt_rev2.git
cd pixxgen_gui_qt_rev2
```

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
python main.py
```

## 설정

### config.ini 파일 설정

`config.ini` 파일에서 다음 설정을 조정할 수 있습니다:

1. 모터 속도 설정
   - ST1MAXSPEED: 스테핑 모터 1 최대 속도
   - ST1MINSPEED: 스테핑 모터 1 최소 속도
   - ST2MAXSPEED: 스테핑 모터 2 최대 속도
   - ST2MINSPEED: 스테핑 모터 2 최소 속도
   - ST3MAXSPEED: 스테핑 모터 3 최대 속도
   - ST3MINSPEED: 스테핑 모터 3 최소 속도
   - COLL1MAXSPEED: 콜리메이터 최대 속도
   - COLL1MINSPEED: 콜리메이터 최소 속도
   - DC1MAXSPEED: DC 모터 최대 속도
   - DC1MINSPEED: DC 모터 최소 속도

2. TCP 서버 설정
   - 기본 포트: 9527
   - 기본 호스트: 192.168.100.120

## JSON 클라이언트 사용 방법

별도의 `jsonclient.py` 프로그램을 사용하여 TCP/IP를 통해 장비를 제어할 수 있습니다:

```bash
python jsonclient.py --host 192.168.100.120 --port 9527 --sel 1 --onoff 1
```

### 클라이언트 옵션
- `--host`: 서버 IP 주소
- `--port`: 서버 포트 번호
- `--sel`: X-ray 선택 (1 또는 2)
- `--onoff`: 전원 제어 (0: OFF, 1: ON)
- `--continuous`: 연속 모드 사용
- `--no-buzzer`: 부저 비활성화

## 라이선스

이 프로젝트는 독점 라이선스로 보호됩니다. 무단 사용 및 배포를 금지합니다.

## 문의

기술 지원 및 문의사항은 아래 연락처로 문의해주세요:
- Email: k2hcis03@gmail.com 
