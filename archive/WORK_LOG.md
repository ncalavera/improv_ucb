# Work Log

This file tracks the development progress and decisions made during the project.

## 2024-11-19

### Completed Work

#### 1. Removed Legacy Archive Directory
- Deleted `/archive/` directory to remove confusing legacy files
- Cleaned up project structure

#### 2. Fixed PDF Generation Issues
- **Bold text rendering**: Fixed inline bold text (`**text**`) rendering in PDFs
  - Updated `jam_generator.py` to properly handle markdown bold within paragraphs
  - Now converts `**text**` to HTML `<b>text</b>` correctly in reportlab backend

#### 3. Reorganized Jam Plan Structure
- Changed plan format to show **theory first, then practice**:
  - Frameworks (key concepts) appear first
  - Exercises appear second
- This follows a logical learning flow: understand concepts, then practice them

#### 4. Built Complete Jam Plan Generation Workflow
- Created `src/jam_plan_generator.py` module with:
  - `_load_catalog_data()` - Loads frameworks and exercises from catalog
  - `_load_chapter_content()` - Loads chapter markdown files
  - `_get_russian_text()` - Uses catalog Russian translations when available
  - `_ensure_translations()` - Only translates missing Russian fields
  - `_format_jam_plan()` - Formats markdown plan with proper structure
  - `generate_jam_plan()` - Main function to generate PDF from catalog + chapters

#### 5. Implemented Catalog-First Approach
- **Primary source**: Catalog data is now the primary source for jam plans
- **Less stochastic**: Uses structured, curated catalog entries instead of re-extracting
- **Gap detection**: System detects when chapter content mentions items not in catalog
- **Smart proposals**: Proposes adding missing items to catalog when found
- **Translation strategy**: Uses existing Russian translations from catalog first, only translates when missing

#### 6. Created Interactive Workflow Framework
- `interactive_jam_plan_workflow()` - Main interactive workflow function
- `_summarize_chapter()` - Generates LLM-based chapter summaries with catalog context
- `propose_frameworks()` - Displays available frameworks from catalog for selection
- `propose_exercises()` - Displays exercises with suggested timelines
- `propose_catalog_additions()` - Proposes adding missing items to catalog
- `add_items_to_catalog()` - Adds approved items to catalog

### Workflow Design

The interactive workflow follows this structure:
1. **Load catalog data** (primary source) - structured, verified entries
2. **Generate chapter summaries** - with catalog context, detects gaps
3. **Propose catalog additions** - if items found in chapters but not in catalog
4. **User selects frameworks** - from catalog (theory/concepts)
5. **User selects exercises** - from catalog with timeline (practice)
6. **Generate PDF** - using selected catalog items

### Key Design Decisions

1. **Catalog as source of truth**: All jam plans use catalog entries, ensuring consistency
2. **Translation reuse**: Uses existing Russian translations from catalog, only translates when needed
3. **Gap detection**: Automatically identifies missing items during summarization
4. **Theory-first structure**: Frameworks before exercises for better learning flow
5. **Interactive selection**: User chooses which concepts/exercises to include

### Technical Implementation

- **Files created/modified**:
  - `src/jam_plan_generator.py` - New module for jam plan generation
  - `src/jam_generator.py` - Fixed bold text rendering
  - `WORK_LOG.md` - This file

- **Dependencies**:
  - Uses existing `CatalogManager`, `Translator`, and `JamGenerator` classes
  - Integrates with catalog CSV structure
  - Supports both reportlab and weasyprint PDF backends

### Testing

- Successfully tested with chapters 0-1
- Generated PDF: `output/jam_plans/jam_plan_chapters_0_1_20251119_084230.pdf`
- Verified catalog data loading (19 frameworks, 4 exercises)
- Confirmed Russian translation usage from catalog

## Next Steps

### Immediate
1. **Complete interactive workflow implementation**
   - Currently workflow functions print prompts but don't wait for user input
   - Need to implement actual user interaction in Cursor chat
   - User should be able to respond to proposals and make selections

2. **Test full interactive workflow**
   - Test chapter summary generation
   - Test gap detection and catalog addition proposals
   - Test framework/exercise selection
   - Verify PDF generation with selected items

### Short-term
3. **Improve chapter summarization**
   - Make summaries more focused on catalog-relevant content
   - Better integration with catalog context

4. **Enhance gap detection**
   - Improve accuracy of detecting missing items
   - Better extraction of concepts/exercises from chapter text

5. **Add exercise timeline management**
   - Allow user to specify custom durations for exercises
   - Calculate and display total time allocation
   - Validate timeline fits within total duration

### Medium-term
6. **Add validation and sanity checks**
   - Verify selected items make sense together
   - Check for logical flow (concepts before exercises that use them)
   - Validate time allocations

7. **Improve PDF formatting**
   - Better visual hierarchy
   - Add page breaks where appropriate
   - Improve readability

8. **Add catalog management features**
   - Easy way to review and edit catalog entries
   - Batch operations on catalog
   - Export/import catalog data

### Long-term
9. **Multi-chapter planning**
   - Support for planning across multiple chapters
   - Chapter progression logic
   - Prerequisite tracking

10. **Template system**
    - Save and reuse jam plan templates
    - Common plan structures
    - Quick plan generation from templates

## 2025-11-19

### Fixed Missing Chapter 2 Review Text
- Added rule-based OCR auto-detection in `src/pdf_processor.py`. The extractor now measures alpha vs symbol ratios plus word runs and forces OCR when the base text is clearly garbled.
- Exposed tuning knobs via `PDFProcessor.__init__` so future books can adjust thresholds without editing the method logic.
- Regenerated `data/chapters/chapter_2.md`; the Chapter Review and exercise list (book page 61) now appear alongside the rest of the chapter.
- Created a `.venv` with `pdfplumber` and `pytesseract` installed so OCR fallback is available locally (requires the `tesseract` binary in PATH).

### Sequential Russian Jam Plans and Session Logging (Session 2)

#### Requirements Established via Socratic Dialogue
The user clarified requirements for jam plans through structured questions:

**Primary Purpose:**
- Single unified text that works as both facilitator guide and participant reference (no big distinction needed)
- Plans should be in **Russian** (catalog entries are English-first, then translated to Russian)

**Session Flow:**
- **Sequential, not separated**: Theory and exercises interleaved step-by-step
- Each step: explain concept → do exercise → next concept → next exercise
- Follows book's logical framework structure
- Flexible in execution (can skip/modify as needed)

**Time Management:**
- Rough estimates only (not strict timelines)
- Account for reality: 3-hour jam = ~30 min late arrivals + ~30 min warm-up + ~2 hours main work
- Bias towards "things take longer than planned"

**Theory & Exercise Depth:**
- Full explanations of each framework (but more concise than the book)
- Full step-by-step instructions for exercises
- Group context: 6-10 people, with adaptation notes

**What Makes a "Best" Plan:**
- Clear framework reference (details matter for experimentation)
- Immediately usable without extra prep
- Accounts for lessons learned from previous sessions

**Session Logging Requirements:**
- Human-readable CSV format (`data/session_logs.csv`)
- Log: what was covered, how it went, participant feedback, timing issues
- Use past session data to learn and improve future plans
- Future: account for recordings/transcripts when available

**First Session Retrospective (Last Friday, 2025-11-14):**
- Covered: Chapter 1 + parts of Chapter 2 (commitment/realistic behavior exercises)
- What worked: "Folding the laundry" exercise, "three-phrase base reality" exercise
- What didn't work: Everyone giving feedback at once made some feel attacked
- Lesson learned: Need structured, softer feedback (one person at a time, adapt to sensitivity)
- Next session plan: Thoroughly refresh base reality (Chapter 1), then revisit Chapter 2 commitment exercises

#### Completed Work

**1. Chapter 2 Extraction**
- Extracted Chapter 2 from UCB PDF using `PDFProcessor.save_chapter(2)`
- Saved to `data/chapters/chapter_2.md` with standard header format
- Verified content includes full chapter text (323 pages, book pages 36-371)

**2. Catalog Data for Chapters 1-2**
- Existing `data/catalog.csv` already contains comprehensive entries for chapters 0-1:
  - 19+ frameworks (Base Reality, Who/What/Where, Yes And, Initiation, Object Work, etc.)
  - 4 exercises (EXERCISE: FIND YES AND IN A REAL CONVERSATION, EXERCISE: CHARACTER OF THE SPACE, EXERCISE: THREE LINE SCENES, EXERCISE: FOLD LAUNDRY WHILE TALKING)
- All chapter 1 entries have both English and Russian translations
- Chapter 2 extraction attempted but JSON parsing error occurred (extractor returned 0 entries)
- **Note**: Chapter 2 catalog entries may need manual verification/addition

**3. Redesigned Jam Plan Format to Sequential Russian Flow**
- **Replaced** old "theory section → exercises section" layout with **single sequential flow**
- Updated `JamPlanGenerator._format_jam_plan()` in `src/jam_plan_generator.py`:

  **New Structure:**
  - **Header/Meta (Russian)**: Title, creation date, duration, chapters used
  - **"Кратко о сессии"**: Brief overview of what will happen in the session
  - **"Принципы обратной связи на всю сессию"**: Built-in feedback guidelines based on first session lessons:
    - One person gives feedback at a time
    - Adapt feedback style to player sensitivity (soft vs. direct)
    - Focus on observable behavior, not personalities
  - **"Пошаговый план (основная часть)"**: Sequential steps that interleave theory and practice:
    - Each step pairs a framework (concept) with an exercise
    - Format: `### Шаг N. [Framework Name] + [Exercise Name] (~X минут)`
    - Each step includes:
      - **Концепция**: Russian description + how-to from catalog
      - **Упражнение**: Full Russian instructions for 6-10 person group
      - Reminder about structured, sensitive feedback during debrief
    - Rough time estimates per step (derived from total duration)
  - **"Контекст из глав"**: Optional brief excerpts from chapter markdown files (for facilitator reference only)

- Plans are now **fully in Russian** and follow logical book framework order
- Maintains flexibility: works for any chapter list, adaptable to group needs

**4. Session Logging System**
- Created new module `src/session_logger.py` with `SessionLogger` class
- **CSV Format**: `data/session_logs.csv` with columns:
  - `SessionID`, `Date`, `JamPlanFile`, `Chapters`, `DurationMinutes`, `GroupSize`
  - `FrameworksUsed`, `ExercisesUsed` (semicolon-separated lists)
  - `WhatWorked`, `WhatDidntWork`, `TimingIssues`, `ParticipantFeedback`, `FacilitatorNotes`
  - `RecordingDate`, `RecordingPath`, `TranscriptPath` (for future recording integration)
- **API**: `log_session_result(...)` convenience function for easy logging
- Human-readable format, can be opened in any spreadsheet
- Supports retroactive logging of past sessions

**5. Files Created/Modified**
- `src/jam_plan_generator.py` - Redesigned `_format_jam_plan()` method
- `src/session_logger.py` - New module for session logging
- `data/chapters/chapter_2.md` - Extracted Chapter 2 content
- `WORK_LOG.md` - This entry

#### Technical Notes

**Import Path Issues:**
- Module imports use relative paths (`from catalog_manager import CatalogManager`)
- When running scripts directly, Python path may need adjustment
- Workaround: Run from project root or use `python -m` syntax, or adjust `PYTHONPATH`

**Chapter 2 Catalog Status:**
- FrameworkExercisesExtractor encountered JSON parsing error when processing Chapter 2
- May need manual catalog entry addition or re-extraction with improved error handling
- Current catalog has rich Chapter 1 data that is sufficient for initial jam plans

**Jam Plan Generation:**
- New sequential format is implemented and ready to use
- To generate a plan: `from src.jam_plan_generator import JamPlanGenerator; gen = JamPlanGenerator(); gen.generate_jam_plan([1, 2], duration=120)`
- Output: Russian PDF with sequential theory→exercise flow

#### Next Steps for New Agent

**Immediate Priority: Generate and Refine Example Jam Plan**

1. **Generate Initial Plan for Chapters 1-2**
   - Use `JamPlanGenerator.generate_jam_plan([1, 2], duration=120)` to create first version
   - Review the generated PDF/markdown output
   - Verify Russian translations are clear and complete

2. **Socratic Dialogue to Refine Plan**
   The user needs to answer these questions to tailor the plan to their group:

   **Question 1: How many concept-exercise cycles in 2-hour main part?**
   - a) 2-3 deep cycles (more time per topic, lots of repetition)
   - b) 4-5 medium cycles
   - c) More cycles, but each kept very short

   **Question 2: Priority for second session?**
   - a) Strong refresh of base reality (Who/What/Where, object work, talk about something else), THEN short revisit of commitment from Chapter 2
   - b) Quick refresh of base reality, THEN focus mainly on commitment and realistic behavior
   - c) 50/50 split between base reality and commitment work

   **Question 3: Default feedback tone for sensitive commitment exercises?**
   - a) Very soft and supportive by default, harsher feedback only if explicitly requested
   - b) Neutral but clear: name issues directly, but always framed as "what you can try next"
   - c) Quite direct and technical by default, with opt-out for more sensitive players

3. **Iterate on Plan Structure**
   - Based on user answers, adjust:
     - Number of steps and time allocation per step
     - Which exercises come first (base reality vs. commitment)
     - Feedback guidance wording in each step
   - May need to modify `_format_jam_plan()` logic if structural changes are needed
   - Generate updated PDF and review with user

4. **Log First Session Retroactively**
   - Use `SessionLogger.log_session_result()` to log the first session (last Friday, 2025-11-14)
   - Include all the retrospective data provided by user:
     - What worked: "Folding the laundry", "three-phrase base reality"
     - What didn't: simultaneous feedback, some felt attacked
     - Lessons: need structured, one-person-at-a-time feedback
   - This creates the foundation for data-driven improvements

5. **Future Enhancements (After Example Plan is Refined)**
   - Add Chapter 2 catalog entries if missing (may need manual extraction or improved error handling)
   - Consider adding exercise selection/filtering logic to `JamPlanGenerator` (currently uses all available)
   - Add helper to load past session logs and show history when creating new plans
   - Integrate recording/transcript paths when user starts using recordings

#### Key Files Reference

- **Jam Plan Generation**: `src/jam_plan_generator.py` - `JamPlanGenerator` class, `_format_jam_plan()` method
- **Session Logging**: `src/session_logger.py` - `SessionLogger` class, `log_session_result()` function
- **Catalog Data**: `data/catalog.csv` - Main source of truth for frameworks and exercises
- **Chapter Files**: `data/chapters/chapter_1.md`, `data/chapters/chapter_2.md` - English chapter text
- **Output**: `output/jam_plans/` - Generated PDF jam plans
- **Session Logs**: `data/session_logs.csv` - Session history (to be created on first log)

#### User Context for Next Agent

- **User's Group**: 6-10 people, improv jam sessions
- **Session Format**: 3 hours total (~30 min late arrivals, ~30 min warm-up, ~2 hours main work)
- **Language**: All jam plans must be in Russian
- **First Session Date**: Last Friday (2025-11-14) - already completed, needs retroactive logging
- **Next Session**: Planning for chapters 1-2, focus on base reality refresh + commitment exercises
- **Feedback Sensitivity**: Group includes people who don't like harsh criticism; need adaptive, supportive approach

## 2025-11-19 (Evening)

### Jam Plan Structure for Session 2 (Chapters 1-2)

**Duration**: 120 minutes

**Block Structure** (3 blocks):

1. **Block 1: Построение платформы (Platform Building)**
   - Frameworks: Who/What/Where, Base Reality
   - Exercise: EXERCISE: THREE LINE SCENES

2. **Block 2: Объектная работа (Object Work)**
   - Frameworks: Character of the Space, Show Don't Tell, Talk About Something Else, Agreement (Physical/Emotional State)
   - Exercises: EXERCISE: FOLD LAUNDRY WHILE TALKING, EXERCISE: CHARACTER OF THE SPACE

3. **Block 3: Обязательство (Commitment)**
   - Framework: Commitment
   - Exercise: EXERCISE: GIVE THE SETUP (4-step exercise)

**Key Requirements**:
- Use exact exercise instructions from chapter content (not catalog summaries)
- Generate separate Russian and English PDFs
- Clean formatting without repetitive headlines
- Format should match chapter style
- Focus on Chapter 1 foundation, with Chapter 2 commitment as supporting work

**Generated Files**:
- `output/jam_plans/jam_plan_blocks_20251119_182832_ru.pdf` (Russian)
- `output/jam_plans/jam_plan_blocks_20251119_182832_en.pdf` (English)

## 2025-11-20

### Session 2 Jam Plan - Markdown-First Approach

**New Workflow Established:**
Created first jam plan as English markdown file before translation, allowing for easier review and iteration.

**File Created:**
- `output/jam_plans/session_2_jam_plan_en.md` - English markdown jam plan

**Jam Plan Structure:**

**Duration:** 120 minutes (2 hours main work)

**Block Structure** (3 blocks):

1. **Block 1: Platform Building (35-40 minutes)**
   - Concepts: Who/What/Where, Base Reality
   - Exercise: THREE LINE SCENES (Chapter 2)

2. **Block 2: Object Work & Space (55-60 minutes)**
   - Concepts: Character of the Space, Show Don't Tell, Talk About Something Else
   - Exercises:
     - CHARACTER OF THE SPACE (Chapter 1, group adaptation for 6-10 people)
     - SILENT OBJECT WORK (Chapter 1, from CHARACTER OF THE SPACE exercise)
     - TALK ABOUT SOMETHING ELSE (Chapter 1)

3. **Block 3: Commitment (25-30 minutes)**
   - Concept: Commitment, Top of Your Intelligence
   - Exercise: GIVE THE SETUP (Chapter 2, all 4 parts)

**Key Design Decisions:**

1. **Exercise Verification:** All exercise names and instructions verified against actual chapter content
   - Corrected "FOLD LAUNDRY WHILE TALKING" → "TALK ABOUT SOMETHING ELSE"
   - Replaced creative interpretation with actual "GIVE THE SETUP" 4-part structure from book

2. **Group Adaptations:** 
   - CHARACTER OF THE SPACE: Adapted from book's two-person format to whole-group format (everyone moves through spaces together)
   - SILENT OBJECT WORK: Added as warm-up before TALK ABOUT SOMETHING ELSE
   - All exercises include specific adaptations for 6-10 person groups

3. **Sequential Flow:** Each block follows concept → exercise pattern for immediate practice

4. **Feedback Integration:** Built-in feedback principles from Session 1 lessons:
   - One person at a time
   - Adapt to sensitivity
   - Focus on observable behavior
   - Frame as "what to try next"

5. **Facilitator Support:** Includes timing flexibility notes, energy management tips, and common issues to watch for

**Next Steps:**
- ~~Translate to Russian markdown~~ ✅ Completed: `output/jam_plans/session_2_jam_plan_ru.md`
- Generate PDF versions (Russian and English) - optional
- Test with actual session and log results

**Files Created:**
- `output/jam_plans/session_2_jam_plan_en.md` - English markdown jam plan
- `output/jam_plans/session_2_jam_plan_ru.md` - Russian markdown jam plan


## 2025-11-23

### Architectural Shift: Removing Catalog System
- **Decision**: Removed the `catalog.csv` and intermediate extraction step.
- **Reasoning**: The structured catalog was adding unnecessary complexity and friction. Working directly with the original chapter text (`data/chapters/*.md`) allows for more flexible and accurate jam plan generation using LLMs.
- **Changes**:
  - Removed `src/catalog_manager.py`
  - Removed `src/framework_exercises_extractor.py`
  - Removed `data/catalog.csv`
  - Refactored `src/jam_plan_generator.py` to generate plans directly from text.

### Code Cleanup: Removing Redundant Jam Plan Files
- **Decision**: Archived legacy jam plan generation files
- **Reasoning**: After catalog removal, `JamGenerator` (template-based) became redundant. Current workflow uses `JamPlanGenerator` (LLM-based) exclusively.
- **Changes**:
  - Archived `src/jam_generator.py` → `archive/jam_generator.py`
  - Archived `scripts/create_jam_plan.py` → `archive/create_jam_plan.py`
  - Created `archive/README.md` documenting why files were archived
  - Updated `README.md` to reflect LLM-based workflow
  - Updated architecture documentation to show 7 core components (was 8)

**Current Workflow (Simplified):**
```
Chapter PDF → PDFProcessor → ChapterFormatter → Chapter Markdown
                                                        ↓
                                                 JamPlanGenerator (LLM)
                                                        ↓
                                                 Jam Plan Markdown
                                                        ↓
                                                  PDFGenerator
                                                        ↓
                                                 Versioned PDF
```
