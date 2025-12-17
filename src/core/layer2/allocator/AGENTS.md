# Token Allocator Agents

## Purpose

Calculates and validates SYNTH token allocations based on PoC and PoD evaluation scores. Implements comprehensive tokenomics rules including tier multipliers, epoch validation, and balance management.

## Key Modules

### TokenAllocator Class (`token_allocator.py`)

Core allocation computation agent:

- **`__init__()`**: Initialize with base reward and tokenomics parameters
- **`calculate_reward()`**: Main allocation calculation method
- **`_calculate_bonuses()`**: Apply evaluation-based reward bonuses
- **`_validate_evaluation_input()`**: Input validation and error checking
- **`get_allocation_summary()`**: Generate detailed allocation reports

### Tokenomics Integration

Allocation validation and state management:

- **Tier Availability**: Verify tier access for specific epochs
- **Balance Checking**: Ensure sufficient epoch token reserves
- **State Updates**: Coordinate with tokenomics state persistence
- **Transaction Preparation**: Format allocations for blockchain submission

## Integration Points

### Evaluation Systems

- **PoC Server**: Receives multi-metal allocation requests
- **PoD Server**: Processes legacy single-tier allocations
- **Evaluation Results**: Consumes scores from Grok API evaluations

### Tokenomics State

- **Balance Verification**: Check epoch token availability
- **Allocation Recording**: Update persistent allocation history
- **State Synchronization**: Maintain consistency across server restarts
- **Statistics Tracking**: Provide allocation analytics

### Blockchain Layer

- **Transaction Creation**: Format allocations for Layer 1 submission
- **Balance Updates**: Trigger epoch balance reductions
- **Validation Confirmation**: Receive allocation confirmations
- **Error Handling**: Manage blockchain submission failures

## Development Guidelines

### Allocation Logic

- **Formula Consistency**: Maintain precise tokenomics calculations
- **Tier Enforcement**: Strictly validate tier availability rules
- **Balance Protection**: Prevent over-allocation of epoch reserves
- **Error Transparency**: Provide clear allocation failure reasons

### State Management

- **Atomic Updates**: Ensure allocation and balance changes are consistent
- **Rollback Support**: Implement allocation reversal mechanisms
- **Audit Trails**: Maintain comprehensive allocation history
- **Synchronization**: Handle concurrent allocation requests

### Validation Rules

- **Input Sanitization**: Validate all evaluation and epoch inputs
- **Range Checking**: Ensure scores and parameters within valid ranges
- **Business Rules**: Enforce tokenomics policy constraints
- **Error Propagation**: Surface meaningful error messages

## Common Patterns

### Allocation Workflow

1. **Input Validation**: Verify evaluation data and epoch parameters
2. **Tier Verification**: Confirm requested tier available in epoch
3. **Balance Checking**: Validate sufficient epoch token reserves
4. **Reward Calculation**: Apply tokenomics formula with bonuses
5. **State Update**: Record allocation in persistent storage
6. **Transaction Preparation**: Format for blockchain submission
7. **Response Generation**: Return detailed allocation results

### Error Recovery

- **Validation Failures**: Clear error messages for invalid inputs
- **Balance Shortages**: Handle insufficient epoch reserves
- **State Conflicts**: Resolve concurrent allocation conflicts
- **Blockchain Errors**: Manage Layer 1 submission failures

## Key Functions

### TokenAllocator

- `calculate_reward(evaluation, epoch)`: Main allocation calculation
- `_calculate_bonuses(scores, base_tokens)`: Apply evaluation bonuses
- `_validate_evaluation_input(evaluation, epoch)`: Input validation
- `get_allocation_summary(allocation)`: Generate allocation reports

### Helper Methods

- **Tier Validation**: Check epoch-specific tier availability
- **Balance Verification**: Confirm epoch token sufficiency
- **Bonus Calculation**: Apply novelty and significance multipliers
- **Error Formatting**: Generate consistent error responses

## Performance Characteristics

- **Calculation Speed**: Sub-millisecond per allocation request
- **Memory Usage**: Minimal memory footprint for computation
- **Concurrent Safety**: Thread-safe allocation processing
- **Scalability**: Linear performance with allocation volume

## Error Scenarios

### Validation Errors

- **Invalid Scores**: PoD scores outside acceptable ranges
- **Tier Unavailable**: Requested tier not permitted in epoch
- **Epoch Invalid**: Non-existent or inactive epoch specified
- **Input Malformed**: Missing or incorrect evaluation data

### Allocation Errors

- **Insufficient Balance**: Allocation exceeds epoch token supply
- **State Corruption**: Tokenomics state inconsistency
- **Concurrent Conflicts**: Multiple allocations attempting same resources
- **Blockchain Rejection**: Layer 1 transaction failures

### System Errors

- **Database Failure**: Tokenomics state persistence issues
- **Network Timeout**: Blockchain communication problems
- **Resource Exhaustion**: Memory or processing capacity limits

## Quality Assurance

### Calculation Accuracy

- **Formula Verification**: Validate tokenomics mathematical correctness
- **Bonus Application**: Ensure proper multiplier calculations
- **Rounding Consistency**: Maintain precision in token amounts
- **Edge Case Handling**: Test boundary conditions and extremes

### State Integrity

- **Balance Consistency**: Verify epoch balances remain accurate
- **History Completeness**: Ensure all allocations are recorded
- **Synchronization**: Confirm state consistency across components
- **Recovery Testing**: Validate state restoration after failures

## Testing and Validation

### Unit Tests

- **Calculation Logic**: Test tokenomics formula implementations
- **Validation Rules**: Verify input validation and error handling
- **Tier Availability**: Test epoch-specific tier access rules
- **Bonus Calculations**: Validate multiplier and bonus applications

### Integration Tests

- **State Integration**: Test with tokenomics state persistence
- **Blockchain Connection**: Verify Layer 1 transaction handling
- **Concurrent Access**: Test multi-threaded allocation scenarios
- **Error Propagation**: Validate error handling across components

## Tokenomics Rules Implementation

### Tier Multipliers

- **Gold**: 1000x multiplier, available all epochs
- **Silver**: 100x multiplier, Community and Ecosystem epochs
- **Copper**: 1x multiplier, Pioneer, Community, Ecosystem epochs

### Epoch Structure

- **Founder**: 45T supply, Gold tier only
- **Pioneer**: 22.5T supply, Gold and Copper tiers
- **Community**: 11.25T supply, all tiers available
- **Ecosystem**: 11.25T supply, all tiers available

### Bonus System

- **Novelty Bonus**: Additional rewards for high novelty scores
- **Significance Bonus**: Extra tokens for significant contributions
- **Epoch Bonus**: Decreasing bonus for early participation

## Monitoring and Observability

### Allocation Metrics

- **Volume Tracking**: Monitor allocation frequency and amounts
- **Tier Distribution**: Track allocation patterns by tier
- **Epoch Utilization**: Measure epoch balance consumption
- **Error Rates**: Monitor allocation failure frequencies

### Performance Monitoring

- **Latency Tracking**: Measure allocation calculation times
- **Resource Usage**: Monitor memory and CPU consumption
- **Throughput Metrics**: Track allocations per second capacity
- **Error Patterns**: Identify common failure modes

## Future Enhancements

- **Dynamic Tokenomics**: ML-based reward adjustment
- **Community Governance**: Allocation parameter voting
- **Advanced Bonuses**: Context-aware reward multipliers
- **Prediction Markets**: Allocation outcome forecasting
- **Cross-Chain Support**: Multi-blockchain allocation capabilities</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/core/layer2/allocator/AGENTS.md
