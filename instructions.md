# How to Run `app.py` Step-by-Step

This guide explains how to run the `app.py` file for your project. Two methods are provided:
1. **Using Python directly within the directory**.
2. **Using a virtual environment for better dependency management**.

---

## **Method 1: Run Directly Within the Directory**
This method is simple and doesn't require setting up a virtual environment.

### Steps:
1. **Navigate to the project directory**:
   ```bash
   cd path/to/your/project
   ```

2. **Run the app.py using Python**:
   ```bash
   python app.py
   ```
   > Note: Ensure you're using a supported Python version (e.g., Python 3.10), as newer versions like Python 3.13 may cause compatibility issues with certain packages.

---

## **Method 2: Use a Virtual Environment (Recommended)**
A virtual environment isolates dependencies, ensuring no conflicts with system-wide packages.

### Steps:
1. **Navigate to the project directory**:
   ```bash
   cd path/to/your/project
   ```

2. **Create a virtual environment**:
   ```bash
   python3.10 -m venv venv310
   ```
   - This creates a virtual environment named `venv310` using Python 3.10.

3. **Activate the virtual environment**:
   - On **Windows**:
     ```bash
     venv310\Scripts\activate
     ```
   - On **Mac/Linux**:
     ```bash
     source venv310/bin/activate
     ```

4. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```
   - This installs all dependencies specified in the `requirements.txt` file.

5. **Run the app.py**:
   ```bash
   python app.py
   ```

6. **Deactivate the virtual environment (optional)**:
   ```bash
   deactivate
   ```

---

## Important Notes:
- **Python Version**: Ensure you're using Python 3.10 for compatibility with certain packages like `sentencepiece`.
- **Port and Debugging**: The app runs on `http://127.0.0.1:5000` by default. Check the logs for any errors.
- **Dependencies**: If `requirements.txt` is missing, manually install required packages (e.g., `torch`, `transformers`, `gTTS`, `Pillow`, etc.).

By following these steps, you can successfully run the application either directly or in a virtual environment.
