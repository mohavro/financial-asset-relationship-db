# Performance Optimizations

This document summarizes the performance-oriented refactors made to the 3D graph visualizations.

## Highlights

- Centralized styling and color mapping for relationship types to reduce duplicated logic.
- **O(1) lookups via pre-built indices** for asset IDs and relationship pairs, avoiding repeated list.index() calls and O(n) iterations.
- Single-pass collection and grouping of relationships to reduce complexity and improve throughput.
- Pre-allocation of arrays for edge coordinates and hovertexts to minimize dynamic resizing and allocations.
- Vectorized NumPy operations where appropriate to reduce Python-level loops.

## Specific Changes

1. **Relationship Processing** (Addresses Code Review Feedback)
   - Introduced an index `(source, target, type) -> strength` via `_build_relationship_index()` to enable **constant-time O(1) reverse lookup** and bidirectionality checks.
   - This optimization directly addresses the review comment about improving time complexity from O(n) to O(1) for relationship existence checks.
   - Removed redundant passes and replaced tuple sorting with a simple canonical pair key.
   - The relationship index is built once and reused for all lookups, significantly improving performance for large graphs.

2. Edge Building
   - Replaced repeated extend() calls with pre-allocated lists sized to the exact number of values.
   - Uses O(1) asset ID lookups via `_build_asset_id_index()` instead of O(n) list.index() calls.

3. Directional Arrows
   - Replaced per-edge Python-loop arithmetic with vectorized NumPy operations for arrow positions:
     - Compute arrow positions at 70% along the edge using: `src + 0.7 * (tgt - src)`
     - This significantly reduces overhead for large graphs.
   - Uses pre-built relationship index for O(1) reverse relationship checks.

## Performance Impact

### Before Optimization
- Checking for reverse relationships: **O(n)** per relationship (iterating through all relationships)
- Asset ID lookups: **O(n)** per lookup (using list.index())
- Total complexity for relationship processing: **O(n²)** for n relationships

### After Optimization
- Checking for reverse relationships: **O(1)** per relationship (dictionary lookup)
- Asset ID lookups: **O(1)** per lookup (dictionary lookup)
- Total complexity for relationship processing: **O(n)** for n relationships

This represents a significant performance improvement, especially for graphs with thousands of relationships.

## Code Review Response

The optimization strategy implemented in this PR directly addresses the code review feedback:

> "The function `_build_relationship_set` iterates through all relationships for a given source ID to check if both source and target IDs are in `asset_ids`. This approach has a time complexity of O(n) for each call, which can be inefficient if the number of relationships is large."

**Implementation:**
- Created `_build_relationship_index()` function that converts relationships into a dictionary for O(1) lookups
- Used this index in both `_collect_and_group_relationships()` and `_create_directional_arrows()`
- Eliminated all O(n) iterations for relationship existence checks
- Added explicit comments in the code highlighting these optimizations

## Notes

- No functional changes are intended. The visual output remains consistent with prior behavior while improving performance and maintainability.
- These optimizations are designed to scale better for large graphs (thousands of nodes and edges).
- All optimizations maintain backward compatibility with existing tests and API contracts.
