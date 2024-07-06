from fastapi import FastAPI
import uvicorn
app = FastAPI()

@app.get("/")
def get_root():
    return "Hello to API"

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if(__name__ == '__main__'):
    main()