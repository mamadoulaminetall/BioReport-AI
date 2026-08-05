import fitz

# En dessous de ce seuil (caractères/page), le PDF est probablement un scan sans
# couche de texte réelle (image pure) plutôt qu'un PDF texte natif.
MIN_CHARS_PER_PAGE = 40


def extract_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def extract_text_with_diagnostics(pdf_bytes: bytes) -> tuple[str, dict]:
    """Comme extract_text, mais signale si le PDF semble scanné (texte non extractible).
    Ne fait aucune bascule automatique vers un autre mode d'extraction — la décision
    revient à l'appelant, car un PDF scanné ne peut pas passer par l'anonymisation
    texte actuelle."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    n_pages = len(doc)
    text = "\n".join(page.get_text() for page in doc)
    chars_per_page = (len(text.strip()) / n_pages) if n_pages else 0
    diagnostics = {
        "pages": n_pages,
        "chars_per_page": round(chars_per_page, 1),
        "likely_scanned": chars_per_page < MIN_CHARS_PER_PAGE,
    }
    return text, diagnostics
