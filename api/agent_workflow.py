from __future__ import annotations

from typing import Any, TypedDict


def build_report(analysis: dict[str, Any]) -> dict[str, Any]:
    """Deterministic report used directly and as an agent tool.

    It never diagnoses.  Keeping this function independent from an LLM makes the
    API reproducible and gives LangGraph/LangChain a safe, bounded tool later.
    """

    findings = []
    actions = []
    for task, probabilities in analysis.get("results", {}).items():
        if task == "view":
            continue
        probability = float(probabilities.get(task, 0.0))
        if probability >= 0.5:
            findings.append({"code": task, "probability": probability})
            actions.append(f"Revisar manualmente posible {task}.")

    privacy = analysis.get("privacy", {})
    if privacy.get("metadata_identifier_count", 0):
        findings.append({
            "code": "dicom_identifiers",
            "count": privacy["metadata_identifier_count"],
        })
        actions.append("Desidentificar metadata antes de compartir el archivo.")
    if privacy.get("pixel_text_review_required"):
        actions.append("Revisar texto incrustado en los pixeles mediante OCR.")

    return {
        "status": "review" if findings or actions else "ok",
        "findings": findings,
        "recommended_actions": list(dict.fromkeys(actions)),
        "disclaimer": "Informe de apoyo tecnico; no es diagnostico medico.",
        "engine": "deterministic-tool-workflow",
        "langgraph_ready": True,
    }


def langgraph_available() -> bool:
    try:
        import langgraph  # noqa: F401
    except ImportError:
        return False
    return True


class AnalysisState(TypedDict, total=False):
    analysis: dict[str, Any]
    report: dict[str, Any]


def run_report_workflow(analysis: dict[str, Any]) -> dict[str, Any]:
    """Run one bounded LangGraph node when installed, otherwise use the tool directly."""

    if not langgraph_available():
        return build_report(analysis)

    from langgraph.graph import END, START, StateGraph

    def reporting_node(state: AnalysisState) -> AnalysisState:
        report = build_report(state["analysis"])
        report["engine"] = "langgraph-deterministic-workflow"
        return {"report": report}

    graph = StateGraph(AnalysisState)
    graph.add_node("technical_report", reporting_node)
    graph.add_edge(START, "technical_report")
    graph.add_edge("technical_report", END)
    result = graph.compile().invoke({"analysis": analysis})
    return result["report"]
