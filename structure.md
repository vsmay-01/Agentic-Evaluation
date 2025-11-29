Agentic-Evaluation/
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI app entry point
│       ├── core/
│       │   └── config.py           # Gemini & environment config
│       ├── services/
│       │   ├── llm_provider.py     # Gemini API integration
│       │   ├── llm_judge.py        # Evaluation orchestrator
│       │   ├── rule_based.py       # Length/punctuation checks
│       │   └── batch_processor.py  # Async batch processing
│       └── api/
│           ├── evaluate.py         # Single evaluation endpoint
│           └── batch.py            # Batch endpoints
│
├── frontend/
│   └── react_app/
│       ├── src/
│       │   ├── App.js              # Main React component (form)
│       │   └── utils/
│       │       └── api.js          # Backend API client
│       └── package.json            # npm dependencies
│
├── data/
│   └── evaluations.json            # Stored results
│
├── .env.example                     # Configuration template
├── .env                             # Your actual credentials (git-ignored)
├── README.md                        # Project documentation
└── requirements.txt                 # Python dependencies