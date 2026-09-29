package com.example.model

enum class QuestionFormat {
    PRELIMS_MCQ,
    MAINS_DESCRIPTIVE
}

enum class TestMode(val title: String) {
    SINGLE_CHAPTER_MCQ("Single Chapter MCQ"),
    CONCEPT_BUILDER("Concept Builder"),
    REVERSE_ENGINEER("Reverse Engineer"),
    TREND_HIGH_YIELD("Trend High Yield")
}

enum class OptionRole {
    ANSWER_CHOICE,
    ABSTAIN,
    NONE_OF_ABOVE,
    MORE_THAN_ONE,
    COMBINED_NONE_OR_MORE_THAN_ONE
}

data class Option(
    val id: String,
    val text: String,
    val role: OptionRole = OptionRole.ANSWER_CHOICE
)

data class DistractorDissection(
    val optionId: String,
    val trapType: String,
    val dissection: String
)

sealed interface ExamQuestion {
    val id: String
    val format: QuestionFormat
    val chapterCode: String
    val questionText: String
    val questionFormatType: String
    val imageUrl: String?
    val familyId: String?
    val familyStage: String?
}

/**
 * {
 *   "chapterCode": "UPSC-GEO-01",
 *   "questionText": "Which of the following best explains the formation of oxbow lakes?",
 *   "options": [
 *     {"id": "opt_A", "text": "They are formed by tectonic uplift."},
 *     {"id": "opt_B", "text": "They are formed by the cutoff of a river meander."},
 *     {"id": "opt_C", "text": "They are formed by glacial deposition."},
 *     {"id": "opt_D", "text": "They are formed by wind erosion."}
 *   ],
 *   "correctAnswerId": "opt_B",
 *   "correctExplanation": "Oxbow lakes form when a meander is cut off.",
 *   "distractorDissections": [
 *     {"optionId": "opt_A", "trapType": "Irrelevant Fact", "dissection": "Mountain building."},
 *     {"optionId": "opt_C", "trapType": "Factual Inversion", "dissection": "Moraines."},
 *     {"optionId": "opt_D", "trapType": "Reversed Causality", "dissection": "Yardangs."}
 *   ]
 * }
 */
data class MCQQuestion(
    override val id: String,
    override val format: QuestionFormat = QuestionFormat.PRELIMS_MCQ,
    override val chapterCode: String,
    override val questionText: String,
    override val questionFormatType: String = "Direct Fact",
    override val imageUrl: String? = null,
    val timeLimitSeconds: Int = 90,
    val options: List<Option>,
    val correctAnswerId: String,
    val correctExplanation: String,
    val distractorDissections: List<DistractorDissection>,
    override val familyId: String? = null,
    override val familyStage: String? = null
) : ExamQuestion

/**
 * {
 *   "id": "desc_1",
 *   "chapterCode": "UPSC-GEO-02",
 *   "questionText": "Critically analyze the impact of Western Disturbances.",
 *   "directive": "Critically Analyze",
 *   "wordLimit": 250,
 *   "structureBreakdown": [
 *     "Intro: Define Western Disturbances and their origin.",
 *     "Body Pillar 1: Impact on precipitation (rain and snow).",
 *     "Body Pillar 2: Impact on agriculture (Rabi crops).",
 *     "Conclusion: Summarize the overall economic and climatic significance."
 *   ],
 *   "modelAnswer": "Western Disturbances are extratropical storms...",
 *   "keyKeywords": ["Mediterranean", "Rabi crops", "precipitation", "extratropical"]
 * }
 */
data class DescriptiveQuestion(
    override val id: String,
    override val format: QuestionFormat = QuestionFormat.MAINS_DESCRIPTIVE,
    override val chapterCode: String,
    override val questionText: String,
    override val questionFormatType: String = "Direct Fact",
    override val imageUrl: String? = null,
    val directive: String,
    val wordLimit: Int,
    val structureBreakdown: List<String>,
    val modelAnswer: String,
    val keyKeywords: List<String>,
    val timeLimitSeconds: Int = 1800,
    override val familyId: String? = null,
    override val familyStage: String? = null
) : ExamQuestion

data class TestUiState(
    val currentTestMode: TestMode? = null,
    val currentQuestion: ExamQuestion? = null,
    val timeRemaining: Int = 0,
    val isBookmarked: Boolean = false,
    val selectedOptionId: String? = null,
    val pendingOptionId: String? = null,
    val crossedOutOptionIds: Set<String> = emptySet(),
    val selectedConfidence: String? = null,
    val userTypedAnswer: String = "",
    val questionNumber: Int = 1,
    val currentScore: ExactFraction = ExactFraction.ZERO,
    val totalQuestionsInSet: Int = 10,
    val isLoading: Boolean = false,
    val error: String? = null,
    val isTestFinished: Boolean = false,
    val detectedConfusionPair: com.example.repository.ConfusionDetectionResult? = null,
    val userAnswers: Map<String, String> = emptyMap(),
    val skippedQuestions: Set<String> = emptySet(),
    val allQuestions: List<ExamQuestion> = emptyList(),
    val marksLostReport: List<String> = emptyList()
)


enum class AttemptOutcome {
    CORRECT, INCORRECT, ABSTAINED, UNANSWERED
}







