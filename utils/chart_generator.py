import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class ChartGenerator:
    """Generate interactive Plotly charts based on data and configuration"""
    
    def create_chart(self, data, chart_type, config):
        """
        Create a chart based on the specified type and configuration
        
        Args:
            data: pandas.DataFrame
            chart_type: str - type of chart (bar, line, scatter, pie)
            config: dict - chart configuration parameters
            
        Returns:
            plotly.graph_objects.Figure: Interactive chart
        """
        if data is None or data.empty:
            return self._create_empty_chart("No data available")
        
        try:
            if chart_type == 'bar':
                return self._create_bar_chart(data, config)
            elif chart_type == 'line':
                return self._create_line_chart(data, config)
            elif chart_type == 'scatter':
                return self._create_scatter_chart(data, config)
            elif chart_type == 'pie':
                return self._create_pie_chart(data, config)
            else:
                return self._create_empty_chart(f"Unsupported chart type: {chart_type}")
                
        except Exception as e:
            return self._create_empty_chart(f"Error creating chart: {str(e)}")
    
    def _create_bar_chart(self, data, config):
        """Create a bar chart"""
        x_col = config.get('x')
        y_col = config.get('y')
        color_col = config.get('color')
        
        if not x_col or not y_col:
            return self._create_empty_chart("Please select X and Y axes for bar chart")
        
        if x_col not in data.columns or y_col not in data.columns:
            return self._create_empty_chart("Selected columns not found in data")
        
        # Create bar chart
        fig = px.bar(
            data, 
            x=x_col, 
            y=y_col,
            color=color_col if color_col and color_col in data.columns else None,
            title=f"Bar Chart: {y_col} by {x_col}",
            labels={x_col: x_col.title(), y_col: y_col.title()}
        )
        
        # Update layout
        fig.update_layout(
            showlegend=bool(color_col),
            hovermode='x unified',
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        
        return fig
    
    def _create_line_chart(self, data, config):
        """Create a line chart"""
        x_col = config.get('x')
        y_col = config.get('y')
        color_col = config.get('color')
        
        if not x_col or not y_col:
            return self._create_empty_chart("Please select X and Y axes for line chart")
        
        if x_col not in data.columns or y_col not in data.columns:
            return self._create_empty_chart("Selected columns not found in data")
        
        # Sort data by x column for better line visualization
        data_sorted = data.sort_values(by=x_col)
        
        # Create line chart
        fig = px.line(
            data_sorted, 
            x=x_col, 
            y=y_col,
            color=color_col if color_col and color_col in data.columns else None,
            title=f"Line Chart: {y_col} over {x_col}",
            labels={x_col: x_col.title(), y_col: y_col.title()},
            markers=True
        )
        
        # Update layout
        fig.update_layout(
            showlegend=bool(color_col),
            hovermode='x unified',
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        
        return fig
    
    def _create_scatter_chart(self, data, config):
        """Create a scatter plot"""
        x_col = config.get('x')
        y_col = config.get('y')
        color_col = config.get('color')
        size_col = config.get('size')
        
        if not x_col or not y_col:
            return self._create_empty_chart("Please select X and Y axes for scatter plot")
        
        if x_col not in data.columns or y_col not in data.columns:
            return self._create_empty_chart("Selected columns not found in data")
        
        # Create scatter plot
        fig = px.scatter(
            data, 
            x=x_col, 
            y=y_col,
            color=color_col if color_col and color_col in data.columns else None,
            size=size_col if size_col and size_col in data.columns else None,
            title=f"Scatter Plot: {y_col} vs {x_col}",
            labels={x_col: x_col.title(), y_col: y_col.title()},
            hover_data=data.columns.tolist()
        )
        
        # Update layout
        fig.update_layout(
            showlegend=bool(color_col or size_col),
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        
        return fig
    
    def _create_pie_chart(self, data, config):
        """Create a pie chart"""
        values_col = config.get('values')
        names_col = config.get('names')
        
        if not values_col or not names_col:
            return self._create_empty_chart("Please select Values and Names for pie chart")
        
        if values_col not in data.columns or names_col not in data.columns:
            return self._create_empty_chart("Selected columns not found in data")
        
        # Aggregate data for pie chart if needed
        pie_data = data.groupby(names_col)[values_col].sum().reset_index()
        
        # Create pie chart
        fig = px.pie(
            pie_data, 
            values=values_col, 
            names=names_col,
            title=f"Pie Chart: {values_col} by {names_col}",
            hover_data=[values_col]
        )
        
        # Update layout
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.01
            )
        )
        
        # Update traces for better hover information
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        return fig
    
    def _create_empty_chart(self, message):
        """Create an empty chart with a message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            showlegend=False,
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        return fig
    
    def create_correlation_heatmap(self, data):
        """Create a correlation heatmap for numeric columns"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return self._create_empty_chart("Need at least 2 numeric columns for correlation")
        
        # Calculate correlation matrix
        corr_matrix = data[numeric_cols].corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Correlation Heatmap",
            color_continuous_scale='RdBu_r'
        )
        
        return fig
    
    def create_histogram(self, data, column):
        """Create a histogram for a specific column"""
        if column not in data.columns:
            return self._create_empty_chart("Column not found in data")
        
        fig = px.histogram(
            data, 
            x=column,
            title=f"Distribution of {column}",
            labels={column: column.replace('_', ' ').title()}
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis_title=column.replace('_', ' ').title(),
            yaxis_title="Frequency"
        )
        
        return fig
