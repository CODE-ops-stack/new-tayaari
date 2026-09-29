# V13.1 Architecture: Safe Semantic Contracts

To resolve the catastrophic failures of the string-based V13 generation pipeline, V13.1 introduces a strict typed semantic contract architecture. The generator will no longer process raw strings; it will pass strongly typed Python `dataclass` objects through the pipeline. 

## 1. KnowledgeUnit
Represents the exact source knowledge extracted from the corpus, gated for quality.
```python
@dataclass
class KnowledgeUnit:
    source_id: str          # e.g. "ncert_class11_physical"
    raw_text: str           # The exact source text
    block_type: str         # PROSE, TABLE, LIST (reject OCR_FRAGMENT, HEADER, FOOTER)
    entities: List[str]     # Properly extracted named entities (using word boundaries/NLP)
    relations: Dict[str, Any] # e.g. {"subject": "Indus", "predicate": "flows_through", "object": "Ladakh"}
```

## 2. QuestionIntent
Defines the cognitive goal and structure of the question before any text is generated.
```python
@dataclass
class QuestionIntent:
    knowledge: KnowledgeUnit
    target_entity: str      # The specific entity being tested (e.g. "Indus")
    intent_type: str        # e.g. "IDENTIFY_FEATURE", "EXPLAIN_CAUSE", "SEQUENCE_ITEMS"
    cognitive_level: str    # "RECALL", "UNDERSTAND", "APPLY" (strictly assigned based on intent_type, not regex)
```

## 3. AnswerContract
Enforces the semantic bounds of the correct answer. 
```python
@dataclass
class AnswerContract:
    intent: QuestionIntent
    correct_answer: str     # Must match the target_entity or relation exactly
    semantic_type: str      # e.g. "RIVER", "PLANET", "YEAR". Prevent "RIVER" answering an "INDUSTRY" question.
```

## 4. DistractorContract
Ensures distractors are semantically valid and plausible, bounded by the AnswerContract.
```python
@dataclass
class DistractorContract:
    answer_contract: AnswerContract
    distractors: List[str]  # Must be of the same `semantic_type` as the AnswerContract
    trap_types: List[str]   # e.g. ["COMMON_MISCONCEPTION", "OPPOSITE_FACT"]
```

## 5. GeneratedQuestion
The final compiled question, generated only after all contracts are fulfilled.
```python
@dataclass
class GeneratedQuestion:
    stem: str               # Synthesized from QuestionIntent, NOT raw source text
    options: Dict[str, str] # Shuffled correct_answer + distractors
    correct_key: str        # e.g. "opt_a"
    explanation: str        # Synthesized explanation
    contracts: dict         # Store the contracts (Intent, Answer, Distractor) for audit
    topic: str              # Semantically mapped topic (no fallback to Physical Geography)
    exam_target: str        # Strictly mapped exam based on cognitive_level and topic
```

## 6. ValidationResult
The result of the 11-point strict gate validation.
```python
@dataclass
class ValidationResult:
    is_valid: bool
    failure_reasons: List[str]
    # Gates must check:
    # 1. Answer satisfies QuestionIntent
    # 2. Distractors satisfy AnswerContract semantic type
    # 3. Stem is grammatically complete and self-contained
    # 4. No string overlap leakage between stem and answer
```

## Pipeline Flow

1. **Source Gating**: `extract()` -> `KnowledgeUnit` (Filters out OCR artifacts).
2. **Intent Generation**: `KnowledgeUnit` -> `QuestionIntent` (Explicit semantic mapping).
3. **Answer & Distractor Generation**: `QuestionIntent` -> `AnswerContract` -> `DistractorContract` (Type bounds enforced).
4. **Stem Synthesis**: Synthesize `stem` using `QuestionIntent` (No templates).
5. **Compilation**: Compile into `GeneratedQuestion`.
6. **Validation**: Validate `GeneratedQuestion` -> `ValidationResult`. If valid, accept.
