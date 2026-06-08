import hashlib
import os
import requests
import time

def compute_md5_and_size(file_path):
    """Calculates the MD5 checksum and file size without loading the whole file into RAM."""
    print("Calculating MD5 and file size (this will take a few minutes for 15GB)...")
    md5 = hashlib.md5()
    size = 0
    with open(file_path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            size += len(chunk)
            md5.update(chunk)
    return md5.hexdigest(), size


def initiate_upload(article_id, file_path, md5, size):
    """Registers the file with the article and gets the upload URLs."""
    print("Initiating upload with Figshare API...")
    endpoint = f"{BASE_URL}/account/articles/{article_id}/files"
    data = {
        "name": os.path.basename(file_path),
        "md5": md5,
        "size": size
    }

    response = requests.post(endpoint, headers=HEADERS, json=data)
    response.raise_for_status()

    # The API returns a location URL to fetch the file info
    location = response.json()["location"]
    file_info_resp = requests.get(location, headers=HEADERS)
    file_info_resp.raise_for_status()

    return file_info_resp.json()


def upload_parts(file_info, file_path):
    """Fetches the required parts and uploads the specific byte ranges with retries."""
    upload_url = file_info["upload_url"]

    parts_resp = requests.get(upload_url, headers=HEADERS)
    parts_resp.raise_for_status()
    parts = parts_resp.json()["parts"]

    total_parts = len(parts)
    print(f"Divided into {total_parts} parts for upload.")

    # Configuration for retries
    MAX_RETRIES = 7

    with open(file_path, 'rb') as f:
        for part in parts:
            part_no = part["partNo"]
            start = part["startOffset"]
            end = part["endOffset"]

            f.seek(start)
            data = f.read(end - start + 1)
            part_url = f"{upload_url}/{part_no}"

            # --- THE NEW RETRY LOOP ---
            for attempt in range(MAX_RETRIES):
                try:
                    # We added a 60-second timeout so it doesn't hang forever
                    put_resp = requests.put(part_url, headers=HEADERS, data=data, timeout=60)
                    put_resp.raise_for_status()

                    # If we make it here, the chunk succeeded! Print and break the retry loop.
                    print(f"Uploaded part {part_no}/{total_parts} successfully.")
                    break

                except requests.exceptions.RequestException as e:
                    print(f"  [!] Network drop on part {part_no} (Attempt {attempt + 1} of {MAX_RETRIES}): {e}")

                    if attempt == MAX_RETRIES - 1:
                        print("  [!] Max retries reached. The upload has failed.")
                        raise  # Give up and crash if we failed 5 times in a row

                    # Wait a few seconds before trying again (2s, 4s, 8s...)
                    sleep_time = 2 ** attempt
                    print(f"  Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)

def create_new_article():
    endpoint = f"{BASE_URL}/account/articles"

    # You must provide at least a title to create a new article
    data = {
        "title": "FBperception-test1",
        "defined_type": "dataset"  # Optional: specifies the type of item
    }

    print("Creating new article...")
    response = requests.post(endpoint, headers=HEADERS, json=data)

    if response.status_code == 201:
        # The API returns 'entity_id', which is your new Article ID
        article_id = response.json().get("entity_id")
        print(f"Success! Your new Article ID is: {article_id}")
        return article_id
    else:
        print(f"Failed to create article: {response.status_code}")
        print(response.text)
        return None


# Run the function


def clean_slate():
    endpoint = f"{BASE_URL}/account/articles/{ARTICLE_ID}/files"

    print(f"Checking for stuck files in Article {ARTICLE_ID}...")
    response = requests.get(endpoint, headers=HEADERS)
    response.raise_for_status()

    files = response.json()

    if not files:
        print("No files found. The slate is already clean!")
        return

    for f in files:
        file_id = f["id"]
        file_name = f["name"]
        print(f"Found stuck file: {file_name}. Deleting...")

        delete_url = f"{endpoint}/{file_id}"
        del_resp = requests.delete(delete_url, headers=HEADERS)

        if del_resp.status_code == 204:
            print(f"Successfully deleted {file_name}.")
        else:
            print(f"Failed to delete {file_name}. Status: {del_resp.status_code}")



def complete_upload(article_id, file_id):
    """Tells Figshare to stitch the parts together and finalize the file."""
    print("Stitching parts and completing upload...")
    endpoint = f"{BASE_URL}/account/articles/{article_id}/files/{file_id}"
    response = requests.post(endpoint, headers=HEADERS)
    response.raise_for_status()
    print("Upload successfully completed!")


def main():
    if not os.path.exists(FILE_PATH):
        print(f"Error: File not found at {FILE_PATH}")
        return

    try:
        # Step 1: Analyze the file
        md5, size = compute_md5_and_size(FILE_PATH)

        # Step 2: Inform Figshare of the incoming file
        file_info = initiate_upload(ARTICLE_ID, FILE_PATH, md5, size)

        # Step 3: Stream the chunks
        upload_parts(file_info, FILE_PATH)

        # Step 4: Finalize
        complete_upload(ARTICLE_ID, file_info["id"])

    except requests.exceptions.RequestException as e:
        print(f"A network/API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    BASE_URL = "https://api.figshare.com/v2"

    CHUNK_SIZE = 10485760  # 10MB chunks to prevent memory overload

    FILE_PATH = "../Dataset.zip"
    TOKEN = "abc123"
    HEADERS = {"Authorization": f"token {TOKEN}"}
    ARTICLE_ID = create_new_article()  # IMPORTANT: Replace with your actual Figshare Article ID


    clean_slate()
    main()