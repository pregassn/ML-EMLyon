@ECHO OFF
call C:/ProgramData/Anaconda3/Scripts/activate.bat
cd %~dp0
call conda activate fastai-cpu-v0.7
streamlit run BulldozerUI_mod.py --server.port 8011
call conda deactivate
pause