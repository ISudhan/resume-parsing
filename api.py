from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/data/")
async def get_json(request: Request):
    data = await request.json()  # parse raw JSON
    return {"received_data": data}
