import streamlit as st
from streamlit_app.components.sidebar import render_sidebar

st.set_page_config(page_title="Educational Outreach | NCPOR", page_icon="🎓", layout="wide")
render_sidebar()

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 style="color: #38BDF8; margin: 0;">🎓 Polar Science Educational Outreach & Youth Hub</h2>
    <p style="color: #94A3B8; margin: 0.3rem 0;">Inspiring the next generation of Indian polar scientists and climate researchers</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🧒 School Student Guide", "🧠 Interactive Polar Quiz", "📖 Polar Glossary", "🌟 Fascinating Polar Facts"])

with tabs[0]:
    st.subheader("❄️ Why Does India Go All the Way to the Poles?")
    st.markdown("""
    Imagine Earth as a living body. The equator is the warm heart, while Antarctica and the Arctic are the **giant refrigerators** that keep the planetary system cool!
    
    * **How Antarctica Affects the Indian Monsoon**:
      When the icy winds blow off the Antarctic continent, they push ocean currents all the way up through the Indian Ocean. If Antarctic ice sheets melt, our monsoons and rainfall patterns in India change!
    * **The Secret Under the Ice**:
      Antarctica has ice that has been frozen for over **800,000 years**. By drilling deep ice cylinders called *ice cores*, Indian scientists can see what Earth's atmosphere was like thousands of years ago!
    """)
    
    st.subheader("🏠 India's Polar Bases at a Glance")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **Maitri (Antarctica)**
        - Built on rocky oasis bedrock in 1989
        - Sits next to fresh Lake Priyadarshini
        - Studies blizzards, auroras & geomagnetism
        """)
    with col2:
        st.markdown("""
        **Bharati (Antarctica)**
        - Ultra-modern green station built in 2012
        - Made from 134 modular containers on stilts
        - Direct satellite link with ISRO!
        """)
    with col3:
        st.markdown("""
        **Himadri & IndARC (Arctic)**
        - Located in Svalbard near the North Pole
        - IndARC is anchored 192m underwater in a fjord!
        - Listens to whale songs & ocean currents
        """)

with tabs[1]:
    st.subheader("🧠 Test Your Polar Knowledge!")
    st.write("Answer the 3 questions below to earn your **Junior Polar Explorer Badge**:")
    
    q1 = st.radio(
        "1. Where does Maitri station get its fresh drinking water in Antarctica?",
        ["From melted sea ice", "From Lake Priyadarshini", "Shipped from Goa in bottles", "From melted glaciers only"]
    )
    q2 = st.radio(
        "2. What is IndARC in the Arctic?",
        ["An icebreaking ship", "A high-altitude radar plane", "An underwater moored observatory in a fjord", "A satellite tracking dish"]
    )
    q3 = st.radio(
        "3. In what year was Bharati Station commissioned?",
        ["1983", "1989", "2012", "2020"]
    )
    
    if st.button("Submit Quiz Answers"):
        score = 0
        if q1 == "From Lake Priyadarshini":
            score += 1
        if q2 == "An underwater moored observatory in a fjord":
            score += 1
        if q3 == "2012":
            score += 1
            
        if score == 3:
            st.balloons()
            st.success(f"🎉 Perfect Score! 3/3! You have officially earned the NCPOR Junior Polar Explorer Badge!")
        elif score == 2:
            st.info(f"Great effort! You scored 2/3. Check the guide above to find the one you missed!")
        else:
            st.warning(f"You scored {score}/3. Explore the guide above and try again!")

with tabs[2]:
    st.subheader("📖 Polar Science Glossary")
    glossary = {
        "Katabatic Wind": "Extremely high-density, gravity-driven cold winds that plunge down steep Antarctic ice slopes at blizzard speeds (>150 km/h).",
        "Ice Core": "A cylindrical sample extracted from an ice sheet containing ancient air bubbles that record past atmospheric greenhouse gases.",
        "Schirmacher Oasis": "A 35-square-kilometer ice-free rocky plateau in East Antarctica where India's Maitri station is situated.",
        "Aurora Australis": "Spectacular southern lights caused by solar energetic particles colliding with oxygen and nitrogen atoms in the upper polar atmosphere.",
        "IndARC": "India's first multi-sensor moored underwater observatory deployed in Kongsfjorden, Svalbard, Arctic Ocean at 192m depth.",
        "Larsemann Hills": "An Antarctic coastal ice-free region in Prydz Bay hosting India's eco-friendly Bharati research station."
    }
    for term, definition in glossary.items():
        st.markdown(f"**{term}**: {definition}")

with tabs[3]:
    st.subheader("🌟 Did You Know?")
    st.markdown("""
    * 🐧 **No Penguins in the Arctic**: Penguins only live in the Southern Hemisphere (Antarctica)! In the Arctic, you find polar bears and puffins.
    * 🏜️ **Antarctica is the World's Largest Desert**: Because it receives so little rainfall or snowfall (less than 50 mm/year inland), it is technically a polar desert!
    * 🌑 **6 Months of Darkness**: During the polar winter, the sun sinks below the horizon in May and doesn't rise until August!
    """)
