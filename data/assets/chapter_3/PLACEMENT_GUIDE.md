# Chapter 3 Image Placement Guide

This guide specifies where each diagram should be placed in `chapter_3_ru.md` for PDF generation.

## Image Placement Instructions

### 1. Game vs Plot Comparison
**File:** `data/assets/chapter_3/01_game_vs_plot_comparison.png`
**Location:** After line 23 (after the paragraph explaining that plot (Who, What, Where) is different from game, and that game is not beholden to specifics)
**Markdown:**
```markdown
![Сравнение Игры и Сюжета](data/assets/chapter_3/01_game_vs_plot_comparison.png)
```

---

### 2. Pattern Recognition in Game (Numbers 3→6→9)
**File:** `data/assets/chapter_3/02_number_pattern_game_analogy.png`
**Location:** After line 35 (after the paragraph explaining how the pattern 3→6→9 gets "locked" and must stay the same)
**Markdown:**
```markdown
![Распознавание Паттерна в Игре](data/assets/chapter_3/02_number_pattern_game_analogy.png)
```

---

### 3. Three Different Patterns from One Word (ЛУК)
**File:** `data/assets/chapter_3/03_luk_three_patterns.png`
**Location:** After line 53 (after the "Пример" section showing three different patterns from "orange" - this image uses "ЛУК" as a Russian wordplay example)
**Markdown:**
```markdown
![Три Разных Паттерна из Одного Слова](data/assets/chapter_3/03_luk_three_patterns.png)
```

---

### 4. Parrot Sketch Game Abstraction
**File:** `data/assets/chapter_3/04_game_abstraction_parrot.png`
**Status:** ⏳ PENDING - User generating with other agent
**Location:** After line 19 (after the paragraph about the bedroom sketch having the same game as Parrot Sketch)
**Markdown:**
```markdown
![Абстракция Игры из Скетча о Попугае](data/assets/chapter_3/04_game_abstraction_parrot.png)
```

---

### 5. Yes And to If Then Transition
**File:** `data/assets/chapter_3/05_yes_and_to_if_then.png`
**Status:** ✅ DONE
**Location:** After line 25 (after the paragraph explaining the shift from "Yes And" to "If...Then")
**Markdown:**
```markdown
![Переход от "Да, и..." к "Если...То"](data/assets/chapter_3/05_yes_and_to_if_then.png)
```

---

### 6. Game Makes Improv Easier
**File:** `data/assets/chapter_3/06_game_narrows_possibilities.png`
**Status:** ✅ DONE
**Location:** After line 57 (after the paragraph explaining how game narrows down limitless possibilities)
**Markdown:**
```markdown
![Игра Облегчает Импровизацию](data/assets/chapter_3/06_game_narrows_possibilities.png)
```

---

### 7. Basketball Analogy
**File:** `data/assets/chapter_3/07_basketball_game_analogy.png`
**Status:** ✅ DONE
**Location:** After line 63 (after the paragraph about sports analogy and basketball rules)
**Markdown:**
```markdown
![Аналогия с Баскетболом](data/assets/chapter_3/07_basketball_game_analogy.png)
```

---

### 8. Forest Path Metaphor
**File:** `data/assets/chapter_3/08_forest_path_metaphor.png`
**Status:** ✅ DONE
**Location:** After line 67 (after the paragraph about the forest path metaphor)
**Markdown:**
```markdown
![Метафора Дорожки через Лес](data/assets/chapter_3/08_forest_path_metaphor.png)
```

---

### 9. Game Move Sequence
**File:** `data/assets/chapter_3/09_game_moves_sequence.png`
**Status:** ✅ DONE
**Location:** After line 25 (after the paragraph explaining how game moves form a pattern, around the "If...Then" explanation)
**Markdown:**
```markdown
![Последовательность Ходов Игры](data/assets/chapter_3/09_game_moves_sequence.png)
```

---

### 10. Alternative Patterns from Same Start (3→6→9 vs 3→6→12)
**File:** `data/assets/chapter_3/10_multiple_valid_patterns.png`
**Location:** After line 43 (after the paragraph explaining that both patterns (Add 3 and Multiply by 2) are valid from the same starting point)
**Markdown:**
```markdown
![Альтернативные Паттерны из Одного Начала](data/assets/chapter_3/10_multiple_valid_patterns.png)
```

---

### 11. Scene Structure Formula
**File:** `data/assets/chapter_3/11_scene_structure_formula.png`
**Status:** ⏳ PENDING - Image not yet generated
**Location:** After line 59 (after the formula "Base Reality + First Unusual Thing → Yes And → Heighten + Expire")
**Markdown:**
```markdown
![Формула Структуры Сцены](data/assets/chapter_3/11_scene_structure_formula.png)
```

---

### 12. Breaking the Pattern (Wrong)
**File:** `data/assets/chapter_3/12_breaking_pattern_wrong.png`
**Status:** ⏳ PENDING - Image not yet generated
**Location:** After line 33 (after the paragraph explaining what happens if you "Add 2" or "Add 5" instead of following the pattern)
**Markdown:**
```markdown
![Нарушение Паттерна (Неправильно)](data/assets/chapter_3/12_breaking_pattern_wrong.png)
```

---

## Summary of Placements (in order of appearance)

1. **Line 23** → Game vs Plot Comparison ✅
2. **Line 25** → Yes And to If Then Transition ⏳
3. **Line 25** → Game Move Sequence ⏳
4. **Line 33** → Breaking the Pattern (Wrong) ⏳
5. **Line 35** → Pattern Recognition in Game (Numbers) ✅
6. **Line 43** → Alternative Patterns from Same Start ⏳ (moved to #10)
7. **Line 53** → Three Different Patterns from ЛУК ✅ (now #3)
8. **Line 57** → Game Makes Improv Easier ⏳
9. **Line 59** → Scene Structure Formula ⏳
10. **Line 63** → Basketball Analogy ⏳
11. **Line 67** → Forest Path Metaphor ⏳
12. **Line 19** → Parrot Sketch Game Abstraction ⏳

---

## PDF Generation Notes

- All images should be referenced using relative paths from the project root: `data/assets/chapter_3/`
- Images will be automatically embedded during PDF generation
- Ensure all image files exist in `data/assets/chapter_3/` before running PDF generation
- Line numbers are approximate and may need adjustment based on actual content when placing images



