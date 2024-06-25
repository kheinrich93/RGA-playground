# RGA-playground
This repo is a personal playground to test the functionalities of large language models.

So far implemented:
- Webscraping song lyrics using GeniusAPI
- Preprocessing: removing duplicates, covers, cleaning text data, etc.
- Created custom haystack generator to use groq API
- Haystack 2.x implementation of:
    - Basic retrieval qa pipeline
    - Hybrid retrieval
    - RAG to create new song lyric based on top-3 lyrics that closest to a query

What's next:
- Result evaluation
- Language detection
- Fallbacks and conditional routing
- Experiment with different document stores, like DB

On hold:
- Improve pipeline building, serialization -> document store 