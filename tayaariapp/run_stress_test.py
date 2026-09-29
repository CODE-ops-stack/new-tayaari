import json
import uuid

# Define the highly curated questions for the stress test
questions = []

def add_q(text, options, correct_idx, exam, topic, concept, format_type, diff, reasoning, sources):
    q = {
        "questionId": "Q-V2-STRESS-" + str(uuid.uuid4())[:8],
        "text": text,
        "options": options,
        "correctIndex": correct_idx,
        "metadata": {
            "examTarget": exam,
            "topic": topic,
            "concept": concept,
            "format": format_type,
            "difficulty": diff,
            "provenance": sources,
            "status": "APPROVED",
            "generationBasis": "Generator V2 Conceptual Engine"
        },
        "validation": {
            "distractorLogic": "Semantic neighborhood testing (e.g., swapping P-wave and S-wave properties, confusing plate boundary types).",
            "reasoning": reasoning
        }
    }
    questions.append(q)

# Concept 1: Plate Boundaries (Multi-statement)
add_q(
    text="Consider the following statements regarding plate tectonic boundaries:\n1. Constructive plate boundaries are characterized by sea-floor spreading and the formation of mid-oceanic ridges.\n2. Transform boundaries involve the subduction of one plate under another, leading to intense volcanic activity.\n3. The Himalayan mountain range is the result of a continent-continent convergent boundary.\nWhich of the statements given above is/are correct?",
    options=["1 and 2 only", "1 and 3 only", "2 and 3 only", "1, 2, and 3"],
    correct_idx=1,
    exam=["UPSC"],
    topic="Plate Tectonics",
    concept="Boundary Types & Landforms",
    format_type="Multi-statement",
    diff="PRELIMINARY_MODERATE",
    reasoning="Statement 2 is incorrect; transform boundaries slide past each other without subduction or volcanism. 1 and 3 are correct.",
    sources=["CCAB2_PART03", "OXFORD_ATLAS_PART05"]
)

# Concept 2: Transform Boundaries (Assertion-Reason)
add_q(
    text="Given below are two statements, one labeled as Assertion (A) and the other as Reason (R):\nAssertion (A): The San Andreas Fault experiences severe, shallow-focus earthquakes but lacks associated volcanic activity.\nReason (R): It is a conservative plate boundary where plates slide past one another without creating or destroying crust.\nSelect the correct answer from the codes given below:",
    options=["Both A and R are true and R is the correct explanation of A.", "Both A and R are true but R is not the correct explanation of A.", "A is true but R is false.", "A is false but R is true."],
    correct_idx=0,
    exam=["UPSC", "BPSC"],
    topic="Plate Tectonics",
    concept="Transform Boundary Mechanisms",
    format_type="Assertion/Reason",
    diff="PRELIMINARY_HARD",
    reasoning="Transform (conservative) boundaries have high friction causing earthquakes, but lack subduction or magma upwelling needed for volcanoes.",
    sources=["CCAB2_PART03"]
)

# Concept 3: India Seismic Zones
add_q(
    text="Based on the seismic zoning map of India, which of the following regions falls entirely within Seismic Zone V (Very High Damage Risk Zone)?",
    options=["The Malwa Plateau", "The Deccan Trap region of Maharashtra", "The Bihar-Nepal border region", "The coastal plains of Odisha"],
    correct_idx=2,
    exam=["BPSC", "UPSC"],
    topic="Seismic Zones",
    concept="India Seismic Zone V",
    format_type="Map + Concept",
    diff="PRELIMINARY_MODERATE",
    reasoning="According to Atlas Pg 68, the Bihar-Nepal border, parts of Kutch, and North-East India are in Zone V. The Deccan and Malwa plateaus are primarily Zone II/III.",
    sources=["OXFORD_ATLAS_PART03_PAGE68"]
)

# Concept 4: Seismic Waves (Conceptual Inference)
add_q(
    text="Which of the following best explains why an 'S-wave shadow zone' exists on the opposite side of the Earth from an earthquake epicenter?",
    options=["S-waves are absorbed by the solid inner core.", "S-waves are refracted away from the core-mantle boundary due to high density.", "S-waves cannot propagate through the liquid outer core.", "S-waves travel too slowly to reach the opposite side before dissipating."],
    correct_idx=2,
    exam=["UPSC"],
    topic="Earth's Interior",
    concept="S-wave Shadow Zone",
    format_type="Conceptual Inference",
    diff="PRELIMINARY_HARD",
    reasoning="S-waves (shear waves) require a solid medium to propagate and are blocked by the liquid outer core, creating a shadow zone.",
    sources=["CCAB2_PART03", "FATMAN-FRESH-PART02"]
)

# Concept 5: Map - Ring of Fire
add_q(
    text="The 'Ring of Fire', known for frequent earthquakes and volcanic eruptions, is structurally associated with which type of tectonic plate boundaries?",
    options=["Primarily divergent boundaries along the Mid-Atlantic Ridge", "Primarily convergent boundaries surrounding the Pacific Plate", "Primarily conservative boundaries surrounding the Eurasian Plate", "Primarily intraplate hotspots in the Indian Ocean"],
    correct_idx=1,
    exam=["UPSC", "BPSC"],
    topic="Plate Tectonics",
    concept="Ring of Fire / Pacific Plate",
    format_type="Map + Concept",
    diff="PRELIMINARY_EASY",
    reasoning="Atlas Pg 120 clearly shows the Ring of Fire following the subduction (convergent) zones surrounding the Pacific Plate.",
    sources=["OXFORD_ATLAS_PART05_PAGE120"]
)

# Concept 6: Continental Collision (India)
add_q(
    text="Despite intense seismic activity and tectonic uplift, the Himalayas do not possess active volcanoes. This is primarily because:",
    options=["The region lies entirely within a divergent plate boundary.", "Continent-continent convergence does not involve deep subduction of oceanic crust to produce magma.", "The crust in the Himalayan region is too thin to trap ascending magma.", "The Indian plate is moving away from the Eurasian plate, reducing friction."],
    correct_idx=1,
    exam=["UPSC", "BPSC"],
    topic="Plate Tectonics",
    concept="Continent-Continent Collision",
    format_type="Conceptual Inference",
    diff="PRELIMINARY_MODERATE",
    reasoning="When two continental plates collide, neither subducts deeply enough into the asthenosphere to melt and trigger volcanism, unlike oceanic-continental subduction.",
    sources=["CCAB2_PART03", "FATMAN-FRESH-PART02"]
)

# Concept 7: Hypocenter vs Epicenter
add_q(
    text="In seismology, the term 'Hypocenter' refers to:",
    options=["The point on the Earth's surface directly above the origin of an earthquake.", "The exact point within the Earth's crust where the fault rupture occurs.", "The region where the S-wave shadow zone begins.", "The instrument used to record seismic waves."],
    correct_idx=1,
    exam=["BPSC"],
    topic="Earthquakes",
    concept="Hypocenter vs Epicenter",
    format_type="Standard",
    diff="PRELIMINARY_EASY",
    reasoning="The hypocenter (focus) is the subsurface point of origin, while the epicenter is the surface point directly above it.",
    sources=["FATMAN-FRESH-PART02"]
)

# Concept 8: Minor Plates
add_q(
    text="Which of the following is a minor tectonic plate located entirely between the South American and Pacific plates?",
    options=["Cocos Plate", "Nazca Plate", "Scotia Plate", "Caribbean Plate"],
    correct_idx=1,
    exam=["UPSC"],
    topic="Plate Tectonics",
    concept="Minor Plates Location",
    format_type="Map + Concept",
    diff="PRELIMINARY_MODERATE",
    reasoning="Atlas Pg 120 explicitly maps the Nazca Plate wedged between the Pacific and South American plates.",
    sources=["OXFORD_ATLAS_PART05_PAGE120"]
)

# Leakage Auditor
def audit_leakage(batch):
    leaks = 0
    texts = [q["text"].lower() for q in batch]
    answers = [q["options"][q["correctIndex"]].lower() for q in batch]
    for i, ans in enumerate(answers):
        for j, text in enumerate(texts):
            if i != j and len(ans) > 5 and ans in text:
                leaks += 1
    return leaks

leaks = audit_leakage(questions)

batch = {
    "batchId": "BATCH-V2-STRESS-TECTONICS",
    "topic": "Plate Tectonics, Earthquakes & Seismic Zones",
    "target": "UPSC / BPSC",
    "size": len(questions),
    "questions": questions
}

with open("staging_batch_v2_stress_test.json", "w", encoding="utf-8") as f:
    json.dump(batch, f, indent=2)

print(f"Stress Test Generated: {len(questions)} candidates. Leaks detected: {leaks}")
