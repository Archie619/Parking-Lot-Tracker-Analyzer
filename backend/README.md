# The Backend

This folder contains the files and logic for the University Parking 
Lot Tracker and Analyzation System backend

## Version

Currently, the backend is being developed in Python 3.11.9

## Basics

To get the backend up and running perform the following...

1. Make / open your python venv
    - If not created: python -m venv .venv
    - If activating:
        - Linux: source .venv/bin/activate
        - Windows: .\\.venv\Scripts\activate

2. Install the requirements if not installed
    - pip install -r requirements.txt
    - NOTE: this file is in the backend folder you may need to cd
      into the correct directory

3. Start uvicorn:
    - Move into the backend directory
    - uvicorn api_init:app --reload

## Tips

- If you can't execute your activate script for your virtual environment,
  verify your execution policy is not blocking it:
    - Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy AllSigned
    - NOTE: You can set your policy to something else if you'd like