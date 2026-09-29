file = 'app/src/main/java/com/example/repository/LearnerModelEngine.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val weakTopics: List<TopicPerformance>,', 'val topicPerformances: Map<Int, TopicPerformance>,\n    val weakTopics: List<TopicPerformance>,')
text = text.replace('val weakTopics = activeTopics.takeLast(3).filter { it.accuracy < 0.5 }.reversed()', 'val weakTopics = activeTopics.takeLast(3).filter { it.accuracy < 0.5 }.reversed()')
text = text.replace('weakTopics = weakTopics,', 'topicPerformances = topicPerf,\n            weakTopics = weakTopics,')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
