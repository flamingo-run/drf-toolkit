# Models

DRF Toolkit provides enhanced model functionality through various base classes and mixins. Each model type serves a specific purpose and can be combined with others to create more complex functionality.

## Available Models

### Base Models
- [Base Models](base.md) - Core functionality and timestamp tracking
- [Diff Models](diff.md) - Track field changes in models

### Feature Models
- [Availability Models](availability.md) - Time-based availability management
- [File Models](file.md) - File handling and storage
- [Inheritance Models](inheritance.md) - Model inheritance capabilities
- [Ordered Models](ordered.md) - Ordered item management
- [Soft Delete Models](soft_delete.md) - Soft deletion functionality

### Combined Models
For more complex use cases, these models can be combined. See [Model Combinations](combinations.md) for examples and best practices.

## Best Practices

1. Always inherit from the appropriate base model for your use case
2. Use the provided model managers for consistent behavior
3. Consider using soft delete when data history is important
4. Leverage the diff tracking for audit logs and change tracking
5. Combine models thoughtfully to avoid complexity

For detailed documentation on each model type, click the respective links above.