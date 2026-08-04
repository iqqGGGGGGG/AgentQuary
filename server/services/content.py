import asyncio
import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx


MAX_DOWNLOAD_BYTES = 1_000_000
MAX_CONTENT_CHARS = 12_000
URL_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)


class ContentInputError(ValueError):
    pass


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str):
        if tag in {"script", "style", "noscript", "svg"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str):
        if not self._ignored_depth:
            text = " ".join(data.split())
            if text:
                self.parts.append(text)


async def _ensure_public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ContentInputError("请输入有效的公开网页链接")

    try:
        addresses = await asyncio.to_thread(
            socket.getaddrinfo, parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)
        )
    except socket.gaierror as exc:
        raise ContentInputError("无法解析该网页地址") from exc

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            raise ContentInputError("不支持访问本机或内网地址")


def _html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return "\n".join(parser.parts)


async def _fetch_url(url: str) -> str:
    current_url = url
    headers = {"User-Agent": "AgentQuary/1.0 (+knowledge quiz content reader)"}

    async with httpx.AsyncClient(timeout=httpx.Timeout(15), headers=headers) as client:
        for _ in range(4):
            await _ensure_public_url(current_url)
            async with client.stream("GET", current_url, follow_redirects=False) as response:
                if response.status_code in {301, 302, 303, 307, 308}:
                    location = response.headers.get("location")
                    if not location:
                        raise ContentInputError("网页跳转地址无效")
                    current_url = urljoin(current_url, location)
                    continue

                if response.status_code >= 400:
                    raise ContentInputError(f"网页读取失败（HTTP {response.status_code}）")

                content_type = response.headers.get("content-type", "").lower()
                if not any(kind in content_type for kind in ("text/html", "text/plain", "application/xhtml+xml")):
                    raise ContentInputError("该链接不是可读取的文本网页")

                chunks: list[bytes] = []
                total = 0
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise ContentInputError("网页内容过大，请粘贴需要学习的正文")
                    chunks.append(chunk)

                encoding = response.encoding or "utf-8"
                raw_text = b"".join(chunks).decode(encoding, errors="replace")
                text = _html_to_text(raw_text) if "html" in content_type else raw_text
                text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
                if len(text) < 20:
                    raise ContentInputError("网页正文过少，无法生成有效题目")
                return text[:MAX_CONTENT_CHARS]

    raise ContentInputError("网页跳转次数过多")


async def normalize_content(content: str) -> str:
    clean = content.strip()
    if not clean:
        raise ContentInputError("请输入学习主题或内容")
    if URL_PATTERN.fullmatch(clean):
        return await _fetch_url(clean)
    return clean[:MAX_CONTENT_CHARS]
