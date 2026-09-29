with open('tests/test_v13_adversarial_m5_auditor_stress.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'options={"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Basalt"}, {"id": "opt_c", "text": "Sandstone"}, {"id": "opt_d", "text": "Marble"}],',
    'options={"a": "Oxbow lake", "b": "Cirque lake", "c": "Crater lake", "d": "Glacial tarn"},': 'options=[{"id": "opt_a", "text": "Oxbow lake"}, {"id": "opt_b", "text": "Cirque lake"}, {"id": "opt_c", "text": "Crater lake"}, {"id": "opt_d", "text": "Glacial tarn"}],',
    'options={"a": "Mariana Trench", "b": "Tonga Trench", "c": "Java Trench", "d": "Puerto Rico Trench"},': 'options=[{"id": "opt_a", "text": "Mariana Trench"}, {"id": "opt_b", "text": "Tonga Trench"}, {"id": "opt_c", "text": "Java Trench"}, {"id": "opt_d", "text": "Puerto Rico Trench"}],',
    'options={"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Basalt"}, {"id": "opt_c", "text": "Sandstone"}, {"id": "opt_d", "text": "Marble"}],',
    'options={"a": "Basalt", "b": "Granite", "c": "Shale", "d": "Slate"},': 'options=[{"id": "opt_a", "text": "Basalt"}, {"id": "opt_b", "text": "Granite"}, {"id": "opt_c", "text": "Shale"}, {"id": "opt_d", "text": "Slate"}],',
    'options={"a": "Basalt", "b": "Granite", "c": "Shale", "d": "Slate"},': 'options=[{"id": "opt_a", "text": "Basalt"}, {"id": "opt_b", "text": "Granite"}, {"id": "opt_c", "text": "Shale"}, {"id": "opt_d", "text": "Slate"}],',
    'options={"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Basalt"}, {"id": "opt_c", "text": "Sandstone"}, {"id": "opt_d", "text": "Marble"}],',
    'options={"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Basalt"}, {"id": "opt_c", "text": "Sandstone"}, {"id": "opt_d", "text": "Marble"}],',
    'options={"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Basalt"}, {"id": "opt_c", "text": "Sandstone"}, {"id": "opt_d", "text": "Marble"}],',
    'options={"a": "Troposphere", "b": "Stratosphere", "c": "Mesosphere", "d": "Thermosphere"},': 'options=[{"id": "opt_a", "text": "Troposphere"}, {"id": "opt_b", "text": "Stratosphere"}, {"id": "opt_c", "text": "Mesosphere"}, {"id": "opt_d", "text": "Thermosphere"}],',
    'options={"a": "Troposphere", "b": "Stratosphere", "c": "Mesosphere", "d": "Thermosphere"},': 'options=[{"id": "opt_a", "text": "Troposphere"}, {"id": "opt_b", "text": "Stratosphere"}, {"id": "opt_c", "text": "Mesosphere"}, {"id": "opt_d", "text": "Thermosphere"}],',
    'options={"a": "Granite", "b": "Granite rock", "c": "Basalt", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Granite rock"}, {"id": "opt_c", "text": "Basalt"}, {"id": "opt_d", "text": "Marble"}],',
    'options={"a": "Basalt", "b": "Granite", "c": "Granite rock", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Basalt"}, {"id": "opt_b", "text": "Granite"}, {"id": "opt_c", "text": "Granite rock"}, {"id": "opt_d", "text": "Marble"}],',
    'options={"a": "Granite", "b": "Basalt", "c": "   ", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Basalt"}, {"id": "opt_c", "text": "   "}, {"id": "opt_d", "text": "Marble"}],',
    'options={"a": "Fog", "b": "Mist", "c": "Haze", "d": "Smog"},': 'options=[{"id": "opt_a", "text": "Fog"}, {"id": "opt_b", "text": "Mist"}, {"id": "opt_c", "text": "Haze"}, {"id": "opt_d", "text": "Smog"}],',
    'options={"a": "Thermosphere", "b": "Troposphere", "c": "Stratosphere", "d": "Mesosphere"},': 'options=[{"id": "opt_a", "text": "Thermosphere"}, {"id": "opt_b", "text": "Troposphere"}, {"id": "opt_c", "text": "Stratosphere"}, {"id": "opt_d", "text": "Mesosphere"}],',
    'options={"a": "Igneous rock", "b": "Sedimentary", "c": "Metamorphic", "d": "Volcanic"},': 'options=[{"id": "opt_a", "text": "Igneous rock"}, {"id": "opt_b", "text": "Sedimentary"}, {"id": "opt_c", "text": "Metamorphic"}, {"id": "opt_d", "text": "Volcanic"}],',
    'options={"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Basalt"}, {"id": "opt_c", "text": "Sandstone"}, {"id": "opt_d", "text": "Marble"}],',
    'options={"a": "Granite", "b": "Basalt", "c": "Granite", "d": "Marble"},': 'options=[{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Basalt"}, {"id": "opt_c", "text": "Granite"}, {"id": "opt_d", "text": "Marble"}],',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('tests/test_v13_adversarial_m5_auditor_stress.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')