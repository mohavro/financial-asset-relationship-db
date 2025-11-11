# Performance Optimizations

This document summarizes the performance-oriented refactors made to the 3D graph visualizations.

## Highlights

- Centralized styling and color mapping for relationship types to reduce duplicated logic.
- O(1) lookups via pre-built indices for asset IDs and relationship pairs, avoiding repeated list.index() calls.
- Single-pass collection and grouping of relationships to reduce complexity and improve throughput.
- Pre-allocation of arrays for edge coordinates and hovertexts to minimize dynamic resizing and allocations.
- Vectorized NumPy operations where appropriate to reduce Python-level loops.

## Specific Changes

1. Relationship Processing
   - Introduced an index `(source, target, type) -> strength` to enable constant-time reverse lookup and bidirectionality checks.
   - Removed redundant passes and replaced tuple sorting with a simple canonical pair key.

2. Edge Building
   - Replaced repeated extend() calls with pre-allocated lists sized to the exact number of values.

3. Directional Arrows
   - Replaced per-edge Python-loop arithmetic with vectorized NumPy operations for arrow positions:
     - Compute arrow positions at 70% along the edge using: `src + 0.7 * (tgt - src)`
     - This significantly reduces overhead for large graphs.

## Notes

- No functional changes are intended. The visual output remains consistent with prior behavior while improving performance and maintainability.
- These optimizations are designed to scale better for large graphs (thousands of nodes and edges).
