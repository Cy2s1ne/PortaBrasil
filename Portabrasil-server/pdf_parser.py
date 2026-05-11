import os
import time
import asyncio
from typing import Optional, Callable, Union
from pathlib import Path

from zai import ZhipuAiClient
from zai.core import APIStatusError


class PDFParser:
    """
    基于智谱 AI 的 PDF 解析工具类

    支持同步解析、异步解析、回调通知三种模式
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        polling_interval: int = 2,
        max_polling_time: int = 300
    ):
        """
        初始化解析器

        Args:
            api_key: 智谱 API Key，若为 None 则从环境变量 ZHIPU_API_KEY 读取
            polling_interval: 轮询间隔秒数
            max_polling_time: 最大轮询时间（秒），超时将抛出异常
        """
        self.client = ZhipuAiClient(api_key=api_key or os.getenv("ZHIPU_API_KEY"))
        self.polling_interval = polling_interval
        self.max_polling_time = max_polling_time

    def _validate_file(self, file_path: Union[str, Path]) -> Path:
        """验证文件是否存在且可读"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        if not path.is_file():
            raise ValueError(f"路径不是文件: {file_path}")
        return path

    def parse(
        self,
        file_path: Union[str, Path],
        file_type: str | None = None,
        tool_type: str | None = None,
        format_type: str = "text",
        callback: Optional[Callable[[dict], None]] = None
    ) -> dict:
        """
        同步解析 PDF 文件

        Args:
            file_path: PDF 文件路径
            file_type: 文件类型，默认 "pdf"
            tool_type: 工具类型，默认 "lite"
            format_type: 输出格式，默认 "text"
            callback: 可选的回调函数，状态更新时会调用

        Returns:
            解析结果字典，包含 status 和 content 字段
        """
        path = self._validate_file(file_path)
        if path.stat().st_size <= 0:
            raise ValueError(f"PDF 文件为空: {file_path}")

        selected_file_type = (file_type or os.getenv("ZHIPU_PDF_FILE_TYPE") or "PDF").strip()
        selected_tool_type = (tool_type or os.getenv("ZHIPU_PDF_TOOL_TYPE") or "lite").strip()
        start_time = time.time()

        # 1. 创建解析任务
        response = self._create_parse_task(path, selected_file_type, selected_tool_type)

        task_id = getattr(response, "task_id", None)
        if not task_id:
            raise RuntimeError(f"创建任务失败，未获取到 task_id: {response}")

        # 2. 轮询获取结果
        while True:
            elapsed = time.time() - start_time
            if elapsed > self.max_polling_time:
                raise TimeoutError(f"解析超时（{self.max_polling_time}秒），task_id: {task_id}")

            res = self.client.file_parser.content(
                task_id=task_id,
                format_type=format_type
            )

            result = res.json()

            if callback:
                callback(result)

            status = result.get("status")
            if status == "succeeded":
                return result
            elif status == "failed":
                raise RuntimeError(f"解析失败: {result.get('error', 'unknown error')}")
            else:
                time.sleep(self.polling_interval)

    def _create_parse_task(self, path: Path, file_type: str, tool_type: str):
        attempts = [file_type]
        swapped_case = file_type.upper() if file_type != file_type.upper() else file_type.lower()
        if swapped_case not in attempts:
            attempts.append(swapped_case)

        errors: list[str] = []
        for current_file_type in attempts:
            try:
                with open(path, "rb") as f:
                    return self.client.file_parser.create(
                        file=f,
                        file_type=current_file_type,
                        tool_type=tool_type,
                    )
            except APIStatusError as exc:
                message = str(exc)
                errors.append(f"file_type={current_file_type}, tool_type={tool_type}: {message}")
                if getattr(exc, "status_code", None) != 400:
                    break

        raise RuntimeError(
            "创建智谱 PDF 解析任务失败。"
            "请确认 ZHIPU_API_KEY 有效、文件是可解析 PDF，"
            "必要时设置 ZHIPU_PDF_TOOL_TYPE=prime。"
            f" 尝试详情: {' | '.join(errors)}"
        )

    async def aparse(
        self,
        file_path: Union[str, Path],
        file_type: str = "pdf",
        tool_type: str = "lite",
        format_type: str = "text",
        on_progress: Optional[Callable[[dict], None]] = None
    ) -> dict:
        """
        异步解析 PDF 文件（使用线程池避免阻塞）

        Args:
            file_path: PDF 文件路径
            file_type: 文件类型，默认 "pdf"
            tool_type: 工具类型，默认 "lite"
            format_type: 输出格式，默认 "text"
            on_progress: 进度回调函数

        Returns:
            解析结果字典
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.parse,
            file_path, file_type, tool_type, format_type, on_progress
        )

    def parse_to_text(self, file_path: Union[str, Path]) -> str:
        """
        便捷方法：直接返回解析后的文本内容

        Args:
            file_path: PDF 文件路径

        Returns:
            解析后的纯文本内容
        """
        result = self.parse(file_path)
        return result.get("content", "")


# 便捷函数，保持向后兼容
_parser_instance: Optional[PDFParser] = None


def get_parser() -> PDFParser:
    """获取全局解析器实例（延迟初始化）"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = PDFParser()
    return _parser_instance


def parse_pdf(file_path: Union[str, Path], **kwargs) -> dict:
    """快捷函数：使用全局解析器解析 PDF"""
    return get_parser().parse(file_path, **kwargs)
