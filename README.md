# Mood Indigo Points Manipulation - Brute Force Script

## Overview

This project contains a Python automation script that uses a brute-force approach to interact with the Mood Indigo system. Using Selenium for web automation, the script explores input combinations to adjust point values within the system while reducing manual involvement.

> **Warning**: This tool serves educational purposes for authorized testing in controlled environments. Misuse of the script may result in account suspension or legal consequences. Use responsibly.

## Features

- **Brute-Force Automation**: Systematically explores input permutations to manipulate Mood Indigo points.
- **Web Automation**: Employs Selenium WebDriver to automate browser interactions and handle complex UI elements.
- **OTP Handling**: Automates temporary email generation and OTP retrieval to streamline the login process.
- **Robust Error Handling**: Implements retry logic, delays, and exception management to address transient issues.
- **Configurable Parameters**: Options for input values such as full name, date of birth (dd/mm/yyyy), phone number, and gender.

## Prerequisites

- **Python 3.x**
- **Selenium WebDriver** (compatible with your browser, e.g., Microsoft Edge)
- Libraries listed in `requirements.txt` (e.g., `requests`)

Install dependencies using:

```bash
pip install -r requirements.txt
```

## Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/akashch1512/MoodIndigo-Points-Automator.git
   ```

2. **Navigate to the project directory**:

   ```bash
   cd MoodIndigo-Points-Automator
   ```

3. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before running the script, update settings in `main.py`:

- **Credentials & Session Details**: Adjust login and session parameters for your testing environment.
- **Input Parameters**: Set values for full name, date of birth, phone number, and gender.
- **Automation Settings**: Adjust timing delays and retry attempts to suit your network and system conditions.

## Usage

Run the script using:

```bash
python main.py
```

The script will:

- Launch an automated browser session.
- Generate a temporary email and request an OTP.
- Automatically verify the OTP and fill in necessary form fields.
- Navigate through pages to execute the point manipulation process.

## Customization

- **Point Manipulation Logic**: Adjust the brute-force algorithm to target specific point ranges or input conditions.
- **Error Handling & Retries**: Configure wait times and retry attempts for improved reliability.
- **UI Element Selectors**: Update selectors if the target website changes.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for improvements or bug fixes.

## License

This project uses the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This script comes as-is without any warranty. The user assumes full responsibility for its use. Unauthorized use may lead to severe consequences.
