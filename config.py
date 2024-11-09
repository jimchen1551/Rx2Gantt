import os

def ensure_folder_exists(folder_path):
    """Ensures that the specified folder exists, creating it if necessary."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Output paths will be dynamically generated based on the selected file or folder
def get_output_paths(pdf_path):
    """Generates output file paths based on the input PDF file's path."""
    input_dir = os.path.dirname(os.path.abspath(pdf_path))
    summary_dir = os.path.join(input_dir, "summary")
    gantt_dir = os.path.join(input_dir, "gantt")

    # Ensure the summary and gantt directories exist
    ensure_folder_exists(summary_dir)
    ensure_folder_exists(gantt_dir)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]  # Get the file name without extension
    output_csv_path = os.path.join(summary_dir, f"{base_name}_summary.csv")
    output_gantt_path = os.path.join(gantt_dir, f"{base_name}_gantt.png")
    return output_csv_path, output_gantt_path

# Settings for UI mode (single file or folder)
MODE = "single"  # Default mode; can be "single" or "folder"
INPUT_PATH = ""  # To be dynamically set by the GUI
PDF_COLUMNS = ["開立時間", "學名<<商品名>>", "劑量", "途徑", "頻次", "停止時間", "總量"]
COLUMN_BOUNDARIES = [
    (24, 54), (62, 255), (269, 316), (324, 343), (347, 393), (393, 424), (434, 444)
]
RXNAV_BASE_URL = "https://rxnav.nlm.nih.gov/REST"
LOGGING_LEVEL = "INFO"
CHART_COLOR_SCHEME = "Pastel1"
