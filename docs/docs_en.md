# Braille Camp Docs

[한국어](./docs_ko.md) | **English**

## Introduction

The Math_to_Braille package converts LaTeX-based mathematical expressions into Braille formats, supporting both BRF (Braille Ready Format) and Unicode Braille output. It adheres to the Korean Braille regulations for mathematics, including the February 2024 revision.

### 1) Scope and Features

- Covers mathematics defined in the Korean 2015 revised curriculum for middle and high schools.
- Accurately transcribes a wide variety of mathematical constructs such as fractions, roots, logarithms, and trigonometric functions.
- Ensures rule-compliant output for both BRF files and Unicode Braille, enabling compatibility with Braille displays and related assistive technologies.

### 2) Structure

Math_to_Braille is organized into multiple modules, each responsible for a specific part of the transcription process:

- Mapping LaTeX symbols to BRF codes.
- Converting BRF codes to Unicode Braille.
- Executing step-by-step LaTeX-to-BRF transformations.

### 3) Document Structure

This document is organized into the following sections:

1. **Introduction** – Overview of the package, scope, and purpose.
2. **Module Overview** – Description of each module and its role in the package.
3. **Notes** – Important details, caveats, and special cases to be aware of when using the modules.

## Module Overview

### 1. `brf_code`

- This module contains a dictionary named `code` used for mapping LaTeX expressions to their corresponding BRF codes.
- `Key`: LaTeX math expression. Some keys may include a combination of LaTeX and BRF.
- `Value`: `(latex_code: str, brf_code: str)` — `tuple` containing the original LaTeX code and its corresponding `BRF` code.

Example:

```
 (key -> value):
  "(" -> ("(", "8")
  "\\times" -> ("\\times", "\*")
  "\\left8" -> ("\\left(", "8")
```

### 2. `brf_to_indeterminate_letter`

- This module contains a dictionary named `indeterminate_code` used for mapping BRF codes to their corresponding Unicode Braille characters.
- `Key`: BRF code.
- `Value`: `(brf_code: str, unicode_braille: str)` — tuple containing the BRF code and its corresponding Unicode Braille representation.

### 3. `MathBrailleTranscribe`

This module contains functions for converting LaTeX-based mathematical expressions into BRF format. These functions are organized into the following categories:

1. Basic Translation – Performs a one-to-one translation of LaTeX symbols into BRF by referencing the brf_code dictionary.

2. Translation Functions for Specific LaTeX Symbols – Converts LaTeX expressions written in specific formats. This includes most mathematical constructs such as fractions, line segments, and logarithms.

3. Sophisticated Process – Edits the BRF output to comply with specific rules in the Korean Braille regulations for mathematics (e.g., adjustments required under Section 6-2 and Section 12-1).

4. Change Form – Modifies the structure or representation of LaTeX expressions to make transcription easier. For example, wrapping the argument of a logarithm in `{}` or enclosing the values of trigonometric functions in `{}`.

### Main Functions

1.  mathBrailleTranscribe
    Converts a LaTeX string directly into BRF using the complete math transcription algorithm.
    This function is recommended when you want to use the developed transcription service without modifying the code.

- Input: `latex_str` (str) – LaTeX math expression.
- Output: `str` – BRF code.

2.  translate_to_math_braille
    Executes functions from all categories except certain functions in the Change Form category, in the proper sequence for the transcription process.

- Input: `latex_str` (str) – LaTeX math expression.
- Output: `str` – BRF code.

## 3. Notes

### Main Function: `translate_to_math_braille`

- Applies the Basic Translation step first, then removes spaces from the result.
- When spacing is required under the transcription rules, a special placeholder string `WSP` is inserted. After the conversion process is complete, all `WSP` placeholders are replaced with standard spaces.
- The Greek letters _eta_, _theta_, and _chi_ are temporarily converted to `.h`, `.j`, and `.q` respectively for consistency and convenience during transcription, and then converted back to their correct Braille patterns.

### Handling of Grouping Parentheses (Korean Math Braille Regulation Section 6-2)

- The function responsible for handling grouping parentheses is `brf_parentheses` in the Sophisticated Process category.
- Grouping parentheses are initially applied to all expressions where they may be required. The `brf_parentheses` function then determines whether to retain or remove them.
- Example – processing of a fraction:
  \frac{1}{x + 1}
  → Basic Translation → \frac{#a}{x5#a}
  → frac → (x5#a)/(#a)
  → brf_parentheses → (x5#a)/#a

- If an expression does not match a case defined as “no parentheses needed” in `brf_parentheses`, the grouping parentheses are retained. This can result in some unnecessary grouping parentheses in the output.

### Compliance with Spacing Rules

- Compliance with spacing-related provisions, including Section 11 of the Korean Math Braille regulations, is not fully accurate.
