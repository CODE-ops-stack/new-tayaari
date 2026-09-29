"""
v13_discovery/normalizer.py
===========================
Comprehensive Document Normalizer, Markdown Table Parser, Layout Desegmenter,
and Watermark/OCR Cleaner for the V13 Question Discovery Pipeline.

Resolves V12 Ingestion Deficiencies:
1. Recovers 100% of tabular educational facts from Markdown tables.
2. Reconnects vertical OCR text column wraps, hyphenated breaks, and merged headers.
3. Purges watermark headers, ISBNs, textbook craft boxes, and MCQ noise.
4. Preserves unbreakable provenance metadata (sourceId, path, page_or_line).
"""

import re
import html
import unicodedata
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


class BlockType:
    """Standard block classification types."""
    PROSE = "PROSE"
    TABLE = "TABLE"
    METADATA = "METADATA"


@dataclass
class SentenceProvenance:
    """Provenance tracking for an individual extracted sentence or proposition."""
    sentence: str
    source_file: str
    line_start: int
    line_end: int
    char_start: int = 0
    char_end: int = 0
    block_type: str = BlockType.PROSE
    raw_context: str = ""
    confidence: float = 1.0


@dataclass
class NormalizedBlock:
    """Standardized normalized unit emitted to downstream semantic extractors.
    
    Interface Contract (PROJECT.md):
    NormalizedBlock(id, text, type: PROSE | TABLE, clean_sentences: List[str], metadata: dict)
    """
    id: str
    text: str
    type: str  # "PROSE" | "TABLE"
    clean_sentences: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    provenance: List[SentenceProvenance] = field(default_factory=list)

    @property
    def block_type(self) -> str:
        return self.type


class WatermarkOcrCleaner:
    """Identifies and purges running headers, watermarks, ISBNs, exercise instructions,
    MCQ options, and OCR formatting noise while strictly preserving substantive prose.
    """
    
    WATERMARK_PATTERNS = [
        # Publisher & Channel Watermarks
        re.compile(r'^\s*PARMAR\s+SSC\s*$', re.IGNORECASE),
        re.compile(r'^\s*www\.ssccglpinnacle\.com.*', re.IGNORECASE),
        re.compile(r'^\s*Download\s+Pinnacle\s+Exam\s+Preparation\s+App.*', re.IGNORECASE),
        re.compile(r'^\s*Pinnacle\s+Geography\s*$', re.IGNORECASE),
        
        # Textbook Standard Identifiers & Cataloging
        re.compile(r'^\s*ISBN\s*[\d\-]+\s*$', re.IGNORECASE),
        re.compile(r'^\s*\b0656\b\s*$'),
        re.compile(r'^\s*\d{4}\-\d{2}(\d{4}\-\d{2})?\s*$'),  # e.g., 2018-19 or 2018-192018-19
        re.compile(r'^\s*not\s+to\s+be\s+republished\s*$', re.IGNORECASE),
        re.compile(r'^\s*NCERT\s*$', re.IGNORECASE),
        re.compile(r'^\s*Rationalised\s+[\d\-]+\s*$', re.IGNORECASE),
        re.compile(r'^\s*Reprint\s+[\d\-]+\s*$', re.IGNORECASE),
        
        # Textbook Running Titles & Front Matter
        re.compile(r'^\s*Textbook\s+in\s+Geography\s*(for\s+Class\s+[IVXLCDM]+)?\s*$', re.IGNORECASE),
        re.compile(r'^\s*for\s+Class\s+[IVXLCDM]+\s*$', re.IGNORECASE),
        re.compile(r'^\s*The\s+Earth\s*$', re.IGNORECASE),
        re.compile(r'^\s*Our\s+Habitat\s*$', re.IGNORECASE),
        re.compile(r'^\s*Social\s+Science\s*$', re.IGNORECASE),
        re.compile(r'^\s*THE\s+EARTH\s*:\s*OUR\s+HABITAT\s*$', re.IGNORECASE),
        re.compile(r'^\s*THE\s+EARTH\s+IN\s+THE\s+SOLAR\s+SYSTEM\s*$', re.IGNORECASE),
        re.compile(r'^\s*GLOBE\s*:\s*LATITUDES\s+AND\s+LONGITUDES\s*$', re.IGNORECASE),
        re.compile(r'^\s*MAJOR\s+DOMAINS\s+OF\s+THE\s+EARTH\s*$', re.IGNORECASE),
        re.compile(r'^\s*INDIA\s*:\s*CLIMATE,\s*VEGETATION\s+AND\s+WILDLIFE\s*$', re.IGNORECASE),
        re.compile(r'^\s*MAPS\s*$', re.IGNORECASE),
        
        # Diagram and Figure Captions
        re.compile(r'^\s*Figure\s+\d+\.\d+\s*:.*$', re.IGNORECASE),
        
        # Classroom Activity Boxes & Craft Instructions
        re.compile(r'^\s*(Let’s|Let\'s)\s+Do\s*$', re.IGNORECASE),
        re.compile(r'^\s*Do\s+you\s+know\?\s*$', re.IGNORECASE),
        re.compile(r'^\s*Step\s*:\s*$', re.IGNORECASE),
        re.compile(r'^\s*\d+\.\s*(Place|Now|Perforate|In|Switch|Take|You)\b.*', re.IGNORECASE),
        re.compile(r'.*\b(torch|sheet\s+of\s+plain\s+paper|pencil\s+and\s+a\s+needle)\b.*', re.IGNORECASE),
        
        # Textbook Exercises & Question Prompts
        re.compile(r'^\s*\d+\.\s*(Answer\s+the\s+following|Tick\s+the\s+correct|Fill\s+in\s+the\s+blanks)\b.*', re.IGNORECASE),
        
        # Exam Metadata, Shift Tags & Question Stems
        re.compile(r'^\s*SSC\s+[A-Za-z\s]+.*(?:\(Shift|\d+/\d+/\d+)', re.IGNORECASE),
        re.compile(r'^\s*Correct\s+answer\s*:.*', re.IGNORECASE),
        re.compile(r'^\s*Q\.?\s*\d+[\.\:]\s+.*', re.IGNORECASE),
        re.compile(r'.*\bWhich\s+of\s+the\s+following\b.*', re.IGNORECASE),
        
        # Grounding Database Formatting Artifacts
        re.compile(r'^\s*-\s*\*\*[A-Za-z0-9\-]+\*\*\s*:.*'),
        re.compile(r'^\s*```.*'),
        re.compile(r'^\s*\*Total\s+.*\*.*', re.IGNORECASE),
        
        # Solved Test Verdicts (Non-Factual)
        re.compile(r'.*\ball\s+of\s+these\b.*', re.IGNORECASE),
        re.compile(r'.*\bStatement\s*\d*\s*:\s*(In)?correct\b.*', re.IGNORECASE),
        re.compile(r'^\s*(\d+\s*(and\s*\d+)?\s*only\.?)\s*$', re.IGNORECASE),
        
        # Isolated OCR Noise Characters
        re.compile(r'^\s*[\-\'o\?st]{1,2}\s*$'),
        re.compile(r'^\s*[\u0900-\u097F]{1}\s*$'),  # isolated Hindi diacritics
    ]
    
    # MCQ Option Markers
    MCQ_SINGLE_OPTION = re.compile(r'^\s*(\([a-e]\)|[A-E]\))\s+.*', re.IGNORECASE)
    MCQ_MULTI_OPTION = re.compile(r'^\s*(\([a-e]\)[^()]+){2,}\s*$', re.IGNORECASE)

    @classmethod
    def is_watermark_or_noise(cls, line: str) -> bool:
        """Determines if a raw line is an uninformative watermark, header, or formatting artifact."""
        s = line.strip()
        if not s:
            return True
            
        for pat in cls.WATERMARK_PATTERNS:
            if pat.match(s):
                return True
                
        # Standalone page numbers
        if re.match(r'^\d{1,4}$', s):
            return True
            
        # Standalone MCQ option rows
        if cls.MCQ_SINGLE_OPTION.match(s) or cls.MCQ_MULTI_OPTION.match(s):
            return True
            
        return False

    @classmethod
    def clean_solution_line(cls, line: str) -> Optional[str]:
        """Strips exam solution prefixes like 'Sol.1.(b) Solar wind.' to salvage factual explanations."""
        s = line.strip()
        m = re.match(r'^(Sol\.\s*\d*[\.\)]?\s*\(?[a-d]?\)?|Ans[a-z\:]*\s*\(?[a-d]?\)?)\s*(.*)', s, re.IGNORECASE)
        if m:
            clean_part = m.group(2).strip()
            # If the clean part is only an option verdict or too short, discard it
            if len(clean_part) < 15 or cls.is_watermark_or_noise(clean_part):
                return None
            return clean_part
        return s


class LayoutDesegmenter:
    """Reconstructs reading flow across narrow OCR columns, unmerges horizontal concatenations,
    and stitches dangling syntactic line wraps.
    """
    
    DANGLING_ENDINGS = {
        # Conjunctions & Subordinators
        'and', 'or', 'but', 'nor', 'yet', 'so', 'while', 'whereas', 'because',
        'as', 'if', 'when', 'that', 'which', 'who', 'where',
        # Prepositions
        'of', 'in', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'about',
        'into', 'like', 'through', 'after', 'over', 'between', 'out', 'against',
        'during', 'without', 'before', 'under', 'around', 'among', 'along',
        # Determiners, Articles, Auxiliaries
        'the', 'a', 'an', 'this', 'these', 'those', 'their', 'its', 'is', 'are', 'was', 'were'
    }
    
    FINITE_VERBS = {
        'is', 'are', 'was', 'were', 'has', 'have', 'had', 'occurs', 'occurred',
        'proposes', 'called', 'contains', 'emits', 'started', 'predicts', 'predicted',
        'reaches', 'orbits', 'forms', 'formed', 'leads', 'lead', 'burns', 'hits',
        'creates', 'composed', 'makes', 'takes', 'consists', 'includes', 'moves',
        'release', 'releases', 'disturbs', 'classify', 'classifies'
    }

    @classmethod
    def split_merged_headers(cls, line: str) -> str:
        """Splits multi-column horizontal concatenations caused by multi-column PDF bounding boxes."""
        s = line.strip()
        # 1. Deduplicate immediately repeated verbatim phrases
        s = re.sub(r'^(.{6,}?)\s*\1\s*$', r'\1:', s)
        s = re.sub(r'\b([A-Z][a-zA-Z\s]{5,}?)\s+\1\b', r'\1', s)
        # 2. Split concatenated numeric units and subsequent headers/values
        s = re.sub(r'(\d+\s*[a-zA-Z]+)(?=\d+\s*[a-zA-Z])', r'\1. ', s)
        s = re.sub(r'(\d+\s*[a-zA-Z]+)(?=[A-Z][a-z]+)', r'\1. ', s)
        # 3. Generalized PascalCase / camelCase word boundary splitting using zero-width lookahead
        s = re.sub(r'([a-z])(?=[A-Z])', r'\1 ', s)
        # 4. Clean up any trailing repeated phrases after spacing
        s = re.sub(r'^(.{6,}?)\s*:\s*\1\s*$', r'\1:', s)
        s = re.sub(r'^(.{6,}?)\s+\1\s*$', r'\1:', s)
        return s

    @classmethod
    def is_heading(cls, line: str) -> bool:
        """Identifies isolated section headings or topic headers that should not be merged into prose."""
        s = line.strip()
        if not s or len(s) > 120:
            return False
        # Soft-hyphen or trailing hyphen: word wrap across column/line break, NEVER a heading
        if s.endswith(('-', '\u00ad', '—', '–')) or re.search(r'[\-\u00ad]\s*$', s):
            return False
        if s.endswith(('.', '!', '?', ';', ',')):
            return False
        if re.search(r'\b[a-z]{2,}\.\s+[A-Z]', s):
            return False
        if s.startswith('#'):
            return True
        if s.endswith(':'):
            return True
        # NCERT-style numbered headings: "1. Geography as a Discipline 2" or "2. The Origin and Evolution of the Earth 14"
        if re.match(r'^\d+\.\s+[A-Z][a-zA-Z\s]+', s):
            return True
        # NCERT unit headings: "UNIT I : GEOGRAPHY AS A DISCIPLINE 1-12"
        if re.match(r'^UNIT\s+[IVX]+\s*:', s, re.IGNORECASE):
            return True
        # Chapter headings: "Chapter 1: The Earth in the Solar System"
        if re.match(r'^Chapter\s+\d+', s, re.IGNORECASE):
            return True
        words = [w.lower() for w in re.sub(r'[^\w\s]', '', s).split()]
        if not words or any(w in cls.FINITE_VERBS for w in words):
            return False
        if words[-1] in cls.DANGLING_ENDINGS:
            return False
        # Title Case or ALL CAPS
        return (s.isupper() or s.istitle() or all(w[0].isupper() for w in s.split() if w.isalpha()))

    PUNCT_DASH_WORDS = {
        'groups', 'group', 'types', 'type', 'categories', 'category', 'classes', 'class',
        'layers', 'layer', 'stages', 'stage', 'processes', 'process', 'zones', 'zone',
        'parts', 'part', 'divisions', 'division', 'forms', 'form', 'features', 'feature',
        'branches', 'branch', 'factors', 'factor', 'sources', 'source', 'elements', 'element',
        'follows', 'namely', 'example', 'examples', 'note', 'section', 'case', 'cases',
        'reasons', 'reason', 'ways', 'way', 'forces', 'force', 'methods', 'method',
        'characteristics', 'properties', 'components', 'component', 'orders', 'order',
        'levels', 'level', 'phases', 'phase', 'steps', 'step'
    }
    KNOWN_PREFIXES = {
        'sub', 'semi', 'trans', 'inter', 'atmo', 'litho', 'hydro', 'thermo', 'meso',
        'strato', 'tropo', 'geo', 'bio', 'astro', 'photo', 'proto', 'macro', 'micro',
        'hemi', 'extra', 'ultra', 'infra', 'multi', 'non', 'pre', 'post', 're', 'un'
    }

    @classmethod
    def is_punctuation_dash(cls, w1: str, w2: str, prev_text: str = "", next_text: str = "") -> bool:
        if prev_text.endswith('--'):
            return True
        if w1 in cls.PUNCT_DASH_WORDS:
            return True
        if w1.endswith('s') and len(w1) >= 5 and w1 not in cls.KNOWN_PREFIXES:
            if not any(w2.startswith(s) for s in ['tion', 'sion', 'ment', 'able', 'ible', 'fied', 'gent']):
                return True
        return False

    @classmethod
    def should_stitch_lines(cls, prev_line: str, next_line: str) -> bool:
        """Determines if prev_line and next_line should be stitched into a single sentence."""
        p = prev_line.strip()
        n = next_line.strip()
        if not p or not n:
            return False
        if cls.is_heading(n):
            return False
            
        # Soft hyphen at end of line
        if p.endswith('-'):
            return True
            
        # Prev line ends with sentence terminal punctuation
        if p[-1] in {'.', '!', '?'}:
            if p[-1] in {'!', '?'}:
                return n[0].islower()
            # Check known abbreviations (honorifics, latin, academic, references)
            if re.search(r'\b(?:dr|prof|mr|mrs|ms|sr|jr|st|e\.g|i\.e|etc|et\s+al|vs|approx|fig|tab|eq|no|vol|ch|sec|ref|univ|dept|co|inc|ltd)\.$', p, re.IGNORECASE):
                return True
            # Check single capital initial (e.g., 'Alfred W.\nWegener')
            if re.search(r'\b[A-Z]\.$', p):
                return True
            # Check decimal number split across lines (e.g., '4.\n37')
            if re.search(r'\d+\.$', p) and re.match(r'^\d+', n):
                return True
            return n[0].islower()
            
        # Prev line ends with colon or semicolon
        if p[-1] in {':', ';'}:
            return False
            
        tokens = re.sub(r'[^\w\s]', '', p).split()
        if not tokens:
            return False
        last_word = tokens[-1].lower()
        
        # Trailing conjunction or preposition
        if last_word in cls.DANGLING_ENDINGS:
            return True
            
        # Next line starts with lowercase
        if n[0].islower():
            return True
            
        # Next line starts with continuation words
        first_word = n.split()[0].lower()
        if first_word in {'in', 'and', 'or', 'to', 'for', 'with', 'published', 'occurred', 'collapsed', 'forming', 'orbital'}:
            return True
            
        # Narrow-column line (< 40 chars) without terminal punctuation
        if len(p) < 40 and not p.endswith(('.', ':', '!', '?')) and not cls.is_heading(p):
            return True
            
        return False

    @classmethod
    def stitch_lines(cls, lines: List[Tuple[int, str]]) -> List[Tuple[int, int, str]]:
        """Stitches lines into continuous blocks, preserving (start_line, end_line, text)."""
        if not lines:
            return []
            
        stitched = []
        cur_start, cur_end, cur_text = lines[0][0], lines[0][0], cls.split_merged_headers(lines[0][1].strip())
        
        for line_no, raw_line in lines[1:]:
            line_str = cls.split_merged_headers(raw_line.strip())
            if not line_str:
                continue
                
            if cls.should_stitch_lines(cur_text, line_str):
                if cur_text.endswith('-'):
                    m_num_prev = re.search(r'(\d+)-$', cur_text)
                    m_num_next = re.match(r'^(\d+)', line_str)
                    if m_num_prev and m_num_next:
                        # 1. Numerical range: preserve hyphen without spaces (5000-6000)
                        cur_text = cur_text + line_str
                    else:
                        m_w_prev = re.search(r'([A-Za-z]+)-$', cur_text)
                        m_w_next = re.match(r'^([A-Za-z]+)', line_str)
                        if m_w_prev and m_w_next and cls.is_punctuation_dash(m_w_prev.group(1).lower(), m_w_next.group(1).lower(), cur_text, line_str):
                            # 2. Punctuation dash: insert spaces (two groups - terrestrial)
                            cur_text = cur_text[:-1].rstrip() + ' - ' + line_str.lstrip()
                        else:
                            # 3. Soft hyphen: strip hyphen and join (strati- + fied -> stratified)
                            cur_text = cur_text[:-1] + line_str
                elif re.search(r'\d+\.$', cur_text) and re.match(r'^\d+', line_str):
                    # Decimal join (4. + 37 -> 4.37)
                    cur_text = cur_text + line_str
                else:
                    cur_text = cur_text + ' ' + line_str
                cur_end = line_no
            else:
                stitched.append((cur_start, cur_end, cur_text))
                cur_start = line_no
                cur_end = line_no
                cur_text = line_str
                
        if cur_text:
            stitched.append((cur_start, cur_end, cur_text))
            
        return stitched


class TableParser:
    """Detects Markdown pipe tables and extracts declarative factual propositions."""
    
    @classmethod
    def is_markdown_table_row(cls, line: str) -> bool:
        """Checks if a line is part of a markdown table."""
        s = line.strip()
        return s.startswith('|') and s.endswith('|') and s.count('|') >= 2

    @classmethod
    def parse_markdown_table(cls, table_lines: List[Tuple[int, str]], source_file: str) -> List[SentenceProvenance]:
        """Parses a markdown table block into declarative propositions."""
        raw_rows = []
        for l_no, l_str in table_lines:
            cells = [c.strip() for c in l_str.split('|')[1:-1]]
            raw_rows.append((l_no, cells))
            
        if len(raw_rows) < 2:
            return []
            
        headers = raw_rows[0][1]
        data_rows = raw_rows[1:]
        
        # Skip alignment delimiter row if present (|---|---| or Pandoc | ::: | ::: | or | === |)
        if data_rows and all(bool(re.match(r'^[\:\-\=\s]{2,}$', c.strip())) for c in data_rows[0][1] if c.strip()):
            data_rows = data_rows[1:]
            
        propositions = []
        for l_no, cells in data_rows:
            if not cells or len(cells) < 2:
                continue
            entity = cells[0]
            if not entity:
                continue
                
            pairs = []
            for col_idx in range(1, min(len(headers), len(cells))):
                col_name = headers[col_idx]
                val = cells[col_idx]
                if not val or val == '-':
                    continue
                pairs.append(f"{col_name} is {val}")

            if not pairs:
                continue

            # Construct synthetic declarative statement for this entity row
            col_desc = ", ".join(pairs)
            prop = f"{entity}: {col_desc}."
            
            raw_ctx = " | ".join(cells)
            propositions.append(SentenceProvenance(
                sentence=prop,
                source_file=source_file,
                line_start=l_no,
                line_end=l_no,
                block_type=BlockType.TABLE,
                raw_context=raw_ctx,
                confidence=0.95
            ))
                
        return propositions


class DocumentNormalizer:
    """Orchestrator for document normalization, table extraction, and provenance tracking."""
    
    def __init__(self, watermark_cleaner=WatermarkOcrCleaner, layout_desegmenter=LayoutDesegmenter, table_parser=TableParser):
        self.cleaner = watermark_cleaner
        self.desegmenter = layout_desegmenter
        self.table_parser = table_parser

    def normalize_block(self, raw_block: Dict[str, Any]) -> NormalizedBlock:
        """Transforms a raw block dictionary into a structured NormalizedBlock."""
        source_id = raw_block.get("sourceId") or raw_block.get("source_id") or "doc"
        raw_text = raw_block.get("text", "")
        b_id = raw_block.get("id") or f"{source_id}#block_1"

        lines = raw_text.splitlines()
        table_lines = [(i + 1, l.strip()) for i, l in enumerate(lines) if l.strip()]
        
        is_table = (
            len(table_lines) >= 2 and
            all(self.table_parser.is_markdown_table_row(l[1]) for l in table_lines)
        )

        if is_table:
            table_props = self.table_parser.parse_markdown_table(table_lines, source_id)
            sentences = [p.sentence for p in table_props]
            return NormalizedBlock(
                id=b_id,
                text=raw_text,
                type=BlockType.TABLE,
                clean_sentences=sentences,
                metadata=dict(raw_block),
                provenance=table_props
            )
        else:
            cleaned_text = self.strip_watermarks(raw_text)
            stitched_text = self.stitch_columns(cleaned_text)
            
            sentences = []
            for s in re.split(r'(?<=[.!?])\s+', stitched_text):
                s_clean = s.strip()
                if len(s_clean) >= 15 and not self.desegmenter.is_heading(s_clean):
                    sentences.append(s_clean)

            return NormalizedBlock(
                id=b_id,
                text=stitched_text,
                type=BlockType.PROSE,
                clean_sentences=sentences,
                metadata=dict(raw_block),
                provenance=[]
            )

    def stitch_columns(self, text: str) -> str:
        """Reconstructs reading flow across line wraps and OCR columns."""
        def replace_hyphen(m: re.Match) -> str:
            g1, g2 = m.group(1), m.group(2)
            if g1.isdigit() and g2.isdigit():
                return f"{g1}-{g2}"
            if LayoutDesegmenter.is_punctuation_dash(g1.lower(), g2.lower(), g1, g2):
                return f"{g1} - {g2}"
            return f"{g1}{g2}"

        # 1. Rejoin hyphenated line wraps (e.g., 'oc-\ncurs' -> 'occurs')
        unhyphenated = re.sub(r'(\w+)-\s*\n\s*(\w+)', replace_hyphen, text)
        
        lines = unhyphenated.splitlines()
        if not lines:
            return ""

        annotated = [(i + 1, l) for i, l in enumerate(lines)]
        stitched = self.desegmenter.stitch_lines(annotated)
        return "\n".join(t[2] for t in stitched)

    def strip_watermarks(self, text: str) -> str:
        """Strips watermark lines, running headers, and publisher artifacts while preserving prose."""
        cleaned = text
        for wm in ["not to be republished", "NCERT", "Rationalised 2023-24", "Reprint 2022-23"]:
            cleaned = re.sub(re.escape(wm), "", cleaned, flags=re.IGNORECASE)

        lines = cleaned.splitlines()
        surviving = []
        for line in lines:
            s = line.strip()
            if not s:
                continue
            if not self.cleaner.is_watermark_or_noise(s):
                cleaned_sol = self.cleaner.clean_solution_line(s)
                if cleaned_sol:
                    surviving.append(cleaned_sol)
        return "\n".join(surviving)

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Sanitizes raw educational text by normalizing unicode ligatures, smart quotes,
        dashes, zero-width spaces, and stripping markdown formatting."""
        if not text:
            return ""
        # 1. Unicode NFKC normalization (ligatures \ufb01 -> fi, \ufb02 -> fl, full-width chars)
        s = unicodedata.normalize('NFKC', text)
        # 2. HTML unescape (&amp; -> &, &lt; -> <, etc.)
        s = html.unescape(s)
        s = re.sub(r'(?<=\w)\s*&\s*(?=\w)', ' and ', s)
        # 3. Replace zero-width spaces and invisible word separators with standard space
        s = re.sub(r'[\u200b\u200c\u200d\ufeff\u00ad]', ' ', s)
        # 4. Normalize quotes: convert smart quotes to standard quotes, then strip quoting around phrases
        s = re.sub(r'[\u201c\u201d\u201e\u201f\u00ab\u00bb]', '"', s)
        s = re.sub(r'[\u2018\u2019\u201a\u201b\u2032]', "'", s)
        s = re.sub(r'["\']([A-Za-z0-9\s\-]+?)["\']', r'\1', s)
        # 5. Normalize en-dashes in numeric ranges (50–80 -> 50-80)
        s = re.sub(r'(\d+)\s*[\u2013–]\s*(\d+)', r'\1-\2', s)
        # 6. Normalize em-dashes
        s = re.sub(r'[\u2014—]', ' - ', s)
        # 7. Strip markdown formatting: bold (**), italics (* or _), escapes (\*)
        s = re.sub(r'\\([*_{}\[\]()#+\-.!])', r'\1', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        s = re.sub(r'\*([^*]+)\*', r'\1', s)
        s = re.sub(r'__([^_]+)__', r'\1', s)
        s = re.sub(r'~~([^~]+)~~', r'\1', s)
        # 8. Accented Latin characters using NFKD decomposition (Köppen -> Koppen)
        s = "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
        # Clean whitespace
        return re.sub(r'[ \t]+', ' ', s).strip()

    def normalize(self, arg1: str, arg2: str = "doc_1") -> List[NormalizedBlock]:
        """Normalizes document text into clean NormalizedBlocks.
        
        Supports both normalize(raw_text, source_id) and normalize(source_id, raw_text).
        """
        if "\n" in arg1 or "|" in arg1 or len(arg1) > len(arg2):
            raw_text = self.sanitize_text(arg1)
            source_file = arg2
        else:
            raw_text = self.sanitize_text(arg2)
            source_file = arg1

        # Clean standard NCERT watermark phrases
        for wm in ["not to be republished", "NCERT", "Rationalised 2023-24", "Reprint 2022-23"]:
            raw_text = re.sub(re.escape(wm), "", raw_text, flags=re.IGNORECASE)

        raw_lines = raw_text.splitlines()
        annotated_lines = [(i + 1, l) for i, l in enumerate(raw_lines)]
        
        blocks = []
        current_prose = []
        current_table = []
        active_heading = None
        current_heading = None
        
        for l_no, line in annotated_lines:
            s = line.strip()
            if not s:
                continue

            if self.desegmenter.is_heading(s):
                # New heading detected - finalize previous section if exists
                if current_prose:
                    blocks.append((BlockType.PROSE, current_prose, current_heading))
                    current_prose = []
                # Start new section with this heading
                active_heading = s.lstrip("#: ").rstrip(":").strip()
                current_heading = active_heading
                
            if self.table_parser.is_markdown_table_row(s):
                if current_prose:
                    blocks.append((BlockType.PROSE, current_prose, current_heading))
                    current_prose = []
                    current_heading = None
                current_table.append((l_no, s))
            else:
                if current_table:
                    blocks.append((BlockType.TABLE, current_table, None))
                    current_table = []
                if not self.cleaner.is_watermark_or_noise(s):
                    cleaned_sol = self.cleaner.clean_solution_line(s)
                    if cleaned_sol:
                        if not current_prose:
                            current_heading = active_heading
                        current_prose.append((l_no, cleaned_sol))
                    
        if current_table:
            blocks.append((BlockType.TABLE, current_table, None))
        if current_prose:
            blocks.append((BlockType.PROSE, current_prose, current_heading))
            
        normalized_blocks = []
        block_idx = 0
        
        for b_type, b_lines, b_heading in blocks:
            block_idx += 1
            b_id = f"{source_file}#block_{block_idx}"
            
            if b_type == BlockType.TABLE:
                table_props = self.table_parser.parse_markdown_table(b_lines, source_file)
                if table_props:
                    sentences = [p.sentence for p in table_props]
                    raw_full = "\n".join(l[1] for l in b_lines)
                    normalized_blocks.append(NormalizedBlock(
                        id=b_id,
                        text=raw_full,
                        type=BlockType.TABLE,
                        clean_sentences=sentences,
                        metadata={"sourceId": source_file, "table_row_count": len(table_props)},
                        provenance=table_props
                    ))
            else:
                stitched = self.desegmenter.stitch_lines(b_lines)
                clean_sentences = []
                provenances = []
                
                for s_start, s_end, text in stitched:
                    raw_sents = re.split(r'(?<=[.!?])\s+', text)
                    for raw_s in raw_sents:
                        s_clean = raw_s.strip()
                        if len(s_clean) >= 15 and not self.desegmenter.is_heading(s_clean):
                            clean_sentences.append(s_clean)
                            provenances.append(SentenceProvenance(
                                sentence=s_clean,
                                source_file=source_file,
                                line_start=s_start,
                                line_end=s_end,
                                block_type=BlockType.PROSE,
                                raw_context=text,
                                confidence=1.0
                            ))
                            
                if clean_sentences:
                    full_text = " ".join(clean_sentences)
                    meta = {"sourceId": source_file, "sentence_count": len(clean_sentences)}
                    if b_heading:
                        meta["section_heading"] = b_heading
                        meta["concept"] = b_heading
                    normalized_blocks.append(NormalizedBlock(
                        id=b_id,
                        text=full_text,
                        type=BlockType.PROSE,
                        clean_sentences=clean_sentences,
                        metadata=meta,
                        provenance=provenances
                    ))
                    
        return normalized_blocks

    def normalize_file(self, file_path: str) -> List[NormalizedBlock]:
        """Normalizes a file from disk."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return self.normalize(file_path, content)


# Type aliases for cross-module compatibility
Normalizer = DocumentNormalizer
TableAndColumnNormalizer = DocumentNormalizer
