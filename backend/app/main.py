from fastapi import FastAPI

app = FastAPI(title="Clinic-Specific AI Dental Screening API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
