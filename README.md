# AI-Powered On-Page SEO Automation Platform

This project is a clone of `metamonster.ai`, an AI automation platform for on-page SEO at scale. It allows users to crawl sites, prepare content for AI, work in spreadsheet-like tables, run SEO prompt templates in bulk, and more.

## Project Structure

The project is a monorepo containing two main parts:

-   `./frontend`: A [Next.js](https://nextjs.org/) application that serves as the user interface.
-   `./backend`: A [FastAPI](https://fastapi.tiangolo.com/) application that provides the backend API.

## Tech Stack

-   **Frontend**: Next.js, React, TypeScript, Tailwind CSS, TanStack Table
-   **Backend**: Python, FastAPI, Celery
-   **Database**: PostgreSQL with the `pgvector` extension
-   **Crawler**: Playwright
-   **LLM Integration**: Ollama, LiteLLM

## Getting Started

### Prerequisites

-   Node.js and npm
-   Python 3.9+ and pip
-   Docker and Docker Compose (for PostgreSQL and Redis)

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the development server:
    ```bash
    uvicorn main:app --reload
    ```

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install the required dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
