# -----------------------------------------------------------------------
# Section 1: Imports
# -----------------------------------------------------------------------
import os
import sys
import json
import time
import logging
import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -----------------------------------------------------------------------
# Section 2: Configuration & Security
# -----------------------------------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Define paths (relative paths are best for servers) ---
CORPUS_PATH = 'corpus'
CLEANED_PATH = 'cleaned_corpus'
STATE_FILE = 'processing_state.json'
LOG_FILE = 'processing.log'

# --- Model and Performance Settings ---
MODEL_NAME = 'gemini-2.0-flash'

# CRITICAL: A small chunk size is essential for low-RAM (1GB) instances
# to prevent the script from crashing.
CHUNK_SIZE = 15000


# -----------------------------------------------------------------------
# Section 3: Logging Setup
# -----------------------------------------------------------------------
# This sets up logging to both a file and the console.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)


# -----------------------------------------------------------------------
# Section 4: Helper and Core Functions
# -----------------------------------------------------------------------

# --- State Management Functions ---
def load_state():
    """Loads the processing state from a JSON file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.warning(f"State file {STATE_FILE} is corrupted. Starting fresh.")
            return {"processed_files": [], "partially_processed": {}}
    return {"processed_files": [], "partially_processed": {}}

def save_state(state):
    """Saves the processing state to a JSON file."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

# --- File Processing Function ---
def read_in_chunks(file_path, chunk_size=CHUNK_SIZE, start_byte=0):
    """Generator to read a file in chunks, starting from a specific byte."""
    with open(file_path, 'r', encoding='utf-8') as f:
        f.seek(start_byte)
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk, f.tell()

# --- Gemini API Interaction Functions ---
def get_gemini_prompt(text_chunk):
    """Formats the specialized prompt for the API call."""
    return f"""
### ARABIC CORPUS REFINEMENT ###

**Persona:**
You are a computational linguist and Arabic language expert. Your goal is to meticulously clean and normalize a given text chunk. The ultimate purpose is to prepare this text for pre-training a high-quality Large Language Model (LLM) for Arabic.

**Primary Directive:**
Process the following text by strictly adhering to the rules below. The output MUST ONLY be the refined text. Do not add any commentary, explanations, or apologies. Preserve the core meaning and unique flavor of the Arabic dialect at all times.

**Cleaning & Normalization Rules:**
1.  **Orthographic Normalization:**
    - Standardize all instances of "ى" (alif maqsura) to "ي" (ya), unless it is grammatically required as the final letter of a verb or specific noun.
    - Remove tashkeel and tatweel (diacritics) from the text.
    - Unify representations of laughter (e.g., "ههههه", "خهخهخ") to a standard "ههه".
    - Remove excessive or repeated punctuation (e.g., "!!!!", "؟؟؟") and replace with a single, appropriate punctuation mark.
    - Eliminate any non-essential characters, timestamps, HTML tags, emojis, text art, or formatting artifacts from social media.

2.  **Spelling and Typo Correction:**
    - Correct common spelling mistakes and typos based on standard Arabic pronunciation and writing.
    - Standardize common word variations. Choose the most common and formal variant.

3.  **Punctuation and Sentence Structure:**
    - Ensure sentences are properly punctuated. Add periods, commas, and question marks where they are grammatically necessary but missing.
    - Break up extremely long, run-on sentences into clearer, more coherent sentences.

4.  **Content Refinement:**
    - Remove conversational filler words that add no semantic value (e.g., "آآآآ", "امممم", "يعني" when used as a stutter).
    - Handle transliterated English/foreign words written in Arabic script. Maintain their original form but ensure they are spelled consistently.

**Crucial Negative Constraint:**
- **DO NOT** translate the dialect to Modern Standard Arabic (MSA).
- **DO NOT** remove unique dialect slang or expressions. The goal is to clean, not to neuter the dialect.

**Text to Process:**
{text_chunk}
    """

def clean_and_refine_text(model, text_chunk):
    """Sends text to Gemini API with retry logic."""
    prompt = get_gemini_prompt(text_chunk)
    retries = 3
    for i in range(retries):
        try:
            response = model.generate_content(prompt)
            if response.text:
                return response.text.strip()
            else:
                logging.warning(f"API returned an empty response for chunk. Part: {response.parts}")
                return "GEMINI_API_EMPTY_RESPONSE"
        except Exception as e:
            logging.error(f"API Error: {e}. Retrying in {5 * (i+1)} seconds...")
            time.sleep(5 * (i+1))
    logging.critical(f"API call failed after {retries} retries.")
    return "GEMINI_API_FAILED_AFTER_RETRIES"

# --- Dashboard Display Functions ---
def _progress_bar(percent, length=30):
    """Helper function to create a text-based progress bar."""
    filled_len = int(length * percent)
    bar = '█' * filled_len + '─' * (length - filled_len)
    return bar

def format_time(seconds):
    """Formats seconds into a human-readable string H:M:S."""
    return str(datetime.timedelta(seconds=int(seconds)))


# -----------------------------------------------------------------------
# Section 5: Main Execution Logic
# -----------------------------------------------------------------------
def main():
    """The main function that runs the entire cleaning pipeline."""
    # --- Check for API Key at the start ---
    if not GOOGLE_API_KEY:
        logging.error("API Key not found. Please set the GOOGLE_API_KEY environment variable.")
        sys.exit("ERROR: GOOGLE_API_KEY environment variable not set.")

    # --- Initialize API and Model ---
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        logging.error(f"Failed to configure Gemini API: {e}")
        sys.exit("Exiting due to API configuration error.")

    os.makedirs(CLEANED_PATH, exist_ok=True)
    logging.info("Starting automated processing. Calculating corpus statistics...")
    state = load_state()

    try:
        all_files = sorted([f for f in os.listdir(CORPUS_PATH) if f.endswith('.txt')])
        if not all_files:
            logging.error(f"No .txt files found in the corpus directory: '{CORPUS_PATH}'")
            sys.exit("Exiting because no source files were found.")
        total_files_count = len(all_files)
        total_corpus_bytes = sum(os.path.getsize(os.path.join(CORPUS_PATH, f)) for f in all_files)
    except FileNotFoundError:
        logging.error(f"Corpus path not found: '{CORPUS_PATH}'. Please make sure the corpus folder exists.")
        sys.exit("Exiting due to missing corpus folder.")

    # --- Initialize Status Variables ---
    processed_bytes_total = 0
    total_words_processed = 0
    files_processed_count = len(state.get("processed_files", []))
    start_time = time.time()

    try:
        for filename in all_files:
            if filename in state["processed_files"]:
                processed_bytes_total += os.path.getsize(os.path.join(CORPUS_PATH, filename))
                continue

            logging.info(f"--- Starting automated processing for file: {filename} ---")
            input_file_path = os.path.join(CORPUS_PATH, filename)
            output_file_path = os.path.join(CLEANED_PATH, f"cleaned_{filename}")
            current_file_size = os.path.getsize(input_file_path)

            start_byte = 0
            file_mode = 'w'

            if filename in state.get("partially_processed", {}):
                start_byte = state["partially_processed"][filename]
                file_mode = 'a'
                processed_bytes_total += start_byte
                logging.info(f"Resuming {filename} from byte position {start_byte}")

            chunk_generator = read_in_chunks(input_file_path, start_byte=start_byte)

            with open(output_file_path, file_mode, encoding='utf-8') as outfile:
                for i, (chunk, next_byte_pos) in enumerate(chunk_generator, start=1):
                    os.system('clear' if os.name == 'posix' else 'cls')
                    elapsed_time = time.time() - start_time
                    current_progress_bytes = processed_bytes_total + (next_byte_pos - start_byte)
                    percent_complete = current_progress_bytes / total_corpus_bytes if total_corpus_bytes > 0 else 0
                    eta_seconds = (elapsed_time / percent_complete) * (1 - percent_complete) if percent_complete > 0.001 else 0
                    
                    print("==========================================================")
                    print("     Corpus Cleaning - Live Automated Status")
                    print("==========================================================")
                    print(f" PROGRESS: [{_progress_bar(percent_complete)}] {percent_complete:.2%}")
                    print(f"      ETA: {format_time(eta_seconds)}")
                    print(f"  ELAPSED: {format_time(elapsed_time)}")
                    print("----------------------------------------------------------")
                    print(f"   COUNTS: {total_words_processed:,} words cleaned")
                    print(f"    FILES: {files_processed_count} / {total_files_count} completed")
                    print(f"CURRENT FILE: {filename} (chunk {i})")
                    print("----------------------------------------------------------")
                    
                    # Process chunk with Gemini API
                    cleaned_chunk = clean_and_refine_text(model, chunk)
                    
                    if cleaned_chunk and not cleaned_chunk.startswith("GEMINI_API"):
                        outfile.write(cleaned_chunk + '\n')
                        total_words_processed += len(cleaned_chunk.split())
                    else:
                        logging.warning(f"Skipping chunk {i} in {filename} due to API error")
                    
                    # Update state with current position
                    state["partially_processed"][filename] = next_byte_pos
                    save_state(state)

            # Mark file as completed
            state["processed_files"].append(filename)
            if filename in state.get("partially_processed", {}):
                del state["partially_processed"][filename]
            
            processed_bytes_total += current_file_size
            files_processed_count += 1
            save_state(state)
            logging.info(f"Completed processing {filename}")

    except KeyboardInterrupt:
        logging.info("Processing interrupted by user. State saved.")
        save_state(state)
    except Exception as e:
        logging.error(f"Unexpected error during processing: {e}")
        save_state(state)
    finally:
        logging.info("Processing session ended.")

if __name__ == "__main__":
    main()