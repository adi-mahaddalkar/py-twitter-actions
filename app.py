import streamlit as st
import pandas as pd


def main():
    st.title("Twitter Insights")

    # File uploader
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], help='CSV file should contain the column "URL" which will have a list of valid Twitter URLs')

    if uploaded_file is not None:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)

        # Check if the 'URL' column exists
        if 'URL' in df.columns:
            # Extract the URLs from the 'URL' column
            url_list = df['URL'].tolist()

            # Display the extracted URLs
            st.write("Extracted URLs:")
            st.write(url_list)

        else:
            st.error("The CSV file does not contain a column named 'URL'. Please ensure the column exists.")


if __name__ == "__main__":
    main()
