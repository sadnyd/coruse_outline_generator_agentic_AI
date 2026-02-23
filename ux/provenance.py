"""
8.6 Provenance & Source Attribution - Track all data sources and influences.

For each module:
- Retrieved curriculum references (institution, year)
- Web sources (URLs, titles)
- Uploaded PDF influence (section references)

Academic integrity: Always visible, never hallucinated.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from utils.flow_logger import function_logger


class SourceType(Enum):
    """Types of sources."""
    CURRICULUM_RETRIEVAL = "curriculum_retrieval"
    WEB_SEARCH = "web_search"
    PDF_UPLOAD = "pdf_upload"
    GENERATED = "generated"


@dataclass
class Source:
    """Represents a single source."""
    source_type: SourceType
    title: str
    url: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[int] = None
    pdf_section: Optional[str] = None  # e.g., "pages 34-56"
    relevance_score: float = 1.0  # 0.0-1.0
    used_for: List[str] = field(default_factory=list)  # e.g., ["module_1", "module_2"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'type': self.source_type.value,
            'title': self.title,
            'url': self.url,
            'institution': self.institution,
            'year': self.year,
            'pdf_section': self.pdf_section,
            'relevance': self.relevance_score,
            'used_for': self.used_for,
        }


@dataclass
class ModuleProvenance:
    """Track all sources for a single module."""
    module_id: str
    module_title: str
    
    curriculum_sources: List[Source] = field(default_factory=list)
    web_sources: List[Source] = field(default_factory=list)
    pdf_sources: List[Source] = field(default_factory=list)
    
    # Direct generation (no sources)
    is_generated: bool = False
    generation_note: str = ""
    
    # Summary
    has_sources: bool = True
    source_quality: float = 1.0  # Average relevance
    
    def add_source(self, source: Source):
        """Add a source."""
        if source.source_type == SourceType.CURRICULUM_RETRIEVAL:
            self.curriculum_sources.append(source)
        elif source.source_type == SourceType.WEB_SEARCH:
            self.web_sources.append(source)
        elif source.source_type == SourceType.PDF_UPLOAD:
            self.pdf_sources.append(source)
        elif source.source_type == SourceType.GENERATED:
            self.is_generated = True
        
        self._update_quality()
    
    def _update_quality(self):
        """Update quality score based on sources."""
        all_sources = self.curriculum_sources + self.web_sources + self.pdf_sources
        
        if not all_sources:
            self.has_sources = False
            self.source_quality = 0.0
            return
        
        self.source_quality = sum(s.relevance_score for s in all_sources) / len(all_sources)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'module_id': self.module_id,
            'module_title': self.module_title,
            'curriculum_sources': [s.to_dict() for s in self.curriculum_sources],
            'web_sources': [s.to_dict() for s in self.web_sources],
            'pdf_sources': [s.to_dict() for s in self.pdf_sources],
            'is_generated': self.is_generated,
            'has_sources': self.has_sources,
            'source_quality': self.source_quality,
        }


@function_logger("Initialize provenance tracker")
class ProvenanceTracker:
    """Track and manage source attribution for outlines."""
    
    def __init__(self):
        """Initialize tracker."""
        self.provenance_map: Dict[str, ModuleProvenance] = {}
    
    @function_logger("Register module provenance")
    def register_module(self, module_id: str, title: str) -> ModuleProvenance:
        """Create provenance record for a module."""
        prov = ModuleProvenance(module_id=module_id, module_title=title)
        self.provenance_map[module_id] = prov
        return prov
    
    @function_logger("Add curriculum source")
    def add_curriculum_source(
        self,
        module_id: str,
        title: str,
        institution: str,
        year: int,
        relevance: float = 0.9
    ) -> bool:
        """Add a curriculum database reference."""
        if module_id not in self.provenance_map:
            self.register_module(module_id, "")
        
        source = Source(
            source_type=SourceType.CURRICULUM_RETRIEVAL,
            title=title,
            institution=institution,
            year=year,
            relevance_score=relevance
        )
        
        self.provenance_map[module_id].add_source(source)
        return True
    
    @function_logger("Add web source")
    def add_web_source(
        self,
        module_id: str,
        title: str,
        url: str,
        relevance: float = 0.7
    ) -> bool:
        """Add a web search result."""
        if module_id not in self.provenance_map:
            self.register_module(module_id, "")
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return False
        
        source = Source(
            source_type=SourceType.WEB_SEARCH,
            title=title,
            url=url,
            relevance_score=relevance
        )
        
        self.provenance_map[module_id].add_source(source)
        return True
    
    @function_logger("Add PDF source")
    def add_pdf_source(
        self,
        module_id: str,
        title: str,
        pdf_section: str,
        relevance: float = 0.85
    ) -> bool:
        """Add reference to uploaded PDF."""
        if module_id not in self.provenance_map:
            self.register_module(module_id, "")
        
        source = Source(
            source_type=SourceType.PDF_UPLOAD,
            title=title,
            pdf_section=pdf_section,
            relevance_score=relevance
        )
        
        self.provenance_map[module_id].add_source(source)
        return True
    
    @function_logger("Mark module as generated")
    def mark_generated(self, module_id: str, note: str = ""):
        """Mark module as AI-generated without sources."""
        if module_id not in self.provenance_map:
            self.register_module(module_id, "")
        
        prov = self.provenance_map[module_id]
        prov.is_generated = True
        prov.generation_note = note
        prov.has_sources = False
    
    @function_logger("Get provenance for module")
    def get_provenance(self, module_id: str) -> Optional[ModuleProvenance]:
        """Get provenance record for a module."""
        return self.provenance_map.get(module_id)
    
    @function_logger("Get all provenance")
    def get_all_provenance(self) -> Dict[str, ModuleProvenance]:
        """Get all provenance records."""
        return self.provenance_map.copy()
    
    @function_logger("Get integrity report")
    def get_integrity_report(self) -> Dict[str, Any]:
        """Generate report on source integrity."""
        report = {
            'total_modules': len(self.provenance_map),
            'modules_with_sources': 0,
            'modules_generated_only': 0,
            'total_sources': 0,
            'source_breakdown': {
                'curriculum': 0,
                'web': 0,
                'pdf': 0,
                'generated': 0,
            },
            'average_source_quality': 0.0,
            'hallucination_risk': 'low'
        }
        
        quality_scores = []
        
        for module_id, prov in self.provenance_map.items():
            if prov.has_sources:
                report['modules_with_sources'] += 1
            else:
                report['modules_generated_only'] += 1
            
            report['total_sources'] += len(prov.curriculum_sources)
            report['total_sources'] += len(prov.web_sources)
            report['total_sources'] += len(prov.pdf_sources)
            
            report['source_breakdown']['curriculum'] += len(prov.curriculum_sources)
            report['source_breakdown']['web'] += len(prov.web_sources)
            report['source_breakdown']['pdf'] += len(prov.pdf_sources)
            
            if prov.is_generated:
                report['source_breakdown']['generated'] += 1
            
            quality_scores.append(prov.source_quality)
        
        if quality_scores:
            report['average_source_quality'] = sum(quality_scores) / len(quality_scores)
        
        # Assess hallucination risk
        generated_ratio = report['modules_generated_only'] / max(1, report['total_modules'])
        if generated_ratio > 0.7:
            report['hallucination_risk'] = 'high'
        elif generated_ratio > 0.4:
            report['hallucination_risk'] = 'medium'
        else:
            report['hallucination_risk'] = 'low'
        
        return report
    
    @function_logger("Validate no hallucinations")
    def validate_no_hallucinations(self) -> tuple[bool, List[str]]:
        """
        Check for potential hallucinations.
        
        Returns: (is_clean, issues)
        """
        issues = []
        
        for module_id, prov in self.provenance_map.items():
            # Flag modules with no sources and no generation note
            if not prov.has_sources and not prov.is_generated:
                issues.append(f"{prov.module_title}: No sources and not marked as generated")
            
            # Flag low quality sources
            if prov.source_quality < 0.5:
                issues.append(f"{prov.module_title}: Low source quality ({prov.source_quality:.0%})")
        
        return len(issues) == 0, issues
    
    @function_logger("Export provenance")
    def to_dict(self) -> Dict[str, Any]:
        """Export all provenance data."""
        return {
            module_id: prov.to_dict()
            for module_id, prov in self.provenance_map.items()
        }
    
    @function_logger("Load provenance from dict")
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProvenanceTracker':
        """Load provenance from dictionary."""
        tracker = cls()
        # Implementation would deserialize the data
        # For now, return empty tracker
        return tracker


# Streamlit display helpers
@function_logger("Display provenance in streamlit")
def st_display_sources(provenance: ModuleProvenance):
    """Display sources for a module in Streamlit."""
    import streamlit as st
    
    if not provenance.has_sources and provenance.is_generated:
        st.info(f"✨ **AI-Generated**: {provenance.generation_note or 'Generated without specific sources'}")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if provenance.curriculum_sources:
            st.subheading(f"📚 Curriculum ({len(provenance.curriculum_sources)})")
            for source in provenance.curriculum_sources:
                st.caption(f"**{source.title}** ({source.year})")
                if source.institution:
                    st.caption(f"_{source.institution}_")
    
    with col2:
        if provenance.web_sources:
            st.subheading(f"🌐 Web Sources ({len(provenance.web_sources)})")
            for source in provenance.web_sources:
                st.caption(f"[{source.title}]({source.url})")
    
    with col3:
        if provenance.pdf_sources:
            st.subheading(f"📄 From PDF ({len(provenance.pdf_sources)})")
            for source in provenance.pdf_sources:
                st.caption(f"_pages {source.pdf_section}_")


@function_logger("Display integrity report in streamlit")
def st_display_integrity_report(report: Dict[str, Any]):
    """Display integrity report in Streamlit."""
    import streamlit as st
    
    st.markdown("### 🔍 Source Integrity Report")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Modules with Sources", report['modules_with_sources'])
    with col2:
        st.metric("AI-Generated Only", report['modules_generated_only'])
    with col3:
        st.metric("Source Quality", f"{report['average_source_quality']:.0%}")
    
    # Risk indicator
    risk_colors = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
    risk_emoji = risk_colors.get(report['hallucination_risk'], '⚪')
    st.write(f"{risk_emoji} **Hallucination Risk**: {report['hallucination_risk'].title()}")
    
    # Breakdown
    breakdown = report['source_breakdown']
    st.write("**Source Breakdown:**")
    st.write(f"- Curriculum: {breakdown['curriculum']}")
    st.write(f"- Web: {breakdown['web']}")
    st.write(f"- PDF: {breakdown['pdf']}")
    st.write(f"- AI-Generated: {breakdown['generated']}")
