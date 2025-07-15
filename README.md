# Arabic Corpus Refinery

A specialized tool for cleaning and normalizing Arabic text corpora using Google's Gemini. This tool is designed to prepare high-quality text data for training Large Language Models (LLMs) while preserving the unique characteristics of Arabic dialects and expressions.

## Features

- **Automated Text Cleaning**: Uses Google Gemini AI to intelligently clean and normalize Arabic text
- **Dialect Preservation**: Maintains unique dialect expressions and vocabulary while standardizing orthography
- **Memory Efficient**: Processes large corpora in chunks to work on low-memory systems (1GB RAM)
- **Resume Capability**: Can resume processing from where it left off if interrupted
- **Progress Tracking**: Real-time dashboard showing processing progress and statistics
- **Robust Error Handling**: Includes retry logic for API calls and comprehensive logging

## Prerequisites

- Python 3.7 or higher
- Google Gemini API key
- Text corpus files in `.txt` format

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/o96a/LLMCorpusKit.git
   cd LLMCorpusKit
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Get your Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add your API key to the `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env file and add your API key
   ```

## Usage

1. **Prepare your corpus:**
   - Create a `corpus` folder in the project directory
   - Place your `.txt` files containing Arabic text in this folder

2. **Run the cleaning process:**
   ```bash
   python main.py
   ```

3. **Monitor progress:**
   - The script displays a real-time dashboard with progress information
   - Cleaned files will be saved in the `cleaned_corpus` folder
   - Processing state is automatically saved and can be resumed if interrupted

## Configuration

You can modify the following settings in `main.py`:

- `CHUNK_SIZE`: Size of text chunks processed at once (default: 15000 characters)
- `MODEL_NAME`: Gemini model to use (default: 'gemini-2.0-flash')
- `CORPUS_PATH`: Path to input corpus files (default: 'corpus')
- `CLEANED_PATH`: Path for cleaned output files (default: 'cleaned_corpus')

## Text Processing Rules

The tool applies the following cleaning and normalization rules:

### Orthographic Normalization
- Standardizes "ى" (alif maqsura) to "ي" (ya) where appropriate
- Removes diacritics and tatweel marks
- Standardizes laughter expressions (e.g., "ههههه" → "ههه")
- Removes excessive punctuation

### Spelling Correction
- Fixes common typos and spelling mistakes
- Standardizes word variations while preserving dialect

### Content Refinement
- Removes conversational filler words with no semantic value
- Improves sentence structure and punctuation
- Handles transliterated foreign words consistently

### Preservation Constraints
- **Does NOT** translate to Modern Standard Arabic (MSA)
- **Does NOT** remove unique dialect expressions
- Maintains the authentic flavor of the dialect

## File Structure

```
LLMCorpusKit/
├── main.py                 # Main processing script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── corpus/                # Input text files (create this folder)
├── cleaned_corpus/        # Output cleaned files (auto-created)
├── processing_state.json  # Processing state (auto-created)
└── processing.log         # Processing logs (auto-created)
```

## Troubleshooting

### Common Issues

1. **API Key Error:**
   - Ensure your `.env` file contains a valid `GOOGLE_API_KEY`
   - Verify your API key has access to Gemini models

2. **Memory Issues:**
   - Reduce `CHUNK_SIZE` if running on very low memory systems
   - Ensure you have enough disk space for output files

3. **Processing Interruption:**
   - The script automatically saves progress and can resume from the last checkpoint
   - Simply run `python main.py` again to continue

### Logs and Debugging

- Check `processing.log` for detailed error messages
- The script provides verbose console output during processing
- Processing state is saved in `processing_state.json`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gemini AI for powerful text processing capabilities
- The Arabic language community for preserving rich dialects

## Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Search existing [GitHub Issues](https://github.com/o96a/LLMCorpusKit/issues)
3. Create a new issue with detailed information about your problem

---

**Note:** This tool is designed for Arabic text processing. It can work with various Arabic dialects and maintains their unique characteristics while improving text quality.
