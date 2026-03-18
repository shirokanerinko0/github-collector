@echo off
echo Starting TRae Visualization Dashboard...
echo.
echo Please make sure you have installed the required packages:
echo   pip install streamlit pandas plotly
echo.
echo Opening browser at http://localhost:8501
echo.
streamlit run src/visualization/dashboard.py --server.port 8501
