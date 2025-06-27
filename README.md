# CodeRunners: LLM Paper Reproducibility Showdown Portal

## Overview

This portal is part of the SGX3 ADMI Hackathon project **"CodeRunners - Reproducibility Showdown"**. Our mission is to evaluate the reproducibility of 189 LLM research papers, score them using a robust 100-point framework, and visualize the results in a public-facing web portal.

## Features
- **Interactive, Modern UI**: Built with Streamlit, featuring animated metrics, beautiful cards, and responsive design.
- **Scorecard Visualization**: Each paper is scored across four main categories (Code & Environment, Documentation & Transparency, Data & Model Reuse, Community Engagement) on a 1–4 scale, normalized to 100.
- **Filtering & Search**: Filter by score, status, conference, or search by title/ID.
- **Direct Links**: Click to view the GitHub repository for each paper.
- **Team Section**: Meet the team with real GitHub links and avatars.
- **Robust Data Handling**: Parses real CSV data, including extracting repository links from notes.
- **Error Handling**: Graceful handling of missing data, empty filters, and more.

## Data Structure
- **CSV File**: `data/scorecard_summary.csv` contains all paper metadata and scores.
  - Key columns: `Paper File`, `Availability of Code and Software`, `Documentation Quality`, `Dataset Availability`, etc.
  - GitHub links are extracted from the "Availability of Code and Software" notes.

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone https://github.com/SGX3CodeRunners/website-portal.git
   cd website-portal
   ```
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app:**
   ```bash
   streamlit run app.py
   ```
5. **View in browser:**
   Open [http://localhost:8501](http://localhost:8501) (or the URL shown in your terminal).

## Usage
- Use the sidebar to filter and search papers.
- Click a paper to view its detailed scorecard.
- Click "View GitHub Repository for this Paper" to visit the code.
- Explore score breakdowns, trends, and team info.

## Deployment
- The app is ready for deployment on [Streamlit Cloud](https://streamlit.io/cloud) or any platform supporting Python and Streamlit.
- Ensure `requirements.txt` and `data/scorecard_summary.csv` are present in the repository.

## Team
- **Aaliyah Lockett** ([GitHub](https://github.com/AaliyahKam)) – Experiment Engineer
- **Arghavan Noori** ([GitHub](https://github.com/arghavxn)) – Model Analyst
- **Agyei Holy** ([GitHub](https://github.com/holly-agyei)) – Portal Builder
- **Iyana** ([GitHub](https://github.com/iyana1127)) – Project Lead
- **Copernic Mensah** ([GitHub](https://github.com/notcopernicus)) – Presenter

## Acknowledgments
- SGX3 ADMI Hackathon organizers and mentors
- All open-source contributors and the Streamlit community

## License
MIT License (see `LICENSE` file) 