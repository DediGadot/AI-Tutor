Awesome — here’s the next deliverable: a **task-ready backlog + acceptance criteria** that expands your design into buildable work. I’ve leaned on open-source tools and linked primary docs for each major choice.

---

# TUTOR\_BACKLOG.md

## 0) Scope & North Star

Build a **browser-only Hebrew tutor** that teaches a 5th-grader to code by making simple games. Sessions are **≤20 minutes**, themes are **European football, space, robots/transformers**, and the system is **agentic** (plans lessons, coaches, grades, adapts). Everything runs on your Ubuntu server **without Docker**; the learner’s Windows desktop uses only a browser.

**Core OSS pillars**

* Creative coding + physics in the browser: **p5.js**, **Matter.js**. ([p5.js][1])
* In-browser editor & tests: **Monaco**, **Mocha + Chai**. ([Microsoft GitHub][2])
* Agent orchestration: **LangGraph**; model gateway: **LiteLLM** (with optional **OpenRouter**). ([LangChain][3])
* i18n/RTL & UI: **next-intl / i18next**, **Tailwind**, **Headless UI / Radix**. ([NextIntl][4])
* Voice (optional): **Web Speech API** TTS; STT via local **faster-whisper** if needed. ([MDN Web Docs][5])
* Accessibility guardrails: **RTL with CSS logical properties**, **WCAG 2.2 target size ≥24×24**, **prefers-reduced-motion**. ([MDN Web Docs][6])
* Analytics (optional, self-host): **PostHog / Matomo / Plausible**. ([PostHog][7])

**Instructional spine** (why the UX is built this way)
Worked examples → guided practice; retrieval & spacing baked into short checks and next-day reviews. ([Teaching + Learning Lab][8])

---

## 1) Release plan (phased)

* **R1 (MVP, 3–4 weeks):** Single theme (football), one track (JS+p5), 6 lessons × 3 milestones, client-side tests, XP+badges, Hebrew/RTL, TTS.
* **R2 (Fit & polish):** Adaptive difficulty, server-side “final check,” theme switching (space/robots), parent dashboard, analytics.
* **R3 (Options):** Python track (Pyodide) and/or offline fallback model; STT.

---

## 2) Epics, user stories, and acceptance criteria

### Epic A  Playground (Editor + Runner + Tests)

**Goal:** A kid can type code, run it, and see pass/fail tests—entirely in-browser.

* **Story A1:** As a learner, I see an editor and a live canvas preview side-by-side.

  * **Acceptance:**

    * Monaco editor loads with Hebrew UI labels; preview shows `p5.js` canvas. ([Microsoft GitHub][2])
    * Layout is **RTL** and stable across 1280×720–1920×1080; targets ≥24×24 CSS px. ([MDN Web Docs][6])
* **Story A2:** As a learner, I click “Run & Check” and get Mocha/Chai results.

  * **Acceptance:**

    * Tests execute in a sandboxed iframe; pass/fail counts and titles are visible. ([Mocha][9])
    * No network access from the runner; failures never crash the page (error surfaced as a message).
* **Story A3:** As a learner, I can reduce motion if sensitive to animation.

  * **Acceptance:**

    * `prefers-reduced-motion` respected; heavy animations replaced with fades. ([MDN Web Docs][10])

**Non-functional:** First paint ≤2s on mid-range laptop; first “Run & Check” ≤1s for starter code.

---

### Epic B — Agent Brain (Planner → Projector → Coach → Grader)

**Goal:** The system plans a 20-minute lesson, provides hints, and adapts difficulty.

* **Story B1 (Planner):** As a learner, I get a 20-minute micro-plan with 3–4 milestones.

  * **Acceptance:**

    * Plan delivered in Hebrew, includes **goal**, **starter snippet** descriptor, **tests**, **XP**.
    * Plan aligns with last session’s mastery (spaced review item appears). ([Learning Attention and Perception Lab][11])
* **Story B2 (Projector):** As a learner, each milestone arrives with starter code description and tests.

  * **Acceptance:**

    * Tests are **Mocha/Chai** specs runnable in browser; titles are in Hebrew. ([Mocha][9])
* **Story B3 (Coach):** As a learner, I receive **one concise hint** at a time, in Hebrew.

  * **Acceptance:**

    * Hints follow **worked-example → faded guidance**; full solution only after ≥2 failed tries. ([Teaching + Learning Lab][8])
* **Story B4 (Grader):** As a learner, I advance when tests pass; otherwise I get targeted help.

  * **Acceptance:**

    * Passing threshold and remediation policy are consistent across lessons; coach references failing expectations by name.

**Constraint:** Orchestration uses **LangGraph** with explicit state transitions; LLMs accessed via **LiteLLM** gateway. ([LangChain][3])

---

### Epic C — Gamification & Rewards

**Goal:** Make progress feel rewarding without distracting from learning.

* **Story C1:** As a learner, I earn **XP** and **concept badges** at milestone completion.

  * **Acceptance:**

    * XP appears instantly with confetti TTS (“כל הכבוד!”); badge names map to concept taxonomy (e.g., vectors, collisions).
* **Story C2:** As a learner, I unlock **cosmetics** (ball trails, robot emotes, starfields) from **CC0** packs.

  * **Acceptance:**

    * All assets are CC0 (e.g., Kenney/OpenGameArt) and listed in a credits modal.
* **Story C3:** As a learner, my **streak** increments daily; missed days don’t penalize XP.

  * **Acceptance:**

    * Streak shown as gentle nudge; no “loss” framing.

---

### Epic D — Hebrew, RTL & Voice

**Goal:** Native-feeling Hebrew experience with optional voice prompts.

* **Story D1:** As a learner, I see right-to-left layout and Hebrew microcopy everywhere.

  * **Acceptance:**

    * Root `<html dir="rtl">`; RTL verified via **CSS logical properties** for spacing and alignment. ([MDN Web Docs][6])
* **Story D2:** As a learner, I hear short encouragements in Hebrew (TTS).

  * **Acceptance:**

    * TTS uses **SpeechSynthesis**; a toggle enables/disables voice. ([MDN Web Docs][12])
* **Story D3 (optional):** As a learner, I can **speak** short answers or commands (beta).

  * **Acceptance:**

    * STT powered by local **faster-whisper** endpoint; the UI labels feature as “Beta”; browser Web Speech **SpeechRecognition** used only when compatible. ([MDN Web Docs][13])

---

### Epic E — Parent Experience & Privacy

**Goal:** Give you visibility without storing sensitive data.

* **Story E1:** As a parent, I see **XP, badges, streaks, and concept mastery** at a glance.

  * **Acceptance:**

    * No PII beyond nickname; export of achievements as a local file or shareable image.
* **Story E2:** As a parent, I can **toggle** voice prompts, themes, and session length.

  * **Acceptance:**

    * Changes apply next session; stored locally or on your server with a child-safe profile.

---

### Epic F — Analytics (Optional, self-host)

**Goal:** Understand where the learner gets stuck; keep it privacy-friendly.

* **Story F1:** As an operator, I see funnels (open lesson → run → pass).

  * **Acceptance:**

    * One of **PostHog/Matomo/Plausible** is wired; key events captured (see §5). ([PostHog][7])

---

### Epic G — Theming & Assets

**Goal:** Swap visual themes without changing mechanics.

* **Story G1:** As a learner, I choose a theme on /play; cosmetics match that theme.

  * **Acceptance:**

    * Theme is a design-token set (palette, sounds, sprites); all assets are CC0.

---

## 3) Open design questions (resolve before build)

1. **Hint policy:** After how many failed runs does the coach reveal a worked step vs. full code? (Recommend: hint after 1 fail; code after 3). ([Teaching + Learning Lab][8])
2. **Difficulty target:** Keep first-try pass rates ≈70–85% to preserve motivation.
3. **Voice defaults:** TTS on by default? STT off by default due to inconsistent support. ([MDN Web Docs][13])
4. **Theme persona:** One coach voice across themes or distinct personas per theme?
5. **Analytics choice:** Minimal (Plausible) vs. product analytics (PostHog/Matomo). ([Plausible Analytics][14])
6. **Final check:** Client-only tests (fast) vs. add server “final check” (trust).

---

## 4) Spikes & research tasks

* **R-01:** Verify Hebrew font stack pairing (Noto Sans Hebrew / Assistant for body; Secular One for headings). Confirm license & fallback strategy. ([Google Fonts][15])
* **R-02:** p5.js + Matter.js integration patterns for simple physics (e.g., ball bounce, gravity). ([Code by Liabru][16])
* **R-03:** Measure **SpeechSynthesis** Hebrew voice availability across Edge/Chrome on Windows. ([MDN Web Docs][17])
* **R-04:** Compare **next-intl** vs. **i18next** ergonomics in CSR/SSR for Hebrew pluralization. ([NextIntl][4])
* **R-05:** LiteLLM routing policy: which model for pedagogy (Hebrew explanations) vs. code feedback. ([LiteLLM][18])
* **R-06:** WCAG 2.2 tap target audit of initial UI prototypes. ([W3C][19])

---

## 5) Telemetry events (names & intent)

* `lesson_opened`, `milestone_started`, `run_clicked`, `tests_passed`, `tests_failed`, `hint_requested`, `hint_auto_shown`, `milestone_completed`, `badge_awarded`, `session_completed`, `streak_incremented`, `tts_toggled`, `theme_changed`.
* Use **PostHog/Matomo/Plausible** depending on depth needed. ([PostHog][7])

---

## 6) Acceptance tests (representative, no code)

* **Playground (A1–A2):**

  * *Given* a first-time learner on `/learn`, *when* “Run & Check” is pressed with starter code, *then* a canvas renders and Mocha/Chai reports at least one passing and one failing test with Hebrew titles. ([Mocha][9])
* **Agent (B1–B4):**

  * *Given* a completed milestone, *when* `tests_passed` threshold is met, *then* the next milestone is announced with a single Hebrew hint and updated tests; *when* tests fail twice, *then* the coach surfaces a stronger worked step before any complete solution. ([Teaching + Learning Lab][8])
* **Gamification (C1–C2):**

  * *Given* a milestone completion, *then* XP increments and a badge popup appears; *and* a CC0 cosmetic unlock is listed in Rewards.
* **RTL/Accessibility (D1):**

  * *Given* the app root has `dir="rtl"`, *then* all page sections render with correct margins/paddings using **logical properties**; primary actions meet **24×24** target size. ([MDN Web Docs][6])
* **Voice (D2):**

  * *Given* voice is enabled, *when* a milestone completes, *then* **SpeechSynthesis** speaks a short Hebrew praise (and can be muted). ([MDN Web Docs][12])

---

## 7) Non-functional requirements

* **Performance:** First usable render ≤2s on mid-range Windows laptop; “Run & Check” round-trip ≤1s for baseline tests.
* **Privacy:** No PII beyond nickname; all code executes in a sandboxed iframe; analytics—if enabled—are cookie-less and IP-anonymized. (Plausible is cookie-less; Matomo/PostHog configurable.) ([Plausible Analytics][14])
* **Reliability:** If LLM is unreachable, fallback to cached lesson plans; if tests fail to load, show a graceful retry with offline hints.

---

## 8) Content authoring model

* **LessonPlan JSON** with `title`, `duration_min`, `theme`, `milestones[]` (`goal_he`, `starter_description`, `tests_titles_he`, `hints_he[]`, `xp`, `badge`).
* **Taxonomy:** `concepts[]` (variables, loops, conditionals, vectors, collision).
* **Spacing:** Each new lesson schedules 1–2 short review checks from prior concepts. ([augmentingcognition.com][20])

---

## 9) UX writing & visual design guidelines

* **Tone:** Encouraging, playful, concrete verbs; one task per hint.
* **Typography:** Body text in **Noto Sans Hebrew** or **Assistant**; display headings in **Secular One**. Validate legibility on Windows ClearType. ([Google Fonts][15])
* **Layout:** RTL with **logical properties**; high-contrast theme toggle; motion-reduced variant. ([MDN Web Docs][6])
* **Components:** Prefer **Headless UI** or **Radix** primitives + Tailwind utility styling to stay accessible and customize easily. ([GitHub][21])

---

## 10) Risks & mitigations

* **Browser STT inconsistency:** Default STT off; offer local **faster-whisper** backend as opt-in. ([MDN Web Docs][13])
* **Over-helping:** Enforce hint cadence; promote retrieval practice mid-session. ([colinallen.dnsalias.org][22])
* **RTL regressions:** Add visual regression snapshots for LTR/RTL pairs; use logical properties to avoid per-component flips. ([MDN Web Docs][6])

---

## 11) Build checklist (no code, stepwise)

1. **Set up** Next.js app with **Tailwind**; add **RTL** base and **next-intl**. ([Tailwind CSS][23])
2. Add **Monaco** editor and a preview panel; wire **p5.js**; confirm simple sketch renders. ([Microsoft GitHub][2])
3. Add **Mocha/Chai** test runner in an iframe; display pass/fail UI. ([Mocha][9])
4. Stand up a **LiteLLM** proxy locally; call it from the backend; add **LangGraph** state machine endpoints. ([LiteLLM][18])
5. Author **LessonPlan JSON** for 6 football lessons; validate tests and hints flow.
6. Ship **XP/badges** + **CC0 cosmetics** (Kenney/OpenGameArt) and a basic **/rewards** view.
7. Add **TTS** toggle; test Hebrew voices; ship reduced-motion variant. ([MDN Web Docs][12])
8. (Optional) Enable analytics with **Plausible** or **PostHog**; log core events. ([Plausible Analytics][14])

---

## 12) Success metrics

* **Learning velocity:** median milestones completed per 20-min session ≥3.
* **Retention:** 7-day return rate ≥60% over first month.
* **Quality:** average runs per milestone before pass 1–3; hint requests ≤2 per milestone.
* **Delight:** post-session smiley (1–5) ≥4 average.

---

If you want, I can now turn this into a **Jira-sized ticket list** (EPIC → Story → Tasks with estimates) tailored to your team size, or prioritize R1 into a 2-sprint plan.

[1]: https://p5js.org/?utm_source=chatgpt.com "p5.js"
[2]: https://microsoft.github.io/monaco-editor/?utm_source=chatgpt.com "Monaco Editor"
[3]: https://www.langchain.com/langgraph?utm_source=chatgpt.com "LangGraph"
[4]: https://next-intl.dev/?utm_source=chatgpt.com "next-intl – Internationalization (i18n) for Next.js"
[5]: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API?utm_source=chatgpt.com "Web Speech API - MDN - Mozilla"
[6]: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_logical_properties_and_values?utm_source=chatgpt.com "CSS logical properties and values - MDN"
[7]: https://posthog.com/docs/self-host?utm_source=chatgpt.com "Self-host PostHog - Docs"
[8]: https://tll.mit.edu/teaching-resources/how-people-learn/worked-examples/?utm_source=chatgpt.com "Worked Examples | Teaching + Learning Lab - MIT"
[9]: https://mochajs.org/?utm_source=chatgpt.com "Mocha - the fun, simple, flexible JavaScript test framework"
[10]: https://developer.mozilla.org/en-US/docs/Web/CSS/%40media/prefers-reduced-motion?utm_source=chatgpt.com "prefers-reduced-motion - CSS | MDN - Mozilla"
[11]: https://laplab.ucsd.edu/articles/Cepeda%20et%20al%202008_psychsci.pdf?utm_source=chatgpt.com "Spacing Effects in Learning"
[12]: https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis?utm_source=chatgpt.com "SpeechSynthesis - Web APIs - MDN - Mozilla"
[13]: https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition?utm_source=chatgpt.com "SpeechRecognition - Web APIs - MDN"
[14]: https://plausible.io/open-source-website-analytics?utm_source=chatgpt.com "Plausible: Open source Google Analytics alternative"
[15]: https://fonts.google.com/noto/specimen/Noto%2BSans%2BHebrew?utm_source=chatgpt.com "Noto Sans Hebrew"
[16]: https://brm.io/matter-js/docs/?utm_source=chatgpt.com "Matter.js Physics Engine API Docs - brm·io"
[17]: https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices?utm_source=chatgpt.com "SpeechSynthesis: getVoices() method - Web APIs - MDN"
[18]: https://docs.litellm.ai/?utm_source=chatgpt.com "LiteLLM - Getting Started | liteLLM"
[19]: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html?utm_source=chatgpt.com "Understanding SC 2.5.8: Target Size (Minimum) (Level AA)"
[20]: https://augmentingcognition.com/assets/Cepeda2006.pdf?utm_source=chatgpt.com "Distributed Practice in Verbal Recall Tasks: A Review and ..."
[21]: https://github.com/tailwindlabs/headlessui?utm_source=chatgpt.com "tailwindlabs/headlessui"
[22]: https://colinallen.dnsalias.org/Readings/2006_Roediger_Karpicke_PsychSci.pdf?utm_source=chatgpt.com "Test-Enhanced Learning - Colin Allen"
[23]: https://tailwindcss.com/?utm_source=chatgpt.com "Tailwind CSS - Rapidly build modern websites without ever ..."

