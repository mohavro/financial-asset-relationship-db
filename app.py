import gradio as gr
import json
import logging
from typing import Optional
from dataclasses import asdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import modular components
from src.logic.asset_graph import AssetRelationshipGraph
from src.data.sample_data import create_sample_database
from src.visualizations.graph_visuals import visualize_3d_graph
from src.visualizations.metric_visuals import visualize_metrics
from src.reports.schema_report import generate_schema_report

# ------------- Gradio Interface -------------

def create_interface():
    """Create Gradio interface"""

    with gr.Blocks(title="Financial Asset Relationship Database Visualization") as demo:
        gr.Markdown("""
        # 🏦 Financial Asset Relationship Network

        A comprehensive 3D visualization of interconnected financial assets across all major classes:
        **Equities, Bonds, Commodities, Currencies, and Regulatory Events**

        [Built with anycoder](https://huggingface.co/spaces/akhaliq/anycoder)
        """)

        # Global error message display
        error_message = gr.Textbox(label="Error", visible=False, interactive=False, elem_id="error_message")

        with gr.Tabs():
            with gr.Tab("3D Network Visualization"):
                gr.Markdown("### Interactive 3D Asset Relationship Graph")
                with gr.Row():
                    visualization_3d = gr.Plot()
                with gr.Row():
                    with gr.Column(scale=1):
                        refresh_btn = gr.Button("Refresh Visualization", variant="primary")
                    with gr.Column(scale=3):
                        gr.Markdown("")

            with gr.Tab("Metrics & Analytics"):
                gr.Markdown("### Network Metrics and Relationship Analysis")
                with gr.Row():
                    asset_dist_chart = gr.Plot()
                    rel_types_chart = gr.Plot()
                with gr.Row():
                    events_timeline_chart = gr.Plot()
                with gr.Row():
                    metrics_text = gr.Textbox(label="Network Statistics", lines=10, interactive=False)
                with gr.Row():
                    refresh_metrics_btn = gr.Button("Refresh Metrics", variant="primary")

            with gr.Tab("Schema & Rules"):
                gr.Markdown("### Database Schema, Business Rules & Implementation Guide")
                with gr.Row():
                    schema_report = gr.Textbox(
                        label="Schema Report",
                        lines=25,
                        interactive=False,
                    )
                with gr.Row():
                    refresh_schema_btn = gr.Button("Generate Schema Report", variant="primary")

            with gr.Tab("Asset Explorer"):
                gr.Markdown("### Detailed Asset Information & Relationships")
                with gr.Row():
                    with gr.Column(scale=1):
                        asset_selector = gr.Dropdown(label="Select Asset", choices=[], interactive=True)
                    with gr.Column(scale=3):
                        gr.Markdown("")

                with gr.Row():
                    asset_info = gr.JSON(label="Asset Details")

                with gr.Row():
                    asset_relationships = gr.JSON(label="Related Assets")

                with gr.Row():
                    refresh_explorer_btn = gr.Button("Refresh Asset List", variant="primary")

            with gr.Tab("Documentation"):
                gr.Markdown("""
                ## Financial Asset Relationship Database

                ### Architecture Overview

                This system models the complete financial ecosystem with:

                #### Asset Classes
                - **Equities**: Common stocks with fundamentals (P/E, dividend yield, EPS)
                - **Fixed Income**: Bonds with yield, duration, credit ratings
                - **Commodities**: Futures and spot prices with contract specifications
                - **Currencies**: FX pairs with exchange rates and monetary policy links
                - **Derivatives**: Options, futures, swaps (extensible)

                #### Relationship Types
                - **Sector Affinity**: Assets in same industry sector
                - **Corporate Links**: Bonds issued by stock companies
                - **Commodity Exposure**: Equity companies exposed to commodity prices
                - **Currency Risk**: FX exposure for non-USD assets
                - **Income Comparison**: Dividends vs bond yields
                - **Event Impact**: Regulatory and corporate events affecting multiple assets

                #### Regulatory Integration
                - Earnings announcements
                - SEC filings (10-K, 10-Q, 8-K)
                - Dividend announcements
                - Bond issuances
                - M&A activities
                - Bankruptcy filings

                ### Key Features

                1. **Cross-Asset Matching**: Automatically links similar attributes across classes
                2. **Hierarchical Relationships**: Parent-child relationships (company → bonds → stock)
                3. **Strength Metrics**: Each relationship has a 0-1 strength score
                4. **Event Propagation**: Corporate events impact related assets
                5. **Rule Engine**: Business rules for valuation, exposure, and risk

                ### Database Schema

                **Assets Table**
                ```
                asset_id | symbol | name | asset_class | price | currency | metadata
                ```plaintext

                **Relationships Table**
                ```
                source_id | target_id | relationship_type | strength | created_date
                ```plaintext

                **Events Table**
                ```
                event_id | asset_id | event_type | date | impact | related_assets
                ```plaintext

                **Rules Table**
                ```
                rule_id | rule_type | condition | action | priority
                ```plaintext
                """)

        # Initialize graph immediately to avoid None
        try:
            initial_graph = create_sample_database()
            logger.info(f"Initialized sample database with {len(initial_graph.assets)} assets")
            graph_state = gr.State(value=initial_graph)
        except Exception as e:
            logger.error(f"Failed to create sample database: {e}")
            raise

        # Helpers
        def ensure_graph(g: Optional[AssetRelationshipGraph]) -> AssetRelationshipGraph:
            return g if isinstance(g, AssetRelationshipGraph) else create_sample_database()

        def _update_metrics_text(graph):
            graph = ensure_graph(graph)
            metrics = graph.calculate_metrics()
            text = f"""Network Statistics:
Total Assets: {metrics['total_assets']}
Total Relationships: {metrics['total_relationships']}
Avg Relationship Strength: {metrics['average_relationship_strength']:.3f}
Relationship Density: {metrics['relationship_density']:.2f}%
Regulatory Events: {metrics['regulatory_event_count']}

Asset Classes:
{json.dumps(metrics['asset_class_distribution'], indent=2)}

Top 5 Relationships:
"""
            for idx, (s, t, rel, strength) in enumerate(metrics['top_relationships'], 1):
                text += f"{idx}. {s} → {t} ({rel}): {strength:.1%}\n"

            return text

        def update_all_metrics_outputs(graph):
            graph = ensure_graph(graph)
            f1, f2, f3 = visualize_metrics(graph)
            text = _update_metrics_text(graph)
            return f1, f2, f3, text

        def update_asset_info(selected_asset, graph):
            graph = ensure_graph(graph)
            if not selected_asset or selected_asset not in graph.assets:
                return {}, {"outgoing": {}, "incoming": {}}

            asset = graph.assets[selected_asset]
            asset_dict = asdict(asset)
            asset_dict['asset_class'] = asset.asset_class.value

            outgoing = {}
            for target_id, rel_type, strength in graph.relationships.get(selected_asset, []):
                outgoing[target_id] = {
                    "relationship_type": rel_type,
                    "strength": strength
                }

            incoming = {}
            for src_id, rel_type, strength in graph.incoming_relationships.get(selected_asset, []):
                incoming[src_id] = {"relationship_type": rel_type, "strength": strength}

            return asset_dict, {"outgoing": outgoing, "incoming": incoming}

        def refresh_all_outputs(graph):
            try:
                graph = ensure_graph(graph)
                logger.info("Refreshing all visualization outputs")
                viz_3d = visualize_3d_graph(graph)
                f1, f2, f3, metrics_txt = update_all_metrics_outputs(graph)
                schema_rpt = generate_schema_report(graph)
                asset_choices = list(graph.assets.keys())
                logger.info(f"Successfully refreshed outputs for {len(asset_choices)} assets")
                return viz_3d, f1, f2, f3, metrics_txt, schema_rpt, gr.update(choices=asset_choices, value=None), gr.update(value="", visible=False)
            except Exception as e:
                logger.error(f"Error refreshing outputs: {e}")
                return (
                    gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
                    gr.update(choices=[], value=None),
                    gr.update(value=f"Error: {str(e)}", visible=True)
                )

        # Event handlers
        refresh_btn.click(
            refresh_all_outputs,
            inputs=[graph_state],
            outputs=[visualization_3d, asset_dist_chart, rel_types_chart, events_timeline_chart, metrics_text, schema_report, asset_selector, error_message]
        )

        refresh_metrics_btn.click(
            refresh_all_outputs,
            inputs=[graph_state],
            outputs=[visualization_3d, asset_dist_chart, rel_types_chart, events_timeline_chart, metrics_text, schema_report, asset_selector, error_message]
        )

        refresh_schema_btn.click(
            refresh_all_outputs,
            inputs=[graph_state],
            outputs=[visualization_3d, asset_dist_chart, rel_types_chart, events_timeline_chart, metrics_text, schema_report, asset_selector, error_message]
        )

        refresh_explorer_btn.click(
            refresh_all_outputs,
            inputs=[graph_state],
            outputs=[visualization_3d, asset_dist_chart, rel_types_chart, events_timeline_chart, metrics_text, schema_report, asset_selector, error_message]
        )

        asset_selector.change(
            update_asset_info,
            inputs=[asset_selector, graph_state],
            outputs=[asset_info, asset_relationships]
        )

        # Load initial visualizations
        demo.load(
            refresh_all_outputs,
            inputs=[graph_state],
            outputs=[visualization_3d, asset_dist_chart, rel_types_chart, events_timeline_chart, metrics_text, schema_report, asset_selector, error_message]
        )

    return demo

if __name__ == "__main__":
    try:
        logger.info("Starting Financial Asset Relationship Database application")
        demo = create_interface()
        logger.info("Launching Gradio interface")
        demo.launch()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise