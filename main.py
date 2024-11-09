import os
import config
from pdf_processor import PDFProcessor
from data_cleaner import DataCleaner
from drug_classifier import DrugClassifier
from gantt_visualizer import GanttChartVisualizer

def main():
    # Step 1: Get all PDF files in the input folder
    pdf_files = [f for f in os.listdir(config.INPUT_FOLDER) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in the specified folder.")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")

    # Process each PDF file
    for pdf_file in pdf_files:
        pdf_path = os.path.join(config.INPUT_FOLDER, pdf_file)
        print(f"\nProcessing file: {pdf_path}")

        try:
            # Step 2: Extract raw data from the PDF
            pdf_processor = PDFProcessor(pdf_path)
            raw_data = pdf_processor.extract_data()
            print(f"  Raw data extracted: {len(raw_data)} rows.")

            # Step 3: Clean and preprocess the data
            data_cleaner = DataCleaner()
            cleaned_data = data_cleaner.clean_data(raw_data, config.PDF_COLUMNS)
            print(f"  Cleaned data prepared: {len(cleaned_data)} rows.")

            # Step 4: Fetch drug classifications
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

            # Step 5: Save outputs in the same directory as the PDF file
            output_csv_path, output_gantt_path = config.get_output_paths(pdf_path)
            cleaned_data.to_csv(output_csv_path, index=False, columns=["學名", "EPC", "MOA", "PE", "DDI", "SE"])
            print(f"  Enriched data saved to {output_csv_path}.")

            # Step 6: Generate and save the Gantt chart
            visualizer = GanttChartVisualizer(cleaned_data)
            visualizer.plot(output_gantt_path)
            print(f"  Gantt chart saved to {output_gantt_path}.")

        except Exception as e:
            print(f"  Error processing {pdf_file}: {e}")

    print("\nBatch processing complete.")


if __name__ == "__main__":
    main()
