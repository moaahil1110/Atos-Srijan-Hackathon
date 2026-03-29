from __future__ import annotations

import html
import json
import re
import subprocess
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PROVIDER_ROOT = ROOT / "docs" / "providers"


@dataclass(frozen=True)
class DocTarget:
    path: Path
    title: str
    urls: tuple[str, ...]


DOC_TARGETS = (
    DocTarget(
        path=PROVIDER_ROOT / "azure" / "azure-storage.md",
        title="Azure Storage",
        urls=(
            "https://learn.microsoft.com/en-us/azure/storage/common/storage-introduction",
            "https://learn.microsoft.com/en-us/azure/storage/blobs/security-recommendations",
        ),
    ),
    DocTarget(
        path=PROVIDER_ROOT / "azure" / "azure-compute.md",
        title="Azure Compute",
        urls=(
            "https://learn.microsoft.com/en-us/azure/virtual-machines/overview",
            "https://learn.microsoft.com/en-us/azure/virtual-machines/security-recommendations",
        ),
    ),
    DocTarget(
        path=PROVIDER_ROOT / "azure" / "azure-virtual-network.md",
        title="Azure Virtual Network",
        urls=("https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview",),
    ),
    DocTarget(
        path=PROVIDER_ROOT / "azure" / "azure-key-vault.md",
        title="Azure Key Vault",
        urls=(
            "https://learn.microsoft.com/en-us/azure/key-vault/general/overview",
            "https://learn.microsoft.com/en-us/azure/key-vault/general/security-features",
        ),
    ),
    DocTarget(
        path=PROVIDER_ROOT / "azure" / "azure-security-center.md",
        title="Azure Security Center and Fundamentals",
        urls=(
            "https://learn.microsoft.com/en-us/azure/security/fundamentals/overview",
            "https://learn.microsoft.com/en-us/azure/security/fundamentals/encryption-overview",
        ),
    ),
    DocTarget(
        path=PROVIDER_ROOT / "gcp" / "gcp-cloud-storage.md",
        title="GCP Cloud Storage",
        urls=(
            "https://cloud.google.com/storage/docs/concepts",
            "https://cloud.google.com/storage/docs/access-control",
        ),
    ),
    DocTarget(
        path=PROVIDER_ROOT / "gcp" / "gcp-compute-engine.md",
        title="GCP Compute Engine",
        urls=(
            "https://cloud.google.com/compute/docs/overview",
            "https://cloud.google.com/compute/docs/access",
        ),
    ),
    DocTarget(
        path=PROVIDER_ROOT / "gcp" / "gcp-vpc.md",
        title="GCP VPC",
        urls=(
            "https://cloud.google.com/vpc/docs/overview",
            "https://cloud.google.com/vpc/docs/firewall-policies-overview",
        ),
    ),
    DocTarget(
        path=PROVIDER_ROOT / "gcp" / "gcp-iam.md",
        title="GCP IAM",
        urls=(
            "https://cloud.google.com/iam/docs/overview",
            "https://cloud.google.com/iam/docs/best-practices-for-securing-service-accounts",
        ),
    ),
    DocTarget(
        path=PROVIDER_ROOT / "gcp" / "gcp-kms.md",
        title="GCP Cloud KMS",
        urls=(
            "https://cloud.google.com/kms/docs/concepts",
            "https://cloud.google.com/kms/docs/key-rotation",
        ),
    ),
)


REMOVE_TAGS = (
    "script",
    "style",
    "nav",
    "header",
    "footer",
    "aside",
    "noscript",
    "svg",
    "form",
    "button",
    "template",
)
BLOCK_TAGS = {
    "article",
    "div",
    "main",
    "section",
    "p",
    "blockquote",
    "table",
    "tr",
    "hr",
}


def fetch_html(url: str) -> str:
    result = subprocess.run(
        ["curl.exe", "-L", "--fail", "--silent", "--show-error", url],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"curl exited with code {result.returncode}")
    return result.stdout


def strip_unwanted(html_text: str) -> str:
    cleaned = re.sub(r"<!--.*?-->", "", html_text, flags=re.DOTALL)
    for tag in REMOVE_TAGS:
        cleaned = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}>",
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )
    return cleaned


def extract_main_html(html_text: str) -> str:
    cleaned = strip_unwanted(html_text)
    patterns = (
        r"<main\b[^>]*>(.*?)</main>",
        r"<article\b[^>]*>(.*?)</article>",
        r"<body\b[^>]*>(.*?)</body>",
    )
    for pattern in patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    return cleaned


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip()


class MarkdownExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.output: list[str] = []
        self.list_stack: list[str] = []
        self.href_stack: list[str | None] = []
        self.heading_level: int | None = None
        self.in_pre = False
        self.in_code = False
        self.current_anchor_parts: list[str] = []

    def append(self, text: str) -> None:
        if not text:
            return
        self.output.append(text)

    def ensure_blank_line(self) -> None:
        if not self.output:
            return
        joined = "".join(self.output)
        if joined.endswith("\n\n"):
            return
        if joined.endswith("\n"):
            self.output.append("\n")
        else:
            self.output.append("\n\n")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {key.lower(): value for key, value in attrs}

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.ensure_blank_line()
            self.heading_level = int(tag[1])
            self.append("#" * self.heading_level + " ")
            return

        if tag in BLOCK_TAGS:
            self.ensure_blank_line()
            return

        if tag == "br":
            self.append("\n")
            return

        if tag in {"ul", "ol"}:
            self.list_stack.append(tag)
            self.ensure_blank_line()
            return

        if tag == "li":
            indent = "  " * max(len(self.list_stack) - 1, 0)
            marker = "- " if not self.list_stack or self.list_stack[-1] == "ul" else "1. "
            if not "".join(self.output).endswith("\n"):
                self.append("\n")
            self.append(f"{indent}{marker}")
            return

        if tag == "pre":
            self.ensure_blank_line()
            self.in_pre = True
            self.append("```text\n")
            return

        if tag == "code":
            if not self.in_pre:
                self.in_code = True
                self.append("`")
            return

        if tag == "a":
            self.href_stack.append(attr_map.get("href"))
            self.current_anchor_parts = []
            return

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_level = None
            self.ensure_blank_line()
            return

        if tag in BLOCK_TAGS | {"li"}:
            if not "".join(self.output).endswith("\n"):
                self.append("\n")
            return

        if tag in {"ul", "ol"}:
            if self.list_stack:
                self.list_stack.pop()
            self.ensure_blank_line()
            return

        if tag == "pre":
            self.in_pre = False
            if not "".join(self.output).endswith("\n"):
                self.append("\n")
            self.append("```\n\n")
            return

        if tag == "code":
            if not self.in_pre and self.in_code:
                self.in_code = False
                self.append("`")
            return

        if tag == "a":
            href = self.href_stack.pop() if self.href_stack else None
            anchor_text = normalize_whitespace("".join(self.current_anchor_parts))
            self.current_anchor_parts = []
            if href and anchor_text and href not in anchor_text:
                self.append(f" ({href})")

    def handle_data(self, data: str) -> None:
        if not data:
            return

        if self.in_pre:
            self.append(data)
            return

        text = normalize_whitespace(data)
        if not text:
            return

        if self.href_stack:
            self.current_anchor_parts.append(text)

        if self.output:
            previous = self.output[-1]
            if previous and not previous.endswith((" ", "\n", "`", "(", "/")):
                self.append(" ")
        self.append(text)

    def get_markdown(self) -> str:
        markdown = "".join(self.output)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        markdown = re.sub(r"[ \t]+\n", "\n", markdown)
        markdown = re.sub(r"\n +", "\n", markdown)
        return markdown.strip() + "\n"


def extract_title(html_text: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return "Source Document"
    raw = normalize_whitespace(re.sub(r"<[^>]+>", "", match.group(1)))
    if not raw:
        return "Source Document"
    return raw.split(" - ")[0].split(" | ")[0].strip()


def html_to_markdown(html_text: str) -> str:
    parser = MarkdownExtractor()
    parser.feed(extract_main_html(html_text))
    parser.close()
    return clean_markdown(parser.get_markdown())


def is_placeholder(text: str) -> bool:
    return "Replace this file with the actual" in text


def content_is_substantial(markdown: str) -> bool:
    word_count = len(markdown.split())
    line_count = len([line for line in markdown.splitlines() if line.strip()])
    return word_count >= 200 and line_count >= 20


def clean_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    heading_index = next((index for index, line in enumerate(lines) if re.match(r"^#\s+\S", line)), 0)
    lines = lines[heading_index:]

    cleaned: list[str] = []
    skip_patterns = (
        r"^Read in .+ Edit \(",
        r"^#### Share via$",
        r"^Facebook \(",
        r"^Home \(https://docs\.cloud\.google\.com/",
        r"^Documentation \(https://docs\.cloud\.google\.com/",
        r"^Storage \(https://docs\.cloud\.google\.com/",
        r"^Cloud Storage \(https://docs\.cloud\.google\.com/",
        r"^Guides \(https://docs\.cloud\.google\.com/",
        r"^Note$",
        r"^Access to this page requires authorization\.",
        r"^You can try signing in",
        r"^You can try changing directories",
    )
    inline_replacements = (
        (
            " Stay organized with collections Save and categorize content based on your preferences.",
            "",
        ),
    )

    for line in lines:
        line = line.strip()
        if not line:
            cleaned.append("")
            continue
        for source, replacement in inline_replacements:
            line = line.replace(source, replacement)
        if any(re.search(pattern, line) for pattern in skip_patterns):
            continue
        if re.fullmatch(r"-", line):
            continue
        cleaned.append(line)

    normalized = "\n".join(cleaned)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip() + "\n"


def build_file_content(target: DocTarget, pages: Iterable[tuple[str, str, str]]) -> str:
    sections = [f"# {target.title}", "", "Source pages:"]
    for _, title, url in pages:
        sections.append(f"- {title}: {url}")
    sections.append("")

    for _, title, url in pages:
        sections.append(f"## {title}")
        sections.append("")
        sections.append(f"Source: {url}")
        sections.append("")
        sections.append(_)
        sections.append("")

    return "\n".join(sections).strip() + "\n"


def main() -> int:
    successes: list[str] = []
    failures: list[dict[str, str]] = []

    for target in DOC_TARGETS:
        existing = target.path.read_text(encoding="utf-8")
        page_sections: list[tuple[str, str, str]] = []
        target_failed = False

        for url in target.urls:
            try:
                html_text = fetch_html(url)
                title = extract_title(html_text)
                markdown = html_to_markdown(html_text)
                if not content_is_substantial(markdown):
                    raise RuntimeError("extracted content was too small to trust")
                page_sections.append((markdown, title, url))
                print(f"[ok] {url} -> {target.path.relative_to(ROOT)}")
            except Exception as exc:  # noqa: BLE001
                target_failed = True
                failures.append(
                    {
                        "url": url,
                        "file": str(target.path.relative_to(ROOT)),
                        "reason": str(exc),
                    }
                )
                print(
                    f"[failed] {url} -> {target.path.relative_to(ROOT)} "
                    f"(manual replacement needed: {exc})"
                )

        if target_failed or not page_sections:
            if is_placeholder(existing):
                print(f"[kept-placeholder] {target.path.relative_to(ROOT)}")
            else:
                print(f"[kept-existing] {target.path.relative_to(ROOT)}")
            continue

        target.path.write_text(build_file_content(target, page_sections), encoding="utf-8")
        successes.append(str(target.path.relative_to(ROOT)))

    print("\nSummary JSON:")
    print(
        json.dumps(
            {
                "replaced_files": successes,
                "failed_pages": failures,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
