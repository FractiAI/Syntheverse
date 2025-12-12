"""
PDF Generator for PoD Reports and Certificates
Generates PDF documents for PoD submissions and certificates.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
from pathlib import Path
import json


class PODPDFGenerator:
    """Generate PDF reports and certificates for PoD submissions."""
    
    def __init__(self, output_dir: str = "test_outputs/pdf_reports"):
        """
        Initialize PDF generator.
        
        Args:
            output_dir: Directory for output PDFs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Check if styles already exist before adding
        if 'PODTitle' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='PODTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=30,
                alignment=TA_CENTER
            ))
        
        if 'PODHeading' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='PODHeading',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#764ba2'),
                spaceAfter=12,
                spaceBefore=12
            ))
        
        if 'PODBody' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='PODBody',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=12
            ))
        
        if 'CertificateTitle' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='CertificateTitle',
                parent=self.styles['Heading1'],
                fontSize=32,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=20,
                alignment=TA_CENTER
            ))
    
    def generate_report_pdf(self, submission: dict, report_data: dict = None) -> str:
        """
        Generate PDF report for a PoD submission.
        
        Args:
            submission: Submission data
            report_data: Optional report data (will load if not provided)
        
        Returns:
            Path to generated PDF file
        """
        submission_hash = submission.get('submission_hash', 'unknown')
        filename = f"pod_report_{submission_hash}.pdf"
        filepath = self.output_dir / filename
        
        # Load report data if not provided
        if not report_data:
            report_dir = Path('test_outputs/pod_reports')
            report_files = list(report_dir.glob(f"{submission_hash}_*.json"))
            if report_files:
                latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
                with open(latest_report, 'r') as f:
                    report_data = json.load(f)
        
        # Create PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("Syntheverse Proof-of-Discovery Report", self.styles['PODTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Submission Details
        story.append(Paragraph("Submission Details", self.styles['PODHeading']))
        
        submission_table_data = [
            ['Title:', submission.get('title', 'N/A')],
            ['Submission Hash:', submission_hash[:32] + '...'],
            ['Contributor:', submission.get('contributor', 'N/A')],
            ['Category:', submission.get('category', 'N/A').title()],
            ['Submitted:', submission.get('timestamp', 'N/A')],
            ['Status:', submission.get('status', 'pending').upper()],
        ]
        
        submission_table = Table(submission_table_data, colWidths=[2*inch, 4.5*inch])
        submission_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(submission_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Evaluation Results
        if report_data and report_data.get('evaluation'):
            evaluation = report_data['evaluation']
            story.append(Paragraph("Evaluation Results", self.styles['PODHeading']))
            
            eval_table_data = [
                ['Metric', 'Score', 'Description'],
                ['Coherence', f"{evaluation.get('coherence', 0):.0f}/10000", 
                 'Fractional fractal grammar closure and structural consistency'],
                ['Density', f"{evaluation.get('density', 0):.0f}/10000",
                 'Structural contribution per fractal unit'],
                ['Novelty', f"{evaluation.get('novelty', 0):.0f}/10000",
                 'Non-redundancy relative to existing knowledge'],
                ['PoD Score', f"{report_data.get('pod_score', 0):.2f}/10000",
                 'Overall Proof-of-Discovery score'],
                ['Tier', evaluation.get('tier', 'N/A').title(),
                 'Contribution tier classification'],
                ['Qualified Epoch', report_data.get('qualified_epoch', 'N/A').title(),
                 'Epoch qualification based on density'],
            ]
            
            eval_table = Table(eval_table_data, colWidths=[1.5*inch, 1.5*inch, 3.5*inch])
            eval_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))
            
            story.append(eval_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Reasoning
            if evaluation.get('reasoning'):
                story.append(Paragraph("Evaluation Reasoning", self.styles['PODHeading']))
                story.append(Paragraph(evaluation['reasoning'], self.styles['PODBody']))
                story.append(Spacer(1, 0.3*inch))
        
        # Token Allocation
        if report_data and report_data.get('allocation') and report_data['allocation'].get('success'):
            allocation = report_data['allocation']
            story.append(Paragraph("Token Allocation", self.styles['PODHeading']))
            
            alloc_table_data = [
                ['Epoch:', allocation.get('epoch', 'N/A').title()],
                ['Tier:', allocation.get('tier', 'N/A').title()],
                ['PoD Score:', f"{allocation.get('pod_score', 0):.2f}"],
                ['SYNTH Tokens Allocated:', f"{allocation.get('reward', 0):,.2f}"],
            ]
            
            alloc_table = Table(alloc_table_data, colWidths=[2*inch, 4.5*inch])
            alloc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4caf50')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            
            story.append(alloc_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['PODBody']
        ))
        story.append(Paragraph(
            "Syntheverse Proof-of-Discovery Protocol",
            self.styles['PODBody']
        ))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def generate_certificate_pdf(self, submission: dict, allocation: dict) -> str:
        """
        Generate PoD certificate PDF for awarded submissions.
        
        Args:
            submission: Submission data
            allocation: Token allocation data
        
        Returns:
            Path to generated certificate PDF
        """
        submission_hash = submission.get('submission_hash', 'unknown')
        filename = f"pod_certificate_{submission_hash}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Certificate Border (using table)
        border_table = Table([['']], colWidths=[6.5*inch], rowHeights=[9*inch])
        border_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (0, 0), 3, colors.HexColor('#667eea')),
            ('LINEABOVE', (0, 0), (0, 0), 3, colors.HexColor('#667eea')),
            ('LINEBEFORE', (0, 0), (0, 0), 3, colors.HexColor('#667eea')),
            ('LINEAFTER', (0, 0), (0, 0), 3, colors.HexColor('#667eea')),
        ]))
        
        story.append(Spacer(1, 0.5*inch))
        story.append(border_table)
        
        # Certificate Content
        story = []  # Reset for proper layout
        
        # Title
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph("CERTIFICATE OF DISCOVERY", self.styles['CertificateTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        story.append(Paragraph(
            "Proof-of-Discovery Protocol",
            ParagraphStyle(
                name='Subtitle',
                parent=self.styles['Normal'],
                fontSize=18,
                textColor=colors.HexColor('#764ba2'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
        ))
        story.append(Spacer(1, 0.5*inch))
        
        # Award text
        award_text = f"""
        This certifies that<br/><br/>
        <b>{submission.get('contributor', 'Contributor')}</b><br/><br/>
        has successfully contributed to the Syntheverse knowledge base through the
        Proof-of-Discovery protocol.
        """
        story.append(Paragraph(award_text, ParagraphStyle(
            name='AwardText',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=30
        )))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Submission details
        details_table_data = [
            ['Title:', submission.get('title', 'N/A')],
            ['Submission Hash:', submission_hash[:32] + '...'],
            ['Category:', submission.get('category', 'N/A').title()],
            ['Tier:', allocation.get('tier', 'N/A').title()],
            ['Epoch:', allocation.get('epoch', 'N/A').title()],
            ['PoD Score:', f"{allocation.get('pod_score', 0):.2f}/10000"],
            ['SYNTH Tokens Awarded:', f"{allocation.get('reward', 0):,.2f}"],
        ]
        
        details_table = Table(details_table_data, colWidths=[2.5*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Blockchain registration instructions
        story.append(Paragraph("Blockchain Registration", ParagraphStyle(
            name='InstructionsTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#667eea'),
            alignment=TA_CENTER,
            spaceAfter=15
        )))
        
        instructions = """
        <b>To register this certificate on the Syntheverse blockchain:</b><br/><br/>
        
        1. Visit the Syntheverse platform at: <b>http://localhost:5000</b><br/>
        2. Navigate to the "Register Certificate" section<br/>
        3. Enter your submission hash: <b>{}</b><br/>
        4. Verify your contributor ID: <b>{}</b><br/>
        5. Submit the registration transaction<br/><br/>
        
        Your certificate will be permanently recorded on the blockchain, providing
        immutable proof of your contribution to the Syntheverse knowledge base.
        """.format(
            submission_hash,
            submission.get('contributor', 'N/A')
        )
        
        story.append(Paragraph(instructions, ParagraphStyle(
            name='Instructions',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            leftIndent=0.5*inch,
            rightIndent=0.5*inch,
            spaceAfter=20
        )))
        
        # Date and signature
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"Issued: {datetime.now().strftime('%B %d, %Y')}",
            ParagraphStyle(
                name='Date',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER
            )
        ))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            "Syntheverse Proof-of-Discovery Protocol",
            ParagraphStyle(
                name='Signature',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#667eea')
            )
        ))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)


if __name__ == "__main__":
    # Test PDF generation
    generator = PODPDFGenerator()
    
    test_submission = {
        "submission_hash": "test123",
        "title": "Test Paper",
        "contributor": "researcher-001",
        "category": "scientific",
        "status": "approved",
        "timestamp": datetime.now().isoformat()
    }
    
    test_allocation = {
        "epoch": "founder",
        "tier": "gold",
        "pod_score": 7429.0,
        "reward": 1234567.89
    }
    
    # Generate certificate
    cert_path = generator.generate_certificate_pdf(test_submission, test_allocation)
    print(f"Certificate generated: {cert_path}")
