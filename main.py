from fastapi import FastAPI, UploadFile, Form, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
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

SERCRET = "super-coding"
manager = LoginManager(SERCRET, '/login')

@manager.user_loader()
def query_user(data):
    WHERE_STATEMENTS = f'id="{data}"'
    if type(data) == dict:
        WHERE_STATEMENTS = f'''id="{data['id']}"'''
    con.row_factory = sqlite3.Row #컬럼명도 같이 가져옴
    cur = con.cursor()
    user = cur.execute(f"""
                       SELECT * from users 
                       WHERE {WHERE_STATEMENTS}
                       """).fetchone()
    return user

#로그인
@app.post('/login')
def iogin(id:Annotated[str,Form()], 
           password:Annotated[str, Form()]):
    user = query_user(id)
    if not user: #유저 정보가 없거나
        raise InvalidCredentialsException #401 에러 생성해서 내려줌
    elif password != user['password']: #패스워드가 같지 않은 경우
         raise InvalidCredentialsException
     
    #토큰에 값을 넣어 보여줄 수 있음
    access_token = manager.create_access_token(data={
        'sub': {
            'id' : user['id'],
            'name' : user['name'],
            'email' : user['email']
        }
     })
    
    return {'access_token':access_token}
    #return 'hi' #지정하지 않아도 서버에서 자동으로 200(성공)으로 내려줌
    

#회원가입
@app.post('/signup')
def signup(id:Annotated[str,Form()], 
           password:Annotated[str, Form()],
           name:Annotated[str,Form()],
           email:Annotated[str,Form()]):
    
    #받은 정보 db에 저장하기
    cur.execute(f"""
                INSERT INTO users(id, name, email, password)
                VALUES ('{id}', '{name}', '{email}', '{password}')
                """)
    con.commit()
    
    return "200"

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
async def get_items(user=Depends(manager)): #증명된 유저에게만 보여주겠다고 설정
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

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

