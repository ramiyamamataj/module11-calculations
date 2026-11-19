# Module 11: Calculation Model, Factory Pattern, and Pydantic Validation

## Overview
This project expands the FastAPI + PostgreSQL application layer with a polymorphic SQLAlchemy `Calculation` model (`AddCalculation`, `SubCalculation`, `MultiplyCalculation`, `DivideCalculation`), a Factory pattern (`Calculation.create()`), and Pydantic v2 validation schemas (`CalculationCreate`, `CalculationRead`).

## Docker Hub Repository
- **Docker Hub Image:** https://hub.docker.com/r/ramiyamamataj/module11-calculations

## Running Tests Locally
1. Start the PostgreSQL database container:
   ```bash
   docker compose up -d db
