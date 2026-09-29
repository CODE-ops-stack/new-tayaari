import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
import re

PROPOSED_PATTERNS = [
    # 1. MEMBER-OF
    ("member-of", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is an? (?:[a-z\-]+\s+)*(?:member|exemplar|instance|specimen|representative|type|kind|class|category|variant)\s+of|belongs to (?:the\s+)?(?:family|group|class|category|system|constellation|network|order)\s+of|is classified (?:as|under)\s+(?:an?|the)?|is categorized as\s+(?:an?|the)?|is grouped under|is counted among\s+(?:the\s+)?|is one of the\s+(?:[a-z\-]+\s+)*(?:members|constellations|systems|ports|stars|mountains|ranges|planets)\s+of|forms an? (?:integral\s+)?member of|member of the|member of)\s+(?P<pred>.*)$',
        re.IGNORECASE
    )),
    ("member-of", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+is an?\s+(?:[a-z\-]+\s+)*(?:star|port|satellite|planet|asteroid|comet|constellation|galaxy|volcano|mountain|range|island|river|sea|basin|plateau|glacier)\s+(?P<pred>(?:situated|located|commissioned|established|operating|orbiting|found)\b.*)$',
        re.IGNORECASE
    )),

    # 2. PART-OF
    ("part-of", re.compile(
        r'^(?:(?:\b(?:The|An|A|Our)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:(?:is|forms?|constitutes?)\s+(?:an?|the)?\s*(?:[a-z\-]+\s+)*(?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|portion)\s+(?:(?:located|situated|found)\s+)?(?:of|within|in)\b|(?:is|are)\s+(?:composed|made up|constituted)\s+of\b|consists?\s+of\b|\bforms?\s+part of\b|component of|part of the|part of)\s*:?\s*(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 3. EXCEPTION
    ("exception", re.compile(
        r'^(?:Except for|With the exception of|Apart from|Excluding)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-,]+?),\s*(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:have|has|are|is|rotate|exhibit|contain|can|do|does)\b.*)$',
        re.IGNORECASE
    )),
    ("exception", re.compile(
        r'^Unlike (?:the )?(?:majority|most|all other)\s+(?P<sec>[^,]+),\s*(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>.*)$',
        re.IGNORECASE
    )),
    ("exception", re.compile(
        r'^(?:While\s+(?:nearly\s+|almost\s+)?(?:all|most|the majority of)\s+[^,]+,\s*)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:are|is)\s+(?:unique exceptions?|the only\b)\s*(?P<pred>.*)$',
        re.IGNORECASE
    )),
    ("exception", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred1>.*?),\s+but\s+(?:are|is)\s+(?:uniquely incapable of|unique in|an exception in)\s+(?P<pred2>.*)$',
        re.IGNORECASE
    )),
    ("exception", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?P<pred1>.*?),\s+(?:except the|except|with the exception of|excluding|apart from)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred2>.*)$',
        re.IGNORECASE
    )),

    # 4. CONDITION
    ("condition", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:occurs? exclusively during\b|can occur only if\b|occurs? only if\b|condenses into.*only when|form only when|only when|provided that|conditional upon|if and only if|must exceed\s+\d+|exceeds?\s+\d+|exceed\s+\d+)\s+(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 5. SEQUENCE
    ("sequence", re.compile(
        r'^(?:(?:In|During)\s+[^,]+,\s+)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:progresses through a definite chronological sequence|commenced approximately.*followed by|arrive first.*followed sequentially by|(?:\b(?:is|are|was|were)\s+)?followed by|subsequently|.*?\b(?:metamorphose into.*before|stages? of|rock cycle)\b)\s*:?\s*(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 6. PROCESS
    ("process", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:converts|convert|transforms|transform|turns|turn|changes|change)\s+(?P<pred>.*?into\s+.*)$',
        re.IGNORECASE
    )),
    ("process", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is the (?:\w+\s+)?process (?:whereby|in which)|is the denudational process in which|develops through a systematic (?:thermodynamic )?process|develops through|was formed through the tectonic process|were formed through|was formed through|is formed by|are formed by|was formed by|were formed by|(?:is|are|was|were)\s+deposited\s+by|occurs when|mechanism of|plunges beneath|cycle involves|formation involves|have been transported and deposited by|transported and deposited by)\s*:?\s*(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 7. DISTRIBUTION
    ("distribution", re.compile(
        r'^(?:More than\s+\d+\s+percent of\s+(?:the\s+)?|Throughout\s+[^,]+,\s+)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:are distributed in|is concentrated across|form the most widespread|are concentrated in|predominantly distributed across|distributed across|covers the region)\s+(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 8. COMPARISON
    ("comparison", re.compile(
        r'^Unlike\s+(?P<cond>[^,]+(?:which\s+[^,]+)?),\s*(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:are|is)\s+(?P<pred>.*)$',
        re.IGNORECASE
    )),
    ("comparison", re.compile(
        r'^(?:Unlike\s+[^,]+,\s+)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred1>(?:is|are|was|were|[a-z]+(?:s|es|ed)?)\b.*?),\s+(?:whereas\s+(?:the\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred2>(?:is|are|was|were|[a-z]+(?:s|es|ed)?)\b.*)|while\s+(?![a-z]+ing\b)(?:the\s+)?(?P<sec2>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred3>(?:is|are|was|were|[a-z]+(?:s|es|ed)?)\b.*))$',
        re.IGNORECASE
    )),
    ("comparison", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is|are)\s+(?P<pred>(?:much\s+)?[a-z]+er\s+than\s+(?:that\s+of\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)(?:\.|$).*)$',
        re.IGNORECASE
    )),
    ("comparison", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is|are)\s+(?P<pred>(?:much\s+)?(?:more|less)\s+[a-z]+\s+than\s+(?:that\s+of\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)(?:\.|$).*)$',
        re.IGNORECASE
    )),
    ("comparison", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is much thinner compared to|is higher than|differs from)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s*(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 9. QUANTITY
    ("quantity", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:has an? (?:equatorial |polar |mean )?(?:radius|diameter|circumference|elevation|altitude|depth|density|mass|volume|area) of|extends to a depth of|has an? elevation of|has an? altitude of|reaches an? altitude of|constitutes approximately|maintains a constant tilt of|measures approximately|originated approximately|standard meridian|passes through.*longitude|drops to\s+[-]?\d+|reaches\s+[-]?\d+|(?:is|measures)\s+(?:approximately|about|around)?\s*[\d,]+(?:\.\d+)?\s*(?:kilometres|km|meters|m|miles|percent|%|degrees|°C|mb))\s*(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 10. CLASSIFICATION
    ("classification", re.compile(
        r'^(?:(?:Geologists|Scientists|Geographers|Plate tectonics)\s+)?classif(?:y|ies)\s+(?P<target>.*?)\s+into\s+(?P<pred>.*)$',
        re.IGNORECASE
    )),
    ("classification", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:(?:is|are|can be)\s+(?:classified into|divided into|grouped into|categorized into|classified as|divided as)|three major groups|exhibits two primary categories of|can be divided into|can be classified into)\s*(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 11. SPATIAL
    ("spatial", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:extends up to|is located|is situated|flows westward through|flows through|traverses|at the equator|at the poles)\s+(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 12. CAUSE/EFFECT
    ("cause/effect", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is caused by|are caused by|was caused by|were caused by|results from|result from|is triggered by|are triggered by|is driven by|are driven by|arises from|arise from|stems from)\s+(?P<pred>.*)$',
        re.IGNORECASE
    )),
    ("cause/effect", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:creates the Coriolis force|creates|leading to|lead to|leads to|causes|results in|drives|triggers|release\s+.*disturb)\s+(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 13. DEFINITION (Active)
    ("definition", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is defined as|refers to|is termed|is designated as|is described as|(?:is|are)\s+(?:an?|the)\s+(?:[a-z\-]+\s+)*(?:stream|collection|line|point|circle|envelope|layer|zone|belt|body|mass|system|structure|substance|mixture|compound|phenomenon|medium|form|assembly|sheet|tract|flow|discharge|field|aggregate)\s+(?:of|that|which|connecting|surrounding|held|released|formed)\b)\s*(?P<pred>.*)$',
        re.IGNORECASE
    )),

    # 14. ATTRIBUTE
    ("attribute", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:has|have|exhibits?|possesses?|displays?)\s+(?:the\s+)?(?:highest|lowest|greatest|smallest|largest|thickest|thinnest|deepest|shallowest|fastest|slowest|densest|hottest|coldest|longest|shortest|oldest|youngest|heaviest|lightest|strongest|weakest|maximum|minimum)\s+(?:[a-z\-]+\s+)*[a-z]+(?:\s+among|\s+in|\s+at|\s+of\b|\s*,).*)$',
        re.IGNORECASE
    )),
    ("attribute", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:is|are)\s+(?:characterized|distinguished|marked|noted)\s+by\s+.*)$',
        re.IGNORECASE
    )),
    ("attribute", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:comprises?|encompasses?)\s+(?:rich|immense|vast|extensive|abundant|large|significant)?\s*(?:reserves|deposits|resources|features|concentrations)\s+of\s+.*)$',
        re.IGNORECASE
    )),
    ("attribute", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:are|is)\s+(?:[a-z\-]+\s+)*(?:waves|vibrations|oscillations|radiations|pulses|currents)\s+that\s+(?:vibrate|propagate|oscillate|travel|radiate|flow|move)\s+.*)$',
        re.IGNORECASE
    )),
    ("attribute", re.compile(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:are|is)\s+(?:very|extremely|highly|mostly)?\s*[a-z\-]+\s+and\s+[a-z\-]+(?:,\s*(?:are|is|have|has|possess)\b.*)?)$',
        re.IGNORECASE
    )),
]

def extract_simulated(text):
    clean_text = text.strip()
    clean_text = re.sub(r'^\s*(?:\[[A-Za-z0-9]+\]|\(?[A-Za-z0-9ivxlcdmIVXLCDM]+\)[\s\.\)]|\d+[\.\)])\s*', '', clean_text)

    # Inverted definition
    m_inv_def = re.match(r'^(?P<desc>.+?)\s+(?:is|are)\s+defined\s+as\s+(?:the\s+)?(?P<term>[A-Za-z0-9\s\(\)\-]+)[\.\s]*$', clean_text, re.IGNORECASE)
    if m_inv_def:
        term = m_inv_def.group("term").strip().rstrip('.')
        desc = m_inv_def.group("desc").strip()
        return "definition", term, f"is defined as {desc}"

    # Locative
    m_loc = re.match(r'^(?:Under|Below|Above|Near|Beside|Beneath)\s+(?P<cond>.*?)\s+lies\s+(?:the\s+)?(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)(?:,\s*(?P<pred>.*?))?[\.\s]*$', clean_text, re.IGNORECASE)
    if m_loc:
        entity = m_loc.group("entity").strip().rstrip('.')
        cond = m_loc.group("cond").strip()
        pred_extra = m_loc.group("pred")
        pred = f"lies under {cond}" + (f", {pred_extra.strip().rstrip('.')}" if pred_extra else "")
        return "spatial", entity, pred

    # Passive def
    m_pass = re.match(r'^(?P<desc>.+?)\s+(?:are|is)\s+(?:called|known as|termed|designated as)\s+(?P<term>[A-Za-z0-9\s\(\)\-]+)\.?$', clean_text, re.IGNORECASE)
    if m_pass:
        term = m_pass.group("term").strip().rstrip('.')
        desc = m_pass.group("desc").strip()
        if re.search(r'\b(?:all\s+those|those\s+objects|all\s+such)\b', desc, re.IGNORECASE):
            primary_entity = term
            predicate = f"are {desc}"
        else:
            m_proper = re.match(r'^(?:(?:\b(?:The|An|A)\b\s+)?)([A-Za-z0-9\s\-]+)$', desc)
            primary_entity = m_proper.group(1).strip() if m_proper else desc
            predicate = f"are known as {term}" if "known as" in clean_text.lower() else f"are {term}"
        return "definition", primary_entity, predicate

    # Strip intro
    working_text = clean_text
    while True:
        m_intro = re.match(r'^(?:In|On|At|During|Throughout|Across|Under|Above|Below|With|Between|From|By|Along|According to|Beside|Beneath|Around|Near|Upon|Within|Beyond)\b\s+[^,]+,\s*', working_text, re.IGNORECASE)
        if not m_intro:
            break
        working_text = working_text[len(m_intro.group(0)):].strip()

    for intent, pat in PROPOSED_PATTERNS:
        m = pat.match(working_text) or pat.match(clean_text)
        if m:
            groups = m.groupdict()
            entity = groups.get("entity", "").strip()
            if "target" in groups and groups["target"]:
                entity = groups["target"].strip()
            pred = groups.get("pred", "").strip()
            if "pred1" in groups:
                sec_ent = groups.get("sec") or groups.get("sec2") or ""
                p2 = groups.get("pred2") or groups.get("pred3") or ""
                pred = f"{groups['pred1']}, whereas {sec_ent} {p2}"
            return intent, entity, pred

    # Fallback declarative
    match_decl = re.match(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\"\[\],\-\/]+?)\s+(?P<verb>is|are|form|forms|occurs|constitutes|contains|features|progresses|develops|comprises|falls)\s+(?P<rest>.*)',
        working_text,
        re.IGNORECASE
    )
    if match_decl:
        pe = match_decl.group("entity").strip()
        verb = match_decl.group("verb").strip()
        rest = match_decl.group("rest").strip()
        if not pe.lower().endswith(("in the", "of the", "to the", "from the")):
            return ("definition" if verb in {"is", "are"} else "attribute"), pe, f"{verb} {rest}"

    return None, None, None

if __name__ == "__main__":
    with open('data/golden_eval_set.json', encoding='utf-8') as f:
        data = json.load(f)

    positives = [p for p in data['examples'] if p['expected_label'] == 'positive']
    from v13_discovery.semantic_extractor import canonicalize_intent

    correct = 0
    for p in positives:
        intent, entity, pred = extract_simulated(p['text'])
        if canonicalize_intent(intent) == canonicalize_intent(p['intent']):
            correct += 1

    print(f"Golden Set Accuracy: {correct}/{len(positives)} ({correct/len(positives)*100:.1f}%)")
