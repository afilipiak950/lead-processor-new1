import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

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

# Beispieldaten
def get_sample_data():
    return pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=10),
        'name': ['Lead ' + str(i) for i in range(1, 11)],
        'email': [f'lead{i}@example.com' for i in range(1, 11)],
        'company': [f'Company {i}' for i in range(1, 11)],
        'status': ['aktiv', 'inaktiv', 'abgeschlossen'] * 4,
        'communication_style': ['formal', 'informal'] * 5
    })

# Sidebar mit verbessertem Design
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/rocket.png", width=100)
    st.title("🚀 Lead Processor")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Leads"],
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
    
    # Beispieldaten laden
    df = get_sample_data()
    
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
        st.metric(
            "Geplante E-Mails",
            0,
            delta="0",
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
    
    df = get_sample_data()
    
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