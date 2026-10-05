def build_diagnosis_query(pest_label: str, crop: str | None) -> str:
    crop_context = f" Cultivo: {crop}." if crop else ""
    return (
        f"Información agronómica sobre la plaga {pest_label}."
        f"{crop_context} Síntomas, ciclo, daños y manejo integrado."
    )
