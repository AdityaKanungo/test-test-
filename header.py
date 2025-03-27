import streamlit as st

class Header:
    def render(self):
        st.markdown(
            """
            <style>
                /* Hide Streamlit’s default top bar, menu & footer */
                [data-testid="stDecoration"], 
                header[data-testid="stHeader"], 
                #MainMenu, 
                footer {
                    display: none !important;
                }

                div[data-testid="column"] {
                    padding: 0 !important;
                    margin: 0 !important;
                    width: 100% !important;
                }

                /* Remove default padding on main container */
                [data-testid="block-container"]  {
                    padding-left: 0 !important;
                    padding-right: 0 !important;
                }
                [class^='st-emotion-cache-10oheav'] { 
                    padding-top: 0rem; 
                }

                /* Fixed header styling */
                [data-testid="stAppViewContainer"] .fixed-header {
                    position: sticky;
                    top: 0;
                    width: 100%;
                    background-color: #FAF9F6;
                    padding: 10px;
                    z-index: 999;
                    display: flex;
                    justify-content: center; /* centers header-title */
                    align-items: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    background: #fff;
                    font-family: 'Arial';
                    position: relative; /* for absolute positioning of email */
                }

                /* Ensure header icons have proper size */
                .header-icon {
                    width: 1.5rem;
                    margin-right: 0.5rem;
                }
                /* Enlarge left icon */
                .header-left .header-icon {
                    width: 2.5rem;
                    height: auto;
                    margin-right: 0.5rem;
                }

                /* Center title + icon together with underline */
                .header-title {
                    display: inline-flex;
                    align-items: center;
                    border-bottom: 0.2rem solid #004C97;
                    margin: 0 auto;
                }

                /* Position email to far right and set text color to grey */
                .header-email {
                    position: absolute;
                    right: 1rem;
                    color: grey !important;
                    font-family: Arial;
                }

                /* Remove padding from page content */
                .block-container {
                    padding-top: 0rem !important;
                    padding-left: 0rem !important;
                    padding-right: 0rem !important;
                }
            </style>

            <div class="fixed-header">
                <div class="header-left">
                    <img src="https://images.rawpixel.com/image_png_800/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIyLTA2L2pvYjk0Ny0wNjctcC5wbmc.png" alt="Left Icon" class="header-icon"/>
                </div>
                <div class="header-title">
                    <img src="https://images.rawpixel.com/image_png_800/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIyLTA2L2pvYjk0Ny0wNjctcC5wbmc.png" alt="Icon" class="header-icon"/>
                    <span><b>Policy Navigator</b></span>
                </div>
                <span class="header-email">example@epa.gov</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
