import streamlit as st

st.title('Batting')


st.markdown(f"👤 **Logged in as:** {st.experimental_user.name}")

st.write(st.experimental_user)
