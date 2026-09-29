# Forensic Audit: Tayaari Pakki Content Discovery Pipeline (v10)

## Call Graph
1. DiscoveryEngine.run()
   - Initializes glob parsing of source-material/*.txt
2. SourceParser.parse(filenames)
   - Strips explicit MCQ (Q., (a))
   - Classifies PROSE vs TABLE_OR_META
3. KnowledgeExtractor.extract(blocks)
   - Sentences split via regex (?<=[.!?])\s+
   - Scans against RELATIONS dict (DEFINITION, CAUSE_EFFECT, SPATIAL, DISTRIBUTION, COMPARISON)
   - Rejects if cause_subj or effect_obj start with words in BAD_ENTITIES (e.g., "it", "they", "which").
   - Truncates if length exceeds OCR thresholds.
4. OpportunityEngine.synthesize(nodes)
   - Maps relations to generic stem templates.
   - Example (Bad): When comparing geographic features, how does '[LEFT]' differ... -> It differs in that [RIGHT]
   - Distractor pooling: Collects all effect_obj strings from the same RELATIONS type.
5. BatchAuditor.audit(opportunities)
   - Filters exact text duplicates and answer duplicates.

## Weaknesses Identified
- **Fragmented Clause Vulnerability**: The regex (.*) while (.*) blindly splits clauses without verifying if the right-hand side has a valid subject noun phrase. Result: "lies south of it" becomes an object.
- **Generic Quotation Stems**: Wrapping raw source text in '[TEXT]' creates disjointed, unnatural reading experiences that test quotation parsing rather than geographic knowledge.
- **Pronoun Blindness in Secondary Clauses**: While BAD_ENTITIES blocks "It" at the start of an extracted clause, it fails to resolve internal pronouns (e.g. "south of it").
- **Blind Distractor Polling**: Distractors share the same relation category (e.g. all COMPARISON objects) but lack grammatical alignment to the specific stem.
