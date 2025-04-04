from typing import Dict, List, Any, TypedDict, Annotated
from langgraph.graph import Graph, StateGraph
from lead_processor import LeadProcessor
from sheets_manager import SheetsManager
import json

# Definiere den State für den Graph
class LeadState(TypedDict):
    leads: List[Dict]
    processed_leads: List[Dict]
    current_lead: Dict
    error: str

def create_lead_processing_graph():
    # Initialisiere die Komponenten
    lead_processor = LeadProcessor()
    sheets_manager = SheetsManager()
    
    # Definiere die Workflow-Funktionen
    def fetch_leads(state: LeadState) -> LeadState:
        try:
            leads = lead_processor.fetch_leads_from_apify()
            return {"leads": leads, "processed_leads": [], "current_lead": {}, "error": ""}
        except Exception as e:
            return {"leads": [], "processed_leads": [], "current_lead": {}, "error": str(e)}
    
    def process_next_lead(state: LeadState) -> LeadState:
        if not state["leads"]:
            return state
            
        current_lead = state["leads"][0]
        remaining_leads = state["leads"][1:]
        
        try:
            processed_lead = lead_processor.process_lead(current_lead)
            sheets_manager.append_lead(processed_lead)
            
            return {
                "leads": remaining_leads,
                "processed_leads": state["processed_leads"] + [processed_lead],
                "current_lead": processed_lead,
                "error": ""
            }
        except Exception as e:
            return {
                "leads": remaining_leads,
                "processed_leads": state["processed_leads"],
                "current_lead": current_lead,
                "error": str(e)
            }
    
    def should_continue(state: LeadState) -> bool:
        return len(state["leads"]) > 0
    
    # Erstelle den Graph
    workflow = StateGraph(LeadState)
    
    # Füge die Nodes hinzu
    workflow.add_node("fetch_leads", fetch_leads)
    workflow.add_node("process_lead", process_next_lead)
    
    # Definiere die Edges
    workflow.add_edge("fetch_leads", "process_lead")
    workflow.add_conditional_edges(
        "process_lead",
        should_continue,
        {
            True: "process_lead",
            False: "end"
        }
    )
    
    # Setze den Entry Point
    workflow.set_entry_point("fetch_leads")
    
    return workflow.compile()

def main():
    # Erstelle und starte den Graph
    graph = create_lead_processing_graph()
    
    # Initialisiere den State
    initial_state = {
        "leads": [],
        "processed_leads": [],
        "current_lead": {},
        "error": ""
    }
    
    # Führe den Graph aus
    final_state = graph.invoke(initial_state)
    
    # Gib die Ergebnisse aus
    print(f"Verarbeitete Leads: {len(final_state['processed_leads'])}")
    if final_state["error"]:
        print(f"Fehler aufgetreten: {final_state['error']}")

if __name__ == "__main__":
    main() 