#!/usr/bin/env python
"""
Setup script for downloading required NLP models and initializing the system.
Run this script after installing requirements.
"""

import subprocess
import sys
import nltk


def download_spacy_model():
    """Download spaCy English model."""
    print("\n" + "="*60)
    print("Downloading spaCy model (en_core_web_sm)...")
    print("="*60)
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ])
        print("✓ spaCy model downloaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to download spaCy model: {e}")
        return False


def download_nltk_data():
    """Download required NLTK data."""
    print("\n" + "="*60)
    print("Downloading NLTK data...")
    print("="*60)
    
    resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'omw-1.4']
    
    for resource in resources:
        try:
            print(f"Downloading {resource}...", end=" ")
            nltk.download(resource, quiet=True)
            print("✓")
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    print("✓ All NLTK data downloaded successfully")
    return True


def test_imports():
    """Test if all required packages can be imported."""
    print("\n" + "="*60)
    print("Testing imports...")
    print("="*60)
    
    required_packages = [
        'sklearn',
        'spacy',
        'nltk',
        'sentence_transformers',
        'flask',
        'flask_cors',
        'pandas',
        'numpy'
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            print(f"Importing {package}...", end=" ")
            __import__(package)
            print("✓")
        except ImportError as e:
            print(f"✗ Failed: {e}")
            all_ok = False
    
    return all_ok


def initialize_database():
    """Initialize the SQLite database."""
    print("\n" + "="*60)
    print("Initializing database...")
    print("="*60)
    
    try:
        from src.database import Database
        db = Database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        return False


def test_embedding_model():
    """Test if the embedding model can be loaded."""
    print("\n" + "="*60)
    print("Testing embedding model...")
    print("="*60)
    
    try:
        from src.embeddings import EmbeddingGenerator
        print("Loading model (this may take a moment)...")
        generator = EmbeddingGenerator()
        
        # Test embedding generation
        test_text = "This is a test sentence"
        embedding = generator.generate_embedding(test_text)
        print(f"✓ Model loaded successfully (embedding dim: {len(embedding)})")
        return True
    except Exception as e:
        print(f"✗ Failed to load embedding model: {e}")
        return False


def main():
    """Run all setup steps."""
    print("\n" + "="*60)
    print("RESUME SCREENER SYSTEM - SETUP")
    print("="*60)
    
    steps = [
        ("Testing imports", test_imports),
        ("Downloading NLTK data", download_nltk_data),
        ("Downloading spaCy model", download_spacy_model),
        ("Initializing database", initialize_database),
        ("Testing embedding model", test_embedding_model)
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            success = step_func()
            results.append((step_name, success))
        except Exception as e:
            print(f"\n✗ Unexpected error in {step_name}: {e}")
            results.append((step_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    
    for step_name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {step_name}")
    
    all_success = all(success for _, success in results)
    
    if all_success:
        print("\n" + "="*60)
        print("✓ Setup completed successfully!")
        print("="*60)
        print("\nYou can now start the API server:")
        print("  python app.py")
        print("\nOr run the example:")
        print("  python example_usage.py")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("✗ Setup completed with errors")
        print("="*60)
        print("\nPlease fix the errors above and run setup.py again")
        sys.exit(1)


if __name__ == '__main__':
    main()
