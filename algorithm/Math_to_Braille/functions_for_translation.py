import re
from . import brf_code
from . import brf_to_indeterminate_letter as bil

# mathBrailleTranscribe method

def mathBrailleTranscribe(latex):
    # 공백 \quad, ~, \right. 제거
    latex = latex.replace("\\quad", "").replace("~", "").replace("\\right.", "")

    if r"\text" in latex:
        PATTERN_OF_TEXT_PART = re.compile(r"\\text ?{.+?}")
        text_list = []
        latex_copy = latex
        for m in PATTERN_OF_TEXT_PART.finditer(latex):
            start, end = m.span()
            text_list.append(latex[start + 6 : end - 1])  # 'text' 내용 저장

        latex = PATTERN_OF_TEXT_PART.sub("텍스트파트", latex_copy)

    #      삼각함수 편집
    if any(
        trig in latex for trig in ("\\sin", "\\cos", "\\tan", "\\csc", "\\sec", "\\cot")
    ):
        latex = wrap_trig_argument(latex)

    #  log 편집
    if r"\log" in latex:
        latex = wrap_log_argument(latex)

    result = translate_to_math_braille(latex)
    # 미정의 문자로 변환
    result = bil.translate_brf_to_il(result)

    # textpart 토큰 원래 텍스트로 복원
    if "텍스트파트" in result:
        for t in text_list:
            # '\text { }' 형태로 띄어쓰기가 들어가면 추출된 텍스트의 첫 글자가 '{'이기 때문에 별도 처리 필요.
            if t[0] == "{":
                t = t[1:]
            result = result.replace("텍스트파트", f" {t} ", 1)
    return result


# 수식 점역 함수
def translate_to_math_braille(latex_match):
    # change form
    output_of_unit = unit(latex_match)
    output_of_mathrm = mathrm(output_of_unit)
    result_cf = output_of_mathrm
    # Basic Translation
    # 한 글자씩 변환 후에 latex코드 상으로 공백을 뜻하는 '\ '를 삭제한다
    print("result_cf", result_cf)
    # 한 글자씩 점역 후 "\\", "\ " 기호를 처리
    output_of_translate_one_to_one = (
        translate_one_to_one(result_cf).replace(r"\\", "\n").replace(r"\ ", "")
    )
    # 벡슬래시와 함께 쓰이는 latex를 변환 후에 공백을 삭제한다
    output_of_translate_latex_with_backslash = translate_latex_with_backslash(
        output_of_translate_one_to_one
    ).replace(" ", "")

    # 연립식 점역
    print("before", output_of_translate_latex_with_backslash)
    output_of_equation_array = equation_array2(output_of_translate_latex_with_backslash)

    # Translation Function for Specific Latex Symbols
    output_of_fraction = fraction(output_of_equation_array)
    output_of_root = root(output_of_fraction)
    output_of_square_root = square_root(output_of_root)
    output_of_trigonometric_function = trigonometric_function(output_of_square_root)
    output_of_log = (
        log(output_of_trigonometric_function)
        .replace("\\ln", "ln")
        .replace("\\log", "_")
    )
    output_of_summation = summation1(summation(output_of_log))
    output_of_integral = integral2(integral1(integral(output_of_summation)))
    output_of_limit = limit(output_of_integral)
    output_of_dot = dot(output_of_limit)
    output_of_overline = overline(output_of_dot)
    output_of_bar = bar(output_of_overline)
    output_of_number_of_poss = number_of_poss(output_of_bar)
    output_of_superscript = superscript(prime(output_of_number_of_poss)).replace(
        "{}^", "^"
    )  # 윗첨자 앞에 빈 중괄호쌍이 있는 경우 중괄호쌍을 제거
    output_of_subscript = subscript(output_of_superscript)
    restore_whitespace = output_of_subscript.replace("WSP", " ")

    # Sophisticated Process
    output_of_add_dot_between_number_and_alphabet = add_dot_between_number_and_alphabet(
        restore_whitespace
    )
    output_of_capital_sign = capital_sign(output_of_add_dot_between_number_and_alphabet)
    output_of_delete_number_sign_between_numbers = delete_number_sign_between_numbers(
        output_of_capital_sign
    )
    output_of_delete_number_sign_after_dot = delete_number_sign_after_dot(
        output_of_delete_number_sign_between_numbers
    )
    result = restore_brf_parentheses(
        brf_parentheses(output_of_delete_number_sign_after_dot)
    )

    # 기타함수
    # 단위 기호 관련 끝처리
    result = unit1(result)
    # 단항식인 경우 영어시작표 처리 후 그리스 문자(eta, theta, chi) 올바른 점형으로 수정
    result = (
        variable(result).replace(".h", ".:").replace(".j", ".?").replace(".q", ".&")
    )
    return result


# Basic Translation
# brf_code.code를 참조해서 latex를 brf로 변환하는 함수
def translate_latex_to_brf(latex):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    #   그리고 brf_code.code 와 제대로 대응되기 위해서 latex 안에 있는 공백을 제거한다
    if isinstance(latex, re.Match):
        latex_str = latex.group().replace(" ", "")
    else:
        latex_str = latex.replace(" ", "")

    #   brf_code.code 에는 대문자 알파벳에 해당하는 brf가 따로 없으므로 대문자는 별도로 brf로 점역한다.
    if len(latex_str) == 1 and latex_str.isupper():
        return "," + latex_str.lower()

    #   brf_code.code 를 참조해서 latex를 brf로 점역한다.
    if latex_str in brf_code.code:
        result_brf = brf_code.code[latex_str][1]
    else:
        result_brf = latex_str
    return result_brf


# 한 글자씩 순차적으로 점역하는 함수
def translate_one_to_one(latex):
    brf_result = ""  # 추후에 점역된 결과로 채워질 것이다.

    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(latex, re.Match):
        latex_str = latex.group()
    else:
        latex_str = latex

    #   brf_code.code 를 참조해서 한 글자씩 순차적으로 brf로 점역한다.
    for i in latex_str:
        if i in brf_code.code:
            brf_result += translate_latex_to_brf(i)
        #       대문자 알파벳이 brf_code.code에 존재하지 않아서 따로 구별해야 한다.
        elif i.isupper():
            brf_result += translate_latex_to_brf(i)
        #       brf_code.code에 존재하지 않는 latex이면 그대로 반환한다.
        else:
            brf_result += i

    return brf_result


# 벡슬래시가 앞에 붙는 latex 기호를 점역하는 함수
def translate_latex_with_backslash(mixed_latex_brf):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    BACKSLASH_ALPHABETS = r"\\,?[a-zA-Z]+"  # 대문자 그리스 문자 때문에 ','를 추가
    BACKSLASH_LEFT_OR_RIGHT_PUCTUATION = r"\\left[\\]?.|\\right[\\]?."
    BACKSLASH_SINGLE_LETTER = r"\\."
    PATTERN_OF_ALPHABETS = re.compile(BACKSLASH_ALPHABETS)
    PATTERN_OF_LEFT_OR_RIGHT_PUCTUATION = re.compile(BACKSLASH_LEFT_OR_RIGHT_PUCTUATION)
    PATTERN_OF_SINGLE_LETTER = re.compile(BACKSLASH_SINGLE_LETTER)
    PATTERNS = [
        PATTERN_OF_ALPHABETS,
        PATTERN_OF_LEFT_OR_RIGHT_PUCTUATION,
        PATTERN_OF_SINGLE_LETTER,
    ]

    brf_result = latex_str
    for i in enumerate(PATTERNS):
        brf_result = i[1].sub(translate_latex_to_brf, brf_result)

    # 대괄호 \left[, \right] 처리하기 위한 코드
    brf_result = brf_result.replace("\\left('", "('").replace("\\right,)", ",)")
    return brf_result


# Translation Function for Specific Latex Symbols
# 분수를 점역하는 함수
def fraction(
    mixed_latex_brf, add_numerator_parentheses=0, add_denominator_parentheses=0
):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 fraction의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 r"\\frac{.*?}{.*?}" 이다.
    pattern_of_fraction = re.compile(
        r"\\frac{("
        + ".*?}" * add_numerator_parentheses
        + ".*?)}{("
        + ".*?}" * add_denominator_parentheses
        + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile(r"\\frac{.*?}{.*?}")

    #   fraction이 문자열에 있는지 확인한다.
    has_fraction = list(pattern_of_fraction.finditer(latex_str))
    if has_fraction:
        numerator, denominator = has_fraction[0].group(1), has_fraction[0].group(2)
        #       아래의 변수는 분자와 분모 안에 '{', '}' 기호의 개수가 같은지 판별하기 위한 변수이다.
        (
            numerator_difference_of_left_and_right,
            denominator_difference_of_left_and_right,
        ) = (
            numerator.count("{") - numerator.count("}"),
            denominator.count("{") - denominator.count("}"),
        )
    else:
        return latex_str

    # 분자와 분모 안에 '{', '}'의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        numerator_difference_of_left_and_right,
        denominator_difference_of_left_and_right,
    ) == (0, 0):
        brf_result = pattern_of_fraction.sub("(\g<2>)/(\g<1>)", latex_str, 1)
        # 한 번 점역된 결과값에fraction이 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return fraction(brf_result)
        else:
            return brf_result

    else:
        if numerator_difference_of_left_and_right:
            add_numerator_parentheses += 1
        elif denominator_difference_of_left_and_right:
            add_denominator_parentheses += 1
        return fraction(
            latex_str, add_numerator_parentheses, add_denominator_parentheses
        )


# 윗첨자(지수)를 점역하는 함수
def superscript(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 윗첨자(지수)의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 "\^{.*?}" 이다.
    pattern_of_superscript = re.compile("\^{(" + ".*?}" * add_parentheses + ".*?)}")
    PATTERN_OF_BASIC_FORM = re.compile("\^{.*?}")

    #   superscript가 문자열에 있는지 확인한다.
    has_superscript = list(pattern_of_superscript.finditer(latex_str))
    if has_superscript:
        content_of_superscript = has_superscript[0].group(1)
    else:
        return latex_str

    # superscript 안의 '{', '}' 의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if content_of_superscript.count("{") - content_of_superscript.count("}") == 0:
        brf_result = pattern_of_superscript.sub("^(\g<1>)", latex_str, 1)
        # 한 번 점역된 결과값에 superscript가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return superscript(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return superscript(latex_str, add_parentheses)


# 제곱근을 점역하는 함수
def square_root(mixed_latex_brf, add_degree_parentheses=0, add_content_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 square_root의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 r"\\sqrt[.*?]{.*?}" 이다.
    pattern_of_square_root = re.compile(
        r"\\sqrt\('("
        + ".*?,\)" * add_degree_parentheses
        + ".*?),\){("
        + ".*?}" * add_content_parentheses
        + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile(r"\\sqrt\[.*?\]{.*?}")

    #   square_root이 문자열에 있는지 확인한다.
    has_square_root = list(pattern_of_square_root.finditer(latex_str))
    if has_square_root:
        degree, content = has_square_root[0].group(1), has_square_root[0].group(2)
        #       아래의 변수는 차수와 근호 안에 괄호 기호의 개수가 같은지 판별하기 위한 변수이다.
        (degree_difference_of_left_and_right, content_difference_of_left_and_right) = (
            degree.count("[") - degree.count("]"),
            content.count("{") - content.count("}"),
        )
    else:
        return latex_str

    # 차수와 근호 안에 괄호 기호의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (degree_difference_of_left_and_right, content_difference_of_left_and_right) == (
        0,
        0,
    ):
        brf_result = pattern_of_square_root.sub("(\g<1>)}(\g<2>)", latex_str, 1)
        # 한 번 점역된 결과값에square_root이 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return square_root(brf_result)
        else:
            return brf_result

    else:
        if degree_difference_of_left_and_right:
            add_degree_parentheses += 1
        elif content_difference_of_left_and_right:
            add_content_parentheses += 1
        return square_root(latex_str, add_degree_parentheses, add_content_parentheses)


# 루트를 점역하는 함수
def root(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 root의 형태를 정규표현식으로 작성한 것이다. root의 기본 형태는
    pattern_of_root = re.compile(r"\\sqrt{(" + ".*?}" * add_parentheses + ".*?)}")
    PATTERN_OF_BASIC_FORM = re.compile(r"\\sqrt{.*?}")

    #   root가 문자열에 있는지 확인한다.
    has_root = list(pattern_of_root.finditer(latex_str))
    if has_root:
        content_of_root = has_root[0].group(1)
    else:
        return latex_str

    #   root 안의 '{', '}' 개수가 일치하는지 판별해서 점을 할지 결정한다.
    if content_of_root.count("{") - content_of_root.count("}") == 0:
        brf_result = pattern_of_root.sub(">(\g<1>)", latex_str, 1)
        #   한번 점역된 결과물에 root가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return root(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return root(latex_str, add_parentheses)


# 아랫첨자(수열)를 점역하는 함수
def subscript(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 아랫첨자(수열)의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 "_{.*?}" 이다.
    pattern_of_subscript = re.compile("_{(" + ".*?}" * add_parentheses + ".*?)}")
    PATTERN_OF_BASIC_FORM = re.compile("_{.*?}")

    #   subscript 가 문자열에 있는지 확인한다.
    has_subscript = list(pattern_of_subscript.finditer(latex_str))
    if has_subscript:
        content_of_subscript = has_subscript[0].group(1)
    else:
        return latex_str

    # subscript 안의 '{', '}' 의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if content_of_subscript.count("{") - content_of_subscript.count("}") == 0:
        brf_result = pattern_of_subscript.sub(";(\g<1>)", latex_str, 1)
        # 한 번 점역된 결과값에 subscript 가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return subscript(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return subscript(latex_str, add_parentheses)


# 순환소수 점역하는 함수
def dot(mixed_latex_brf):
    if isinstance(mixed_latex_brf, re.Match):
        latex = mixed_latex_brf.group()
    else:
        latex = mixed_latex_brf
    if "\\dot" not in latex:
        return latex

    pattern_of_dot = re.compile(r"\\dot{#([a-j])}")

    result = pattern_of_dot.sub(r"`\g<1>", latex)  # \g<1>을 이스케이프하여 사용

    remove_dot = re.compile("`[a-j](#[a-j])*?`[a-j]")  # 기존의 remove_dot 패턴 유지
    result = remove_dot.sub(
        lambda x: "`" + x.group().replace("`", "").replace("#", ""), result
    )

    return result


# bar v.s. segment
# bar 기호인지 segment 기호인지 판별하여 점역하는 함수
def bar_vs_segment(input_match):
    if isinstance(input_match, re.Match):
        bar_or_segment = input_match.group("content")
    else:
        bar_or_segment = input_match

    pattern_of_segment = re.compile("^,[a-z]-?,[a-z]-?$")
    # segment인 경우
    if pattern_of_segment.match(bar_or_segment):
        result_brf = "`c,," + bar_or_segment.replace(",", "")
    # bar인 경우
    else:
        result_brf = "(" + bar_or_segment + ")`c"
    return result_brf


# 선분 및 바(bar)를 점역하는 함수 (overline)
def overline(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 overline의 형태를 정규표현식으로 작성한 것이다. overline의 기본 형태는
    pattern_of_overline = re.compile(
        r"\\overline{(?P<content>" + ".*?}" * add_parentheses + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile(r"\\overline{.*?}")

    #   overline가 문자열에 있는지 확인한다.
    has_overline = list(pattern_of_overline.finditer(latex_str))
    if has_overline:
        content_of_overline = has_overline[0].group(1)
    else:
        return latex_str

    #   overline 안의 '{', '}' 개수가 일치하는지 판별해서 점을 할지 결정한다.
    if content_of_overline.count("{") - content_of_overline.count("}") == 0:
        brf_result = pattern_of_overline.sub(bar_vs_segment, latex_str, 1)
        #   한번 점역된 결과물에 overline가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return overline(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return overline(latex_str, add_parentheses)


# 선분 및 바(bar)를 점역하는 함수 (bar)
def bar(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 bar의 형태를 정규표현식으로 작성한 것이다. bar의 기본 형태는
    pattern_of_bar = re.compile(
        r"\\bar{(?P<content>" + ".*?}" * add_parentheses + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile(r"\\bar{.*?}")

    #   bar가 문자열에 있는지 확인한다.
    has_bar = list(pattern_of_bar.finditer(latex_str))
    if has_bar:
        content_of_bar = has_bar[0].group(1)
    else:
        return latex_str

    #   bar 안의 '{', '}' 개수가 일치하는지 판별해서 점을 할지 결정한다.
    if content_of_bar.count("{") - content_of_bar.count("}") == 0:
        brf_result = pattern_of_bar.sub(bar_vs_segment, latex_str, 1)
        #   한번 점역된 결과물에 bar가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return bar(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return bar(latex_str, add_parentheses)


# 직선 기호를 점역하는 함수
def overleftrightline(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 overleftrightline의 형태를 정규표현식으로 작성한 것이다. overleftrightline의 기본 형태는
    pattern_of_overleftrightline = re.compile(
        r"\\overleftrightline{(" + ".*?}" * add_parentheses + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile(r"\\overleftrightline{.*?}")

    #   overleftrightline가 문자열에 있는지 확인한다.
    has_overleftrightline = list(pattern_of_overleftrightline.finditer(latex_str))
    if has_overleftrightline:
        content_of_overleftrightline = has_overleftrightline[0].group(1)
    else:
        return latex_str

    #   overleftrightline 안의 '{', '}' 개수가 일치하는지 판별해서 점을 할지 결정한다.
    if (
        content_of_overleftrightline.count("{")
        - content_of_overleftrightline.count("}")
        == 0
    ):
        brf_result = pattern_of_overleftrightline.sub("{3o\g<1>", latex_str, 1)
        #   한번 점역된 결과물에 overleftrightline가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return overleftrightline(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return overleftrightline(latex_str, add_parentheses)


# 반직선 기호를 점역하는 함수
def overrightline(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 overrightline의 형태를 정규표현식으로 작성한 것이다. overrightline의 기본 형태는
    pattern_of_overrightline = re.compile(
        r"\\overrightline{(" + ".*?}" * add_parentheses + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile(r"\\overrightline{.*?}")

    #   overrightline가 문자열에 있는지 확인한다.
    has_overrightline = list(pattern_of_overrightline.finditer(latex_str))
    if has_overrightline:
        content_of_overrightline = has_overrightline[0].group(1)
    else:
        return latex_str

    #   overrightline 안의 '{', '}' 개수가 일치하는지 판별해서 점을 할지 결정한다.
    if content_of_overrightline.count("{") - content_of_overrightline.count("}") == 0:
        brf_result = pattern_of_overrightline.sub("{3o\g<1>", latex_str, 1)
        #   한번 점역된 결과물에 overrightline가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return overrightline(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return overrightline(latex_str, add_parentheses)


# 호(arc) 기호를 점역하는 함수
def arc(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 호 기호의 형태를 정규표현식으로 작성한 것이다. 호 기호의 기본 형태는
    pattern_of_arc = re.compile(r"\\arc{(" + ".*?}" * add_parentheses + ".*?)}")
    PATTERN_OF_BASIC_FORM = re.compile(r"\\arc{.*?}")

    #   호 기호가 문자열에 있는지 확인한다.
    has_arc = list(pattern_of_arc.finditer(latex_str))
    if has_arc:
        content_of_arc = has_arc[0].group(1)
    else:
        return latex_str

    #   호 기호 안의 '{', '}' 개수가 일치하는지 판별해서 점을 할지 결정한다.
    if content_of_arc.count("{") - content_of_arc.count("}") == 0:
        brf_result = pattern_of_arc.sub("_{\g<1>", latex_str, 1)
        #   한번 점역된 결과물에 호 기호가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return arc(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return arc(latex_str, add_parentheses)


# 삼각함수를 점역하는 함수
def trigonometric_function(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 삼각함수의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 PATTERN_OF_BASIC_FORM 이다.
    pattern_of_trigonometric_function = re.compile(
        r"\\(?P<kind>sin|cos|tan|csc|sec|cot)\s*?(?P<supersc>\^{[^}]+})?\s*?{(?P<content>"
        + ".*?}" * add_parentheses
        + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile("(sin|cos|tan|csc|sec|cot)")
    #   Key is latex, Value is brf.
    KIND_OF_TRIGONOMETRIC = {
        "sin": "6s",
        "cos": "6c",
        "tan": "6t",
        "csc": "6<",
        "sec": "6-",
        "cot": "6|",
    }

    #   trigonometric_function 가 문자열에 있는지 확인한다.
    has_trigonometric_function = list(
        pattern_of_trigonometric_function.finditer(latex_str)
    )
    if has_trigonometric_function:
        content_of_trigonometric_function = has_trigonometric_function[0].group(
            "content"
        )
        kind = has_trigonometric_function[0].group("kind")
    else:
        return latex_str

    # trigonometric_function안의 '{', '}' 의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        content_of_trigonometric_function.count("{")
        - content_of_trigonometric_function.count("}")
        == 0
    ):
        brf_result = pattern_of_trigonometric_function.sub(
            lambda m: (
                KIND_OF_TRIGONOMETRIC[kind]
                + (
                    "{}({})".format(m.group("supersc"), m.group("content"))
                    if m.group("supersc")  # 지수가 있으면
                    else "({})".format(m.group("content"))
                )
            ),
            latex_str,
            1,
        )

        # 한 번 점역된 결과값에         trigonometric_function 가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return trigonometric_function(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return trigonometric_function(latex_str, add_parentheses)


# 로그를 점역하는 함수
# 로그의 밑이 숫자로만 되어 있을 때 내려쓰기
def log_brl(log_match: re.Match) -> str:
    """
    re.sub() 치환 함수.
    매치 객체에서
        group(1) → 밑(base)
        group(2) → 진수(argument)
    를 추출해 브라유 표기로 변환해 반환한다.
    """
    # 문자(a‑j) → 숫자(1‑0) 변환 테이블
    table = str.maketrans(
        {
            "#": "",
            "a": "1",
            "b": "2",
            "c": "3",
            "d": "4",
            "e": "5",
            "f": "6",
            "g": "7",
            "h": "8",
            "i": "9",
            "j": "0",
        }
    )

    # 밑이 '#a'‑'#j' 패턴(여러 개 반복)으로만 이루어졌는지 검사
    pattern_of_only_num = re.compile(r"^(#[a-j])+$")

    base = log_match.group(1)  # 밑
    arg = log_match.group(2)  # 진수

    # ① 밑이 숫자(= a‑j)로만 구성 → 내려쓰기 표기
    if pattern_of_only_num.match(base):
        return "_,{}({})".format(base.translate(table), arg)
    # ② 그 외 밑 → 일반 표기
    else:
        return "_;({})({})".format(base, arg)


def log(mixed_latex_brf, add_base_parentheses=0, add_antilogarithm_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 log의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 PATTERN_OF_BASIC_FORM 이다.
    pattern_of_log = re.compile(
        r"\\log_{("
        + ".*?}" * add_base_parentheses
        + ".*?)}{("
        + ".*?}" * add_antilogarithm_parentheses
        + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile(r"\\log_{.*?}{.*?}")

    #   log 가 문자열에 있는지 확인한다.
    has_log = list(pattern_of_log.finditer(latex_str))
    if has_log:
        base, antilogarithm = has_log[0].group(1), has_log[0].group(2)
        #       아래의 변수는 밑과 분모 안에 '{', '}' 기호의 개수가 같은지 판별하기 위한 변수이다.
        (
            base_difference_of_left_and_right,
            antilogarithm_difference_of_left_and_right,
        ) = (
            base.count("{") - base.count("}"),
            antilogarithm.count("{") - antilogarithm.count("}"),
        )
    else:
        return latex_str

    # 밑과 진수 안에 '{', '}'의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        base_difference_of_left_and_right,
        antilogarithm_difference_of_left_and_right,
    ) == (0, 0):
        brf_result = pattern_of_log.sub(log_brl, latex_str, 1)
        # 한 번 점역된 결과값에log이 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return log(brf_result)
        else:
            return brf_result
    else:
        if base_difference_of_left_and_right:
            add_base_parentheses += 1
        elif antilogarithm_difference_of_left_and_right:
            add_antilogarithm_parentheses += 1
        return log(latex_str, add_base_parentheses, add_antilogarithm_parentheses)


# 수열의 합(시그마)을 점역하는 함수
def summation(
    mixed_latex_brf,
    add_subscript_parentheses=0,
    add_superscript_parentheses=0,
    add_content_parentheses=0,
):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 summation의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 r"\\sum_{.*?}\^{.*?}{.*?}" 이다.
    summation_form = (
        r"\\sum_{("
        + ".*?}" * add_subscript_parentheses
        + ".*?)}\^{("
        + ".*?}" * add_superscript_parentheses
        + ".*?)}{("
        + ".*?}" * add_content_parentheses
        + ".*?)}"
    )
    pattern_of_summation = re.compile(summation_form)
    PATTERN_OF_BASIC_FORM = re.compile(r"\\sum_{.*?}\^{.*?}{.*?}")

    #   summation이 문자열에 있는지 확인한다.
    has_summation = list(pattern_of_summation.finditer(latex_str))
    if has_summation:
        subscript, superscript, content = (
            has_summation[0].group(1),
            has_summation[0].group(2),
            has_summation[0].group(3),
        )
        #       아래의 변수는 아랫끝과 위끝, 내용물(수열) 안에 '{', '}' 기호의 개수가 같은지 판별하기 위한 변수이다.
        (
            subscript_difference_of_left_and_right,
            superscript_difference_of_left_and_right,
            content_difference_of_left_and_right,
        ) = (
            subscript.count("{") - subscript.count("}"),
            superscript.count("{") - superscript.count("}"),
            content.count("{") - content.count("}"),
        )
    else:
        return latex_str

    # 아랫끝과 윗끝, 내용물(수열) 안에 '{', '}'의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        subscript_difference_of_left_and_right,
        superscript_difference_of_left_and_right,
        content_difference_of_left_and_right,
    ) == (0, 0, 0):
        brf_result = pattern_of_summation.sub(",.s;\g<1> \g<2> \g<3>", latex_str, 1)
        # 한 번 점역된 결과값에summation이 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return summation(brf_result)
        else:
            return brf_result

    else:
        if subscript_difference_of_left_and_right:
            add_subscript_parentheses += 1
        elif superscript_difference_of_left_and_right:
            add_superscript_parentheses += 1
        elif content_difference_of_left_and_right:
            add_content_parentheses += 1
        return summation(
            latex_str,
            add_subscript_parentheses,
            add_superscript_parentheses,
            add_content_parentheses,
        )


def summation1(
    mixed_latex_brf, add_subscript_parentheses=0, add_superscript_parentheses=0
):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 summation1의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 r"\\sum_{.*?}^{.*?}" 이다.
    summation1_form = (
        r"\\sum_{("
        + ".*?}" * add_subscript_parentheses
        + ".*?)}\^{("
        + ".*?}" * add_superscript_parentheses
        + ".*?)}"
    )
    pattern_of_summation1 = re.compile(summation1_form)
    PATTERN_OF_BASIC_FORM = re.compile(r"\\sum_{.*?}\^{.*?}")

    #   summation1이 문자열에 있는지 확인한다.

    has_summation1 = list(pattern_of_summation1.finditer(latex_str))
    if has_summation1:
        subscript, superscript = has_summation1[0].group(1), has_summation1[0].group(2)
        #       아래의 변수는 아랫끝과 위끝 안에 '{', '}' 기호의 개수가 같은지 판별하기 위한 변수이다.
        (
            subscript_difference_of_left_and_right,
            superscript_difference_of_left_and_right,
        ) = subscript.count("{") - subscript.count("}"), superscript.count(
            "{"
        ) - superscript.count(
            "}"
        )
    else:
        return latex_str

    # 아랫끝과 윗끝, 내용물(수열) 안에 '{', '}'의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        subscript_difference_of_left_and_right,
        superscript_difference_of_left_and_right,
    ) == (0, 0):
        brf_result = pattern_of_summation1.sub(",.s;\g<1> \g<2> ", latex_str, 1)
        # 한 번 점역된 결과값에summation1이 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return summation1(brf_result)
        else:
            return brf_result

    else:
        if subscript_difference_of_left_and_right:
            add_subscript_parentheses += 1
        elif superscript_difference_of_left_and_right:
            add_superscript_parentheses += 1
        return summation1(
            latex_str, add_subscript_parentheses, add_superscript_parentheses
        )


# limit을 점역하는 함수
def limit(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 limit의 형태를 정규표현식으로 작성한 것이다. limit의 기본 형태는
    pattern_of_limit = re.compile(r"\\lim_{(" + ".*?}" * add_parentheses + ".*?)}")
    PATTERN_OF_BASIC_FORM = re.compile(r"\\lim_{.*?}")

    #   limit가 문자열에 있는지 확인한다.
    has_limit = list(pattern_of_limit.finditer(latex_str))
    if has_limit:
        content_of_limit = has_limit[0].group(1)
    else:
        return latex_str

    #   limit 안의 '{', '}' 개수가 일치하는지 판별해서 점을 할지 결정한다.
    if content_of_limit.count("{") - content_of_limit.count("}") == 0:
        brf_result = pattern_of_limit.sub("lim;\g<1>WSP", latex_str, 1)
        #   한번 점역된 결과물에 limit가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return limit(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return limit(latex_str, add_parentheses)


# 적분 기호(integral)를 점역하는 함수
def integral(
    mixed_latex_brf,
    add_subscript_parentheses=0,
    add_superscript_parentheses=0,
    add_content_parentheses=0,
):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 integral의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 r"\\int_{.*?}\^{.*?}{.*?}" 이다.
    integral_form = (
        r"\\int_{("
        + ".*?}" * add_subscript_parentheses
        + ".*?)}\^{("
        + ".*?}" * add_superscript_parentheses
        + ".*?)}{("
        + ".*?}" * add_content_parentheses
        + ".*?)}"
    )
    pattern_of_integral = re.compile(integral_form)
    PATTERN_OF_BASIC_FORM = re.compile(r"\\int_{.*?}\^{.*?}{.*?}")

    #   integral이 문자열에 있는지 확인한다.
    has_integral = list(pattern_of_integral.finditer(latex_str))
    if has_integral:
        subscript, superscript, content = (
            has_integral[0].group(1),
            has_integral[0].group(2),
            has_integral[0].group(3),
        )
        #       아래의 변수는 아랫끝과 위끝, 내용물(함수) 안에 '{', '}' 기호의 개수가 같은지 판별하기 위한 변수이다.
        (
            subscript_difference_of_left_and_right,
            superscript_difference_of_left_and_right,
            content_difference_of_left_and_right,
        ) = (
            subscript.count("{") - subscript.count("}"),
            superscript.count("{") - superscript.count("}"),
            content.count("{") - content.count("}"),
        )
    else:
        return latex_str

    # 아랫끝과 윗끝, 내용물(함수) 안에 '{', '}'의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        subscript_difference_of_left_and_right,
        superscript_difference_of_left_and_right,
        content_difference_of_left_and_right,
    ) == (0, 0, 0):
        brf_result = pattern_of_integral.sub("!;\g<1> \g<2> \g<3>", latex_str, 1)
        # 한 번 점역된 결과값에integral이 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return integral(brf_result)
        else:
            return brf_result

    else:
        if subscript_difference_of_left_and_right:
            add_subscript_parentheses += 1
        elif superscript_difference_of_left_and_right:
            add_superscript_parentheses += 1
        elif content_difference_of_left_and_right:
            add_content_parentheses += 1
        return integral(
            latex_str,
            add_subscript_parentheses,
            add_superscript_parentheses,
            add_content_parentheses,
        )


# 적분 type2
def integral1(
    mixed_latex_brf, add_subscript_parentheses=0, add_superscript_parentheses=0
):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 integral1의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 r"\\int_{.*?}^{.*?}" 이다.
    integral1_form = (
        r"\\int_{("
        + ".*?}" * add_subscript_parentheses
        + ".*?)}\^{("
        + ".*?}" * add_superscript_parentheses
        + ".*?)}"
    )
    pattern_of_integral1 = re.compile(integral1_form)
    PATTERN_OF_BASIC_FORM = re.compile(r"\\int_{.*?}\^{.*?}")

    #   integral1이 문자열에 있는지 확인한다.

    has_integral1 = list(pattern_of_integral1.finditer(latex_str))
    if has_integral1:
        subscript, superscript = has_integral1[0].group(1), has_integral1[0].group(2)
        #       아래의 변수는 아랫끝과 위끝 안에 '{', '}' 기호의 개수가 같은지 판별하기 위한 변수이다.
        (
            subscript_difference_of_left_and_right,
            superscript_difference_of_left_and_right,
        ) = subscript.count("{") - subscript.count("}"), superscript.count(
            "{"
        ) - superscript.count(
            "}"
        )
    else:
        return latex_str

    # 아랫끝과 윗끝, 내용물(수열) 안에 '{', '}'의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        subscript_difference_of_left_and_right,
        superscript_difference_of_left_and_right,
    ) == (0, 0):
        brf_result = pattern_of_integral1.sub("!;\g<1> \g<2> ", latex_str, 1)
        # 한 번 점역된 결과값에integral1이 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return integral1(brf_result)
        else:
            return brf_result

    else:
        if subscript_difference_of_left_and_right:
            add_subscript_parentheses += 1
        elif superscript_difference_of_left_and_right:
            add_superscript_parentheses += 1
        return integral1(
            latex_str, add_subscript_parentheses, add_superscript_parentheses
        )


# 적분 type3 (부정적분)
def integral2(mixed_latex_brf):
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    if "\\int" not in latex_str:
        return latex_str

    pattern_of_integral2 = re.compile(r"\\int(?=[^_])")
    result_brf = pattern_of_integral2.sub("!", latex_str)
    return result_brf


# 미분기호(prime)를 점역하는 함수
def prime(mixed_latex_brf):
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    if "\\prime" not in latex_str:
        return latex_str

    # 미분기호의 pattern
    pattern_of_prime = re.compile(r"\^{(?P<prime>(\\prime)+)}")
    result_brf = pattern_of_prime.sub(
        lambda m: m.group("prime").replace("\\prime", "-"), latex_str
    )
    return result_brf


# 경우의 수 기호를 점역하는 함수
def number_of_poss(mixed_latex_brf):
    NUMBER_OF_POSS = re.compile(
        r"""{ ?}\s*_{(?P<first>[^}]*)}\s*   # {}_{ n }
            (?P<kind>,c|,p|,h|,.p)\s*       # C·P·H·.P 구분
            _{(?P<sec>[^}]*)}               # _{ k }
        """,
        re.VERBOSE,
    )
    return NUMBER_OF_POSS.sub("\g<kind>(\g<first> \g<sec>)", mixed_latex_brf)


# Sophisticated Process
# 알파벳 a-j 앞에 숫자가 있으면 5점(")를 붙인다.
def add_dot_between_number_and_alphabet(brf):
    PATTERN_OF_NUMBER_ALPHABET = re.compile("#[a-j][a-j]")
    brf_result = PATTERN_OF_NUMBER_ALPHABET.sub(
        lambda x: x.group()[0:2] + '"' + x.group()[2], brf
    )
    return brf_result


# 대문자가 연속해서 나오면 첫 글자에 6점 두 개를 붙인다
def capital_sign(brf):
    PATTERN_OF_CAPITAL_ALPHABETS = re.compile(",[a-z](,[a-z])+")
    brf_result = PATTERN_OF_CAPITAL_ALPHABETS.sub(
        lambda x: ",," + x.group().replace(",", ""), brf
    )
    return brf_result


# 숫자가 연속해서 나올 때 처음에만 수표를 붙인다
def delete_number_sign_between_numbers(brf):
    PATTERN_OF_NUMBER_SIGN_BETWEEN_NUMBERS = re.compile("#[a-j](#[a-j])+")
    brf_result = PATTERN_OF_NUMBER_SIGN_BETWEEN_NUMBERS.sub(
        lambda x: "#" + x.group().replace("#", ""), brf
    )
    return brf_result


# 소수점 뒤에 수표를 붙이지 않는다
def delete_number_sign_after_dot(brf):
    PATTERN_OF_NUMBER_SIGN_AFTER_DOT = re.compile("#[a-j]+?4#[a-j]")
    brf_result = PATTERN_OF_NUMBER_SIGN_AFTER_DOT.sub(
        lambda x: x.group().replace("4#", "4"), brf
    )
    return brf_result


# 묶음괄호를 처리하는 함수
#  brf_parentheses 함수는 묶음괄호를 사용하는 경우 '(', ')' 기호를 '"LEFT, "RIGHT"로 바꾸고, 묶음괄호를 사용하지 않는 경우 '(', ')' 기호를 삭제하는 함수이다.
def brf_parentheses(brf, move_in=0):
    #   grouping 는 가장 바깥쪽의 '(' (여는 묶음괄호)와 가장 안쪽의 '(' 사이의 수식들을 그룹핑해서 보호하는 역할을 한다.
    if move_in == 0:
        grouping = 0
    else:
        grouping = 1
    #   pattern_of_brf_parentheses 은 묶음괄호가 사용된 부분을 정규표현식으로 나타낸 것이다.
    #   "(?!')", "(?!,)"는 대괄호("('", ",)")와 겹치지 않고 묶음괄호만을 탐색할 수 있도록 하는 역할이다.
    pattern_of_brf_parentheses = re.compile(
        "(" * grouping
        + "[(](?!').*?" * move_in
        + ")" * grouping
        + "[(](?!')(?P<content>.*?)(?!,)[)]"
    )
    PATTERN_OF_BASIC_FORM = re.compile("[(](?!').*?(?!,)[)]")
    #   아래는 묶음괄호가 사용되지 않는 경우들이다.
    CASE_OF_NOT_USING = re.compile(
        r"""^(
    [59]?>?,?[.]?[a-z]  # '부호' + '루트' + '대문자여부' + '알파벳'/'그리스 문자'
   |[59]?>?[#][a-j]+  # '부호' + '루트' + '숫자'
    |[59]?(d|\$)(\^\#[a-j])?,?[.]?[a-z](\^\#[a-j])?  # '부호' + '미분기호'/'편미분기호' + '미분 횟수' + '대문자여부' + '알파벳'/'그리스 문자' + '미분횟수'
    | -+  # 'prime'기호
    )$""",
        re.VERBOSE,
    )

    #   묶음괄호가 문자열에 있는지 확인한다.
    has_brf_parentheses = list(pattern_of_brf_parentheses.finditer(brf))
    if has_brf_parentheses:
        content_between_brf_parentheses = has_brf_parentheses[0].group("content")
    else:
        return brf

    #   가장 안쪽의 묶음괄호까지 이동했는지 판별한다.
    if (
        content_between_brf_parentheses.count("(")
        - content_between_brf_parentheses.count(")")
        == 0
    ):
        #       묶음괄호를 사용하지 않는 겨우인지 사용하는 경우인지를 판별해서 묶음괄호를 제거하거나 "LEFT"/"RIGHT"으로 대체한다.
        if CASE_OF_NOT_USING.match(content_between_brf_parentheses):
            result_brf = pattern_of_brf_parentheses.sub(
                "\g<1>" * grouping + "\g<content>", brf, 1
            )
        else:
            result_brf = pattern_of_brf_parentheses.sub(
                "\g<1>" * grouping + "LEFT\g<content>RIGHT", brf, 1
            )

        #       한 번 점역된 결과값에 묶음괄호가 사용된 부분이 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(result_brf):
            return brf_parentheses(result_brf)
        else:
            return result_brf
    else:
        move_in += 1
        return brf_parentheses(brf, move_in)


# restore_brf_parentheses 함수는 "LEFT", "RIGHT" 을 묶음괄호 '(', ')'로 복원한다.
def restore_brf_parentheses(output_of_brf_parentheses, n=0):
    result_brf = output_of_brf_parentheses.replace("LEFT", "(").replace("RIGHT", ")")
    return result_brf


#  기타 함수
# 단항식으로 사용된 로마자와 그리스 문자 처리하는 함수
def variable(brf):
    # 미지수가 한 개인 경우 처리하기 윈한 pattern
    pattern_of_one_variable = re.compile("^,?\.?([a-z])$")
    # 미지수가 comma로 나열된 경우 처리하기 위한 pattern
    pattern_of_variable_comma = re.compile('^(,?\.?([a-z])" )+,?\.?([a-z])$')

    def exception_aio(m):
        # a, i, o를 제외하고 영어철자표를 붙이는 함수이다
        # 영어 철자 기호를 사용하는 경우를 처리하기 위한 pattern
        pattern_of_exception = re.compile("(?<!\.),?[b-hj-np-z]")
        result = pattern_of_exception.sub(";\g<0>", m.group())
        return result

    case1 = pattern_of_one_variable.match(brf)
    case2 = pattern_of_variable_comma.match(brf)

    if case1:
        return "0" + pattern_of_one_variable.sub(exception_aio, brf) + "4"
    elif case2:
        return "0" + pattern_of_variable_comma.sub(exception_aio, brf) + "4"
    else:
        return brf

    ## change form: 기존의 함수로는 점역하기 어려운 구조의 latex를 점역하기 위한 함수


# 단위 기호 처리하는 함수
def unit(latex):
    if isinstance(latex, re.Match):
        latex = latex.group()

    if "\\mathrm" not in latex and "circ" not in latex:
        return latex

    pattern_of_unit1 = re.compile(r"\\mathrm{(mm|cm|m|km|g|kg)} ?(\^{[0-9]})")
    pattern_of_unit2 = re.compile(r"\\mathrm{(mm|cm|m|km|g|kg)}")

    # 온도 점역
    latex = latex.replace(
        "^{\\circ} \\mathrm{C}", "ooodCooc"
    )  # 'ooo'/'ooc' 는 영어시작표와 종료표
    # 각도 기호 점역
    latex = latex.replace("^{\\circ}", "ooodooc")

    latex = pattern_of_unit1.sub("ooo\g<1>\g<2>", latex)
    result = pattern_of_unit2.sub("ooo\g<1>ooc", latex)
    return result


def unit1(brf):
    result = brf.replace("ooo", "0").replace('ooc"', '"').replace("ooc", "4")
    return result


def mathrm(latex):
    if isinstance(latex, re.Match):
        latex = latex.group()

    if "\\mathrm" not in latex:
        return latex

    pattern_of_mathrm = re.compile(r"\\mathrm{([a-zA-Z]+)}")
    result_brf = pattern_of_mathrm.sub("\g<1>", latex)
    return result_brf


def equation_array1(latex):
    # Match를 문자열로 변환
    if isinstance(latex, re.Match):
        latex = latex.group()

    # 시작과 끝 패턴 정의
    pattern_beginning = re.compile(r"\\begin.+?[\n&]")
    pattern_ending = re.compile(r"\\end\{.+?\}\s*(\\right\.)?")

    match_begin = pattern_beginning.search(latex)
    match_end = pattern_ending.search(latex)

    # 패턴 없으면 점자로 변환하고 종료 (종료 조건)
    if not match_begin or not match_end:
        return translate_to_math_braille(latex.replace("\\ ", "wsp")).replace(
            "wsp", " "
        )

    # span 위치 찾기
    start, mid1 = match_begin.span()
    mid2, end = match_end.span()

    # content 추출 및 전처리
    content = latex[mid1:mid2].replace(r"\\", "\n").replace("&", "\n")
    if "\\begin" in content or "\\end" in content:
        content = pattern_beginning.sub("", content)
        content = pattern_ending.sub("", content)

    # 재귀 호출을 위한 나머지 부분 추출
    remaining_latex = latex[end:].replace("\\right.", "")

    # 재귀 호출 결과
    recursive_result = equation_array(remaining_latex)

    # 최종 결과 구성
    result = (
        translate_to_math_braille(latex[:start].replace("\\ ", "wsp")).replace(
            "wsp", " "
        )
        + "7'"
        + translate_to_math_braille(content).replace("\n\n", "\n").strip()
        + ",7"
        + recursive_result
    )

    return result.replace("77'", "7'").replace(
        "\n", "\n  "
    )  # '{'와 여는 연립 괄호가 겹칠 때가 있음.


def equation_array2(latex):
    pattern_of_beg = re.compile(r"\\begin{.+?}({.+?})?")
    pattern_of_end = re.compile(r"\\end{.+?}({.+?})?")

    result_beg = pattern_of_beg.sub("7'", latex)
    result_end = pattern_of_end.sub(",7WSP", result_beg)

    print(result_end)
    result = result_end.replace(r"\\", "\n")
    print(result)
    result = (
        result.replace("&", "\n")
        .replace("77'", "7'")
        .replace("\n\n", "\n")
        .replace("7'\n", "7'")
        .replace("\n,7", ",7")
    )
    return result


# 로그 점역의 편의를 위해 편집하는 함수
BREAK_CHARS = "+-*/=<>,:;&"  # 필요에 따라 구분자 추가·삭제


def is_token_char(ch: str) -> bool:
    """토큰(숫자·문자·명령어)이 계속될 수 있는지 판단"""
    return (not ch.isspace()) and ch not in BREAK_CHARS


def scan_braces(s: str, idx: int) -> int:
    """s[idx] == '{' 기준, 중첩을 고려해 짝 '}' 뒤 인덱스 반환"""
    depth = 0
    for i in range(idx, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1  # '}' 직후
    return len(s)  # 비정상이라도 안전 종료


def _skip_delim(s: str, k: int) -> int:
    """\left / \right 뒤의 실제 구분자(1글자 또는 \command)를 건너뜀"""
    if k >= len(s):
        return k
    if s[k] == "\\":  # 예: \langle, \lvert …
        k += 1
        while k < len(s) and s[k].isalpha():
            k += 1
    else:  # 예: ( , [ , | , . 등
        k += 1
    return k


def wrap_log_argument(expr: str) -> str:
    """
    \log_{base} 뒤의 진수가 { … } 로 감싸져 있지 않으면 자동 감싸기.
    이미 { … } 인 경우, 또는 진수가 아예 없는 경우는 그대로 둔다.
    """
    if "\\log" not in expr:  # 빠른 반환
        return expr

    i, n, out = 0, len(expr), []
    while i < n:
        if expr.startswith(r"\log", i):
            j = i + 4
            while j < n and expr[j].isspace():
                j += 1
            if j >= n or expr[j] != "_":  # 밑(base) 없으면 복사
                out.append(expr[i])
                i += 1
                continue

            # ── base 파싱 ─────────────────────────────────────
            j += 1
            while j < n and expr[j].isspace():
                j += 1
            if j < n and expr[j] == "{":
                base_end = scan_braces(expr, j)
            else:  # 단일 토큰
                base_end = j
                while base_end < n and is_token_char(expr[base_end]):
                    base_end += 1
            out.append(expr[i:base_end])

            # ── base 뒤 공백 skip ─────────────────────────────
            k = base_end
            while k < n and expr[k].isspace():
                k += 1
            if k < n and expr[k] == "{":  # 이미 감싸짐
                i = k
                continue

            # ── 진수(argument) 파싱 ───────────────────────────
            arg_start, stk, abs_depth = k, [], 0
            while k < n:
                # 1) 바깥쪽 \right → 종료
                if expr.startswith(r"\right", k) and not stk and abs_depth == 0:
                    break

                # 2) \left 처리
                if expr.startswith(r"\left", k):
                    stk.append(r"\left")
                    k = _skip_delim(expr, k + len(r"\left"))
                    continue

                # 3) \right 처리
                if expr.startswith(r"\right", k):
                    if stk and stk[-1] == r"\left":
                        stk.pop()
                    k = _skip_delim(expr, k + len(r"\right"))
                    continue

                ch = expr[k]
                if ch in "([{":
                    stk.append(ch)
                elif ch in ")]}":
                    if stk:
                        stk.pop()
                    else:
                        if ch == "}":  # 상위 brace 닫힘
                            break
                elif ch == "|":  # 절댓값 기호
                    abs_depth ^= 1

                # 스택·abs 깊이 0 이고 다음이 공백/구분자면 종료
                if not stk and abs_depth == 0 and (ch.isspace() or ch in BREAK_CHARS):
                    break
                k += 1

            # ── 래핑 적용 ────────────────────────────────────
            out.extend(["{", expr[arg_start:k], "}"])
            i = k
        else:
            out.append(expr[i])
            i += 1
    print("".join(out))

    return "".join(out)


# ──

# 점역의 편의를 위해 삼각함수를 편집하는 함수

# ── 헬퍼 ────────────────────────────────────────────────────────────


def is_token_char(ch: str) -> bool:
    """값(argument)에 포함될 수 있는 1글자 토큰"""
    return ch.isalnum() or ch in r"\._"


def scan_braces(s: str, idx: int) -> int:
    """s[idx]=='{' 일 때 대응 '}' 뒤 위치 반환(중첩 허용)"""
    depth = 0
    while idx < len(s):
        if s[idx] == "{":
            depth += 1
        elif s[idx] == "}":
            depth -= 1
            if depth == 0:
                return idx + 1
        idx += 1
    raise ValueError("unbalanced braces")


def wrap_trig_argument(expr) -> str:
    """
    삼각함수(\sin 등)의
      · 지수가 ^n 형태라면 {n} 으로,
      · 값(진수)이 {…} 로 감싸지지 않았다면 {…} 로
    자동 래핑.
    """
    if isinstance(expr, re.Match):
        expr = expr.group()
    TRIG_FUNCS = ("sin", "cos", "tan", "csc", "sec", "cot")
    TRIG_START_RE = re.compile(r"\\(?:" + "|".join(TRIG_FUNCS) + r")\b")

    i, n = 0, len(expr)
    out = []

    while i < n:
        m = TRIG_START_RE.match(expr, i)
        if not m:
            out.append(expr[i])
            i += 1
            continue

        func_end = m.end()  # \sin, \cos … 끝
        j = func_end

        # ── 1. 지수 처리 # 공백 skip
        while j < n and expr[j].isspace():
            j += 1
        if j < n and expr[j] == "^":
            j += 1
            while j < n and expr[j].isspace():
                j += 1
            if j < n and expr[j] != "{":
                # 숫자·변수 한 토큰을 { } 로 감싸기
                exp_start = j
                while j < n and is_token_char(expr[j]):
                    j += 1
                exponent = expr[exp_start:j]
                out.append(expr[i:exp_start])  # 함수명 + '^'
                out.append("{" + exponent + "}")
            else:
                # 이미 ^{…} 형태
                if j < n and expr[j] == "{":
                    j = scan_braces(expr, j)
                out.append(expr[i:j])
        else:
            # 지수 없음
            out.append(expr[i:j])

        # ── 2. 값(argument) 처리
        k = j
        while k < n and expr[k].isspace():
            k += 1

        # 이미 { … } 로 감싸짐?
        if k < n and expr[k] == "{":
            k = scan_braces(expr, k)
            out.append(expr[j:k])
            i = k
            continue

        arg_start = k
        par_stack, abs_depth = [], 0
        while k < n:
            # 확장 괄호
            if expr.startswith(r"\left", k):
                par_stack.append(r"\left")
                k += len(r"\left")
                continue
            if expr.startswith(r"\right", k):
                if par_stack and par_stack[-1] == r"\left":
                    par_stack.pop()
                k += len(r"\right")
                continue

            ch = expr[k]
            if ch in "([{":
                par_stack.append(ch)
            elif ch in ")]}":
                if par_stack:
                    par_stack.pop()
            elif ch == "|":
                abs_depth ^= 1
            k += 1

            # ‘\frac{…}{…} ’ + 공백 + (\pi | \theta …) 특례
            if (
                expr[arg_start:k].endswith("}")  # \frac 끝
                and k < n
                and expr[k].isspace()
            ):
                probe = k
                while probe < n and expr[probe].isspace():
                    probe += 1
                if expr.startswith(("\\pi", "\\theta", "\\alpha", "\\beta"), probe):
                    k = probe + 1  # pi 등 첫 글자 포함 후 loop 계속
                    continue

            if (
                not par_stack
                and abs_depth == 0
                and (k == n or not is_token_char(expr[k]))
            ):
                break

        argument = expr[arg_start:k]
        out.append("{" + argument + "}")
        i = k

    return "".join(out)
