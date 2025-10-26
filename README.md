# Financial Asset Relationship Database

A comprehensive 3D visualization system for interconnected financial assets across all major classes: **Equities, Bonds, Commodities, Currencies, and Regulatory Events**.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd financial-asset-relationship-db
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - **Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The application will launch in your browser automatically at `http://localhost:7860`.

## 📊 Features

### Core Functionality
- **3D Network Visualization**: Interactive 3D graph of asset relationships
- **Cross-Asset Analysis**: Automatic relationship discovery between asset classes
- **Regulatory Integration**: Corporate events and SEC filings impact modeling
- **Real-time Metrics**: Network statistics and relationship strength analysis

### Asset Classes Supported
- **Equities**: Stocks with P/E ratios, dividend yields, EPS
- **Fixed Income**: Bonds with yield, duration, credit ratings
- **Commodities**: Futures and spot prices with contract specifications
- **Currencies**: FX pairs with exchange rates and monetary policy links
- **Regulatory Events**: Earnings, SEC filings, M&A activities

### Relationship Types
- **Sector Affinity**: Assets in same industry sector
- **Corporate Links**: Bonds issued by stock companies
- **Commodity Exposure**: Equity companies exposed to commodity prices
- **Currency Risk**: FX exposure for non-USD assets
- **Income Comparison**: Dividends vs bond yields
- **Event Impact**: Regulatory events affecting multiple assets

## 🏗️ Architecture

### Key Components
- **`app.py`**: Gradio web interface and event handlers
- **`src/logic/asset_graph.py`**: Core graph algorithms and relationship engine
- **`src/models/financial_models.py`**: Domain model dataclasses and enums
- **`src/data/sample_data.py`**: Sample dataset creation
- **`src/visualizations/`**: Plotly-based charts and 3D graphs
- **`src/reports/`**: Schema and business rules reporting

### Data Model
```
Assets -> Relationships -> Regulatory Events
    ↓           ↓              ↓
  Attributes  Strength    Impact Score
```

- **Relationship Strength**: Normalized 0.0-1.0 scale
- **Regulatory Impact**: -1 to +1 scale (negative to positive)
- **3D Positions**: Deterministic layout with seed=42 for consistency

## 🧪 Development

### Project Structure
```
.
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── .github/copilot-instructions.md # AI agent guidance
├── src/
│   ├── data/
│   │   └── sample_data.py         # Sample database creation
│   ├── logic/
│   │   └── asset_graph.py         # Core relationship engine
│   ├── models/
│   │   └── financial_models.py    # Domain model classes
│   ├── reports/
│   │   └── schema_report.py       # Schema documentation
│   └── visualizations/
│       ├── graph_visuals.py       # 3D network visualization
│       └── metric_visuals.py      # Analytics charts
```

### Key Patterns
- **Bidirectional Relationships**: Some relationships are symmetric (e.g., `same_sector`)
- **Directional Relationships**: Others flow one way (e.g., `corporate_bond_to_equity`)
- **Deterministic Positions**: 3D layout uses fixed random seed for consistency
- **Relationship Discovery**: Automatic relationship detection via `_find_relationships()`

## 📈 Usage Examples

### Adding New Asset Types
```python
from src.models.financial_models import Asset, AssetClass

# Extend Asset for new types
@dataclass
class Derivative(Asset):
    underlying_asset: str
    expiration_date: str
    strike_price: Optional[float] = None
```

### Custom Relationship Rules
```python
# Add to _find_relationships() in AssetRelationshipGraph
if isinstance(asset1, Derivative) and isinstance(asset2, Equity):
    if asset1.underlying_asset == asset2.symbol:
        relationships.append(("derivative_underlying", 0.95, False))
```

## 🛠️ API Reference

### Core Methods
- `AssetRelationshipGraph.add_asset(asset)` - Add asset to graph
- `AssetRelationshipGraph.add_relationship(source, target, type, strength)` - Create relationship
- `AssetRelationshipGraph.build_relationships()` - Auto-discover relationships
- `AssetRelationshipGraph.calculate_metrics()` - Generate network statistics
- `AssetRelationshipGraph.get_3d_visualization_data()` - Export for visualization

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

For AI agents: see `.github/copilot-instructions.md` for development guidelines.