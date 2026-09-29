"""
V13.1 Generator Package
=======================
Complete rewrite of the V13 question generation pipeline.
Fixes all 12 systemic failures identified by independent Opus audit.

Architecture:
  SOURCE EVIDENCE → KNOWLEDGE UNIT → QUESTION INTENT → ANSWER CONTRACT
  → DISTRACTOR CONTRACT → QUESTION → INDEPENDENT VALIDATION → ACCEPT
"""
