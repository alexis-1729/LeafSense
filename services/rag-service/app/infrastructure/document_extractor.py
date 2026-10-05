from io import BytesIO

from pypdf import PdfReader


class DocumentExtractor:
    @staticmethod
    def extract(content: bytes, extension: str) -> str:
        try:
            if extension in {"txt", "md"}:
                return content.decode("utf-8-sig")
            if extension == "pdf":
                reader = PdfReader(BytesIO(content), strict=True)
                if reader.is_encrypted:
                    raise ValueError("Encrypted PDFs are not supported")
                return "\n".join(page.extract_text() or "" for page in reader.pages)
        except (UnicodeDecodeError, OSError, ValueError) as exc:
            if isinstance(exc, ValueError) and str(exc) == "Encrypted PDFs are not supported":
                raise
            raise ValueError("Document could not be parsed") from exc
        except Exception as exc:
            raise ValueError("Document could not be parsed") from exc
        raise ValueError("Unsupported document format")
