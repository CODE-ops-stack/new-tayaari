import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/OnboardingScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('"BPSC_PRELIMS_5_OPT" ->', '"BPSC_CCE_68TH", "BPSC_CCE_70TH_CURRENT" ->')

with codecs.open('app/src/main/java/com/example/ui/screens/OnboardingScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
