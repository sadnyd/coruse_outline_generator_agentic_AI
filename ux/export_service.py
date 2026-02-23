"""
8.7 Export System - Multi-format educator delivery (Markdown, PDF, JSON).

Exports reflect user edits.
Includes validator summary and learning outcomes.
Excludes internal metadata and regeneration logs.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from io import BytesIO
import re

from utils.flow_logger import function_logger


@function_logger("Initialize export service")
class ExportService:
    """Handle course outline exports in multiple formats."""
    
    @staticmethod
    @function_logger("Export to markdown")
    def export_markdown(
        outline: Dict[str, Any],
        include_validator_summary: bool = True,
        include_provenance: bool = False
    ) -> str:
        """
        Export outline as clean Markdown.
        
        Perfect for:
        - Learning management systems
        - Instruction documents
        - Sharing with stakeholders
        """
        lines = []
        
        # Title
        lines.append(f"# {outline.get('course_title', 'Untitled Course')}")
        lines.append("")
        
        # Summary
        if outline.get('course_summary'):
            lines.append(outline['course_summary'])
            lines.append("")
        
        # Metadata
        lines.append("## Course Information")
        lines.append("")
        lines.append(f"**Level:** {outline.get('audience_level', 'N/A').title()}")
        lines.append(f"**Category:** {outline.get('audience_category', 'N/A').title()}")
        lines.append(f"**Learning Mode:** {outline.get('learning_mode', 'N/A').replace('_', ' ').title()}")
        lines.append("")
        
        # Calculate total duration
        total_hours = sum(m.get('estimated_hours', 0) for m in outline.get('modules', []))
        lines.append(f"**Total Duration:** {total_hours} hours")
        lines.append("")
        
        # Course objectives
        if outline.get('course_objectives'):
            lines.append("## Learning Outcomes")
            lines.append("")
            for obj in outline['course_objectives']:
                bloom = obj.get('bloom_level', 'unknown').upper()
                lines.append(f"- {obj.get('statement', '')} _(Bloom: {bloom})_")
            lines.append("")
        
        # Modules
        lines.append("## Course Modules")
        lines.append("")
        
        for i, module in enumerate(outline.get('modules', []), 1):
            lines.append(f"### Module {i}: {module.get('title', 'Untitled')}")
            lines.append("")
            
            if module.get('description'):
                lines.append(module['description'])
                lines.append("")
            
            # Duration and ID
            lines.append(f"**Duration:** {module.get('estimated_hours', 0)} hours")
            lines.append("")
            
            # Learning objectives
            if module.get('learning_objectives'):
                lines.append("#### Learning Objectives")
                lines.append("")
                for j, obj in enumerate(module['learning_objectives'], 1):
                    lines.append(f"{j}. {obj.get('statement', '')}")
                    bloom = obj.get('bloom_level', 'unknown')
                    lines.append(f"   - _Bloom Level: {bloom.title()}_")
                lines.append("")
            
            # Lessons
            if module.get('lessons'):
                lines.append("#### Lessons")
                lines.append("")
                for lesson in module['lessons']:
                    lines.append(f"- **{lesson.get('title', 'Untitled')}**")
                    if lesson.get('description'):
                        lines.append(f"  - {lesson['description']}")
                lines.append("")
            
            # Assessments
            if module.get('assessments'):
                lines.append("#### Assessments")
                lines.append("")
                for assessment in module['assessments']:
                    lines.append(f"- **{assessment.get('title', 'Assessment')}** ({assessment.get('type', 'Unknown')})")
                    if assessment.get('description'):
                        lines.append(f"  - {assessment['description']}")
                lines.append("")
        
        # Capstone
        if outline.get('capstone'):
            capstone = outline['capstone']
            lines.append("## Capstone Project")
            lines.append("")
            lines.append(f"### {capstone.get('title', 'Capstone')}")
            lines.append("")
            if capstone.get('description'):
                lines.append(capstone['description'])
                lines.append("")
            
            if capstone.get('requirements'):
                lines.append("**Requirements:**")
                for req in capstone['requirements']:
                    lines.append(f"- {req}")
                lines.append("")
        
        # Evaluation
        if outline.get('evaluation_strategy'):
            lines.append("## Evaluation Strategy")
            lines.append("")
            lines.append(outline['evaluation_strategy'])
            lines.append("")
        
        # Validator summary (optional)
        if include_validator_summary and outline.get('_validator_feedback'):
            lines.append("---")
            lines.append("## Quality Assessment")
            lines.append("")
            feedback = outline['_validator_feedback']
            if feedback.get('quality_score'):
                lines.append(f"**Overall Quality Score:** {feedback['quality_score']:.0%}")
                lines.append("")
        
        # Footer
        lines.append("---")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(lines)
    
    @staticmethod
    @function_logger("Export to JSON")
    def export_json(
        outline: Dict[str, Any],
        include_metadata: bool = False,
        pretty: bool = True
    ) -> str:
        """
        Export as JSON for LMS integration or API use.
        
        Excludes:
        - Internal metadata (prefixed with _)
        - Regeneration logs
        - Edit history
        """
        export = {}
        
        # Copy all visible fields
        for key, value in outline.items():
            if not key.startswith('_'):
                export[key] = value
        
        # Add metadata if requested
        if include_metadata:
            export['_metadata'] = {
                'export_time': datetime.now().isoformat(),
                'version': '1.1',
                'schema': 'course_outline_v1'
            }
        
        if pretty:
            return json.dumps(export, indent=2, default=str)
        else:
            return json.dumps(export, default=str)
    
    @staticmethod
    @function_logger("Export to PDF")
    def export_pdf(
        outline: Dict[str, Any],
        **kwargs
    ) -> bytes:
        """
        Export as PDF (print-ready).
        
        Requires markdown first, then converts to PDF.
        Returns bytes for download.
        """
        # First generate Markdown
        markdown = ExportService.export_markdown(outline, **kwargs)
        
        # Convert to PDF using markdown-pdf converter
        try:
            import pypandoc
            pdf_bytes = pypandoc.convert_text(
                markdown,
                'pdf',
                format='md'
            )
            return pdf_bytes
        except ImportError:
            # Fallback if pypandoc not available
            # Return markdown converted to bytes as alternative
            return markdown.encode('utf-8')
    
    @staticmethod
    @function_logger("Validate export")
    def validate_export(
        format_type: str,
        data: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate exported data format.
        
        Returns: (is_valid, error_message)
        """
        if format_type == 'json':
            try:
                json.loads(data)
                return True, None
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON: {str(e)}"
        
        elif format_type == 'markdown':
            # Basic checks
            if not data or len(data) < 100:
                return False, "Markdown output too short"
            
            if '# ' not in data:
                return False, "Missing title in Markdown"
            
            return True, None
        
        return True, None
    
    @staticmethod
    @function_logger("Generate export filename")
    def generate_filename(
        course_title: str,
        format_type: str
    ) -> str:
        """Generate clean filename for export."""
        # Sanitize course title
        clean_title = re.sub(r'[^a-zA-Z0-9_-]', '_', course_title)
        clean_title = re.sub(r'_+', '_', clean_title).strip('_')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        extension_map = {
            'markdown': 'md',
            'json': 'json',
            'pdf': 'pdf',
            'md': 'md',
        }
        
        ext = extension_map.get(format_type, format_type)
        return f"{clean_title}_{timestamp}.{ext}"
    
    @staticmethod
    @function_logger("Export with summary")
    def export_with_summary(
        outline: Dict[str, Any],
        format_type: str = 'markdown',
        validator_summary: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export complete with metadata.
        
        Returns:
        {
            'format': 'markdown',
            'filename': 'course_title_20231122.md',
            'size_bytes': 5000,
            'content': '...',
            'valid': True,
        }
        """
        # Generate content
        if format_type in ['markdown', 'md']:
            content = ExportService.export_markdown(outline)
            ext = 'md'
        elif format_type == 'json':
            content = ExportService.export_json(outline)
            ext = 'json'
        elif format_type == 'pdf':
            content = ExportService.export_pdf(outline)
            ext = 'pdf'
        else:
            return {'valid': False, 'error': f'Unknown format: {format_type}'}
        
        # Validate
        if isinstance(content, bytes):
            size = len(content)
            valid = size > 0
        else:
            size = len(content.encode('utf-8'))
            valid = True
        
        # Generate filename
        filename = ExportService.generate_filename(
            outline.get('course_title', 'course'),
            ext
        )
        
        return {
            'valid': valid,
            'format': format_type,
            'filename': filename,
            'size_bytes': size,
            'content': content,
            'created_at': datetime.now().isoformat(),
        }


# Streamlit helpers
@function_logger("Create streamlit download button for export")
def st_download_export(
    content: str,
    filename: str,
    format_type: str,
    label: str = "Download"
):
    """Create Streamlit download button for export."""
    import streamlit as st
    
    mime_type_map = {
        'markdown': 'text/markdown',
        'md': 'text/markdown',
        'json': 'application/json',
        'pdf': 'application/pdf',
    }
    
    mime = mime_type_map.get(format_type, 'text/plain')
    
    st.download_button(
        label=label,
        data=content,
        file_name=filename,
        mime=mime,
        use_container_width=True
    )
