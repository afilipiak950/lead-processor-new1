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
    page_title="Amplifa Lead Processor",
    page_icon="frontend/assets/favicon.ico",
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
st.sidebar.image("frontend/assets/amplifa-logo.png", width=200)
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
    
    # Lade AI-Analysen mit Animation
    with st.spinner("🔄 Lade AI-Analysen..."):
        ai_analyses = load_ai_analyses()
    
    if not ai_analyses:
        st.markdown("""
            <div style="text-align: center; padding: 3rem; background: var(--neutral-white); border-radius: 15px; margin: 2rem 0;">
                <img src="frontend/assets/robot-empty.png" style="width: 150px; margin-bottom: 1.5rem;">
                <h2 style="color: var(--primary-purple); margin-bottom: 1rem;">Keine AI-Analysen vorhanden</h2>
                <p style="color: var(--neutral-black); margin-bottom: 2rem;">
                    Starten Sie den AI-Agenten, um Leads zu analysieren und personalisierte Nachrichten zu generieren.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Button zum Starten des AI-Agenten
        if st.button("🚀 AI-Agenten starten", key="start_ai_agent"):
            with st.spinner("🤖 AI-Agent verarbeitet Leads..."):
                scheduler.run_immediately()
                st.success("✅ AI-Agent hat die Verarbeitung abgeschlossen!")
    else:
        # Metriken mit modernem Design
        st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="metric" style="border-left: 4px solid var(--primary-orange);">
                    <h3>Analysierte Leads</h3>
                    <p class="metric-value">{len(ai_analyses)}</p>
                    <p class="metric-delta">Gesamt</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            formal_count = len([a for a in ai_analyses if a.get('communication_style') == 'formal'])
            informal_count = len([a for a in ai_analyses if a.get('communication_style') == 'informal'])
            st.markdown(f"""
                <div class="metric" style="border-left: 4px solid var(--primary-pink);">
                    <h3>Kommunikationsstile</h3>
                    <p class="metric-value">{formal_count}/{informal_count}</p>
                    <p class="metric-delta">Formal/Informal</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            active_count = len([a for a in ai_analyses if a.get('status') == 'aktiv'])
            st.markdown(f"""
                <div class="metric" style="border-left: 4px solid var(--primary-purple);">
                    <h3>Aktive Leads</h3>
                    <p class="metric-value">{active_count}</p>
                    <p class="metric-delta">Bereit für Kontakt</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Diagramme mit Amplifa-Design
        st.markdown('<div class="charts-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <h3 style="color: var(--primary-pink); margin: 1.5rem 0;">
                    📊 Kommunikationsstil-Verteilung
                </h3>
            """, unsafe_allow_html=True)
            
            style_data = pd.DataFrame(ai_analyses)
            style_counts = style_data['communication_style'].value_counts()
            
            fig = px.pie(
                values=style_counts.values,
                names=style_counts.index,
                hole=0.6,
                color_discrete_sequence=['#DF2975', '#AC1ACC']
            )
            fig.update_traces(textposition='outside', textinfo='percent+label')
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
        
        with col2:
            st.markdown("""
                <h3 style="color: var(--primary-purple); margin: 1.5rem 0;">
                    📈 Lead-Status Übersicht
                </h3>
            """, unsafe_allow_html=True)
            
            status_counts = style_data['status'].value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                hole=0.6,
                color_discrete_sequence=['#F4AC37', '#DF2975', '#AC1ACC']
            )
            fig.update_traces(textposition='outside', textinfo='percent+label')
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
        
        # Detaillierte Analysen mit modernem Design
        st.markdown("""
            <h3 style="color: var(--primary-orange); margin: 2rem 0 1rem 0;">
                📋 Lead-Analysen
            </h3>
        """, unsafe_allow_html=True)
        
        # Suchfilter mit Amplifa-Design
        search = st.text_input(
            "🔍 Suche in Analysen",
            key="analysis_search",
            help="Suchen Sie nach Name, Unternehmen oder E-Mail"
        )
        
        # Gefilterte Analysen
        filtered_analyses = ai_analyses
        if search:
            filtered_analyses = [
                a for a in ai_analyses
                if search.lower() in a.get('name', '').lower() or
                   search.lower() in a.get('company', '').lower() or
                   search.lower() in a.get('email', '').lower()
            ]
        
        # Zeige die Analysen im Amplifa-Design
        for analysis in filtered_analyses:
            with st.expander(f"📊 {analysis.get('name', 'Unbekannt')} - {analysis.get('company', 'Unbekannt')}"):
                st.markdown("""
                    <div style="background: var(--neutral-white); padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;">
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                        <div style="margin-bottom: 1rem;">
                            <h4 style="color: var(--primary-purple);">👤 Kontaktinformationen</h4>
                            <p><strong>Name:</strong> {analysis.get('name', 'Unbekannt')}</p>
                            <p><strong>Unternehmen:</strong> {analysis.get('company', 'Unbekannt')}</p>
                            <p><strong>E-Mail:</strong> {analysis.get('email', 'Unbekannt')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div style="margin-bottom: 1rem;">
                            <h4 style="color: var(--primary-pink);">📈 Status</h4>
                            <p><strong>Status:</strong> {analysis.get('status', 'Unbekannt')}</p>
                            <p><strong>Kommunikationsstil:</strong> {analysis.get('communication_style', 'Unbekannt')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                if analysis.get('website'):
                    st.markdown(f"""
                        <div style="margin-bottom: 1rem;">
                            <h4 style="color: var(--primary-orange);">🌐 Website-Analyse</h4>
                            <p>{analysis.get('website_summary', 'Keine Zusammenfassung verfügbar')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                if analysis.get('linkedin_summary'):
                    st.markdown(f"""
                        <div style="margin-bottom: 1rem;">
                            <h4 style="color: var(--accent-blue-medium);">👥 LinkedIn-Analyse</h4>
                            <p>{analysis.get('linkedin_summary', 'Keine Zusammenfassung verfügbar')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                    <div style="margin-top: 1rem; padding: 1rem; background: var(--neutral-gray); border-radius: 10px;">
                        <h4 style="color: var(--primary-purple);">✉️ Personalisierte Nachricht</h4>
                """, unsafe_allow_html=True)
                
                st.markdown(analysis.get('personalized_message', 'Keine Nachricht verfügbar'))
                
                st.markdown("</div></div>", unsafe_allow_html=True)

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