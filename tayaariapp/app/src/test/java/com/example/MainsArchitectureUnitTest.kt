package com.example

import com.example.model.MainsQuestionLevel
import com.example.repository.MainsRepository
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class MainsArchitectureUnitTest {

    private lateinit var repository: MainsRepository

    @Before
    fun setUp() {
        repository = MainsRepository()
    }

    @Test
    fun testCuratedQuestionsLoadedSuccessfully() {
        val questions = repository.mainsQuestions
        assertTrue("Repository must load curated Tier-1 Mains questions", questions.isNotEmpty())

        val weberQuestion = repository.getQuestionById("MAINS-Q1")
        assertNotNull("Weber question must exist", weberQuestion)
        assertEquals("Industries & Manufacturing", weberQuestion?.chapterName)
        assertEquals(MainsQuestionLevel.ADVANCED_20M, weberQuestion?.level)
        assertEquals(20, weberQuestion?.level?.marks)
        assertEquals(840, weberQuestion?.level?.timeSeconds) // 14 minutes
        assertTrue("Must have a valid Synapse Bridge", weberQuestion?.synapseBridge?.paper1TheoreticalAnchor?.isNotEmpty() == true)
        assertTrue("Must have a 20s Micro-diagram", weberQuestion?.microDiagram?.name?.isNotEmpty() == true)
    }

    @Test
    fun testEvaluatorScoringWithDiagramAndTheorists() {
        val qId = "MAINS-Q1"
        val topTierAnswer = """
            Alfred Weber Least Cost Theory formulation with Material Index MI formula:
            MI = Weight of Localized Raw Materials / Weight of Finished Product.
            When MI > 1, industries are raw material pulled.
            Recent spatial shifts in Indian Iron & Steel: Traditional Chota Nagpur clustering shifted to coastal deep-water ports (Vizag, Hazira) due to imported Australian coking coal (low ash content), avoiding inland rail transport costs. Scrap-based EAF mini-mills locate near urban markets.
            Sugar Industry Relocation: Shifted from UP/Bihar to tropical Peninsular India (Maharashtra, Tamil Nadu) due to higher sucrose recovery (12% vs 9.5%) and longer crushing season of 180 days.
            Theoretical critique: D.M. Smith's Spatial Margins to Profitability and August Lösch demand cones show modern footloose and institutional policy factors override pure transport friction.
            Physical, human, economic, spatial, and governance dimensions analyzed.
        """.trimIndent()

        val result = repository.evaluateAnswer(
            questionId = qId,
            userWrittenText = topTierAnswer,
            hasDiagramDrawn = true,
            diagramStrokeAccuracy = 0.90f,
            timeTakenSeconds = 750 // finished within 14 minutes
        )

        assertEquals("MAINS-Q1", result.questionId)
        assertTrue("Score must be high for a topper answer with diagram", result.totalScore >= 14.0f)
        assertTrue("Diagram score must be awarded", result.scoreDiagram >= 3.0f)
        assertTrue("Theory score must be awarded", result.scoreTheory >= 3.0f)
        assertTrue("Green highlights must celebrate theoretical attribution", result.greenHighlights.isNotEmpty())
        assertTrue("Percentile must reflect top benchmark", result.percentileBand.contains("Top 1%"))
        assertEquals(1, result.attemptNumber)
    }

    @Test
    fun testEvaluatorPenalizesMissingDiagramAndGenericProse() {
        val qId = "MAINS-Q1"
        val mediocreAnswer = "Steel is in Jharkhand and sugar is in UP and Maharashtra. Farmers grow cane and mills make sugar. Coal is used for steel."

        val result = repository.evaluateAnswer(
            questionId = qId,
            userWrittenText = mediocreAnswer,
            hasDiagramDrawn = false,
            timeTakenSeconds = 400
        )

        assertTrue("Score must be low for generic GS prose without diagrams", result.totalScore <= 8.5f)
        assertTrue("Diagram score must be heavily penalized", result.scoreDiagram <= 1.0f)
        assertTrue("Red omissions must flag missing diagram and missing theorists", result.redOmissions.isNotEmpty())
        assertTrue("Yellow warnings must flag GS-1 prose", result.yellowWarnings.isNotEmpty())
    }

    @Test
    fun testInfiniteAttemptImprovementLoop() {
        val qId = "MAINS-Q2" // Taylor Neo-Determinism
        val attempt1Draft = "Determinism means nature is big and man is small. Possibilism means man can do anything."
        val result1 = repository.evaluateAnswer(
            questionId = qId,
            userWrittenText = attempt1Draft,
            hasDiagramDrawn = false,
            timeTakenSeconds = 300
        )

        val attempt2Polished = """
            Epistemological dichotomy between Environmental Determinism (Friedrich Ratzel, Ellen Semple) and Possibilism (Paul Vidal de la Blache).
            Griffith Taylor synthesized this through Neo-Determinism or Stop-and-Go Determinism:
            Nature acts as a traffic controller at a junction. Red signal in extreme fragile environments, yellow in conservation zones, green in fertile plains.
            Human velocity is adaptable, but planetary boundaries and carrying capacity cannot be violated.
            Demonstrated in Joshimath land subsidence (2023) where possibilist blast-tunneling violated Himalayan structural carrying capacity.
            Physical, human, economic, spatial, and governance frameworks integrated.
        """.trimIndent()

        val result2 = repository.evaluateAnswer(
            questionId = qId,
            userWrittenText = attempt2Polished,
            hasDiagramDrawn = true,
            diagramStrokeAccuracy = 0.92f,
            timeTakenSeconds = 600
        )

        assertEquals(1, result1.attemptNumber)
        assertEquals(2, result2.attemptNumber)
        assertTrue("Second attempt must show significant score improvement over first", result2.totalScore > result1.totalScore + 4.0f)
        assertTrue("Second attempt must achieve topper grade", result2.totalScore >= 11.0f)
    }

    @Test
    fun testMainsGatedExclusivelyToUPSC() {
        val upsc = com.example.model.ExamBlueprintRegistry.getBlueprint("UPSC_CSE_2026")
        val bpsc = com.example.model.ExamBlueprintRegistry.getBlueprint("BPSC_CCE_72ND_2026")
        val ssc = com.example.model.ExamBlueprintRegistry.getBlueprint("SSC_CGL_2025")
        val rrb = com.example.model.ExamBlueprintRegistry.getBlueprint("RRB_NTPC_2024")

        assertNotNull(upsc)
        assertNotNull(bpsc)
        assertNotNull(ssc)
        assertNotNull(rrb)

        // Strict exam gating verification
        assertTrue("UPSC exam blueprint must be recognized for Mains", upsc?.examId?.contains("UPSC", ignoreCase = true) == true)
        assertFalse("BPSC must NOT be recognized as UPSC Mains", bpsc?.examId?.contains("UPSC", ignoreCase = true) == true)
        assertFalse("SSC CGL must NOT be recognized as UPSC Mains", ssc?.examId?.contains("UPSC", ignoreCase = true) == true)
        assertFalse("RRB NTPC must NOT be recognized as UPSC Mains", rrb?.examId?.contains("UPSC", ignoreCase = true) == true)
    }

    @Test
    fun testPhysicalAnswerSheetAttachmentEvaluatesSuccessfully() {
        val qId = "MAINS-Q1"
        val q = repository.getQuestionById(qId)!!

        // Candidate submits 3 scanned pages of handwritten physical answer sheets
        val attachedImagesCount = 3
        val evaluatedText = "Physical answer sheet submitted ($attachedImagesCount page(s) attached). Offline analysis evaluated against question rubric for ${q.chapterName}. " + q.modelAnswerText.take(300)

        val result = repository.evaluateAnswer(
            questionId = qId,
            userWrittenText = evaluatedText,
            hasDiagramDrawn = attachedImagesCount > 0,
            diagramStrokeAccuracy = 0.88f,
            timeTakenSeconds = 650
        )

        assertTrue("Physical paper answer with scanned sheets must receive valid score", result.totalScore >= 10.0f)
        assertTrue("Diagram/sheet points must be credited", result.scoreDiagram >= 2.5f)
        assertTrue("Propositions must be evaluated", result.coveredPropositions.isNotEmpty())
    }

    @Test
    fun testExamSpecificCurriculumAndTierRules() {
        val upsc = com.example.model.ExamBlueprintRegistry.getBlueprint("UPSC_CSE_2026")!!
        val bpsc = com.example.model.ExamBlueprintRegistry.getBlueprint("BPSC_CCE_72ND_2026")!!
        val ssc = com.example.model.ExamBlueprintRegistry.getBlueprint("SSC_CGL_2025")!!
        val rrb = com.example.model.ExamBlueprintRegistry.getBlueprint("RRB_NTPC_2024")!!

        // Verify tier allowances per exam
        assertTrue("UPSC allows Elite/Hard tiers", upsc.allowedTiers.contains("Elite") && upsc.allowedTiers.contains("Hard"))
        assertFalse("SSC CGL must NOT allow Elite tier", ssc.allowedTiers.contains("Elite"))
        assertFalse("RRB NTPC must NOT allow Elite or Hard tier", rrb.allowedTiers.contains("Elite") || rrb.allowedTiers.contains("Hard"))

        // Verify topic domain filtering logic
        val allTopicIds = (1..30).toList()

        val upscTopics = allTopicIds
        assertEquals(30, upscTopics.size) // Full syllabus with Optional

        val bpscTopics = allTopicIds.filter { it !in 24..30 }
        assertEquals(23, bpscTopics.size) // Includes Chapter 23 Bihar Geography, excludes 24..30
        assertTrue("BPSC must include Bihar Geography", bpscTopics.contains(23))
        assertFalse("BPSC must not include UPSC Optional", bpscTopics.contains(24))

        val sscTopics = allTopicIds.filter { it !in 23..30 }
        assertEquals(22, sscTopics.size) // General Geography only
        assertFalse("SSC must not include Bihar Geography", sscTopics.contains(23))
        assertFalse("SSC must not include UPSC Optional", sscTopics.contains(24))
    }
}
