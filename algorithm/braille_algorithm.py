import re
from copy import copy

from .Math_to_Braille import functions_for_translation as MathBrailleTranscribe


def convert_latex_to_braille(problem):
    PATTERN_OF_MATH_PART = re.compile(r"\\[(].+?\\[)]|\\[[].+?\\[]]", re.DOTALL)
    math_list = []  # 수식 부분을 저장할 리스트

    twice_preprocessed_problem = problem
    twice_preprocessed_problem_copy = copy(problem)

    # 수식 부분 분리하기
    math_part_matches = PATTERN_OF_MATH_PART.finditer(twice_preprocessed_problem)
    for i, j in enumerate(math_part_matches):
        starting, ending = j.span()
        math_list.append(twice_preprocessed_problem[(starting + 2) : (ending - 2)])
        twice_preprocessed_problem_copy = PATTERN_OF_MATH_PART.sub(
            f"math{i}", twice_preprocessed_problem_copy, 1
        )

    text_part = twice_preprocessed_problem_copy
    ## step2 수식 부분 점역하기
    translated_math = [
        MathBrailleTranscribe.mathBrailleTranscribe(i) for i in math_list
    ]

    # step2 점역된 수식과 텍스트 부분 합치기
    PATTERN_OF_MATH_NUMBERING = re.compile("math[0-9]+?(?=[^0-9]|$)")

    for i in translated_math:
        text_part = PATTERN_OF_MATH_NUMBERING.sub(i, text_part, 1)

    result = text_part
    return result
