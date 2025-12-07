# Changelog

## [Fixed] - Agent Response Input Issue

### Critical Fix
- **Fixed**: System now correctly evaluates actual agent responses instead of comparing prompt to reference
- **Added**: `agent_response` field as required input in evaluation requests
- **Updated**: Evaluation logic now evaluates `agent_response` against `prompt`
- **Changed**: `reference` field is now optional and used only for accuracy comparison

### Backend Changes
- Updated `EvaluationInput` model to include required `agent_response` field
- Modified evaluation endpoints to use `agent_response` for evaluation
- Updated LLM providers to accept optional `reference` parameter
- Enhanced accuracy evaluation to compare agent_response with reference when provided
- Updated database schema to store `agent_response`

### Frontend Changes
- Added "Agent Response" input field to evaluation form (required)
- Updated form labels and hints for clarity
- Updated batch upload JSON placeholder with correct schema
- Updated sample data files

### Documentation Updates
- Updated API documentation with new request format
- Updated README with correct examples
- Updated code examples in documentation

### Breaking Changes
⚠️ **This is a breaking change** - Existing API clients must be updated:
- `agent_response` is now **required** in all evaluation requests
- `reference` is now **optional** (was previously used as the response to evaluate)

### Migration Guide
If you have existing code or data:
1. Update all API calls to include `agent_response` field
2. Move any data from `reference` to `agent_response` if it represents the actual agent output
3. Keep `reference` only if it's a ground truth answer for comparison

