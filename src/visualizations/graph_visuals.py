 def _create_relationship_traces(
     graph: AssetRelationshipGraph,
     positions: np.ndarray,
     asset_ids: List[str],
-    relationship_filters: Optional[dict] = None,
    relationship_filters: Optional[dict] = None,
 ) -> List[go.Scatter3d]:
     """Create separate traces for different types of relationships with enhanced visibility.
@@ -334,5 +334,7 @@
-    relationship_groups = _collect_and_group_relationships(graph, asset_ids, relationship_filters)
    if relationship_filters is None:
        all_relationships, bidirectional_pairs = _collect_relationships(graph, asset_ids)
    else:
        all_relationships, bidirectional_pairs = _collect_relationships(graph, asset_ids, relationship_filters)
    relationship_groups = _group_relationships(all_relationships, bidirectional_pairs)

     traces = []
