"""
AI Features Package
Contains Gemini-powered, ML-based, and offline AI features

Note: Imports are lazy-loaded to avoid unnecessary dependencies
"""

__all__ = [
    # Offline AI features (no dependencies)
    "attendance_optimizer",
    "cgpa_calculator",
    "exam_schedule_optimizer",
    # Gemini features
    "smart_grade_predictor",
    "study_optimizer",
    "semester_insights",
    "study_guide",
    "vtop_coach",
    "performance_insights",
    "career_advisor",
    "voice_assistant",
    # ML features (lazy load due to sklearn)
    "academic_performance_ml",
]

# Lazy imports - modules loaded only when accessed
def __getattr__(name):
    """Lazy module loading to avoid importing heavy dependencies"""
    if name in __all__:
        import importlib
        return importlib.import_module(f".{name}", package="features")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


