import streamlit as st

class Sidebar:
    def render(self, history: list[str]):
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] > div:first-child {
                    display: flex;
                    flex-direction: column;
                    height: 100vh !important;
                    overflow: hidden !important;

                }
                .sidebar-top {
                    flex: 1;
                    overflow-y: auto;
                    padding: 1rem 2rem;
                    border-bottom: 1px solid rgba(255,255,255,0.2);
                }
                .sidebar-footer {
                    padding: 1rem 0.75rem;
                    border-top: 0px solid rgba(255,255,255,0.2);
                }
                section[data-testid="stSidebar"] { background-color: #004C97 !important; }
                

             

            </style>
            """,
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            """
            <div class="sidebar-top">
                <div style="display:flex; justify-content: space-between; align-items:center;">
                    <h2 style="margin:0;color:white">Chat History</h2>
                    <span style="
                        background:white;
                        border-radius:50%;
                        width:24px;
                        height:24px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        cursor:pointer;
                    ">🗑️</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        # Render chat history
        for msg in history:
            st.sidebar.markdown(f"<div style='padding:0.25rem 0;'>{msg}</div>", unsafe_allow_html=True)

        # Insert 5 empty placeholder rows with thin separators
        for _ in range(5):
            st.sidebar.markdown(
                """
                <div style="height:80px; border-bottom:1px solid rgba(255,255,255,0.2); display:flex; align-items:center; padding-left:1rem;">
                    <svg width="24" height="40" viewBox="0 0 24 24" fill="none"
                         stroke="white" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 5H3V15H15L18 17L17 15H21V5Z"/>
                    </svg>
                </div>

                """,
                unsafe_allow_html=True,
            )
        for _ in range(3):
            st.sidebar.markdown(
                """
                <div style="height:50px;"></div>
                """,
                unsafe_allow_html=True,
            )

        # Close top section & render footer
        st.sidebar.markdown(
            """
            </div>
            <div class="sidebar-footer" style="display:flex; justify-content: space-between; align-items:center;">
                <span style="margin:0; color:white ;white-space: nowrap;">Export Chat History</span>
                <span style="
                    background:white;
                    border-radius:50%;
                    width:24px;
                    height:24px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    cursor:pointer;
                    color:black !important;
                    font-size:16px;
                ">➦</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
