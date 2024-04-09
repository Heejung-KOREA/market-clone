from fastapi import FastAPI, UploadFile, Form, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import sqlite3

#데이터베이스 연결
con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()

#IF NOT EXISTS --> 테이블이 없으면 생성
cur.execute(f"""
            CREATE Table IF NOT EXISTS items ( 
                id INTEGER PRIMARY KEY, 
                title TEXT NOT NULL,
                image BLOB,
                price INTEGER NOT NULL,
                description TEXT,
                place TEXT NOT NULL,
                insertAt INTEGER NOT NULL);
            """)

app = FastAPI()

@app.post('/items')
async def create_item(image:UploadFile, 
                title:Annotated[str,Form()], #title 데이터는 Form() 형식의 문자열로 받는다.
                price:Annotated[int,Form()], 
                description:Annotated[str,Form()], 
                place:Annotated[str,Form()],
                insertAt:Annotated[int,Form()]
                ):
    
    image_bytes = await image.read() #이미지는 크기가 크기 때문에 읽는 시간이 필요함.
    #데이터베이스에 값 저장
    cur.execute(f"""
                INSERT INTO items (title, image, price, description, place, insertAt)
                VALUES ('{title}', '{image_bytes.hex()}', {price}, '{description}', '{place}',{insertAt}) 
                """)    #image값은 길므로 16진수로 바꿔서 넣어주고, price는 숫자 값이므로 따옴표를 때준다. (str을 나타내기 때문)
    con.commit()
    return '200'

#서버에 저장된 값 보여주기
@app.get('/items')
async def get_items():
    #데이터베이스에서 가져오기
    con.row_factory = sqlite3.Row #컬럼명도 같이 가져옴
    cur = con.cursor()
    rows = cur.execute(f"""
                       SELECT * from items;
                       """).fetchall()
    
    return JSONResponse(jsonable_encoder(dict(row) for row in rows)) #json 형식으로 바꾸어줌

#이미지id 값에 맞는 이미지 가져오기
@app.get('/images/{item_id}')
async def get_image(item_id):
    cur = con.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id ={item_id}
                              """).fetchone()[0] #16진법 상태
    
    return Response(content = bytes.fromhex(image_bytes), media_type='image/*')

@app.post('/signup')
def signup(id:Annotated[str,Form()], password:Annotated[str, Form()]):
    print(id, password)
    return '200'

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

