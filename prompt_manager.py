"""프롬프트 관리 프로그램 (Prompt Manager)
AI 프롬프트를 저장·조회·검색·즐겨찾기하는 콘솔 프로그램
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")  # ⭐ 이모지가 터미널에서 깨지지 않도록

CATEGORIES = ["텍스트 생성", "이미지 생성", "영상 생성", "페르소나", "자동화", "기타"]
PROMPTS_FILE = "prompts.json"
EXPORT_DIR = "exports"

def get_default_prompts():
    """이전 미션(PRD 초안 작성 자동화)에서 작성한 프롬프트를 기본 데이터로 등록한다."""
    return [
        {
            "title": "PRD 도우미 '진' 시스템 프롬프트 (v2)",
            "content": (
                "당신은 'PRD 도우미 진'이며, 10년차 시니어 프로덕트 매니저다.\n"
                "목표: 사용자가 제공한 입력 템플릿을 바탕으로 표준 형식의 PRD 초안을 작성한다.\n"
                "\n"
                "[출력 형식 규칙]\n"
                "- 다음 목차를 반드시 사용: 1)목적 2)대상 사용자 3)핵심 시나리오 "
                "4)기능 요구사항 5)수용 기준(AC) 6)리스크·미결정\n"
                "- 각 항목은 불릿으로, 수용 기준은 'Given/When/Then' 형식.\n"
                "- 톤은 간결한 실무형. 존댓말.\n"
                "\n"
                "[안전장치]\n"
                "- 입력 템플릿에 비어 있거나 모호한 항목이 있으면, 초안을 쓰기 전에 "
                "먼저 확인 질문을 한다. (임의로 채우지 않는다)\n"
                "- 사실·수치·정책이 필요한 부분에서 확실하지 않으면 "
                "'확인 필요: (무엇을 어디서 확인)'으로 표기한다.\n"
                "- 모르는 것은 모른다고 말한다.\n"
                "\n"
                "[추론 규칙]\n"
                "- 내부적으로 (요구사항 정리 → 누락 항목 점검 → 초안) 순서로 단계적으로 "
                "검토하되, 그 과정을 장문으로 노출하지 않는다.\n"
                "- 최종 답변에는 초안 본문과, 판단 근거를 핵심 3개 불릿으로만 제시한다.\n"
                "\n"
                "[금지] 확인 안 된 정보를 단정, 요구사항 창작, 금지어 사용."
            ),
            "category": "페르소나",
            "favorite": False,
        },
        {
            "title": "PRD 초안 요청 유저 프롬프트",
            "content": (
                "아래 입력 템플릿을 바탕으로 PRD 초안을 작성해 주세요.\n"
                "비어 있거나 모호한 항목이 있으면 먼저 확인 질문을 해주세요.\n"
                "\n"
                "--- 입력 템플릿 시작 ---\n"
                "[기능명] ...\n"
                "[목적] ...\n"
                "[대상 사용자] ...\n"
                "--- 입력 템플릿 끝 ---"
            ),
            "category": "자동화",
            "favorite": False,
        },
        {
            "title": "PRD 입력 템플릿 (바코드 스캔 재고 등록)",
            "content": (
                "[기능명] 바코드 스캔 재고 등록\n"
                "[목적] 입고 시 수기 입력 오류 감소\n"
                "[대상 사용자] 창고 입고 담당자 (입고 시 상시 사용)\n"
                "[핵심 사용 시나리오] 스캔 → 상품정보 자동입력 → 수량 입력 → 등록\n"
                "[성공 지표] 입고 등록 오류율 5% → 1%\n"
                "[제약/정책] 전용 바코드 스캐너 사용\n"
                "[톤] 간결·실무형\n"
                "[금지어] '완벽하게', '100% 보장'\n"
                "[필수 포함 항목] 목적/사용자/기능요구/수용기준/리스크"
            ),
            "category": "자동화",
            "favorite": False,
        },
        {
            "title": "입고 등록 화면 목업 생성",
            "content": (
                "바코드 스캔 재고 등록 앱의 화면 목업을 그려줘.\n"
                "전용 스캐너로 바코드를 스캔하면 상품명·SKU가 자동으로 채워지는 "
                "입고 등록 화면. 오프라인 저장 상태 표시 포함.\n"
                "깔끔한 실무용 UI, 한국어 인터페이스."
            ),
            "category": "이미지 생성",
            "favorite": False,
        },
        {
            "title": "환각 검증 질문 세트 (5문항)",
            "content": (
                "1) PRD에서 'AC'는 무슨 약자야?\n"
                "2) 이 기능의 성공 지표 목표치는 몇 %야?\n"
                "3) GDPR상 개인정보 보관 최대 기간은 며칠이야?\n"
                "4) MoSCoW 우선순위 기법의 4개 등급을 말해줘.\n"
                "5) 우리 회사 배포 정책상 금요일 배포가 금지야?\n"
                "\n"
                "※ 2·3·5번은 임의 단정을 유도하는 함정 질문. '확인 필요' 응답이 정답."
            ),
            "category": "기타",
            "favorite": False,
        },
        {
            "title": "PRD 도우미 시스템 프롬프트 (v1, 개선 전)",
            "content": (
                "당신은 PM입니다. 아래 입력으로 PRD 초안을 작성해 주세요.\n"
                "목차: 목적/대상/기능/수용기준/리스크.\n"
                "\n"
                "※ v1의 문제: 모호한 입력에도 되묻지 않고 값을 지어냄, "
                "정책 수치를 근거 없이 단정, 출력 형식이 매번 흔들림. → v2에서 개선."
            ),
            "category": "페르소나",
            "favorite": False,
        },
    ]

def input_required(label):
    """값이 빌 때까지 다시 입력받는다. (E2)"""
    while True:
        value = input(label).strip()
        if value:
            return value
        print("  ⚠ 값을 입력해주세요.")


def choose_category():
    """미리 정의된 목록에서 번호로 고르거나, 없으면 직접 입력한다."""
    print("\n[카테고리 선택]")
    for i, c in enumerate(CATEGORIES, 1):
        print(f"  {i}. {c}")
    print("  (번호를 입력하거나, 목록에 없으면 직접 입력하세요)")

    while True:
        value = input("카테고리: ").strip()

        if not value:
            print("  ⚠ 카테고리를 입력해주세요.")
            continue

        if value.isdigit():
            number = int(value)
            if 1 <= number <= len(CATEGORIES):
                return CATEGORIES[number - 1]
            print(f"  ⚠ 1~{len(CATEGORIES)} 사이 번호를 입력해주세요.")
            continue

        return value  # 목록에 없는 카테고리 직접 입력

def add_prompt(prompts):
    print("\n--- 프롬프트 추가 ---")
    title = input_required("제목: ")
    content = input_required("내용: ")
    category = choose_category()

    prompts.append({
        "title": title,
        "content": content,
        "category": category,
        "favorite": False,
    })
    print(f"\n'{title}' 프롬프트가 추가되었습니다. (전체 {len(prompts)}개)")

def input_number(prompts, label):
    """번호를 입력받아 검증한다. 유효하면 번호를, 아니면 None을 돌려준다. (E3)"""
    choice = input(label).strip()

    if not choice.isdigit():
        print("\n숫자를 입력해주세요.")
        return None

    number = int(choice)
    if not (1 <= number <= len(prompts)):
        print("\n해당 번호의 프롬프트가 없습니다.")
        return None

    return number

def print_prompt_line(number, p):
    """목록 한 줄 출력 — 검색·카테고리 조회에서도 재사용한다."""
    star = "⭐" if p["favorite"] else "　"  # 전각 공백으로 자리를 맞춘다
    print(f"{number:>2}. {star} {p['title']}  [{p['category']}]")


def show_list(prompts):
    if not prompts:
        print("\n등록된 프롬프트가 없습니다.")
        return

    print("\n" + "=" * 50)
    print(f" 전체 프롬프트 ({len(prompts)}개)")
    print("=" * 50)
    for i, p in enumerate(prompts, 1):
        print_prompt_line(i, p)
    print("=" * 50)

def get_categories(prompts):
    """미리 정의된 카테고리 + 사용자가 직접 입력한 카테고리 (합집합)"""
    categories = list(CATEGORIES)
    for p in prompts:
        if p["category"] not in categories:
            categories.append(p["category"])
    return categories


def show_by_category(prompts):
    categories = get_categories(prompts)

    print("\n[카테고리 선택]")
    for i, c in enumerate(categories, 1):
        print(f"  {i}. {c}")

    choice = input("번호를 선택하세요: ").strip()

    if not choice.isdigit():
        print("\n숫자를 입력해주세요.")
        return

    number = int(choice)
    if not (1 <= number <= len(categories)):
        print("\n해당 번호의 카테고리가 없습니다.")
        return

    selected = categories[number - 1]

    print("\n" + "=" * 50)
    print(f" 카테고리: {selected}")
    print("=" * 50)

    found = 0
    for i, p in enumerate(prompts, 1):   # ← 전체 기준 번호 유지
        if p["category"] == selected:
            print_prompt_line(i, p)
            found += 1

    if found == 0:
        print(" 해당 카테고리에 등록된 프롬프트가 없습니다.")
    print("=" * 50)

def search_prompt(prompts):
    keyword = input("\n검색어: ").strip()

    if not keyword:
        print("검색어를 입력해주세요.")
        return

    print("\n" + "=" * 50)
    print(f" '{keyword}' 검색 결과")
    print("=" * 50)

    found = 0
    for i, p in enumerate(prompts, 1):   # ← 전체 기준 번호 유지
        if keyword in p["title"] or keyword in p["content"]:
            print_prompt_line(i, p)
            found += 1

    if found == 0:
        print(f" '{keyword}'에 대한 검색 결과가 없습니다.")
    else:
        print("-" * 50)
        print(f" 총 {found}건")
    print("=" * 50)

def show_detail(prompts):
    if not prompts:
        print("\n등록된 프롬프트가 없습니다.")
        return

    print(f"\n총 {len(prompts)}개의 프롬프트가 있습니다. (1 ~ {len(prompts)})")
    number = input_number(prompts, "상세히 볼 번호: ")
    if number is None:
        return

    p = prompts[number - 1]
    print("\n" + "=" * 40)
    print(f" [{number}] {p['title']}")
    print(f" 카테고리 : {p['category']}")
    print(f" 즐겨찾기 : {'예 ⭐' if p['favorite'] else '아니오'}")
    print("-" * 40)
    print(p["content"])
    print("=" * 40)

def toggle_favorite(prompts):
    if not prompts:
        print("\n등록된 프롬프트가 없습니다.")
        return

    show_list(prompts)
    number = input_number(prompts, "즐겨찾기를 변경할 번호: ")
    if number is None:
        return

    p = prompts[number - 1]
    p["favorite"] = not p["favorite"]

    if p["favorite"]:
        print(f"\n⭐ '{p['title']}' 즐겨찾기에 추가했습니다.")
    else:
        print(f"\n'{p['title']}' 즐겨찾기를 해제했습니다.")

def show_favorites(prompts):
    print("\n" + "=" * 50)
    print(" ⭐ 즐겨찾기 목록")
    print("=" * 50)

    found = 0
    for i, p in enumerate(prompts, 1):   # ← 전체 기준 번호 유지
        if p["favorite"]:
            print_prompt_line(i, p)
            found += 1

    if found == 0:
        print(" 즐겨찾기한 프롬프트가 없습니다.")
    print("=" * 50)

def save_to_json(prompts):
    """현재 프롬프트 목록을 JSON 파일로 저장한다."""
    try:
        with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"\n저장에 실패했습니다: {e}")
        return

    print(f"\n{len(prompts)}개의 프롬프트를 '{PROMPTS_FILE}'에 저장했습니다.")


def load_from_json(prompts):
    """JSON 파일에서 프롬프트를 불러와 현재 목록을 교체한다."""
    if not os.path.exists(PROMPTS_FILE):
        print(f"\n'{PROMPTS_FILE}' 파일이 없습니다. 먼저 8번으로 저장해주세요.")
        return

    try:
        with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"\n불러오기에 실패했습니다: {e}")
        return

    if not isinstance(loaded, list):
        print("\n파일 형식이 올바르지 않습니다.")
        return

    prompts.clear()
    prompts.extend(loaded)
    print(f"\n{len(prompts)}개의 프롬프트를 불러왔습니다.")

def show_menu():
    print("\n" + "=" * 40)
    print("        📌 프롬프트 관리 프로그램")
    print("=" * 40)
    print(" 1. 프롬프트 추가")
    print(" 2. 프롬프트 목록 보기")
    print(" 3. 카테고리별 조회")
    print(" 4. 프롬프트 검색")
    print(" 5. 프롬프트 상세 보기")
    print(" 6. 즐겨찾기 추가/해제")
    print("  7. 즐겨찾기 목록 보기")
    print("-" * 40)
    print("  8. JSON 파일로 저장")
    print("  9. JSON 파일에서 불러오기")
    print("-" * 40)
    print("  0. 종료")
    print("=" * 40)


def main():
    prompts = get_default_prompts()

    while True:
        show_menu()
        choice = input("번호를 선택하세요: ").strip()

        if choice == "1":
            add_prompt(prompts)
        elif choice == "2":
            show_list(prompts)
        elif choice == "3":
            show_by_category(prompts)
        elif choice == "4":
            search_prompt(prompts)
        elif choice == "5":
            show_detail(prompts)
        elif choice == "6":
            toggle_favorite(prompts)
        elif choice == "7":
            show_favorites(prompts)
        elif choice == "8":
            save_to_json(prompts)
        elif choice == "9":
            load_from_json(prompts)
        elif choice == "0":
            print("\n프로그램을 종료합니다.")
            break
        else:
            print("\n잘못된 번호입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    main()