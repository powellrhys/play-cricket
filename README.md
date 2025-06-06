# play-cricket

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![PowerShell](https://img.shields.io/badge/powershell-239120?style=for-the-badge&logo=powershell&logoColor=white)
![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

This project is a data-driven web app that displays club cricket statistics for analysis. This repository contains the backend and frontend code for the entire project.

## Backend

The backend uses the play cricket endpoints to collect data from matches played by the 1st and 2nd XI from the previous 10 seasons. Data scrapping occurs weekly, orchestrated by the `collect_data.yml` github action. 

## Frontend

The frontend is written in python and uses the streamlit library. The frontend consists 6 pages (illustrated below) and uses data from an azure blob storage account to render various tables and plots.

Given the private nature of the data, access to the application is limited and is handled by oauth0.

The application has been deployed twice:

- [Azure]()
- [Streamlit Cloud](https://play-cricket-creigiaucc.streamlit.app/)

### Home Page

![Home Page](./docs/home_page.png)

### Batting Club Analysis Page

![Batting Club Analysis Page](./docs/batting_club_page.png)

### Batting Player Analysis Page

![Batting Player Analysis Page](./docs/batting_player_page.png)

### Bowling Club Analysis

![Bowling Club Analysis Page](./docs/bowling_club_page.png)

### Bowling Player Analysis

![Bowling Player Analysis Page](./docs/bowling_player_page.png)

### Extract Data Page

![Extract Data Page](./docs/extract_data_page.png)
