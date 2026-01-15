"""
Main application entry point for Resume Screening System.
"""

from src.api import ResumeScreenerAPI


def main():
    """Start the Resume Screening API server."""
    api = ResumeScreenerAPI()
    api.run()


if __name__ == '__main__':
    main()
