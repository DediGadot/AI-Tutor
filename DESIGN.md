Below is a design brief you can hand to an implementation team (or a coding LLM). I’ve leaned heavily on **open‑source** stacks and included **source citations** for the key framework and UX principles you’ll want to rely on.

---

# TUTOR.md

## 1) Product vision

Build a **browser‑based, agentic AI tutor in Hebrew** that teaches a 5th‑grader to code by creating **simple games** (football, space, robots/transformers themes). Sessions are **micro‑lessons up to 20 minutes**, playable on a Windows desktop with always‑on internet, but running entirely in the **browser** (no desktop installs). The server is Ubuntu (no Docker), which hosts the API, model gateway, and data.

**Core outcomes**

* The learner completes **hands‑on game milestones** with immediate visual feedback.
* The agent **plans, coaches, evaluates, and adapts** difficulty live.
* The experience is **fun and safe**: code runs in a sandboxed iframe; minimal data; no social features.
* The interface is **Hebrew‑first + RTL** and follows kid‑friendly accessibility patterns (large tap/click targets, legible fonts, supportive feedback). ([W3C][1])

---

## 2) Open‑source & platform choices (why these)

**Creative coding & simple physics (in the browser)**

* **p5.js** for sketching/drawing and game loops (friendly for beginners; huge education community). ([p5.js][2])
* **Matter.js** for light 2D physics (bounces, gravity, collisions) when needed. ([Code by Liabru][3])

**In‑browser editor + tests**

* **Monaco Editor** (the VS Code editor in the browser) for code editing. ([Microsoft GitHub][4])
* **Mocha + Chai** to run milestone tests **in the browser**; serial tests, clear pass/fail. ([Mocha][5])

**Agentic orchestration + LLM gateway**

* **LangGraph** for an explicit, controllable agent state machine (planner → projector → coach → grader). ([Langchain AI][6])
* **LiteLLM proxy** as a **local** LLM gateway (swap Claude/Gemini/Qwen/OpenRouter routes behind one OpenAI‑style endpoint; logs/quotas). ([LiteLLM][7])
* Optional **OpenRouter** if you want a single API to many hosted models with fallback logic. ([OpenRouter][8])
* (Optional offline/local): **Ollama** for running local OSS models if internet is down or for privacy experiments. ([Ollama Documentation][9])

**Hebrew / RTL & UI framework**

* **i18next / next‑i18next** (or `next-intl`) for localization and message catalogs. ([i18next][10])
* RTL & layout via **CSS logical properties** + `dir="rtl"` (MDN guidance). ([MDN Web Docs][11])
* UI scaffolding with **Tailwind CSS** + **Headless UI** or **Radix Primitives** for accessible components. ([Tailwind CSS][12])

**Voice (optional, motivational)**

* **Web Speech API**: browser **TTS** (SpeechSynthesis) for short coach prompts; STT is possible but has limited, inconsistent browser support—use server STT if needed. ([MDN Web Docs][13])
* **faster‑whisper** server (Hebrew capable) if you want **reliable STT** via your Ubuntu box. ([GitHub][14])

**Analytics (self‑host, optional)**

* **PostHog** or **Matomo** (self‑host, open‑source) for product analytics; **Plausible** as lightweight privacy‑friendly page analytics. ([GitHub][15])

**Assets / theming**

* **Kenney** and **OpenGameArt** CC0 packs for badges, icons, sounds, football/space/robot sprites (no licensing headache). ([Kenney][16])

**Hebrew fonts**

* **Noto Sans Hebrew**, **Assistant**, or **Secular One** (Google Fonts). ([Google Fonts][17])

---

## 3) UX principles for a 5th‑grader (age \~10–11)

* **Micro‑lessons (≤20 minutes)** with clear starts/finishes and visible progress bars.
* **Worked examples → minimal viable code** → **guided practice** (reduces cognitive load; then shift to retrieval practice/testing). ([Wikipedia][18])
* **Retrieval practice & short checks**: quick “run tests” cycles and small quizzes; it strengthens memory (testing effect). ([Psychnet][19])
* **Spaced practice** across sessions: revisit prior concepts with new themes (football → robots → space) to promote durable learning. ([PMC][20])
* **Kid‑appropriate targets & feedback**: large hit areas and immediate, upbeat feedback. Aim for **≥24×24 CSS px** targets. ([W3C][21])
* **Narrow scope per step**: one micro‑goal at a time (“add velocity vx, then bounce off wall”), visible in the UI.

---

## 4) Core user journeys

### 4.1 First‑time setup (parent)

1. Parent opens the site, picks **Hebrew** and **theme** (default: European football).
2. Brief **safety & privacy note**; create **nickname** (no PII), choose **session length** (20m default).
3. Tutorial shows **editor + preview + “Run & Check”** and how badges/XP unlock.

### 4.2 Lesson flow (student)

**Timeline (20 minutes)**

* **0–2m**: Onboarding comic panel with the theme coach (robot/astronaut/coach) + one worked example. ([Wikipedia][18])
* **2–15m**: Milestone loop ×3–4

  * Goal in Hebrew (short), **starter code scaffold** in editor, **Run & Check** to see tests.
  * The **coach** suggests one tiny change at a time; immediate pass/fail marks.
* **15–18m**: **Boss check** (one combined test) → award **XP + badge** and show a replay GIF.
* **18–20m**: **Reflection**: “מה למדת היום?” choose 1–2 statements (retrieval); schedule the next mission (spaced revisit). ([PMC][22])

### 4.3 Parent dashboard (optional)

* See **streaks**, **badges**, and **concept mastery** (arrays, loops, conditions).
* Toggle **voice prompts** and **theme**.
* Export a **shareable GIF** of the game moment (local render, no uploads).

---

## 5) Information architecture (IA)

* **/play** → lesson selector (football / space / robots / transformers)
* **/learn/\[track]/\[lesson]** → editor + preview + tests panel
* **/rewards** → badges, levels, inventory (cosmetic only)
* **/parent** → progress, toggles, privacy note
* **/settings** → fonts, voice on/off, color contrast mode

---

## 6) Gamification economy (lightweight & intrinsic)

* **XP**: 10–25 per milestone; **level up** each 100 XP (increasing threshold).
* **Badges**: per concept (e.g., “בועט‑ע” for vectors, “אסטרונאוט/ית מסלול” for gravity).
* **Streak**: +1 per day; **streak saver** consumable earned every 5 completions.
* **Cosmetics**: unlock **ball trails**, **spaceship skins**, **robot emotes** (all CC0 assets). ([Kenney][23])
* **No shops, no currency purchases**; everything earned via play.

---

## 7) Theming system (football, space, robots/transformers)

* **Palette & sounds** swap by theme; mechanics stay constant (minimize cognitive load).
* Provide **2–3 scene templates** per theme (e.g., *Penalty Kick*, *Orbit Runner*, *Robot Bumper Arena*).
* Asset packs sourced from **Kenney / OpenGameArt** (CC0). ([Kenney][16])

---

## 8) Coach tone & Hebrew content style

* Tone: **encouraging, concise, playful**, second person singular.
* Microcopy examples:

  * “בוא/י נוסיף מהירות אופקית (vx). שתי שורות וזהו.”
  * “יש! עברת שני מבחנים—ממשיכים לבעיטה מעגלית.”
* Use **Assistant** or **Noto Sans Hebrew** for UI (good legibility), **Secular One** for badges/headlines. ([Google Fonts][24])

---

## 9) Accessibility checklist (kids + Hebrew)

* **RTL layout** (`<html dir="rtl">` + CSS **logical properties** like `margin-inline-start`). ([MDN Web Docs][25])
* Touch/click targets ≥ **24×24 CSS px** (WCAG 2.2 AA). ([W3C][21])
* **High contrast** color mode toggle.
* **Voice prompts** via Web Speech TTS; note STT is **limited cross‑browser**, so use server STT (**faster‑whisper**) when needed. ([MDN Web Docs][26])
* Animations are **short and purposeful**; reduce motion toggle.
* Reading load: short Hebrew sentences; pictograms alongside text (Headless/Radix components are accessible). ([headlessui.com][27])

---

## 10) Agent design (LangGraph)

**Nodes & responsibilities**

* **Planner**: builds a 20‑min plan (Hebrew), aligns with prior mastery, sets 3–4 milestones.
* **Projector**: emits **starter code deltas**, **test specs** (Mocha/Chai), and hints. ([Mocha][5])
* **Coach**: keeps hints atomic; uses **worked example → faded guidance** pattern; triggers retrieval prompts. ([Wikipedia][18])
* **Grader**: ingests test results, decides **advance vs. remediate**, awards **XP/badges**.

**Why LangGraph**: explicit graph/state, **reliability/controllability**, persistence, and human‑in‑the‑loop affordances when needed. ([Langchain AI][28])

**Model routing (LiteLLM)**

* Default: **router** across hosted models (Claude/Gemini/Qwen) for best Hebrew/code quality vs. cost.
* Fallbacks: set **per‑tool routes** (e.g., coding hints → model A; tone/style → model B). ([LiteLLM][7])
* Optional: **OpenRouter** for consolidated access/fallback behavior. ([OpenRouter][8])

---

## 11) Evaluation & testing strategy

* **Milestone tests** (Mocha/Chai) visible to the learner for tight feedback loops. ([Mocha][5])
* **Server verification** (optional) for “final checks” to prevent gaming client tests.
* **Static analysis** (Esprima/Acorn) for gentle hints (e.g., “נראה שלא קראת לפנקציה `kick()`”). ([Esprima][29])
* **Telemetry** (Matomo/PostHog/Plausible) to spot stuck steps and refine hints. ([Analytics Platform - Matomo][30])

---

## 12) Privacy & safety

* Single local profile (nickname only), **no PII**, no uploads; **all code runs in a sandboxed iframe**.
* Asset licensing: use **CC0** packs only; document sources per theme. ([Kenney][16])
* Voice: TTS stays on device; STT uploads audio only to **your** Ubuntu STT endpoint if enabled.

---

## 13) “No‑Docker” server plan (Ubuntu)

* **Processes** managed by `systemd`:

  * **Model gateway**: LiteLLM proxy (OpenAI‑compatible endpoint). ([LiteLLM][7])
  * **API**: FastAPI app exposing `/agent/tick`, `/grade`, `/rewards`.
  * **STT** (optional): faster‑whisper HTTP server for Hebrew. ([GitHub][14])
  * **Web**: Next.js app (served via Nginx).
* **Data**: PostgreSQL for sessions, XP, badges.

---

## 14) Content model (how lessons are authored)

**LessonPlan JSON**

* `title`, `duration_min`, `theme`
* `milestones[]`: `{id, goal_he, starter_code, tests_spec, hints_he[], xp, badge}`
* `prereqs[]`: concept tags, e.g., `["variables","loops","collision"]`
* `review_items[]`: quick retrieval prompts from prior sessions (for spacing). ([PMC][20])

**Theme extensions**

* Each milestone can optionally reference `assets.themeKey` (ball sprite, robot emoji, starfield).

---

## 15) Detailed UX decisions (to answer before build)

1. **Coach persona** per theme: one unified voice or different personas?
2. **Difficulty curve**: target **70–85%** first‑try pass rate (tune tests to encourage short retries).
3. **Hint reveal policy**: after N failed runs or by explicit request?
4. **Final check** server‑side or client‑only (trade cost vs. anti‑cheat)?
5. **Voice** defaults: TTS on? STT off by default? (STT is limited across browsers). ([MDN Web Docs][26])
6. **Parent controls**: turn off themes (e.g., transformers), require “ask‑to‑proceed” between milestones?
7. **Analytics**: enable **privacy‑first** page analytics (Plausible) vs. richer product analytics (PostHog/Matomo). ([Plausible Analytics][31])
8. **Fonts**: Assistant vs. Noto Sans Hebrew for body; Secular One for headings—pick one combo. ([Google Fonts][24])
9. **Badge art**: select CC0 packs (Kenney) and map to concept taxonomy. ([Kenney][23])

---

## 16) Session design (example: “פנדלים – בעיטה ראשונה”)

* **Goal**: Ball moves with vx/vy; `kick(angle,power)` updates velocity.
* **Starter code**: Minimal canvas + ball.
* **Tests** (Mocha/Chai):

  * `vx` and `vy` exist, numeric.
  * `kick()` changes velocity based on angle/power.
  * Ball stays within bounds (bounce or clamp). ([Mocha][5])
* **Coach hints**:

  1. “נגדיר משתנה `vx` ונעדכן את `x` בכל פריים.”
  2. “נוסיף `vy` ונתחיל לנוע באלכסון.”
  3. “נחשב `vx = power * cos(angle)` ו‑`vy = power * sin(angle)`.”
* **Reward**: Badge “בועט‑על” + 20 XP; unlock a **ball trail** cosmetic (CC0). ([Kenney][23])

---

## 17) Measuring learning (beyond XP)

* **Concept mastery**: per concept, store `last_pass_at`, `fail_count`, and a rolling score; surface to Planner for adaptive sequencing (spaced retrieval). ([PMC][20])
* **Time‑in‑hint vs. time‑in‑code** ratio as a frustration proxy.
* **Qualitative prompts**: 1–2 reflective questions at the end (“מה היה מאתגר?”, “מה עזר לך?”).

---

## 18) Roadmap

**Phase 1 (MVP)**

* One track (football) with 6 lessons × 3 milestones each.
* Agent loop (Planner → Projector → Coach → Grader), client‑side tests, XP/badges, TTS.
* RTL + Hebrew UI; large hit areas; dark/light themes.

**Phase 2**

* Add **server‑side final checks**, **adaptive spacing** of review items, and **theme switching** (space/robots).
* Parent dashboard; **streaks** and **cosmetics inventory**.

**Phase 3**

* Optional **Python track** (Pyodide or pygbag‑based playground), if desired for variety. ([Pyodide][32])

---

## 19) Risks & mitigations

* **Browser STT** inconsistency → default to **TTS only**; server STT via faster‑whisper when needed. ([MDN Web Docs][26])
* **Over‑helping** by the agent → apply **worked examples** only at start; shift to **retrieval/testing** mid‑lesson. ([Wikipedia][18])
* **Cognitive overload** → one clear micro‑goal per step; keep hints short; use visual scaffolds (p5.js canvas). ([p5.js][2])
* **Licensing** → CC0 assets only (Kenney/OpenGameArt). ([Kenney][16])
* **RTL glitches** → use CSS logical properties + `dir="rtl"` at root; test frequently. ([MDN Web Docs][11])

---

## 20) Acceptance criteria (MVP)

1. **Open /play** → choose football → **/learn** opens with Hebrew UI and RTL by default. ([MDN Web Docs][25])
2. Editor (Monaco) + preview; **Run & Check** shows Mocha results with pass/fail counts. ([Microsoft GitHub][4])
3. Agent returns **Hebrew hints** and **tests**; tests update after each run; advancing milestones awards XP & a CC0 badge. ([Kenney][23])
4. **Targets** (buttons, toggles) meet **≥24×24 CSS px** requirement. ([W3C][21])
5. Session ends in ≤20 minutes with a reflection prompt and scheduled review item for next time (spaced revisit). ([PMC][20])

---

### Appendix A — Key references

* p5.js (creative coding): official site & reference. ([p5.js][2])
* Matter.js (physics): docs & site. ([Code by Liabru][33])
* Monaco Editor: docs & repo. ([Microsoft GitHub][34])
* Mocha/Chai (browser tests): official docs. ([Mocha][5])
* LangGraph (agent orchestration): docs. ([Langchain AI][6])
* LiteLLM (LLM gateway): docs. ([LiteLLM][7])
* OpenRouter (multi‑model): docs. ([OpenRouter][8])
* i18next / next‑i18next / next‑intl (i18n for Next.js). ([i18next][10])
* RTL & CSS logical properties (MDN). ([MDN Web Docs][11])
* WCAG 2.2 AA target size (≥24×24). ([W3C][21])
* Web Speech API (TTS/STT) status (MDN). ([MDN Web Docs][35])
* faster‑whisper (ASR): repo. ([GitHub][14])
* Fonts (Hebrew): Noto Sans Hebrew, Assistant, Secular One. ([Google Fonts][17])
* Analytics: PostHog, Matomo, Plausible. ([GitHub][15])
* Gamification assets: Kenney & OpenGameArt (CC0). ([Kenney][16])
* Learning science: worked examples, retrieval practice, spacing. ([Wikipedia][18])

---

**Ready for build:** The next step is to translate this design into a minimal backlog (tickets per section). If you’d like, I can convert each section into actionable tasks and acceptance tests for your team.

[1]: https://www.w3.org/TR/WCAG22/?utm_source=chatgpt.com "Web Content Accessibility Guidelines (WCAG) 2.2"
[2]: https://p5js.org/?utm_source=chatgpt.com "p5.js"
[3]: https://brm.io/matter-js/?utm_source=chatgpt.com "Matter.js - a 2D rigid body JavaScript physics engine - brm·io"
[4]: https://microsoft.github.io/monaco-editor/?utm_source=chatgpt.com "Monaco Editor"
[5]: https://mochajs.org/?utm_source=chatgpt.com "Mocha - the fun, simple, flexible JavaScript test framework"
[6]: https://langchain-ai.github.io/langgraph/?utm_source=chatgpt.com "LangGraph - GitHub Pages"
[7]: https://docs.litellm.ai/?utm_source=chatgpt.com "LiteLLM - Getting Started | liteLLM"
[8]: https://openrouter.ai/docs/quickstart?utm_source=chatgpt.com "OpenRouter Quickstart Guide | Developer Documentation"
[9]: https://ollama.readthedocs.io/en/?utm_source=chatgpt.com "Home - Ollama English Documentation"
[10]: https://www.i18next.com/?utm_source=chatgpt.com "i18next documentation: Introduction"
[11]: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_logical_properties_and_values?utm_source=chatgpt.com "CSS logical properties and values - MDN"
[12]: https://tailwindcss.com/?utm_source=chatgpt.com "Tailwind CSS - Rapidly build modern websites without ever ..."
[13]: https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis?utm_source=chatgpt.com "SpeechSynthesis - Web APIs - MDN - Mozilla"
[14]: https://github.com/SYSTRAN/faster-whisper?utm_source=chatgpt.com "Faster Whisper transcription with CTranslate2"
[15]: https://github.com/PostHog/posthog?utm_source=chatgpt.com "PostHog provides open-source web & product analytics ..."
[16]: https://kenney.nl/support?utm_source=chatgpt.com "Support"
[17]: https://fonts.google.com/noto/specimen/Noto%2BSans%2BHebrew?utm_source=chatgpt.com "Noto Sans Hebrew"
[18]: https://en.wikipedia.org/wiki/Worked-example_effect?utm_source=chatgpt.com "Worked-example effect"
[19]: https://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Roediger-Karpicke-2006_PPS.pdf?utm_source=chatgpt.com "The Power of Testing Memory"
[20]: https://pmc.ncbi.nlm.nih.gov/articles/PMC8759977/?utm_source=chatgpt.com "Evidence of the Spacing Effect and Influences on Perceptions of ..."
[21]: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html?utm_source=chatgpt.com "Understanding SC 2.5.8: Target Size (Minimum) (Level AA)"
[22]: https://pmc.ncbi.nlm.nih.gov/articles/PMC3983480/?utm_source=chatgpt.com "Retrieval practice enhances new learning: the forward ..."
[23]: https://kenney.nl/assets?utm_source=chatgpt.com "Assets"
[24]: https://fonts.google.com/specimen/Assistant?utm_source=chatgpt.com "Assistant"
[25]: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/dir?utm_source=chatgpt.com "HTML dir global attribute - MDN"
[26]: https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition?utm_source=chatgpt.com "SpeechRecognition - Web APIs - MDN"
[27]: https://headlessui.com/?utm_source=chatgpt.com "Headless UI - Unstyled, fully accessible UI components"
[28]: https://langchain-ai.github.io/langgraph/concepts/why-langgraph/?utm_source=chatgpt.com "Learn LangGraph basics - Overview"
[29]: https://esprima.org/?utm_source=chatgpt.com "Esprima"
[30]: https://matomo.org/free-software/?utm_source=chatgpt.com "Free Open-Source Web Analytics - Matomo"
[31]: https://plausible.io/self-hosted-web-analytics?utm_source=chatgpt.com "Plausible: Self-Hosted Google Analytics alternative"
[32]: https://pyodide.org/?utm_source=chatgpt.com "Pyodide — Version 0.28.2"
[33]: https://brm.io/matter-js/docs/?utm_source=chatgpt.com "Matter.js Physics Engine API Docs - brm·io"
[34]: https://microsoft.github.io/monaco-editor/docs.html?utm_source=chatgpt.com "Monaco Editor API"
[35]: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API?utm_source=chatgpt.com "Web Speech API - MDN - Mozilla"

