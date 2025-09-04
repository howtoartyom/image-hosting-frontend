[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# IMAGE HOSTING

## Overview

**IMAGE HOSTING** это проект, который позволяет пользователю загружать изображения и получать ссылки на них.

## Quick Start with Docker

To quickly set up and run the application using Docker, follow these steps:

### 1. Build and Run the Docker Container

```bash
docker-compose up --build
```

The image hosting will be available at `http://localhost:8000/`.

## Installation

### Prerequisites

- **Python 3.10**

### Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/howtoartyom/image-hosting-frontend.git
   cd image-hosting-frontend
   ```

2. **Set Up the Virtual Environment:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Development Server:**

   ```bash
   python app.py
   ```

   The API will be available at `http://127.0.0.1:8000/`.

## Usage

### Example Request

**Creating a Wallet:**

```bash
curl -I http://localhost:8080/
```

**Creating a Transaction:**

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@test.jpg"
```

## Running Tests

To run the test suite with coverage:

```bash
pytest --cov=wallet_transaction_api
```


## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact
