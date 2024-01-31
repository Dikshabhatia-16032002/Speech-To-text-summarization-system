from app import app, db, User,Summary
import sqlite3

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Password: {user.password},mobile Number={user.mobilenumber}")
    summary=Summary.query.all()
    for data in summary:
        print(f"user ID:{data.user_id} , text_to_summarize:{data.text_to_summarize} ,generated_summary: {data.generated_summary}")