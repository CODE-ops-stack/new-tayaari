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
import com.example.ui.screens.InvestorPreviewScreen
import com.example.ui.screens.MasterRoadmapScreen
import com.example.ui.screens.TrapDashboardScreen
import com.example.ui.screens.BookmarksScreen
import com.example.ui.screens.RevisionDashboardScreen
import com.example.viewmodel.BookmarksViewModel
import com.example.repository.UserPreferencesRepository
import com.example.ui.screens.OnboardingScreen
import com.example.ui.screens.AuthScreen
import com.example.viewmodel.MainViewModel
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

private const val QUESTION_BANK_VERSION = 5

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Production Anti-Piracy: Blocks screen recording & screenshots of Mains blueprints
        if (!BuildConfig.DEBUG) {
            window.setFlags(
                android.view.WindowManager.LayoutParams.FLAG_SECURE,
                android.view.WindowManager.LayoutParams.FLAG_SECURE
            )
        }

        val db = AppDatabase.getDatabase(applicationContext)
        val authFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                if (modelClass.isAssignableFrom(com.example.viewmodel.AuthViewModel::class.java)) {
                    return com.example.viewmodel.AuthViewModel(db.userDao()) as T
                }
                throw IllegalArgumentException("Unknown ViewModel class")
            }
        }
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

        // Notification channel and background alarm setup
        com.example.updater.UpdateNotificationHelper.createNotificationChannel(applicationContext)
        com.example.updater.AppUpdateManager.schedulePeriodicCheck(applicationContext)

        // Android 13+ runtime notification permission request
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), 101)
            }
        }
        
        // Sync questions dynamically from Cloud CDN repository (IO thread)
        lifecycleScope.launch(Dispatchers.IO) {
            val questionCount = db.appDao().getQuestionCount()
            val syncResult = com.example.repository.CloudQuestionSyncService.syncWithCloud(this@MainActivity)
            Log.d("MainActivity", "Cloud Sync Result: $syncResult")
            if (syncResult is com.example.repository.CloudQuestionSyncService.SyncResult.Failure && !syncResult.usingCache && questionCount == 0) {
                Log.w("MainActivity", "Cloud database fetch failed on first launch: ${syncResult.message}")
            }
        }

        // Autonomous Over-The-Air (OTA) APK update trigger on launch
        val isExplicitUpdateIntent = intent.getBooleanExtra("EXTRA_TRIGGER_UPDATE", false)
        lifecycleScope.launch(Dispatchers.IO) {
            com.example.updater.AppUpdateManager.checkForUpdates(applicationContext, autoDownload = true)
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
                return MainViewModel(userPrefsRepo, db.userDao()) as T
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
            val mainViewModel: MainViewModel = viewModel(factory = mainFactory)
            val themeMode by mainViewModel.themeMode.collectAsStateWithLifecycle()
            val fontScaleOption by mainViewModel.fontScaleOption.collectAsStateWithLifecycle()
            val isZenMode by mainViewModel.isZenMode.collectAsStateWithLifecycle()
            val dailyTarget by mainViewModel.dailyTarget.collectAsStateWithLifecycle()
            val todaySolvedCount by mainViewModel.todaySolvedCount.collectAsStateWithLifecycle()

            MyApplicationTheme(
                themeMode = themeMode,
                fontScale = fontScaleOption.scale,
                zenMode = isZenMode
            ) {
                val isLoading by mainViewModel.isLoading.collectAsStateWithLifecycle()
                val selectedProfiles by mainViewModel.selectedProfiles.collectAsStateWithLifecycle()

                val showSplash = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf(true) }

                androidx.compose.runtime.LaunchedEffect(Unit) {
                    kotlinx.coroutines.delay(2000)
                    showSplash.value = false
                }
                
                val loggedInUserId by mainViewModel.loggedInUserId.collectAsStateWithLifecycle()
                
                if (showSplash.value || isLoading) {
                    com.example.ui.screens.SplashScreen()
                } else if (loggedInUserId == null) {
                    val authViewModel: com.example.viewmodel.AuthViewModel = viewModel(factory = authFactory)
                    val authUiState by authViewModel.uiState.collectAsStateWithLifecycle()
                    AuthScreen(
                        uiState = authUiState,
                        onUsernameChange = authViewModel::onUsernameChange,
                        onPasswordChange = authViewModel::onPasswordChange,
                        onToggleMode = authViewModel::toggleMode,
                        onSubmit = {
                            authViewModel.authenticate { userId ->
                                mainViewModel.loginUser(userId)
                            }
                        },
                        onGuestLogin = {
                            mainViewModel.loginAsGuest(listOf(com.example.model.ExamBlueprintRegistry.blueprints.first()))
                        }
                    )
                } else if (selectedProfiles.isEmpty()) {
                    OnboardingScreen(
                        onProfilesSelected = { profiles ->
                            mainViewModel.saveProfiles(profiles)
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
                    val isSyncing by topicViewModel.isSyncing.collectAsStateWithLifecycle()
                    val syncStatusMessage by topicViewModel.syncStatusMessage.collectAsStateWithLifecycle()
                    val updateState by com.example.updater.AppUpdateManager.updateState.collectAsStateWithLifecycle()
                    
                    NavHost(navController = navController, startDestination = "topics") {
                        composable("topics") {
                            TopicSelectionScreen(
                                topics = topics,
                                nextAction = nextAction,
                                profile = selectedProfiles.firstOrNull(),
                                allSelectedProfiles = selectedProfiles,
                                onSelectActiveProfile = { bp ->
                                    mainViewModel.setActiveProfile(bp.examId)
                                },
                                isSyncing = isSyncing,
                                syncStatusMessage = syncStatusMessage,
                                updateState = updateState,
                                themeMode = themeMode,
                                onThemeModeChange = mainViewModel::setThemeMode,
                                fontScaleOption = fontScaleOption,
                                onFontScaleOptionChange = mainViewModel::setFontScaleOption,
                                isZenMode = isZenMode,
                                onZenModeChange = mainViewModel::setZenMode,
                                dailyTarget = dailyTarget,
                                onDailyTargetChange = mainViewModel::setDailyTarget,
                                todaySolvedCount = todaySolvedCount,
                                onTopicSelected = { topicName, tier, format ->
                                      topicViewModel.onPracticeIntent(topicName, tier, format) { t, r, f ->
                                          val encT = android.net.Uri.encode(t)
                                          val encR = android.net.Uri.encode(r)
                                          val encF = android.net.Uri.encode(f)
                                          navController.navigate("practice/$encT/$encR/$encF")
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
                                onMainsPracticeClick = {
                                    navController.navigate("mains_practice")
                                },
                                onInsightsClick = {
                                    navController.navigate("insights")
                                },
                                onChangeExam = {
                                    mainViewModel.clearProfile()
                                },
                                onRefreshSync = {
                                    topicViewModel.refreshFromCloud(this@MainActivity)
                                    lifecycleScope.launch(Dispatchers.IO) {
                                        com.example.updater.AppUpdateManager.checkForUpdates(applicationContext, autoDownload = true)
                                    }
                                },
                                onCheckUpdate = {
                                    lifecycleScope.launch(Dispatchers.IO) {
                                        com.example.updater.AppUpdateManager.checkForUpdates(applicationContext, autoDownload = true)
                                    }
                                },
                                onInvestorPreviewClick = {
                                    navController.navigate("investor_preview")
                                },
                                onRoadmapClick = {
                                    navController.navigate("master_roadmap")
                                }
                            )
                        }
                        composable("master_roadmap") {
                            MasterRoadmapScreen(
                                onBackClick = { navController.popBackStack() },
                                onTopicSelect = { topicName, tier, format ->
                                    topicViewModel.onPracticeIntent(topicName, tier, format) { t, r, f ->
                                        val encT = android.net.Uri.encode(t)
                                        val encR = android.net.Uri.encode(r)
                                        val encF = android.net.Uri.encode(f)
                                        navController.navigate("practice/$encT/$encR/$encF")
                                    }
                                }
                            )
                        }
                        composable("investor_preview") {
                            InvestorPreviewScreen(
                                onBack = { navController.popBackStack() }
                            )
                        }
                        composable("mains_practice") {
                            val isUpsc = selectedProfiles.firstOrNull()?.examId?.contains("UPSC", ignoreCase = true) == true
                            if (!isUpsc) {
                                androidx.compose.runtime.LaunchedEffect(Unit) {
                                    navController.popBackStack()
                                }
                            } else {
                                com.example.ui.mains.MainsPracticeScreen(
                                    questionId = "MAINS-Q1",
                                    onBack = { navController.popBackStack() }
                                )
                            }
                        }
                        composable("mains_practice/{questionId}") { backStackEntry ->
                            val isUpsc = selectedProfiles.firstOrNull()?.examId?.contains("UPSC", ignoreCase = true) == true
                            if (!isUpsc) {
                                androidx.compose.runtime.LaunchedEffect(Unit) {
                                    navController.popBackStack()
                                }
                            } else {
                                val qId = backStackEntry.arguments?.getString("questionId") ?: "MAINS-Q1"
                                com.example.ui.mains.MainsPracticeScreen(
                                    questionId = qId,
                                    onBack = { navController.popBackStack() }
                                )
                            }
                        }

                composable("insights") {
                    InsightsDashboardScreen(
                        localRepository = localRepository,
                        profile = selectedProfiles.firstOrNull(),
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
                            
                            val activeProfile = selectedProfiles.firstOrNull() ?: com.example.model.ExamBlueprintRegistry.blueprints.first()

                            androidx.compose.runtime.LaunchedEffect(topicName, tier, format, activeProfile) {
                                viewModel.startPractice(topicName, activeProfile, tier, format)
                            }
                            
                            PracticeScreen(
                                topicName = topicName,
                                tier = tier,
                                format = format,
                                profile = activeProfile,
                                uiState = uiState,
                                onOptionSelected = { optId ->
                                    viewModel.onOptionPending(optId)
                                    mainViewModel.incrementTodaySolved()
                                },
                                onOptionCrossOut = viewModel::toggleOptionCrossedOut,
                                onSubmitAnswer = viewModel::submitAnswer,
                                onBookmarkToggle = viewModel::toggleBookmark,
                                onPrevious = viewModel::generatePreviousQuestion,
                                onSkip = viewModel::skipQuestion,
                                onNext = viewModel::generateNextQuestion,
                                onDashboardClick = { navController.navigate("dashboard") },
                                onRestart = viewModel::restartPractice,
                                onJumpToQuestion = viewModel::jumpToQuestion,
                                onToggleGameMode = viewModel::toggleGameMode,
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
                            val profile = mainViewModel.selectedProfiles.collectAsStateWithLifecycle().value.firstOrNull()
                            val paperTwinViewModel: com.example.viewmodel.PaperTwinViewModel = viewModel(factory = paperTwinFactory)
                            if (profile != null) {
                                com.example.ui.screens.PaperTwinScreen(
                                    viewModel = paperTwinViewModel,
                                    examId = selectedProfiles.firstOrNull()?.examId ?: "",
                                    onBack = { navController.popBackStack() },
                                    onStartTest = {
                                        navController.navigate("practice_papertwin")
                                    }
                                )
                            }
                        }
                        composable("practice_papertwin") {
                            val practiceViewModel: PracticeViewModel = viewModel(factory = practiceFactory)
                            val profile = mainViewModel.selectedProfiles.collectAsStateWithLifecycle().value.firstOrNull()
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
                                profile = profile,
                                uiState = uiState,
                                onOptionSelected = practiceViewModel::onOptionPending,
                                onOptionCrossOut = practiceViewModel::toggleOptionCrossedOut,
                                onSubmitAnswer = practiceViewModel::submitAnswer,
                                onBookmarkToggle = practiceViewModel::toggleBookmark,
                                onPrevious = practiceViewModel::generatePreviousQuestion,
                                onSkip = practiceViewModel::skipQuestion,
                                onNext = practiceViewModel::generateNextQuestion,
                                onDashboardClick = { navController.navigate("dashboard") },
                                onRestart = practiceViewModel::restartPractice,
                                onJumpToQuestion = practiceViewModel::jumpToQuestion,
                                onToggleGameMode = practiceViewModel::toggleGameMode,
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

    override fun onResume() {
        super.onResume()
        lifecycleScope.launch(Dispatchers.IO) {
            com.example.repository.CloudQuestionSyncService.syncWithCloud(this@MainActivity)
            com.example.updater.AppUpdateManager.checkForUpdates(applicationContext, autoDownload = true)
        }
    }
}



