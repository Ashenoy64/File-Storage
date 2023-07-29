# FileStorage Project


Welcome to the FileStorage project! This project is a simple file storage application built with Python, Streamlit, and Sockets. With this application, you can easily upload files to the server and download them whenever needed.

## Features

- **Upload Files:** Easily upload files from your local machine to the server.
- **Download Files:** Download the uploaded files whenever you need them.

## Installation

To run this project locally, follow these steps:

1. Clone the repository to your local machine.
   ```bash
   git clone https://github.com/Ashenoy64/File-Storage.git
   ```

2. Navigate to the project directory.
   ```bash
   cd File-Storage
   ```

3. Install the required dependencies for both the server and the client.
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Open a terminal window and navigate to the `server` directory.
   ```bash
   cd server
   ```

2. Run the server by executing the following command:
   ```bash
   python server.py
   ```

3. Open a new terminal window and navigate to the `client` directory.
   ```bash
   cd ../client
   ```

4. Launch the web application using Streamlit by running:
   ```bash
   streamlit run app.py
   ```

5. Access the web application in your browser at `http://localhost:8501`.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
