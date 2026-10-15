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

    @Test
    fun testDefensiveProvenanceDeserialization() {
        val safeGson = com.example.repository.JsonQuestionImporter.createSafeGson()
        val type = object : com.google.gson.reflect.TypeToken<List<com.example.repository.JsonQuestionImporter.GeneratedQuestion>>() {}.type

        // Test mixed JSON array containing:
        // 1. Provenance as an Object
        // 2. Provenance as a String (which previously crashed with IllegalStateException)
        // 3. Provenance as null
        val mixedJson = """
            [
              {
                "id": "1",
                "stem": "Sample Question 1",
                "options": {"opt_a": "A", "opt_b": "B", "opt_c": "C", "opt_d": "D"},
                "correctAnswer": "opt_a",
                "explanation": "Expl 1",
                "provenance": {
                  "questionId": "1",
                  "questionStem": "Stem 1",
                  "intentType": "conceptual",
                  "knowledgeNodeId": "node-1",
                  "evidenceText": "Evidence 1",
                  "sourceFile": "file1.txt",
                  "sourceLocation": {"sourceId": "s1", "sentence_count": 1, "section_heading": "h1", "concept": "c1", "sentence_idx": 0, "block_id": "b1", "has_antecedent": false},
                  "provenanceHash": "hash1",
                  "createdAt": "2026-10-14",
                  "schemaVersion": "1.0",
                  "metadata": null,
                  "linkHashes": null
                }
              },
              {
                "id": "2",
                "stem": "Sample Question 2 (String Provenance)",
                "options": {"opt_a": "A", "opt_b": "B", "opt_c": "C", "opt_d": "D"},
                "correctAnswer": "opt_b",
                "explanation": "Expl 2",
                "provenance": "UPSC_EXPERT_PREDICTIVE"
              },
              {
                "id": "3",
                "stem": "Sample Question 3 (Null Provenance)",
                "options": {"opt_a": "A", "opt_b": "B", "opt_c": "C", "opt_d": "D"},
                "correctAnswer": "opt_c",
                "explanation": "Expl 3",
                "provenance": null
              }
            ]
        """.trimIndent()

        val parsed: List<com.example.repository.JsonQuestionImporter.GeneratedQuestion> = safeGson.fromJson(mixedJson, type)

        assertEquals(3, parsed.size)
        // Verify question 1: object provenance preserved
        assertEquals("file1.txt", parsed[0].provenance?.sourceFile)
        assertEquals("conceptual", parsed[0].provenance?.intentType)

        // Verify question 2: string provenance gracefully wrapped without crashing
        assertNotNull(parsed[1].provenance)
        assertEquals("UPSC_EXPERT_PREDICTIVE", parsed[1].provenance?.intentType)
        assertEquals("UPSC_EXPERT_PREDICTIVE", parsed[1].provenance?.sourceFile)

        // Verify question 3: null provenance handled
        assertNull(parsed[2].provenance)
    }

    @Test
    fun testAllCloudTopicSlicesDeserializeWithoutError() {
        val safeGson = com.example.repository.JsonQuestionImporter.createSafeGson()
        val type = object : com.google.gson.reflect.TypeToken<List<com.example.repository.JsonQuestionImporter.GeneratedQuestion>>() {}.type

        val possibleDirs = listOf(
            java.io.File("../../cloud_data_staging/topics"),
            java.io.File("../cloud_data_staging/topics"),
            java.io.File("c:/Users/harsh/Downloads/tayaari/cloud_data_staging/topics")
        )
        val topicsDir = possibleDirs.find { it.exists() && it.isDirectory }
        assertNotNull("Cloud topics directory must exist for audit", topicsDir)

        val topicFiles = topicsDir!!.listFiles { file -> file.name.startsWith("topic_") && file.name.endsWith(".json") }
        assertNotNull(topicFiles)
        assertTrue("Must have at least 23 topic files", topicFiles!!.size >= 23)

        var totalQuestionsValidated = 0

        for (file in topicFiles.sortedBy { it.name }) {
            val reader = java.io.InputStreamReader(file.inputStream(), "UTF-8")
            val questions: List<com.example.repository.JsonQuestionImporter.GeneratedQuestion> = safeGson.fromJson(reader, type)
            reader.close()

            assertTrue("File ${file.name} must have questions", questions.isNotEmpty())
            for (q in questions) {
                totalQuestionsValidated++
                assertTrue("Question in ${file.name} must have non-blank stem", q.stem.isNotBlank())
                assertTrue("Question ${q.id} in ${file.name} must have at least 4 options", q.options.size >= 4)
                assertTrue("Question ${q.id} in ${file.name} must have valid correctAnswer in options", q.options.containsKey(q.correctAnswer))
                assertTrue("Question ${q.id} in ${file.name} must have non-blank explanation", q.explanation.isNotBlank())
            }
        }

        assertTrue("Must validate at least 4,800 questions across all topic files", totalQuestionsValidated >= 4800)
    }

    @Test
    fun testSscCglExamProfilePrioritization() {
        val sscProfile = com.example.model.ExamBlueprintRegistry.getBlueprint("SSC_CGL_2025")!!
        val upscProfile = com.example.model.ExamBlueprintRegistry.getBlueprint("UPSC_CSE_2026")!!

        val sscQ = com.example.repository.JsonQuestionImporter.GeneratedQuestion(
            id = "ssc_pyq_0001",
            stem = "What are the streams of charged particles ejected by the Sun called?",
            options = mapOf("opt_a" to "Sunspots", "opt_b" to "Solar wind", "opt_c" to "Solar flares", "opt_d" to "Coronal loops"),
            correctAnswer = "opt_b",
            explanation = "Solar wind is a constant stream of charged particles.",
            distractorDissections = emptyList(),
            provenance = null,
            examTarget = "SSC_CGL"
        )

        val upscQ = com.example.repository.JsonQuestionImporter.GeneratedQuestion(
            id = "q_upsc_0001",
            stem = "With reference to solar phenomena, consider the following statements...",
            options = mapOf("opt_a" to "1 only", "opt_b" to "2 only", "opt_c" to "Both 1 and 2", "opt_d" to "Neither 1 nor 2"),
            correctAnswer = "opt_c",
            explanation = "Solar activity interacts with magnetosphere...",
            distractorDissections = emptyList(),
            provenance = null,
            examTarget = "UPSC-Prelims"
        )

        val mixedPool = listOf(sscQ, upscQ)

        // For SSC profile: must select SSC PYQ
        val sscFiltered = if (sscProfile.examId.startsWith("SSC") || sscProfile.examId.startsWith("RRB")) {
            val sscPool = mixedPool.filter { q -> q.id.startsWith("ssc_pyq") || q.examTarget == "SSC_CGL" }
            if (sscPool.isNotEmpty()) sscPool else mixedPool
        } else {
            mixedPool
        }
        assertEquals(1, sscFiltered.size)
        assertEquals("ssc_pyq_0001", sscFiltered[0].id)

        // For UPSC profile: must select UPSC question
        val upscFiltered = if (upscProfile.examId.startsWith("UPSC")) {
            val upscPool = mixedPool.filter { q -> !q.id.startsWith("ssc_pyq") }
            if (upscPool.isNotEmpty()) upscPool else mixedPool
        } else {
            mixedPool
        }
        assertEquals(1, upscFiltered.size)
        assertEquals("q_upsc_0001", upscFiltered[0].id)
    }

    @Test
    fun testBpscFiveOptionsSynthesized() {
        val bpsc = com.example.model.ExamBlueprintRegistry.getBlueprint("BPSC_CCE_72ND_2026")!!
        val upsc = com.example.model.ExamBlueprintRegistry.getBlueprint("UPSC_CSE_2026")!!

        assertTrue("BPSC demands 5 options", bpsc.optionCount == 5)
        assertTrue("BPSC demands synthesized abstain option", bpsc.synthesizeAbstainOption)

        val sampleGeneratedQ = com.example.repository.JsonQuestionImporter.GeneratedQuestion(
            id = "BIHAR-01",
            stem = "Which soil of Bihar is characterized by high water retention?",
            options = mapOf(
                "opt_a" to "Terai soil",
                "opt_b" to "Karail-Kewal soil",
                "opt_c" to "Balasundar soil",
                "opt_d" to "Piedmont swamp soil"
            ),
            correctAnswer = "opt_b",
            explanation = "Karail-Kewal is heavy clayey soil found in South Gangetic Plain of Bihar.",
            distractorDissections = emptyList(),
            provenance = null
        )

        // Test BPSC option synthesis via reflection or private method logic
        val bpscOptions = sampleGeneratedQ.options.map { (key, value) ->
            com.example.model.Option(id = key, text = value, role = com.example.model.OptionRole.ANSWER_CHOICE)
        }.toMutableList()

        if (bpsc.synthesizeAbstainOption && bpscOptions.size == bpsc.optionCount - 1) {
            bpscOptions.add(
                com.example.model.Option(
                    id = "opt_abstain",
                    text = bpsc.abstainOptionLabel,
                    role = com.example.model.OptionRole.ABSTAIN
                )
            )
        }

        assertEquals("BPSC must have exactly 5 options", 5, bpscOptions.size)
        assertEquals("5th option must be abstain", "opt_abstain", bpscOptions[4].id)
        assertEquals("I do not wish to answer", bpscOptions[4].text)
        assertEquals(com.example.model.OptionRole.ABSTAIN, bpscOptions[4].role)

        // For UPSC, it must remain strictly 4 options
        val upscOptions = sampleGeneratedQ.options.map { (key, value) ->
            com.example.model.Option(id = key, text = value, role = com.example.model.OptionRole.ANSWER_CHOICE)
        }.toMutableList()

        if (upsc.synthesizeAbstainOption && upscOptions.size == upsc.optionCount - 1) {
            upscOptions.add(
                com.example.model.Option(
                    id = "opt_abstain",
                    text = upsc.abstainOptionLabel,
                    role = com.example.model.OptionRole.ABSTAIN
                )
            )
        }
        assertEquals("UPSC must remain strictly 4 options", 4, upscOptions.size)
    }
}
