# Layer 2 - POD Evaluator and Token Allocator

Layer 2 components for evaluating Proof-of-Discovery (POD) submissions and allocating SYNTH tokens.

## Components

### Evaluator (`evaluator/`)
- Evaluates POD submissions against Syntheverse criteria
- Validates discovery claims and research contributions
- Integrates with RAG API for knowledge verification
- Generates evaluation reports

### Allocator (`allocator/`)
- Calculates SYNTH token rewards based on POD evaluations
- Implements tokenomics rules and epoch-based distribution
- Manages token allocation schedules
- Tracks contributor rewards

## Status

🚧 **In Development** - Component scaffolding created, implementation pending.

## Integration

- **Input**: POD submissions from UI
- **Processing**: Evaluation via RAG API + custom criteria
- **Output**: Token allocation instructions to Layer 1 blockchain

