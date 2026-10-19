package com.example.ui.components

import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.example.ui.theme.*

enum class AtlasSheetCategory(val title: String, val icon: String) {
    KOPPEN("Koppen Climate", "🌦️"),
    RIVERS("River Drainage", "🌊"),
    SEISMIC("Earth Interior", "🌋"),
    SOILS("Soil Orders", "🌱"),
    CURRENTS("Ocean Currents", "🌊"),
    PASSES("Mountain Passes", "⛰️"),
    RAMSAR("Ramsar & Parks", "🦏")
}

data class AtlasMatrixEntry(
    val codeOrName: String,
    val title: String,
    val geographicRegion: String,
    val examMnemonicKey: String,
    val highYieldTrap: String
)

@Composable
fun CartographicAtlasSheetDialog(
    onDismissRequest: () -> Unit
) {
    var selectedCategory by remember { mutableStateOf(AtlasSheetCategory.KOPPEN) }
    var searchQuery by remember { mutableStateOf("") }
    val fontScale = LocalFontScale.current

    val koppenEntries = remember {
        listOf(
            AtlasMatrixEntry("Amw", "Monsoon with Short Dry Winter", "Malabar Coast, Konkan, Western Ghats windward, Goa", "Amw = Malabar Wet monsoon", "High rainfall (>200cm); dry season is short winter."),
            AtlasMatrixEntry("As", "Monsoon with Dry Summer", "Coromandel Coast (Coastal Tamil Nadu & parts of AP)", "As = Autumn Shower / Dry Summer", "TRAP: Receives peak rainfall in Nov-Dec from Northeast Monsoon, not summer!"),
            AtlasMatrixEntry("Aw", "Tropical Savanna (Wet & Dry)", "Most of Peninsular Plateau south of Tropic of Cancer", "Aw = All-plateau Winter dry", "Distinct dry winter; deciduous teak and sal forests."),
            AtlasMatrixEntry("BShw", "Semi-Arid Steppe Climate", "Rain shadow Western Ghats, Haryana, Western Punjab, parts of Rajasthan", "BShw = Steppe Semi-arid", "Rainfall 30-75cm; thorny shrubs and acacia."),
            AtlasMatrixEntry("BWhw", "Hot Desert Climate", "Thar Desert, Western Rajasthan (Jaisalmer, Bikaner)", "BWhw = Whole desert Waste", "Rainfall <30cm; intense evapotranspiration, xerophytes."),
            AtlasMatrixEntry("Cwg", "Monsoon with Dry Winter (Ganga)", "Northern Ganga Plains, UP, Bihar, Assam, Bengal", "Cwg = Gangetic Plain (g = gangetic temperature curve)", "Warmest month occurs in May BEFORE summer solstice rains."),
            AtlasMatrixEntry("Dfc", "Cold Humid Winter Short Summer", "Arunachal Pradesh, Sikkim, upper Eastern Himalayas", "Dfc = Far eastern Cold", "High humidity, coniferous pine forests, harsh winters."),
            AtlasMatrixEntry("ET", "Tundra / Polar Alpine", "High Himalayas, Ladakh, Zanskar, Karakoram ranges", "ET = Extreme Tundra", "Permafrost, sparse lichens, short freezing summers.")
        )
    }

    val riverEntries = remember {
        listOf(
            AtlasMatrixEntry("Ganga", "Ganga Basin Tributaries", "Left: Ramganga, Gomti, Ghaghara, Gandak, Kosi, Mahananda | Right: Yamuna, Son, Punpun, Damodar", "Left bank all start north of Ganga from Himalayas (except Gomti in plains); Right bank join from south.", "Kosi is known as Sorrow of Bihar due to dynamic channel avulsion shifting westward 120km."),
            AtlasMatrixEntry("Indus", "Indus System Tributaries", "Left (Panjnad): Zanskar, Suru, Jhelum, Chenab, Ravi, Beas, Sutlej | Right: Shyok, Gilgit, Hunza, Swat, Kabul, Kurram, Gomal", "North to South Panjnad order: Indus -> Jhelum -> Chenab -> Ravi -> Beas -> Sutlej", "Chenab is the largest tributary of Indus in India; Beas lies entirely within India."),
            AtlasMatrixEntry("Brahmaputra", "Brahmaputra (Tsangpo)", "Left: Dibang, Lohit, Burhi Dihing, Dhansiri | Right: Subansiri, Kameng, Manas, Sankosh, Teesta", "Teesta was historically a tributary of Ganga, shifted to Brahmaputra after the 1787 floods.", "Enters India through Arunachal Pradesh as Siang/Dihang; cuts the grand Namcha Barwa syntaxis."),
            AtlasMatrixEntry("Godavari", "Dakshin Ganga (Longest Peninsular)", "Left: Penganga, Wardha, Wainganga (Pranhita), Indravati, Sabari | Right: Pravara, Mula, Manjra", "Pranhita (Penganga + Wardha + Wainganga) is the largest tributary by discharge.", "Manjra flows northwards from Maharashtra/Karnataka border as a right-bank tributary."),
            AtlasMatrixEntry("Krishna", "Krishna Basin", "Left: Bhima, Dindi, Musi, Munneru | Right: Koyna, Panchganga, Dudhganga, Ghataprabha, Malaprabha, Tungabhadra", "Tungabhadra is formed by the confluence of Tunga and Bhadra at Koodli.", "Musi river flows through Hyderabad; Koyna is famous for reservoir-induced seismicity (1967).")
        )
    }

    val seismicEntries = remember {
        listOf(
            AtlasMatrixEntry("C", "Conrad Discontinuity (~15-20 km)", "Upper Continental Crust (Sial) vs Lower Continental Crust (Sima)", "C-M-R-G-L: Conrad is outermost", "Only found in continental crust; absent in oceanic crust."),
            AtlasMatrixEntry("M", "Mohorovičić (Moho) (~35 km)", "Crust vs Upper Mantle (Asthenosphere boundary)", "C-M-R-G-L: Moho separates crust & mantle", "Depth is ~35-70 km under mountain chains (Himalayas) but only ~5-10 km under oceanic crust."),
            AtlasMatrixEntry("R", "Repetti Discontinuity (~700 km)", "Upper Mantle (Asthenosphere) vs Lower Mantle (Mesosphere)", "C-M-R-G-L: Repetti divides mantle layers", "Marks transition where mantle silicates rearrange into high-density perovskite structure."),
            AtlasMatrixEntry("G", "Gutenberg Discontinuity (~2,900 km)", "Lower Mantle vs Outer Core", "C-M-R-G-L: Gutenberg = Core boundary", "S-waves completely disappear here because the outer core is molten iron-nickel! Creates S-wave shadow zone (105°-105°)."),
            AtlasMatrixEntry("L", "Lehmann Discontinuity (~5,150 km)", "Outer Molten Core vs Inner Solid Core", "C-M-R-G-L: Lehmann = Deepest core center", "Inner core is solid iron-nickel despite temperatures exceeding 5,400°C due to colossal pressure (3.6 million atm).")
        )
    }

    val soilEntries = remember {
        listOf(
            AtlasMatrixEntry("Inceptisols", "Embryonic / Young Soils (39.7%)", "Alluvial plains of North India, deltas, coastal tracts", "Largest Soil Order in India by area!", "Weakly developed B-horizon; high fertility when renewed by river alluvium."),
            AtlasMatrixEntry("Entisols", "Undeveloped Profile Soils (28.1%)", "Flood plains, active flood deposits, sandy riverine tracts, dunes", "Second largest order; zero B-horizon", "Includes newly laid Khadar soils; lack distinct pedogenic genetic horizons."),
            AtlasMatrixEntry("Alfisols", "Weathered Forest / Red Soils (13.5%)", "Tamil Nadu, Karnataka, Southern Odisha, Chota Nagpur plateau", "Clay accumulation in B-horizon; base saturation >35%", "Rich in iron and aluminum oxides; responsive to chemical fertilizers."),
            AtlasMatrixEntry("Vertisols", "Black Cotton Soil / Regur (8.5%)", "Deccan Traps (Maharashtra, Malwa, Saurashtra, Northern Karnataka)", "Montmorillonite clay; High Swell-Shrink self-ploughing", "Develops deep fissures in summer; sticky when wet, retaining moisture for dry-season cotton."),
            AtlasMatrixEntry("Aridisols", "Desert / Calcareous Soils (4.3%)", "Western Rajasthan (Thar), Southern Punjab, Rann of Kutch", "Kankar (calcium carbonate) sub-horizon", "High capillary evaporation causes salinization; fertile under drip/canal irrigation.")
        )
    }

    val currentEntries = remember {
        listOf(
            AtlasMatrixEntry("Labrador & Gulf Stream", "North Atlantic Gyre", "Labrador (Cold) southward meets Gulf Stream (Warm) northward at Newfoundland", "Grand Banks fog & world's premier cod fishing grounds", "Meeting of warm and cold currents stimulates phytoplankton bloom but causes hazardous navigational fogs."),
            AtlasMatrixEntry("Benguela & Agulhas", "South Atlantic & Indian Ocean", "Benguela (Cold) flows along Namibia/South Africa coast; Agulhas (Warm) along east coast", "Benguela chills air creating Namib desert stability", "Cold offshore currents create trade-wind coastal deserts (Namib, Atacama, Sahara)."),
            AtlasMatrixEntry("Kuroshio & Oyashio", "North Pacific Gyre", "Kuroshio (Warm) northward meets Oyashio/Kuril (Cold) southward near Hokkaido Japan", "Pacific equivalent of Gulf Stream / Labrador confluence", "Oyashio is nutrient-rich Subarctic water; Kuroshio is warm tropical water."),
            AtlasMatrixEntry("Peru (Humboldt)", "South Pacific (Cold Current)", "Flows northwards along Chile & Peru; upwelling nutrients support anchovy fishery", "Weakens during El Niño, triggering global climatic anomalies", "El Niño warms the Peruvian coast, collapsing the cold Humboldt upwelling and suppressing Indian monsoon."),
            AtlasMatrixEntry("West Australian", "South Indian Ocean (Cold Current)", "Flows northward along western coast of Australia", "Responsible for the Great Sandy & Gibson deserts", "Only major cold ocean current in the southern Indian Ocean gyre.")
        )
    }

    val passEntries = remember {
        listOf(
            AtlasMatrixEntry("Zoji La", "Zaskar / Greater Himalayas (3,528 m)", "Connects Srinagar with Kargil and Leh (Ladakh)", "Zoji La = Zero winter travel without tunnel; NH-1D gateway", "Situated on the Zaskar range; historic battlefield of Operation Bison (1948)."),
            AtlasMatrixEntry("Shipki La", "Himachal Pradesh - Tibet Border (3,930 m)", "Kinnaur district, HP; River Sutlej enters India through this gorge", "Shipki = Sutlej highway into India", "Tributary gorge of Sutlej; ancient silk route spur to Tibet."),
            AtlasMatrixEntry("Nathu La & Jelep La", "Sikkim - Tibet Border", "Nathu La (Dongkya Range) & Jelep La (Chumbi Valley route)", "Nathu La = Reopened border trade post (2006); Jelep La = Passes through Chumbi Valley", "Strategic bottleneck close to Siliguri Corridor (Chicken's Neck)."),
            AtlasMatrixEntry("Lipulekh", "Uttarakhand (Pithoragarh) - Tibet Tri-junction", "Connects Kumaon with Purang (Tibet); Kailash-Mansarovar Yatra", "Lipulekh = Pilgrimage gateway at Kalapani tri-junction", "Located near the Kali river source; dispute point in Indo-Nepal cartography."),
            AtlasMatrixEntry("Rohtang & Atal Tunnel", "Pir Panjal Range, HP (3,978 m)", "Connects Kullu Valley with Lahaul and Spiti Valleys", "Rohtang = Pile of corpses; bypassed by world's longest highway tunnel >10,000 ft (Atal Tunnel)", "Separates the Chenab and Beas drainage basins in Himachal Pradesh."),
            AtlasMatrixEntry("Bomdi La", "Arunachal Pradesh (Himalayas)", "Connects Tezpur/Assam with Tawang near Bhutan border", "Bomdi La = Gateway to Tawang Monastery", "Strategic pass crossing Greater Himalayas into Tibetan plateau."),
            AtlasMatrixEntry("Thal & Bhor Ghat", "Western Ghats (Sahyadris), Maharashtra", "Thal Ghat (Kasara): Mumbai-Nashik-Kolkata | Bhor Ghat: Mumbai-Pune-Chennai", "Thal = Northbound to Nashik; Bhor = Southbound to Pune", "Historic rail inclines conquering the steep Sahyadri scarp."),
            AtlasMatrixEntry("Palghat Gap", "Western Ghats Break (Kerala-Tamil Nadu)", "Connects Palakkad (Kerala) with Coimbatore (Tamil Nadu)", "Palghat = 30-40 km wide tectonic shear gap between Nilgiris & Anamalai", "Crucial break allowing Arabian Sea monsoon clouds to penetrate interior Tamil Nadu; vital rail/road freight corridor.")
        )
    }

    val ramsarEntries = remember {
        listOf(
            AtlasMatrixEntry("Loktak Lake", "Manipur (Montreux Record Ramsar)", "Keibul Lamjao National Park (World's only floating national park)", "Loktak = Floating Phumdis (heterogeneous organic mats)", "Home to endangered Sangai (Dancing Brow-antlered deer); plagued by siltation and hydel dams."),
            AtlasMatrixEntry("Keoladeo Ghana", "Rajasthan (Bharatpur) (Montreux Record)", "Confluence of Gambhir and Banganga rivers", "Keoladeo = Artificial man-made wetland built by Maharaja Suraj Mal", "Wintering ground for endangered Siberian Crane; placed on Montreux Record due to water shortages."),
            AtlasMatrixEntry("Chilika Lake", "Odisha Coast (First Indian Ramsar Site 1981)", "Asia's largest brackish water lagoon; Daya river mouth", "Chilika = Successfully removed from Montreux Record after opening new sea mouth", "Home to endangered Irrawaddy Dolphins (Orcaella brevirostris) and Nalabana Bird Sanctuary."),
            AtlasMatrixEntry("Kabartal / Kanwar", "Begusarai, Bihar (Ramsar Site #39)", "North Gangetic Plain oxbow lake formed by Gandak river migration", "Kabartal = Bihar's premier freshwater wetland", "Vital stopover on Central Asian Flyway; critically endangered vultures (White-rumped, Indian)."),
            AtlasMatrixEntry("Vembanad-Kol", "Kerala (Longest Lake in India)", "Ramsar wetland fed by Pamba, Periyar, Meenachil, Achankovil, Manimala rivers", "Vembanad = Divided into salt and fresh zones by Thanneermukkom barrage", "Threatened by reclamation; venue of the famous Nehru Trophy Snake Boat Race (Vallam Kali)."),
            AtlasMatrixEntry("Deepor Beel", "Kamrup, Assam (Brahmaputra Valley)", "Permanent freshwater lake in former channel of Brahmaputra", "Deepor Beel = Only Ramsar site in Assam; elephant foraging sanctuary", "Critical urban wetland bordering Guwahati; threatened by municipal dumping.")
        )
    }

    val activeEntries = when (selectedCategory) {
        AtlasSheetCategory.KOPPEN -> koppenEntries
        AtlasSheetCategory.RIVERS -> riverEntries
        AtlasSheetCategory.SEISMIC -> seismicEntries
        AtlasSheetCategory.SOILS -> soilEntries
        AtlasSheetCategory.CURRENTS -> currentEntries
        AtlasSheetCategory.PASSES -> passEntries
        AtlasSheetCategory.RAMSAR -> ramsarEntries
    }

    val filteredEntries = remember(searchQuery, activeEntries) {
        if (searchQuery.isBlank()) activeEntries
        else {
            val q = searchQuery.trim().lowercase()
            activeEntries.filter {
                it.codeOrName.lowercase().contains(q) ||
                it.title.lowercase().contains(q) ||
                it.geographicRegion.lowercase().contains(q) ||
                it.examMnemonicKey.lowercase().contains(q) ||
                it.highYieldTrap.lowercase().contains(q)
            }
        }
    }

    Dialog(
        onDismissRequest = onDismissRequest,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(0.95f)
                .fillMaxHeight(0.90f)
                .clip(RoundedCornerShape(20.dp))
                .background(MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                // Header Row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("📐", fontSize = 22.sp)
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Text(
                                text = "High-Yield Cartographic Atlas Matrix",
                                fontFamily = CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                color = SunstoneGold,
                                fontSize = (16 * fontScale).sp
                            )
                            Text(
                                text = "RAPID MEMORY ANCHORS // ZERO-SPOILER REFERENCE",
                                fontFamily = CoordinatesMonospace,
                                fontSize = (9.5 * fontScale).sp,
                                color = HydrosphereCyan,
                                letterSpacing = 0.8.sp
                            )
                        }
                    }

                    IconButton(onClick = onDismissRequest, modifier = Modifier.size(32.dp)) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Close",
                            tint = MaterialTheme.colorScheme.onSurface
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Search Bar
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    placeholder = {
                        Text(
                            "Filter by code, tributary, order or region...",
                            fontSize = (12 * fontScale).sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    },
                    leadingIcon = {
                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = "Search",
                            tint = SunstoneGold,
                            modifier = Modifier.size(18.dp)
                        )
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedContainerColor = MaterialTheme.colorScheme.surfaceVariant,
                        unfocusedContainerColor = MaterialTheme.colorScheme.surfaceVariant,
                        focusedBorderColor = SunstoneGold,
                        unfocusedBorderColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.5f),
                        focusedTextColor = MaterialTheme.colorScheme.onSurface,
                        unfocusedTextColor = MaterialTheme.colorScheme.onSurface
                    ),
                    singleLine = true
                )

                Spacer(modifier = Modifier.height(10.dp))

                // Category Chips (Horizontal Scroll)
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    AtlasSheetCategory.entries.forEach { cat ->
                        val isSelected = cat == selectedCategory
                        Surface(
                            color = if (isSelected) SunstoneGold else MaterialTheme.colorScheme.surfaceVariant,
                            shape = RoundedCornerShape(8.dp),
                            border = BorderStroke(
                                1.dp,
                                if (isSelected) SunstoneGold else MaterialTheme.colorScheme.outline.copy(alpha = 0.4f)
                            ),
                            modifier = Modifier.clickable {
                                selectedCategory = cat
                                searchQuery = ""
                            }
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(cat.icon, fontSize = 12.sp)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = cat.title,
                                    color = if (isSelected) Color.Black else MaterialTheme.colorScheme.onSurface,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = (11.5 * fontScale).sp
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Entry List
                if (filteredEntries.isEmpty()) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text(
                            text = "No atlas records matching '$searchQuery'",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            fontSize = (13 * fontScale).sp
                        )
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        items(filteredEntries, key = { it.codeOrName }) { item ->
                            AtlasMatrixCard(item = item, fontScale = fontScale)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun AtlasMatrixCard(item: AtlasMatrixEntry, fontScale: Float) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.4f))
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    color = ContourEmerald.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(6.dp),
                    border = BorderStroke(0.8.dp, ContourEmerald.copy(alpha = 0.5f))
                ) {
                    Text(
                        text = item.codeOrName,
                        color = ContourEmerald,
                        fontWeight = FontWeight.Black,
                        fontFamily = CoordinatesMonospace,
                        fontSize = (12.5 * fontScale).sp,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                    )
                }

                Text(
                    text = item.title,
                    color = SunstoneGold,
                    fontWeight = FontWeight.Bold,
                    fontSize = (12 * fontScale).sp
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Geographic Region
            Text(
                text = "📍 Spatial Coverage: ${item.geographicRegion}",
                color = MaterialTheme.colorScheme.onSurface,
                fontSize = (11.5 * fontScale).sp,
                lineHeight = (16 * fontScale).sp
            )

            Spacer(modifier = Modifier.height(6.dp))

            // Mnemonic Anchor
            Surface(
                color = HydrosphereCyan.copy(alpha = 0.10f),
                shape = RoundedCornerShape(6.dp),
                border = BorderStroke(0.6.dp, HydrosphereCyan.copy(alpha = 0.35f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "🧠 Memory Anchor: ${item.examMnemonicKey}",
                    color = HydrosphereCyan,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = (11 * fontScale).sp,
                    modifier = Modifier.padding(8.dp)
                )
            }

            Spacer(modifier = Modifier.height(6.dp))

            // High-Yield Trap Dissection
            Text(
                text = "⚠️ Exam Trap: ${item.highYieldTrap}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                fontSize = (11 * fontScale).sp,
                lineHeight = (15 * fontScale).sp
            )
        }
    }
}
