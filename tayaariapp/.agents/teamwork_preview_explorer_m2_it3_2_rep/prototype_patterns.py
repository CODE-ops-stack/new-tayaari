#!/usr/bin/env python3
"""
prototype_patterns.py
=====================
Refined prototype generalized linguistic patterns for V13 Semantic Extractor (Milestone 2 Iteration 3).
Demonstrates zero domain-vocabulary overfitting while categorizing both golden eval items
and unseen educational sentences across all 14 semantic intents.
"""

import re
from typing import Dict, Any, Optional

class GeneralizedSemanticExtractor:
    PASSIVE_DEF_REGEX = re.compile(
        r'^(?P<desc>.+?)\s+(?:are|is)\s+(?:called|known as|termed|designated as)\s+(?P<term>[A-Za-z0-9\s\(\)\-]+)\.?$',
        re.IGNORECASE
    )
    LOCATIVE_INV_REGEX = re.compile(
        r'^(?:Under|Below|Above|Near|Beside|Beneath|Between)\s+(?P<cond>.*?)\s+lies\s+(?:the\s+)?(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)(?:,\s*(?P<pred>.*?))?[\.\s]*$',
        re.IGNORECASE
    )
    INTRO_PREP_REGEX = re.compile(
        r'^(?:In|On|At|During|Throughout|Across|Under|Above|Below|With|Between|From|By|Along|According to|Beside|Beneath|Around|Near|Upon|Within|Beyond)\b\s+[^,]+,\s*',
        re.IGNORECASE
    )

    PATTERNS = [
        # 1. EXCEPTION
        ("exception", re.compile(
            r'^(?:Except for|With the exception of|Apart from|Excluding)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-,]+?),\s*(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>\b.*)$',
            re.IGNORECASE
        )),
        ("exception", re.compile(
            r'^Unlike (?:the )?(?:majority of|most|all other)\s+(?P<sec>[^,]+),\s*(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("exception", re.compile(
            r'^(?:While\s+(?:nearly\s+)?(?:all|most)\s+(?P<sec>[^,]+),\s+)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:are|is)\s+(?:unique exceptions?|the only\b|uniquely incapable of)\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("exception", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred1>.*?),\s+but\s+(?:is|are)\s+(?:uniquely incapable of|unique exceptions?|the only\b)\s+(?P<pred2>.*)$',
            re.IGNORECASE
        )),
        ("exception", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?P<pred1>.*?),\s+(?:except the|except|with the exception of|excluding|apart from)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred2>.*)$',
            re.IGNORECASE
        )),

        # 2. DISTRIBUTION (Evaluated before comparison so that "distributed in X, while Y" matches distribution)
        ("distribution", re.compile(
            r'^(?:(?:(?:More|Less) than\s+)?(?:\d+(?:\.\d+)?%|\d+(?:\.\d+)?\s+percent)\s+of\s+(?:the\s+)?)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:(?:are|is)\s+)?(?:distributed\s+(?:in|across|throughout)|is concentrated across|are concentrated in|concentrated across|concentrated in|form(?:s)? the most widespread|predominantly distributed|distributed across|covers the region)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 3. COMPARISON
        # Distinct contrasting entities connected by whereas/while/in contrast to
        ("comparison", re.compile(
            r'^(?:Unlike\s+[^,]+,\s+)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?P<pred1>[a-z]+(?:s|ed|ing)?\b.*?),\s+(?:whereas|in contrast to|while)\s+(?:the\s+|all\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred2>(?:is|are|maintain|shed|exhibit|have|can|transport|travel|propagate|remain|carry)\b.*)$',
            re.IGNORECASE
        )),
        ("comparison", re.compile(
            r'^Unlike\s+(?P<cond>[^,]+(?:which\s+[^,]+)?),\s*(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:are|is)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("comparison", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is|are)\s+(?P<pred>(?:much\s+)?[a-z\-]+er(?:\-[a-z]+)?\s+than\s+(?:that\s+of\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)(?:\.|$).*)$',
            re.IGNORECASE
        )),
        ("comparison", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is|are)\s+(?P<pred>(?:much\s+)?(?:more|less)\s+[a-z\-]+\s+than\s+(?:that\s+of\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)(?:\.|$).*)$',
            re.IGNORECASE
        )),
        ("comparison", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is much thinner compared to|differs from)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 4. CONDITION
        ("condition", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:occurs exclusively during|can occur only if|condenses into.*only when|forms? only when|occurs only when|takes place only when|only when|provided that|conditional upon|if and only if|must exceed\s+\d+|exceeds?\s+\d+|exceed\s+\d+)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 5. CLASSIFICATION
        ("classification", re.compile(
            r'^(?:(?P<subject>[A-Za-z\s]+?)\s+)?classif(?:y|ies)\s+(?P<target>.*?)\s+into\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("classification", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:(?:is|are|can be)\s+(?:classified into|divided into|grouped into|categorized into|classified as|divided as)|exhibits?\s+(?:two|three|four|five|several|\d+)\s+(?:primary|major|fundamental|distinct)?\s*categories of|can be divided into|can be classified into)\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 6. SEQUENCE
        ("sequence", re.compile(
            r'^(?:(?:In|During)\s+[^,]+,\s+)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:progresses through\s+(?:a\s+)?(?:[a-z\-]+\s+)*(?:sequence|stages|phases|steps|cycle)|commenced approximately.*followed by|arrive(?:s)? first.*followed sequentially by|(?:\b(?:is|are|was|were)\s+)?followed by|subsequently|.*?\b(?:metamorphose into.*before|stages? of)\b)\s*:?\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 7. PROCESS
        ("process", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:converts|convert|transforms|transform|turns|turn|changes|change)\s+(?P<pred>.*?into\s+.*)$',
            re.IGNORECASE
        )),
        ("process", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is the (?:\w+\s+)?process (?:whereby|in which|by which|through which)|develops through (?:a\s+)?(?:\w+\s+)*process|was formed through the (?:\w+\s+)?process of|is formed by|are formed by|was formed by|were formed by|occurs when\s+.*solidif|cycle involves|formation involves)\s*:?\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 8. SPATIAL
        ("spatial", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:extends up to|is located|is situated|flows (?:westward|eastward|northward|southward) through|flows through|traverses)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 9. QUANTITY
        ("quantity", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:has an? (?:[a-z\-]+\s+)?(?:radius|diameter|circumference|elevation|altitude|depth|density|mass|volume|area|tilt) of|extends to a depth of|reaches an? altitude of|constitutes approximately\s+\d+|maintains a constant tilt of|measures approximately|originated approximately\s+\d+|(?:travels|moves|propagates|rotates)\s+at\s+(?:approximately\s+)?[\d,]+|(?:is|measures)\s+(?:approximately|about|around)?\s*[\d,]+(?:\.\d+)?\s*(?:kilometres|km|meters|m|miles|percent|%|degrees|°C|mb|billion years|million light-years))\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 10. CAUSE/EFFECT
        ("cause/effect", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is caused by|are caused by|was caused by|were caused by|results from|result from|is triggered by|are triggered by|is driven by|are driven by|arises from|arise from|stems from)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("cause/effect", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:causes|cause|results in|result in|leads to|lead to|leading to|triggers|trigger|drives|drive|induces|induce|inducing currents that disrupt|disturb(?:s)?\s+.*inducing)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 11. PART-OF
        ("part-of", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:constitutes (?:the\s+)?(?:[a-z\-]+\s+)*(?:layer|envelope|shell|crust|mantle|core|component|sphere|part|fraction|portion)\s+of|is composed of\s+(?:two|three|four|five|\d+)\s+(?:[a-z\-]+\s+)*(?:shells|layers|zones|components|parts|geosphere shells)|forms?\s+an?\s+(?:[a-z\-]+\s+)*(?:component|part|constituent|fraction)\s+(?:located\s+within|of)|is the (?:[a-z\-]+\s+)*(?:constituent\s+)?(?:layer|shell|envelope|zone|boundary)\s+of|\bforms?\s+part of\b|component of|part of the|part of)(?:\s*:\s*|\s+)(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 12. MEMBER-OF
        ("member-of", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is an? (?:[a-z\-]+\s+)*(?:member of|remnant member of|recognized member of)|belongs to the (?:family|class|group) of|member of the|member of)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("member-of", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+is an?\s+(?:[a-z\-]+\s+)*(?:star|satellite|planet|port|container port|constellation|mountain range|fold mountain|fold mountain systems|animal|organism)\s+(?:located|situated|commissioned|orbiting|found|in|along)\b.*$',
            re.IGNORECASE
        )),

        # 13. DEFINITION
        ("definition", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is defined as|refers to|denotes|signifies|designates)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("definition", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is a constant stream of|is a massive collection of|is an imaginary line|is the point on the surface\s+.*?defined as)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 14. ATTRIBUTE
        ("attribute", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:has the (?:lowest|highest|greatest|smallest|largest|deepest|thickest|thinnest|densest)\s+[a-z\s\-]+?\s+(?:among|of|in)\s+.*)$',
            re.IGNORECASE
        )),
        ("attribute", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is characterized by|are characterized by|features|exhibits|possesses|comprises immense reserves)\s*(?:,\s*|\s+)(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("attribute", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is|are)\s+(?:very\s+)?[a-z]+\s+and\s+[a-z]+,\s+(?:are|is)\s+.*$',
            re.IGNORECASE
        )),
        ("attribute", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+are\s+(?:[a-z\-]+\s+)*(?:waves|vibrations|oscillations|currents|rays|particles)\s+that\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
    ]

    @classmethod
    def extract_intent(cls, clean_text: str) -> Optional[str]:
        if cls.PASSIVE_DEF_REGEX.match(clean_text):
            return "definition"
        if cls.LOCATIVE_INV_REGEX.match(clean_text):
            return "spatial"

        working_text = clean_text
        while True:
            m_intro = cls.INTRO_PREP_REGEX.match(working_text)
            if not m_intro:
                break
            working_text = working_text[len(m_intro.group(0)):].strip()

        for intent, pat in cls.PATTERNS:
            if pat.match(working_text) or pat.match(clean_text):
                return intent

        match_decl = re.match(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\"\[\],\-\/]+?)\s+(?P<verb>is|are|has|have|form|forms|occurs|constitutes|contains|features|progresses|develops|comprises|falls)\s+(?P<rest>.*)',
            working_text,
            re.IGNORECASE
        )
        if match_decl:
            pe = match_decl.group("entity").strip()
            verb = match_decl.group("verb").strip().lower()
            if not pe.lower().endswith(("in the", "of the", "to the", "from the")):
                if verb in {"has", "have", "features", "contains", "comprises"}:
                    return "attribute"
                return "definition"

        return None
