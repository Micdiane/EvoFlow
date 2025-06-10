"""
数据分析Agent
"""
import json
import pandas as pd
from typing import Dict, Any, List
from decimal import Decimal
from io import StringIO

from .base import BaseAgent, AgentResult, AgentError


class DataAnalysisAgent(BaseAgent):
    """数据分析Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="DataAnalysisAgent",
            agent_type="analysis",
            capabilities=["data_analysis", "statistics", "visualization"],
            config=config
        )
        self.max_data_size = self.config.get("max_data_size", "10MB")
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AgentResult:
        """执行数据分析"""
        data_source = input_data.get("data_source")
        analysis_type = input_data.get("analysis_type", "basic_stats")
        columns = input_data.get("columns", [])
        
        try:
            # 加载数据
            df = await self._load_data(data_source)
            
            # 执行分析
            analysis_result = await self._perform_analysis(df, analysis_type, columns)
            
            return AgentResult(
                success=True,
                data={
                    "analysis_type": analysis_type,
                    "data_shape": df.shape,
                    "columns": list(df.columns),
                    "analysis_result": analysis_result
                },
                metadata={
                    "data_size": len(str(data_source)),
                    "row_count": len(df),
                    "column_count": len(df.columns)
                }
            )
            
        except Exception as e:
            raise AgentError(f"Data analysis failed: {str(e)}")
    
    async def _load_data(self, data_source: Any) -> pd.DataFrame:
        """加载数据"""
        if isinstance(data_source, str):
            # 假设是CSV格式的字符串
            try:
                df = pd.read_csv(StringIO(data_source))
                return df
            except Exception:
                raise AgentError("Failed to parse CSV data")
        
        elif isinstance(data_source, list):
            # 假设是字典列表
            try:
                df = pd.DataFrame(data_source)
                return df
            except Exception:
                raise AgentError("Failed to create DataFrame from list")
        
        elif isinstance(data_source, dict):
            # 假设是字典格式的数据
            try:
                df = pd.DataFrame(data_source)
                return df
            except Exception:
                raise AgentError("Failed to create DataFrame from dict")
        
        else:
            raise AgentError("Unsupported data source format")
    
    async def _perform_analysis(
        self, 
        df: pd.DataFrame, 
        analysis_type: str, 
        columns: List[str]
    ) -> Dict[str, Any]:
        """执行数据分析"""
        
        if analysis_type == "basic_stats":
            return self._basic_statistics(df, columns)
        
        elif analysis_type == "correlation":
            return self._correlation_analysis(df, columns)
        
        elif analysis_type == "distribution":
            return self._distribution_analysis(df, columns)
        
        elif analysis_type == "missing_values":
            return self._missing_values_analysis(df)
        
        elif analysis_type == "summary":
            return self._data_summary(df)
        
        else:
            raise AgentError(f"Unsupported analysis type: {analysis_type}")
    
    def _basic_statistics(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """基础统计分析"""
        if columns:
            df_subset = df[columns]
        else:
            df_subset = df.select_dtypes(include=['number'])
        
        stats = df_subset.describe().to_dict()
        
        return {
            "statistics": stats,
            "numeric_columns": list(df_subset.columns)
        }
    
    def _correlation_analysis(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """相关性分析"""
        if columns:
            df_subset = df[columns]
        else:
            df_subset = df.select_dtypes(include=['number'])
        
        if len(df_subset.columns) < 2:
            raise AgentError("Need at least 2 numeric columns for correlation analysis")
        
        correlation_matrix = df_subset.corr().to_dict()
        
        return {
            "correlation_matrix": correlation_matrix,
            "analyzed_columns": list(df_subset.columns)
        }
    
    def _distribution_analysis(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """分布分析"""
        if not columns:
            columns = list(df.select_dtypes(include=['number']).columns)
        
        distributions = {}
        for col in columns:
            if col in df.columns:
                distributions[col] = {
                    "mean": float(df[col].mean()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                    "median": float(df[col].median()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                    "std": float(df[col].std()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                    "min": float(df[col].min()) if pd.api.types.is_numeric_dtype(df[col]) else str(df[col].min()),
                    "max": float(df[col].max()) if pd.api.types.is_numeric_dtype(df[col]) else str(df[col].max()),
                    "unique_count": int(df[col].nunique())
                }
        
        return {
            "distributions": distributions,
            "analyzed_columns": columns
        }
    
    def _missing_values_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """缺失值分析"""
        missing_counts = df.isnull().sum().to_dict()
        missing_percentages = (df.isnull().sum() / len(df) * 100).to_dict()
        
        return {
            "missing_counts": {k: int(v) for k, v in missing_counts.items()},
            "missing_percentages": {k: float(v) for k, v in missing_percentages.items()},
            "total_rows": len(df)
        }
    
    def _data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """数据摘要"""
        return {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage": df.memory_usage(deep=True).sum(),
            "missing_values": df.isnull().sum().sum()
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        data_source = input_data.get("data_source")
        if data_source is None:
            return False
        
        analysis_type = input_data.get("analysis_type", "basic_stats")
        valid_types = ["basic_stats", "correlation", "distribution", "missing_values", "summary"]
        if analysis_type not in valid_types:
            return False
        
        return True
    
    def get_cost_estimate(self, input_data: Dict[str, Any]) -> Decimal:
        """获取成本估算"""
        # 数据分析成本主要基于数据大小和复杂度
        data_source = input_data.get("data_source")
        data_size = len(str(data_source)) if data_source else 0
        
        base_cost = Decimal("0.005")  # 基础成本
        
        # 根据数据大小调整成本
        if data_size > 100000:  # 100KB
            base_cost *= Decimal("2.0")
        elif data_size > 10000:  # 10KB
            base_cost *= Decimal("1.5")
        
        analysis_type = input_data.get("analysis_type", "basic_stats")
        if analysis_type in ["correlation", "distribution"]:
            base_cost *= Decimal("1.3")  # 复杂分析成本更高
        
        return base_cost
