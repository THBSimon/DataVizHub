# Interactive Data Visualization Dashboard

An advanced Streamlit dashboard for interactive data exploration with dynamic filtering, drag-and-drop chart functionality, and comprehensive export capabilities.

## Features

- **Interactive Data Upload**: Support for CSV and Excel files
- **Dynamic Filtering**: Real-time filters with text selection and range sliders
- **Drag-and-Drop Charts**: Customizable dashboard layout with sortable charts
- **Inline Chart Settings**: Configure charts directly from the dashboard
- **Multi-tab Interface**: Separate tabs for Dashboard, Data Explorer, and Export
- **Export Functionality**: Export data and charts in multiple formats

## Local Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone or download the project files
2. Navigate to the project directory
3. Install dependencies:

```bash
pip install -r dependencies.txt
```

Or install packages individually:

```bash
pip install streamlit>=1.28.0
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install plotly>=5.17.0
pip install openpyxl>=3.1.0
pip install streamlit-sortables>=0.2.0
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

1. **Upload Data**: Use the file uploader to upload CSV or Excel files
2. **Apply Filters**: Use the sidebar filters to narrow down your data
3. **View Dashboard**: See interactive charts that update based on your filters
4. **Explore Data**: Switch to the Data Explorer tab for detailed data analysis
5. **Export Results**: Use the Export tab to download filtered data and charts

## Project Structure

```
├── app.py                 # Main Streamlit application
├── utils/
│   ├── chart_generator.py # Chart creation and configuration
│   ├── data_processor.py  # Data loading and filtering
│   └── export_helper.py   # Export functionality
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── dependencies.txt      # Package dependencies
```

## Configuration

The `.streamlit/config.toml` file contains server configuration for proper deployment. Modify this file if you need to change server settings.