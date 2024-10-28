# Flask Data Store API

This is a simple Flask application that provides a RESTful API to store, retrieve, update, and delete data using an SQLite database. It also includes rate limiting, API key validation, and caching for improved performance.

## Features

- **CRUD Operations**: Create, Read, Update, and Delete data.
- **Rate Limiting**: Limits the number of requests to protect the server.
- **API Key Authentication**: Requires a valid API key for access.
- **Caching**: Uses caching to speed up data retrieval.
- **HEAD Method Support**: Check for the existence of keys without fetching the full data.

## Requirements

Make sure you have Python 3.7 or higher installed on your machine.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment** (optional but recommended):

   ```bash
   python -m venv myenv
   ```

3. **Activate the Virtual Environment**:

   - On Windows:
     ```bash
     myenv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source myenv/bin/activate
     ```

4. **Install Required Packages**:

   ```bash
   pip install -r requirements.txt
   ```

   This command will install all the necessary libraries as specified in the `requirements.txt` file.

5. **Set Up Environment Variables** (if necessary):

   If your application requires any environment variables (e.g., for configuration), create a `.env` file in the root of your project and define them as follows:

   ```
   FLASK_ENV=development
   API_KEYS=validapi1,validapi2,validapi3
   ```

6. **Initialize the Database**:

   Before running the server, initialize the database:

   1. **Run the Flask application once to create the database**:
   
      ```bash
      python app.py
      ```

      After running this command, you can stop the server. The `data_store.db` SQLite database file will be created in the same directory.

## Running the Server

1. **Start the Flask Server**:

   ```bash
   python app.py
   ```

   The server will start running on `http://0.0.0.0:5000`.

2. **Access the API**:

   Use an API client like Postman or `curl` to make requests to the server.

## API Endpoints

- **GET** `/data/<key>`: Retrieve data for the specified key.
- **POST** `/data`: Add new data (requires JSON payload with `key` and `value`).
- **PUT** `/data/<key>`: Update existing data for the specified key (requires JSON payload with `value`).
- **DELETE** `/data/<key>`: Delete data for the specified key.
- **HEAD** `/data/<key>`: Check if a key exists.

### Example Requests

- **Add Data**:
  ```bash
  curl -X POST -H "X-API-KEY: validapi1" -H "Content-Type: application/json" -d '{"key": "exampleKey", "value": "exampleValue"}' http://localhost:5000/data
  ```

- **Get Data**:
  ```bash
  curl -X GET -H "X-API-KEY: validapi1" http://localhost:5000/data/exampleKey
  ```

- **Update Data**:
  ```bash
  curl -X PUT -H "X-API-KEY: validapi1" -H "Content-Type: application/json" -d '{"value": "newValue"}' http://localhost:5000/data/exampleKey
  ```

- **Delete Data**:
  ```bash
  curl -X DELETE -H "X-API-KEY: validapi1" http://localhost:5000/data/exampleKey
  ```

- **Check Existence**:
  ```bash
  curl -X HEAD -H "X-API-KEY: validapi1" http://localhost:5000/data/exampleKey
  ```

## Error Handling

The API returns standard HTTP status codes to indicate the outcome of requests:

- `200 OK`: Successful request.
- `201 Created`: Successfully added data.
- `400 Bad Request`: Invalid input or request format.
- `401 Unauthorized`: Missing or invalid API key.
- `404 Not Found`: Key does not exist.
- `500 Internal Server Error`: An unexpected error occurred on the server.
