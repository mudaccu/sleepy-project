SLEEP QUALITY PREDICTOR - how to run in VS Code
================================================

1. Install Python from python.org (tick "Add Python to PATH" during install).
2. In VS Code, install the "Python" extension (by Microsoft).
3. File > Open Folder > choose this SleepProject folder.
4. Open the terminal: Terminal > New Terminal. Then run these, one at a time:

   pip install -r requirements.txt      (installs pandas, scikit-learn, streamlit)
   python train.py                      (trains + saves the model)
   python test_app.py                   (checks predictions work)
   streamlit run app.py                 (opens the website in your browser)

To stop the website: click in the terminal and press Ctrl + C.
If "pip" or "python" is not found on Windows, try "py -m pip install -r requirements.txt" and "py train.py".
