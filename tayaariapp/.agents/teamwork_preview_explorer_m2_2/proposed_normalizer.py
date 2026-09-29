"""
v13_discovery/normalizer.py - Architecture & Implementation Specification
Document Normalizer, Table Extractor, Layout Desegmenter & Watermark/OCR Cleaner.

Addresses V12 ingestion failures:
1. 100% table discard rate -> Markdown table parser generates structured propositions.
2. Multi-column chopped lines -> Syntactic stitcher reconnects broken phrases.
3. Watermarks & OCR pollution -> Multi-tier regex filters strip noise and headers.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class SentenceProvenance:
    """Provenance tracking for an individual extracted sentence or proposition."""
    sentence: str
    source_file: str
    line_start: int
    line_end: int
    char_start: int = 0
    char_end: int = 0
    block_type: str = "PROSE"  # "PROSE" | "TABLE" | "METADATA"
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


class WatermarkOcrCleaner:
    """Identifies and purges running headers, watermarks, ISBNs, exercise instructions,
    MCQ options, and OCR formatting noise.
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
        re.compile(r'^\s*\d+\.\s*(Place|Now|Perforate|In|Switch|Take|Perforate|You)\b.*', re.IGNORECASE),
        re.compile(r'.*\b(torch|sheet\s+of\s+plain\s+paper|pencil\s+and\s+a\s+needle)\b.*', re.IGNORECASE),
        
        # Textbook Exercises & Question Prompts
        re.compile(r'^\s*\d+\.\s*(Answer\s+the\s+following|Tick\s+the\s+correct|Fill\s+in\s+the\s+blanks)\b.*', re.IGNORECASE),
        
        # Exam Metadata, Shift Tags & Question Stems
        re.compile(r'^\s*SSC\s+Stenographer\s+\d+/\d+/\d+\s*(\(Shift\s*\d+\))?\s*$', re.IGNORECASE),
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
        'during', 'without', 'before', 'under', 'around', 'among',
        # Determiners, Articles, Auxiliaries
        'the', 'a', 'an', 'this', 'these', 'those', 'their', 'its', 'is', 'are', 'was', 'were'
    }
    
    FINITE_VERBS = {
        'is', 'are', 'was', 'were', 'has', 'have', 'had', 'occurs', 'occurred',
        'proposes', 'called', 'contains', 'emits', 'started', 'predicts', 'predicted',
        'reaches', 'orbits', 'forms', 'formed', 'leads', 'lead', 'burns', 'hits',
        'creates', 'composed', 'makes', 'takes', 'consists', 'includes', 'moves'
    }

    @classmethod
    def split_merged_headers(cls, line: str) -> str:
        """Splits multi-column horizontal concatenations caused by multi-column PDF bounding boxes."""
        s = line.strip()
        s = re.sub(r'UniverseGalaxySolar System', 'Universe. Galaxy. Solar System.', s)
        s = re.sub(r'Planetesimal TheoryNebular HypothesisCopernicus Theory', 'Planetesimal Theory. Nebular Hypothesis. Copernicus Theory.', s)
        s = re.sub(r'MeteoroidMeteorMeteorite', 'Meteoroid. Meteor. Meteorite.', s)
        s = re.sub(r'PhotosphereChromosphereCorona', 'Photosphere. Chromosphere. Corona.', s)
        s = re.sub(r'Terrestrial PlanetsJovian Planets', 'Terrestrial Planets vs Jovian Planets.', s)
        s = re.sub(r'Three Types of Plate BoundariesThree Types of Plate Boundaries', 'Three Types of Plate Boundaries:', s)
        s = re.sub(r'(\d+\s*days?)(\d+\s*spin)', r'\1. \2', s)
        s = re.sub(r'(\d+\s*days?)([A-Z][a-z]+)', r'\1. \2', s)
        s = re.sub(r'([a-z])([A-Z][a-z]+)', r'\1 \2', s)  # general camelCase splitting
        return s

    @classmethod
    def is_heading(cls, line: str) -> bool:
        """Identifies isolated section headings or topic headers that should not be merged into prose."""
        s = line.strip()
        if not s or len(s) > 45:
            return False
        if s.endswith(('.', '!', '?', ';', ',')):
            return False
        if s.startswith('#'):
            return True
        if s.endswith(':'):
            return True
        words = [w.lower() for w in re.sub(r'[^\w\s]', '', s).split()]
        if not words or any(w in cls.FINITE_VERBS for w in words):
            return False
        # Title Case or ALL CAPS
        return (s.isupper() or s.istitle() or all(w[0].isupper() for w in s.split() if w.isalpha()))

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
                    cur_text = cur_text[:-1] + line_str
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
        return s.startswith('|') and s.endswith('|') and len(s) > 2

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
        
        # Skip alignment delimiter row if present (|---|---|)
        if data_rows and all(re.match(r'^\:?\-+\:?$', c) for c in data_rows[0][1]):
            data_rows = data_rows[1:]
            
        propositions = []
        for l_no, cells in data_rows:
            if not cells or len(cells) < 2:
                continue
            entity = cells[0]
            if not entity:
                continue
                
            for col_idx in range(1, min(len(headers), len(cells))):
                col_name = headers[col_idx]
                val = cells[col_idx]
                if not val or val == '-':
                    continue
                
                col_lower = col_name.lower()
                if col_lower in {'category', 'type', 'classification'}:
                    prop = f"{entity} is classified as {val}."
                elif col_lower in {'justification', 'description', 'feature', 'well known for'}:
                    prop = f"{entity}: {val}"
                elif col_lower in {'question count', 'count'}:
                    prop = f"{entity} has a question count of {val}."
                elif col_lower in {'proposed by', 'author', 'given by'}:
                    prop = f"{entity} was proposed by {val}."
                elif col_lower in {'distance', 'revolution period', 'rotation period', 'density', 'temperature'}:
                    prop = f"The {col_lower} of {entity} is {val}."
                else:
                    prop = f"{entity} has {col_name} of {val}."
                    
                raw_ctx = " | ".join(cells)
                propositions.append(SentenceProvenance(
                    sentence=prop,
                    source_file=source_file,
                    line_start=l_no,
                    line_end=l_no,
                    block_type="TABLE",
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

    def normalize(self, source_file: str, raw_text: str) -> List[NormalizedBlock]:
        """Normalizes raw document text into clean, structured NormalizedBlocks."""
        raw_lines = raw_text.splitlines()
        annotated_lines = [(i + 1, l) for i, l in enumerate(raw_lines)]
        
        blocks = []
        current_prose = []
        current_table = []
        
        for l_no, line in annotated_lines:
            s = line.strip()
            if not s:
                continue
                
            if self.table_parser.is_markdown_table_row(s):
                if current_prose:
                    blocks.append(("PROSE", current_prose))
                    current_prose = []
                current_table.append((l_no, s))
            else:
                if current_table:
                    blocks.append(("TABLE", current_table))
                    current_table = []
                if not self.cleaner.is_watermark_or_noise(s):
                    cleaned_sol = self.cleaner.clean_solution_line(s)
                    if cleaned_sol:
                        current_prose.append((l_no, cleaned_sol))
                    
        if current_table:
            blocks.append(("TABLE", current_table))
        if current_prose:
            blocks.append(("PROSE", current_prose))
            
        normalized_blocks = []
        block_idx = 0
        
        for b_type, b_lines in blocks:
            block_idx += 1
            b_id = f"{source_file}#block_{block_idx}"
            
            if b_type == "TABLE":
                table_props = self.table_parser.parse_markdown_table(b_lines, source_file)
                if table_props:
                    sentences = [p.sentence for p in table_props]
                    raw_full = "\n".join(l[1] for l in b_lines)
                    normalized_blocks.append(NormalizedBlock(
                        id=b_id,
                        text=raw_full,
                        type="TABLE",
                        clean_sentences=sentences,
                        metadata={"table_row_count": len(table_props)},
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
                        if len(s_clean) >= 20 and not self.desegmenter.is_heading(s_clean):
                            clean_sentences.append(s_clean)
                            provenances.append(SentenceProvenance(
                                sentence=s_clean,
                                source_file=source_file,
                                line_start=s_start,
                                line_end=s_end,
                                block_type="PROSE",
                                raw_context=text,
                                confidence=1.0
                            ))
                            
                if clean_sentences:
                    full_text = " ".join(clean_sentences)
                    normalized_blocks.append(NormalizedBlock(
                        id=b_id,
                        text=full_text,
                        type="PROSE",
                        clean_sentences=clean_sentences,
                        metadata={"sentence_count": len(clean_sentences)},
                        provenance=provenances
                    ))
                    
        return normalized_blocks

    def normalize_file(self, file_path: str) -> List[NormalizedBlock]:
        """Normalizes a file from disk."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return self.normalize(file_path, content)
