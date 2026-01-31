# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

'밑바닥부터 시작하는 웹 브라우저' 도서 기반의 학습용 Python 웹 브라우저 구현 프로젝트. 외부 라이브러리 없이 Python 표준 라이브러리만 사용한다.

## Communication Style

파이썬과 타입스크립트에 대해 잘 알고있는 프로그래밍 교육자로서 응답한다.
파이썬 관련된 개념을 설명할 때, 웹 프론트엔드 개발자가 이해하기 쉽도록 자바스크립트, 타입스크립트의 문법에 빗대어 설명한다.

## Running

```bash
python3 browser.py
```

테스트 URL은 `browser.py`의 `if __name__ == "__main__":` 블록에서 주석을 토글하여 선택한다.

## Architecture

두 개의 소스 파일로 구성된 단일 실행 스크립트:

- **browser.py** — URL 파싱, HTTP 통신, 렌더링, 브라우저 오케스트레이션을 모두 포함
- **cache.py** — 캐시 추상 인터페이스(`Cache` ABC)와 메모리 구현체(`MemoryCache`)

### 핵심 흐름

```
Browser.load(url_string)
  → URL 파싱 (data/file 스킴은 여기서 조기 반환)
  → Cache.get()으로 캐시 확인
  → cache miss 시 HttpClient.fetch()로 네트워크 요청
    → 소켓 생성/재사용 (keep-alive)
    → 요청 전송 → 응답 파싱 (status, headers, body)
    → gzip 압축 해제 (content-encoding 확인)
    → 301/302 리다이렉트 시 재귀 호출
  → Cache-Control 헤더 기반으로 캐시 저장 여부 결정
  → Renderer로 본문 출력 (HTML / ViewSource / File)
```

### 클래스 책임

| 클래스 | 책임 |
|---|---|
| `URL` | URL 문자열 → scheme, host, port, path 파싱 |
| `HttpClient` | 소켓 관리, HTTP 요청/응답, gzip, chunked encoding, 리다이렉트 |
| `Browser` | 클라이언트 풀링(`host:port` 기준), 캐시 연동, 렌더러 선택 |
| `Cache` / `MemoryCache` | 추상 캐시 인터페이스 + dict 기반 메모리 구현 (max-age 만료 지원) |
| `HtmlRenderer` | HTML 태그 제거 후 텍스트 출력 |
| `ViewSourceRenderer` | HTML 소스 코드 그대로 출력 |
| `FileRenderer` | 로컬 파일 읽기 (MIME 타입 기반 image/text 분기) |

### 설계 패턴

- **의존성 주입**: `Browser`는 `Cache` 추상 타입을 받으므로 캐시 구현체 교체가 가능
- **커넥션 풀링**: `Browser.clients` dict로 동일 `host:port`에 대해 소켓 재사용
- **전략 패턴**: URL 스킴과 상태에 따라 적절한 Renderer를 선택
