# Introduction
This repository contains an import sheet column mapper built on LLMs. The purpose of this mapper is to facilitate onboarding of users raw data onto Talenox in the simplest way possible. 

# Setup
1. Install Python from [Python.org](https://www.python.org/) if you have not already done so.
2. Clone this repository.
3. Navigate into the project directory:

   ```
   $ cd import_sheet_mapper
   ```

5. Create a new virtual environment:

    ```
    macOS:
    
    $ python -m venv venv
    $ . venv/bin/activate
    ```

6. Install the requirements:

    ```
    $ pip install -r requirements.txt
    ```

7. Make a copy of the example environment variables file:

    ```
    $ cp .env.example .env
    ```

8. Add your API key to the newly created .env file.

This app still does not have a UI but you can test it using the following command:

```
python main.py
```
