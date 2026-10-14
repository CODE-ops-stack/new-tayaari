package com.example.repository

import com.example.model.*

class MainsRepository {

    // In-memory catalog of high-yield questions authored by Chief Examiner
    private val _mainsQuestions = mutableListOf<MainsQuestion>()
    val mainsQuestions: List<MainsQuestion> get() = _mainsQuestions

    // History of attempts per question
    private val attemptHistory = mutableMapOf<String, MutableList<MainsEvaluationResult>>()

    init {
        loadCuratedTier1Questions()
    }

    private fun loadCuratedTier1Questions() {
        _mainsQuestions.clear()

        // =========================================================================
        // 1. WEBER'S LEAST COST THEORY & SPATIAL SHIFTS (Topic 18 / Topic 25)
        // =========================================================================
        _mainsQuestions.add(
            MainsQuestion(
                id = "MAINS-Q1",
                chapterCode = "TOPIC_18",
                chapterName = "Industries & Manufacturing",
                level = MainsQuestionLevel.ADVANCED_20M,
                questionText = "Critically analyze Weber's Least Cost Theory in the context of recent spatial shifts in India's iron & steel and sugar industries. Illustrate how non-transport cost factors and footloose dynamics challenge traditional locational paradigms.",
                directiveKeyword = "Critically Analyze",
                isPYQ = true,
                pyqYear = "UPSC 2022 / Predicted Extension",
                funAnalogy = "Weight-loss in sugar vs french fries: Why carry 10kg heavy raw sugarcane or raw potatoes across state borders when 9kg is thrown away as waste? You crush it right at the field! Conversely, for Coca-Cola, water is everywhere, so you bottle inside the city.",
                microStructureBlueprint = listOf(
                    "Quadrant 1: Weberian Theoretical Core (Material Index MI formula, Locational Triangle, Critical Isodapane).",
                    "Quadrant 2: Iron & Steel Spatial Shift (Chota Nagpur coal-bed -> Coastal deepwater ports Hazira/Vizag & Scrap-EAF mini-mills).",
                    "Quadrant 3: Sugar Industry Spatial Shift (Subtropical UP/Bihar -> Tropical Maharashtra/TN cooperative clusters).",
                    "Quadrant 4: Theoretical Critique (D.M. Smith's Spatial Margins, August Lösch's Demand Cones, Footloose high-tech value chains)."
                ),
                synapseBridge = SynapseBridge(
                    paper1TheoreticalAnchor = "Alfred Weber's Least Cost Theory (MI > 1 raw material pull) & D.M. Smith's Spatial Margins to Profitability.",
                    paper2IndianSpatialContext = "Relocation of Indian integrated steel plants to coastal deep-water ports and sugar migration to tropical Peninsular India.",
                    topperQuoteFormula = "The historic migration of India's sugar mills to Maharashtra reflects a shift from Weberian raw-material weight-loss to agro-climatic recovery optimization (higher sucrose content 12% vs 9.5% and 180-day crushing season), expanding Smith's spatial margin of profitability.",
                    empiricalDataEvidence = "Coastal steel plants (AM/NS Hazira, POSCO Paradip, Vizag) bypass domestic high-ash coal by importing Australian coking coal (ash < 10% vs domestic > 25%)."
                ),
                microDiagram = MicroDiagramBlueprint(
                    id = "MD-02",
                    name = "Weberian Locational Triangle & Critical Isodapane",
                    targetSeconds = 20,
                    dimensions = "Spatial Plane (R1, R2, Market M)",
                    strokeInstructions = listOf(
                        "Stroke 1 (4s): Inverted triangle: Top M (Market), Base R1, R2.",
                        "Stroke 2 (5s): Mark Point P (Least Transport Point).",
                        "Stroke 3 (6s): Draw 2 concentric isodapane loops; bold the outer Critical Isodapane.",
                        "Stroke 4 (5s): Place Labor Point L inside loop; annotate: 'Labor Saving > Transport Penalty'."
                    ),
                    asciiRendering = """
       Market (M)                      Market (M)
          / \                             / \
         /   \                           /   \   P2 (Coastal Port:
        /  P1 \  <-- Traditional        /     \      Imported Coking Coal)
       /   .   \     Least Cost Point  /  P2*  \
      /   / \   \                     /________/\
     /___/_____\_\                   /           \
   R1(Coal)    R2(Iron Ore)       R1(Domestic)  R2(Imported)
   [Traditional Weberian MI > 2]     [Modern Port-Led Coastal Shift]
                    """.trimIndent()
                ),
                modelAnswerText = """
1. THEORETICAL ANCHOR: WEBER'S LEAST COST PARADIGM & MATERIAL INDEX
Alfred Weber (1909) postulated that industrial location is governed primarily by transport minimization:
MI = (Weight of Localized Raw Materials) / (Weight of Finished Product)
- MI > 1: Raw material oriented (weight-losing gross inputs).
- MI < 1: Market oriented (weight-gaining).
- MI = 1: Footloose.
Labor cost shifts occur when labor savings exceed extra transport cost (enclosed within the Critical Isodapane).

2. SPATIAL METAMORPHOSIS OF INDIA'S IRON & STEEL INDUSTRY:
- Traditional Phase: Localized in Chota Nagpur belt (Jamshedpur, Bokaro, Bhilai) due to ultra-high MI > 4 (2t iron ore + 1.5t coking coal per tonne steel).
- Contemporary Coastal Shift: Mega-plants at Vizag, Hazira, and Paradip decouple from inland coalfields due to imported Australian coking coal (ash < 10% vs domestic > 25%), eliminating inland rail freight penalties.
- Scrap-based EAF mini-mills near metropolitan construction hubs.

3. SPATIAL MIGRATION OF THE SUGAR INDUSTRY (NORTH TO SOUTH):
- Traditional Gangetic Belt (UP/Bihar): MI ≈ 10 with rapid sucrose inversion within 24h.
- Shift to Peninsular Belt (Maharashtra, TN, Karnataka):
  * Higher sucrose recovery (11.5–12.5% vs 9–10%).
  * Extended crushing season (160–180 days vs 110–120 days).
  * Cooperative capitalization with bagasse cogeneration.

4. THEORETICAL CRITIQUE & MODERN PARADIGMS:
- D.M. Smith's Spatial Margins to Profitability: Viability exists in spatial zone where TR > TC.
- Footloose & High-Tech Dynamics: Transport is < 2% of value; talent, clean power, and PLI policy dictate clusters.
                """.trimIndent(),
                rubric = EvaluationRubric(
                    maxMarks = 20,
                    keyKeywords = listOf("Material Index", "Critical Isodapane", "D.M. Smith", "sucrose recovery", "coking coal ash", "EAF mini-mills", "Agglomeration"),
                    mustCiteTheorists = listOf("Alfred Weber", "D.M. Smith", "August Lösch"),
                    topperBenchmarkScore = 15.0f,
                    atomicPropositions = listOf(
                        AtomicProposition(
                            id = "P1",
                            title = "Weberian Core & Material Index (MI > 1)",
                            conceptClusters = listOf(
                                listOf("material index", "mi >", "mi>", "weight loss", "weight-loss", "gross raw", "transport cost minimization"),
                                listOf("raw material", "field", "mine", "pithead", "source", "crushing", "localized")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "Mastered Weberian Core: Verified Material Index (MI > 1) raw-material pull.",
                            feedbackIfMissed = "Missing Weberian Axiom: Must articulate Material Index formula (MI > 1) and raw material orientation."
                        ),
                        AtomicProposition(
                            id = "P2",
                            title = "Iron & Steel Coastal Shift (Imported Coking Coal)",
                            conceptClusters = listOf(
                                listOf("coastal", "port", "vizag", "hazira", "paradip", "deepwater"),
                                listOf("imported", "australia", "coking coal", "ash", "scrap", "eaf", "mini mill")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "Empirical Proof: Cites Indian coastal steel shift driven by low-ash (<10%) imported Australian coal.",
                            feedbackIfMissed = "Missing Empirical Steel Shift: Explain shift from Chota Nagpur to coastal ports (Vizag/Hazira) due to imported coal."
                        ),
                        AtomicProposition(
                            id = "P3",
                            title = "Sugar Industry Peninsular Migration (Agro-Climatic Advantage)",
                            conceptClusters = listOf(
                                listOf("sugar", "peninsular", "maharashtra", "south", "tropical"),
                                listOf("sucrose", "crushing season", "cooperative", "bagasse", "recovery")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "Agro-Industrial Dynamics: Analyzed Peninsular sugar migration (higher sucrose 12% & extended crushing).",
                            feedbackIfMissed = "Missing Sugar Migration: Address North to South shift driven by tropical sucrose recovery and cooperative models."
                        ),
                        AtomicProposition(
                            id = "P4",
                            title = "Theoretical Critique: D.M. Smith & Footloose Dynamics",
                            conceptClusters = listOf(
                                listOf("smith", "d.m. smith", "dm smith", "lösch", "losch", "footloose"),
                                listOf("spatial margin", "margin of profitability", "demand cone", "sub-optimal", "pli", "high-tech")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "Theoretical Synthesis: Successfully critiqued Weber using D.M. Smith's Spatial Margins to Profitability.",
                            feedbackIfMissed = "Missing Theoretical Critique: 'Critically Analyze' demands citing D.M. Smith's Spatial Margins or Lösch's Demand Cones."
                        )
                    )
                )
            )
        )

        // =========================================================================
        // 2. DETERMINISM, POSSIBILISM & NEO-DETERMINISM (Topic 24 Perspectives)
        // =========================================================================
        _mainsQuestions.add(
            MainsQuestion(
                id = "MAINS-Q2",
                chapterCode = "TOPIC_24",
                chapterName = "Perspectives in Human Geography",
                level = MainsQuestionLevel.APPLIED_15M,
                questionText = "Differentiate between Environmental Determinism and Possibilism. How did Griffith Taylor's Neo-Determinism ('Stop-and-Go Determinism') synthesize this dichotomy in the light of 21st-century planetary boundaries?",
                directiveKeyword = "Differentiate & Synthesize",
                isPYQ = true,
                pyqYear = "UPSC 2022",
                funAnalogy = "Driving a car: Determinism is an automated rollercoaster with no steering wheel; Possibilism is a bulldozer trying to flatten every hill; Neo-Determinism is driving in a city with Traffic Lights (Red = Stop/fragile zone, Yellow = Caution/drip irrigation, Green = Go/fertile plain). Ignore red lights, and the car crashes!",
                microStructureBlueprint = listOf(
                    "Intro: Epistemological debate on nature vs human agency.",
                    "Comparative Matrix: Determinism (Ratzel, Semple) vs Possibilism (Blache, Febvre).",
                    "Griffith Taylor's Traffic Controller synthesis and sustainable speed.",
                    "21st Century Planetary Boundaries (Rockström) & Indian empirical proof (Joshimath subsidence)."
                ),
                synapseBridge = SynapseBridge(
                    paper1TheoreticalAnchor = "Griffith Taylor's Neo-Determinism vs Paul Vidal de la Blache's Possibilism.",
                    paper2IndianSpatialContext = "Joshimath land subsidence (2023) and Western Ghats eco-fragility (Madhav Gadgil report).",
                    topperQuoteFormula = "Taylor's Neo-Determinism provides the philosophical foundation for sustainable development (SDG 2030), confirming that human agency can dictate velocity, but ecological red signals cannot be violated without systemic disaster.",
                    empiricalDataEvidence = "Unplanned hill-toe cutting and tunneling in fragile Himalayan collision zones precipitated the Joshimath sinking disaster."
                ),
                microDiagram = MicroDiagramBlueprint(
                    id = "MD-01B",
                    name = "Taylor's Stop-and-Go Traffic Controller Model",
                    targetSeconds = 18,
                    dimensions = "Tripartite Philosophical Continuum",
                    strokeInstructions = listOf(
                        "Stroke 1 (3s): 3 connected hexagonal cells.",
                        "Stroke 2 (5s): Cell 1 = Determinism (Nature Master); Cell 2 = Possibilism (Man Master); Cell 3 = Neo-Determinism (Traffic Police).",
                        "Stroke 3 (5s): Annotate: 'Car Speed = Human Technology | Red Light = Ecological Carrying Capacity'.",
                        "Stroke 4 (5s): Link to Planetary Boundaries (Rockström)."
                    ),
                    asciiRendering = """
[DETERMINISM]                 [POSSIBILISM]
Nature Master                 Man Master
Passive Human                 Anthropocentric Hubris
      \                            /
       \                          /
        v                        v
         [TAYLOR'S NEO-DETERMINISM]
        "Traffic Controller Paradigm"
     Red Light: Extreme Fragility (Stop)
     Yellow: Drip Adaptation (Caution)
     Green: Fertile Plains (Go)
                    """.trimIndent()
                ),
                modelAnswerText = """
1. DIRECT COMPARATIVE MATRIX:
- Proponents: Determinism (Ratzel, Semple, Huntington) vs Possibilism (Vidal de la Blache, Febvre).
- View of Agency: Passive recipient of topographic-climatic tyranny vs active creative decision-maker.
- Critical Flaw: Teleological & colonial rationalization vs anthropocentric disregard of ecological carrying capacity.

2. GRIFFITH TAYLOR'S STOP-AND-GO SYNTHESIS:
- Nature acts as a traffic controller at a highway junction.
- Man can accelerate the vehicle of industrial civilization, but cannot alter the topography or run red lights.

3. 21ST-CENTURY RELEVANCE:
- Global: 6 of 9 Planetary Boundaries breached (Rockström et al.).
- Indian Context: Joshimath land subsidence (2023) proved that possibilist heavy blast-tunneling on Himalayan unconsolidated moraines triggers catastrophic structural failure.
                """.trimIndent(),
                rubric = EvaluationRubric(
                    maxMarks = 15,
                    keyKeywords = listOf("Griffith Taylor", "Stop-and-Go", "Possibilism", "Environmental Determinism", "carrying capacity", "Planetary Boundaries", "Joshimath"),
                    mustCiteTheorists = listOf("Griffith Taylor", "Friedrich Ratzel", "Paul Vidal de la Blache"),
                    topperBenchmarkScore = 11.5f,
                    atomicPropositions = listOf(
                        AtomicProposition(
                            id = "P1",
                            title = "Determinism vs Possibilism Dichotomy",
                            conceptClusters = listOf(
                                listOf("determinism", "ratzel", "semple", "nature master"),
                                listOf("possibilism", "blache", "febvre", "human agency", "man master")
                            ),
                            weightMarks = 3.5f,
                            feedbackIfCovered = "Epistemological Rigor: Clear contrast between Environmental Determinism and Possibilism.",
                            feedbackIfMissed = "Missing Philosophical Dichotomy: Contrast Ratzel/Semple (Determinism) with Vidal de la Blache (Possibilism)."
                        ),
                        AtomicProposition(
                            id = "P2",
                            title = "Griffith Taylor's Traffic Controller Paradigm",
                            conceptClusters = listOf(
                                listOf("taylor", "griffith taylor", "stop and go", "stop-and-go", "neo-determinism", "neodeterminism"),
                                listOf("traffic", "controller", "red light", "speed", "velocity", "carrying capacity")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "Synthesis Mastered: Cites Taylor's Stop-and-Go traffic controller paradigm.",
                            feedbackIfMissed = "Missing Core Synthesis: Explain Taylor's concept of human technology choosing speed while nature controls the signals."
                        ),
                        AtomicProposition(
                            id = "P3",
                            title = "21st-Century Planetary Boundaries & Indian Application",
                            conceptClusters = listOf(
                                listOf("planetary boundaries", "rockstrom", "carrying capacity", "tipping point", "anthropocene"),
                                listOf("joshimath", "himalaya", "western ghats", "gadgil", "subsidence")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "Contemporary Grounding: Grounded in Planetary Boundaries and Indian proof (Joshimath subsidence).",
                            feedbackIfMissed = "Missing Contemporary Link: Connect Neo-Determinism to modern Planetary Boundaries and Joshimath disaster."
                        )
                    )
                )
            )
        )

        // =========================================================================
        // 3. DAVIS VS PENCK GEOMORPHIC SLOPE EVOLUTION (Topic 5 Geomorphology)
        // =========================================================================
        _mainsQuestions.add(
            MainsQuestion(
                id = "MAINS-Q3",
                chapterCode = "TOPIC_5",
                chapterName = "Geomorphic Processes & Landforms",
                level = MainsQuestionLevel.APPLIED_15M,
                questionText = "Critically analyze the Davisian model of the Geomorphic Cycle of Erosion. Why did Walther Penck reject the concept of sequential time stages, proposing instead that landforms reflect the ratio between endogenetic uplift rate and exogenetic denudation rate?",
                directiveKeyword = "Critically Analyze",
                isPYQ = true,
                pyqYear = "UPSC 2020",
                funAnalogy = "Davis thinks of a mountain like a human: born, grows old, wrinkles, and flattens into a calm senile plain. Penck says: 'No! The mountain is like an elevator going up while someone chips away at the roof simultaneously. If the elevator rises faster than you can chip, it gets steeper!'",
                microStructureBlueprint = listOf(
                    "Intro: Davisian Triad (Structure, Process, Stage) and time-dependent decay.",
                    "Penck's Radical Departure: Coeval uplift and erosion; Morphological Analysis.",
                    "Penck's 3 Development Phases: Aufsteigende, Gleichförmige, Absteigende Entwicklung.",
                    "Indian Field Evidence: Tectonic youthful incision in Himalayas vs relict senile plains in Peninsular India."
                ),
                synapseBridge = SynapseBridge(
                    paper1TheoreticalAnchor = "W.M. Davis (Peneplanation / Down-wearing) vs Walther Penck (Slope Replacement / Endrumpf).",
                    paper2IndianSpatialContext = "Himalayan antecedent gorges (Indus, Brahmaputra) confirming continuous tectonic uplift outstripping erosion.",
                    topperQuoteFormula = "While Davisian peneplanation models stable cratonic shields like the Peninsular Deccan, Himalayan orogenesis validates Penckian waxing development where rapid uplift outpaces fluvial downcutting, producing razor-sharp convex youthful canyons.",
                    empiricalDataEvidence = "Main Central Thrust (MCT) neotectonic activity producing incised knickpoints across Uttarakhand river profiles."
                ),
                microDiagram = MicroDiagramBlueprint(
                    id = "MD-01",
                    name = "Davisian vs Penckian Slope & Elevation Curves",
                    targetSeconds = 20,
                    dimensions = "Elevation (H) vs Time (t)",
                    strokeInstructions = listOf(
                        "Stroke 1 (3s): L-shaped axis: Y = Elevation, X = Time.",
                        "Stroke 2 (5s): Davis curve: Instant vertical uplift step, then UC & LC converge to Peneplain.",
                        "Stroke 3 (7s): Penck curve: Waxing (Aufsteigende), rectilinear (Gleichförmige), waning (Absteigende) to Endrumpf.",
                        "Stroke 4 (5s): Annotate: 'UC = Divides | LC = Valley Bottoms | Primärrumpf -> Endrumpf'."
                    ),
                    asciiRendering = """
Elevation (H)
 ^
 |        /---\ UC (Divides)               /---\ UC
 |       /     \                          /     \
 |      /       \                        /       \
 |     /         \                      /         \ (Gleichförmige)
 |    /           \ Peneplain          /           \-------
 |   /   Relief    \                  / Aufsteigende       \ Endrumpf
 |  /-----\         \                /                      \--------
 | /       \         \ LC (Valleys) /                        \ LC
 |/         \_________\            /                          \_______
 +--------------------------> Time +----------------------------------> Time
      DAVIS (Episodic Uplift)              PENCK (Continuous Uplift/Erosion)
                    """.trimIndent()
                ),
                modelAnswerText = """
1. THE DAVISIAN GEOMORPHIC CYCLE (1899):
W.M. Davis postulated that landforms are a function of 'Structure, Process, and Stage':
- Episodic Assumption: Rapid, short-lived uplift of a landmass, with erosion commencing ONLY after uplift entirely ceases.
- Sequential Stages: Youth (V-notches, relief expands) -> Maturity (lateral planation) -> Old Age (Peneplain with Monadnocks).

2. WALTHER PENCK'S MORPHOLOGICAL ANALYSIS (1924):
Penck attacked Davis's historical stage cycle as physically unrealistic:
- Coeval Dynamics: Uplift and erosion occur simultaneously and continuously.
- Landforms = Ratio of Endogenetic forces (uplift rate) to Exogenetic forces (erosion rate).
- Three Evolutionary Phases (Entwicklung):
  1. Aufsteigende Entwicklung (Waxing): Uplift rate > Erosion rate. Convex slopes, incised gorges.
  2. Gleichförmige Entwicklung (Uniform): Uplift rate = Erosion rate. Rectilinear slopes; Boschwand & Haldenhang.
  3. Absteigende Entwicklung (Waning): Uplift rate < Erosion rate. Concave slopes terminating in an Endrumpf with Inselbergs.

3. INDIAN EMPIRICAL APPLICATION (PAPER-II):
- Himalayas: Active Indo-Eurasian convergence (5 cm/yr) creates Penckian waxing relief with youthful convex canyons.
- Peninsular India: Ancient Precambrian craton exhibits senile planation surfaces with monadnock-like residual hills.
                """.trimIndent(),
                rubric = EvaluationRubric(
                    maxMarks = 15,
                    keyKeywords = listOf("Walther Penck", "W.M. Davis", "Aufsteigende Entwicklung", "Endrumpf", "Primärrumpf", "Haldenhang", "Boschwand", "Peneplain"),
                    mustCiteTheorists = listOf("W.M. Davis", "Walther Penck", "John Hack"),
                    topperBenchmarkScore = 11.5f,
                    atomicPropositions = listOf(
                        AtomicProposition(
                            id = "P1",
                            title = "Davisian Triad & Sequential Time Cycle",
                            conceptClusters = listOf(
                                listOf("davis", "davisian", "structure process stage", "triad"),
                                listOf("peneplain", "monadnock", "episodic uplift", "time dependent", "down-wasting")
                            ),
                            weightMarks = 3.5f,
                            feedbackIfCovered = "Davisian Framework: Cites Structure, Process, Stage and time-dependent peneplanation.",
                            feedbackIfMissed = "Missing Davisian Core: Explain Davis's assumption that erosion begins only after rapid uplift ceases."
                        ),
                        AtomicProposition(
                            id = "P2",
                            title = "Penck's Morphological Analysis & Rate Ratio",
                            conceptClusters = listOf(
                                listOf("penck", "walther penck", "morphological analysis"),
                                listOf("ratio", "endogenetic", "exogenetic", "simultaneous", "coeval", "uplift rate", "erosion rate")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "Penckian Departure: Articulates simultaneous uplift/erosion and the endogenetic-to-exogenetic rate ratio.",
                            feedbackIfMissed = "Missing Penckian Premise: Explain that landforms reflect the ratio of uplift rate to erosion rate."
                        ),
                        AtomicProposition(
                            id = "P3",
                            title = "Penck's 3 Development Phases (Entwicklung)",
                            conceptClusters = listOf(
                                listOf("aufsteigende", "gleichformige", "absteigende", "entwicklung", "phases"),
                                listOf("endrumpf", "primarrumpf", "boschwand", "haldenhang", "convex", "rectilinear")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "Academic Nomenclature: Uses exact terms (Aufsteigende, Gleichförmige, Absteigende, Endrumpf).",
                            feedbackIfMissed = "Missing German Terminology: Inject Penck's exact phases (Aufsteigende, Gleichförmige, Absteigende)."
                        )
                    )
                )
            )
        )

        // =========================================================================
        // 4. COUPLED ENSO & IOD MONSOON TELECONNECTIONS (Topic 12 Climatology)
        // =========================================================================
        _mainsQuestions.add(
            MainsQuestion(
                id = "MAINS-Q4",
                chapterCode = "TOPIC_12",
                chapterName = "Indian Climate & Monsoon",
                level = MainsQuestionLevel.APPLIED_15M,
                questionText = "Explain the mechanisms of the Indian Ocean Dipole (IOD) and the El Niño Southern Oscillation (ENSO). How does their phase interaction dictate the spatial and temporal anomalies of the Indian Southwest Monsoon?",
                directiveKeyword = "Explain & Interlink",
                isPYQ = true,
                pyqYear = "UPSC 2023",
                funAnalogy = "The Indian Monsoon is a vacuum cleaner pulling ocean moisture. El Niño in the Pacific is a massive LEAK in the vacuum hose (diverting rain to Peru and starving India). A Positive IOD (+IOD) in the Indian Ocean is a BOOSTER MOTOR right in India's backyard. When both happen together, the +IOD booster motor can cancel out the Pacific leak!",
                microStructureBlueprint = listOf(
                    "Intro: Indian Monsoon as a coupled planetary ocean-atmosphere system.",
                    "ENSO Mechanism: Pacific Walker Cell displacement & atmospheric subsidence over India.",
                    "IOD Mechanism: Dipole Mode Index (DMI), warm pool near East Africa vs Sumatra upwelling.",
                    "The Teleconnection Duel: Constructive vs destructive phase interactions (1997 vs 2002 droughts)."
                ),
                synapseBridge = SynapseBridge(
                    paper1TheoreticalAnchor = "Walker Circulation & Planetary Ocean-Atmosphere Teleconnections (Bjerknes).",
                    paper2IndianSpatialContext = "Kharif foodgrain production volatility and drought regionalization in Northwest India.",
                    topperQuoteFormula = "Dynamic long-range forecasting by the IMD proves that the Indian Ocean Dipole acts as an oceanic shield against Pacific El Niño disruptions, where a positive DMI sustains the cross-equatorial Somali Jet even during warm ENSO phases.",
                    empiricalDataEvidence = "During the 1997 Super El Niño, a historic +IOD delivered near-normal monsoon rainfall across India (102% of LPA)."
                ),
                microDiagram = MicroDiagramBlueprint(
                    id = "MD-06",
                    name = "Coupled Pacific-Indian Ocean Teleconnection Box",
                    targetSeconds = 20,
                    dimensions = "Indo-Pacific Equatorial Basin",
                    strokeInstructions = listOf(
                        "Stroke 1 (4s): Two side-by-side sea basins: Left = Indian Ocean, Right = Pacific Ocean.",
                        "Stroke 2 (6s): Draw Walker cell rising over West Pacific / Indonesia, sinking over Peru.",
                        "Stroke 3 (5s): Draw tilted thermocline: deep in West Pacific, shallow in East.",
                        "Stroke 4 (5s): Mark +IOD warm anomaly in Western Indian Ocean feeding Somali Jet."
                    ),
                    asciiRendering = """
WEST INDIAN OCEAN         INDONESIAN SEAS          EAST PACIFIC (PERU)
      ^ Rising                  ^ Rising (Normal)         v Sinking
     [+IOD Warm Pool]          [Warm Pool / Convection]  [Cold Upwelling]
            \                          /
             \                        /
              v                      v
        [INDIAN SUMMER MONSOON TROUGH]
     Rule: +IOD neutralizes El Niño drought via local Somali Jet moisture pumping!
                    """.trimIndent()
                ),
                modelAnswerText = """
The Indian Summer Monsoon Rainfall (ISMR) is intimately coupled to global ocean-atmosphere teleconnections across the Indo-Pacific realm.

1. INDEPENDENT PHYSICAL MECHANISMS:
• ENSO (Pacific Basin):
  - Normal Phase: Strong easterly trade winds pool warm water in the western Pacific. Ascending limb of the Walker circulation over Indonesia supports the monsoon trough.
  - El Niño Phase: Warm pool shifts eastward to central/eastern Pacific. Ascending convection relocates to Peru; anomalous atmospheric subsidence descends over India, triggering monsoon breaks and drought.
• IOD (Indian Ocean Basin):
  - Quantified via Dipole Mode Index (DMI): SST gradient between Western Equatorial Indian Ocean (50°–70°E) and Eastern Indian Ocean (90°–110°E).
  - Positive IOD (+IOD): Anomalously warm waters off East Africa and cool upwelling near Sumatra enhance local convection and moisture flux directly into the Southwest Monsoon.

2. COUPLED INTERACTION DYNAMICS (THE TELECONNECTION DUEL):
- El Niño + Negative IOD: Compounded subsidence; catastrophic all-India drought (e.g., 2002 severe drought).
- El Niño + Positive IOD: +IOD acts as an 'Oceanic Shield'; local western Indian Ocean convection overcomes Pacific subsidence (e.g., 1997 Super El Niño yielded normal rain; 2019 excess rainfall).
- La Niña + Positive IOD: Synergistic moisture pumping; widespread flooding and extended withdrawal.
                """.trimIndent(),
                rubric = EvaluationRubric(
                    maxMarks = 15,
                    keyKeywords = listOf("Indian Ocean Dipole", "ENSO", "Walker Circulation", "Dipole Mode Index", "Somali Jet", "El Niño Modoki", "thermocline"),
                    mustCiteTheorists = listOf("Gilbert Walker", "Jacob Bjerknes"),
                    topperBenchmarkScore = 11.5f,
                    atomicPropositions = listOf(
                        AtomicProposition(
                            id = "P1",
                            title = "Pacific ENSO & Walker Circulation Mechanism",
                            conceptClusters = listOf(
                                listOf("enso", "el nino", "walker cell", "walker circulation"),
                                listOf("subsidence", "trade winds", "warm pool", "trough", "drought")
                            ),
                            weightMarks = 3.5f,
                            feedbackIfCovered = "ENSO Teleconnection: Clear explanation of Walker circulation displacement causing atmospheric subsidence.",
                            feedbackIfMissed = "Missing ENSO Mechanism: Detail how El Niño shifts convection eastward, forcing subsidence over India."
                        ),
                        AtomicProposition(
                            id = "P2",
                            title = "Indian Ocean Dipole (IOD) & Dipole Mode Index",
                            conceptClusters = listOf(
                                listOf("iod", "indian ocean dipole", "dmi", "dipole mode index"),
                                listOf("somali jet", "east africa", "sumatra", "positive iod", "+iod", "upwelling")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "IOD Mechanism: Articulates SST gradient between Western Indian Ocean and Sumatra upwelling.",
                            feedbackIfMissed = "Missing IOD Formulation: Explain the Dipole Mode Index (DMI) and +IOD moisture flux."
                        ),
                        AtomicProposition(
                            id = "P3",
                            title = "The Teleconnection Duel (Shielding Effect)",
                            conceptClusters = listOf(
                                listOf("+iod", "positive iod", "shield", "counter", "interaction"),
                                listOf("1997", "normal monsoon", "excess", "neutralize", "somali jet")
                            ),
                            weightMarks = 4.0f,
                            feedbackIfCovered = "Teleconnection Duel: Explains how a +IOD acts as an oceanic shield against Pacific El Niño droughts.",
                            feedbackIfMissed = "Missing Coupled Interaction: Explain how +IOD overcomes El Niño subsidence (e.g. 1997 Super El Niño)."
                        )
                    )
                )
            )
        )

        // =========================================================================
        // 5. LANDSLIDES: HIMALAYAS VS WESTERN GHATS (Topic 10 / Contemporary)
        // =========================================================================
        _mainsQuestions.add(
            MainsQuestion(
                id = "MAINS-Q5",
                chapterCode = "TOPIC_10",
                chapterName = "Physiography & Hazards",
                level = MainsQuestionLevel.FOUNDATION_10M,
                questionText = "Differentiate between the causes, triggers, and geomorphic mechanisms of landslides in the Himalayan Region versus the Western Ghats. Suggest site-specific disaster risk reduction strategies.",
                directiveKeyword = "Differentiate & Suggest",
                isPYQ = true,
                pyqYear = "UPSC 2021",
                funAnalogy = "Himalaya is a restless teenager going through a growth spurt—rocks are brittle, shattered, and folded by colliding tectonic plates. Western Ghats is a sleeping ancient grandfather—the bedrock is solid rigid basalt, but when 3,000mm monsoon rain drenches the thick sponge-like soil on top, the wet mud slips off like wet soap on a tin roof!",
                microStructureBlueprint = listOf(
                    "Intro: High landslide susceptibility in both regions governed by contrasting geomorphic regimes.",
                    "Comparative Matrix: Tectonic youth vs ancient fault scarp; Lithology, Triggering mechanisms, Anthropogenic stressors.",
                    "20s Diagram: Himalayan thrust fold slope vs Western Ghats weathered laterite regolith slip.",
                    "Site-Specific DRR: Seismically resilient bio-engineering vs Gadgil committee eco-zoning."
                ),
                synapseBridge = SynapseBridge(
                    paper1TheoreticalAnchor = "Slope Instability & Shear Stress vs Shear Strength (Terzaghi's effective stress).",
                    paper2IndianSpatialContext = "Wayanad catastrophe (2024) vs Char Dham highway toe-cutting slope failures.",
                    topperQuoteFormula = "While Himalayan landslides represent deep-seated structural collapses driven by neotectonic plate convergence, Western Ghats slope failures represent shallow translational debris flows triggered by extreme pore-water pressure along the weathered laterite-bedrock interface.",
                    empiricalDataEvidence = "Wayanad (July 2024) received > 500 mm rain in 48 hours, mobilizing loose lateritic regolith along 30° slopes."
                ),
                microDiagram = MicroDiagramBlueprint(
                    id = "MD-08B",
                    name = "Himalayan vs Western Ghats Slope Failure Profiles",
                    targetSeconds = 18,
                    dimensions = "Geomorphic Slope Cross-Sections",
                    strokeInstructions = listOf(
                        "Stroke 1 (4s): Left: Steep folded strata with Main Boundary Thrust fault.",
                        "Stroke 2 (5s): Right: Horizontal Deccan basalt lava flows with thick red laterite top cap.",
                        "Stroke 3 (5s): Mark failure plane: Deep rock fracture (Himalaya) vs Shallow mud regolith slip (Ghats).",
                        "Stroke 4 (4s): Annotate triggers: 'Seismic tremors + GLOFs' vs '3,000mm Orographic Pore Pressure'."
                    ),
                    asciiRendering = """
HIMALAYAS (Active Collision Zone)          WESTERN GHATS (Precambrian Escarpment)
     /\\  Folded Strata                         |  Thick Permeable Laterite Cap
    /  \\ Low Shear Strength                    |  (High Pore-Water Pressure)
   / *  \\ [Seismic Tremors]                 ---|-----------------------------
  /______\\ MCT / MBT Fault Lines           ====|==== Rigid Impermeable Basalt
  Mechanism: Deep Rockfall & Slump         Mechanism: Shallow Debris Avalanche
                    """.trimIndent()
                ),
                modelAnswerText = """
1. COMPARATIVE GEOMORPHIC MATRIX:
Parameter            Himalayan Region                        Western Ghats
-------------------------------------------------------------------------------------------------
Tectonic Regime      Youthful, active Indo-Eurasian          Ancient, rigid Precambrian fault scarp; 
                     collision zone; high seismicity.        tectonically quiescent.
Lithology            Fractured sedimentary schists,          Hard crystalline Deccan basalt/charnockite; 
                     shales, phyllites; low shear strength.  thick porous lateritic regolith cap.
Primary Triggers     Orographic bursts PLUS freeze-thaw,     Intense monsoonal downpours (>3,000 mm) 
                     glacial melt, and moraine breaches.     causing acute pore-water pressure spikes.
Failure Mechanism    Deep-seated rotational rockslides       Rapid translational debris flows & mud avalanches 
                     and catastrophic debris avalanches.     along the regolith-bedrock boundary.
Human Stressors      Hydro-tunnel blasting & Char Dham       Monoculture plantations (tea/rubber), 
                     four-lane slope toe undercut.           quarrying, resort sprawl (Wayanad 2024).

2. SITE-SPECIFIC DISASTER RISK REDUCTION:
• Himalayas: LiDAR-based slope hazard zonation; tunnel-bypass design avoiding fault gouges; automated GLOF sirens.
• Western Ghats: Strict enforcement of Madhav Gadgil Committee eco-sensitive zones; ban on slope-toe quarrying; agro-forestry root anchoring.
                """.trimIndent(),
                rubric = EvaluationRubric(
                    maxMarks = 10,
                    keyKeywords = listOf("Shear Strength", "pore-water pressure", "Deccan basalt", "lateritic regolith", "neotectonics", "Wayanad", "Gadgil Committee"),
                    mustCiteTheorists = listOf("Karl Terzaghi", "Madhav Gadgil"),
                    topperBenchmarkScore = 7.5f,
                    atomicPropositions = listOf(
                        AtomicProposition(
                            id = "P1",
                            title = "Contrasting Tectonic & Lithological Regimes",
                            conceptClusters = listOf(
                                listOf("himalaya", "tectonic", "collision", "folded", "schist", "mct", "mbt"),
                                listOf("western ghats", "precambrian", "basalt", "escarpment", "shield", "rigid")
                            ),
                            weightMarks = 2.5f,
                            feedbackIfCovered = "Geomorphic Contrast: Clear contrast between active Himalayan collision and ancient Precambrian basalt scarp.",
                            feedbackIfMissed = "Missing Lithological Contrast: Compare fragile Himalayan schists with rigid Western Ghats basalt."
                        ),
                        AtomicProposition(
                            id = "P2",
                            title = "Geomorphic Failure Mechanisms (Deep Rockfall vs Shallow Regolith)",
                            conceptClusters = listOf(
                                listOf("shear strength", "terzaghi", "effective stress", "pore water", "pore-water"),
                                listOf("deep-seated", "shallow", "debris flow", "laterite", "regolith", "mud avalanche")
                            ),
                            weightMarks = 2.5f,
                            feedbackIfCovered = "Failure Mechanisms: Differentiates deep-seated Himalayan rockslides from shallow Ghats lateritic debris slips.",
                            feedbackIfMissed = "Missing Mechanics: Contrast deep-seated rockfall with intense monsoonal pore-water pressure along laterite regolith."
                        ),
                        AtomicProposition(
                            id = "P3",
                            title = "Site-Specific Disaster Risk Reduction (DRR)",
                            conceptClusters = listOf(
                                listOf("gadgil", "madhav gadgil", "eco-sensitive", "kasturirangan", "bio-engineering"),
                                listOf("hazard zonation", "lidar", "gaps", "wayanad", "quarrying", "toe-cutting")
                            ),
                            weightMarks = 2.5f,
                            feedbackIfCovered = "Actionable DRR: Recommends Gadgil committee eco-zoning for Ghats and slope bio-engineering for Himalayas.",
                            feedbackIfMissed = "Missing Site-Specific DRR: Suggest Gadgil committee eco-zoning for Ghats and LiDAR hazard mapping for Himalayas."
                        )
                    )
                )
            )
        )
    }

    fun getQuestionById(id: String): MainsQuestion? {
        return _mainsQuestions.find { it.id == id } ?: _mainsQuestions.firstOrNull()
    }

    private fun levenshteinDistance(s1: String, s2: String): Int {
        val dp = Array(s1.length + 1) { IntArray(s2.length + 1) }
        for (i in 0..s1.length) dp[i][0] = i
        for (j in 0..s2.length) dp[0][j] = j
        for (i in 1..s1.length) {
            for (j in 1..s2.length) {
                val cost = if (s1[i - 1] == s2[j - 1]) 0 else 1
                dp[i][j] = minOf(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost
                )
            }
        }
        return dp[s1.length][s2.length]
    }

    private fun getAliasesForConcept(term: String): List<String> {
        val t = term.lowercase()
        return when {
            t.contains("weber") -> listOf("weber", "weberian", "least cost", "locational triangle")
            t.contains("smith") -> listOf("smith", "d.m. smith", "dm smith", "spatial margin")
            t.contains("lösch") || t.contains("losch") -> listOf("losch", "lösch", "loesch", "demand cone")
            t.contains("davis") -> listOf("davis", "davisian", "cycle of erosion", "peneplain", "monadnock")
            t.contains("penck") -> listOf("penck", "penk", "morphological analysis", "entwicklung", "endrumpf", "primarrumpf")
            t.contains("taylor") -> listOf("taylor", "griffith taylor", "stop and go", "neo-determinism", "neodeterminism")
            t.contains("ratzel") -> listOf("ratzel", "friedrich ratzel", "anthropogeography")
            t.contains("blache") -> listOf("blache", "vidal", "possibilism")
            t.contains("king") -> listOf("king", "l.c. king", "pediplanation")
            t.contains("terzaghi") -> listOf("terzaghi", "karl terzaghi", "shear strength", "effective stress")
            t.contains("gadgil") -> listOf("gadgil", "madhav gadgil", "eco-sensitive")
            t.contains("walker") -> listOf("walker", "gilbert walker", "walker cell", "walker circulation")
            t.contains("bjerknes") -> listOf("bjerknes", "jacob bjerknes", "teleconnection")
            t.contains("isodapane") -> listOf("isodapane", "isodapan", "critical isodapane")
            t.contains("material index") -> listOf("material index", "mi >", "mi>", "mi =", "mi=")
            else -> emptyList()
        }
    }

    private fun fuzzyMatches(textLower: String, tokens: List<String>, target: String): Boolean {
        val targetLower = target.lowercase().trim()
        if (textLower.contains(targetLower)) return true

        val aliases = getAliasesForConcept(targetLower)
        for (alias in aliases) {
            if (textLower.contains(alias)) return true
        }

        val targetWords = targetLower.split("\\s+".toRegex()).filter { it.length >= 4 }
        if (targetWords.isEmpty()) return false

        for (tw in targetWords) {
            val maxAllowedDist = if (tw.length >= 8) 2 else 1
            val matchedToken = tokens.any { token ->
                token.length >= 4 && kotlin.math.abs(token.length - tw.length) <= maxAllowedDist &&
                        levenshteinDistance(token, tw) <= maxAllowedDist
            }
            if (matchedToken) return true
        }
        return false
    }

    /**
     * Evaluates a student's answer using the Offline Chief Evaluator Rubric.
     * Features:
     * 1. Typo / Phonetic fault-tolerance (Levenshtein & Aliases)
     * 2. Atomic Proposition Equivalence (Length-invariant scoring for concise vs verbose answers)
     * 3. Word Count Envelope & Density Calibration
     * 4. 5D P-H-E-S-G Dimensional Depth
     * 5. Micro-Diagram verification
     */
    fun evaluateAnswer(
        questionId: String,
        userWrittenText: String,
        hasDiagramDrawn: Boolean,
        diagramStrokeAccuracy: Float = 0.85f,
        timeTakenSeconds: Int = 500
    ): MainsEvaluationResult {
        val q = getQuestionById(questionId) ?: _mainsQuestions.first()
        val rubric = q.rubric
        val maxMarks = rubric.maxMarks.toFloat()

        val textLower = userWrittenText.lowercase()
        val rawTokens = textLower.split("[\\s,.;:()\"'-]+".toRegex()).filter { it.isNotBlank() }
        val wordCount = userWrittenText.trim().split("\\s+".toRegex()).filter { it.isNotBlank() }.size
        val targetLimit = q.level.wordLimit

        // 1. Fuzzy Theorist & Keyword Attribution (Typo-Tolerant)
        val citedTheorists = rubric.mustCiteTheorists.count { fuzzyMatches(textLower, rawTokens, it) }
        val theoristRatio = citedTheorists.toFloat() / rubric.mustCiteTheorists.size.coerceAtLeast(1)

        val matchedKeywords = rubric.keyKeywords.count { fuzzyMatches(textLower, rawTokens, it) }
        val keywordRatio = matchedKeywords.toFloat() / rubric.keyKeywords.size.coerceAtLeast(1)

        // 2. Atomic Proposition Equivalence (Length-Invariant Semantic Meaning)
        val coveredPropositions = mutableListOf<String>()
        val missedPropositions = mutableListOf<String>()
        var propositionScoreEarned = 0.0f
        var totalPropositionWeight = 0.0f

        for (prop in rubric.atomicPropositions) {
            totalPropositionWeight += prop.weightMarks
            // A proposition is covered if EVERY required conceptCluster has at least ONE term matched
            val isCovered = prop.conceptClusters.all { cluster ->
                cluster.any { term -> fuzzyMatches(textLower, rawTokens, term) }
            }

            if (isCovered) {
                coveredPropositions.add(prop.feedbackIfCovered)
                propositionScoreEarned += prop.weightMarks
            } else {
                missedPropositions.add(prop.feedbackIfMissed)
            }
        }

        val propositionRatio = if (totalPropositionWeight > 0f) {
            (propositionScoreEarned / totalPropositionWeight).coerceIn(0.0f, 1.0f)
        } else {
            theoristRatio * 0.5f + keywordRatio * 0.5f
        }

        // Conceptual Density: Percentage of core atomic propositions packed into answer
        val conceptualDensity = if (rubric.atomicPropositions.isNotEmpty()) {
            (coveredPropositions.size.toFloat() / rubric.atomicPropositions.size.toFloat()) * 100f
        } else {
            keywordRatio * 100f
        }

        // 3. Word Count Envelope Calibration (Parabolic sweet spot with High-Density Boost)
        val (baseMultiplier, envelopeFeedback) = when {
            wordCount < (targetLimit * 0.25) -> {
                Pair(0.75f, "⚠️ Underdeveloped Answer (${wordCount}W vs ${targetLimit}W target). Expand your arguments to satisfy UPSC depth.")
            }
            wordCount < (targetLimit * 0.60) -> {
                Pair(0.92f, "⚡ High Word Economy (${wordCount}W). Concepts are concise; ensure empirical examples are detailed.")
            }
            wordCount <= (targetLimit * 1.30) -> {
                Pair(1.00f, "🎯 Optimal UPSC Exam Envelope (${wordCount}W / ${targetLimit}W target). Excellent balance of pace and paper space.")
            }
            wordCount <= (targetLimit * 1.60) -> {
                Pair(0.95f, "⏱️ Extended Length (${wordCount}W). Good detail, but watch your exam clock to avoid leaving later questions.")
            }
            else -> {
                Pair(0.88f, "🚨 Booklet & Time Overflow (${wordCount}W). Exceeds physical UPSC 2-page answer booklet and steals time!")
            }
        }

        // If candidate achieves high conceptual density (>= 75%), boost multiplier so concise masters are not penalized
        val envelopeMultiplier = if (conceptualDensity >= 75f) {
            baseMultiplier.coerceAtLeast(0.96f)
        } else {
            baseMultiplier
        }

        // 4. Component Scoring (Out of maxMarks * component weight)
        val maxPerComponent = maxMarks * 0.20f

        // Theory score blends theorist citation and proposition mastery
        val scoreTheory = (maxPerComponent * (0.35f + 0.35f * theoristRatio + 0.30f * propositionRatio)).coerceIn(1.0f, maxPerComponent)
        val scoreEmpirical = (maxPerComponent * (0.30f + 0.40f * keywordRatio + 0.30f * propositionRatio)).coerceIn(1.0f, maxPerComponent)

        val scoreDiagram = if (hasDiagramDrawn) {
            (maxPerComponent * diagramStrokeAccuracy).coerceIn(2.0f, maxPerComponent)
        } else {
            0.5f // Penalty for zero diagram in optional answer
        }

        // Expanded 5D P-H-E-S-G Ontology
        val hasP = textLower.contains("physical") || textLower.contains("geomorph") || textLower.contains("climate") ||
                textLower.contains("litholog") || textLower.contains("slope") || textLower.contains("drainage") ||
                textLower.contains("relief") || textLower.contains("hydrolog") || textLower.contains("pedogen") ||
                textLower.contains("soil") || textLower.contains("sucrose") || textLower.contains("monsoon")
        val hasH = textLower.contains("human") || textLower.contains("labor") || textLower.contains("labour") ||
                textLower.contains("migrat") || textLower.contains("tribal") || textLower.contains("demograph") ||
                textLower.contains("workforce") || textLower.contains("cooperative") || textLower.contains("displace")
        val hasE = textLower.contains("economic") || textLower.contains("cost") || textLower.contains("transport") ||
                textLower.contains("freight") || textLower.contains("material index") || textLower.contains("agglomerat") ||
                textLower.contains("value chain") || textLower.contains("capital") || textLower.contains("eaf")
        val hasS = textLower.contains("spatial") || textLower.contains("region") || textLower.contains("coastal") ||
                textLower.contains("hinterland") || textLower.contains("corridor") || textLower.contains("port") ||
                textLower.contains("chota nagpur") || textLower.contains("peninsular") || textLower.contains("western ghats")
        val hasG = textLower.contains("govern") || textLower.contains("policy") || textLower.contains("scheme") ||
                textLower.contains("tribunal") || textLower.contains("act") || textLower.contains("statutory") ||
                textLower.contains("gadgil") || textLower.contains("pli") || textLower.contains("gati shakti")

        val dimensionCount = listOf(hasP, hasH, hasE, hasS, hasG).count { it }
        val scorePhesg = (maxPerComponent * (dimensionCount.toFloat() / 5.0f).coerceAtLeast(0.4f)).coerceIn(1.0f, maxPerComponent)

        val timePenalty = if (timeTakenSeconds > q.level.timeSeconds + 60) 0.85f else 1.0f
        val scorePresentation = (maxPerComponent * 0.85f * timePenalty).coerceIn(1.0f, maxPerComponent)

        // Aggregate Raw Score adjusted by envelopeMultiplier
        val uncalibratedTotal = scoreTheory + scoreEmpirical + scoreDiagram + scorePhesg + scorePresentation
        val calibratedTotal = (uncalibratedTotal * envelopeMultiplier).coerceIn(1.0f, maxMarks)
        val totalScore = String.format("%.1f", calibratedTotal).toFloat()

        // Detailed Feedback Construction
        val green = mutableListOf<String>()
        val yellow = mutableListOf<String>()
        val red = mutableListOf<String>()

        // Add verified proposition highlights
        coveredPropositions.forEach { green.add("✓ $it") }

        if (theoristRatio >= 0.6f) {
            green.add("Excellent theoretical attribution: Cites ${q.rubric.mustCiteTheorists.joinToString(", ")}.")
        } else {
            red.add("Omission: Failed to explicitly name mandatory theorists (${q.rubric.mustCiteTheorists.joinToString(", ")}).")
        }

        if (hasDiagramDrawn) {
            green.add("Visual schematic included: 20s Micro-diagram earns visuo-spatial bonus (+2.5 Marks).")
        } else {
            red.add("Zero Diagram: Missing schematic diagram caps the answer at sub-par 40% band.")
        }

        // Add missed proposition penalties
        missedPropositions.forEach { red.add("✗ $it") }

        if (keywordRatio >= 0.5f) {
            green.add("High academic terminology density: Verified ${matchedKeywords} core syllabus terms.")
        } else {
            yellow.add("Prose reads like General Studies (GS-1). Inject academic terms (e.g., Isodapane, Spatial Margins, Carrying Capacity).")
        }

        if (dimensionCount < 3) {
            yellow.add("Narrow dimensional coverage: Missing P-H-E-S-G dimensions. Include governance and spatial perspectives.")
        }

        // Directive Compliance Check
        if (q.directiveKeyword.contains("Critically", ignoreCase = true)) {
            val hasCritique = textLower.contains("critic") || textLower.contains("limitation") ||
                    textLower.contains("smith") || textLower.contains("margin") || textLower.contains("however") ||
                    textLower.contains("challenge") || textLower.contains("footloose")
            if (hasCritique) {
                green.add("Directive Honored: 'Critically Analyze' fulfilled by presenting limitations and alternative paradigms.")
            } else {
                yellow.add("Directive Incomplete: 'Critically Analyze' requires discussing limitations and modern counter-theories.")
            }
        }

        val percentile = when {
            totalScore >= rubric.topperBenchmarkScore -> "Top 1% (Topper Benchmark - Ranker Grade 🏆)"
            totalScore >= maxMarks * 0.60f -> "Top 15% (Solid Optional Grade)"
            else -> "Needs Theoretical Grounding (Average GS Band)"
        }

        val verdict = if (totalScore >= rubric.topperBenchmarkScore) {
            "Exceptional answer. Pristine balance of first-principles theory, diagrammatic accuracy, and Indian empirical proof."
        } else {
            "Answer exhibits good structural effort but lacks academic rigor and micro-diagram presence. Incorporate the red feedback flags."
        }

        val previousAttempts = attemptHistory.getOrPut(questionId) { mutableListOf() }
        val result = MainsEvaluationResult(
            questionId = questionId,
            scoreTheory = String.format("%.1f", scoreTheory).toFloat(),
            scoreEmpirical = String.format("%.1f", scoreEmpirical).toFloat(),
            scoreDiagram = String.format("%.1f", scoreDiagram).toFloat(),
            scorePhesg = String.format("%.1f", scorePhesg).toFloat(),
            scorePresentation = String.format("%.1f", scorePresentation).toFloat(),
            totalScore = totalScore,
            maxMarks = maxMarks,
            percentileBand = percentile,
            greenHighlights = green,
            yellowWarnings = yellow,
            redOmissions = red,
            examinerVerdict = verdict,
            attemptNumber = previousAttempts.size + 1,
            wordCount = wordCount,
            wordCountEnvelopeFeedback = envelopeFeedback,
            conceptualDensityScore = String.format("%.0f", conceptualDensity).toFloat(),
            coveredPropositions = coveredPropositions,
            missedPropositions = missedPropositions
        )
        previousAttempts.add(result)
        return result
    }
}
