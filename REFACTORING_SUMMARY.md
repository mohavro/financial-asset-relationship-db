# Refactoring Summary for `graph_visuals.py`

## Performance Improvements

### Reduced Computational Complexity

1. **Combined Data Processing Pipeline**:
   - Merged `_collect_relationships` and `_group_relationships` into a single `_collect_and_group_relationships` function
   - Eliminated redundant passes through the relationship data
   - Reduced memory overhead by avoiding intermediate data structures

2. **Optimized Lookups**:
   - Created `asset_id_to_idx` mapping once and reused it across functions
   - Passed the mapping as a parameter to avoid recreating it in each function call
   - Used set-based lookups consistently for O(1) membership testing

3. **Improved Directional Arrow Detection**:
   - Replaced nested loops with set-based lookups for detecting unidirectional relationships
   - Pre-built relationship sets for faster reverse relationship detection

### Code Structure Improvements

1. **Enhanced Type Annotations**:
   - Added proper type hints for all functions
   - Used Optional and Dict types for better code clarity

2. **Improved Function Signatures**:
   - Added optional parameters to avoid redundant computations
   - Standardized parameter ordering and naming

3. **Better Documentation**:
   - Added detailed docstrings explaining function purpose and parameters
   - Included performance considerations in comments

## Addressing CodeFactor Issues

1. **Duplication Removal**:
   - Consolidated duplicated styling and formatting logic into helper functions

2. **Complexity Reduction**:
   - Decomposed complex functions into smaller, single-purpose functions
   - Simplified conditional logic by using data structures more effectively
