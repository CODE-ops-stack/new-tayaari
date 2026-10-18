#!/usr/bin/env python3
"""Exhaustive NCERT Geography Key Term Audit across Topics 1 to 23."""
import json, os

STAGING = r'C:\Users\harsh\Downloads\tayaari\cloud_data_staging\topics'

EXHAUSTIVE_NCERT_MAP = {
    1: ('Universe & Solar System', [
        'nebular hypothesis', 'planetesimal', 'big bang', 'singularity', 'edwin hubble',
        'aphelion', 'perihelion', 'summer solstice', 'winter solstice', 'equinox',
        'circle of illumination', 'coriolis', 'sidereal day', 'solar day', 'light year',
        'terrestrial planets', 'jovian planets', 'kuiper belt', 'oort cloud', 'asteroid belt'
    ]),
    2: ('Globe & Coordinates', [
        'great circle', 'small circle', 'prime meridian', 'international date line',
        'antipode', 'rhumb line', 'loxodrome', 'local time', 'standard time',
        'indian standard time', 'greenwich', 'time zone', 'latitudinal extent', 'longitudinal extent'
    ]),
    3: ('Maps, Projections & GIS', [
        'representative fraction', 'contour line', 'contour interval', 'cylindrical projection',
        'mercator', 'conical projection', 'zenithal projection', 'azimuthal', 'gnomonic',
        'stereographic', 'orthographic', 'remote sensing', 'gis', 'dem', 'spectral resolution'
    ]),
    4: ('Earth Interior & Plate Tectonics', [
        'conrad discontinuity', 'mohorovicic', 'repetti', 'gutenberg', 'lehmann',
        'asthenosphere', 'lithosphere', 'p-wave shadow zone', 's-wave shadow zone',
        'paleomagnetism', 'seafloor spreading', 'benioff zone', 'subduction', 'mid-oceanic ridge',
        'batholith', 'laccolith', 'lopolith', 'phacolith', 'sill', 'dyke', 'ophiolite', 'continental drift'
    ]),
    5: ('Geomorphic Processes & Landforms', [
        'diastrophism', 'orogenic', 'epeirogenic', 'exfoliation', 'carbonation', 'hydration',
        'solifluction', 'mass wasting', 'peneplain', 'pediplain', 'monadnock', 'ox-bow lake',
        'meander', 'pothole', 'plunge pool', 'stalactite', 'stalagmite', 'sinkhole', 'doline',
        'uvala', 'polje', 'lapies', 'cirque', 'arete', 'horn', 'drumlin', 'esker', 'kame',
        'moraine', 'fiord', 'barchan', 'seif', 'yardang', 'zeugen', 'pediment', 'bajada',
        'playa', 'inselberg', 'tombolo', 'spit', 'wave-cut platform'
    ]),
    6: ('Atmosphere & Climate', [
        'insolation', 'solar constant', 'albedo', 'normal lapse rate', 'temperature inversion',
        'coriolis force', 'geostrophic wind', 'hadley cell', 'ferrel cell', 'polar cell',
        'itcz', 'doldrums', 'horse latitudes', 'rossby waves', 'jet stream', 'foehn', 'chinook',
        'sirocco', 'mistral', 'harmattan', 'frontogenesis', 'frontolysis', 'cold front',
        'warm front', 'occluded front', 'extra-tropical cyclone', 'tropical cyclone', 'eye of cyclone'
    ]),
    7: ('Oceanography', [
        'continental shelf', 'continental slope', 'continental rise', 'abyssal plain',
        'submarine canyon', 'guyot', 'seamount', 'mid-oceanic ridge', 'thermocline',
        'halocline', 'pycnocline', 'isohaline', 'spring tide', 'neap tide', 'syzygy',
        'quadrature', 'apogee', 'perigee', 'upwelling', 'kuroshio', 'oyashio', 'gulf stream',
        'labrador', 'benguela', 'humboldt', 'sargasso sea', 'great barrier reef'
    ]),
    8: ('Biogeography & Ecosystems', [
        'biome', 'trophic level', 'ecological pyramid', 'pyramid of numbers', 'pyramid of biomass',
        'pyramid of energy', '10% law', 'hydrarch', 'xerarch', 'sere', 'pioneer species',
        'climax community', 'nitrogen cycle', 'phosphorus cycle', 'carbon cycle',
        'biodiversity hotspot', 'norman myers', 'endemic species', 'alpha diversity', 'beta diversity'
    ]),
    9: ('India Location & Neighbours', [
        'standard meridian', '82°30', 'tropic of cancer', 'radcliffe line', 'mcmahon line',
        'durand line', 'ten degree channel', 'nine degree channel', 'eight degree channel',
        'duncan passage', 'great channel', 'coco channel', 'sir creek', 'siliguri corridor',
        'indira point', 'kanyakumari', 'kibithu', 'gughar moti'
    ]),
    10: ('Physiography of India', [
        'himadri', 'himachal', 'shiwalik', 'trans-himalaya', 'pir panjal', 'dhauladhar',
        'bhabar', 'terai', 'bhangar', 'khadar', 'karewa', 'dun', 'duar', 'malda fault',
        'garo-rajmahal gap', 'deccan trap', 'thal ghat', 'bhor ghat', 'palghat', 'shencottah',
        'anamudi', 'doddabetta', 'barren island', 'narcondam', 'vembanad', 'chilika'
    ]),
    11: ('Drainage System of India', [
        'antecedent drainage', 'superimposed drainage', 'dendritic pattern', 'trellis pattern',
        'radial pattern', 'centripetal pattern', 'water divide', 'panch prayag', 'devprayag',
        'rudraprayag', 'karnaprayag', 'nandaprayag', 'vishnuprayag', 'indus water treaty',
        'majuli', 'brahmaputra', 'narmada rift valley', 'tapi rift valley', 'godavari', 'krishna',
        'kaveri', 'mahanadi', 'hirakud'
    ]),
    12: ('Indian Climate & Monsoon', [
        'southwest monsoon', 'northeast monsoon', 'break in the monsoon', 'tibetan plateau',
        'tropical easterly jet', 'somali jet', 'findlater jet', 'el nino', 'la nina', 'enso',
        'southern oscillation', 'indian ocean dipole', 'madden-julian oscillation',
        'western disturbance', 'kalbaisakhi', 'bardoli chheerha', 'mango shower', 'blossom shower',
        'koppen', 'amw', 'as', 'aw', 'cwg', 'dfc', 'bshw', 'bwhw', 'et'
    ]),
    13: ('Soils & Natural Vegetation of India', [
        'icar', 'alluvial soil', 'black soil', 'regur', 'self-ploughing', 'laterite', 'leaching',
        'red and yellow soil', 'saline soil', 'usar', 'kallar', 'peaty soil', 'kari',
        'inceptisols', 'vertisols', 'alfisols', 'entisols', 'sheet erosion', 'gully erosion',
        'chambal ravines', 'champion and seth', 'tropical wet evergreen', 'tropical moist deciduous',
        'tropical dry deciduous', 'thorn forest', 'shola', 'pneumatophore', 'vivipary', 'sundari'
    ]),
    14: ('Wildlife & Conservation', [
        'biosphere reserve', 'man and biosphere', 'national park', 'wildlife sanctuary',
        'community reserve', 'conservation reserve', 'ramsar site', 'montreux record',
        'project tiger', 'project elephant', 'mike site', 'wildlife protection act',
        'iucn red list', 'critically endangered', 'kaziranga', 'keibul lamjao', 'silent valley'
    ]),
    15: ('Agriculture', [
        'kharif', 'rabi', 'zaid', 'subsistence farming', 'intensive subsistence',
        'plantation agriculture', 'shifting cultivation', 'jhum', 'system of rice intensification',
        'direct seeded rice', 'shree anna', 'millets', 'minimum support price', 'cacp',
        'crop combination', 'weaver', 'agro-climatic zones', 'planning commission'
    ]),
    16: ('Water Resources & Dams', [
        'groundwater extraction', 'central ground water board', 'watershed management',
        'haryali', 'neeru-meeru', 'arvari pani sansad', 'khadin', 'johad', 'national waterways',
        'nw-1', 'nw-2', 'river inter-linking', 'ken-betwa', 'bhakra nangal', 'sardar sarovar',
        'tehri dam', 'micro-irrigation', 'pmksy', 'atal bhujal yojana'
    ]),
    17: ('Minerals & Energy', [
        'haematite', 'magnetite', 'bauxite', 'monazite', 'thorium', 'rare earth elements',
        'gondwana coal', 'tertiary coal', 'digboi', 'mumbai high', 'kg basin', 'bailadila',
        'kudremukh', 'khetri', 'koderma', 'panchpatmali', 'jaduguda', 'amjhor'
    ]),
    18: ('Industries', [
        'alfred weber', 'least cost theory', 'material index', 'agglomeration economies',
        'footloose industry', 'tisco', 'iisco', 'bhilai', 'rourkela', 'durgapur', 'bokaro',
        'visakhapatnam steel', 'salem steel', 'sugar industry migration', 'petrochemical complex',
        'industrial corridor', 'dmic', 'sez'
    ]),
    19: ('Transport & Trade', [
        'golden quadrilateral', 'north-south corridor', 'east-west corridor', 'bharatmala',
        'sagarmala', 'dedicated freight corridor', 'deendayal port', 'kandla', 'jnpt',
        'nhava sheva', 'mormugao', 'new mangalore', 'cochin port', 'v.o. chidambaranar',
        'chennai port', 'kamarajar port', 'visakhapatnam port', 'paradip', 'syama prasad mookerjee port'
    ]),
    20: ('Population & Settlements', [
        'demographic transition theory', 'notestein', 'crude birth rate', 'crude death rate',
        'natural growth rate', 'sex ratio', 'child sex ratio', 'density of population',
        'clustered settlement', 'semi-clustered', 'hamleted settlement', 'dispersed settlement',
        'panna', 'para', 'nagla', 'dhani', 'conurbation', 'patrick geddes', 'megalopolis',
        'jean gottmann', 'primate city', 'mark jefferson'
    ]),
    21: ('Human Development & Economic Models', [
        'human development index', 'mahbub ul haq', 'amartya sen', 'multidimensional poverty index',
        'gender inequality index', 'primary activities', 'secondary activities', 'tertiary activities',
        'quaternary activities', 'quinary activities', 'red collar', 'blue collar', 'white collar',
        'gold collar', 'von thunen', 'isolated state', 'rostow stages of growth'
    ]),
    22: ('World Regional Geography', [
        'strait of malacca', 'strait of hormuz', 'bab-el-mandeb', 'suez canal', 'panama canal',
        'bosporus', 'dardanelles', 'strait of gibraltar', 'dover strait', 'great rift valley',
        'ring of fire', 'mariana trench', 'amazon basin', 'nile river', 'congo basin',
        'mekong river', 'danube river', 'rhine river', 'sahel', 'taiga', 'tundra'
    ]),
    23: ('Bihar Geography', [
        'someshwar range', 'dun valley', 'north gangetic plain', 'south gangetic plain',
        'kosi', 'sorrow of bihar', 'gandak', 'son', 'punpun', 'falgu', 'karmanasa', 'haroha',
        'karail-kewal', 'tal soil', 'balasundar', 'piedmont swamp soil', 'terai soil',
        'valmiki tiger reserve', 'kanwar lake', 'kabartal', 'vikramshila dolphin', 'bhimbandh',
        'amjhor pyrite', 'barauni refinery'
    ])
}

def run_audit():
    gaps_per_topic = {}
    for tid, (tname, terms) in EXHAUSTIVE_NCERT_MAP.items():
        fp = os.path.join(STAGING, f'topic_{tid}.json')
        if not os.path.exists(fp):
            continue
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        qs = data if isinstance(data, list) else data.get('questions', [])
        
        # Build comprehensive lowercase search corpus
        corpus_parts = []
        for q in qs:
            corpus_parts.append(q.get('stem', ''))
            for opt in q.get('options', {}).values():
                corpus_parts.append(str(opt))
            corpus_parts.append(q.get('explanation', ''))
            dds = q.get('distractorDissections', [])
            if isinstance(dds, list):
                for dd in dds:
                    if isinstance(dd, dict):
                        corpus_parts.append(dd.get('dissection', ''))
        corpus = ' '.join(corpus_parts).lower()
        c_clean = corpus.replace('-', ' ').replace("'", '')
        
        missing = []
        for term in terms:
            t_clean = term.lower().replace('-', ' ').replace("'", '')
            if t_clean not in c_clean and term.lower() not in corpus:
                missing.append(term)
                
        found_count = len(terms) - len(missing)
        pct = (found_count / len(terms)) * 100
        gaps_per_topic[tid] = (tname, len(terms), found_count, pct, missing)
        print(f"Topic {tid:02d} ({tname[:26]:26s}): {found_count:2d}/{len(terms):2d} ({pct:5.1f}%) | Gaps: {len(missing)}")
        if missing:
            print(f"   -> Missing: {missing}")

    total_terms = sum(v[1] for v in gaps_per_topic.values())
    total_found = sum(v[2] for v in gaps_per_topic.values())
    print(f"\n==========================================")
    print(f"Total High-Yield NCERT Terms Audited: {total_terms}")
    print(f"Found in Question Bank: {total_found} ({(total_found/total_terms)*100:.1f}%)")
    print(f"Total Identified Missing Concepts: {total_terms - total_found}")
    print(f"==========================================")
    
    with open('ncert_gaps_report.json', 'w', encoding='utf-8') as f:
        json.dump(gaps_per_topic, f, indent=2)

if __name__ == '__main__':
    run_audit()
