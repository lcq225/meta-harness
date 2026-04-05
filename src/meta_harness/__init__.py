# -*- coding: utf-8 -*-
"""
Meta-Harness: Agent Output Quality Evaluation and Experience Tracking System

A comprehensive system for evaluating AI agent outputs and tracking execution experiences.
"""

from meta_harness.evaluator import HarnessEvaluator, quick_evaluate, EvaluationResult
from meta_harness.tracker import ExperienceTracker

__version__ = "1.0.0"
__author__ = "Meta-Harness Team"

__all__ = [
    "HarnessEvaluator",
    "quick_evaluate",
    "EvaluationResult",
    "ExperienceTracker",
]