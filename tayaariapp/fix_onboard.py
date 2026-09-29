import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/OnboardingScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('"UPSC_CSE" ->', '"UPSC_CSE_2026" ->')
content = content.replace('"BPSC_PRELIMS" ->', '"BPSC_PRELIMS_5_OPT" ->')
content = content.replace('"SSC_CGL", "SSC_CHSL" ->', '"SSC_CGL_2025", "SSC_CHSL_2025" ->')
content = content.replace('"RRB_NTPC", "RRB_GROUP_D" ->', '"RRB_NTPC_2024", "RRB_GROUP_D_2024" ->')

with codecs.open('app/src/main/java/com/example/ui/screens/OnboardingScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
