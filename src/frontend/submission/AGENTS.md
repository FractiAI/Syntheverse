# Submission Interface Agents

## Purpose

User interface for submitting Proof-of-Contribution (PoC) and Proof-of-Discovery (PoD) to the Syntheverse system.

## Key Modules

### Submission UI (`src/`)

- **HTML Interface**: Basic HTML scaffold for submission interface
- **Document Upload**: File upload functionality for PDFs and documents
- **Form Handling**: Contributor information and category selection
- **Status Tracking**: Submission status and progress monitoring
- **Evaluation Display**: Real-time evaluation results and scoring
- **Token Rewards**: Display of allocated SYNTH tokens
- **Certificate Generation**: PoD certificate creation and download

## Integration Points

- Submission interface connects to PoC API for contribution submission
- Links to Layer 2 evaluation system for real-time processing
- Integrates with Layer 1 blockchain for token allocation
- Uses frontend file upload and validation
- Connects to notification system for status updates

## Development Guidelines

- Implement secure file upload with validation
- Provide clear progress indicators during evaluation
- Ensure mobile-friendly responsive design
- Include offline submission capabilities
- Test file upload limits and error handling

## Common Patterns

- Document submission workflows
- File upload interfaces
- Progress tracking displays
- Status notification systems
- Certificate generation and display





