# play-cricket

### Project Codebase

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![PowerShell](https://img.shields.io/badge/powershell-239120?style=for-the-badge&logo=powershell&logoColor=white)
![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

### Project GitHub Action Pipelines

![Collect Play Cricket Data](https://github.com/powellrhys/play-cricket/actions/workflows/collect_data.yml/badge.svg)
![Build & Deploy](https://github.com/powellrhys/play-cricket/actions/workflows/build-and-deploy.yml/badge.svg)

### Codebase Coverage

[![codecov](https://codecov.io/gh/powellrhys/play-cricket/branch/main/graph/badge.svg?token=yNhANNzdtx)](https://codecov.io/gh/powellrhys/golf-ui-streamlit)
![GitHub issues](https://img.shields.io/github/issues/powellrhys/play-cricket.svg)

### Codebase Structure

```
golf-ui-streamlit
├── .github
│   └── workflows
├── backend
│   ├── functions
├── frontend
│   ├── functions
│   └── pages
├── infra
└── tests
    ├── features
    └── unit_tests
```


## Overview

**play-cricket** is a full-stack, data-driven web application that collects, processes, and visualizes cricket performance statistics for the club’s 1st and 2nd XI across the past ten seasons.

- Automatically scrapes match data from the **Play Cricket API**  
- Weekly data ingestion via a scheduled **GitHub Actions** workflow  
- Stores processed datasets in **Azure Blob Storage**  
- Interactive **Streamlit** UI for batting, bowling, and data extraction  
- Application access restricted and authenticated through **Auth0**  

## Backend

- Python-based backend for scraping and transforming historical and recent match data  
- Integrates with Play Cricket endpoints to gather club and player statistics  
- Weekly ETL pipeline coordinated via `collect_data.yml` GitHub Action  
- Outputs stored in Azure Blob Storage for consumption by the frontend  

## Frontend

- Implemented in **Streamlit** for fast and interactive analytics dashboards  
- Loads all datasets directly from Azure Blob Storage  
- Includes six pages covering club-level and player-level batting and bowling performance, plus data extraction tools  

## Infrastructure

- **Terraform** used for Infrastructure-as-Code, stored in the `infra/` directory  
- Azure services include:  
  - Blob Storage (data)  
  - App Service (frontend hosting)  
- Fully reproducible deployment and environment setup  

## Deployment

The application is deployed in two environments:

- [Azure App Service Deployment](https://play-cricket-streamlit-frontend.azurewebsites.net/)

- [Streamlit Cloud Deployment](https://play-cricket-creigiaucc.streamlit.app/)

Both deployments require authentication via **Auth0**, due to the sensitive nature of the underlying data.

## Frontend Application

### Home Page
![Home Page](./docs/home_page.png)

### Batting Club Analysis
![Batting Club Analysis Page](./docs/batting_club_page.png)

### Batting Player Analysis
![Batting Player Analysis Page](./docs/batting_player_page.png)

### Bowling Club Analysis
![Bowling Club Analysis Page](./docs/bowling_club_page.png)

### Bowling Player Analysis
![Bowling Player Analysis Page](./docs/bowling_player_page.png)

### Extract Data Page
![Extract Data Page](./docs/extract_data_page.png)


