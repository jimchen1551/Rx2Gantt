import re
import pandas as pd

class DataCleaner:
    @staticmethod
    def clean_drug_name(raw_name):
        """Cleans the drug name by removing special characters and numbers."""
        match = re.match(r"^[A-Za-z\s\-\(\)\.]*", raw_name)
        return match.group(0).strip() if match else raw_name

    @staticmethod
    def concatenate_rows(df, columns):
        """Concatenates rows grouped in sets of 3."""
        concatenated_data = []
        for i in range(0, len(df), 3):
            concatenated_row = []
            for col in columns:
                concatenated_text = "".join(
                    df.iloc[i:i+3][col].dropna().astype(str).values
                )
                concatenated_row.append(concatenated_text)
            concatenated_data.append(concatenated_row)
        return pd.DataFrame(concatenated_data, columns=columns)

    @staticmethod
    def preprocess_dates(df, time_columns):
        """Converts date columns to datetime format."""
        for col in time_columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", format="%Y-%m-%d%H:%M")
        return df

    @staticmethod
    def drop_invalid_rows(df, required_columns):
        """Drops rows with invalid or missing required columns."""
        return df.dropna(subset=required_columns)

    def clean_data(self, raw_data, columns):
        """Cleans and processes the raw data."""
        # Concatenate rows in groups of 3
        df = self.concatenate_rows(raw_data, columns)

        # Clean the last column (e.g., remove unwanted characters)
        last_column = columns[-1]
        df[last_column] = df[last_column].str.replace(r"[A-Za-z]", "", regex=True).str.strip()

        # Preprocess date columns
        df = self.preprocess_dates(df, ["開立時間", "停止時間"])

        # Drop rows with invalid dates
        df = self.drop_invalid_rows(df, ["開立時間", "停止時間"])

        # Extract and clean drug names
        df["學名"] = df["學名<<商品名>>"].str.split("<<").str[0].apply(self.clean_drug_name)

        return df
