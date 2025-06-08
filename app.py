import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processor import DataProcessor
from utils.chart_generator import ChartGenerator
from utils.export_helper import ExportHelper
import io
import base64

# Configure page
st.set_page_config(
    page_title="Interactive Data Visualization Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None
if 'chart_configs' not in st.session_state:
    st.session_state.chart_configs = {
        'chart1': {'type': 'bar', 'x': None, 'y': None, 'color': None},
        'chart2': {'type': 'line', 'x': None, 'y': None, 'color': None},
        'chart3': {'type': 'scatter', 'x': None, 'y': None, 'color': None, 'size': None},
        'chart4': {'type': 'pie', 'values': None, 'names': None}
    }
if 'layout_config' not in st.session_state:
    st.session_state.layout_config = {
        'columns': 2,
        'chart_order': ['chart1', 'chart2', 'chart3', 'chart4']
    }

def main():
    st.title("📊 Interactive Data Visualization Dashboard")
    st.markdown("Upload your data and create interactive visualizations with filtering and aggregation capabilities.")
    
    # Initialize helper classes
    data_processor = DataProcessor()
    chart_generator = ChartGenerator()
    export_helper = ExportHelper()
    
    # Sidebar for data upload and configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # File upload section
        st.subheader("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your dataset to get started with visualization"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("Loading data..."):
                    st.session_state.data = data_processor.load_data(uploaded_file)
                    st.session_state.filtered_data = st.session_state.data.copy()
                st.success(f"✅ Data loaded successfully! ({len(st.session_state.data)} rows)")
                
                # Display basic data info
                st.write("**Data Overview:**")
                st.write(f"- Rows: {len(st.session_state.data)}")
                st.write(f"- Columns: {len(st.session_state.data.columns)}")
                
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                st.session_state.data = None
    
    if st.session_state.data is not None:
        # Main content area
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Data Explorer", "⚙️ Chart Settings", "📤 Export"])
        
        with tab1:
            display_dashboard(chart_generator)
        
        with tab2:
            display_data_explorer(data_processor)
        
        with tab3:
            display_chart_settings()
        
        with tab4:
            display_export_options(export_helper)
    
    else:
        st.info("👆 Please upload a CSV or Excel file to get started.")
        
        # Show sample data format
        st.subheader("📝 Expected Data Format")
        sample_data = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'Category': ['A', 'B', 'A'],
            'Value': [100, 150, 120],
            'Count': [5, 8, 6]
        })
        st.dataframe(sample_data, use_container_width=True)
        st.caption("Your data should have column headers in the first row.")

def display_dashboard(chart_generator):
    """Display the main dashboard with charts"""
    st.header("📊 Interactive Dashboard")
    
    if st.session_state.filtered_data is not None and not st.session_state.filtered_data.empty:
        # Layout configuration
        col1, col2 = st.columns([3, 1])
        with col2:
            st.subheader("Layout")
            layout_cols = st.selectbox("Columns per row", [1, 2, 3, 4], index=1)
            st.session_state.layout_config['columns'] = layout_cols
        
        # Create charts based on layout
        charts = []
        for chart_id in st.session_state.layout_config['chart_order']:
            config = st.session_state.chart_configs[chart_id]
            try:
                chart = chart_generator.create_chart(
                    st.session_state.filtered_data, 
                    config['type'], 
                    config
                )
                if chart:
                    charts.append((chart_id, chart))
            except Exception as e:
                st.error(f"Error creating {chart_id}: {str(e)}")
        
        # Display charts in configured layout
        if charts:
            cols_per_row = st.session_state.layout_config['columns']
            for i in range(0, len(charts), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, (chart_id, chart) in enumerate(charts[i:i+cols_per_row]):
                    with cols[j]:
                        st.plotly_chart(chart, use_container_width=True, key=f"dashboard_{chart_id}")
        else:
            st.warning("⚠️ Please configure chart settings in the 'Chart Settings' tab to display visualizations.")
    else:
        st.warning("⚠️ No data available. Please check your filters.")

def display_data_explorer(data_processor):
    """Display data exploration and filtering interface"""
    st.header("🔍 Data Explorer")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Raw Data")
        if st.session_state.data is not None:
            # Display filtered data
            st.dataframe(st.session_state.filtered_data, use_container_width=True, height=400)
            
            # Data statistics
            if not st.session_state.filtered_data.empty:
                st.subheader("📈 Data Statistics")
                numeric_cols = st.session_state.filtered_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    stats_df = st.session_state.filtered_data[numeric_cols].describe()
                    st.dataframe(stats_df, use_container_width=True)
    
    with col2:
        st.subheader("🔍 Filters & Aggregation")
        
        # Column filters
        st.write("**Column Filters:**")
        columns = st.session_state.data.columns.tolist()
        
        filters = {}
        for col in columns:
            if st.session_state.data[col].dtype == 'object':
                unique_values = st.session_state.data[col].unique()
                selected = st.multiselect(
                    f"Filter {col}",
                    options=unique_values,
                    default=unique_values,
                    key=f"filter_{col}"
                )
                if selected != list(unique_values):
                    filters[col] = selected
            else:
                min_val = float(st.session_state.data[col].min())
                max_val = float(st.session_state.data[col].max())
                range_val = st.slider(
                    f"Range for {col}",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    key=f"range_{col}"
                )
                if range_val != (min_val, max_val):
                    filters[col] = range_val
        
        # Apply filters
        if st.button("🔄 Apply Filters", type="primary"):
            st.session_state.filtered_data = data_processor.apply_filters(
                st.session_state.data, filters
            )
            st.rerun()
        
        # Reset filters
        if st.button("🔄 Reset Filters"):
            st.session_state.filtered_data = st.session_state.data.copy()
            st.rerun()
        
        # Aggregation options
        st.write("**Data Aggregation:**")
        numeric_columns = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = st.session_state.data.select_dtypes(include=['object']).columns.tolist()
        
        if numeric_columns and categorical_columns:
            group_by = st.selectbox("Group by", categorical_columns)
            agg_column = st.selectbox("Aggregate column", numeric_columns)
            agg_function = st.selectbox("Function", ["sum", "mean", "count", "min", "max"])
            
            if st.button("📊 Apply Aggregation"):
                st.session_state.filtered_data = data_processor.aggregate_data(
                    st.session_state.filtered_data, group_by, agg_column, agg_function
                )
                st.rerun()

def display_chart_settings():
    """Display chart configuration interface"""
    st.header("⚙️ Chart Settings")
    
    if st.session_state.filtered_data is not None:
        columns = st.session_state.filtered_data.columns.tolist()
        numeric_columns = st.session_state.filtered_data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Chart configuration tabs
        chart_tabs = st.tabs(["Chart 1 (Bar)", "Chart 2 (Line)", "Chart 3 (Scatter)", "Chart 4 (Pie)"])
        
        # Chart 1 - Bar Chart
        with chart_tabs[0]:
            st.subheader("📊 Bar Chart Configuration")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.session_state.chart_configs['chart1']['x'] = st.selectbox(
                    "X-axis", columns, key="bar_x",
                    index=columns.index(st.session_state.chart_configs['chart1']['x']) 
                    if st.session_state.chart_configs['chart1']['x'] in columns else 0
                )
            
            with col2:
                st.session_state.chart_configs['chart1']['y'] = st.selectbox(
                    "Y-axis", numeric_columns, key="bar_y",
                    index=numeric_columns.index(st.session_state.chart_configs['chart1']['y']) 
                    if st.session_state.chart_configs['chart1']['y'] in numeric_columns else 0
                ) if numeric_columns else None
            
            with col3:
                color_options = ['None'] + columns
                color_selection = st.selectbox("Color by", color_options, key="bar_color")
                st.session_state.chart_configs['chart1']['color'] = color_selection if color_selection != 'None' else None
        
        # Chart 2 - Line Chart
        with chart_tabs[1]:
            st.subheader("📈 Line Chart Configuration")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.session_state.chart_configs['chart2']['x'] = st.selectbox(
                    "X-axis", columns, key="line_x",
                    index=columns.index(st.session_state.chart_configs['chart2']['x']) 
                    if st.session_state.chart_configs['chart2']['x'] in columns else 0
                )
            
            with col2:
                st.session_state.chart_configs['chart2']['y'] = st.selectbox(
                    "Y-axis", numeric_columns, key="line_y",
                    index=numeric_columns.index(st.session_state.chart_configs['chart2']['y']) 
                    if st.session_state.chart_configs['chart2']['y'] in numeric_columns else 0
                ) if numeric_columns else None
            
            with col3:
                color_options = ['None'] + columns
                color_selection = st.selectbox("Color by", color_options, key="line_color")
                st.session_state.chart_configs['chart2']['color'] = color_selection if color_selection != 'None' else None
        
        # Chart 3 - Scatter Plot
        with chart_tabs[2]:
            st.subheader("🔵 Scatter Plot Configuration")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.session_state.chart_configs['chart3']['x'] = st.selectbox(
                    "X-axis", numeric_columns, key="scatter_x",
                    index=numeric_columns.index(st.session_state.chart_configs['chart3']['x']) 
                    if st.session_state.chart_configs['chart3']['x'] in numeric_columns else 0
                ) if numeric_columns else None
            
            with col2:
                st.session_state.chart_configs['chart3']['y'] = st.selectbox(
                    "Y-axis", numeric_columns, key="scatter_y",
                    index=numeric_columns.index(st.session_state.chart_configs['chart3']['y']) 
                    if st.session_state.chart_configs['chart3']['y'] in numeric_columns else 0
                ) if numeric_columns else None
            
            with col3:
                color_options = ['None'] + columns
                color_selection = st.selectbox("Color by", color_options, key="scatter_color")
                st.session_state.chart_configs['chart3']['color'] = color_selection if color_selection != 'None' else None
            
            with col4:
                size_options = ['None'] + numeric_columns
                size_selection = st.selectbox("Size by", size_options, key="scatter_size")
                st.session_state.chart_configs['chart3']['size'] = size_selection if size_selection != 'None' else None
        
        # Chart 4 - Pie Chart
        with chart_tabs[3]:
            st.subheader("🥧 Pie Chart Configuration")
            col1, col2 = st.columns(2)
            
            with col1:
                st.session_state.chart_configs['chart4']['values'] = st.selectbox(
                    "Values", numeric_columns, key="pie_values",
                    index=numeric_columns.index(st.session_state.chart_configs['chart4']['values']) 
                    if st.session_state.chart_configs['chart4']['values'] in numeric_columns else 0
                ) if numeric_columns else None
            
            with col2:
                st.session_state.chart_configs['chart4']['names'] = st.selectbox(
                    "Labels", columns, key="pie_names",
                    index=columns.index(st.session_state.chart_configs['chart4']['names']) 
                    if st.session_state.chart_configs['chart4']['names'] in columns else 0
                )

def display_export_options(export_helper):
    """Display export functionality"""
    st.header("📤 Export Options")
    
    if st.session_state.filtered_data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Export Data")
            
            # Export filtered data
            if st.button("📥 Download Filtered Data (CSV)", type="primary"):
                csv = st.session_state.filtered_data.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv,
                    file_name="filtered_data.csv",
                    mime="text/csv"
                )
            
            if st.button("📥 Download Filtered Data (Excel)"):
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    st.session_state.filtered_data.to_excel(writer, index=False, sheet_name='Data')
                
                st.download_button(
                    label="💾 Download Excel",
                    data=buffer.getvalue(),
                    file_name="filtered_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col2:
            st.subheader("📈 Export Charts")
            st.info("Charts can be exported individually using the menu in the top-right corner of each chart.")
            st.write("Available export formats:")
            st.write("- PNG (static image)")
            st.write("- HTML (interactive)")
            st.write("- SVG (vector graphics)")
    
    else:
        st.warning("⚠️ No data available for export.")

if __name__ == "__main__":
    main()
