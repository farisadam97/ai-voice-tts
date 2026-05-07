# Python Rules

## Code Style

- Follow PEP 8
- Use black for formatting
- Use isort for imports
- Maximum line length: 88 characters

## Type Safety

- Use type hints for all function signatures
- Use mypy for type checking
- Avoid `Any` type when possible

## Testing

- Use pytest
- Minimum 80% coverage
- Write tests before implementation (TDD)

## Audio Processing Specific

- Handle audio file errors gracefully
- Check sample rates match expected format
- Clean up temporary audio files
- Validate reference audio exists before cloning
