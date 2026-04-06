# -*- coding: utf-8 -*-
import sys
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "st.subheader(\"📍 Detect Your Real Location\")" in line:
        start_idx = i
        break

for i in range(start_idx, len(lines)):
    if "elif \"real_doctors_result\" in st.session_state:" in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_ui = """    st.subheader("📍 Real-Time Location Tracking")
    st.caption("Click the button below to enable live location tracking.")
    location = streamlit_geolocation()

    gps_lat = location.get("latitude") if location else None
    gps_lon = location.get("longitude") if location else None

    if not gps_lat or not gps_lon:
        st.warning("⚠️ Waiting for location... Please allow location access to track nearby doctors.")
    else:
        st.success(f"✅ Live Location Active: {gps_lat:.5f}, {gps_lon:.5f}")
        
        filter_col, map_col = st.columns([1, 2.5])
        
        with filter_col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🔍 Filters")
            max_distance_km = st.slider("Radius (km)", min_value=1, max_value=20, value=5, step=1)
            facility_filter = st.selectbox("Facility Type", ["All", "Hospital", "Clinic", "Doctors", "Dentist", "Cardiologist", "Pharmacy", "Health Centre"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.spinner("Finding nearby doctors..."):
                raw_doctors = fetch_real_doctors(gps_lat, gps_lon, radius_m=max_distance_km * 1000)
            
            real_doctors = []
            if raw_doctors:
                if facility_filter != "All":
                    for d in raw_doctors:
                        kw = facility_filter.lower()
                        if kw in ["dentist", "cardiologist"]:
                            if kw in d["type"].lower() or kw in d["name"].lower():
                                real_doctors.append(d)
                        elif kw in d["type"].lower():
                            real_doctors.append(d)
                else:
                    real_doctors = raw_doctors
                    
            real_doctors = sorted(real_doctors, key=lambda x: x["distance_km"])
            st.markdown(f"**Found {len(real_doctors)} nearby {facility_filter.lower() if facility_filter!='All' else 'results'}**")
            
        with map_col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            m = folium.Map(location=[gps_lat, gps_lon], zoom_start=14, tiles="CartoDB positron", control_scale=True)

            folium.Marker(
                location=[gps_lat, gps_lon],
                popup="📌 Your Live Location",
                icon=folium.Icon(color="red", icon="user", prefix='fa'),
                tooltip="You are here"
            ).add_to(m)
            
            folium.Circle(
                location=[gps_lat, gps_lon],
                radius=max_distance_km * 1000,
                color="#1976d2",
                fill=True,
                fill_opacity=0.08,
            ).add_to(m)

            type_colors = {
                "hospital": "darkred", "clinic": "cadetblue", "doctors": "blue",
                "pharmacy": "orange", "health centre": "purple"
            }
            for doc in real_doctors:
                color = type_colors.get(doc["type"].lower(), "darkblue")
                popup_html = f\"\"\"
                <div style="font-family:sans-serif;">
                <b>{doc['name']}</b><br>
                🏥 {doc['type']}<br>
                📞 {doc['phone']}<br>
                📍 {doc['address']}<br>
                🕐 {doc['opening_hours']}<br>
                <b style="color:#d32f2f;">📏 {doc['distance_km']} km away</b>
                </div>
                \"\"\"
                folium.Marker(
                    location=[doc["lat"], doc["lon"]],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=color, icon="medkit", prefix='fa'),
                    tooltip=f"{doc['name']} ({doc['distance_km']} km)"
                ).add_to(m)

            st_folium(m, width="100%", height=500, key="uber_map")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.divider()
        if real_doctors:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("👨‍⚕️ Available Providers (Ranked By Distance)")

            nearest = real_doctors[0]
            st.success(f"🏆 **NEAREST:** {nearest['name']} ({nearest['type']}) — **{nearest['distance_km']} km away** | 📞 {nearest['phone']}")

            display_df = pd.DataFrame(real_doctors)[["name", "type", "distance_km", "phone", "address", "opening_hours"]]
            display_df.columns = ["Name", "Type", "Distance (km)", "Phone", "Address", "Opening Hours"]
            st.dataframe(display_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("💡 Recommend by Diagnosis")
        selected_diagnosis = st.selectbox("Select your diagnosis", list(medicine_mapping.keys()), key="diag_recommend")
        recommended_specialties = SpecialtyMatcher.get_matching_specialties(selected_diagnosis)
        st.info(f"Recommended specialties for **{selected_diagnosis}**: {', '.join(recommended_specialties)}")
        st.markdown('</div>', unsafe_allow_html=True)

"""
    
    lines[start_idx:end_idx] = [new_ui]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Done rewriting UI block")
else:
    print(f"Could not find markers: {start_idx}, {end_idx}")
