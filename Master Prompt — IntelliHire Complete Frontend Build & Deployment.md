# MASTER PROMPT — BUILD INTELLIHIRE FRONTEND

You are a senior frontend architect, product designer, UX engineer, and Next.js developer.

Build a **complete, polished, production-quality frontend for IntelliHire**, an AI-based placement training and recruitment simulation platform.

The uploaded IntelliHire IEEE paper and blueprint/reference images are the authoritative product references for this implementation.

## 1. PRODUCT VISION

IntelliHire is an AI-powered recruitment simulation platform designed to reproduce the major stages of a real hiring process inside one unified candidate experience.

The frontend must communicate this journey clearly:

**Resume Screening → Adaptive Assessment → Technical Interview → HR Interview & Behavioural Analysis → AI Hiring Committee / Candidate Readiness**

The platform should feel like a serious **AI recruitment intelligence product**, not a generic student dashboard.

Core positioning:

> **Train Smart. Perform Better. Get Placed.**

Primary UX goal:

> Give a candidate a realistic, structured, measurable placement-preparation journey and show exactly where they are strong, where they are weak, and what they should practice next.

---

# 2. VERY IMPORTANT SCOPE RULE

## FRONTEND ONLY

Do NOT build a real backend.

Do NOT create:

- FastAPI services
- Node.js backend APIs
- PostgreSQL
- Supabase database
- Firebase
- Azure Cosmos DB
- Judge0 server integration
- Azure OpenAI server integration
- authentication backend
- payment backend
- server-side AI inference
- server-side resume processing
- server-side PDF generation
- production WebSocket server

The IEEE paper describes these backend technologies as part of the proposed complete system, but this task is specifically to build the **frontend first**.

Instead, create a robust **frontend simulation/mock architecture** that makes the application look and behave like the finished product.

Every backend-dependent feature should have a clean frontend service abstraction and realistic mock data.

For example:

```text
src/
  services/
    auth.service.ts
    resume.service.ts
    assessment.service.ts
    technical.service.ts
    hr.service.ts
    behavioral.service.ts
    readiness.service.ts
```

These services should initially return mock/local data.

Design them so real APIs can replace them later without rewriting the UI.

---

# 3. TECHNOLOGY STACK

Use:

- Next.js 14+
- App Router
- TypeScript
- Tailwind CSS
- React
- Recharts
- Lucide React icons
- shadcn/ui where appropriate
- React Hook Form
- Zod
- Zustand for client state where useful
- Monaco Editor for the coding interview UI
- Framer Motion for subtle UI animation
- date-fns where useful

Use modern React patterns.

Prefer reusable components over duplicated page-specific markup.

Use strict TypeScript.

Avoid `any` unless absolutely unavoidable.

---

# 4. VISUAL DESIGN LANGUAGE

Use the uploaded IntelliHire blueprint images as the visual direction.

The design should strongly resemble the supplied blueprint:

### Primary visual identity

- Deep navy / midnight background
- Electric blue accents
- Cyan highlights
- Purple/violet secondary accents
- Green success states
- Orange warning/action states
- White/light cards
- Soft gradients
- Subtle circuit-board / AI-tech motifs
- Glowing borders used sparingly
- Rounded cards
- Strong dashboard hierarchy
- Professional enterprise AI aesthetic

The design should combine:

**AI platform + recruitment analytics + futuristic technical dashboard + premium SaaS**

Do NOT make it look like:

- a gaming website
- a cryptocurrency dashboard
- a generic admin template
- a childish student portal
- an over-animated landing page

---

# 5. RESPONSIVE DESIGN

The application must work properly on:

- desktop
- laptop
- tablet
- mobile

Desktop should be the primary experience because interviews, coding, analytics and dashboards require screen real estate.

However, every page must remain usable on mobile.

Use:

- responsive grids
- collapsible navigation
- mobile drawer/sidebar
- responsive tables
- horizontal scrolling only where genuinely necessary
- stacked cards on small screens
- responsive charts
- mobile-friendly interview controls

---

# 6. GLOBAL APPLICATION STRUCTURE

Create a professional application shell.

## Public area

Routes:

```text
/
 /about
 /how-it-works
 /features
 /pricing
 /contact
 /login
 /signup
```

## Candidate application

```text
/app
/app/dashboard
/app/profile
/app/resume
/app/resume/analyze
/app/assessment
/app/assessment/instructions
/app/assessment/session
/app/assessment/results
/app/technical
/app/technical/instructions
/app/technical/session
/app/technical/results
/app/hr
/app/hr/instructions
/app/hr/session
/app/hr/results
/app/behavior
/app/behavior/session
/app/behavior/results
/app/readiness
/app/reports
/app/progress
/app/settings
```

## Future recruiter/admin placeholders

Create visually complete but clearly marked frontend-only pages:

```text
/admin
/admin/dashboard
/admin/candidates
/admin/jobs
/admin/questions
/admin/reports
/admin/settings
```

These should use mock data only.

---

# 7. LANDING PAGE

Create a premium IntelliHire landing page.

Hero:

**IntelliHire**

**An AI-Based Placement Trainer**

Headline:

> Train Smart. Perform Better. Get Placed.

Supporting copy:

> Simulate the real recruitment journey, practice every stage, understand your weaknesses, and improve your placement readiness with AI-powered feedback.

Hero visual:

Create a polished dashboard/laptop-style product preview inspired by the supplied blueprint.

Show:

- Candidate Readiness Score
- module scores
- performance chart
- hiring probability
- recent interview activity

Primary CTA:

**Start Your Journey**

Secondary CTA:

**Explore How It Works**

---

# 8. LANDING PAGE SECTIONS

Implement:

## What is IntelliHire?

Explain the platform as an AI-powered recruitment simulation environment.

Show the five major capabilities:

- AI Resume Screening / ATS
- Adaptive Online Assessment
- AI Technical Interview
- AI HR Interview
- Behavioural Analysis

## Why IntelliHire?

Use six visual benefit cards:

1. Replicates Real Recruitment
2. AI-Powered Personalization
3. Context-Aware Intelligence
4. Real-Time Behavioural Insights
5. Actionable Feedback
6. Improves Placement Readiness

## Who is it for?

Show:

- Students & Graduates
- Job Seekers
- Internship Aspirants
- Career Switchers
- Training Institutes
- Recruiters & HR Teams

## Benefits

Show:

- understand placement readiness
- personalized feedback
- unlimited practice
- realistic interview simulation
- data-driven preparation
- smarter preparation

## End-to-End Recruitment Lifecycle

Create a visual five-step horizontal journey:

```text
01 Resume Screening
        ↓
02 Adaptive Assessment
        ↓
03 Technical Interview
        ↓
04 HR Interview + Behavioural Analysis
        ↓
05 AI Hiring Committee
```

Use arrows and animated progression.

---

# 9. AUTHENTICATION UI

Since there is no backend, authentication is simulated.

Create:

### Login

Fields:

- email
- password
- remember me

Buttons:

- Sign In
- Continue as Demo Candidate

### Signup

Fields:

- name
- email
- password
- education
- target role
- experience level

On submission, store mock session in localStorage/Zustand and redirect to dashboard.

Include polished validation and error states.

---

# 10. CANDIDATE DASHBOARD

This is the central application screen.

Create a high-quality dashboard.

Header:

- greeting
- profile avatar
- notifications
- current target role
- readiness status

Hero metric:

## Candidate Readiness Index

Example:

**88 / 100**

Label:

**Interview Ready**

Show:

- readiness trend
- hiring probability
- percentile
- improvement since last session

Do not imply this is a real prediction. Clearly label mock/demo data where appropriate.

---

# 11. READINESS BREAKDOWN

Create five major score cards:

### ATS Score

Example:

**82%**

### Aptitude

Example:

**76%**

### Technical

Example:

**91%**

### HR

Example:

**84%**

### Behavioural

Example:

**79%**

Show:

- score
- previous score
- change
- status
- CTA to practice

---

# 12. CRI IMPLEMENTATION

The IEEE paper defines the Candidate Readiness Index as a weighted combination of the five module scores.

Use the reference weights:

```text
ATS          20%
Aptitude     20%
Technical    25%
HR           20%
Behavioural  15%
```

Frontend calculation:

```ts
CRI =
  ATS * 0.20 +
  Aptitude * 0.20 +
  Technical * 0.25 +
  HR * 0.20 +
  Behavioural * 0.15
```

Implement this calculation in a reusable utility.

Example:

```text
src/lib/readiness/calculateCRI.ts
```

The score must update dynamically when mock module scores change.

---

# 13. DASHBOARD CHARTS

Use Recharts.

Implement:

### Readiness radar chart

Dimensions:

- ATS
- Aptitude
- Technical
- HR
- Behavioural

### Progress line chart

Show readiness over:

- Week 1
- Week 2
- Week 3
- Week 4
- Week 5

### Skill-gap bar chart

Show:

- DSA
- Communication
- Aptitude
- Resume
- System Design
- Behavioural

### Interview performance chart

Show:

- technical
- HR
- communication
- confidence
- problem solving

Charts must have:

- tooltips
- legends where useful
- responsive containers
- accessible labels
- empty/loading states

---

# 14. RESUME / ATS MODULE

Create a complete resume-analysis workflow.

## Resume landing page

Show:

- current ATS score
- previous scans
- strongest sections
- missing keywords
- improvement suggestions
- job matching history

## Upload screen

Support UI for:

- PDF
- DOCX

Use drag-and-drop.

Show:

- file name
- file size
- upload progress
- remove
- replace

Because there is no backend, simulate parsing.

Include a **Demo Resume** option.

---

# 15. JOB DESCRIPTION INPUT

Allow the user to:

- paste job description
- select a mock job
- load demo job description

Show:

- target role
- company
- skills
- experience
- responsibilities

---

# 16. ATS RESULTS

Create a visually rich results dashboard.

Show:

## ATS Score

Large circular progress visualization.

Then six scoring dimensions aligned with the IEEE specification:

1. Keyword Alignment
2. Section Completeness
3. Skills Coverage
4. Formatting Compliance
5. ATS Parseability
6. Summary Quality

Use the reference default weights:

```text
Keyword Alignment     35%
Section Completeness  20%
Skills Coverage       20%
Formatting            10%
Parseability          10%
Summary Quality        5%
```

Display each dimension with:

- score
- weight
- explanation
- status

---

# 17. RESUME GAP ANALYSIS

Show:

### Missing Keywords

Example:

- REST APIs
- Docker
- TypeScript
- System Design

### Weak Areas

Example:

- measurable achievements
- professional summary
- technical project descriptions

### Suggestions

Each suggestion should show:

- original text
- recommended improvement
- reason
- apply button

Since there is no AI backend, the suggestions are mock/generated locally.

---

# 18. RESUME ITERATION EXPERIENCE

Allow:

```text
Version 1
Version 2
Version 3
```

Show ATS improvement:

```text
64 → 72 → 82
```

Visualize progress.

Include:

**Compare Versions**

with side-by-side sections.

---

# 19. ADAPTIVE ASSESSMENT MODULE

Create a realistic assessment experience.

Categories:

- Quantitative Aptitude
- Logical Reasoning
- Verbal Ability

Before starting:

- instructions
- number of questions
- estimated time
- difficulty adaptation explanation
- progress

---

# 20. ASSESSMENT SESSION UI

Build a polished test interface.

Layout:

### Left/main

Question.

### Right/sidebar

- question number
- progress
- timer
- answered/unanswered
- mark for review

Controls:

- Previous
- Next
- Mark for Review
- Submit

Question types:

- single choice
- multiple choice
- numeric answer

Use mock question bank.

---

# 21. ADAPTIVE BEHAVIOUR SIMULATION

Do not implement the real backend IRT engine.

Instead create a frontend mock adaptive engine.

Track:

```ts
abilityEstimate
difficulty
questionIndex
correctAnswers
incorrectAnswers
standardError
```

Simulate the 3PL-IRT concept described in the paper.

Display a subtle UI indicator:

> Assessment difficulty is adapting to your performance.

The test should appear to select increasingly appropriate questions.

---

# 22. ASSESSMENT RESULTS

Show:

- overall score
- ability estimate
- accuracy
- estimated percentile
- category breakdown
- strengths
- weaknesses
- recommended practice

Charts:

- performance by topic
- accuracy over questions
- difficulty progression

CTA:

**Practice Weak Areas**

---

# 23. TECHNICAL INTERVIEW MODULE

Create a realistic technical interview simulator.

Domains:

- Data Structures & Algorithms
- Operating Systems
- Databases
- System Design

Structure:

```text
Question & Answer
       ↓
Coding Challenge
       ↓
Solution Explanation
       ↓
Technical Evaluation
```

---

# 24. TECHNICAL INTERVIEW SESSION

Create a professional interview workspace.

Header:

- interviewer status
- interview timer
- question number
- target role

Question panel:

- interviewer question
- difficulty
- topic

Answer panel:

- text response
- voice-response UI

Coding panel:

Use Monaco Editor.

Features:

- language selector
- theme selector
- run
- submit
- reset
- test cases
- output console

Mock languages:

- JavaScript
- TypeScript
- Python
- Java
- C++
- C
- Go

Do not execute arbitrary code on the frontend.

Use simulated execution results.

---

# 25. TECHNICAL EVALUATION

After submission, show four criteria from the IEEE specification:

1. Conceptual Accuracy
2. Complexity Analysis
3. Edge-Case Awareness
4. Communication Clarity

Example result:

```text
Conceptual Accuracy      88%
Complexity Analysis      76%
Edge Cases               81%
Communication             90%
```

Generate mock feedback.

---

# 26. HR INTERVIEW MODULE

Create a realistic AI HR interview interface.

The interviewer should appear professional.

Use:

- interviewer avatar
- question bubble
- candidate response area
- microphone control
- recording status
- transcript
- conversation history

Mock interview questions should be context-aware based on:

- resume
- target role
- experience level

---

# 27. STAR FRAMEWORK

Evaluate responses against:

```text
Situation
Task
Action
Result
```

Show a STAR score from 0–4.

Example:

```text
Situation   ✓
Task        ✓
Action      ✓
Result      ⚠ Missing detail
```

Include feedback:

> Strengthen the Result section by quantifying the impact of your action.

---

# 28. HR ANALYTICS

Show:

- STAR completeness
- sentiment
- relevance
- vocabulary richness
- communication confidence

Use mock VADER-style sentiment values.

Do not claim that actual sentiment analysis is happening.

Use a clear demo/mock architecture until backend services exist.

---

# 29. BEHAVIOURAL ANALYSIS MODULE

Create the frontend interface for browser-native behavioural analysis.

The paper specifies three behavioural streams:

### Eye Contact

Track/display:

- eye-contact percentage
- gaze consistency
- off-screen duration

### Emotion

Display:

- confidence
- neutral
- positive
- nervous

### Posture

Display:

- confident
- neutral
- defensive

The paper describes MediaPipe FaceMesh, DeepFace and YOLOv8 pose processing inside a browser Web Worker.

For this frontend-only build, create the UI and simulation layer only.

---

# 30. CAMERA / MICROPHONE UI

Build a realistic interview camera interface.

Show:

- webcam preview
- microphone state
- camera state
- recording indicator
- permission states
- connection state

If browser permissions are available, you may implement local `getUserMedia()` preview.

IMPORTANT:

Do not upload video/audio anywhere.

Do not transmit biometric data.

Keep all demo processing local.

Clearly communicate:

> Your camera preview remains on this device in demo mode.

---

# 31. BEHAVIOURAL SCORE

Implement the frontend calculation:

```text
BCI =
0.40 × Eye Contact
+
0.30 × Posture
+
0.30 × Emotion
```

Show the result as:

**Behavioural Confidence Index**

Example:

**81 / 100**

Break down the score visually.

---

# 32. AI HIRING COMMITTEE

Create a final simulated hiring committee screen.

Display four fictional panel members:

- Technical Interviewer
- HR Interviewer
- Placement Specialist
- Hiring Manager

Each provides a recommendation based on mock module results.

Possible statuses:

- Strong Hire
- Hire
- Consider
- Needs Improvement

Do not represent this as an actual hiring decision.

Use:

> Simulated recommendation

---

# 33. FINAL READINESS REPORT

Create the strongest page in the application.

Title:

# Your IntelliHire Readiness Report

Show:

### Candidate Readiness Index

Large score.

### Hiring Readiness

Example:

**High Readiness**

### Module Performance

Radar chart.

### Strengths

Examples:

- Strong technical problem solving
- Good communication
- Strong resume structure

### Improvement Areas

Examples:

- Aptitude speed
- STAR Result articulation
- Eye-contact consistency

### Recommended Practice Plan

Create a prioritized list:

```text
1. Practice 10 aptitude questions
2. Complete one technical interview
3. Practice two STAR responses
4. Improve resume keyword alignment
5. Complete one behavioural session
```

---

# 34. REPORT HISTORY

Create:

```text
Report #1
Report #2
Report #3
Current Report
```

Allow the user to compare reports.

Show improvement over time.

---

# 35. PROGRESS TRACKING

Create a dedicated progress page.

Show:

- CRI progression
- ATS progression
- aptitude progression
- technical progression
- HR progression
- behavioural progression

Include milestone cards:

```text
✓ First Resume Analysis
✓ First Assessment
✓ First Technical Interview
✓ First HR Interview
✓ First Behavioural Session
✓ Readiness Report Generated
```

---

# 36. RECOMMENDATION ENGINE — FRONTEND MOCK

Create a deterministic recommendation engine.

Example:

```ts
if (aptitudeScore < 70)
  recommend("Practice Quantitative Aptitude");

if (technicalScore < 75)
  recommend("Complete a Technical Interview");

if (hrScore < 75)
  recommend("Practice STAR Responses");

if (behavioralScore < 75)
  recommend("Practice Behavioural Interview");

if (atsScore < 75)
  recommend("Improve Resume ATS Alignment");
```

Prioritize the lowest-performing module.

Display recommendations across:

- dashboard
- readiness report
- module result pages

---

# 37. COMPONENT ARCHITECTURE

Create a reusable component system.

Suggested structure:

```text
components/
  layout/
    AppShell
    Sidebar
    Header
    MobileNav

  dashboard/
    ReadinessCard
    ModuleScoreCard
    ProgressChart
    RadarChart
    SkillGapChart
    RecommendationCard

  resume/
    ResumeUploader
    JobDescriptionInput
    ATSScore
    ATSBreakdown
    KeywordGapList
    ResumeSuggestion
    ResumeComparison

  assessment/
    QuestionCard
    AssessmentTimer
    QuestionNavigator
    AssessmentProgress
    AssessmentResult

  technical/
    InterviewQuestion
    CodeEditor
    Console
    TestCasePanel
    InterviewTimer
    TechnicalScore

  hr/
    InterviewerPanel
    Conversation
    ResponseRecorder
    STARScore
    HRAnalytics

  behavioral/
    CameraPreview
    BehaviourMetrics
    EyeContactCard
    EmotionCard
    PostureCard
    BCIChart

  readiness/
    CRIOverview
    ModuleRadar
    StrengthsCard
    WeaknessCard
    PracticePlan
    HiringCommittee

  ui/
    Button
    Card
    Modal
    Badge
    Progress
    Tabs
    Tooltip
    EmptyState
    Skeleton
    Alert
```

---

# 38. MOCK DATA ARCHITECTURE

Create centralized mock data.

```text
src/
  mock/
    candidate.ts
    resume.ts
    jobs.ts
    assessments.ts
    technical.ts
    interviews.ts
    behavioral.ts
    readiness.ts
```

Do not scatter fake data throughout JSX.

---

# 39. TYPE SYSTEM

Create proper TypeScript types.

Examples:

```ts
type ModuleScore = {
  score: number;
  previousScore: number;
  trend: number;
};

type CandidateReadiness = {
  ats: number;
  aptitude: number;
  technical: number;
  hr: number;
  behavioral: number;
  cri: number;
};

type ResumeAnalysis = {
  keywordAlignment: number;
  sectionCompleteness: number;
  skillsCoverage: number;
  formatting: number;
  parseability: number;
  summaryQuality: number;
};

type AssessmentResult = {
  score: number;
  abilityEstimate: number;
  standardError: number;
  accuracy: number;
};

type TechnicalEvaluation = {
  conceptualAccuracy: number;
  complexityAnalysis: number;
  edgeCaseAwareness: number;
  communicationClarity: number;
};

type HREvaluation = {
  starCompleteness: number;
  sentiment: number;
  relevance: number;
  vocabularyRichness: number;
};

type BehavioralEvaluation = {
  eyeContact: number;
  posture: number;
  emotion: number;
  bci: number;
};
```

---

# 40. STATE MANAGEMENT

Use Zustand or React Context for application-level state.

Store:

- candidate profile
- current resume
- target job
- module scores
- assessment session
- technical session
- HR session
- behavioural session
- readiness data
- completed modules

Persist demo state in localStorage.

Provide a:

**Reset Demo Data**

button under Settings.

---

# 41. LOADING STATES

Every simulated AI operation must have realistic loading UX.

Examples:

Resume analysis:

```text
Parsing resume...
Extracting skills...
Comparing job requirements...
Calculating ATS score...
Generating recommendations...
```

Interview:

```text
Preparing interviewer...
Analyzing response...
Generating feedback...
```

Assessment:

```text
Selecting next question...
```

Readiness:

```text
Aggregating performance...
Calculating readiness...
Generating recommendations...
```

Use skeletons, progress bars and subtle animations.

---

# 42. ERROR STATES

Build proper error states.

Examples:

- invalid file
- unsupported file
- camera denied
- microphone denied
- session expired
- simulated AI failure
- empty assessment
- no previous reports
- missing resume

Never leave the UI blank.

---

# 43. ACCESSIBILITY

Implement:

- semantic HTML
- keyboard navigation
- visible focus states
- accessible form labels
- ARIA labels
- sufficient contrast
- reduced-motion support
- screen-reader-friendly charts where possible

---

# 44. SECURITY UX

Even though there is no backend, design the UI as if it will become production-ready.

Never expose:

- API keys
- secrets
- private credentials

Never put fake secrets into the repository.

Use environment variable placeholders only when necessary.

---

# 45. DARK MODE

Primary application experience should be dark.

Provide:

- dark mode
- light mode

Persist preference locally.

Use a consistent IntelliHire design system across both modes.

---

# 46. ANIMATIONS

Use animation strategically.

Good uses:

- dashboard number counters
- card entrance
- progress changes
- interview state transitions
- assessment transitions
- radar/chart rendering
- readiness score reveal

Avoid excessive animation.

The interface should feel fast and professional.

---

# 47. ICONOGRAPHY

Use Lucide React icons consistently.

Suggested icon mapping:

- Resume → FileText
- Assessment → ClipboardCheck
- Technical → Code2
- HR → Users
- Behaviour → ScanFace
- Readiness → Gauge
- Reports → FileBarChart
- Settings → Settings
- Security → ShieldCheck
- Progress → TrendingUp

---

# 48. NAVIGATION

Sidebar:

```text
Dashboard

Prepare
  Resume & ATS
  Aptitude Assessment
  Technical Interview
  HR Interview
  Behavioural Practice

Insights
  Readiness
  Progress
  Reports

Account
  Profile
  Settings
```

Use active navigation states.

Show completion indicators beside modules.

Example:

```text
Resume & ATS        ✓
Aptitude            80%
Technical           65%
HR Interview        —
Behavioural         —
```

---

# 49. ONBOARDING

After first login, create a short onboarding flow.

Steps:

1. Profile
2. Target role
3. Experience
4. Resume
5. Preparation goal

Example target roles:

- Software Engineer
- Data Scientist
- ML Engineer
- Data Analyst
- Product Manager
- VLSI Engineer

The IEEE paper identifies future domain-specific tracks such as product management, data science and VLSI, so structure the frontend so additional tracks can be added later.

---

# 50. DEMO MODE

The entire application must work immediately after installation without a backend.

Provide:

## "Explore Demo"

This should populate:

- candidate
- resume
- job
- ATS result
- assessment history
- technical result
- HR result
- behavioural result
- readiness report

The user should be able to navigate through the complete IntelliHire journey without configuring anything.

---

# 51. FRONTEND MOCK SERVICES

Implement services such as:

```ts
mockResumeAnalysis()
mockAssessmentSession()
mockTechnicalEvaluation()
mockHRInterview()
mockBehavioralAnalysis()
mockReadinessReport()
```

Each should simulate network latency using promises.

Example:

```ts
await delay(1200);
return mockResult;
```

This makes the frontend feel like a real production application while keeping the backend out of scope.

---

# 52. API-READY ARCHITECTURE

Even though there is no backend, structure service functions like:

```ts
export async function analyzeResume(input: ResumeInput) {
  if (USE_MOCK_API) {
    return mockResumeAnalysis(input);
  }

  return apiClient.post("/resume/analyze", input);
}
```

Create a single configuration:

```env
NEXT_PUBLIC_USE_MOCK_API=true
```

Do not implement the actual API.

This allows future backend integration with minimal refactoring.

---

# 53. PERFORMANCE

Optimize:

- Next.js route loading
- dynamic imports
- chart components
- Monaco Editor
- camera components
- heavy behavioural components

Lazy-load heavy modules.

Do not load Monaco or camera processing globally.

Use client components only where necessary.

---

# 54. CODE QUALITY

Follow:

- SOLID principles where applicable
- DRY
- separation of concerns
- feature-based organization
- typed service boundaries
- reusable UI primitives

Avoid huge page components.

Avoid deeply nested conditional JSX.

Use clear naming.

---

# 55. TESTING

Add frontend tests for important logic.

Test:

### CRI

```text
CRI calculation
weight validation
score updates
```

### ATS

```text
weighted score calculation
```

### Behaviour

```text
BCI calculation
```

### Assessment

```text
question progression
score calculation
completion state
```

### UI

Test important components with appropriate React testing tools.

---

# 56. SEO / METADATA

Configure proper Next.js metadata.

Title:

**IntelliHire — AI-Based Placement Trainer**

Description:

> Practice the complete recruitment journey with AI-powered resume analysis, adaptive assessments, technical interviews, HR simulations and behavioural insights.

Create appropriate metadata for public pages.

---

# 57. README

Create a comprehensive README containing:

- project overview
- architecture
- technology stack
- setup
- development
- environment variables
- mock mode
- folder structure
- deployment
- future backend integration
- testing

Explicitly explain:

> This repository currently implements the frontend only. Backend services are represented by mock service abstractions.

---

# 58. DEPLOYMENT

Prepare the frontend for deployment to **Vercel**.

Use:

```bash
npm run build
npm run start
```

Make sure:

```bash
npm run build
```

passes successfully.

Fix all:

- TypeScript errors
- ESLint errors
- build errors
- hydration errors
- broken imports
- missing environment variables

Do not deploy any backend.

The deployed result must be a working frontend-only IntelliHire demo.

---

# 59. DEPLOYMENT CONFIGURATION

Create appropriate:

```text
.env.example
```

with only safe public variables, for example:

```env
NEXT_PUBLIC_APP_NAME=IntelliHire
NEXT_PUBLIC_USE_MOCK_API=true
```

Do not include secret keys.

---

# 60. FINAL QUALITY BAR

Before considering the project complete, verify:

### Product

- [ ] Landing page
- [ ] Authentication UI
- [ ] Onboarding
- [ ] Candidate dashboard
- [ ] Resume/ATS module
- [ ] Adaptive assessment
- [ ] Technical interview
- [ ] HR interview
- [ ] Behavioural analysis
- [ ] Hiring committee simulation
- [ ] CRI/readiness report
- [ ] Progress tracking
- [ ] Reports
- [ ] Settings
- [ ] Demo mode

### Engineering

- [ ] TypeScript
- [ ] reusable components
- [ ] centralized mock data
- [ ] service abstraction
- [ ] Zustand/state architecture
- [ ] responsive design
- [ ] accessibility
- [ ] loading states
- [ ] error states
- [ ] empty states
- [ ] tests
- [ ] clean build

### UX

- [ ] consistent navigation
- [ ] polished animations
- [ ] clear hierarchy
- [ ] mobile responsive
- [ ] keyboard accessible
- [ ] intuitive workflows
- [ ] professional AI/recruitment aesthetic

### Deployment

- [ ] production build succeeds
- [ ] no backend dependency
- [ ] no secret keys
- [ ] Vercel-ready
- [ ] README complete
- [ ] `.env.example` included

---

# 61. DO NOT FAKE BACKEND INTEGRATION

Do not write comments claiming that a real AI model, Judge0, Azure OpenAI, Firebase, PostgreSQL, or other service is connected when it is not.

Instead use:

```text
Demo / Mock Analysis
Simulated Interview
Demo Evaluation
Local Preview
```

where appropriate.

The frontend should demonstrate the intended experience without falsely claiming production AI processing.

---

# 62. IMPORTANT PRODUCT TERMINOLOGY

Use the IntelliHire terminology consistently:

- IntelliHire
- AI-Based Placement Trainer
- ATS Resume Screening
- Adaptive Online Assessment
- AI Technical Interview
- AI HR Interview
- Behavioural Analysis
- Candidate Readiness Index
- Behavioural Confidence Index
- AI Hiring Committee
- Placement Readiness
- Skill Gap Analysis
- Personalized Feedback
- Detailed Reports & Roadmaps

Do not randomly rename these features.

---

# 63. VISUAL REFERENCE PRIORITY

Use the supplied blueprint images as the visual north star.

The blueprint presents:

- IntelliHire branding
- dark navy background
- blue/cyan/purple accents
- five recruitment lifecycle stages
- ten production-engineering architecture blocks
- system architecture
- technology stack
- observability/security concepts
- impact metrics
- user testimonials
- final CTA

Reinterpret those visuals into a **real interactive application**, rather than copying the infographic literally.

The actual product should feel like the blueprint has become a working SaaS platform.

---

# 64. SYSTEM ARCHITECTURE REPRESENTATION

The supplied architecture diagram presents the frontend/client layer, API gateway, backend services, data layer, external services and real-time engine. For this task, implement only the frontend/client-facing portions and represent the remaining layers through mock service boundaries.

The frontend should conceptually be:

```text
                 IntelliHire Frontend
                        │
        ┌───────────────┼────────────────┐
        │               │                │
    Candidate       Interview         Analytics
      UI               UI                UI
        │               │                │
        └───────────────┼────────────────┘
                        │
                 Mock Service Layer
                        │
              Local State / Mock Data
```

Future architecture:

```text
Frontend
   ↓
API Gateway
   ↓
Backend Services
   ↓
AI / ML / Database Services
```

Do not implement the latter yet.

---

# 65. IMPORTANT IMPLEMENTATION ORDER

Build in this sequence:

## Phase 1 — Foundation

- Next.js
- TypeScript
- Tailwind
- theme
- fonts
- global CSS
- component primitives
- application shell
- navigation

## Phase 2 — Marketing

- landing page
- about
- features
- how it works
- login/signup

## Phase 3 — Candidate Platform

- onboarding
- dashboard
- profile
- settings

## Phase 4 — Core Modules

- ATS
- assessment
- technical interview
- HR interview
- behavioural analysis

## Phase 5 — Intelligence Layer

- CRI
- BCI
- recommendations
- progress
- reports
- hiring committee

## Phase 6 — Polish

- loading states
- animations
- accessibility
- responsive design
- error handling
- empty states
- demo mode

## Phase 7 — Quality

- tests
- lint
- TypeScript
- build
- performance review

## Phase 8 — Deployment

- Vercel configuration
- environment configuration
- production build
- deployment

---

# 66. FINAL INSTRUCTION

Do not stop after creating a landing page.

Build the **complete navigable frontend product**.

Every major navigation item must lead to a functional page.

Every major workflow must be clickable.

Every module must have:

```text
Landing/Instructions
       ↓
Active Session
       ↓
Processing/Analysis
       ↓
Results
       ↓
Recommendations
```

The application should feel like a real product even though all backend functionality is mocked.

The user should be able to start from the IntelliHire homepage and experience the entire simulated recruitment journey through to the final Candidate Readiness Index.

Prioritize:

**Product completeness > visual polish > architecture quality > animation complexity.**

The finished result should look like a credible production SaaS product suitable for:

- student demonstrations
- IEEE project demonstrations
- placement-cell presentations
- portfolio showcases
- investor/product demos
- future backend integration

Build it as a **frontend-first production-quality foundation**, not as a static prototype.
