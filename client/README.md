# Debate Agent Client

This is the React frontend for the Debate Agent application. It interacts with the Python FastAPI backend to provide an interactive debate experience.

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file in the `client` directory (optional, defaults to localhost:8000):
   ```env
   VITE_API_URL=http://localhost:8000
   ```

## Running the Application

1. Start the Python API server first (from the `serve` directory):
   ```bash
   cd ../serve
   python debate_api.py
   ```

2. Start the React development server:
   ```bash
   npm run dev
   ```

3. Open your browser at the URL shown (usually `http://localhost:5173`).

## Features

- **Topic Generation**: AI generates strategic positions for both teams.
- **Multi-Round Debate**: Supports up to 3 rounds of arguments.
- **AI Agents**: Affirmative and Negative agents generate arguments and rebuttals.
- **AI Judge**: An impartial AI judge evaluates the debate and declares a winner.
- **Transcript**: Download a full transcript of the debate.

## Tech Stack

- React
- Vite
- Axios
- CSS Modules (custom styling)
