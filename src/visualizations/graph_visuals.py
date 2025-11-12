 def _build_relationship_index(
     graph: AssetRelationshipGraph, asset_ids: Iterable[str]
 ) -> Dict[Tuple[str, str, str], float]:
-    """Build optimized relationship index for O(1) lookups with pre-filtering."""
    """Build optimized relationship index for O(1) lookups with pre-filtering.

    This function creates a dictionary mapping (source_id, target_id, rel_type) tuples
    to relationship strengths. It pre-filters relationships to only include those
    involving assets in the provided asset_ids set, improving efficiency.

    Thread Safety:
    - This function is thread-safe for reading from graph.relationships
    - The returned dictionary is a new instance and safe for concurrent reads
    - Callers must handle synchronization if modifying the returned dictionary concurrently

    Args:
        graph: AssetRelationshipGraph instance containing relationships
        asset_ids: Iterable of asset IDs to include in the index

    Returns:
        Dictionary mapping (source_id, target_id, rel_type) to strength values
    """
     asset_ids_set = set(asset_ids)

    # Pre-filter relationships to only include relevant source_ids
    # This reduces unnecessary iterations when source_id is not in asset_ids_set
    filtered_relationships = {
        source_id: rels
        for source_id, rels in graph.relationships.items()
        if source_id in asset_ids_set
    }

     relationship_index: Dict[Tuple[str, str, str], float] = {}
-
-    for source_id, rels in graph.relationships.items():
-        if source_id not in asset_ids_set:
-            continue

    for source_id, rels in filtered_relationships.items():
         for target_id, rel_type, strength in rels:
             if target_id in asset_ids_set:
                 relationship_index[(source_id, target_id, rel_type)] = float(strength)
-

     return relationship_index
