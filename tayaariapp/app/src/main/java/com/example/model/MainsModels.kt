package com.example.model

/**
 * Level of Mains Descriptive Question
 */
enum class MainsQuestionLevel(val label: String, val marks: Int, val wordLimit: Int, val timeSeconds: Int) {
    FOUNDATION_10M("Level 1: Foundation (10M)", 10, 150, 420), // 7 minutes
    APPLIED_15M("Level 2: Applied Synthesis (15M)", 15, 250, 660), // 11 minutes
    ADVANCED_20M("Level 3: Advanced Evaluative (20M)", 20, 300, 840) // 14 minutes
}

/**
 * ⚡ Synapse Bridge: Explicit Paper 1 <-> Paper 2 Interlinkage Matrix
 */
data class SynapseBridge(
    val paper1TheoreticalAnchor: String,
    val paper2IndianSpatialContext: String,
    val topperQuoteFormula: String,
    val empiricalDataEvidence: String
)

/**
 * 20-Second Micro-Diagram Vector Blueprint Data
 */
data class MicroDiagramBlueprint(
    val id: String,
    val name: String,
    val targetSeconds: Int = 20,
    val dimensions: String,
    val strokeInstructions: List<String>,
    val asciiRendering: String,
    val marksImpactBonus: String = "+2.0 to +2.5 Marks"
)

/**
 * The P-H-E-S-G 5-Dimensional Multiplier Framework
 */
enum class PhesgDimension(val code: String, val title: String, val triggerDescription: String) {
    PHYSICAL("P", "Physical & Ecological", "Geomorphology, lithology, micro-climate, water balance, eco-fragility"),
    HUMAN("H", "Human & Demographic", "Population density, tribal/customary rights, migration corridors, human capital"),
    ECONOMIC("E", "Economic & Technological", "Material Index (MI), value chain logistics, agglomeration, multipliers"),
    SPATIAL("S", "Spatial & Regional", "Core-periphery divide, friction of distance, nodal access, urban-rural continuum"),
    GOVERNANCE("G", "Governance & Policy", "Statutory planning, tribunals, PM Gati Shakti, Sendai framework, treaties")
}

/**
 * Atomic Minimal Meaning Proposition for Length-Invariant & Paraphrase-Invariant Evaluation
 */
data class AtomicProposition(
    val id: String,
    val title: String,
    val conceptClusters: List<List<String>>, // At least one term from each cluster must match
    val weightMarks: Float,
    val feedbackIfCovered: String,
    val feedbackIfMissed: String
)

/**
 * Evaluator Scoring Rubric Breakdown
 */
data class EvaluationRubric(
    val maxMarks: Int,
    val theoryWeight: Float = 0.20f,
    val empiricalWeight: Float = 0.20f,
    val diagramWeight: Float = 0.20f,
    val phesgWeight: Float = 0.20f,
    val presentationWeight: Float = 0.20f,
    val keyKeywords: List<String>,
    val mustCiteTheorists: List<String>,
    val topperBenchmarkScore: Float,
    val atomicPropositions: List<AtomicProposition> = emptyList()
)

/**
 * Complete UPSC Geography Mains Question Architecture
 */
data class MainsQuestion(
    val id: String,
    val chapterCode: String,
    val chapterName: String,
    val level: MainsQuestionLevel,
    val questionText: String,
    val directiveKeyword: String,
    val isPYQ: Boolean = false,
    val pyqYear: String? = null,
    val funAnalogy: String,
    val microStructureBlueprint: List<String>,
    val synapseBridge: SynapseBridge,
    val microDiagram: MicroDiagramBlueprint,
    val modelAnswerText: String,
    val rubric: EvaluationRubric
)

/**
 * Result returned by the Chief Evaluator Engine for an Aspirant's Answer
 */
data class MainsEvaluationResult(
    val questionId: String,
    val scoreTheory: Float,
    val scoreEmpirical: Float,
    val scoreDiagram: Float,
    val scorePhesg: Float,
    val scorePresentation: Float,
    val totalScore: Float,
    val maxMarks: Float,
    val percentileBand: String, // e.g. "Top 1% (Topper Benchmark)", "Top 10%", "Needs Grounding"
    val greenHighlights: List<String>,
    val yellowWarnings: List<String>,
    val redOmissions: List<String>,
    val examinerVerdict: String,
    val attemptNumber: Int = 1,
    val wordCount: Int = 0,
    val wordCountEnvelopeFeedback: String = "",
    val conceptualDensityScore: Float = 0f,
    val coveredPropositions: List<String> = emptyList(),
    val missedPropositions: List<String> = emptyList()
)
