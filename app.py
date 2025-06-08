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
from streamlit_sortables import sort_items

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
        'Chart 1': {'type': 'bar', 'x': None, 'y': None, 'color': None, 'size': None, 'values': None, 'names': None, 'title': 'Bar Chart'},
        'Chart 2': {'type': 'line', 'x': None, 'y': None, 'color': None, 'size': None, 'values': None, 'names': None, 'title': 'Line Chart'},
        'Chart 3': {'type': 'scatter', 'x': None, 'y': None, 'color': None, 'size': None, 'values': None, 'names': None, 'title': 'Scatter Plot'},
        'Chart 4': {'type': 'pie', 'x': None, 'y': None, 'color': None, 'size': None, 'values': None, 'names': None, 'title': 'Pie Chart'}
    }
if 'dashboard_layout' not in st.session_state:
    st.session_state.dashboard_layout = ['Chart 1', 'Chart 2', 'Chart 3', 'Chart 4']
if 'columns_layout' not in st.session_state:
    st.session_state.columns_layout = 2

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
                st.session_state.filtered_data = None
    
    if st.session_state.data is not None:
        # Main content area
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔍 Data Explorer", "📤 Export"])
        
        with tab1:
            display_dashboard(chart_generator)
        
        with tab2:
            display_data_explorer(data_processor)
        
        with tab3:
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

def create_chart_widget(chart_name, chart_generator):
    """Create an individual chart widget with inline settings"""
    with st.container(border=True):
        # Chart header with title and settings toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(st.session_state.chart_configs[chart_name]['title'])
        with col2:
            show_settings = st.toggle("⚙️", key=f"settings_{chart_name}", help="Show chart settings")
        
        # Inline settings when toggled
        if show_settings:
            st.markdown("**Chart Configuration:**")
            config = st.session_state.chart_configs[chart_name]
            
            if st.session_state.filtered_data is not None:
                columns = st.session_state.filtered_data.columns.tolist()
                numeric_columns = st.session_state.filtered_data.select_dtypes(include=[np.number]).columns.tolist()
                
                # Chart type selection
                chart_types = ['bar', 'line', 'scatter', 'pie']
                current_type_idx = chart_types.index(config['type']) if config['type'] in chart_types else 0
                config['type'] = st.selectbox("Chart Type", chart_types, index=current_type_idx, key=f"type_{chart_name}")
                
                # Dynamic settings based on chart type
                if config['type'] in ['bar', 'line', 'scatter']:
                    col_x, col_y = st.columns(2)
                    with col_x:
                        x_idx = columns.index(config['x']) if config['x'] in columns else 0
                        config['x'] = st.selectbox("X-axis", columns, index=x_idx, key=f"x_{chart_name}")
                    with col_y:
                        if numeric_columns:
                            y_idx = numeric_columns.index(config['y']) if config['y'] in numeric_columns else 0
                            config['y'] = st.selectbox("Y-axis", numeric_columns, index=y_idx, key=f"y_{chart_name}")
                    
                    # Color option
                    color_options = ['None'] + columns
                    color_idx = color_options.index(config['color']) if config['color'] in color_options else 0
                    color_selection = st.selectbox("Color by", color_options, index=color_idx, key=f"color_{chart_name}")
                    config['color'] = color_selection if color_selection != 'None' else None
                    
                    # Size option for scatter plots
                    if config['type'] == 'scatter':
                        size_options = ['None'] + numeric_columns
                        current_size = config.get('size', None)
                        size_idx = size_options.index(current_size) if current_size in size_options else 0
                        size_selection = st.selectbox("Size by", size_options, index=size_idx, key=f"size_{chart_name}")
                        config['size'] = size_selection if size_selection != 'None' else None
                
                elif config['type'] == 'pie':
                    col_vals, col_names = st.columns(2)
                    with col_vals:
                        if numeric_columns:
                            current_values = config.get('values', None)
                            vals_idx = numeric_columns.index(current_values) if current_values in numeric_columns else 0
                            config['values'] = st.selectbox("Values", numeric_columns, index=vals_idx, key=f"values_{chart_name}")
                    with col_names:
                        current_names = config.get('names', None)
                        names_idx = columns.index(current_names) if current_names in columns else 0
                        config['names'] = st.selectbox("Labels", columns, index=names_idx, key=f"names_{chart_name}")
                
                # Update the session state
                st.session_state.chart_configs[chart_name] = config
        
        # Create and display the chart
        if st.session_state.filtered_data is not None and not st.session_state.filtered_data.empty:
            try:
                chart = chart_generator.create_chart(
                    st.session_state.filtered_data,
                    st.session_state.chart_configs[chart_name]['type'],
                    st.session_state.chart_configs[chart_name]
                )
                if chart:
                    # Include filter counter in key to force refresh when data changes
                    filter_counter = st.session_state.get('filter_update_counter', 0)
                    st.plotly_chart(chart, use_container_width=True, key=f"chart_{chart_name}_{filter_counter}")
                else:
                    st.info("Configure chart settings to display visualization")
            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")
        else:
            st.info("No data available for visualization")

def display_dashboard(chart_generator):
    """Display the main dashboard with charts"""
    st.header("📊 Interactive Dashboard")
    
    # Ensure filtered data is initialized
    if 'filtered_data' not in st.session_state or st.session_state.filtered_data is None:
        if st.session_state.data is not None:
            st.session_state.filtered_data = st.session_state.data.copy()
    
    if st.session_state.filtered_data is not None and not st.session_state.filtered_data.empty:
        # Show current data status with filter update counter for reactivity
        total_rows = len(st.session_state.data) if st.session_state.data is not None else 0
        filtered_rows = len(st.session_state.filtered_data)
        filter_counter = st.session_state.get('filter_update_counter', 0)
        
        if filtered_rows < total_rows:
            st.info(f"📊 Showing {filtered_rows} of {total_rows} rows (filtered) [Update: {filter_counter}]")
        else:
            st.info(f"📊 Showing all {total_rows} rows [Update: {filter_counter}]")
        
        # Dashboard layout controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("**Drag and drop charts to reorder them:**")
        with col2:
            st.session_state.columns_layout = st.selectbox("Columns per row", [1, 2, 3, 4], index=st.session_state.columns_layout-1, key="layout_cols") 
        with col3:
            if st.button("Reset Layout"):
                st.session_state.dashboard_layout = ['Chart 1', 'Chart 2', 'Chart 3', 'Chart 4']
                st.rerun()
        
        # Drag and drop interface for chart ordering
        st.markdown("---")
        sorted_items = sort_items(
            st.session_state.dashboard_layout,
            direction="horizontal",
            key="dashboard_sort"
        )
        
        # Update layout if changed
        if sorted_items and sorted_items != st.session_state.dashboard_layout:
            st.session_state.dashboard_layout = sorted_items
        
        # Display charts in the configured layout
        cols_per_row = st.session_state.columns_layout
        chart_list = st.session_state.dashboard_layout
        
        for i in range(0, len(chart_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, chart_name in enumerate(chart_list[i:i+cols_per_row]):
                if j < len(cols):
                    with cols[j]:
                        create_chart_widget(chart_name, chart_generator)
    else:
        st.warning("⚠️ No data available. Please check your filters.")

def display_data_explorer(data_processor):
    """Display data exploration and filtering interface"""
    st.header("🔍 Data Explorer")
    
    # Initialize filtered data if not exists
    if 'filtered_data' not in st.session_state or st.session_state.filtered_data is None:
        st.session_state.filtered_data = st.session_state.data.copy()
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("🔍 Filters & Aggregation")
        
        # Column filters
        st.write("**Column Filters:**")
        columns = st.session_state.data.columns.tolist()
        
        filters = {}
        filter_changed = False
        
        for col in columns:
            if st.session_state.data[col].dtype == 'object':
                unique_values = st.session_state.data[col].unique()
                selected = st.multiselect(
                    f"Filter {col}",
                    options=unique_values,
                    default=unique_values,
                    key=f"filter_{col}"
                )
                if len(selected) < len(unique_values):
                    filters[col] = selected
                    filter_changed = True
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
                if range_val[0] > min_val or range_val[1] < max_val:
                    filters[col] = range_val
                    filter_changed = True
        
        # Apply filters automatically when they change
        if filters:
            new_filtered_data = data_processor.apply_filters(st.session_state.data, filters)
            # Always update filtered data and increment counter when filters are active
            st.session_state.filtered_data = new_filtered_data
            if 'filter_update_counter' not in st.session_state:
                st.session_state.filter_update_counter = 0
            st.session_state.filter_update_counter += 1
            st.success(f"✅ Applied {len(filters)} filter(s) - {len(st.session_state.filtered_data)} rows shown")
        else:
            # Reset to original data if no filters
            st.session_state.filtered_data = st.session_state.data.copy()
            if 'filter_update_counter' not in st.session_state:
                st.session_state.filter_update_counter = 0
            st.session_state.filter_update_counter += 1
            st.info(f"ℹ️ No filters applied - showing all {len(st.session_state.data)} rows")
        
        # Reset filters
        if st.button("🔄 Reset Filters"):
            # Clear all filter widget states
            for col in columns:
                if st.session_state.data[col].dtype == 'object':
                    if f"filter_{col}" in st.session_state:
                        del st.session_state[f"filter_{col}"]
                else:
                    if f"range_{col}" in st.session_state:
                        del st.session_state[f"range_{col}"]
            st.session_state.filtered_data = st.session_state.data.copy()
            st.rerun()
    
    with col1:
        st.subheader("Filtered Data")
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
