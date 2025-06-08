import pandas as pd
import numpy as np
import io

class DataProcessor:
    """Handle data loading, filtering, and aggregation operations"""
    
    def load_data(self, uploaded_file):
        """
        Load data from uploaded CSV or Excel file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            pandas.DataFrame: Loaded data
        """
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                # Try different encodings for CSV files
                try:
                    data = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)  # Reset file pointer
                    data = pd.read_csv(uploaded_file, encoding='latin-1')
                    
            elif file_extension in ['xlsx', 'xls']:
                data = pd.read_excel(uploaded_file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Basic data cleaning
            data = self._clean_data(data)
            
            return data
            
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def _clean_data(self, data):
        """
        Perform basic data cleaning operations
        
        Args:
            data: pandas.DataFrame
            
        Returns:
            pandas.DataFrame: Cleaned data
        """
        # Remove completely empty rows and columns
        data = data.dropna(how='all').dropna(axis=1, how='all')
        
        # Convert string representations of numbers to numeric where possible
        for col in data.columns:
            if data[col].dtype == 'object':
                # Try to convert to numeric
                numeric_series = pd.to_numeric(data[col], errors='coerce')
                if not numeric_series.isna().all():
                    # If more than 50% of values can be converted, treat as numeric
                    if (numeric_series.notna().sum() / len(data)) > 0.5:
                        data[col] = numeric_series
        
        # Convert date columns
        for col in data.columns:
            if data[col].dtype == 'object':
                try:
                    # Try to parse as datetime
                    date_series = pd.to_datetime(data[col], errors='coerce', infer_datetime_format=True)
                    if not date_series.isna().all():
                        # If more than 50% of values can be converted, treat as datetime
                        if (date_series.notna().sum() / len(data)) > 0.5:
                            data[col] = date_series
                except:
                    pass
        
        return data
    
    def apply_filters(self, data, filters):
        """
        Apply column filters to the data
        
        Args:
            data: pandas.DataFrame
            filters: dict with column names as keys and filter values
            
        Returns:
            pandas.DataFrame: Filtered data
        """
        filtered_data = data.copy()
        
        for column, filter_value in filters.items():
            if column in filtered_data.columns:
                if isinstance(filter_value, list):
                    # Multiple selection filter (for categorical data)
                    filtered_data = filtered_data[filtered_data[column].isin(filter_value)]
                elif isinstance(filter_value, tuple) and len(filter_value) == 2:
                    # Range filter (for numeric data)
                    min_val, max_val = filter_value
                    filtered_data = filtered_data[
                        (filtered_data[column] >= min_val) & 
                        (filtered_data[column] <= max_val)
                    ]
        
        return filtered_data
    
    def aggregate_data(self, data, group_by_column, agg_column, agg_function):
        """
        Perform data aggregation
        
        Args:
            data: pandas.DataFrame
            group_by_column: str - column to group by
            agg_column: str - column to aggregate
            agg_function: str - aggregation function (sum, mean, count, min, max)
            
        Returns:
            pandas.DataFrame: Aggregated data
        """
        try:
            if agg_function == 'count':
                result = data.groupby(group_by_column)[agg_column].count().reset_index()
            elif agg_function == 'sum':
                result = data.groupby(group_by_column)[agg_column].sum().reset_index()
            elif agg_function == 'mean':
                result = data.groupby(group_by_column)[agg_column].mean().reset_index()
            elif agg_function == 'min':
                result = data.groupby(group_by_column)[agg_column].min().reset_index()
            elif agg_function == 'max':
                result = data.groupby(group_by_column)[agg_column].max().reset_index()
            else:
                raise ValueError(f"Unsupported aggregation function: {agg_function}")
            
            # Rename the aggregated column to include the function name
            result.columns = [group_by_column, f"{agg_function}_{agg_column}"]
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in aggregation: {str(e)}")
    
    def get_column_info(self, data):
        """
        Get information about columns in the dataset
        
        Args:
            data: pandas.DataFrame
            
        Returns:
            dict: Column information including types and unique values
        """
        info = {}
        
        for column in data.columns:
            col_info = {
                'dtype': str(data[column].dtype),
                'null_count': data[column].isnull().sum(),
                'unique_count': data[column].nunique(),
                'sample_values': data[column].head(3).tolist()
            }
            
            if data[column].dtype in ['int64', 'float64']:
                col_info['min'] = data[column].min()
                col_info['max'] = data[column].max()
                col_info['mean'] = data[column].mean()
            
            info[column] = col_info
        
        return info
