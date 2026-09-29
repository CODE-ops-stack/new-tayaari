import codecs
import re

with codecs.open('app/src/main/java/com/example/ui/screens/OnboardingScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

# Change items(ExamBlueprintRegistry.blueprints) to items(ExamBlueprintRegistry.blueprints.filter { it.isActive })
content = content.replace(
    'items(ExamBlueprintRegistry.blueprints)', 
    'items(ExamBlueprintRegistry.blueprints.filter { it.isActive })'
)

# Update icon mapping
content = re.sub(
    r'"BPSC_CCE_68TH",\s*"BPSC_CCE_70TH_CURRENT"\s*->', 
    '"BPSC_CCE_72ND_2026" ->', 
    content
)

with codecs.open('app/src/main/java/com/example/ui/screens/OnboardingScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
