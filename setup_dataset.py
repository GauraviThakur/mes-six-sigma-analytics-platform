import wget
import os
import pandas as pd

def download_and_clean_dataset():
    print("[SETUP] Fetching UCI AI4I 2020 Predictive Maintenance Dataset...")
    
    # URL to the raw dataset asset hosted publicly for seamless download
    url = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
    
    # Download the file
    zip_name = "dataset.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    wget.download(url, zip_name)
    print("\n[SETUP] Download complete. Unzipping and preparing CSV file...")
    
    # Unzip file safely
    import zipfile
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(".")
        
    # The UCI dataset comes out named 'ai4i2020.csv'. Let's rename it to what our code looks for
    if os.path.exists("ai4i2020.csv"):
        # Read it to verify, and save it cleanly
        df = pd.read_csv("ai4i2020.csv")
        df.to_csv("predictive_maintenance.csv", index=False)
        print("[SETUP] Success! 'predictive_maintenance.csv' is ready in your project directory.")
        
        # Clean up zip files
        os.remove(zip_name)
        os.remove("ai4i2020.csv")
    else:
        print("[ERROR] Could not find the unzipped data file.")

if __name__ == "__main__":
    download_and_clean_dataset()