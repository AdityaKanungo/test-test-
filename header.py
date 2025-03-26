import streamlit as st

class Header:
    def render(self):
        # Inject CSS and render the full-width fixed header in one markdown block.
        st.markdown(
            """
            <style>
                /* Hide Streamlit’s default top bar, menu & footer */
                [data-testid="stDecoration"], header[data-testid="stHeader"], #MainMenu, footer {
                    display: none !important;
                }

                [data-testid="block-container"]  {
                padding-left: 0 !important;
                padding-right: 0 !important;
                }
                

                [class^='st-emotion-cache-10oheav'] { padding-top: 0rem; }
                /* Pin your header inside the main content area —
                   it will automatically align flush with the sidebar */
                [data-testid="stAppViewContainer"] .fixed-header {
                    position: sticky;
                    top: 0;
                    width: 100%;
                    background-color: #FAF9F6;
                    padding: 10px;
                    z-index: 999;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                [data-testid="stAppViewContainer"] .fixed-header h2,
                [data-testid="stAppViewContainer"] .fixed-header span {
                    color: black !important;
                }

                /* Push page content down so it’s not hidden under the header */
                .block-container {
                    padding-top: 0rem !important;
                }
            </style>

            <div class="fixed-header">
                <h2 style="color:white; margin:0;">Policy Navigator</h2>
                <span style="color:white;">example@epa.gov</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
