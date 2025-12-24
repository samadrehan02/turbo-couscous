def detect_schema(question: str, prev_schema: str | None = None) -> str | None:
    q = question.lower()

    if any(w in q for w in ["customer", "order", "shipping", "bought"]):
        return "commerce"

    if any(w in q for w in ["employee", "department", "salary"]):
        return "hr"

    return prev_schema
