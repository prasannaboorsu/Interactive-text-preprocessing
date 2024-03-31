import streamlit as st
import pandas as pd
import re
import emoji
import chardet
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from textblob import TextBlob

# Remove "not" from stopwords
stp = stopwords.words("english")
stp.remove("not")

# Function to detect encoding
def detect_encoding(file):
    rawdata = file.read(50000)  # Read the first 50,000 bytes to guess the encoding
    file.seek(0)  # Reset file read position
    result = chardet.detect(rawdata)
    return result['encoding']

# Function to check text features
def check_text_features(data, column):
    # Initialize counters or flags
    any_upper = any_lower = html = url = tag = mention = unwanted_characters = emojis = 0
    
    if column in data.columns:
        # Check for case sensitivity
        any_upper = data[column].apply(lambda x: any(c.isupper() for c in x if isinstance(x, str))).any()
        any_lower = data[column].apply(lambda x: any(c.islower() for c in x if isinstance(x, str))).any()
        # Other checks
        html = data[column].apply(lambda x: bool(re.search("<.*?>", x)) if isinstance(x, str) else False).sum()
        url = data[column].apply(lambda x: bool(re.search(r"http[s]?://\S+", x)) if isinstance(x, str) else False).sum()
        tag = data[column].str.contains(r"#\S+", regex=True).sum()
        mention = data[column].str.contains(r"@\S+", regex=True).sum()
        unwanted_characters = data[column].str.contains(r"[\]\[\.\*'\-#$%^&)(0-9]", regex=True).sum()
        emojis = data[column].apply(lambda x: emoji.emoji_count(x) if isinstance(x, str) else 0 > 0).sum()

        # Display results
        if any_upper and any_lower:
            st.write("The text contains both uppercase and lowercase characters.")
        if html > 0:
            st.write("The text contains HTML tags.")
        if url > 0:
            st.write("The text contains URLs.")
        if tag > 0:
            st.write("The text contains hashtags.")
        if mention > 0:
            st.write("The text contains mentions.")
        if unwanted_characters > 0:
            st.write("The text contains unwanted characters.")
        if emojis > 0:
            st.write("The text contains emojis.")
    else:
        st.error(f"The specified column '{column}' does not exist in the uploaded file.")
        
def basic_preprocessing(x, emoj="F", spc="F"):
    x = x.lower() # converting to lower case
    x = re.sub("<.*?>"," ",x) # removing the HTML tags
    x = re.sub(r"http[s]?://.+?\S+"," ",x) # removing URLs
    x = re.sub(r"#\S+"," ",x) # removing hashtags
    x = re.sub(r"@\S+"," ",x) # removing mentions
    if emoj == "T": # converting emojis
        x = emoji.demojize(x)
    x = re.sub(r"[]\.:,\*'\-#$%^&)(0-9]"," ",x) # removing unwanted characters
    if spc == "T": 
        x = TextBlob(x).correct().string # spelling correction
    return x


st.title("Text Analysis Tool")
tabs = st.sidebar.radio("Choose your action:", ("Preprocessing", "Check Text Features"))

if tabs == "Preprocessing":
    st.sidebar.title("Preprocessing Options")
    # File uploader widget
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])
    encoding_option = st.sidebar.radio("Encoding option", ["Automatic", "Specify manually"])
    preprocess_checkbox = st.sidebar.checkbox("Enable Preprocessing")
    # Initialize encoding variable
    file_encoding = "utf-8"  # Default encoding

    if uploaded_file is not None:
        if encoding_option == "Automatic":
            try:
                file_encoding = detect_encoding(uploaded_file)
            except Exception as e:
                st.error(f"Error detecting encoding: {e}")
        else:  # User chooses to specify the encoding manually
            file_encoding = st.sidebar.text_input("Specify file encoding", value="utf-8")

        # Try to read the uploaded CSV file with detected or specified encoding
        try:
            data = pd.read_csv(uploaded_file, encoding=file_encoding)
            column_name = st.sidebar.text_input("Column Name", value="v2")

            if st.sidebar.button("Submit"):
                if column_name:
                    if preprocess_checkbox:  # If preprocessing is enabled
                        try:
                            data[column_name] = data[column_name].apply(basic_preprocessing)
                            st.write("Preprocessing complete.")
                            st.write("Processed Data:")
                            st.write(data)
                        except Exception as e:
                            st.error(f"Error in preprocessing: {e}")

        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.sidebar.write("Upload a CSV file to get started.")

elif tabs == "Check Text Features":
    st.sidebar.title("Check Text Features Options")
    # File uploader widget
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])
    encoding_option = st.sidebar.radio("Encoding option", ["Automatic", "Specify manually"])

    # Initialize encoding variable
    file_encoding = "utf-8"  # Default encoding

    if uploaded_file is not None:
        if encoding_option == "Automatic":
            try:
                file_encoding = detect_encoding(uploaded_file)
            except Exception as e:
                st.error(f"Error detecting encoding: {e}")
        else:  # User chooses to specify the encoding manually
            file_encoding = st.sidebar.text_input("Specify file encoding", value="utf-8")

        # Try to read the uploaded CSV file with detected or specified encoding
        try:
            data = pd.read_csv(uploaded_file, encoding=file_encoding)
            column_name = st.sidebar.text_input("Column Name", value="v2")

            if st.sidebar.button("Submit"):
                if column_name:
                    check_text_features(data, column_name)

        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.sidebar.write("Upload a CSV file to get started.")




