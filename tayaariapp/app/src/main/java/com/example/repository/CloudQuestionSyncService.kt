package com.example.repository

import android.content.Context
import android.util.Log
import androidx.room.withTransaction
import com.example.database.AppDatabase
import com.example.database.Topic
import com.example.model.ExamBlueprint
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion
import com.example.model.Option
import com.example.model.OptionRole
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.InputStreamReader
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.TimeUnit

/**
 * CloudQuestionSyncService (Approach B: 100% On-Demand Live Cloud Fetch)
 *
 * Guarantees:
 * 1. ZERO questions are stored in the local SQLite Room database.
 * 2. Questions are fetched strictly on-demand over HTTP directly into RAM for active practice.
 * 3. Offline access (Airplane Mode) fails immediately as questions live exclusively on the Cloud CDN.
 */
object CloudQuestionSyncService {

    private const val TAG = "CloudQuestionSync"

    val isSyncing = MutableStateFlow(false)
    val syncStatusMessage = MutableStateFlow("Pure Online Stream (v23.0 • 3,942 MCQs on Cloud CDN • Zero Local Questions)")

    private val syncMutex = Mutex()

    // Manifest Endpoints (Topics catalog & counts)
    private const val CDN_MANIFEST_URL = "https://cdn.jsdelivr.net/gh/CODE-ops-stack/my-new-ready-app@main/topics/manifest.json"
    private const val RAW_MANIFEST_URL = "https://raw.githubusercontent.com/CODE-ops-stack/my-new-ready-app/main/topics/manifest.json"

    // Sliced Topic Endpoints (150 KB - 1 MB per topic)
    private const val CDN_TOPIC_URL_TEMPLATE = "https://cdn.jsdelivr.net/gh/CODE-ops-stack/my-new-ready-app@main/topics/topic_%d.json"
    private const val RAW_TOPIC_URL_TEMPLATE = "https://raw.githubusercontent.com/CODE-ops-stack/my-new-ready-app/main/topics/topic_%d.json"

    // Global Fallback Endpoints
    private const val CDN_QUESTIONS_URL = "https://cdn.jsdelivr.net/gh/CODE-ops-stack/my-new-ready-app@main/questions.json"
    private const val RAW_QUESTIONS_URL = "https://raw.githubusercontent.com/CODE-ops-stack/my-new-ready-app/main/questions.json"

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    data class ManifestTopic(
        val topicId: Int,
        val topicName: String,
        val count: Int,
        val file: String
    )

    data class CloudManifest(
        val version: Int,
        val totalQuestions: Int,
        val totalTopics: Int,
        val topics: List<ManifestTopic>
    )

    sealed class SyncResult {
        data class Success(val importedCount: Int, val version: Int) : SyncResult()
        data class AlreadyUpToDate(val version: Int, val count: Int) : SyncResult()
        data class Failure(val message: String, val usingCache: Boolean) : SyncResult()
    }

    private val topicCounts = ConcurrentHashMap<Int, Int>()

    private val defaultTopicCounts = mapOf(
        1 to 150, 2 to 143, 3 to 83, 4 to 328, 5 to 295, 6 to 155, 7 to 312, 8 to 134,
        9 to 139, 10 to 403, 11 to 410, 12 to 145, 13 to 159, 14 to 126, 15 to 327, 16 to 115,
        17 to 250, 18 to 122, 19 to 153, 20 to 197, 21 to 103, 22 to 120, 23 to 62,
        24 to 60, 25 to 60, 26 to 60, 27 to 60, 28 to 60, 29 to 60, 30 to 60
    )

    val topicNameToIdMap = mapOf(
        "Universe, Solar System & Motions of the Earth" to 1,
        "🌌 Universe, Solar System & Motions of the Earth" to 1,
        "Globe, Latitudes, Longitudes & Time" to 2,
        "🌐 Globe, Latitudes, Longitudes & Time" to 2,
        "Maps, Scale, Projections & GIS" to 3,
        "🗺️ Maps, Scale, Projections & GIS" to 3,
        "Earth's Interior, Rocks & Plate Tectonics" to 4,
        "🌋 Earth's Interior, Rocks & Plate Tectonics" to 4,
        "Geomorphic Processes & Landforms" to 5,
        "⛰️ Geomorphic Processes & Landforms" to 5,
        "Atmosphere, Winds & Climate Systems" to 6,
        "🌪️ Atmosphere, Winds & Climate Systems" to 6,
        "Oceanography" to 7,
        "🌊 Oceanography" to 7,
        "Biogeography, Ecosystems & Biodiversity" to 8,
        "🌿 Biogeography, Ecosystems & Biodiversity" to 8,
        "India: Location, Size & Neighbours" to 9,
        "🇮🇳 India: Location, Size & Neighbours" to 9,
        "Physiography of India" to 10,
        "🏔️ Physiography of India" to 10,
        "Drainage System of India" to 11,
        "🏞️ Drainage System of India" to 11,
        "Indian Climate & Monsoon" to 12,
        "🌧️ Indian Climate & Monsoon" to 12,
        "Soils & Natural Vegetation of India" to 13,
        "🌱 Soils & Natural Vegetation of India" to 13,
        "Wildlife, Protected Areas & Conservation" to 14,
        "🐅 Wildlife, Protected Areas & Conservation" to 14,
        "Agriculture" to 15,
        "🌾 Agriculture" to 15,
        "Water Resources, Irrigation & Dams" to 16,
        "💧 Water Resources, Irrigation & Dams" to 16,
        "Minerals & Energy Resources" to 17,
        "⛏️ Minerals & Energy Resources" to 17,
        "Industries" to 18,
        "🏭 Industries" to 18,
        "Transport, Communication & Trade" to 19,
        "🚆 Transport, Communication & Trade" to 19,
        "Population, Migration & Settlements" to 20,
        "👥 Population, Migration & Settlements" to 20,
        "Human Development & Economic Activities" to 21,
        "📈 Human Development & Economic Activities" to 21,
        "World Regional Geography" to 22,
        "🗺️ World Regional Geography" to 22,
        "Bihar Geography" to 23,
        "📍 Bihar Geography" to 23,
        "Bihar Geography: Physiography, Rivers & Resources" to 23,
        "📍 Bihar Geography: Physiography, Rivers & Resources" to 23,
        "State PCS Bihar Special Drills" to 23,
        "Perspectives in Human Geography (Geographical Thought)" to 24,
        "🧠 Perspectives in Human Geography (Geographical Thought)" to 24,
        "Models, Theories & Laws in Human Geography" to 25,
        "📐 Models, Theories & Laws in Human Geography" to 25,
        "Regional Planning & Regionalisation" to 26,
        "🗺️ Regional Planning & Regionalisation" to 26,
        "Cultural Setting of India" to 27,
        "👥 Cultural Setting of India" to 27,
        "Political Aspects of Indian Geography" to 28,
        "🏛️ Political Aspects of Indian Geography" to 28,
        "Advanced Geomorphology & Landscape Evolution" to 29,
        "⛰️ Advanced Geomorphology & Landscape Evolution" to 29,
        "Advanced Ocean Topography & Climatology Models" to 30,
        "🌊 Advanced Ocean Topography & Climatology Models" to 30
    )

    fun getTopicCount(topicId: Int): Int {
        return topicCounts[topicId] ?: defaultTopicCounts[topicId] ?: 0
    }

    fun getTopicIdByName(topicName: String): Int {
        // Exact match
        topicNameToIdMap[topicName]?.let { return it }
        // Prefix or partial match
        for ((name, id) in topicNameToIdMap) {
            if (topicName.contains(name, ignoreCase = true) || name.contains(topicName, ignoreCase = true)) {
                return id
            }
        }
        return 0
    }

    fun getModuleForTopic(topicId: Int): String {
        return when (topicId) {
            in 1..5 -> "📘 Stage 1: Foundation Physical Geography"
            in 6..8 -> "🌪️ Stage 2: Climatology, Oceanography & Biomes"
            in 9..14 -> "🇮🇳 Stage 3: Indian Physical & Environmental Geography"
            in 15..20 -> "🌾 Stage 4: Indian Economic, Resource & Human Geography"
            in 21..22 -> "🌐 Stage 5: Global Regional Geography & Trade"
            23 -> "📍 Stage 5: State PCS Special Drills (Bihar Focus)"
            in 24..30 -> "🎓 Stage 6: UPSC Geography Optional & Theoretical Mastery"
            else -> "📘 Stage 1: Foundation Physical Geography"
        }
    }

    /**
     * Boot-time catalog sync:
     * Downloads the 3 KB manifest to populate the topic catalog and live counts.
     * Enforces that ZERO questions are saved in SQLite Room database on disk.
     */
    suspend fun syncWithCloud(context: Context, force: Boolean = false): SyncResult = withContext(Dispatchers.IO) {
        syncMutex.withLock {
            val database = AppDatabase.getDatabase(context)
            val dao = database.appDao()

            // GUARANTEE: Clear all questions from SQLite so local storage has 0 rows
            dao.clearAllQuestions()

            isSyncing.value = true
            syncStatusMessage.value = "Streaming Cloud Database..."

            val manifest = fetchManifest()
            val topicsToInsert = mutableListOf<Topic>()

            if (manifest != null) {
                for (item in manifest.topics) {
                    topicCounts[item.topicId] = item.count
                    val module = getModuleForTopic(item.topicId)
                    topicsToInsert.add(Topic(item.topicId, item.topicName, "Cloud-CDN", module))
                }
            } else {
                for ((id, count) in defaultTopicCounts) {
                    topicCounts[id] = count
                }
                for ((name, id) in topicNameToIdMap) {
                    val module = getModuleForTopic(id)
                    topicsToInsert.add(Topic(id, name, "Cloud-CDN", module))
                }
            }

            database.withTransaction {
                dao.deleteAllTopics()
                dao.insertTopics(topicsToInsert)
                // Re-verify questions table is 100% empty
                dao.clearAllQuestions()
            }

            val totalOnlineQuestions = manifest?.totalQuestions ?: 4851
            val version = manifest?.version ?: 24
            val successMsg = "Pure Online Stream (v$version • $totalOnlineQuestions MCQs) • Zero Local Asset"
            syncStatusMessage.value = successMsg
            isSyncing.value = false

            Log.i(TAG, "Initialized catalog with ${topicsToInsert.size} topics. Local question table: 0 rows.")
            SyncResult.Success(totalOnlineQuestions, version)
        }
    }

    /**
     * Pure On-Demand Network Fetch:
     * Connects live to Cloud CDN to fetch questions directly into RAM for active practice.
     * Throws an IOException if offline (e.g. Airplane Mode).
     * Never writes questions to SQLite database.
     */
    suspend fun fetchQuestionsOnline(
        topicName: String,
        profile: ExamBlueprint,
        limit: Int = 20,
        format: String = ""
    ): List<ExamQuestion> = withContext(Dispatchers.IO) {
        val topicId = getTopicIdByName(topicName)
        val urls = if (topicId in 1..30) {
            listOf(
                String.format(RAW_TOPIC_URL_TEMPLATE, topicId),
                String.format(CDN_TOPIC_URL_TEMPLATE, topicId)
            )
        } else {
            listOf(RAW_QUESTIONS_URL, CDN_QUESTIONS_URL)
        }

        var jsonReader: InputStreamReader? = null
        var lastException: Exception? = null

        val cacheBuster = System.currentTimeMillis() / 60000 // fresh every minute

        for (baseUrl in urls) {
            try {
                val url = "$baseUrl?cb=$cacheBuster"
                val req = Request.Builder()
                    .url(url)
                    .header("Cache-Control", "no-cache, no-store, must-revalidate")
                    .header("Pragma", "no-cache")
                    .build()
                val resp = client.newCall(req).execute()
                if (resp.isSuccessful) {
                    val stream = resp.body?.byteStream()
                    if (stream != null) {
                        jsonReader = InputStreamReader(stream, "UTF-8")
                        break
                    }
                }
            } catch (e: Exception) {
                lastException = e
                Log.w(TAG, "Failed to fetch from $baseUrl: ${e.message}")
            }
        }

        if (jsonReader == null) {
            throw java.io.IOException(
                "No Internet Connection detected. Questions are served 100% on-demand from the online database. Please connect to Wi-Fi or mobile data to practice.",
                lastException
            )
        }

        val gson = JsonQuestionImporter.createSafeGson()
        val type = object : TypeToken<List<JsonQuestionImporter.GeneratedQuestion>>() {}.type
        val generatedList: List<JsonQuestionImporter.GeneratedQuestion> = gson.fromJson(jsonReader, type)
        jsonReader.close()

        val rawTiers = profile.allowedTiers
        val combinedTiers = if (rawTiers.contains("Advanced") || rawTiers.contains("Elite")) (rawTiers + "Hard").distinct() else rawTiers
        val effectiveTiers = if (combinedTiers.isEmpty()) listOf("Basic", "Medium", "Hard") else combinedTiers

        val filteredByTier = generatedList.filter { q ->
            val qTier = q.tier ?: "Medium"
            effectiveTiers.contains(qTier) || effectiveTiers.contains("All")
        }

        val pool = if (filteredByTier.isNotEmpty()) filteredByTier else generatedList

        val filteredByFormat = if (format.isNotBlank() && format != "Smart Practice") {
            if (format.startsWith("Trap Training:")) {
                val targetTrap = format.substringAfter("Trap Training:").trim()
                pool.filter { q ->
                    q.distractorDissections?.any { it.trapType.equals(targetTrap, ignoreCase = true) } == true
                }
            } else {
                pool.filter { q ->
                    q.format?.contains(format, ignoreCase = true) == true
                }
            }
        } else {
            emptyList()
        }

        val candidatesByExam = if (profile.examId.startsWith("SSC") || profile.examId.startsWith("RRB")) {
            val sscPool = pool.filter { q -> q.id.startsWith("ssc_pyq") || q.examTarget == "SSC_CGL" }
            if (sscPool.isNotEmpty()) sscPool else pool
        } else if (profile.examId.startsWith("UPSC")) {
            val upscPool = pool.filter { q -> !q.id.startsWith("ssc_pyq") }
            if (upscPool.isNotEmpty()) upscPool else pool
        } else {
            pool
        }

        val finalCandidates = if (filteredByFormat.isNotEmpty()) filteredByFormat else candidatesByExam
        
        // Strict Pedagogical Progression:
        // Basic/Foundation (tier 1) -> Medium/Analytical (tier 2) -> Hard/UPSC Ranker (tier 3).
        // For full simulation (Paper Twin), questions are randomized to simulate exam conditions.
        val orderedCandidates = if (format == "Paper Twin") {
            finalCandidates.shuffled()
        } else {
            finalCandidates.sortedWith(compareBy { q ->
                when (q.tier) {
                    "Basic" -> 1
                    "Medium" -> 2
                    "Hard" -> 3
                    else -> 4
                }
            })
        }
        val finalSelection = if (limit > 0 && limit < orderedCandidates.size) {
            orderedCandidates.take(limit)
        } else {
            orderedCandidates
        }
        finalSelection.map { it.toMCQQuestion(profile) }
    }

    private fun JsonQuestionImporter.GeneratedQuestion.toMCQQuestion(profile: ExamBlueprint): MCQQuestion {
        val parsedOptions = options.map { (key, value) ->
            Option(id = key, text = value, role = OptionRole.ANSWER_CHOICE)
        }.toMutableList()

        if (profile.synthesizeAbstainOption && parsedOptions.size == profile.optionCount - 1) {
            parsedOptions.add(
                Option(
                    id = "opt_abstain",
                    text = profile.abstainOptionLabel,
                    role = OptionRole.ABSTAIN
                )
            )
        }

        val parsedDistractors = distractorDissections?.map {
            com.example.model.DistractorDissection(
                optionId = it.optionId,
                trapType = it.trapType,
                dissection = it.dissection
            )
        } ?: emptyList()

        return MCQQuestion(
            id = id,
            chapterCode = provenance?.sourceFile ?: "Cloud-Repository",
            questionText = stem,
            questionFormatType = format ?: "Direct Fact",
            imageUrl = imageUrl,
            timeLimitSeconds = 90,
            options = parsedOptions,
            correctAnswerId = correctAnswer,
            correctExplanation = explanation,
            distractorDissections = parsedDistractors,
            familyId = provenance?.knowledgeNodeId,
            familyStage = provenance?.intentType
        )
    }

    private fun fetchManifest(): CloudManifest? {
        val urls = listOf(RAW_MANIFEST_URL, CDN_MANIFEST_URL)
        val cacheBuster = System.currentTimeMillis() / 60000
        for (baseUrl in urls) {
            try {
                val url = "$baseUrl?cb=$cacheBuster"
                val req = Request.Builder()
                    .url(url)
                    .header("Cache-Control", "no-cache, no-store, must-revalidate")
                    .header("Pragma", "no-cache")
                    .build()
                client.newCall(req).execute().use { resp ->
                    if (resp.isSuccessful) {
                        val body = resp.body?.string()
                        if (!body.isNullOrBlank()) {
                            return Gson().fromJson(body, CloudManifest::class.java)
                        }
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Manifest fetch failed for $baseUrl: ${e.message}")
            }
        }
        return null
    }
}
