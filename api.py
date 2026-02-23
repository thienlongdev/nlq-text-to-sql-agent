from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.multi_agent_graph import build_nlq_to_sql_graph

app = FastAPI(title="NLQ-to-SQL API")

graph = build_nlq_to_sql_graph(include_executor=True)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql: str
    result: list | None = None
    columns: list | None = None


@app.post("/query", response_model=QueryResponse)
async def run_query(req: QueryRequest):
    try:
        state = {"question": req.question}

        output = graph.invoke(state)

        if output.get("error"):
            raise HTTPException(
                status_code=400,
                detail=output.get("error")
            )

        return QueryResponse(
            sql=output.get("sql_query"),
            result=output.get("query_result"),
            columns=output.get("query_columns")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))