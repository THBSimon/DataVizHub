import pandas as pd
import plotly.graph_objects as go
import io
import base64
from typing import Union, List
import zipfile
import json

class ExportHelper:
    """Handle data and chart export functionality"""
    
    def export_data_to_csv(self, data: pd.DataFrame, filename: str = "data.csv") -> str:
        """
        Export DataFrame to CSV format
        
        Args:
            data: pandas.DataFrame to export
            filename: output filename
            
        Returns:
            str: CSV data as string
        """
        return data.to_csv(index=False)
    
    def export_data_to_excel(self, data: pd.DataFrame, filename: str = "data.xlsx") -> bytes:
        """
        Export DataFrame to Excel format
        
        Args:
            data: pandas.DataFrame to export
            filename: output filename
            
        Returns:
            bytes: Excel file as bytes
        """
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            data.to_excel(writer, index=False, sheet_name='Data')
        return buffer.getvalue()
    
    def export_multiple_sheets_excel(self, data_dict: dict, filename: str = "data.xlsx") -> bytes:
        """
        Export multiple DataFrames to different Excel sheets
        
        Args:
            data_dict: dict with sheet names as keys and DataFrames as values
            filename: output filename
            
        Returns:
            bytes: Excel file as bytes
        """
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            for sheet_name, data in data_dict.items():
                data.to_excel(writer, index=False, sheet_name=sheet_name)
        return buffer.getvalue()
    
    def export_chart_to_html(self, fig: go.Figure, filename: str = "chart.html") -> str:
        """
        Export Plotly figure to HTML format
        
        Args:
            fig: Plotly figure object
            filename: output filename
            
        Returns:
            str: HTML content as string
        """
        return fig.to_html(include_plotlyjs='cdn')
    
    def export_chart_to_json(self, fig: go.Figure) -> str:
        """
        Export Plotly figure to JSON format
        
        Args:
            fig: Plotly figure object
            
        Returns:
            str: JSON data as string
        """
        return fig.to_json()
    
    def create_summary_report(self, data: pd.DataFrame) -> dict:
        """
        Create a summary report of the dataset
        
        Args:
            data: pandas.DataFrame to analyze
            
        Returns:
            dict: Summary statistics and information
        """
        summary = {
            'basic_info': {
                'total_rows': len(data),
                'total_columns': len(data.columns),
                'memory_usage': data.memory_usage(deep=True).sum(),
                'column_names': data.columns.tolist()
            },
            'data_types': data.dtypes.astype(str).to_dict(),
            'missing_values': data.isnull().sum().to_dict(),
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # Numeric columns summary
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = data[numeric_cols].describe().to_dict()
        
        # Categorical columns summary
        categorical_cols = data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            summary['categorical_summary'][col] = {
                'unique_values': data[col].nunique(),
                'most_frequent': data[col].mode().iloc[0] if not data[col].mode().empty else None,
                'top_5_values': data[col].value_counts().head().to_dict()
            }
        
        return summary
    
    def export_summary_to_text(self, summary: dict) -> str:
        """
        Convert summary report to formatted text
        
        Args:
            summary: summary dictionary from create_summary_report
            
        Returns:
            str: Formatted text report
        """
        report = []
        report.append("=" * 50)
        report.append("DATA SUMMARY REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Basic info
        report.append("BASIC INFORMATION:")
        report.append("-" * 20)
        for key, value in summary['basic_info'].items():
            if key != 'column_names':
                report.append(f"{key.replace('_', ' ').title()}: {value}")
        report.append("")
        
        # Column information
        report.append("COLUMNS:")
        report.append("-" * 10)
        for i, col in enumerate(summary['basic_info']['column_names'], 1):
            dtype = summary['data_types'].get(col, 'unknown')
            missing = summary['missing_values'].get(col, 0)
            report.append(f"{i}. {col} ({dtype}) - Missing: {missing}")
        report.append("")
        
        # Numeric summary
        if summary['numeric_summary']:
            report.append("NUMERIC COLUMNS SUMMARY:")
            report.append("-" * 25)
            for col, stats in summary['numeric_summary'].items():
                report.append(f"\n{col}:")
                for stat, value in stats.items():
                    report.append(f"  {stat}: {value:.2f}" if isinstance(value, (int, float)) else f"  {stat}: {value}")
            report.append("")
        
        # Categorical summary
        if summary['categorical_summary']:
            report.append("CATEGORICAL COLUMNS SUMMARY:")
            report.append("-" * 30)
            for col, stats in summary['categorical_summary'].items():
                report.append(f"\n{col}:")
                report.append(f"  Unique values: {stats['unique_values']}")
                report.append(f"  Most frequent: {stats['most_frequent']}")
                report.append("  Top 5 values:")
                for value, count in stats['top_5_values'].items():
                    report.append(f"    {value}: {count}")
        
        return "\n".join(report)
    
    def create_export_package(self, data: pd.DataFrame, charts: List[go.Figure], 
                            chart_names: List[str] = None) -> bytes:
        """
        Create a ZIP package with data and charts
        
        Args:
            data: pandas.DataFrame to export
            charts: List of Plotly figures
            chart_names: List of names for charts (optional)
            
        Returns:
            bytes: ZIP file as bytes
        """
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add data files
            zip_file.writestr("data.csv", self.export_data_to_csv(data))
            zip_file.writestr("data.xlsx", self.export_data_to_excel(data))
            
            # Add summary report
            summary = self.create_summary_report(data)
            zip_file.writestr("summary_report.txt", self.export_summary_to_text(summary))
            zip_file.writestr("summary_report.json", json.dumps(summary, indent=2, default=str))
            
            # Add charts
            for i, chart in enumerate(charts):
                if chart_names and i < len(chart_names):
                    name = chart_names[i]
                else:
                    name = f"chart_{i+1}"
                
                # Export as HTML
                zip_file.writestr(f"charts/{name}.html", self.export_chart_to_html(chart))
                
                # Export as JSON
                zip_file.writestr(f"charts/{name}.json", self.export_chart_to_json(chart))
        
        return buffer.getvalue()
    
    def get_file_size_mb(self, data: Union[str, bytes]) -> float:
        """
        Get file size in MB
        
        Args:
            data: file data as string or bytes
            
        Returns:
            float: file size in MB
        """
        if isinstance(data, str):
            size_bytes = len(data.encode('utf-8'))
        else:
            size_bytes = len(data)
        
        return size_bytes / (1024 * 1024)
