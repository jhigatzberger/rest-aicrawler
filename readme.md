# Web Data Extraction API

## Overview
This API is a simple Flask wrapper around [Crawl4AI](https://github.com/unclecode/crawl4ai) using DeepSeek as the LLM for extracting structured data from web pages.

## Deployment

The API can be deployed easily using Docker.

1. Clone the repository:
   ```sh
   git clone https://github.com/jhigatzberger/rest-aicrawler.git
   cd rest-aicrawler
   ```

2. Build and run the Docker container:
   ```sh
   docker build -t rest-aicrawler .
   docker run -d -p 5000:5000 --env API_KEY=your_secret_api_key --env DEEPSEEK_API_KEY=your_deepseek_api_key rest-aicrawler
   ```

The API will be accessible at `http://0.0.0.0:5000`.

## OpenAPI Specification
The API is documented using OpenAPI. You can find the full specification in [`openapi.yaml`](./openapi.yaml).

## Contributing
1. Fork the repository.
2. Create a new branch for your feature.
3. Commit your changes.
4. Submit a pull request.

## License
This project is licensed under the MIT License.
