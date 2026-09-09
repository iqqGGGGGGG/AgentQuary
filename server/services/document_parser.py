import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 500_000


class DocumentParseError(Exception):
    pass


def _clean_text(text: str) -> str:
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_pdf(file_path: str) -> str:
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(file_path)
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text.strip())

        if not parts:
            raise DocumentParseError("PDF 中未找到可提取的文本内容")

        return _clean_text("\n\n".join(parts))
    except DocumentParseError:
        raise
    except Exception as e:
        logger.warning("PDF parse failed: %s", e)
        raise DocumentParseError(f"PDF 解析失败: {e}") from e


def parse_docx(file_path: str) -> str:
    try:
        from docx import Document

        doc = Document(file_path)
        parts: list[str] = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                parts.append(text)

        if not parts:
            raise DocumentParseError("Word 文档中未找到可提取的文本内容")

        return _clean_text("\n\n".join(parts))
    except DocumentParseError:
        raise
    except Exception as e:
        logger.warning("DOCX parse failed: %s", e)
        raise DocumentParseError(f"Word 文档解析失败: {e}") from e


def parse_text(file_path: str) -> str:
    try:
        text = Path(file_path).read_text(encoding="utf-8")
        if not text.strip():
            raise DocumentParseError("文本文件内容为空")
        return _clean_text(text)
    except DocumentParseError:
        raise
    except UnicodeDecodeError:
        try:
            text = Path(file_path).read_text(encoding="gbk")
            if not text.strip():
                raise DocumentParseError("文本文件内容为空")
            return _clean_text(text)
        except Exception as e:
            raise DocumentParseError(f"文本文件编码无法识别: {e}") from e
    except Exception as e:
        raise DocumentParseError(f"文本文件读取失败: {e}") from e


def parse_document(file_path: str, file_type: str) -> str:
    parsers = {
        ".pdf": parse_pdf,
        ".docx": parse_docx,
        ".txt": parse_text,
        ".md": parse_text,
    }

    parser = parsers.get(file_type.lower())
    if not parser:
        raise DocumentParseError(f"不支持的文件格式: {file_type}")

    text = parser(file_path)
    text = text.strip()

    if len(text) < 50:
        raise DocumentParseError("文档内容过少（少于50字），无法生成有效题目")

    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]

    return text
