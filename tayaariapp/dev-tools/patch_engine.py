with open("/app/applet/app/src/main/java/com/example/repository/QuestionSelectionEngine.kt", "r") as f:
    content = f.read()

import re

# Add ExamProfile import
if "import com.example.model.ExamProfile" not in content:
    content = content.replace("import com.example.database.AppDao", "import com.example.model.ExamProfile\nimport com.example.database.AppDao")

# Change constructor
content = content.replace("private val appDao: AppDao,", "private val localRepository: LocalRepository,")

# Change method signature
content = content.replace(
    "suspend fun getQuestionsForTopicAndTier(\n        topicName: String,\n        tier: String,\n        targetCount: Int,\n        preferredFormat: String = \"Statement-based\",\n        documentContext: String? = null\n    ): List<ExamQuestion>",
    "suspend fun getQuestionsForProfile(\n        topicName: String,\n        examProfile: ExamProfile,\n        targetCount: Int,\n        preferredFormat: String = \"Statement-based\",\n        documentContext: String? = null\n    ): List<ExamQuestion>"
)

# Replace the db call
content = content.replace(
    "val dbQuestions = appDao.getQuestionsByTopicAndTier(topicName, tier, targetCount)",
    "val dbQuestions = localRepository.getQuestionsForProfile(topicName, examProfile, targetCount)"
)

# And in the generation fallback, use the profile's tiers? Wait, the original method had `tier`. 
# If we are pulling for an exam profile, what tier do we pass to Gemini?
# Usually, we might want to generate a mix, or randomly pick one from allowed tiers.
# The prompt says: "only tiers their Group allows are ever returned". 
# Let's pass `examProfile.tiers.random()` to Gemini.
content = content.replace(
    "tier = tier,",
    "tier = examProfile.tiers.random(),"
)

with open("/app/applet/app/src/main/java/com/example/repository/QuestionSelectionEngine.kt", "w") as f:
    f.write(content)
