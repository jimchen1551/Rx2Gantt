import os
import socket
import config
from pdf_processor import PDFProcessor
from data_cleaner import DataCleaner
from drug_classifier import DrugClassifier
from gantt_visualizer import GanttChartVisualizer

def is_connected(host="8.8.8.8", port=53, timeout=3):
    """
    Check for internet connectivity by attempting to connect to a host.
    Default host is a Google DNS server (8.8.8.8).
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.create_connection((host, port))
        return True
    except OSError:
        return False

def process_pdf(pdf_path, is_online, generate_gantt=True, generate_summary=True):
    """Process a single PDF file and display the saved directory."""
    try:
        print(f"Processing file: {pdf_path}")

        # Step 2: Extract raw data from the PDF
        pdf_processor = PDFProcessor(pdf_path)
        raw_data = pdf_processor.extract_data()
        print(f"  Raw data extracted: {len(raw_data)} rows.")

        # Step 3: Clean and preprocess the data
        data_cleaner = DataCleaner()
        cleaned_data = data_cleaner.clean_data(raw_data, config.PDF_COLUMNS)
        print(f"  Cleaned data prepared: {len(cleaned_data)} rows.")

        output_paths = []

        if generate_summary:
            if is_online:
                # Fetch drug classifications
                classifier = DrugClassifier()
                cleaned_data["MOA"] = cleaned_data["學名"].apply(
                    lambda name: classifier.fetch_rxclass_filtered(name)["MOA"]
                )
                cleaned_data["EPC"] = cleaned_data["學名"].apply(
                    lambda name: classifier.fetch_rxclass_filtered(name)["EPC"]
                )
                cleaned_data["PE"] = cleaned_data["學名"].apply(
                    lambda name: classifier.fetch_rxclass_filtered(name)["PE"]
                )
                cleaned_data["DDI"] = ""
                cleaned_data["SE"] = ""
                print("  Drug classifications fetched successfully.")
            else:
                # Skip classification in offline mode
                cleaned_data["MOA"] = ""
                cleaned_data["EPC"] = ""
                cleaned_data["PE"] = ""
                cleaned_data["DDI"] = ""
                cleaned_data["SE"] = ""
                print("  Offline mode: Skipping drug classification.")

            # Save the summary CSV
            output_csv_path, _ = config.get_output_paths(pdf_path)
            cleaned_data.to_csv(output_csv_path, index=False, columns=["學名", "EPC", "MOA", "PE", "DDI", "SE"])
            print(f"  Summary CSV saved to {output_csv_path}.")
            output_paths.append(output_csv_path)

        if generate_gantt:
            # Generate and save the Gantt chart
            _, output_gantt_path = config.get_output_paths(pdf_path)
            visualizer = GanttChartVisualizer(cleaned_data)
            visualizer.plot(output_gantt_path)
            print(f"  Gantt chart saved to {output_gantt_path}.")
            output_paths.append(output_gantt_path)

        return output_paths

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []

def main(generate_gantt=True, generate_summary=True):
    """
    Main function to process single or multiple PDFs and return saved file paths.
    """
    is_online = is_connected()
    print("Internet connection detected." if is_online else "Offline mode: Internet not detected.")

    saved_directories = []

    def process_files(file_list):
        for pdf_file in file_list:
            output_paths = process_pdf(pdf_file, is_online, generate_gantt, generate_summary)
            saved_directories.extend(output_paths)

    if config.MODE == "single":
        if not os.path.isfile(config.INPUT_PATH):
            print("Please select a valid PDF file.")
            return []
        print("Processing single file...")
        process_files([config.INPUT_PATH])

    elif config.MODE == "folder":
        if not os.path.isdir(config.INPUT_PATH):
            print("Please select a valid folder containing PDF files.")
            return []

        pdf_files = [os.path.join(config.INPUT_PATH, f) for f in os.listdir(config.INPUT_PATH) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print("No PDF files found in the specified folder.")
            return []

        print(f"Found {len(pdf_files)} PDF files to process.")
        process_files(pdf_files)

    print("\nProcessing complete.")
    return list(set(os.path.dirname(path) for path in saved_directories))

if __name__ == "__main__":
    main()
