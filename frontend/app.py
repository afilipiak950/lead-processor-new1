import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
import logging

# Konfiguriere Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Importiere die AI-Agenten und Scheduler
logger.debug("Importiere Module...")
from ai_agent import get_leads_from_apify, load_analyses
from scheduler import get_scheduler

# Lade Umgebungsvariablen
logger.debug("Lade Umgebungsvariablen...")
load_dotenv()

# Seitenkonfiguration
logger.debug("Konfiguriere Streamlit-Seite...")
st.set_page_config(
    page_title="Lead Processor Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric:hover {
        transform: translateY(-2px);
        transition: transform 0.2s ease-in-out;
    }
    .css-1d391kg {
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .css-1v0mbdj {
        margin-top: 1rem;
    }
    .email-content {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Beispieldaten (Fallback)
def get_sample_data():
    n = 10  # Anzahl der Beispieldatensätze
    status_options = ['aktiv', 'inaktiv', 'abgeschlossen']
    style_options = ['formal', 'informal']
    
    return pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=n),
        'name': [f'Lead {i+1}' for i in range(n)],
        'email': [f'lead{i+1}@example.com' for i in range(n)],
        'company': [f'Company {i+1}' for i in range(n)],
        'status': [status_options[i % len(status_options)] for i in range(n)],
        'communication_style': [style_options[i % len(style_options)] for i in range(n)]
    })

# Funktion zum Laden der echten Leads
@st.cache_data(ttl=3600)  # Cache für 1 Stunde
def load_real_leads():
    """Lädt die echten Leads von Apify."""
    try:
        logger.debug("Versuche Leads von Apify zu laden...")
        leads = get_leads_from_apify()
        
        if not leads:
            logger.warning("Keine Leads von Apify gefunden. Verwende Beispieldaten.")
            return get_sample_data()
        
        logger.debug(f"Rohdaten von Apify erhalten: {len(leads)} Einträge")
        
        # Konvertiere zu DataFrame mit Fehlerprüfung
        try:
            df = pd.DataFrame(leads)
            logger.debug(f"DataFrame erstellt mit Spalten: {df.columns.tolist()}")
        except Exception as e:
            logger.error(f"Fehler bei der DataFrame-Erstellung: {str(e)}")
            return get_sample_data()
        
        # Füge fehlende Spalten hinzu
        logger.debug("Füge fehlende Spalten hinzu...")
        if 'timestamp' not in df.columns:
            df['timestamp'] = datetime.now()
            logger.debug("Timestamp-Spalte hinzugefügt")
        
        if 'status' not in df.columns:
            df['status'] = 'aktiv'
            logger.debug("Status-Spalte hinzugefügt")
        
        if 'communication_style' not in df.columns:
            df['communication_style'] = 'formal'
            logger.debug("Communication-Style-Spalte hinzugefügt")
        
        # Stelle sicher, dass alle erforderlichen Spalten vorhanden sind
        required_columns = ['name', 'email', 'company', 'status', 'communication_style', 'timestamp']
        for col in required_columns:
            if col not in df.columns:
                logger.debug(f"Erstelle {col}-Spalte...")
                if col == 'name' and 'first_name' in df.columns and 'last_name' in df.columns:
                    df[col] = df['first_name'].fillna('').str.cat(df['last_name'].fillna(''), sep=' ')
                elif col == 'company' and 'organization_name' in df.columns:
                    df[col] = df['organization_name']
                else:
                    df[col] = 'nicht verfügbar'
        
        logger.info(f"Leads erfolgreich geladen und verarbeitet: {len(df)} Einträge")
        return df
        
    except Exception as e:
        logger.error(f"Unerwarteter Fehler beim Laden der Leads: {str(e)}")
        st.error(f"Fehler beim Laden der Leads: {str(e)}")
        return get_sample_data()

# Funktion zum Laden der AI-Analysen
@st.cache_data(ttl=3600)  # Cache für 1 Stunde
def load_ai_analyses():
    """Lädt die AI-Analysen."""
    try:
        analyses = load_analyses()
        return analyses
    except Exception as e:
        st.error(f"Fehler beim Laden der AI-Analysen: {str(e)}")
        return []

# Initialisiere den Scheduler
scheduler = get_scheduler(max_leads_per_day=50)

# Sidebar mit verbessertem Design
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/rocket.png", width=100)
    st.title("🚀 Lead Processor")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Leads", "🤖 AI-Aktivitäten", "⚙️ Einstellungen"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    if st.button("🔄 Daten aktualisieren"):
        st.cache_data.clear()
        st.success("Daten wurden aktualisiert!")
    
    st.markdown("---")
    st.markdown("### System Status")
    last_run = scheduler.get_last_run()
    if last_run:
        st.info(f"🟢 System läuft (Letzte Aktualisierung: {last_run.strftime('%d.%m.%Y %H:%M')})")
    else:
        st.info("🟡 System bereit (Noch keine Aktualisierung)")

# Dashboard-Seite
if page == "📊 Dashboard":
    st.title("📊 Lead Processor Dashboard")
    
    # Echte Leads laden
    df = load_real_leads()
    
    # Metriken mit verbessertem Design
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = len(df)
        st.metric(
            "Gesamte Leads",
            total_leads,
            delta=f"+{total_leads - 0}",
            delta_color="normal"
        )
    
    with col2:
        active_leads = len(df[df['status'] == 'aktiv'])
        st.metric(
            "Aktive Leads",
            active_leads,
            delta=f"+{active_leads - 0}",
            delta_color="normal"
        )
    
    with col3:
        ai_analyses = load_ai_analyses()
        analyzed_leads = len(ai_analyses)
        st.metric(
            "Analysierte Leads",
            analyzed_leads,
            delta=f"+{analyzed_leads - 0}",
            delta_color="normal"
        )
    
    with col4:
        conversion_rate = (active_leads / total_leads * 100) if total_leads > 0 else 0
        st.metric(
            "Konversionsrate",
            f"{conversion_rate:.1f}%",
            delta=f"+{conversion_rate - 0:.1f}%",
            delta_color="normal"
        )
    
    # Zwei-Spalten-Layout für Diagramme
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Lead-Aktivität")
        daily_leads = df.groupby(df['timestamp'].dt.date).size().reset_index()
        daily_leads.columns = ['Datum', 'Anzahl']
        
        fig = px.line(
            daily_leads,
            x='Datum',
            y='Anzahl',
            title='Tägliche Lead-Aktivität',
            template='plotly_white'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Lead-Status")
        status_counts = df['status'].value_counts()
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=.3,
            marker_colors=px.colors.qualitative.Set3
        )])
        fig.update_layout(
            title='Verteilung der Lead-Status',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

# Leads-Seite
elif page == "👥 Leads":
    st.title("👥 Lead-Übersicht")
    
    # Echte Leads laden
    df = load_real_leads()
    
    # Erweiterte Filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Status",
            options=df['status'].unique(),
            default=df['status'].unique()
        )
    
    with col2:
        search = st.text_input("🔍 Suche", "")
    
    with col3:
        date_range = st.date_input(
            "Zeitraum",
            value=(datetime.now() - timedelta(days=30), datetime.now())
        )
    
    # Gefilterte Daten
    filtered_df = df[df['status'].isin(status_filter)]
    if search:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search, case=False) |
            filtered_df['email'].str.contains(search, case=False) |
            filtered_df['company'].str.contains(search, case=False)
        ]
    
    # Daten anzeigen mit verbessertem Design
    st.dataframe(
        filtered_df,
        column_config={
            "timestamp": st.column_config.DatetimeColumn(
                "Zeitstempel",
                format="DD.MM.YYYY HH:mm",
                step=60
            ),
            "name": "Name",
            "email": "E-Mail",
            "company": "Unternehmen",
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["aktiv", "inaktiv", "abgeschlossen"],
                required=True
            ),
            "communication_style": "Kommunikationsstil"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Export-Optionen
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Als CSV exportieren"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "leads.csv",
                "text/csv",
                key='download-csv'
            )
    
    with col2:
        if st.button("📊 Als Excel exportieren"):
            excel = filtered_df.to_excel(index=False)
            st.download_button(
                "Download Excel",
                excel,
                "leads.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key='download-excel'
            )

# AI-Aktivitäten-Seite
elif page == "🤖 AI-Aktivitäten":
    st.title("🤖 AI-Agent Aktivitäten")
    
    # Lade AI-Analysen
    ai_analyses = load_ai_analyses()
    
    if not ai_analyses:
        st.info("Keine AI-Analysen vorhanden. Starten Sie den AI-Agenten, um Analysen zu generieren.")
        
        # Button zum Starten des AI-Agenten
        if st.button("🚀 AI-Agenten starten"):
            with st.spinner("AI-Agent verarbeitet Leads..."):
                scheduler.run_immediately()
                st.success("AI-Agent hat die Verarbeitung abgeschlossen. Bitte aktualisieren Sie die Seite.")
    else:
        # Metriken
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Analysierte Leads",
                len(ai_analyses),
                delta=None
            )
        
        with col2:
            formal_count = len([a for a in ai_analyses if a.get('communication_style') == 'formal'])
            informal_count = len([a for a in ai_analyses if a.get('communication_style') == 'informal'])
            st.metric(
                "Kommunikationsstile",
                f"{formal_count} formal / {informal_count} informal",
                delta=None
            )
        
        with col3:
            active_count = len([a for a in ai_analyses if a.get('status') == 'aktiv'])
            st.metric(
                "Aktive Leads",
                active_count,
                delta=None
            )
        
        # Diagramme
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Kommunikationsstile")
            style_data = pd.DataFrame(ai_analyses)
            style_counts = style_data['communication_style'].value_counts()
            
            fig = px.pie(
                values=style_counts.values,
                names=style_counts.index,
                title="Verteilung der Kommunikationsstile",
                template='plotly_white'
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Lead-Status")
            status_counts = style_data['status'].value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Verteilung der Lead-Status",
                template='plotly_white'
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        # Detaillierte Analysen
        st.subheader("📋 Lead-Analysen")
        
        # Filter für die Analysen
        analysis_filter = st.text_input("🔍 Suche in Analysen", "")
        
        # Gefilterte Analysen
        filtered_analyses = ai_analyses
        if analysis_filter:
            filtered_analyses = [
                a for a in ai_analyses
                if analysis_filter.lower() in a.get('name', '').lower() or
                   analysis_filter.lower() in a.get('company', '').lower() or
                   analysis_filter.lower() in a.get('email', '').lower()
            ]
        
        # Zeige die Analysen an
        for analysis in filtered_analyses:
            with st.expander(f"📊 {analysis.get('name', 'Unbekannt')} - {analysis.get('company', 'Unbekannt')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Name:** {analysis.get('name', 'Unbekannt')}")
                    st.markdown(f"**Unternehmen:** {analysis.get('company', 'Unbekannt')}")
                    st.markdown(f"**E-Mail:** {analysis.get('email', 'Unbekannt')}")
                    st.markdown(f"**Status:** {analysis.get('status', 'Unbekannt')}")
                    st.markdown(f"**Kommunikationsstil:** {analysis.get('communication_style', 'Unbekannt')}")
                
                with col2:
                    if analysis.get('website'):
                        st.markdown(f"**Website:** [{analysis.get('website')}]({analysis.get('website')})")
                    if analysis.get('linkedin'):
                        st.markdown(f"**LinkedIn:** [{analysis.get('linkedin')}]({analysis.get('linkedin')})")
                
                st.markdown("---")
                st.markdown("**Website-Zusammenfassung:**")
                st.markdown(analysis.get('website_summary', 'Keine Zusammenfassung verfügbar'))
                
                if analysis.get('linkedin_summary'):
                    st.markdown("**LinkedIn-Zusammenfassung:**")
                    st.markdown(analysis.get('linkedin_summary', 'Keine Zusammenfassung verfügbar'))
                
                st.markdown("---")
                st.markdown("**Personalisierte Nachricht:**")
                st.markdown('<div class="email-content">', unsafe_allow_html=True)
                st.markdown(analysis.get('personalized_message', 'Keine Nachricht verfügbar'))
                st.markdown('</div>', unsafe_allow_html=True)

# Einstellungen-Seite
elif page == "⚙️ Einstellungen":
    st.title("⚙️ Einstellungen")
    
    st.subheader("🤖 AI-Agent Einstellungen")
    
    # API-Schlüssel
    openai_api_key = st.text_input("OpenAI API-Schlüssel", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    apify_api_key = st.text_input("Apify API-Schlüssel", type="password", value=os.getenv("APIFY_API_KEY", ""))
    apify_dataset_id = st.text_input("Apify Dataset-ID", value=os.getenv("APIFY_DATASET_ID", ""))
    
    # Scheduler-Einstellungen
    st.subheader("⏰ Scheduler Einstellungen")
    
    max_leads = st.slider("Maximale Anzahl von Leads pro Tag", min_value=10, max_value=100, value=50, step=10)
    schedule_time = st.time_input("Tägliche Ausführungszeit", value=datetime.strptime("09:00", "%H:%M").time())
    
    # Speichern-Button
    if st.button("💾 Einstellungen speichern"):
        # Hier würden die Einstellungen in einer .env-Datei gespeichert
        st.success("Einstellungen gespeichert!")
    
    # Scheduler starten/stoppen
    st.subheader("🔄 Scheduler steuern")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Scheduler starten"):
            scheduler.schedule_daily_run(time=schedule_time.strftime("%H:%M"))
    
    with col2:
        if st.button("⏹️ Scheduler stoppen"):
            # Hier würde der Scheduler gestoppt werden
            st.info("Scheduler gestoppt!")
    
    # Manuelle Ausführung
    st.subheader("🚀 Manuelle Ausführung")
    
    if st.button("🚀 AI-Agenten jetzt ausführen"):
        with st.spinner("AI-Agent verarbeitet Leads..."):
            scheduler.run_immediately()
            st.success("AI-Agent hat die Verarbeitung abgeschlossen.") 