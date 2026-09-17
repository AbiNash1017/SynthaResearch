# Synthetic User Research Platform: Predefined Prompts, User Inputs & Response Catalogue

This document catalogs all predefined user prompts, sample user questions, and deterministic persona response templates across all **5 CLI menu options** and all **5 synthetic learner archetypes** (modeled after real **Udemy** and **Duolingo** behavior patterns).

For each menu option, a dedicated **Terminal Prompt / What You Should Input / What It Does** table is provided.

---

## 1. Menu Option 1: Setup Experiment Workspace

### Terminal Interaction Table

| Terminal Prompt | What You Should Input / Press | What It Does |
| :--- | :--- | :--- |
| `Select an action [1/2/3/4/5/6] (1):` | Type `1` and press `Enter` | Opens the interactive workspace setup wizard. |
| `Product Name (LearnFlow):` | Press `Enter` (or type custom name) | Sets product identifier to `LearnFlow`. |
| `Product Description (...):` | Press `Enter` (or type custom description) | Configures the Udemy + Duolingo hybrid product description. |
| `Target Audience (...):` | Press `Enter` (or type custom audience) | Calibrates target learner demographics (students & professionals aged 20–35). |
| `Objective 1 (...):` | Press `Enter` | Sets: *Discover why learners drop out of courses after the first week*. |
| `Objective 2 (...):` | Press `Enter` | Sets: *Test reaction to bite-sized 5-minute daily lessons vs 45-minute lectures*. |
| `Objective 3 (...):` | Press `Enter` | Sets: *Evaluate willingness to pay for subscriptions vs one-time course fees*. |
| `Objective 4 (...):` | Press `Enter` | Sets: *Identify if streaks and XP leaderboards create genuine motivation*. |

**Output After Completion:**
```text
✔ Experiment configured and saved to data/experiment.json!
```
The main menu refreshes showing: `Active Experiment: LearnFlow`.

---

## 2. Menu Option 2: Generate Diverse Synthetic Personas

### Terminal Interaction Table

| Terminal Prompt | What You Should Input / Press | What It Does |
| :--- | :--- | :--- |
| `Select an action [1/2/3/4/5/6] (1):` | Type `2` and press `Enter` | Triggers `PersonaGenerationAgent` to synthesize 5 diverse learner personas. |

### Generated Personas Output Details

When selected, 5 visual persona cards are rendered in the terminal:

1. **Persona 1: Rohan Mehta**
   - **Archetype**: `Impulse Buyer` (Udemy flash sale hoarder)
   - **Age / Gender / Location**: 26, Male, Bengaluru, India
   - **Occupation / Income**: Junior Software Engineer | lower-middle
   - **Traits**: `ambitious`, `easily distracted`, `deal-seeking`
   - **Behavior Pattern**: High purchase frequency on sales (₹499/course), low completion rate (<10%), drops out when lectures get theoretical, responds strongly to quick streak wins.

2. **Persona 2: Chloe Martin**
   - **Archetype**: `Streak Chaser` (Duolingo daily streak addict)
   - **Age / Gender / Location**: 22, Female, Paris, France
   - **Occupation / Income**: Graphic Design Intern | entry-level
   - **Traits**: `disciplined`, `competitive`, `habit-driven`
   - **Behavior Pattern**: Maintains 400+ day streak, checks leaderboards daily, studies 3–7 minutes on morning commute, willing to pay for streak freezes.

3. **Persona 3: Aarav Deshmukh**
   - **Archetype**: `Deep Learner` (Rigorous self-studier)
   - **Age / Gender / Location**: 31, Male, Bengaluru, India
   - **Occupation / Income**: Staff Backend Engineer | upper-middle
   - **Traits**: `analytical`, `methodical`, `focused`
   - **Behavior Pattern**: Completes 80%+ of courses, studies 30–45 minute blocks on weekends, dislikes cartoon badges and XP, willing to pay high prices for masterclasses with production-grade depth.

4. **Persona 4: David Kim**
   - **Archetype**: `Career Switcher` (Job-transition focused)
   - **Age / Gender / Location**: 33, Male, Toronto, Canada
   - **Occupation / Income**: Bank Branch Officer -> Aspiring Cloud Engineer | middle
   - **Traits**: `goal-oriented`, `pragmatic`, `time-pressured`
   - **Behavior Pattern**: Studies 2 hours every evening, motivated by resume items, portfolio projects, and hiring outcomes, prefers modular lessons tied to career benchmarks.

5. **Persona 5: Mateo Rossi**
   - **Archetype**: `Casual Browser` (Recreational learner)
   - **Age / Gender / Location**: 22, Male, Rome, Italy
   - **Occupation / Income**: Retail Associate | lower-middle
   - **Traits**: `curious`, `low-commitment`, `recreational`
   - **Behavior Pattern**: Browses apps during idle time, prefers free ad-supported apps, uninstalls if lessons take >5 minutes or guilt-trip notifications are sent.

---

## 3. Menu Option 3: Multi-Persona Survey Mode

### Terminal Interaction Table

| Terminal Prompt | What You Should Input / Press | What It Does |
| :--- | :--- | :--- |
| `Select an action [1/2/3/4/5/6] (1):` | Type `3` and press `Enter` | Opens the Multi-Persona Survey orchestration engine. |
| `Use these questions? [y/n] (y):` | Press `Enter` (or type `y`) | Uses the 3 curated benchmark questions (or type `n` to enter custom questions). |

### Output: Cross-Persona Side-by-Side Survey Results

The terminal renders a cross-comparison matrix displaying each persona's answer alongside their sentiment tag (`[POSITIVE]`, `[NEUTRAL]`, `[NEGATIVE]`):

#### Survey Question 1: *"Why did you abandon or stop using your previous online course or study app?"*

| Persona | Archetype | Response | Sentiment |
| :--- | :--- | :--- | :--- |
| **Rohan Mehta** | Impulse Buyer | *"Honestly, it starts with huge excitement on day 1. But by day 3, the instructor dives into 45-minute abstract slides with no code demo, and I completely lose steam."* | `NEGATIVE` |
| **Chloe Martin** | Streak Chaser | *"My dropouts only happen if an app breaks my habit chain—like an unexpected server downtime or overly long weekend assignments that I can't fit into my schedule."* | `NEGATIVE` |
| **Aarav Deshmukh** | Deep Learner | *"My primary reason for abandoning a course is discovering that it's just a surface-level overview masquerading as an advanced tutorial. If there are no challenging architectural problems, I leave."* | `NEGATIVE` |
| **David Kim** | Career Switcher | *"I drop out when a course turns out to be purely academic without explaining how things are actually done on a real company team. Time is too valuable."* | `NEGATIVE` |
| **Mateo Rossi** | Casual Browser | *"If a course requires 30 hours of commitment, I won't even start. The moment it feels tedious, heavy, or demands strict homework, I uninstall."* | `NEGATIVE` |

#### Survey Question 2: *"Would a 5-minute daily micro-lesson format keep you consistent compared to long video lectures?"*

| Persona | Archetype | Response | Sentiment |
| :--- | :--- | :--- | :--- |
| **Rohan Mehta** | Impulse Buyer | *"5 to 7 minutes is my golden window. Give me one clear concept, an interactive test question right away, and wrap it up. That builds momentum instead of burnout."* | `POSITIVE` |
| **Chloe Martin** | Streak Chaser | *"3 to 7 minutes is the absolute sweet spot. That fits perfectly into my morning metro commute or right before sleeping. It keeps my daily streak alive effortlessly."* | `POSITIVE` |
| **Aarav Deshmukh** | Deep Learner | *"Short snippets often fragment knowledge. You simply cannot explore distributed systems or nuanced architecture in a 3-minute video. I prefer 30-minute deep dives."* | `NEGATIVE` |
| **David Kim** | Career Switcher | *"Bite-sized modules of 12 to 15 minutes that chain together into a weekly mini-project work best for my busy schedule after work."* | `POSITIVE` |
| **Mateo Rossi** | Casual Browser | *"Under 5 minutes for sure! Quick interactive questions with instant feedback while waiting for a friend at a cafe is the only way I'll stick around."* | `POSITIVE` |

#### Survey Question 3: *"How much would you be willing to pay monthly for this learning platform?"*

| Persona | Archetype | Response | Sentiment |
| :--- | :--- | :--- | :--- |
| **Rohan Mehta** | Impulse Buyer | *"I strongly prefer one-time sales of 499 to 799 rupees on Udemy. Monthly subscriptions scare me because paying every month while inactive makes me feel guilty."* | `NEGATIVE` |
| **Chloe Martin** | Streak Chaser | *"I am happy to pay 399 to 599 rupees per month for a premium tier like Duolingo Super, mainly to remove disruptive ads and get unlimited streak freezes."* | `POSITIVE` |
| **Aarav Deshmukh** | Deep Learner | *"I am completely willing to pay premium prices—2,000 to 5,000 rupees monthly or 25,000 annually—if the instructors are distinguished researchers and curriculum is rigorous."* | `POSITIVE` |
| **David Kim** | Career Switcher | *"I am ready to invest 1,500 to 3,000 rupees a month. I view this as an investment in my next salary bracket, provided there is portfolio mentoring."* | `POSITIVE` |
| **Mateo Rossi** | Casual Browser | *"I prefer 100% free apps supported by non-intrusive ads. If an app blocks basic lessons behind a paywall, I will immediately delete it."* | `NEGATIVE` |

---

## 4. Menu Option 4: Interactive Persona Interview Mode

### Terminal Interaction Table

| Terminal Prompt | What You Should Input / Press | What It Does |
| :--- | :--- | :--- |
| `Select an action [1/2/3/4/5/6] (1):` | Type `4` and press `Enter` | Opens live persona selector. |
| `Enter Persona ID (persona_001):` | Type `persona_001` (or press `Enter` for default) | Initiates multi-turn chat session with Rohan Mehta (`Impulse Buyer`). |
| `You:` | Type `Why are you not able to complete courses?` | Queries completion dropouts; receives in-character explanation. |
| `You:` | Type `Does gamification help?` | Queries streak & badge motivation; persona explains streak psychology. |
| `You:` | Type `okay` | Sends conversational acknowledgement; persona follows up naturally. |
| `You:` | Type `What about pricing?` | Queries pricing model; persona responds with sales vs subscription preferences. |
| `You:` | Type `How long should video lectures be?` | Queries attention span limits; persona provides ideal lesson length. |
| `You:` | Type `exit` and press `Enter` | Ends conversation and writes turns to `data/interview_logs.json`. |

### Interview Response Catalogue (Per Persona)

#### 4.1 Rohan Mehta (`Impulse Buyer`)

| Topic / User Input | Sample User Question | Rohan's Response |
| :--- | :--- | :--- |
| **Course Completion** | `"Why are you not able to complete courses?"` | *"Honestly, it starts with huge excitement on day 1. But by day 3, the instructor dives into 45-minute abstract slides with no code demo, and I completely lose steam."* |
| **Gamification** | `"Does gamification help?"` | *"Yes! Gamification definitely works on me. If I get an XP bonus or a streak alert at 9 PM saying 'Keep your 5-day streak alive!', I will open the app and do a 5-minute quiz just to keep the streak."* |
| **Acknowledgement** | `"Okay"` / `"Got it"` | *"Yeah, exactly. That's why traditional 40-hour lecture dumps never work for someone like me."* |
| **Pricing** | `"What about pricing?"` | *"I strongly prefer one-time sales. When Udemy drops a course from 3,499 down to 499 rupees, my brain screams 'deal!' and I swipe my card immediately."* |
| **Lesson Duration** | `"How long should video lectures be?"` | *"Lessons have to be under 8 to 10 minutes max. If I see a 50-minute video lecture, I immediately put it off for the weekend, and that weekend never arrives."* |
| **Frustrations** | `"What frustrates you most?"` | *"My number one frustration is 20-minute theoretical monologues before showing any real-world screen or project. I need hands-on action within the first 60 seconds."* |

#### 4.2 Chloe Martin (`Streak Chaser`)

| Topic / User Input | Sample User Question | Chloe's Response |
| :--- | :--- | :--- |
| **Course Completion** | `"How is your course completion?"` | *"I actually have a great completion record, but only if the app maintains daily continuity. If an app gives me a streak counter, I will show up 365 days in a row."* |
| **Gamification** | `"Do streaks and leaderboards really motivate you?"` | *"Streaks, XP, and weekly leagues are what keep me alive! The psychological urge to protect my streak counter is way stronger than my desire to read a textbook."* |
| **Acknowledgement** | `"Understood"` / `"Makes sense"` | *"Totally agree! Daily habits are the only way skills actually stick over time."* |
| **Pricing** | `"Would you pay for a subscription?"` | *"I am happy to pay 399 to 599 rupees per month for a premium tier like Duolingo Super, mainly to remove disruptive ads and get unlimited streak freezes."* |
| **Lesson Duration** | `"What is your ideal lesson length?"` | *"3 to 7 minutes is the absolute sweet spot. That fits perfectly into my morning metro commute or right before sleeping."* |
| **Frustrations** | `"What makes you hate an app?"` | *"Losing a 200-day streak due to a technical bug or confusing timezone logic is the most heartbreaking thing ever. It makes me want to delete the app."* |

#### 4.3 Aarav Deshmukh (`Deep Learner`)

| Topic / User Input | Sample User Question | Aarav's Response |
| :--- | :--- | :--- |
| **Course Completion** | `"Why do you finish courses while others drop out?"` | *"I measure completion by mastery, not badge counts. I will re-watch a 45-minute lecture 3 times until my local implementation matches production specifications."* |
| **Gamification** | `"Do you enjoy streaks, badges and XP?"` | *"To be blunt, I find cartoon badges, confetti animations, and sound effects juvenile and distracting. I am not playing Candy Crush; I am investing in professional expertise."* |
| **Acknowledgement** | `"I see"` / `"Makes sense"` | *"Indeed. Pedagogical integrity should always take precedence over superficial retention hacks."* |
| **Pricing** | `"How much would you pay?"` | *"Price is secondary to signal-to-noise ratio. A 499 rupee course that wastes 10 hours of my time is vastly more expensive than a 10,000 rupee masterclass that delivers real expertise."* |
| **Lesson Duration** | `"Are 5-minute micro lessons good?"` | *"25 to 45 minutes is appropriate. You simply cannot explore distributed systems, statistical modeling, or nuanced architecture in a 3-minute video."* |
| **Frustrations** | `"What is your biggest pain point?"` | *"Trivial examples. Instructors who demonstrate 'Hello World' and then leave production-level error handling as 'an exercise for the reader.'"* |

#### 4.4 David Kim (`Career Switcher`)

| Topic / User Input | Sample User Question | David's Response |
| :--- | :--- | :--- |
| **Course Completion** | `"What keeps you motivated to complete courses?"` | *"I finish courses when I can clearly trace every module to a bullet point on a job description. If a course promises a portfolio project that impresses recruiters, I stick with it to the end."* |
| **Gamification** | `"Does gamification help you transition careers?"` | *"Streaks are helpful for accountability when I feel exhausted on a Wednesday night. But badges alone won't get me hired—recruiters want live deployed apps."* |
| **Acknowledgement** | `"Got it"` / `"Cool"` | *"That makes complete sense. When you have bills to pay and a career to pivot, efficiency is everything."* |
| **Pricing** | `"Would you pay for career coaching features?"` | *"I am ready to invest 1,500 to 3,000 rupees a month. I view this as an investment in my next salary bracket, provided there are portfolio reviews."* |
| **Lesson Duration** | `"What lesson pace fits your evening schedule?"` | *"12 to 18 minutes is optimal. Long enough to build a real component, but short enough that I can finish one or two modules before dinner."* |
| **Certificates** | `"Are certificates important to you?"` | *"Certificates that carry industry weight plus a verified capstone project give me credibility when competing against candidates with CS degrees."* |

#### 4.5 Mateo Rossi (`Casual Browser`)

| Topic / User Input | Sample User Question | Mateo's Response |
| :--- | :--- | :--- |
| **Course Completion** | `"Do you finish courses?"` | *"I rarely finish long courses. I'll open an app when I'm curious about digital illustration, browse for 3 days, and move on. Keep it low-stress."* |
| **Gamification** | `"Do you like gamified features?"` | *"I love fun animations, quirky character mascots, and colorful celebrations when I get an answer right. It makes my day a little brighter!"* |
| **Acknowledgement** | `"Alright"` / `"Okay"` | *"Yeah, totally! If it feels like school or work, I'm just going to close the app."* |
| **Pricing** | `"Would you pay for lessons?"` | *"I prefer 100% free apps supported by non-intrusive ads. If an app blocks basic lessons behind a 1,000 rupee paywall, I will immediately delete it."* |
| **Lesson Duration** | `"What is your attention limit?"` | *"Under 5 minutes for sure! I usually use learning apps while waiting for a friend at a cafe or on the metro. Anything longer doesn't fit my lifestyle."* |
| **Frustrations** | `"What annoys you most?"` | *"Strict penalties! Apps that lock you out for 5 hours when you make 3 mistakes, or guilt-tripping push notifications when you miss a day."* |

---

## 5. Menu Option 5: Research & Insight Report Output

### Terminal Interaction Table

| Terminal Prompt | What You Should Input / Press | What It Does |
| :--- | :--- | :--- |
| `Select an action [1/2/3/4/5/6] (1):` | Type `5` and press `Enter` | Triggers `InsightExtractionAgent` to aggregate all surveys and interviews. |

### Generated Output Details

1. **Terminal Display**:
   - **Report Summary Panel**: Shows Product Name, Sample Size, Survey Question count, Interview session count.
   - **Sentiment Distribution Table**: Breakdown of positive, neutral, and critical sentiments.
   - **Top Emergent Themes**: Identifies high-frequency bigram clusters (e.g. *micro lessons*, *streak accountability*, *price barriers*).
   - **Key Actionable Insights**: Bulleted strategic product recommendations.

2. **Files Saved to Disk**:
   - `reports/report_<date>.json`: Complete machine-readable insight report.
   - `reports/report_<date>.pdf`: Formatted multi-page PDF document generated via ReportLab.

### Actionable Product Insights Generated:
1. **Critical Dropout Factor**: 4 out of 5 personas report lesson duration exceeding 15 minutes as the #1 reason for quitting a course.
2. **Polarizing Feature**: Leaderboards and competitive XP leagues boost daily engagement for competitive and impulse learners, but actively alienate deep analytical learners.
3. **Pricing Model Dichotomy**: Impulse buyers strongly prefer low-friction one-time course sales (Udemy style), whereas career switchers and deep learners prefer outcome-based subscription tiers.
4. **Retention Formula**: Combining Duolingo-style 5-minute daily micro-habits with structured Udemy-style skill progression maximizes overall platform retention.

---

## 6. Menu Option 6: Exit

### Terminal Interaction Table

| Terminal Prompt | What You Should Input / Press | What It Does |
| :--- | :--- | :--- |
| `Select an action [1/2/3/4/5/6] (1):` | Type `6` and press `Enter` | Prints `Goodbye!` and terminates the application cleanly. |
