import streamlit as st

class Sidebar:
    def render(self, history: list[str]):
        st.markdown(
            """
            <style>
                /* Sidebar background */
                section[data-testid="stSidebar"] {
                    background-color: #00008B !important;
                }
                /* Make all sidebar text white */
                section[data-testid="stSidebar"] *,
                section[data-testid="stSidebar"] label,
                section[data-testid="stSidebar"] h1,
                section[data-testid="stSidebar"] h2 {
                    color: white !important;
                }
                /* Style the Clear History button */
                section[data-testid="stSidebar"] button {
                    background-color: #005BB5 !important;
                    color: white !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.sidebar.title("Chat History")
        for msg in history:
            st.sidebar.write(msg)
        if st.sidebar.button('Clear History'):
            history.clear()
