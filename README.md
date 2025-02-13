# Flow.AI - Lease Exit Workflow Management System

An AI-powered workflow management platform specifically designed to handle lease exit processes. Built using Crew AI agents for orchestrating workflows and integrating with a persistent database for data storage.

## Features

- Dynamic workflow generation and management
- Form processing and validation
- Automated notifications
- Approval chain management
- Document handling
- Role-based access control

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- Anthropic API key

## Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Set up the virtual environment and install dependencies:

For Unix/macOS:
```bash
# Make the setup script executable
chmod +x setup.sh
# Run the setup script
./setup.sh
```

For Windows:
```bash
setup.bat
```

3. Add your Anthropic API key to the `.env` file:
```
ANTHROPIC_API_KEY=your_api_key_here
```

4. Start the backend server:
```bash
# Make sure the virtual environment is activated
source venv/bin/activate  # Unix/macOS
venv\Scripts\activate     # Windows

# Start the server
uvicorn main:app --reload
```

The backend server will be running at `http://localhost:8000`

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
```

The frontend will be running at `http://localhost:3000`

## Project Structure

```
.
├── backend/
│   ├── agents/          # Crew AI agents
│   ├── tools/           # Agent tools
│   ├── main.py          # FastAPI application
│   ├── storage.py       # Database operations
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/        # Next.js pages
│   │   ├── components/ # React components
│   │   └── lib/        # Utilities and helpers
│   └── package.json    # Node.js dependencies
└── README.md
```

## Development

- Backend API documentation is available at `http://localhost:8000/docs`
- The system uses SQLite for development; consider using PostgreSQL for production
- Frontend uses Next.js 14 with App Router and Server Components
- UI components are built using shadcn/ui and Tailwind CSS

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details 