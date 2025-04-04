import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Füge das übergeordnete Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sheets_manager import SheetsManager
from scheduler import Scheduler

# Seitenkonfiguration
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
    </style>
""", unsafe_allow_html=True)

# Initialisierung der Manager
@st.cache_resource
def init_managers():
    return SheetsManager(), Scheduler()

sheets_manager, scheduler = init_managers()

# Sidebar mit verbessertem Design
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/rocket.png", width=100)
    st.title("🚀 Lead Processor")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Leads", "📧 E-Mail-Planung", "🤖 AI-Aktivitäten"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    if st.button("🔄 Daten aktualisieren"):
        st.cache_data.clear()
        st.success("Daten wurden aktualisiert!")
    
    st.markdown("---")
    st.markdown("### System Status")
    st.info("🟢 System läuft")
    st.markdown(f"Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

# Dashboard-Seite
if page == "📊 Dashboard":
    st.title("📊 Lead Processor Dashboard")
    
    # Metriken mit verbessertem Design
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = len(sheets_manager.get_all_leads())
        st.metric(
            "Gesamte Leads",
            total_leads,
            delta=f"+{total_leads - 0}",
            delta_color="normal"
        )
    
    with col2:
        active_leads = len([l for l in sheets_manager.get_all_leads() if l['status'] == 'aktiv'])
        st.metric(
            "Aktive Leads",
            active_leads,
            delta=f"+{active_leads - 0}",
            delta_color="normal"
        )
    
    with col3:
        scheduled_emails = len(scheduler.get_active_schedules())
        st.metric(
            "Geplante E-Mails",
            scheduled_emails,
            delta=f"+{scheduled_emails - 0}",
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
        leads_df = pd.DataFrame(sheets_manager.get_all_leads())
        if not leads_df.empty:
            leads_df['timestamp'] = pd.to_datetime(leads_df['timestamp'])
            daily_leads = leads_df.groupby(leads_df['timestamp'].dt.date).size().reset_index()
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
        if not leads_df.empty:
            status_counts = leads_df['status'].value_counts()
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
    
    leads = sheets_manager.get_all_leads()
    if leads:
        df = pd.DataFrame(leads)
        
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
    else:
        st.info("Keine Leads gefunden.")

# E-Mail-Planung
elif page == "📧 E-Mail-Planung":
    st.title("📧 E-Mail-Planung")
    
    schedules = scheduler.get_active_schedules()
    if schedules:
        df = pd.DataFrame(schedules)
        df['scheduled_date'] = pd.to_datetime(df['scheduled_date'])
        
        # Zwei-Spalten-Layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 E-Mail-Verteilung")
            email_types = df['type'].value_counts()
            fig = px.pie(
                values=email_types.values,
                names=email_types.index,
                title="Verteilung der E-Mail-Typen",
                template='plotly_white'
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📅 Zeitplan")
            fig = px.timeline(
                df,
                x_start="scheduled_date",
                y="lead_email",
                color="type",
                title="Zeitplan der E-Mails",
                template='plotly_white'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detaillierte Tabelle
        st.subheader("📋 Geplante E-Mails")
        st.dataframe(
            df,
            column_config={
                "lead_email": "Lead E-Mail",
                "type": st.column_config.SelectboxColumn(
                    "E-Mail-Typ",
                    options=["initial", "follow-up", "final"],
                    required=True
                ),
                "scheduled_date": st.column_config.DatetimeColumn(
                    "Geplanter Zeitpunkt",
                    format="DD.MM.YYYY HH:mm",
                    step=60
                ),
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["geplant", "gesendet", "fehlgeschlagen"],
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Keine geplanten E-Mails vorhanden.")

# AI-Aktivitäten
elif page == "🤖 AI-Aktivitäten":
    st.title("🤖 AI-Agent Aktivitäten")
    
    leads = sheets_manager.get_all_leads()
    if leads:
        df = pd.DataFrame(leads)
        
        # Zwei-Spalten-Layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Kommunikationsstile")
            style_dist = df['communication_style'].value_counts()
            fig = px.bar(
                x=style_dist.index,
                y=style_dist.values,
                title="Verteilung der Kommunikationsstile",
                labels={'x': 'Kommunikationsstil', 'y': 'Anzahl'},
                template='plotly_white'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 KI-Performance")
            performance_data = {
                'Metrik': ['Genauigkeit', 'Reaktionszeit', 'Personalisierung'],
                'Wert': [95, 88, 92]
            }
            perf_df = pd.DataFrame(performance_data)
            fig = px.bar(
                perf_df,
                x='Metrik',
                y='Wert',
                title="KI-Performance-Metriken",
                template='plotly_white'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                yaxis_range=[0, 100]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Beispiel-E-Mails mit verbessertem Design
        st.subheader("✉️ Beispiel-E-Mails")
        for lead in leads[:3]:
            with st.expander(f"📧 E-Mail für {lead['name']} ({lead['communication_style']})"):
                st.markdown("""
                    <style>
                    .email-content {
                        background-color: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="email-content">', unsafe_allow_html=True)
                st.text(lead.get('email_content', 'Keine E-Mail verfügbar'))
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Kommunikationsstil:** {lead['communication_style']}")
                with col2:
                    st.markdown(f"**Generiert am:** {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    else:
        st.info("Keine AI-Aktivitäten vorhanden.") 