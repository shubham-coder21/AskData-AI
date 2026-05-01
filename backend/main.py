# # from fastapi import FastAPI, UploadFile, Form
# # from fastapi.middleware.cors import CORSMiddleware
# # import pandas as pd
# # from groq import Groq
# # from db import SessionLocal, ChatHistory

# # app = FastAPI()

# # # 🔑 Put your Groq API key here
# # client = Groq(api_key="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")

# # # Allow frontend to connect
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # @app.post("/analyze")
# # async def analyze(files: list[UploadFile], question: str = Form(...)):

# #     # 📂 Read multiple CSVs
# #     dfs = []
# #     for file in files:
# #         df = pd.read_csv(file.file)
# #         dfs.append(df)

# #     combined_df = pd.concat(dfs)

# #     # 🧠 Send sample data to AI (not full data, faster)
# #     data_sample = combined_df.head(20).to_string()

# #     prompt = f"""
# #     You are a data analyst.

# #     Here is dataset sample:
# #     {data_sample}

# #     Question:
# #     {question}

# #     Give a clear answer.
# #     """

# #     response = client.chat.completions.create(
# #         model="llama3-70b-8192",
# #         messages=[{"role": "user", "content": prompt}]
# #     )

# #     answer = response.choices[0].message.content

# #     # 💾 Save in database
# #     db = SessionLocal()
# #     db.add(ChatHistory(question=question, answer=answer))
# #     db.commit()
# #     db.close()

# #     return {"answer": answer}


# # @app.get("/history")
# # def get_history():
# #     db = SessionLocal()
# #     data = db.query(ChatHistory).all()
# #     db.close()

# #     return [{"q": d.question, "a": d.answer} for d in data]


# # ####################################################################

# from fastapi import FastAPI, UploadFile, Form
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import os, re
# from dotenv import load_dotenv
# from groq import Groq
# from db import SessionLocal, ChatHistory

# load_dotenv()

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# client = Groq(api_key=os.getenv("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"))

# df = None


# # -------------------------------
# # SMART LOGIC (FAST)
# # -------------------------------
# def smart_logic(question):
#     global df
#     q = question.lower()

#     # 1. FILTER BY CITY
#     match = re.search(r"from (\w+)", q)
#     if match:
#         city = match.group(1)
#         result = df[df["City"].str.lower() == city.lower()]
#         return result.to_dict(orient="records")

#     # 2. TOP SALES
#     if "top" in q or "highest" in q:
#         result = df.sort_values(by="Sales", ascending=False).head(3)
#         return result[["Name", "Sales"]].to_dict(orient="records")

#     # 3. AVERAGE
#     if "average" in q:
#         return f"Average sales is {round(df['Sales'].mean(),2)}"

#     # 4. CITY REPORT
#     if "total sales" in q or "report" in q:
#         result = df.groupby("City")["Sales"].sum().reset_index()
#         return result.to_dict(orient="records")

#     return None


# # -------------------------------
# # AI FALLBACK
# # -------------------------------
# def ask_ai(question):
#     try:
#         response = client.chat.completions.create(
#             model="llama3-70b-8192",  # ✅ working model
#             messages=[{"role": "user", "content": question}],
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         return f"AI Error: {str(e)}"


# # -------------------------------
# # API ROUTE
# # -------------------------------
# @app.post("/ask")
# async def ask(file: UploadFile, question: str = Form(...)):
#     global df

#     df = pd.read_csv(file.file)

#     # FAST LOGIC FIRST
#     answer = smart_logic(question)

#     # AI FALLBACK
#     if answer is None:
#         answer = ask_ai(question)

#     # SAVE HISTORY
#     db = SessionLocal()
#     db.add(ChatHistory(question=question, answer=str(answer)))
#     db.commit()
#     db.close()

#     return {"answer": answer}


# @app.get("/history")
# def history():
#     db = SessionLocal()
#     data = db.query(ChatHistory).all()
#     db.close()
#     return data
# __________________________________________________________________________
#-------------------------------------------------------------------------------


from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os, re
from dotenv import load_dotenv
from groq import Groq
from db import SessionLocal, ChatHistory

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("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"))

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

df = None


# -------------------------------
# SMART LOGIC
# -------------------------------
def smart_logic(question):
    global df
    q = question.lower()

    # filter by city
    match = re.search(r"from (\w+)", q)
    if match:
        city = match.group(1)
        result = df[df["City"].str.lower() == city.lower()]
        return result.to_dict(orient="records")

    # top
    if "top" in q or "highest" in q:
        result = df.sort_values(by="Sales", ascending=False).head(3)
        return result[["Name", "Sales"]].to_dict(orient="records")

    # average
    if "average" in q:
        return f"Average sales is {round(df['Sales'].mean(),2)}"

    # report
    if "total sales" in q or "report" in q:
        result = df.groupby("City")["Sales"].sum().reset_index()
        return result.to_dict(orient="records")

    return None


# -------------------------------
# AI FALLBACK
# -------------------------------
def ask_ai(question):
    try:
        res = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": question}],
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"


# -------------------------------
# ROUTE
# -------------------------------
@app.post("/ask")
async def ask(file: UploadFile = None, question: str = Form(...)):
    global df

    # save file once
    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(path, "wb") as f:
            f.write(file.file.read())
        df = pd.read_csv(path)

    if df is None:
        return {"answer": "Upload CSV first"}

    answer = smart_logic(question)

    if answer is None:
        answer = ask_ai(question)

    db = SessionLocal()
    db.add(ChatHistory(question=question, answer=str(answer)))
    db.commit()
    db.close()

    return {"answer": answer}


@app.get("/history")
def history():
    db = SessionLocal()
    data = db.query(ChatHistory).all()
    db.close()
    return data