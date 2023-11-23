import uvicorn
import asyncio
from fastapi import FastAPI, UploadFile, Depends
from typing import List, Union
from sqlalchemy import text
from broker import main_logic_kafka
from database import get_async_session, create_db_and_tables, AsyncSession
from schemas import AvgCount


def create_app():
    app = FastAPI(docs_url="/")

    @app.on_event("startup")
    async def startup_event():
        await create_db_and_tables()

    @app.post("/uploadfiles/")
    async def create_upload_files(
        file: UploadFile, session: AsyncSession = Depends(get_async_session)
    ):
        await main_logic_kafka(file.filename, session)
        return "Counted!"

    @app.get("/show/")
    async def show_list(
        session: AsyncSession = Depends(get_async_session),
    ) -> Union[List[AvgCount], List]:
        result = text(
            "SELECT to_char(datetime, 'YYYY-MM-DD'), title, AVG(value_count) FROM linesymbolcounter GROUP BY to_char(datetime, 'YYYY-MM-DD'),title"
        )
        notes = await session.execute(result)
        return [
            AvgCount(date=i[0], title=i[1], x_avg_count_in_line=i[2]) for i in notes
        ]

    return app


def main():
    uvicorn.run(
        f"{__name__}:create_app",
        host="0.0.0.0",
        port=8888,
    )


if __name__ == "__main__":
    main()
