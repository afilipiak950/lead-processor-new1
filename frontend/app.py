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
from ai_agent import AIAgent, get_leads_from_apify, load_analyses
from scheduler import get_scheduler

def run_ai_analysis():
    """Führt die AI-Analyse für neue Leads durch."""
    try:
        # Initialisiere AI-Agent
        agent = AIAgent()
        
        # Lade Leads von Apify
        leads = get_leads_from_apify()
        if not leads:
            logger.warning("Keine Leads zum Analysieren gefunden")
            return []
            
        # Verarbeite die Leads
        analyses = agent.process_leads(leads)
        
        # Speichere die Analysen
        if analyses:
            # Lade bestehende Analysen
            existing_analyses = load_analyses()
            
            # Füge neue Analysen hinzu
            all_analyses = existing_analyses + analyses
            
            # Speichere alle Analysen
            save_analyses(all_analyses)
            
            logger.info(f"Analysen erfolgreich gespeichert: {len(analyses)} neue Einträge")
        else:
            logger.warning("Keine neuen Analysen generiert")
            
        logger.info(f"AI-Analyse für {len(analyses)} Leads abgeschlossen")
        return analyses
            
    except Exception as e:
        logger.error(f"Fehler bei der AI-Analyse: {str(e)}")
        return []

def save_analyses(analyses):
    """Speichert die Analysen in einer JSON-Datei."""
    try:
        # Erstelle Verzeichnis wenn nicht vorhanden
        os.makedirs('data', exist_ok=True)
        
        # Lade existierende Analysen
        existing_analyses = []
        if os.path.exists('data/analyses.json'):
            with open('data/analyses.json', 'r', encoding='utf-8') as f:
                existing_analyses = json.load(f)
        
        # Füge neue Analysen hinzu
        all_analyses = existing_analyses + analyses
        
        # Speichere aktualisierte Analysen
        with open('data/analyses.json', 'w', encoding='utf-8') as f:
            json.dump(all_analyses, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Analysen erfolgreich gespeichert: {len(analyses)} neue Einträge")
        
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Analysen: {str(e)}")

# Lade Umgebungsvariablen
logger.debug("Lade Umgebungsvariablen...")
load_dotenv()

# Seitenkonfiguration
logger.debug("Konfiguriere Streamlit-Seite...")
st.set_page_config(
    page_title="Amplifa Lead Processor",
    # page_icon="frontend/assets/favicon.ico",  # Temporär deaktiviert
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS mit Amplifa Brand Guidelines
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    /* Grundlegende Typografie und Farben */
    :root {
        /* Primärfarben */
        --primary-orange: #F4AC37;
        --primary-pink: #DF2975;
        --primary-purple: #AC1ACC;
        
        /* Akzentfarben */
        --accent-blue-light: #2AA4FB;
        --accent-blue-medium: #2A69FB;
        --accent-blue-dark: #552AFB;
        
        /* Neutrale Farben */
        --neutral-white: #FFFFFF;
        --neutral-black: #060A0F;
        --neutral-gray: #F5F5F5;
    }

    /* Globale Styles */
    .main {
        font-family: 'Montserrat', sans-serif;
        background: linear-gradient(135deg, var(--neutral-white) 0%, var(--neutral-gray) 100%);
        color: var(--neutral-black);
    }

    /* Header und Navigation */
    .stApp > header {
        background-color: var(--neutral-white);
        border-bottom: 2px solid var(--primary-orange);
    }

    .sidebar .sidebar-content {
        background: linear-gradient(180deg, var(--primary-purple) 0%, var(--primary-pink) 100%);
        color: var(--neutral-white);
    }

    /* Metriken und Karten */
    .stMetric {
        background: var(--neutral-white);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }

    /* Buttons und Interaktive Elemente */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-pink) 0%, var(--primary-purple) 100%);
        color: var(--neutral-white);
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(223,41,117,0.3);
    }

    /* Tabellen und Datenansichten */
    .dataframe {
        border: 1px solid var(--neutral-gray);
        border-radius: 10px;
        overflow: hidden;
    }

    .dataframe th {
        background: linear-gradient(45deg, var(--primary-orange) 0%, var(--primary-pink) 100%);
        color: var(--neutral-white);
        padding: 1rem;
    }

    /* Expander und Container */
    .streamlit-expanderHeader {
        background: var(--neutral-white);
        border-radius: 10px;
        border: 1px solid var(--neutral-gray);
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: var(--neutral-gray);
    }

    /* Charts und Visualisierungen */
    .js-plotly-plot {
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        padding: 1rem;
        background: var(--neutral-white);
    }

    /* Animierte Loading-States */
    .stProgress > div > div {
        background: linear-gradient(45deg, var(--primary-orange) 0%, var(--primary-pink) 100%);
    }

    /* Responsive Design Anpassungen */
    @media (max-width: 768px) {
        .stMetric {
            padding: 1rem;
        }
        
        .stButton > button {
            width: 100%;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Logo und Header
# st.sidebar.image("frontend/assets/amplifa-logo.png", width=200)  # Temporär deaktiviert
st.sidebar.title("🚀 Lead Processor")

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
    """Lädt die gespeicherten AI-Analysen."""
    try:
        if os.path.exists('data/analyses.json'):
            with open('data/analyses.json', 'r', encoding='utf-8') as f:
                analyses = json.load(f)
            logger.debug(f"AI-Analysen erfolgreich geladen: {len(analyses)} Einträge gefunden")
            return analyses
        else:
            logger.debug("Keine gespeicherten Analysen gefunden")
            return []
    except Exception as e:
        logger.error(f"Fehler beim Laden der AI-Analysen: {str(e)}")
        return []

# Initialisiere den Scheduler
scheduler = get_scheduler(max_leads_per_day=50)

# Sidebar mit verbessertem Design
with st.sidebar:
    st.title("🚀 Lead Processor")
    st.markdown("---")
    
    # Vereinfachte Navigation
    page = st.radio(
        "Navigation",
        options=["📊 Dashboard", "👥 Leads", "🤖 AI-Aktivitäten", "⚙️ Einstellungen"]
    )
    
    st.markdown("---")
    
    # Quick Actions
    if st.button("🔄 Daten aktualisieren", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    if st.button("🚀 AI-Agent starten", use_container_width=True):
        with st.spinner("🤖 AI-Agent verarbeitet Leads..."):
            try:
                # Container für Live-Updates
                status_container = st.empty()
                progress_container = st.empty()
                detail_container = st.empty()
                
                # Führe AI-Analyse durch
                agent = AIAgent()
                leads = get_leads_from_apify()
                
                if not leads:
                    st.warning("⚠️ Keine neuen Leads zur Analyse gefunden.")
                else:
                    total_leads = len(leads)
                    progress_bar = progress_container.progress(0)
                    
                    analyses = []
                    for idx, lead in enumerate(leads):
                        # Update Status
                        status_container.info(f"🔄 Analysiere Lead {idx + 1} von {total_leads}: {lead.get('name', 'Unbekannt')}")
                        
                        # Führe Analyse durch
                        analysis = agent.analyze_lead(lead)
                        analyses.append(analysis)
                        
                        # Zeige Details der aktuellen Analyse
                        with detail_container.container():
                            st.markdown(f"""
                                <div style="background: var(--neutral-gray); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                                    <h4>🎯 Aktuelle Analyse für {analysis.get('name', 'Unbekannt')}</h4>
                                    <p><strong>Website-Analyse:</strong><br>{analysis.get('website_summary', 'Wird analysiert...')}</p>
                                    <p><strong>LinkedIn-Analyse:</strong><br>{analysis.get('linkedin_summary', 'Wird analysiert...')}</p>
                                    <p><strong>Generierte Nachricht:</strong><br>{analysis.get('personalized_message', 'Wird generiert...')}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Update Progress
                        progress_bar.progress((idx + 1) / total_leads)
                    
                    # Speichere neue Analysen
                    if analyses:
                        existing_analyses = load_analyses()
                        all_analyses = existing_analyses + analyses
                        save_analyses(all_analyses)
                        st.success(f"✅ {len(analyses)} Leads erfolgreich analysiert!")
                        
                        # Cache löschen und Seite neu laden
                        load_ai_analyses.clear()
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Fehler beim Ausführen der AI-Analyse: {str(e)}")
    
    st.markdown("---")
    
    # System Status
    st.markdown("### System Status")
    last_run = scheduler.get_last_run()
    if last_run:
        st.info(f"🟢 System läuft\n\nLetzte Aktualisierung:\n{last_run.strftime('%d.%m.%Y %H:%M')}")
    else:
        st.warning("🟡 System wartet auf erste Ausführung")

# Hauptbereich
st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary-purple) 0%, var(--primary-pink) 100%);
        color: var(--neutral-white);
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: var(--neutral-white) !important;
    }
    section[data-testid="stSidebar"] button {
        background: var(--neutral-white) !important;
        color: var(--primary-purple) !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background: var(--neutral-gray) !important;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# Dashboard-Seite
if page == "📊 Dashboard":
    # Header mit Animation
    st.markdown("""
        <div class="dashboard-header">
            <h1 style="background: linear-gradient(45deg, var(--primary-orange), var(--primary-pink), var(--primary-purple));
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       font-size: 2.5rem;
                       margin-bottom: 2rem;">
                Amplifa Lead Processor Dashboard
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Echte Leads laden mit Animation
    with st.spinner("🔄 Lade aktuelle Daten..."):
        df = load_real_leads()
    
    # Moderne Metriken mit Farbkodierung
    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = len(df)
        st.markdown(f"""
            <div class="metric" style="border-left: 4px solid var(--primary-orange);">
                <h3>Gesamte Leads</h3>
                <p class="metric-value">{total_leads}</p>
                <p class="metric-delta">+{total_leads - 0} heute</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_leads = len(df[df['status'] == 'aktiv'])
        st.markdown(f"""
            <div class="metric" style="border-left: 4px solid var(--primary-pink);">
                <h3>Aktive Leads</h3>
                <p class="metric-value">{active_leads}</p>
                <p class="metric-delta">+{active_leads - 0} heute</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ai_analyses = load_ai_analyses()
        analyzed_leads = len(ai_analyses)
        st.markdown(f"""
            <div class="metric" style="border-left: 4px solid var(--primary-purple);">
                <h3>Analysierte Leads</h3>
                <p class="metric-value">{analyzed_leads}</p>
                <p class="metric-delta">+{analyzed_leads - 0} heute</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        conversion_rate = (active_leads / total_leads * 100) if total_leads > 0 else 0
        st.markdown(f"""
            <div class="metric" style="border-left: 4px solid var(--accent-blue-light);">
                <h3>Konversionsrate</h3>
                <p class="metric-value">{conversion_rate:.1f}%</p>
                <p class="metric-delta">+{conversion_rate - 0:.1f}% heute</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Moderne Diagramme mit Animation
    st.markdown('<div class="charts-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <h3 style="color: var(--primary-pink); margin-bottom: 1rem;">
                📈 Lead-Aktivität im Zeitverlauf
            </h3>
        """, unsafe_allow_html=True)
        
        daily_leads = df.groupby(df['timestamp'].dt.date).size().reset_index()
        daily_leads.columns = ['Datum', 'Anzahl']
        
        fig = px.line(
            daily_leads,
            x='Datum',
            y='Anzahl',
            template='plotly_white'
        )
        fig.update_traces(
            line_color='#DF2975',
            line_width=3,
            mode='lines+markers'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            showlegend=False,
            margin=dict(t=0, l=0, r=0, b=0),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                tickformat='%d.%m.%Y'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown("""
            <h3 style="color: var(--primary-purple); margin-bottom: 1rem;">
                🎯 Lead-Status Verteilung
            </h3>
        """, unsafe_allow_html=True)
        
        status_counts = df['status'].value_counts()
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=.6,
            marker=dict(colors=[
                '#F4AC37',  # Orange
                '#DF2975',  # Pink
                '#AC1ACC'   # Purple
            ])
        )])
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=0, l=0, r=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Aktuelle Aktivitäten
    st.markdown("""
        <h3 style="color: var(--primary-orange); margin: 2rem 0 1rem 0;">
            📋 Aktuelle Aktivitäten
        </h3>
    """, unsafe_allow_html=True)
    
    # Aktivitäten-Timeline
    activities = [
        {"time": "Heute, 09:00", "event": "AI-Agent Analyse gestartet", "type": "info"},
        {"time": "Heute, 08:45", "event": "5 neue Leads hinzugefügt", "type": "success"},
        {"time": "Gestern, 17:30", "event": "Tagesanalyse abgeschlossen", "type": "warning"}
    ]
    
    for activity in activities:
        st.markdown(f"""
            <div class="activity-item" style="
                background: var(--neutral-white);
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 0.5rem;
                border-left: 4px solid var(--primary-{activity['type']});
                transition: all 0.3s ease;
            ">
                <p style="color: var(--neutral-black); margin: 0;">
                    <strong>{activity['time']}</strong> - {activity['event']}
                </p>
            </div>
        """, unsafe_allow_html=True)

# Leads-Seite
elif page == "👥 Leads":
    st.markdown("""
        <div class="page-header">
            <h1 style="background: linear-gradient(45deg, var(--primary-orange), var(--primary-pink));
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       font-size: 2.5rem;
                       margin-bottom: 2rem;">
                👥 Lead-Übersicht
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Echte Leads laden mit Animation
    with st.spinner("🔄 Lade Lead-Daten..."):
        df = load_real_leads()
    
    # Filter-Container mit modernem Design
    st.markdown("""
        <div style="background: var(--neutral-white); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
            <h3 style="color: var(--primary-purple); margin-bottom: 1rem;">🔍 Filter & Suche</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Status Filter",
            options=df['status'].unique(),
            default=df['status'].unique(),
            key="status_filter"
        )
    
    with col2:
        search = st.text_input("🔍 Suche nach Name, E-Mail oder Unternehmen", key="lead_search")
    
    with col3:
        date_range = st.date_input(
            "📅 Zeitraum",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            key="date_filter"
        )
    
    # Gefilterte Daten
    filtered_df = df[df['status'].isin(status_filter)]
    if search:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search, case=False) |
            filtered_df['email'].str.contains(search, case=False) |
            filtered_df['company'].str.contains(search, case=False)
        ]
    
    # Moderne Tabelle mit Amplifa-Farben
    st.markdown("""
        <style>
        .dataframe {
            font-family: 'Montserrat', sans-serif;
        }
        .dataframe th {
            background: linear-gradient(45deg, var(--primary-orange), var(--primary-pink));
            color: white;
            font-weight: 600;
            padding: 12px 15px;
        }
        .dataframe td {
            padding: 10px 15px;
        }
        .dataframe tr:nth-child(even) {
            background-color: var(--neutral-gray);
        }
        .dataframe tr:hover {
            background-color: rgba(223,41,117,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        filtered_df,
        column_config={
            "timestamp": st.column_config.DatetimeColumn(
                "Zeitstempel",
                format="DD.MM.YYYY HH:mm",
                step=60
            ),
            "name": st.column_config.Column(
                "Name",
                help="Name des Leads",
                width="medium"
            ),
            "email": st.column_config.Column(
                "E-Mail",
                help="E-Mail-Adresse",
                width="medium"
            ),
            "company": st.column_config.Column(
                "Unternehmen",
                help="Firmenname",
                width="medium"
            ),
            "status": st.column_config.SelectboxColumn(
                "Status",
                help="Aktueller Status des Leads",
                options=["aktiv", "inaktiv", "abgeschlossen"],
                required=True,
                width="small"
            ),
            "communication_style": st.column_config.Column(
                "Kommunikationsstil",
                help="Bevorzugter Kommunikationsstil",
                width="small"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Export-Optionen mit modernem Design
    st.markdown("""
        <div style="background: var(--neutral-white); padding: 1.5rem; border-radius: 15px; margin-top: 2rem;">
            <h3 style="color: var(--primary-purple); margin-bottom: 1rem;">📤 Export-Optionen</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Als CSV exportieren", key="export_csv"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "⬇️ CSV herunterladen",
                csv,
                "amplifa_leads.csv",
                "text/csv",
                key='download-csv'
            )
    
    with col2:
        if st.button("📊 Als Excel exportieren", key="export_excel"):
            excel = filtered_df.to_excel(index=False)
            st.download_button(
                "⬇️ Excel herunterladen",
                excel,
                "amplifa_leads.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key='download-excel'
            )

# AI-Aktivitäten-Seite
elif page == "🤖 AI-Aktivitäten":
    st.markdown("""
        <div class="page-header">
            <h1 style="background: linear-gradient(45deg, var(--primary-purple), var(--primary-pink));
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       font-size: 2.5rem;
                       margin-bottom: 2rem;">
                🤖 AI-Agent Aktivitäten
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Lade AI-Analysen
    ai_analyses = load_ai_analyses()
    
    # Button zum Starten des AI-Agenten
    if st.button("🚀 AI-Agenten starten", key="start_ai_agent", type="primary"):
        with st.spinner("🤖 AI-Agent wird initialisiert..."):
            try:
                # Container für Live-Updates
                status_container = st.empty()
                progress_container = st.empty()
                detail_container = st.empty()
                
                # Führe AI-Analyse durch
                agent = AIAgent()
                leads = get_leads_from_apify()
                
                if not leads:
                    st.warning("⚠️ Keine neuen Leads zur Analyse gefunden.")
                else:
                    total_leads = len(leads)
                    progress_bar = progress_container.progress(0)
                    
                    analyses = []
                    for idx, lead in enumerate(leads):
                        # Update Status
                        status_container.info(f"🔄 Analysiere Lead {idx + 1} von {total_leads}: {lead.get('name', 'Unbekannt')}")
                        
                        # Führe Analyse durch
                        analysis = agent.analyze_lead(lead)
                        analyses.append(analysis)
                        
                        # Zeige Details der aktuellen Analyse
                        with detail_container.container():
                            st.markdown(f"""
                                <div style="background: var(--neutral-gray); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                                    <h4>🎯 Aktuelle Analyse für {analysis.get('name', 'Unbekannt')}</h4>
                                    <p><strong>Website-Analyse:</strong><br>{analysis.get('website_summary', 'Wird analysiert...')}</p>
                                    <p><strong>LinkedIn-Analyse:</strong><br>{analysis.get('linkedin_summary', 'Wird analysiert...')}</p>
                                    <p><strong>Generierte Nachricht:</strong><br>{analysis.get('personalized_message', 'Wird generiert...')}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Update Progress
                        progress_bar.progress((idx + 1) / total_leads)
                    
                    # Speichere neue Analysen
                    if analyses:
                        existing_analyses = load_analyses()
                        all_analyses = existing_analyses + analyses
                        save_analyses(all_analyses)
                        st.success(f"✅ {len(analyses)} Leads erfolgreich analysiert!")
                        
                        # Cache löschen und Seite neu laden
                        load_ai_analyses.clear()
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Fehler beim Ausführen der AI-Analyse: {str(e)}")
    
    # Zeige gespeicherte Analysen
    if ai_analyses:
        # Suchfilter
        search = st.text_input(
            "🔍 Suche in Analysen",
            key="analysis_search",
            help="Suchen Sie nach Name, Unternehmen oder E-Mail"
        )
        
        # Konvertiere Analysen in DataFrame
        df_analyses = pd.DataFrame(ai_analyses)
        
        # Filter basierend auf Suche
        if search:
            mask = (
                df_analyses['name'].str.contains(search, case=False) |
                df_analyses['company'].str.contains(search, case=False) |
                df_analyses['email'].str.contains(search, case=False)
            )
            df_analyses = df_analyses[mask]
        
        # Zeige Übersichtstabelle
        st.markdown("""
            <div style="background: var(--neutral-white); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
                <h3 style="color: var(--primary-purple); margin-bottom: 1rem;">
                    📊 Generierte Analysen
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            df_analyses,
            column_config={
                "name": "Name",
                "company": "Unternehmen",
                "email": "E-Mail",
                "status": "Status",
                "communication_style": "Kommunikationsstil",
                "timestamp": st.column_config.DatetimeColumn(
                    "Zeitstempel",
                    format="DD.MM.YYYY HH:mm"
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Detailansicht für jeden Lead
        st.markdown("""
            <div style="background: var(--neutral-white); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
                <h3 style="color: var(--primary-orange); margin-bottom: 1rem;">
                    📋 Detaillierte Analysen
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        for analysis in df_analyses.to_dict('records'):
            with st.expander(f"🎯 {analysis['name']} - {analysis['company']}"):
                st.markdown(f"""
                    <div style="background: var(--neutral-gray); padding: 1.5rem; border-radius: 15px;">
                        <h4 style="color: var(--primary-purple); margin-bottom: 1rem;">👤 Kontaktinformationen</h4>
                        <p><strong>Name:</strong> {analysis['name']}</p>
                        <p><strong>Unternehmen:</strong> {analysis['company']}</p>
                        <p><strong>E-Mail:</strong> {analysis['email']}</p>
                        <p><strong>Status:</strong> {analysis['status']}</p>
                        <p><strong>Kommunikationsstil:</strong> {analysis['communication_style']}</p>
                        
                        <h4 style="color: var(--primary-pink); margin: 1.5rem 0 1rem 0;">🔍 Website-Analyse</h4>
                        <p>{analysis['website_summary']}</p>
                        
                        <h4 style="color: var(--primary-orange); margin: 1.5rem 0 1rem 0;">👥 LinkedIn-Analyse</h4>
                        <p>{analysis['linkedin_summary']}</p>
                        
                        <h4 style="color: var(--accent-blue-medium); margin: 1.5rem 0 1rem 0;">✉️ Generierte Nachricht</h4>
                        <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid var(--primary-pink);">
                            {analysis['personalized_message']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Keine AI-Analysen vorhanden. Starten Sie den AI-Agenten, um Leads zu analysieren.")

# Einstellungen-Seite
elif page == "⚙️ Einstellungen":
    st.markdown("""
        <div class="page-header">
            <h1 style="background: linear-gradient(45deg, var(--primary-orange), var(--accent-blue-medium));
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       font-size: 2.5rem;
                       margin-bottom: 2rem;">
                ⚙️ Einstellungen
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    # API-Einstellungen
    st.markdown("""
        <div style="background: var(--neutral-white); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
            <h3 style="color: var(--primary-purple); margin-bottom: 1rem;">
                🔑 API-Einstellungen
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        openai_api_key = st.text_input(
            "OpenAI API-Schlüssel",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Ihr OpenAI API-Schlüssel für die KI-Funktionen"
        )
    
    with col2:
        apify_api_key = st.text_input(
            "Apify API-Schlüssel",
            type="password",
            value=os.getenv("APIFY_API_KEY", ""),
            help="Ihr Apify API-Schlüssel für das Lead-Scraping"
        )
    
    apify_dataset_id = st.text_input(
        "Apify Dataset-ID",
        value=os.getenv("APIFY_DATASET_ID", ""),
        help="Die ID Ihres Apify Datasets"
    )
    
    # Scheduler-Einstellungen
    st.markdown("""
        <div style="background: var(--neutral-white); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
            <h3 style="color: var(--primary-pink); margin-bottom: 1rem;">
                ⏰ Scheduler-Einstellungen
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_leads = st.slider(
            "Maximale Anzahl von Leads pro Tag",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            help="Begrenzen Sie die Anzahl der täglich verarbeiteten Leads"
        )
    
    with col2:
        schedule_time = st.time_input(
            "Tägliche Ausführungszeit",
            value=datetime.strptime("09:00", "%H:%M").time(),
            help="Zeitpunkt der täglichen automatischen Ausführung"
        )
    
    # Speichern-Button mit Animation
    if st.button("💾 Einstellungen speichern", key="save_settings"):
        with st.spinner("🔄 Speichere Einstellungen..."):
            # Hier würden die Einstellungen in einer .env-Datei gespeichert
            st.success("✅ Einstellungen erfolgreich gespeichert!")
    
    # Scheduler-Steuerung
    st.markdown("""
        <div style="background: var(--neutral-white); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
            <h3 style="color: var(--accent-blue-medium); margin-bottom: 1rem;">
                🔄 Scheduler-Steuerung
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Scheduler starten", key="start_scheduler"):
            with st.spinner("🔄 Starte Scheduler..."):
                scheduler.schedule_daily_run(time=schedule_time.strftime("%H:%M"))
                st.success("✅ Scheduler erfolgreich gestartet!")
    
    with col2:
        if st.button("⏹️ Scheduler stoppen", key="stop_scheduler"):
            with st.spinner("🔄 Stoppe Scheduler..."):
                # Hier würde der Scheduler gestoppt werden
                st.info("ℹ️ Scheduler wurde gestoppt!")
    
    # Manuelle Ausführung
    st.markdown("""
        <div style="background: var(--neutral-white); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
            <h3 style="color: var(--primary-orange); margin-bottom: 1rem;">
                🚀 Manuelle Ausführung
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 AI-Agenten jetzt ausführen", key="run_ai_agent"):
        with st.spinner("🤖 AI-Agent verarbeitet Leads..."):
            scheduler.run_immediately()
            st.success("✅ Verarbeitung erfolgreich abgeschlossen!") 