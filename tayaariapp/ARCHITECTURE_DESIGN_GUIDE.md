# Tayaari Pakki — Complete Architecture & Design Guide
## Geography-First Study App for UPSC/SSC/Railway Exams

---

## 1. SYSTEM OVERVIEW

### 1.1 Core Philosophy
**"Geography is spatial, temporal, and visual"** — The app must make students *see* geography, not just memorize facts.

### 1.2 Target Exams & Weightage
| Exam | Geography Weight | Question Style | Penalty |
|------|------------------|----------------|---------|
| UPSC CSE Prelims | ~15-20 Qs | Conceptual, Map-based, CA integration | -0.66 |
| BPSC | ~25-30 Qs | Bihar-specific + Direct fact + A-R | -0.33 |
| SSC CGL/CHSL | ~5-8 Qs | Speed + Accuracy, Basic facts | -0.50 |
| RRB NTPC/Group D | ~10-15 Qs | Foundation + Applied | -0.33 |

### 1.3 Three-Layer Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER (Compose)             │
│  TopicSelectionScreen → PracticeScreen → ResultsScreen     │
│  MistakeReplayScreen → InsightsDashboardScreen             │
│  PaperTwinScreen → OnboardingScreen                        │
├─────────────────────────────────────────────────────────────┤
│                    DOMAIN LAYER (Engines)                   │
│  QuestionSelectionEngine | LearnerModelEngine              │
│  PatternShockEngine | MistakeReplayEngine                  │
│  PaperTwinEngine | StopDoingEngine                         │
│  ConfusionNetwork | NextBestActionEngine                   │
├─────────────────────────────────────────────────────────────┤
│                    DATA LAYER (Room + Provenance)           │
│  Entities: Question, Topic, TestSession, RevisionItem      │
│  Provenance: SHA-256 Merklized chains, 100% audit          │
│  Source: NCERT VI-XII + SSC/UPSC PYQ + Oxford Atlas        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. CONTENT PIPELINE (v13_discovery)

### 2.1 Source Corpus (8 Files, ~2MB, 5,532 Knowledge Nodes)
```
source-material/
├── geography_extracted.txt          # Class VI Geography (582 nodes)
├── geography_extracted_2.txt        # SSC/UPSC PYQ derived (393 nodes)
├── ncert_xi_physical_geo.txt        # Class XI Physical (1,624 nodes)
├── ncert_xi_india_env.txt           # Class XI India Env (707 nodes)
├── ncert_xii_human_geo.txt          # Class XII Human (912 nodes)
├── ncert_xii_india_economy.txt      # Class XII India Eco (1,107 nodes)
├── ncert_x_geo.txt                  # Class X Geo (207 nodes)
└── ncert_ix_geo.txt                 # Class IX Geo (0 nodes - needs OCR)
```

### 2.2 Generation Pipeline (Zero-Error, 1200 Questions)
```
Raw Corpus → DocumentNormalizer → SemanticExtractor → KnowledgeNode (5,532)
    ↓
Filter: primary_entity ≥3 chars, raw_evidence ≥25 chars, no boilerplate
    ↓
QuestionSynthesizer (14 intents) → CandidateQuestion + Provenance
    ↓
Multi-Agent Auditing Gate (4 vetoes: Cognitive, Adversarial, Semantic, Length)
    ↓
Audit: 1200/1200 PASS (100% provenance integrity)
```

### 2.3 Intent Distribution (UPSC-Aligned)
| Intent | Count | Description |
|--------|-------|-------------|
| definition | 822 | "What is X?" |
| attribute | 259 | "Which has property Y?" |
| cause/effect | 35 | "Why does X happen?" |
| spatial | 11 | "Where is X located?" |
| comparison | 13 | "How does X differ from Y?" |
| classification | 9 | "Which category?" |
| part-of | 26 | "X is part of which system?" |
| process | 8 | "Sequence of formation?" |
| quantity | 8 | "How much/many?" |
| sequence | 4 | "Order of events?" |
| distribution | 1 | "Where is it found?" |
| condition | 1 | "Under what conditions?" |
| exception | 2 | "Which does NOT belong?" |
| member-of | 1 | "Which is a member?" |

### 2.4 Provenance Integrity (6-Link Merkle Chain)
```
QuestionID → IntentType → KnowledgeNodeID → EvidenceText → SourceFile → SourceLocation → SHA-256 Root
```
- **Verification**: `audit_provenance_integrity(batch_records, corpus_dict)` → 100% PASS
- **Tamper Detection**: Any mutation invalidates root hash
- **Grounding**: Evidence text must exist verbatim in source corpus (NFKC normalized, fuzzy match fallback)

---

## 3. ANDROID APP ARCHITECTURE (Kotlin + Compose + Room)

### 3.1 Module Structure
```
app/
├── src/main/java/com/example/
│   ├── database/          # Room entities, DAOs, migrations
│   ├── model/             # Domain models (ExamBlueprint, MCQQuestion, etc.)
│   ├── repository/        # Engines (single-responsibility)
│   ├── viewmodel/         # State holders (AAC ViewModels)
│   ├── ui/
│   │   ├── theme/         # Color.kt, Type.kt, Theme.kt, Shape.kt
│   │   ├── screens/       # Compose screens
│   │   └── components/    # Reusable UI (PremiumQuestionCard, etc.)
│   └── MainActivity.kt
└── src/test/              # 80+ unit/integration tests
```

### 3.2 Key Engines (Domain Logic)
| Engine | Responsibility | Key Input → Output |
|--------|----------------|-------------------|
| **QuestionSelectionEngine** | Adaptive question picking by tier/topic/weakness | `Topic + Tier + LearnerState` → `ExamQuestion` |
| **LearnerModelEngine** | Spaced repetition (SM-2 variant) + mastery states | `AttemptHistory` → `RevisionItem (priority, nextDate)` |
| **PatternShockEngine** | Detects "illusion of competence" via confidence calibration | `Confidence vs Accuracy` → `ShockQuestion` |
| **MistakeReplayEngine** | Generates transfer questions for failed concepts | `FailedQuestion + TrapType` → `ReplayQuestion` |
| **PaperTwinEngine** | Mock test mirroring exam DNA (weightage, penalty, format) | `ExamBlueprint` → `FullMockTest` |
| **ConfusionNetwork** | Detects concept confusion pairs (e.g., Westerlies vs Trade Winds) | `ErrorPatterns` → `DisambiguationCard` |
| **NextBestActionEngine** | Recommends single best study action | `LearnerState + ExamDate` → `RecommendedAction` |

### 3.3 Data Flow (Unidirectional)
```
User Action → ViewModel → Repository/Engine → Room DAO → Flow<State> → ViewModel → Compose UI
                    ↑
            ProvenanceTracker.bind() (every question)
```

---

## 4. GEOGRAPHY-THEMED DESIGN SYSTEM

### 4.1 Color Palette (Semantic Geography Colors)
```kotlin
// Color.kt — Each color maps to a geography domain
val DeepOceanBlue       = Color(0xFF004B72)  // Primary — Oceans, Atmosphere
val DeepOceanBlueDark   = Color(0xFF4C99D3)  // Primary dark
val ForestGreen         = Color(0xFF2E7D32)  // Secondary — Vegetation, Biosphere
val ForestGreenLight    = Color(0xFF81C784)
val Terracotta          = Color(0xFFE07A5F)  // Tertiary — Landforms, Soil
val SandGold            = Color(0xFFF4A261)  // Accent — Deserts, Arid zones
val Parchment           = Color(0xFFF4F1EA)  // Background — Maps, Paper texture
val Charcoal            = Color(0xFF1A1D20)  // Dark background — Night sky
val SurfaceLight        = Color(0xFFFFFFFF)
val SurfaceDark         = Color(0xFF2A2D30)
val TextPrimaryLight    = Color(0xFF1C1B1F)
val TextPrimaryDark     = Color(0xFFE6E1E5)
```

### 4.2 Light/Dark Color Schemes
```kotlin
// Theme.kt — Material3 ColorScheme mapping
LightColorScheme(
    primary = DeepOceanBlue,      // Oceanic primary actions
    secondary = ForestGreen,      // Vegetation/positive feedback
    tertiary = Terracotta,        // Landforms/warnings
    background = Parchment,       // Map paper texture
    surface = SurfaceLight,
    onPrimary = White,
    onSecondary = White,
    onTertiary = White,
    onBackground = TextPrimaryLight,
    onSurface = TextPrimaryLight,
)

DarkColorScheme(
    primary = DeepOceanBlueDark,   // Deep ocean at night
    secondary = ForestGreenLight,  // Moonlit forest
    tertiary = SandGold,           // Desert stars
    background = Charcoal,         // Night sky
    surface = SurfaceDark,
    // ... onColors adapted for dark
)
```

### 4.3 Typography (Map-Legible, Readable)
```kotlin
// Type.kt — Optimized for geographic names, diacritics, numbers
val Typography = Typography(
    displayLarge = TextStyle(
        fontFamily = FontFamily.Default,  // Use system font with good Unicode support
        fontWeight = FontWeight.ExtraBold,
        fontSize = 32.sp,
        lineHeight = 40.sp,
        letterSpacing = -0.5.sp,
    ),
    headlineLarge = TextStyle(        // Topic titles
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 22.sp,
        lineHeight = 28.sp,
    ),
    titleLarge = TextStyle(           // Question stems
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.SemiBold,
        fontSize = 18.sp,
        lineHeight = 26.sp,
    ),
    bodyLarge = TextStyle(            // Explanations, options
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp,
    ),
    labelLarge = TextStyle(           // Badge chips (tier, format)
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 1.sp,
    ),
)
```

### 4.4 Shape System (Organic, Map-Inspired)
```kotlin
// Shape.kt
val MapCorner = RoundedCornerShape(16.dp)      // Card corners like map sheets
val ChipCorner = RoundedCornerShape(8.dp)      // Badge chips
val ButtonCorner = RoundedCornerShape(12.dp)   // Action buttons
val AvatarCorner = CircleShape                 // Profile, icons
val ImageCorner = RoundedCornerShape(8.dp)     // Map images, diagrams
val ProgressCorner = RoundedCornerShape(4.dp)  // Thin progress bars
```

### 4.5 Elevation & Shadows (Layered like Topographic Maps)
```kotlin
// Elevation.kt
val ElevationLevel0 = 0.dp      // Background (sea level)
val ElevationLevel1 = 2.dp      // Cards (foothills)
val ElevationLevel2 = 4.dp      // Raised surfaces (plateaus)
val ElevationLevel3 = 8.dp      // Bottom sheets, dialogs (mountains)
val ElevationLevel4 = 16.dp     // Modals, FABs (peaks)
```

---

## 5. SCREEN-BY-SCREEN DESIGN SPECIFICATIONS

### 5.1 OnboardingScreen — "Your Expedition Begins"
```
┌─────────────────────────────────────────┐
│  [Logo]  Tayaari Pakki                  │
│                                         │
│  "Master the Map, Crack the Exam"       │
│                                         │
│  [Illustration: Globe with exam icons]  │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  SELECT YOUR TARGET EXAM        │    │
│  │  ○ UPSC CSE 2026                │    │
│  │  ○ BPSC 72nd                    │    │
│  │  ○ SSC CGL 2025                 │    │
│  │  ○ RRB NTPC 2024                │    │
│  └─────────────────────────────────┘    │
│                                         │
│  [Continue →]                           │
└─────────────────────────────────────────┘
```
- **Animation**: Globe rotates on load (3s loop)
- **Color**: DeepOceanBlue primary, Parchment background
- **Micro-interaction**: Exam cards lift on press (elevation 2→8dp)

### 5.2 TopicSelectionScreen — "The Atlas"
```
┌─────────────────────────────────────────┐
│  Tayaari Pakki        [🔍][📊][⏰][🔖][⚡][✓]│
├─────────────────────────────────────────┤
│  Target Goal: UPSC CSE 2026    [⚡ Hardcore]│
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │  ⚡ Paper Twin — Mirror Exam DNA   │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  ▼ PHYSICAL GEOGRAPHY          [12/45]   │
│     ┌─────────────────────────────────┐  │
│     │ 🌍  The Earth in Solar System   │  │
│     │    23 Questions  ▸ MEDIUM        │  │
│     └─────────────────────────────────┘  │
│     ┌─────────────────────────────────┐  │
│     │ 🌊  Oceanography                │  │
│     │    0 Questions  ⚠ ADVANCED       │  │
│     └─────────────────────────────────┘  │
│  ▶ INDIAN GEOGRAPHY                      │
│  ▶ WORLD GEOGRAPHY                       │
└─────────────────────────────────────────┘
```
- **Module Headers**: DeepOceanBlue background, white text, expand/collapse
- **Topic Cards**: Elevation 2dp, rounded 16dp, icon circle (50dp)
- **Hardcore Mode**: Terracotta accent, shows "Advanced" tier by default
- **Zero-state**: WarningAmber icon, "0 Questions" in Terracotta

### 5.3 PracticeScreen — "The Trail"
```
┌─────────────────────────────────────────┐
│  ←  The Earth in Solar System  [23 Qs]  │
│  [MEDIUM] [Direct Fact]    05:42  [📊]   │
│  ████████████░░░░░░░░░░░░░░░░  3/23     │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ QUESTION                        │   │
│  │                                 │   │
│  │ What is the stream of charged   │   │
│  │ particles ejected by the Sun?   │   │
│  │                                 │   │
│  │ [Image: Solar corona diagram]   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌A┐ ◯ Solar wind          (selected)  │
│  ┌B┐ ◯ Sunspots                        │
│  ┌C┐ ◯ Solar flares                    │
│  ┌D┐ ◯ Coronal loops                   │
│                                         │
│  [Cross-out ✕] on long-press each     │
│                                         │
│  [CORRECT ANSWER]  ✓ Solar wind       │
│  Solar wind is a constant stream...   │
│                                         │
│  [TRAP: COMMON_MISCONCEPTION]         │
│  ⚠ Sunspots are dark surface spots... │
│                                         │
│  ◀ Prev   Skip   Next ▶               │
└─────────────────────────────────────────┘
```
- **Question Card**: Parchment background, DeepOceanBlue text, 18sp, line-height 26sp
- **Options**: Animated border/bg transitions (2dp border, 400ms tween)
- **Cross-out**: Long-press → strikethrough, 50% alpha, disabled
- **Trap Feedback**: Terracotta background, Lightbulb icon, expands below option
- **Confidence Calibration**: After selection, 4 buttons (Certain/Likely/Unsure/Guessing)
- **Progress Bar**: SandGold on DeepOceanBlue 10% track

### 5.4 ResultsScreen — "Base Camp"
```
┌─────────────────────────────────────────┐
│                                         │
│        🏆  Session Complete!            │
│                                         │
│     18/23  (78.3%)                      │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ MARKS-LOST ANALYSIS             │   │
│  │ - 2 x COMMON_MISCONCEPTION      │   │
│  │ - 1 x PARTIAL_TRUTH             │   │
│  │ - 1 x TIMELINE_MISMATCH         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Restart Topic]  [View Traps] [Back]  │
└─────────────────────────────────────────┘
```
- **Celebration**: EmojiEvents icon in SandGold circle
- **Marks-Lost Card**: White surface, DeepOceanBlue text, bullet list

### 5.5 MistakeReplayScreen — "The Compass Correction"
```
┌─────────────────────────────────────────┐
│  ←  Mistake Replay  (12 pending)        │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐   │
│  │ ⚠ TRAP: FALSE_CORRELATION       │   │
│  │ You confused Westerlies with    │   │
│  │ Trade Winds.                    │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ DISENTANGLE: Westerlies vs Trade│   │
│  │                                 │   │
│  │ 🌬️ WESTERLIES                   │   │
│  │ 30°-60° latitude, SW→NE         │   │
│  │                                 │   │
│  │ 🌬️ TRADE WINDS                  │   │
│  │ 0°-30° latitude, NE→SW          │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Practice This Pair →]                │
└─────────────────────────────────────────┘
```
- **Disambiguation Cards**: Side-by-side comparison, color-coded (DeepOceanBlue for both)
- **Evidence Levels**: CONFIRMED (Red), EMERGING (Terracotta), POSSIBLE (SandGold)

### 5.6 InsightsDashboardScreen — "Mission Control"
```
┌─────────────────────────────────────────┐
│  Insights Dashboard                     │
├─────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│  │ READINESS│ │ STREAK  │ │ MASTERY │   │
│  │   72%   │ │   14d   │ │  34/120 │   │
│  └─────────┘ └─────────┘ └─────────┘    │
├─────────────────────────────────────────┤
│  WEAKNESS RADAR (Polar Chart)           │
│  [Visual: 6-axis radar]                 │
│  Conceptual ████████░░  80%             │
│  Map-based  ██████░░░░  60%             │
│  CA Integ.  ████░░░░░░  40%             │
│  Speed      █████████░  90%             │
│  Accuracy   ███████░░░  70%             │
│  Endurance  ██████░░░░  60%             │
├─────────────────────────────────────────┤
│  NEXT BEST ACTION                       │
│  ┌─────────────────────────────────┐   │
│  │ 🎯 "Revise Ocean Currents —     │   │
│  │    3 questions due, 2 traps     │   │
│  │    fallen. 15 min session."     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 5.7 PaperTwinScreen — "The Mirror Exam"
```
┌─────────────────────────────────────────┐
│  Paper Twin: UPSC CSE 2026              │
│  [Generate Mock]                        │
├─────────────────────────────────────────┤
│  Exam DNA:                              │
│  ████████████████████  Conceptual (45%)│
│  ██████████████████    Map-based (30%) │
│  ██████████████        CA Integration(25%)│
│                                         │
│  Settings:                              │
│  ○ 100 Questions  ○ 2 Hours             │
│  ○ -0.66 Penalty  ○ 4 Options           │
│  ○ Include Abstain (BPSC only)          │
│                                         │
│  [START MOCK TEST]                       │
└─────────────────────────────────────────┘
```

---

## 6. GEOGRAPHY-SPECIFIC FEATURES

### 6.1 Map Integration (Critical for Geography)
```kotlin
// MapScreen.kt — Full-screen interactive map
@Composable
fun MapScreen(
    topic: Topic,
    onLocationTap: (LatLng) -> Unit,
    overlayLayers: List<MapLayer> = listOf(
        MapLayer.Rivers, MapLayer.Mountains, 
        MapLayer.Political, MapLayer.ClimateZones
    )
) {
    GoogleMap(
        modifier = Modifier.fillMaxSize(),
        cameraPositionState = rememberCameraPositionState {
            position = CameraPosition.fromLatLngZoom(topic.centerLatLng, 4f)
        },
        properties = MapProperties(mapType = MapType.HYBRID),
        uiSettings = MapUiSettings(
            zoomControlsEnabled = true,
            compassEnabled = true,
            scrollGesturesEnabled = true,
        )
    ) {
        // Overlay KML/GeoJSON layers for rivers, borders, etc.
        overlayLayers.forEach { layer ->
            layer.renderOnMap()
        }
        // Tap to identify feature
        onMapClick { latLng ->
            onLocationTap(latLng)
        }
    }
}
```

### 6.2 Diagram Rendering (Cross-sections, Cycles)
```kotlin
// DiagramViewer.kt — For water cycle, rock cycle, pressure belts
@Composable
fun DiagramViewer(
    diagramUrl: String,
    interactive: Boolean = true,
    labels: Map<String, LatLng> = emptyMap()
) {
    AsyncImage(
        model = diagramUrl,
        contentDescription = "Geography Diagram",
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(4f/3f)
            .clip(MapCorner),
        contentScale = ContentScale.Fit,
    )
    if (interactive) {
        // Tap labels to show definition
        labels.forEach { (name, position) ->
            // Render label overlay at position
        }
    }
}
```

### 6.3 Geographic Name Pronunciation
```kotlin
// TTS integration for difficult names
data class GeoEntity(
    val name: String,
    val pronunciation: String? = null,  // IPA or phonetic
    val audioUrl: String? = null,       // TTS or recorded
    val nativeScript: String? = null    // Devanagari, Tibetan, etc.
)

// Usage in Question Card
IconButton(onClick = { TTS.speak(entity.pronunciation ?: entity.name) }) {
    Icon(Icons.Default.VolumeUp, contentDescription = "Pronounce")
}
```

### 6.4 Unit Converter (Built-in)
```kotlin
// For questions involving km, m, °C, mm, hPa, etc.
object GeoUnits {
    fun convert(value: Double, from: Unit, to: Unit): Double
    fun format(value: Double, unit: Unit, locale: Locale = Locale.getDefault()): String
}

// Auto-detect in explanations: "3,500 km" → tap to see "≈ 2,175 miles"
```

---

## 7. LEARNER MODEL & ADAPTIVE LOGIC

### 7.1 Mastery States (SM-2 Variant)
```
NEW (0) → DUE (1-2 correct) → IMPROVING (3-4) → STRONG (5-6) → MASTERED (7+)
```

### 7.2 Priority Calculation (1=Highest, 5=Lowest)
```kotlin
fun calculatePriority(item: RevisionItem): Int {
    val daysOverdue = (now - item.nextRevisionDate) / DAY_MILLIS
    val trapWeight = if (item.associatedTrap != null) 2 else 0
    val errorWeight = item.incorrectCount * 2
    val basePriority = when {
        item.masteryState == "NEW" -> 1
        item.masteryState == "DUE" -> 2
        item.masteryState == "IMPROVING" -> 3
        item.masteryState == "STRONG" -> 4
        else -> 5
    }
    return min(5, basePriority + daysOverdue + trapWeight + errorWeight)
}
```

### 7.3 Confidence Calibration (Prevents Illusion of Competence)
```kotlin
data class CalibrationState(
    val certainCorrect: Int,
    val certainTotal: Int,
    val likelyCorrect: Int,
    val likelyTotal: Int,
    val unsureCorrect: Int,
    val unsureTotal: Int,
    val guessingCorrect: Int,
    val guessingTotal: Int,
) {
    fun overconfidenceIndex(): Double {
        val certainAcc = certainCorrect.toDouble() / certainTotal.coerceAtLeast(1)
        val guessingAcc = guessingCorrect.toDouble() / guessingTotal.coerceAtLeast(1)
        return certainAcc - guessingAcc  // Should be > 0.5 for good calibration
    }
}
```

---

## 8. IMPLEMENTATION ROADMAP

### Phase 1: Core Content & Provenance (✅ DONE)
- [x] 1200 questions with 100% provenance
- [x] All 666 tests passing
- [x] v13_discovery pipeline operational

### Phase 2: Android App Polish (Current)
- [ ] **Import 1200 questions** into Room via DataImporter
- [ ] **Map integration** (Google Maps SDK + KML layers)
- [ ] **Diagram viewer** for cycles/cross-sections
- [ ] **TTS pronunciation** for geographic names
- [ ] **Unit converter** in explanations

### Phase 3: Adaptive Intelligence
- [ ] **QuestionSelectionEngine** fully adaptive (not random)
- [ ] **PatternShockEngine** confidence calibration UI
- [ ] **ConfusionNetwork** disambiguation cards
- [ ] **PaperTwinEngine** full mock generation

### Phase 4: Geography-Specific UX
- [ ] **Interactive maps** with layer toggles (Rivers, Mountains, Climate)
- [ ] **Diagram hotspots** (tap water cycle stages)
- [ ] **Geo-name pronunciation** (TTS + native script)
- [ ] **Offline map tiles** for key regions (India physical, World political)

### Phase 5: Exam Readiness
- [ ] **Readiness Evidence** (statistical confidence intervals)
- [ ] **Final 30-day plan** (TimeBasedStudyPlanEngine)
- [ ] **Exam-day simulator** (exact timing, penalty, format)

---

## 9. QUALITY GATES (Enforced in CI/CD)

```yaml
# .github/workflows/quality.yml
jobs:
  test:
    steps:
      - run: python -m pytest tests/ -x -q  # 666 tests must pass
      - run: python generate_1200_final.py  # 1200 questions, 100% provenance
      
  android:
    steps:
      - run: ./gradlew testDebugUnitTest
      - run: ./gradlew connectedAndroidTest
      - run: ./gradlew lintDebug
      
  provenance:
    steps:
      - run: python -c "from v13_discovery.provenance import audit_provenance_integrity; assert audit['integrity_rate'] == 1.0"
```

---

## 10. STUDENT JOURNEY MAP

```
NEW USER                    REGULAR USER                    EXAM-READY USER
     │                          │                              │
     ▼                          ▼                              ▼
┌─────────┐              ┌─────────────┐               ┌──────────────┐
│Onboarding│ →            │Topic Selection│ →             │Paper Twin    │
│Exam Select│              │(The Atlas)    │               │(Mock Test)   │
└─────────┘              └─────────────┘               └──────────────┘
     │                          │                              │
     ▼                          ▼                              ▼
┌─────────┐              ┌─────────────┐               ┌──────────────┐
│Practice │              │Practice     │               │Results +     │
│(1st try)│              │(Adaptive)   │               │Analysis      │
└─────────┘              └─────────────┘               └──────────────┘
     │                          │                              │
     ▼                          ▼                              ▼
     │                    ┌─────────────┐               ┌──────────────┐
     │                    │Mistake Replay│              │Readiness     │
     │                    │(Compass)    │               │Evidence      │
     │                    └─────────────┘               └──────────────┘
     │                          │
     └──────────────┬───────────┘
                    ▼
           ┌─────────────────┐
           │Insights Dashboard│
           │(Mission Control) │
           └─────────────────┘
```

---

## 11. ACCESSIBILITY & INCLUSIVITY

| Feature | Implementation |
|---------|----------------|
| **TalkBack** | All icons have `contentDescription`, semantic headings |
| **Large Text** | `sp` units, `fontScale` respected, min 14sp body |
| **Color Blind** | Never rely on color alone (icons + text + patterns) |
| **High Contrast** | `ColorScheme` provides high-contrast variants |
| **RTL** | `LayoutDirection` aware, `start`/`end` padding |
| **Offline** | Room cache + WorkManager sync, 30-day offline support |

---

## 12. PERFORMANCE TARGETS

| Metric | Target | Measurement |
|--------|--------|-------------|
| App Start (Cold) | < 1.5s | `Macrobenchmark` |
| Screen Transition | < 200ms | `FrameTimeline` |
| Question Load | < 100ms | Room query + JSON parse |
| Map Render | < 500ms | `GoogleMap` initial load |
| Database Size | < 50MB | 1200 questions + analytics |
| Sync Time | < 5s | WorkManager periodic |

---

## 13. DEPLOYMENT CHECKLIST

- [ ] **Play Console**: Internal → Closed → Open testing tracks
- [ ] **App Signing**: Play App Signing enabled
- [ ] **Data Safety**: No personal data collected, only local analytics
- [ ] **Target SDK**: 34 (Android 14), Min SDK 24 (Android 7.0)
- [ ] **Architecture**: arm64-v8a, armeabi-v7a (universal APK)
- [ ] **ProGuard/R8**: Enabled, keep Room entities, Provenance classes
- [ ] **Crashlytics**: Firebase Crashlytics integrated
- [ ] **Analytics**: Firebase Analytics (custom events: `question_answered`, `trap_fallen`, `mock_completed`)

---

## 14. FUTURE EXTENSIONS

| Feature | Description | Effort |
|---------|-------------|--------|
| **AR Globe** | Camera-based globe overlay with geo-features | High |
| **Peer Challenges** | 1v1 timed geography duels | Medium |
| **Teacher Dashboard** | Class progress, assignment creation | High |
| **Offline Maps** | MBTiles for India/World physical maps | Medium |
| **AI Tutor** | Gemini-powered "Why is this wrong?" explanations | High |
| **Handwriting** | Stylus input for map labeling practice | Medium |

---

## 15. KEY FILES REFERENCE

| File | Purpose |
|------|---------|
| `v13_discovery/question_synthesizer.py` | Core generation pipeline |
| `v13_discovery/provenance.py` | 6-link Merkle provenance |
| `v13_discovery/auditors.py` | 4-veto auditing gate |
| `app/src/main/java/com/example/repository/*.kt` | 8 domain engines |
| `app/src/main/java/com/example/ui/theme/*.kt` | Design system |
| `app/src/main/java/com/example/ui/screens/*.kt` | All screens |
| `docs/v13_1_architecture.md` | Pipeline contracts |
| `source-material/DataImporterNew.kt` | Markdown → Room import |
| `generated_questions_1200_clean.json` | Production question bank |

---

*This guide is the single source of truth for Tayaari Pakki's architecture, design, and implementation. Update it as the system evolves.*