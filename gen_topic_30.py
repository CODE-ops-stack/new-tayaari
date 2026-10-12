import json
import os

TOPIC_ID = 30
TOPIC_NAME = "Advanced Ocean Topography & Climatology Models"
SECTION = "🎓 UPSC Geography Optional"

questions = []

# -----------------------------------------------------------------------------
# LEVEL 1: FOUNDATION / BASIC (Questions 1 to 15)
# Core ocean bathymetry, air mass fundamentals, thermodynamic lapse rates
# -----------------------------------------------------------------------------
basic_data = [
    (
        "In oceanography, the submarine relief of the Atlantic Ocean is dominated by the 'Mid-Atlantic Ridge'. The portion of this ridge lying north of the equator is historically designated as the:",
        "Dolphin Rise", "Challenger Rise", "Walvis Ridge", "Rio Grande Rise", "opt_a",
        "The Mid-Atlantic Ridge stretches ~16,000 km in an S-shape through the Atlantic Ocean. The northern segment (North Atlantic) is historically termed the 'Dolphin Rise', while the southern segment (South Atlantic) is designated as the 'Challenger Rise'.",
        "Mid-Atlantic Ridge: North Atlantic = Dolphin Rise; South Atlantic = Challenger Rise.",
        "Challenger Rise Trap"
    ),
    (
        "Near the equator, the Mid-Atlantic Ridge is severed by an immense fracture zone and deep trench reaching depths exceeding 7,700 meters, known as the:",
        "Romanche Trench (Romanche Deep)", "Mariana Trench", "Puerto Rico Trench", "Java (Sunda) Trench", "opt_a",
        "The Romanche Trench (Romanche Fracture Zone) is a major equatorial transform fault cleft that cuts directly through the Mid-Atlantic Ridge, allowing cold Antarctic Bottom Water to flow from the western into the eastern Atlantic basin.",
        "Romanche Deep = Major equatorial transform trench severing the Mid-Atlantic Ridge.",
        "Puerto Rico Trench Trap"
    ),
    (
        "In the Indian Ocean, which prominent, continuous, north-south oriented submarine ridge extends along the 90°E meridian for nearly 5,000 km from the Bay of Bengal toward the Southern Ocean?",
        "Ninety East Ridge", "Chagos-Laccadive Ridge", "Carlsberg Ridge", "Southwest Indian Ridge", "opt_a",
        "The Ninety East Ridge is a linear volcanic hotspot track (formed by the Kerguelen hotspot) running parallel to the 90°E meridian, dividing the Central Indian Basin from the Wharton Basin.",
        "Ninety East Ridge = 5,000 km linear submarine ridge along the 90°E meridian in the Indian Ocean.",
        "Carlsberg Ridge Trap"
    ),
    (
        "In the Arabian Sea, the submarine mid-ocean spreading ridge that represents the northwest continuation of the Central Indian Ridge trending toward the Gulf of Aden is the:",
        "Carlsberg Ridge", "Ninety East Ridge", "Chagos-Laccadive Ridge", "Mozambique Ridge", "opt_a",
        "The Carlsberg Ridge is the divergent mid-ocean spreading boundary separating the Arabian and Indian tectonic plates, extending from south of the Chagos archipelago northwestward into the Gulf of Aden.",
        "Carlsberg Ridge = Spreading mid-ocean ridge in the Arabian Sea / Northwest Indian Ocean.",
        "Ninety East Trap"
    ),
    (
        "In the Pacific Ocean, the broad, gently sloping submarine divergence zone that lacks a prominent central rift valley (unlike the slow-spreading Mid-Atlantic Ridge) is known as the:",
        "East Pacific Rise", "Mid-Atlantic Ridge", "Carlsberg Ridge", "Kerguelen Plateau", "opt_a",
        "The East Pacific Rise is a fast-spreading mid-ocean ridge (spreading at 8 to 16 cm/year). Because it spreads so rapidly, volcanic magma floods the crest, forming a broad, smooth topographic swell without a deep central axial rift valley.",
        "East Pacific Rise = Fast-spreading mid-ocean ridge in southeastern Pacific (broad swell without deep rift).",
        "Slow Spreading Fallacy"
    ),
    (
        "Pelagic ocean deposits formed from the microscopic calcium carbonate (CaCO3) shells of single-celled zooplankton floating in warm surface waters are termed:",
        "Globigerina Ooze (Calcareous ooze)", "Diatom Ooze (Siliceous ooze)", "Radiolarian Ooze", "Red Clay (Pelagic clay)", "opt_a",
        "Globigerina Ooze is a calcareous pelagic sediment composed predominantly of the tests of foraminifera (Globigerina), covering vast areas of the tropical and temperate Atlantic, Pacific, and Indian Oceans at depths above the CCD.",
        "Globigerina Ooze = Calcareous pelagic ooze (warm, shallow-to-medium ocean floors above CCD).",
        "Diatom Siliceous Trap"
    ),
    (
        "Pelagic ocean deposits formed from the microscopic silica-based shells of single-celled phytoplankton that thrive in cold, nutrient-rich sub-polar and Antarctic waters are termed:",
        "Diatom Ooze (Siliceous ooze)", "Globigerina Ooze", "Pteropod Ooze", "Coral Sand", "opt_a",
        "Diatom Ooze is a siliceous pelagic deposit formed by microscopic single-celled algae (diatoms) with opaline silica cell walls, covering vast belts of the circumpolar Southern Ocean and North Pacific.",
        "Diatom Ooze = Siliceous ooze (Cold Antarctic and sub-polar waters).",
        "Calcareous Trap"
    ),
    (
        "The 'Carbonate Compensation Depth' (CCD), typically located at an ocean depth of 4,000 to 5,000 meters, is defined as the depth below which:",
        "The rate of calcium carbonate dissolution equals the rate of calcium carbonate supply, meaning calcareous shells dissolve completely",
        "Seawater temperature drops to the absolute freezing point of pure water",
        "Total sunlight penetration drops to exactly zero",
        "All marine organisms are crushed by hydrostatic water pressure", "opt_a",
        "At depths below the CCD (~4,500 m), high hydrostatic pressure, low water temperature, and high dissolved CO2 make seawater highly corrosive to calcium carbonate. Calcareous tests dissolve entirely, leaving only insoluble Red Clay and Siliceous oozes.",
        "Carbonate Compensation Depth (CCD, ~4,500m) = Calcareous shells dissolve completely; only Red Clay & Siliceous oozes survive.",
        "Freezing Point Fallacy"
    ),
    (
        "In the Bergeron classification of air masses, an air mass originating over cold, dry continental landmasses in sub-polar latitudes (such as Siberia or northern Canada in winter) is designated as:",
        "cP (Continental Polar)", "mP (Maritime Polar)", "cT (Continental Tropical)", "mT (Maritime Tropical)", "opt_a",
        "Air mass notation uses a lowercase letter for humidity source (c = continental/dry, m = maritime/moist) and an uppercase letter for thermal source (T = tropical/warm, P = polar/cold, A = arctic/very cold). cP = Continental Polar.",
        "Air Mass Notation: cP = Continental Polar (Cold & Dry). mT = Maritime Tropical (Warm & Humid).",
        "Maritime Inversion Trap"
    ),
    (
        "In Jacob Bjerknes's 'Polar Front Theory' (1918), mid-latitude temperate wave cyclones develop along the boundary separating which two contrasting air masses?",
        "Cold Polar Air Mass and Warm Tropical Air Mass",
        "Equatorial Maritime Air Mass and Desert Air Mass",
        "Upper Stratospheric Air and Mesospheric Air",
        "Two identical warm maritime air masses flowing in the same direction", "opt_a",
        "Bjerknes and the Bergen School established that temperate wave cyclones originate along the semi-permanent Polar Front, where cold polar easterly air masses (cP) clash with warm subtropical westerly air masses (mT), creating wave instability and frontogenesis.",
        "Polar Front Theory (Bjerknes) = Mid-latitude cyclone waves form at the clash of Cold Polar (cP) and Warm Tropical (mT) air masses.",
        "Equatorial Fallacy"
    ),
    (
        "In atmospheric thermodynamics, what is the 'Dry Adiabatic Lapse Rate' (DALR)?",
        "The rate at which an unsaturated parcel of dry air cools as it rises, equal to approximately 9.8°C (or ~10°C) per 1,000 meters",
        "The rate at which saturated clouds drop rain per hour",
        "The horizontal temperature decrease between the equator and poles",
        "The temperature increase inside an urban asphalt parking lot", "opt_a",
        "DALR represents the adiabatic cooling of an unsaturated parcel of air expanding against declining atmospheric pressure without heat exchange, universally constant at approximately 9.8°C/km (or ~1°C/100m).",
        "DALR = 9.8°C per 1,000m (~10°C/km). Unsaturated dry air parcel adiabatic cooling.",
        "SALR Confusion Trap"
    ),
    (
        "Why is the 'Saturated (Wet) Adiabatic Lapse Rate' (SALR / MALR) always lower in value (typically 4°C to 7°C per 1,000 m) than the Dry Adiabatic Lapse Rate?",
        "The condensation of water vapor releases latent heat into the rising parcel, partially offsetting adiabatic expansion cooling",
        "Saturated air parcels expand twice as fast as dry air parcels",
        "Water vapor absorbs cosmic rays from outer space",
        "Cloud droplets freeze immediately into heavy iron spheres", "opt_a",
        "Once an air parcel reaches its dew point and condensation begins, the release of Latent Heat of Condensation (~2.5 x 10^6 J/kg) warms the parcel, reducing the net cooling rate to ~4-7°C/km.",
        "SALR < DALR because Latent Heat of Condensation releases warmth, slowing the net rate of cooling.",
        "Expansion Speed Fallacy"
    ),
    (
        "The 'Urban Heat Island' (UHI) phenomenon in micro-climatology describes which thermal anomaly?",
        "Urban metropolitan cores exhibit significantly higher atmospheric and surface temperatures than their surrounding rural countryside",
        "Cities are always 20 degrees colder than surrounding pine forests",
        "Tropical coral islands that emit underground volcanic steam",
        "A floating solar mirror built above urban skyscrapers", "opt_a",
        "UHIs result from thermal mass storage in concrete/asphalt, reduced evapotranspiration due to lack of vegetation, anthropogenic waste heat from HVAC/vehicles, and urban canyon geometry trapping longwave radiation.",
        "Urban Heat Island (UHI) = Higher urban core temperatures vs cooler rural periphery.",
        "Cold City Fallacy"
    ),
    (
        "In C.W. Thornthwaite's 1948 'Rational Classification of Climate', what fundamental concept was introduced to measure water need and define climatic boundaries?",
        "Potential Evapotranspiration (PET) and the Moisture Index (Im)",
        "Total annual snowfall depth only",
        "Average cloud cover percentage measured by satellite photography",
        "The total volume of groundwater pumped by agricultural tube-wells", "opt_a",
        "Thornthwaite (1948) introduced Potential Evapotranspiration (PET)—the water loss that would occur if water were constantly available in the soil—and formulated the Moisture Index to classify moisture provinces based on actual water balance.",
        "Thornthwaite 1948 = Potential Evapotranspiration (PET) & Moisture Index (Im). Based on water balance.",
        "Koppen Empirical Trap"
    ),
    (
        "Under the United Nations Convention on the Law of the Sea (UNCLOS), the 'International Seabed Authority' (ISA), headquartered in Kingston, Jamaica, was established to govern:",
        "Mineral-related activities in the international seabed area beyond the limits of national jurisdiction (the 'Area'), deemed the Common Heritage of Mankind",
        "All national coastal fishing boat registrations within 12 nautical miles",
        "The pricing of international airline tickets across oceanic flight paths",
        "The military deployment of naval submarine fleets in territorial waters", "opt_a",
        "Part XI of UNCLOS establishes the International Seabed Authority (ISA) to organize, regulate, and control all mineral activities (e.g., polymetallic nodule exploration) in the international seabed beyond national EEZs, governed by the 'Common Heritage of Mankind' principle.",
        "ISA (Kingston, Jamaica) = Regulates deep-seabed mining in international waters ('Common Heritage of Mankind').",
        "Coastal Fishing Trap"
    )
]

for idx, (stem, a, b, c, d, ans, expl, mem, trap) in enumerate(basic_data, 1):
    q = {
        "id": f"opt_q30_{idx:02d}",
        "topicId": TOPIC_ID,
        "topicName": TOPIC_NAME,
        "section": SECTION,
        "tier": "Basic",
        "format": "Direct Fact",
        "stem": stem,
        "options": {"opt_a": a, "opt_b": b, "opt_c": c, "opt_d": d},
        "correctAnswer": ans,
        "explanation": f"{expl}\n\n💡 RANKER'S MEMORY LOCK: {mem}",
        "distractorDissections": [
            {"optionId": "opt_b" if ans != "opt_b" else "opt_a", "trapType": trap, "dissection": "Distractor represents a different oceanic basin or thermodynamic lapse rate."},
            {"optionId": "opt_c" if ans != "opt_c" else "opt_b", "trapType": "Concept Swap Trap", "dissection": "Do not swap the primary thermodynamic or bathymetric feature with a secondary factor."},
            {"optionId": "opt_d" if ans != "opt_d" else "opt_c", "trapType": "Geomorphic Inversion Trap", "dissection": "Avoid confusing calcareous vs siliceous ooze distribution."}
        ]
    }
    questions.append(q)

# -----------------------------------------------------------------------------
# LEVEL 2: MEDIUM (Questions 16 to 35)
# In-depth mechanisms, processes, comparative models, and teleconnections
# -----------------------------------------------------------------------------
medium_data = [
    (
        "The 'Thermohaline Circulation' (often termed the Global Ocean Conveyor Belt, popularized by Wallace Broecker) is driven primarily by density differences governed by:",
        "Water Temperature (thermal) and Salinity (haline) gradients",
        "Surface trade wind friction exclusively",
        "Gravitational pull of Jupiter and Saturn",
        "Underground volcanic magma eruptions along mid-ocean ridges", "opt_a",
        "Thermohaline circulation is deep ocean circulation powered by density contrasts: cold, highly saline surface water sinks in the North Atlantic (forming North Atlantic Deep Water, NADW) and around Antarctica (Antarctic Bottom Water, AABW), initiating a global overturn taking ~1,000 years.",
        "Thermohaline Circulation = Density-driven deep ocean conveyor (Temperature + Salinity). Sinks at North Atlantic & Weddell Sea.",
        "Wind Driven Only Trap"
    ),
    (
        "In physical oceanography, 'Antarctic Bottom Water' (AABW), the densest and coldest water mass in the world ocean, forms primarily through which process in the Weddell and Ross Seas?",
        "Sea ice formation (brine rejection), where freezing seawater expels salt into the underlying freezing water, making it hyper-dense",
        "Evaporation under intense tropical desert sunlight",
        "The influx of boiling hydrothermal vent fluids",
        "River runoff from melting warm continental deltas", "opt_a",
        "When sea ice freezes, salt is rejected from the ice crystal lattice ('brine rejection'). The freezing-cold water beneath becomes highly saline and dense, plunging down the Antarctic continental slope to flow along the ocean floor across the globe.",
        "Antarctic Bottom Water (AABW) = Brine rejection during sea-ice freezing → Densest water mass on Earth.",
        "Tropical Evaporation Trap"
    ),
    (
        "In tropical climatology, the 'Walker Circulation' is an atmospheric zonal overturning circulation over the equatorial Pacific Ocean characterized under normal (non-El Niño) conditions by:",
        "Ascending moist air and low surface pressure over the warm Western Pacific (Indonesia), and descending dry air and high surface pressure over the cold Eastern Pacific (near Peru)",
        "Ascending air over Peru and descending air over Indonesia",
        "Permanent westerly gales blowing across the equator from Chile to Japan",
        "A stagnant atmospheric layer with zero wind movement year-round", "opt_a",
        "Under normal conditions, easterly Trade Winds push warm surface water westward, piling up a warm pool in the Western Pacific (low pressure, deep convection, heavy rain over Indonesia). Cold upwelling waters off Peru create high pressure and descending dry air.",
        "Normal Walker Circulation = Low pressure & rain over Indonesia (Warm pool); High pressure & dry over Peru (Cold upwelling).",
        "El Niño Inversion Trap"
    ),
    (
        "During an 'El Niño' (ENSO warm phase) event, which major oceanographic and atmospheric disruption occurs across the equatorial Pacific?",
        "Trade winds weaken or reverse to westerlies, the warm pool shifts eastward toward South America, and coastal upwelling of cold, nutrient-rich water off Peru is suppressed",
        "Trade winds blow with unprecedented hurricane force toward Indonesia",
        "Peru experiences severe freezing blizzard conditions while Indonesia floods completely",
        "The Pacific Ocean drains completely into the Indian Ocean", "opt_a",
        "During El Niño, relaxed trade winds allow warm water to surge eastward as Kelvin waves. The thermocline flattens, shutting off coastal upwelling off Peru, destroying the anchovy fishery, and shifting rainfall eastward while triggering droughts in Australia, India, and Indonesia.",
        "El Niño = Weak trade winds + Warm water surges to Peru + Thermocline flattens + Upwelling suppressed + Indian Monsoon failure risk.",
        "La Niña Inversion Trap"
    ),
    (
        "The 'Indian Ocean Dipole' (IOD), formulated by Saji et al. (1999), is measured by the Dipole Mode Index (DMI), which calculates the sea surface temperature (SST) anomaly difference between which two regions?",
        "The Western Equatorial Indian Ocean (near Arabian Sea/Africa) and the Eastern Equatorial Indian Ocean (south of Indonesia)",
        "The Bay of Bengal and the Persian Gulf",
        "The Red Sea and the Southern Ocean near Antarctica",
        "The Gulf of Kutch and the Gulf of Khambhat", "opt_a",
        "The IOD is a coupled ocean-atmosphere phenomenon. A 'Positive IOD' occurs when the western equatorial Indian Ocean is anomalously warm and the eastern equatorial Indian Ocean is anomalously cold, which typically aids the Indian summer monsoon.",
        "Indian Ocean Dipole (IOD): Positive IOD = Warm Western Indian Ocean / Cold Eastern Indian Ocean (Favorable for Indian Monsoon).",
        "Bay of Bengal Trap"
    ),
    (
        "The 'Madden-Julian Oscillation' (MJO), discovered in 1971, is an intra-seasonal tropical climate phenomenon characterized by:",
        "An eastward-propagating pulse of cloudiness, convection, and rainfall along the equatorial belt with a periodicity of 30 to 60 days",
        "A permanent stationary cloud that never moves from the North Pole",
        "A multi-decadal 50-year oceanic oscillation in the North Atlantic",
        "A daily diurnal land and sea breeze cycle along tropical coasts", "opt_a",
        "The MJO is the primary intra-seasonal variability in the tropical atmosphere: an eastward-moving disturbance of suppressed and enhanced convective rain traversing the global tropics every 30–60 days, profoundly modulating monsoon active and break spells.",
        "Madden-Julian Oscillation (MJO) = Eastward-propagating tropical convective wave (30–60 day cycle). Enhances/suppresses monsoon bursts.",
        "Decadal Swap Trap"
    ),
    (
        "Charles Darwin's classic 'Subsidence Theory' of coral reef formation (1842) explains the evolutionary sequence of coral reefs as progressing through which three successive stages?",
        "Fringing Reef → Barrier Reef → Atoll",
        "Atoll → Barrier Reef → Fringing Reef",
        "Coral Sand Bar → Barrier Reef → Submerged Seamount",
        "Fringing Reef → Mangrove Swamp → Desert Playa", "opt_a",
        "Darwin demonstrated that coral reefs grow upward around an actively subsiding volcanic island: first forming a 'Fringing Reef' adhering to the shore, evolving into a 'Barrier Reef' as a lagoon develops, and culminating in an 'Atoll' when the central volcanic peak submerges entirely.",
        "Darwin's Reef Evolution: Fringing Reef → Barrier Reef → Atoll (Driven by volcanic island subsidence).",
        "Reverse Evolution Trap"
    ),
    (
        "Reginald Daly's 'Glacial Control Theory' of coral reef formation (1915) contrasted with Darwin by explaining coral atolls through which mechanism?",
        "Pleistocene sea-level drop (by ~100m) allowed wave abrasion to plane down volcanic islands into flat platforms; post-glacial sea-level rise stimulated upward coral growth on these pre-cut platforms",
        "Continuous tectonic uplift pushing coral reefs up into the stratosphere",
        "Meteorite showers blasting circular craters in the ocean floor",
        "Coral polyps migrating across the ocean on the backs of migrating whales", "opt_a",
        "Daly argued that reef foundations were prepared during glacial epochs when sea level dropped and wave action planed volcanic summits flat. When ice sheets melted, returning warm water allowed coral polyps to build upward at an equal pace with rising sea levels.",
        "Reginald Daly = Glacial Control Theory (Glacial wave planation + Post-glacial sea-level rise).",
        "Darwin Subsidence Swap"
    ),
    (
        "W.M. Davis strongly defended Charles Darwin's Subsidence Theory of coral reefs against Reginald Daly's Glacial Control Theory by pointing to which conclusive geomorphic evidence?",
        "Embayed, drowned river valleys (rias) along the central islands behind barrier reefs, proving regional crustal subsidence",
        "The presence of active volcanoes on all coral atolls",
        "The complete absence of water inside lagoon basins",
        "The occurrence of fossilized desert sand dunes on deep ocean floors", "opt_a",
        "Davis argued that coastal indentations and drowned valleys (rias) behind barrier reefs could only form by tectonic subsidence submerging dissected subaerial river topography, providing conclusive physical evidence for Darwin's model.",
        "W.M. Davis = Supported Darwin using drowned valleys (embayed coastlines) as proof of land subsidence.",
        "Volcano Presence Fallacy"
    ),
    (
        "John Murray's 'Non-Subsidence Solution Theory' of coral reefs suggested that atolls form without crustal subsidence through which dual mechanisms?",
        "Deposition of pelagic sediments on submarine banks until reaching the coral-growing photic zone, followed by outward coral growth and biochemical dissolution of dead interior coral to create the lagoon",
        "Continuous subduction of oceanic trenches under island arcs",
        "Glacial moraine deposition in equatorial waters",
        "Tectonic thrust faults uplifting the abyssal plains above sea level", "opt_a",
        "Sir John Murray (Challenger expedition) argued that submarine peaks build up to ~30 fathoms via pelagic sediment accumulation, where corals establish. Corals grow outward where food/oxygen are abundant, while dead interior corals dissolve under carbonated seawater, forming the central lagoon.",
        "John Murray = Submarine bank buildup + Outward coral growth + Solution of interior lagoon (No subsidence).",
        "Subduction Trap"
    ),
    (
        "In C.W. Thornthwaite's 1931 climatic classification, the 'Precipitation Effectiveness' (P/E Index) was formulated to account for:",
        "The relationship between precipitation and evaporation, recognizing that high rainfall in hot climates is less effective for plants than in cool climates",
        "The total number of rainy days recorded by an optical rain gauge",
        "The chemical pH acidity of rainfall droplets",
        "The velocity of raindrops hitting the forest canopy", "opt_a",
        "Thornthwaite realized that raw rainfall numbers are meaningless without accounting for evaporation: 1,000 mm of rain in cool London supports lush vegetation, whereas 1,000 mm in hot Rajasthan evaporates rapidly. P/E index calculated monthly effective moisture.",
        "Thornthwaite 1931 = P/E Index (Precipitation Effectiveness) and T/E Index (Temperature Efficiency).",
        "Raw Rainfall Trap"
    ),
    (
        "Glenn T. Trewartha modified W.M. Koppen's climatic classification primarily to correct which major perceived flaw in Koppen's temperate zone boundaries?",
        "Koppen's definition of subtropical and temperate climates grouped together disparate thermal regimes; Trewartha introduced a requirement that at least 8 months must have mean temperatures of 10°C or above for Subtropical (C) climates",
        "Koppen completely omitted the tropical rainforest climate from his world map",
        "Koppen used letters instead of numbers to designate climate types",
        "Trewartha eliminated all temperature measurements and relied only on cloud photographs", "opt_a",
        "Trewartha simplified Koppen: he defined Subtropical (C) climates as having 8 to 11 months with temperatures >= 10°C, and Temperate (D) climates as having 4 to 7 months >= 10°C, creating a more realistic universal climatic boundary.",
        "Trewartha Modification = Defined Subtropical (C) as 8–11 months >= 10°C; Temperate (D) as 4–7 months >= 10°C.",
        "Rainforest Omission Trap"
    ),
    (
        "In W.M. Koppen's climatic classification, the boundary separating Dry Climates (B) from Humid Climates (A, C, D) is calculated based on:",
        "A mathematical formula linking mean annual temperature and precipitation distribution (whether rainfall is concentrated in winter, summer, or evenly distributed)",
        "The absolute depth of permafrost in the soil",
        "The presence of deciduous versus coniferous tree needles",
        "The elevation of mountain peaks above 5,000 meters", "opt_a",
        "Koppen recognized that aridity depends on temperature: higher temperatures cause higher evaporation. He formulated three threshold equations: r = 2t (winter rain), r = 2t + 28 (summer rain), and r = 2t + 14 (evenly distributed), where r is precipitation in cm and t is mean temperature in °C.",
        "Koppen 'B' Boundary = Temperature vs Precipitation distribution formula (accounts for evaporation demand).",
        "Elevation Only Trap"
    ),
    (
        "In boundary layer climatology, an 'Urban Canopy Layer' (UCL) is distinguished from an 'Urban Boundary Layer' (UBL) because it is:",
        "The micro-scale atmospheric layer extending from the street surface up to the average height of roofs and building tops, dominated by building canyon micro-climates",
        "A regional haze layer extending 10 kilometers into the upper troposphere",
        "An artificial glass dome constructed over sports stadiums",
        "A layer of ozone gas concentrated over municipal sewage treatment facilities", "opt_a",
        "T.R. Oke (1976) divided urban atmospheres into: (1) Urban Canopy Layer (UCL, micro-scale, between buildings from ground to roof level), and (2) Urban Boundary Layer (UBL, mesoscale thermal plume extending above the city into the planetary boundary layer).",
        "Urban Canopy Layer (UCL) = Street level up to roof height (building canyons). Urban Boundary Layer = Mesoscale plume above roofs.",
        "Glass Dome Trap"
    ),
    (
        "What are 'Polymetallic Nodules' (Manganese Nodules) found scattered on deep abyssal plains (such as the Central Indian Ocean Basin at depths of 4,000 to 6,000 m)?",
        "Potato-sized hydrogenous/diagenetic mineral concretions rich in manganese, iron, nickel, copper, and cobalt formed around a nucleus on the ocean floor",
        "Solid blocks of pure radioactive uranium discarded by nuclear submarines",
        "Petrified dinosaur eggs preserved under deep hydrostatic pressure",
        "Deposits of pure gold nuggets washed down by Himalayan rivers", "opt_a",
        "Polymetallic nodules are concentric mineral accretions growing at microscopic rates (few mm per million years) on abyssal plains, containing critical energy-transition metals: Manganese (~28%), Nickel (~1.3%), Copper (~1.1%), and Cobalt (~0.2%).",
        "Polymetallic Nodules = Deep abyssal accretions rich in Manganese, Nickel, Copper, and Cobalt. Regulated by ISA.",
        "Dinosaur Egg Trap"
    ),
    (
        "Under UNCLOS, the continental shelf of a coastal state may be extended beyond the standard 200 nautical miles up to a maximum limit of:",
        "350 Nautical Miles from the baseline (or 100 nautical miles beyond the 2,500-meter isobath), subject to verification by the Commission on the Limits of the Continental Shelf (CLCS)",
        "5,000 Nautical Miles covering the entire global ocean",
        "Strictly 205 Nautical Miles with zero further extension",
        "The mid-point of the nearest foreign continent's mountain range", "opt_a",
        "Under Article 76 UNCLOS, if a state proves its submerged continental margin physically extends beyond 200 nm, it can claim sovereign seabed rights over the 'Extended Continental Shelf' up to 350 nm (or 100 nm beyond the 2,500 m depth contour), approved by the CLCS.",
        "Extended Continental Shelf = Up to 350 nm from baseline (or 100 nm from 2,500m isobath). Approved by UN CLCS.",
        "No Extension Trap"
    ),
    (
        "The 'Circumpolar Deep Water' (CDW) in the Southern Ocean is a unique water mass characterized by being:",
        "A relatively warm and salty water mass sandwiched between cold Antarctic surface water and freezing Antarctic bottom water, upwelling along the Antarctic Divergence",
        "The freshest and sweetest drinking water body in the global ocean",
        "A boiling hydrothermal plume that maintains permanent tropical temperatures at the South Pole",
        "An isolated freshwater underground river flowing through sub-ice volcanic caverns", "opt_a",
        "CDW is an enormous volume of water in the Southern Ocean formed by the blending of North Atlantic Deep Water and other oceans, maintaining a temperature of ~1-2°C (warmer than overlying freezing surface water), upwelling to supply nutrients.",
        "Circumpolar Deep Water (CDW) = Warm, salty intermediate layer in Southern Ocean upwelling at Antarctic Divergence.",
        "Freshwater Myth Trap"
    ),
    (
        "In atmospheric dynamic meteorology, the 'Index Cycle' describes the periodic oscillation of the circumpolar westerly jet stream between:",
        "A high-index state (strong, straight zonal westerlies with little meridional exchange) and a low-index state (meandering, wavy Rossby waves with intense north-south thermal transfer and cut-off cyclones)",
        "A state of zero wind and a state of category 5 supersonic hurricanes",
        "Daily morning breezes and evening land breezes",
        "Seasonal solar flares and lunar gravitational eclipses", "opt_a",
        "The Index Cycle (lasting 3 to 6 weeks) transitions from: Stage 1 (High index, tight zonal flow), to Stages 2 and 3 (Rossby wave amplification and cellular loops), to Stage 4 (Low index, extreme meridional cut-off lows and highs with severe cold air outbreaks).",
        "Jet Stream Index Cycle: High Index (Straight Zonal, West-East) ↔ Low Index (Meandering Rossby Waves, North-South Heat Exchange).",
        "Diurnal Breeze Trap"
    ),
    (
        "In atmospheric thermodynamics, an air parcel is said to be in a state of 'Conditional Instability' when the Environmental Lapse Rate (ELR) is:",
        "Between the Saturated Adiabatic Lapse Rate (SALR) and the Dry Adiabatic Lapse Rate (DALR)",
        "Greater than the Dry Adiabatic Lapse Rate (DALR)",
        "Less than the Saturated Adiabatic Lapse Rate (SALR)",
        "Exactly zero degrees Celsius at all altitudes", "opt_a",
        "Conditional Instability occurs when SALR < ELR < DALR. The parcel is stable if unsaturated (cools faster than environment, sinks), but becomes unstable if forced to rise past its Level of Free Condensation (LFC), where latent heat release makes it warmer than the environment.",
        "Atmospheric Stability: Absolute Stability (ELR < SALR); Absolute Instability (ELR > DALR); Conditional Instability (SALR < ELR < DALR).",
        "Absolute Inversion Trap"
    ),
    (
        "Why do tropical cyclones require a minimum sea surface temperature (SST) of 26.5°C down to a depth of at least 50 meters to develop and sustain themselves?",
        "To provide a massive, continuous supply of latent heat of condensation released through moist convective updrafts, which powers the cyclone's thermal engine",
        "To allow ocean fish to swim faster into the storm core",
        "To melt deep-sea icebergs that would otherwise crush the storm",
        "Because salt crystals dissolve only above 26.5°C to create electric current", "opt_a",
        "Tropical cyclones operate as atmospheric Carnot heat engines. Warm ocean waters evaporate immense amounts of moisture into the boundary layer. As this air ascends and condenses in the eyewall, latent heat release drives pressure falls and cyclonic winds.",
        "Tropical Cyclones = SST >= 26.5°C down to 50m provides the latent heat engine powering convective updrafts.",
        "Electric Current Trap"
    )
]

for idx, (stem, a, b, c, d, ans, expl, mem, trap) in enumerate(medium_data, 16):
    q = {
        "id": f"opt_q30_{idx:02d}",
        "topicId": TOPIC_ID,
        "topicName": TOPIC_NAME,
        "section": SECTION,
        "tier": "Medium",
        "format": "Statement Based",
        "stem": stem,
        "options": {"opt_a": a, "opt_b": b, "opt_c": c, "opt_d": d},
        "correctAnswer": ans,
        "explanation": f"{expl}\n\n💡 RANKER'S MEMORY LOCK: {mem}",
        "distractorDissections": [
            {"optionId": "opt_b" if ans != "opt_b" else "opt_a", "trapType": trap, "dissection": "Distractor represents a different oceanic circulation mode or climatic phase."},
            {"optionId": "opt_c" if ans != "opt_c" else "opt_b", "trapType": "Concept Swap Trap", "dissection": "Do not swap the primary thermodynamic or oceanographic index with a secondary factor."},
            {"optionId": "opt_d" if ans != "opt_d" else "opt_c", "trapType": "Physical Inversion Trap", "dissection": "Avoid confusing high index with low index jet stream dynamics."}
        ]
    }
    questions.append(q)

# -----------------------------------------------------------------------------
# LEVEL 3: HARD / ADVANCED UPSC RANKER (Questions 36 to 60)
# Multi-statement modern count format ("How many of the above statements are correct?"),
# assertion-reasoning, and deep distractor traps
# -----------------------------------------------------------------------------
hard_stems = [
    (
        "Consider the following statements regarding the Bottom Relief of the Atlantic Ocean:\n1. The Mid-Atlantic Ridge divides the Atlantic into two deep parallel basins (Western and Eastern troughs).\n2. The Walvis Ridge branches off the Mid-Atlantic Ridge toward southwest Africa, blocking cold Antarctic bottom water from entering the Angola Basin.\n3. The Romanche Fracture Zone permits cold Antarctic deep water to cross from the western to eastern Atlantic across the equator.",
        "opt_c", "All three statements are correct representations of the bathymetry and hydrographic barriers of the Atlantic Ocean basin.", "All three"
    ),
    (
        "Consider the following statements regarding the Bottom Relief of the Indian Ocean:\n1. The Carlsberg Ridge extends northwestward from the Chagos archipelago toward the Gulf of Aden.\n2. The Ninety East Ridge is a 5,000-km continuous aseismic volcanic ridge running along the 90°E meridian.\n3. The Kerguelen Plateau in the southern Indian Ocean represents a massive submarine Large Igneous Province (LIP).",
        "opt_c", "All three statements accurately articulate major submarine morphological ridges of the Indian Ocean.", "All three"
    ),
    (
        "Consider the following statements regarding Pelagic Ocean Deposits:\n1. Calcareous oozes (Globigerina, Pteropod) dissolve completely below the Carbonate Compensation Depth (CCD, ~4,500m).\n2. Siliceous oozes (Diatom, Radiolarian) are insoluble in cold deep water and accumulate in high-latitude circumpolar belts and equatorial upwelling zones.\n3. Red Clay (Pelagic clay) covers the deepest abyssal floor (below 5,000m), composed of insoluble windblown dust, volcanic ash, and meteorite dust.",
        "opt_c", "All three statements represent verified physical and chemical oceanographic laws governing deep sea sediment deposition.", "All three"
    ),
    (
        "Consider the following statements regarding Atmospheric Stability and Lapse Rates:\n1. An air parcel is in 'Absolute Stability' when the Environmental Lapse Rate (ELR) is less than the Saturated Adiabatic Lapse Rate (SALR).\n2. An air parcel is in 'Absolute Instability' when the ELR is greater than the Dry Adiabatic Lapse Rate (DALR).\n3. 'Conditional Instability' occurs when the ELR lies between the SALR and the DALR.",
        "opt_c", "All three statements accurately define the thermodynamic stability criteria of the atmosphere (Strahler, Barry & Chorley).", "All three"
    ),
    (
        "Consider the following statements regarding Jacob Bjerknes's Polar Front Theory of Extratropical Cyclones:\n1. The incipient wave forms along the polar front separating warm subtropical maritime air from cold polar continental air.\n2. In the mature stage, a distinct warm sector exists between the advancing cold front and the retreating warm front.\n3. Occlusion occurs when the faster-moving cold front overtakes the warm front, lifting the warm air completely off the ground.",
        "opt_c", "All three statements accurately articulate the life cycle of temperate wave cyclones under the Bergen School model.", "All three"
    ),
    (
        "Consider the following statements regarding the Walker Circulation and ENSO:\n1. Under normal conditions, trade winds maintain a deep thermocline in the Western Pacific and a shallow thermocline with vigorous upwelling off Peru.\n2. During an El Niño event, the Southern Oscillation Index (SOI) is strongly negative, accompanied by positive SST anomalies in the central-eastern Pacific.\n3. During a La Niña event, trade winds intensify, pushing cold upwelling water far westward across the equatorial Pacific.",
        "opt_c", "All three statements reflect established physical oceanographic and atmospheric realities of the ENSO cycle.", "All three"
    ),
    (
        "Consider the following statements regarding the Indian Ocean Dipole (IOD):\n1. A Positive IOD features cooler-than-normal SSTs in the eastern equatorial Indian Ocean and warmer-than-normal SSTs in the western equatorial Indian Ocean.\n2. A Positive IOD typically enhances summer monsoon rainfall over India and often counteracts the drying effects of a concurrent El Niño.\n3. A Negative IOD brings unseasonably severe droughts and forest fires to eastern Australia and Indonesia.",
        "opt_b", "Statements 1 and 2 are correct. Statement 3 is incorrect because a Negative IOD brings unusually WET conditions and floods to Australia and Indonesia, while causing droughts in East Africa.", "Only two"
    ),
    (
        "Consider the following statements regarding C.W. Thornthwaite's 1948 Rational Classification of Climate:\n1. It calculates Potential Evapotranspiration (PET) using monthly mean temperatures and day-length latitude adjustments.\n2. The Moisture Index (Im) integrates both moisture surplus and moisture deficiency relative to water need (PET).\n3. When precipitation exceeds PET, soil moisture storage is recharged until field capacity is reached, after which water surplus generates river runoff.",
        "opt_c", "All three statements are correct representations of Thornthwaite's 1948 water balance bookkeeping accounting system.", "All three"
    ),
    (
        "Consider the following statements regarding Glenn Trewartha's World Climatic Classification:\n1. It is a modified, simplified empirical classification based on W.M. Koppen's system.\n2. It recognizes 6 major climatic groups: A (Tropical), B (Dry), C (Subtropical), D (Temperate), E (Boreal), and F (Polar).\n3. It requires that at least 8 months have mean temperatures of 10°C or above for a climate to be classified as Subtropical (C).",
        "opt_c", "All three statements accurately represent the structural taxonomy and criteria of Glenn Trewartha's climatic system.", "All three"
    ),
    (
        "Consider the following statements regarding Coral Reef Theories:\n1. Charles Darwin's Subsidence Theory requires continuous, slow tectonic subsidence of the oceanic volcanic foundation.\n2. Reginald Daly's Glacial Control Theory emphasizes sea-level fluctuations during the Pleistocene ice ages without requiring crustal subsidence.\n3. W.M. Davis supported Darwin's theory by demonstrating that embayed drowned valleys behind barrier reefs prove tectonic subsidence of the central island.",
        "opt_c", "All three statements are correct representations of the three primary competing and complementary geomorphic theories of coral reef development.", "All three"
    ),
    (
        "Consider the following statements regarding the Urban Heat Island (UHI) and Urban Microclimate:\n1. High thermal admittance and heat capacity of construction materials (concrete, brick, asphalt) store daytime insolation and release sensible heat slowly at night.\n2. Building geometry creates 'Urban Canyons' that reduce the sky view factor (SVF), trapping multiple-reflected longwave radiation.\n3. Urban vegetation increases the Bowen Ratio, causing urban temperatures to drop 10°C below surrounding forests.",
        "opt_b", "Statements 1 and 2 are correct. Statement 3 is completely false because urban areas have a HIGH Bowen Ratio (sensible heat dominates over latent heat due to lack of transpiring vegetation), which amplifies the heat island, NOT cools it.", "Only two"
    ),
    (
        "Consider the following statements regarding the Thermohaline Circulation (THC):\n1. The sinking of dense, cold, saline surface waters in the Norwegian, Greenland, and Labrador Seas forms North Atlantic Deep Water (NADW).\n2. The sinking of dense brine-enriched water in the Weddell and Ross Seas forms Antarctic Bottom Water (AABW).\n3. Influx of massive freshwater from melting Greenland glaciers could weaken or collapse the Atlantic Meridional Overturning Circulation (AMOC) by lowering surface salinity and inhibiting sinking.",
        "opt_c", "All three statements reflect established physical oceanographic and climate tipping point science.", "All three"
    ),
    (
        "Consider the following statements regarding the Madden-Julian Oscillation (MJO):\n1. It is an eastward-propagating tropical planetary wave of convective rainfall and winds with an intra-seasonal periodicity of 30 to 60 days.\n2. When the convective active phase of the MJO traverses the Indian Ocean, it triggers enhanced active spells of the Indian summer monsoon.\n3. When the suppressed dry phase of the MJO sits over the Indian Ocean, it can induce severe monsoon break spells.",
        "opt_c", "All three statements accurately articulate the operational teleconnection of the MJO with the Indian Monsoon intra-seasonal oscillations.", "All three"
    ),
    (
        "Consider the following statements regarding Deep-Sea Polymetallic Nodules:\n1. They are found predominantly on abyssal plains between 4,000 and 6,000 meters depth in areas of extremely low sedimentation rates.\n2. They contain high concentrations of strategic critical minerals: Manganese, Nickel, Copper, and Cobalt.\n3. India has been allocated a pioneer exploration area in the Central Indian Ocean Basin (CIOB) by the International Seabed Authority (ISA).",
        "opt_c", "All three statements are verified facts regarding polymetallic nodules and India's 'Deep Ocean Mission' under the ISA framework.", "All three"
    ),
    (
        "Consider the following statements regarding Maritime Baseline and Delimitation under UNCLOS:\n1. The 'Normal Baseline' is the low-water line along the coast as marked on large-scale charts officially recognized by the coastal state.\n2. 'Straight Baselines' may be drawn connecting appropriate points where the coastline is deeply indented or has a fringe of islands along its immediate vicinity.\n3. Waters on the landward side of the baseline are designated as 'Internal Waters', where foreign ships possess an automatic right of innocent passage without permission.",
        "opt_b", "Statements 1 and 2 are correct. Statement 3 is incorrect because in 'Internal Waters' (ports, bays, estuaries), foreign vessels have NO right of innocent passage without prior consent of the coastal state; innocent passage applies only in the Territorial Sea.", "Only two"
    ),
    (
        "Consider the following statements regarding Ocean Water Masses and Stratification:\n1. The ocean water column is generally divided into three layers: Surface Mixed Layer, Pycnocline (density gradient) / Thermocline (temperature gradient), and Deep Cold Layer.\n2. In tropical and subtropical oceans, a permanent thermocline exists year-round between 200m and 1,000m depth.\n3. In polar oceans, surface water is almost as cold as deep water, meaning the permanent thermocline is absent.",
        "opt_c", "All three statements accurately articulate the global physical stratification and thermocline structure of the oceans.", "All three"
    ),
    (
        "Consider the following statements regarding Jet Streams and the Index Cycle:\n1. Polar Front Jet Streams occur in the upper troposphere near the tropopause at altitudes of 9 to 12 km.\n2. In a 'Low Index' circulation pattern, wide-amplitude Rossby waves meander strongly north and south, transferring massive sensible heat and creating cut-off cyclones and anticyclones.\n3. In a 'High Index' circulation pattern, jet stream winds blow in a straight west-to-east zonal track, restricting north-south heat exchange.",
        "opt_c", "All three statements accurately describe the dynamic mechanics of the circumpolar westerly jet stream index cycle.", "All three"
    ),
    (
        "Consider the following statements regarding Tropical Cyclones and Wave Fronts:\n1. Tropical cyclones require warm ocean sea surface temperatures of at least 26.5°C to a depth of ~50 meters to supply latent heat of condensation.\n2. Unlike mid-latitude temperate cyclones, tropical cyclones are thermal engines that possess NO frontogenetic air mass fronts or occluded boundaries.\n3. Tropical cyclones can readily form directly on the equator (0°) because the Coriolis force is at its absolute maximum there.",
        "opt_b", "Statements 1 and 2 are correct. Statement 3 is false because the Coriolis force is ZERO at the equator, preventing the initiation of cyclonic spin; tropical cyclones form at least 5 degrees north or south of the equator.", "Only two"
    ),
    (
        "Consider the following statements regarding Ocean Water Salinity Distribution:\n1. The highest open-ocean surface salinities are found in the subtropical high-pressure belts (horse latitudes around 20° to 35° N/S) where high evaporation exceeds low precipitation.\n2. In the equatorial doldrums, surface salinity is lower despite warm temperatures due to heavy cloud cover, daily convective rainfall, and high humidity.\n3. The Baltic Sea exhibits extremely high surface salinity (>40 psu) due to permanent freezing.",
        "opt_b", "Statements 1 and 2 are correct. Statement 3 is incorrect because the Baltic Sea is a semi-enclosed brackish sea with extremely LOW salinity (<7-10 psu) due to massive freshwater river discharge and low evaporation.", "Only two"
    ),
    (
        "Consider the following statements regarding Thornthwaite's 1931 vs 1948 Climatic Classifications:\n1. The 1931 classification was empirical and utilized Precipitation Effectiveness (P/E) and Temperature Efficiency (T/E) indices.\n2. The 1948 classification was based on the rational concept of water balance, introducing Potential Evapotranspiration (PET) as the primary index of thermal efficiency.\n3. Both the 1931 and 1948 systems classify the world into identical boundaries that never differ from W.M. Koppen's map.",
        "opt_b", "Statements 1 and 2 are correct. Statement 3 is incorrect because Thornthwaite's boundaries diverge significantly from Koppen's, emphasizing water deficit and water surplus rather than simple raw vegetation biomes.", "Only two"
    ),
    (
        "Consider the following statements regarding the Earth's Planetary Heat Budget and Radiative Balance:\n1. The Earth's planetary albedo is approximately 30-31%, meaning nearly one-third of incoming solar insolation is reflected back to space without heating the earth.\n2. Low latitudes between 38°N and 38°S exhibit a net radiative surplus, while high polar latitudes exhibit a net radiative deficit.\n3. If atmospheric winds and oceanic currents did not transport heat poleward, the tropics would become progressively hotter and the poles progressively colder.",
        "opt_c", "All three statements accurately articulate the global radiative balance and meridional heat transfer necessary for climate stability.", "All three"
    ),
    (
        "Consider the following statements regarding Ekman Transport and Coastal Upwelling:\n1. Wind blowing across the ocean surface drives surface water 45° to the right of the wind in the Northern Hemisphere due to Coriolis deflection.\n2. The net water column transport (Ekman transport) moves at 90° to the right of the wind direction in the Northern Hemisphere.\n3. Along the coast of Peru, equatorward winds drive Ekman transport offshore (westward), forcing cold, nutrient-rich deep water to upwell along the coast.",
        "opt_c", "All three statements are correct representations of V. Walfrid Ekman's wind-driven ocean circulation theory and upwelling dynamics.", "All three"
    ),
    (
        "Consider the following statements regarding Coral Bleaching and Marine Heatwaves:\n1. Coral bleaching occurs when heat-stressed corals expel their symbiotic endosymbiotic dinoflagellates (zooxanthellae).\n2. Corals derive up to 90% of their metabolic energy requirements from photosynthetic products provided by zooxanthellae.\n3. Ocean acidification enhances calcification rates, allowing bleached corals to rebuild calcium carbonate skeletons twice as fast.",
        "opt_b", "Statements 1 and 2 are correct. Statement 3 is false because ocean acidification reduces carbonate ion concentrations, hindering and dissolving coral calcification skeletons rather than accelerating them.", "Only two"
    ),
    (
        "Consider the following statements regarding Atmospheric Frontogenesis and Frontolysis:\n1. Frontogenesis is the process of creating or intensifying a horizontal temperature gradient in the atmosphere.\n2. Kinematic deformation fields (stretching and shearing of air parcels) with confluence along the axis of dilatation are primary dynamic drivers of frontogenesis.\n3. Frontolysis occurs when divergent wind fields or turbulent mixing destroy the horizontal temperature gradient across a frontal zone.",
        "opt_c", "All three statements accurately describe the Bergeron-Petterssen kinematic theory of frontogenesis and frontolysis.", "All three"
    ),
    (
        "Consider the following statements regarding Global Climate Change and Ocean-Atmosphere Feedbacks in the Anthropocene:\n1. Over 90% of the excess heat accumulated in the Earth system due to anthropogenic greenhouse gas emissions has been absorbed by the global oceans.\n2. Thermal expansion of warming ocean water and continental glacier/ice-sheet melt are the two dominant contributors to global mean sea-level rise.\n3. Ocean deoxygenation occurs as warmer surface waters hold less dissolved oxygen and increased stratification reduces vertical ocean ventilation.",
        "opt_c", "All three statements represent verified physical findings of the IPCC Sixth Assessment Report (AR6) regarding oceanic responses to climate warming.", "All three"
    )
]

for idx, (stem, ans, expl, count_text) in enumerate(hard_stems, 36):
    q = {
        "id": f"opt_q30_{idx:02d}",
        "topicId": TOPIC_ID,
        "topicName": TOPIC_NAME,
        "section": SECTION,
        "tier": "Hard",
        "format": "Modern Count",
        "stem": stem + "\nHow many of the statements given above are correct?",
        "options": {
            "opt_a": "Only one",
            "opt_b": "Only two",
            "opt_c": "All three",
            "opt_d": "None"
        },
        "correctAnswer": ans,
        "explanation": f"{expl}\n\n💡 RANKER'S MEMORY LOCK: {count_text} statements correct. Examine operational assumptions and physical mechanisms.",
        "distractorDissections": [
            {"optionId": "opt_a" if ans != "opt_a" else "opt_b", "trapType": "Under-count Trap", "dissection": "Verify individual statement veracity before tallying count."},
            {"optionId": "opt_c" if ans != "opt_c" else "opt_a", "trapType": "Total Acceptance Trap", "dissection": "UPSC frequently flips an equatorial Coriolis parameter, acidification effect, or internal waters right."},
            {"optionId": "opt_d" if ans != "opt_d" else "opt_b", "trapType": "Total Rejection Trap", "dissection": "Do not over-eliminate authentic canonical oceanographic and climatological laws."}
        ]
    }
    questions.append(q)

output_path = os.path.join(r"c:\Users\harsh\Downloads\tayaari\cloud_data_staging\topics", f"topic_{TOPIC_ID}.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print(f"Successfully generated exactly {len(questions)} questions for Topic {TOPIC_ID}.")
