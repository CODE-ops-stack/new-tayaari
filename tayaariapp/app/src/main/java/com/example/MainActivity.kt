package com.example

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.example.ui.theme.MyApplicationTheme
import androidx.navigation.compose.rememberNavController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.example.ui.screens.TopicSelectionScreen
import com.example.ui.screens.PracticeScreen
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.viewmodel.PracticeViewModel
import com.example.viewmodel.TopicSelectionViewModel
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.database.AppDatabase
import com.example.repository.LocalRepository
import com.example.repository.JsonQuestionImporter
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.ViewModel
import com.example.ui.screens.InsightsDashboardScreen
import com.example.ui.screens.TrapDashboardScreen
import com.example.ui.screens.BookmarksScreen
import com.example.ui.screens.RevisionDashboardScreen
import com.example.viewmodel.BookmarksViewModel
import com.example.repository.UserPreferencesRepository
import com.example.ui.screens.OnboardingScreen
import com.example.viewmodel.MainViewModel
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val db = AppDatabase.getDatabase(applicationContext)
        val localRepository = LocalRepository(
            bookmarkDao = db.bookmarkDao(),
            trapAnalyticsDao = db.trapAnalyticsDao(),
            mistakeReplayDao = db.mistakeReplayDao(),
            appDao = db.appDao(),
            revisionDao = db.revisionDao(),
            questionAttemptDao = db.questionAttemptDao(),
            analyticsDao = db.analyticsDao(),
            confusionEventDao = db.confusionEventDao()
        )
        val userPrefsRepo = UserPreferencesRepository(applicationContext)

        enableEdgeToEdge()
        
        // Import questions from JSON if database is empty (run on IO thread)
        CoroutineScope(Dispatchers.IO).launch {
            val questionCount = db.appDao().getQuestionCount()
            if (questionCount == 0) {
                Log.d("MainActivity", "Database empty, importing questions from JSON...")
                val result = JsonQuestionImporter.importFromJson(this@MainActivity)
                Log.d("MainActivity", "Import result: $result")
            } else {
                Log.d("MainActivity", "Database already has $questionCount questions, skipping import")
            }
        }
        
        val practiceFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return PracticeViewModel(localRepository) as T
            }
        }

        val mainFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return MainViewModel(userPrefsRepo) as T
            }
        }

        
        val topicFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return TopicSelectionViewModel(com.example.repository.NextBestActionEngine(localRepository), localRepository, userPrefsRepo) as T
            }
        }
        
        val bookmarksFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return BookmarksViewModel(localRepository) as T
            }
        }
        
        val paperTwinFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return com.example.viewmodel.PaperTwinViewModel(localRepository) as T
            }
        }
        
        val mistakeReplayFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return com.example.viewmodel.MistakeReplayViewModel(localRepository) as T
            }
        }

        val readinessFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return com.example.viewmodel.ReadinessViewModel(localRepository) as T
            }
        }
        
        setContent {
            MyApplicationTheme {
                val mainViewModel: MainViewModel = viewModel(factory = mainFactory)
                val isLoading by mainViewModel.isLoading.collectAsStateWithLifecycle()
                val selectedProfile by mainViewModel.selectedProfile.collectAsStateWithLifecycle()

                val showSplash = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf(true) }

                androidx.compose.runtime.LaunchedEffect(Unit) {
                    kotlinx.coroutines.delay(2000)
                    showSplash.value = false
                }
                
                if (showSplash.value || isLoading) {
                    com.example.ui.screens.SplashScreen()
                } else if (selectedProfile == null) {
                    OnboardingScreen(
                        onProfileSelected = { profile ->
                            mainViewModel.saveProfile(profile)
                        }
                    )
                } else {
                    val navController = rememberNavController()
                    val viewModel: PracticeViewModel = viewModel(factory = practiceFactory)
                    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
                    val trapAnalytics by viewModel.trapAnalytics.collectAsStateWithLifecycle(initialValue = emptyList())
                    

                    val topicViewModel: TopicSelectionViewModel = viewModel(factory = topicFactory)
                    val topics by topicViewModel.topics.collectAsStateWithLifecycle()
                    val nextAction by topicViewModel.nextAction.collectAsStateWithLifecycle()
                    
                    NavHost(navController = navController, startDestination = "topics") {
                        composable("topics") {
                            TopicSelectionScreen(
                                topics = topics,
                                nextAction = nextAction,
                                profile = selectedProfile,
                                                                  onTopicSelected = { topicName, tier, format ->
                                      topicViewModel.onPracticeIntent(topicName, tier, format) { t, r, f ->
                                          navController.navigate("practice///")
                                      }
                                  },
                                onBookmarksClick = {
                                    navController.navigate("bookmarks")
                                },
                                onAnalyticsClick = {
                                    navController.navigate("dashboard")
                                },
                                onRevisionClick = {
                                    navController.navigate("revision")
                                },
                                onPaperTwinClick = {
                                    navController.navigate("papertwin")
                                },
                                onReadinessClick = {
                                    navController.navigate("readiness")
                                },
                                onChangeExam = {
                                    mainViewModel.clearProfile()
                                }
                            )
                        }
                        

                composable("insights") {
                    InsightsDashboardScreen(
                        localRepository = localRepository,
                        profile = selectedProfile,
                        onStartMistakeReplay = { navController.navigate("mistake_replay") },
                        onBack = { navController.popBackStack() }
                    )
                }
                composable("readiness") {
                    val readinessViewModel: com.example.viewmodel.ReadinessViewModel = viewModel(factory = readinessFactory)
                    com.example.ui.screens.ReadinessEvidenceScreen(
                        viewModel = readinessViewModel,
                        onBack = { navController.popBackStack() }
                    )
                }
                        composable("bookmarks") {
                            val bookmarksViewModel: BookmarksViewModel = viewModel(factory = bookmarksFactory)
                            BookmarksScreen(
                                viewModel = bookmarksViewModel,
                                onBack = { navController.popBackStack() }
                            )
                        }
                        composable("practice/{topicName}/{tier}/{format}") { backStackEntry ->
                            val topicName = android.net.Uri.decode(backStackEntry.arguments?.getString("topicName") ?: "")
                            val tier = android.net.Uri.decode(backStackEntry.arguments?.getString("tier") ?: "")
                            val format = android.net.Uri.decode(backStackEntry.arguments?.getString("format") ?: "")
                            
                            androidx.compose.runtime.LaunchedEffect(topicName, tier, format, selectedProfile) {
                                if (selectedProfile != null) {
                                    viewModel.startPractice(topicName, selectedProfile!!, tier, format)
                                }
                            }
                            
                            PracticeScreen(
                                topicName = topicName,
                                tier = tier,
                                format = format,
                                uiState = uiState,
                                onOptionSelected = viewModel::onOptionPending,
                                onOptionCrossOut = viewModel::toggleOptionCrossedOut,
                                onSubmitAnswerWithConfidence = viewModel::submitAnswerWithConfidence,
                                onBookmarkToggle = viewModel::toggleBookmark,
                                onPrevious = viewModel::generatePreviousQuestion,
                                onSkip = viewModel::skipQuestion,
                                onNext = viewModel::generateNextQuestion,
                                onDashboardClick = { navController.navigate("dashboard") },
                                onRestart = viewModel::restartPractice,
                                onBack = { navController.popBackStack() }
                            )
                        }
                        composable("revision") {
                            val dueCount by localRepository.getDueItemsCountFlow().collectAsStateWithLifecycle(initialValue = 0)
                            RevisionDashboardScreen(
                                dueCount = dueCount,
                                onStartRevision = { navController.navigate("practice/Smart Revision/All/Smart Revision") },
                                onBack = { navController.popBackStack() }
                            )
                        }
                        composable("mistake_replay") {
                            val mistakeReplayViewModel: com.example.viewmodel.MistakeReplayViewModel = viewModel(factory = mistakeReplayFactory)
                            com.example.ui.screens.MistakeReplayScreen(
                                viewModel = mistakeReplayViewModel,
                                onBack = { navController.popBackStack() }
                            )
                        }
                        composable("papertwin") {
                            val profile = mainViewModel.selectedProfile.collectAsStateWithLifecycle().value
                            val paperTwinViewModel: com.example.viewmodel.PaperTwinViewModel = viewModel(factory = paperTwinFactory)
                            if (profile != null) {
                                com.example.ui.screens.PaperTwinScreen(
                                    viewModel = paperTwinViewModel,
                                    examId = profile.examId,
                                    onBack = { navController.popBackStack() },
                                    onStartTest = {
                                        navController.navigate("practice_papertwin")
                                    }
                                )
                            }
                        }
                        composable("practice_papertwin") {
                            val practiceViewModel: PracticeViewModel = viewModel(factory = practiceFactory)
                            val profile = mainViewModel.selectedProfile.collectAsStateWithLifecycle().value
                            val paper = localRepository.getLastGeneratedPaper()
                            val uiState by practiceViewModel.uiState.collectAsStateWithLifecycle()
                            
                            androidx.compose.runtime.LaunchedEffect(Unit) {
                                if (paper != null && profile != null) {
                                    practiceViewModel.startPaperTwin(paper, profile)
                                }
                            }
                            
                            PracticeScreen(
                                topicName = "Paper Twin",
                                tier = "Mixed",
                                format = "Mixed",
                                uiState = uiState,
                                onOptionSelected = practiceViewModel::onOptionPending,
                                onOptionCrossOut = practiceViewModel::toggleOptionCrossedOut,
                                onSubmitAnswerWithConfidence = practiceViewModel::submitAnswerWithConfidence,
                                onBookmarkToggle = practiceViewModel::toggleBookmark,
                                onPrevious = practiceViewModel::generatePreviousQuestion,
                                onSkip = practiceViewModel::skipQuestion,
                                onNext = practiceViewModel::generateNextQuestion,
                                onDashboardClick = { navController.navigate("dashboard") },
                                onRestart = practiceViewModel::restartPractice,
                                onBack = { navController.popBackStack() }
                            )
                        }
                        composable("dashboard") {
                            TrapDashboardScreen(
                                trapAnalytics = trapAnalytics,
                                onPracticeTrap = { trapType ->
                                    navController.navigate("practice/Trap Practice/All/Trap Training:${trapType}")
                                },
                                onBack = { navController.popBackStack() }
                            )
                        }
                    }
                }
            }
        }
    }
}



