"""
文件处理Agent
"""
import os
import json
import csv
from typing import Dict, Any, List
from decimal import Decimal
from io import StringIO, BytesIO
import base64

from .base import BaseAgent, AgentResult, AgentError


class FileProcessorAgent(BaseAgent):
    """文件处理Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="FileProcessorAgent",
            agent_type="file",
            capabilities=["file_processing", "format_conversion"],
            config=config
        )
        self.supported_formats = self.config.get(
            "supported_formats", 
            ["txt", "csv", "json", "md"]
        )
        self.max_file_size = self.config.get("max_file_size", 10 * 1024 * 1024)  # 10MB
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AgentResult:
        """执行文件处理"""
        operation = input_data.get("operation", "read")
        file_data = input_data.get("file_data")
        file_format = input_data.get("file_format", "txt")
        output_format = input_data.get("output_format")
        
        try:
            if operation == "read":
                result = await self._read_file(file_data, file_format)
            elif operation == "write":
                result = await self._write_file(
                    input_data.get("content"), 
                    file_format,
                    input_data.get("filename", "output")
                )
            elif operation == "convert":
                result = await self._convert_file(file_data, file_format, output_format)
            elif operation == "analyze":
                result = await self._analyze_file(file_data, file_format)
            else:
                raise AgentError(f"Unsupported operation: {operation}")
            
            return AgentResult(
                success=True,
                data={
                    "operation": operation,
                    "file_format": file_format,
                    "output_format": output_format,
                    "result": result
                },
                metadata={
                    "supported_formats": self.supported_formats,
                    "max_file_size": self.max_file_size
                }
            )
            
        except Exception as e:
            raise AgentError(f"File processing failed: {str(e)}")
    
    async def _read_file(self, file_data: str, file_format: str) -> Dict[str, Any]:
        """读取文件"""
        if file_format == "txt" or file_format == "md":
            return {
                "content": file_data,
                "type": "text",
                "line_count": len(file_data.split('\n')),
                "char_count": len(file_data)
            }
        
        elif file_format == "csv":
            try:
                csv_reader = csv.DictReader(StringIO(file_data))
                rows = list(csv_reader)
                return {
                    "content": rows,
                    "type": "structured",
                    "row_count": len(rows),
                    "columns": list(rows[0].keys()) if rows else []
                }
            except Exception as e:
                raise AgentError(f"Failed to parse CSV: {str(e)}")
        
        elif file_format == "json":
            try:
                json_data = json.loads(file_data)
                return {
                    "content": json_data,
                    "type": "structured",
                    "data_type": type(json_data).__name__
                }
            except Exception as e:
                raise AgentError(f"Failed to parse JSON: {str(e)}")
        
        else:
            raise AgentError(f"Unsupported file format for reading: {file_format}")
    
    async def _write_file(self, content: Any, file_format: str, filename: str) -> Dict[str, Any]:
        """写入文件"""
        if file_format == "txt" or file_format == "md":
            file_content = str(content)
        
        elif file_format == "csv":
            if isinstance(content, list) and len(content) > 0:
                output = StringIO()
                if isinstance(content[0], dict):
                    writer = csv.DictWriter(output, fieldnames=content[0].keys())
                    writer.writeheader()
                    writer.writerows(content)
                else:
                    writer = csv.writer(output)
                    writer.writerows(content)
                file_content = output.getvalue()
            else:
                raise AgentError("CSV content must be a list of dictionaries or lists")
        
        elif file_format == "json":
            file_content = json.dumps(content, indent=2, ensure_ascii=False)
        
        else:
            raise AgentError(f"Unsupported file format for writing: {file_format}")
        
        # 在实际应用中，这里会保存到文件系统或云存储
        # 现在返回文件内容的base64编码作为示例
        file_bytes = file_content.encode('utf-8')
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')
        
        return {
            "filename": f"{filename}.{file_format}",
            "size": len(file_bytes),
            "content_base64": file_base64,
            "message": f"File {filename}.{file_format} created successfully"
        }
    
    async def _convert_file(
        self, 
        file_data: str, 
        input_format: str, 
        output_format: str
    ) -> Dict[str, Any]:
        """转换文件格式"""
        # 首先读取原始文件
        read_result = await self._read_file(file_data, input_format)
        content = read_result["content"]
        
        # 转换为目标格式
        if input_format == "csv" and output_format == "json":
            converted_content = json.dumps(content, indent=2, ensure_ascii=False)
        
        elif input_format == "json" and output_format == "csv":
            if isinstance(content, list) and len(content) > 0:
                output = StringIO()
                if isinstance(content[0], dict):
                    writer = csv.DictWriter(output, fieldnames=content[0].keys())
                    writer.writeheader()
                    writer.writerows(content)
                    converted_content = output.getvalue()
                else:
                    raise AgentError("JSON content must be a list of dictionaries for CSV conversion")
            else:
                raise AgentError("JSON content must be a non-empty list for CSV conversion")
        
        elif output_format == "txt":
            if isinstance(content, str):
                converted_content = content
            else:
                converted_content = str(content)
        
        else:
            raise AgentError(f"Conversion from {input_format} to {output_format} not supported")
        
        return {
            "original_format": input_format,
            "target_format": output_format,
            "converted_content": converted_content,
            "size": len(converted_content)
        }
    
    async def _analyze_file(self, file_data: str, file_format: str) -> Dict[str, Any]:
        """分析文件"""
        read_result = await self._read_file(file_data, file_format)
        
        analysis = {
            "file_format": file_format,
            "size": len(file_data),
            "type": read_result["type"]
        }
        
        if file_format in ["txt", "md"]:
            analysis.update({
                "line_count": read_result["line_count"],
                "char_count": read_result["char_count"],
                "word_count": len(file_data.split())
            })
        
        elif file_format == "csv":
            analysis.update({
                "row_count": read_result["row_count"],
                "column_count": len(read_result["columns"]),
                "columns": read_result["columns"]
            })
        
        elif file_format == "json":
            content = read_result["content"]
            analysis.update({
                "data_type": read_result["data_type"],
                "structure": self._analyze_json_structure(content)
            })
        
        return analysis
    
    def _analyze_json_structure(self, data: Any) -> Dict[str, Any]:
        """分析JSON结构"""
        if isinstance(data, dict):
            return {
                "type": "object",
                "keys": list(data.keys()),
                "key_count": len(data)
            }
        elif isinstance(data, list):
            return {
                "type": "array",
                "length": len(data),
                "item_types": list(set(type(item).__name__ for item in data[:10]))  # 前10个元素的类型
            }
        else:
            return {
                "type": type(data).__name__,
                "value": str(data)[:100]  # 前100个字符
            }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        operation = input_data.get("operation", "read")
        if operation not in ["read", "write", "convert", "analyze"]:
            return False
        
        file_format = input_data.get("file_format", "txt")
        if file_format not in self.supported_formats:
            return False
        
        if operation in ["read", "convert", "analyze"]:
            file_data = input_data.get("file_data")
            if not file_data or not isinstance(file_data, str):
                return False
            
            if len(file_data) > self.max_file_size:
                return False
        
        if operation == "write":
            content = input_data.get("content")
            if content is None:
                return False
        
        if operation == "convert":
            output_format = input_data.get("output_format")
            if not output_format or output_format not in self.supported_formats:
                return False
        
        return True
    
    def get_cost_estimate(self, input_data: Dict[str, Any]) -> Decimal:
        """获取成本估算"""
        operation = input_data.get("operation", "read")
        file_data = input_data.get("file_data", "")
        file_size = len(file_data)
        
        # 基础成本
        base_cost = Decimal("0.002")
        
        # 根据操作类型调整成本
        operation_multipliers = {
            "read": Decimal("1.0"),
            "write": Decimal("1.2"),
            "convert": Decimal("1.5"),
            "analyze": Decimal("1.3")
        }
        
        cost = base_cost * operation_multipliers.get(operation, Decimal("1.0"))
        
        # 根据文件大小调整成本
        if file_size > 1024 * 1024:  # 1MB
            cost *= Decimal("2.0")
        elif file_size > 100 * 1024:  # 100KB
            cost *= Decimal("1.5")
        
        return cost
