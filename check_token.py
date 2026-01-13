
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'serve'))
from DatabaseService import DatabaseService

db = DatabaseService()
token = "f32c1191-15de-49b2-8fd7-bc488a12f92c"
data = db.get_token_data(token)
if data:
    print(f"Token found: {data}")
else:
    print(f"Token {token} not found or invalid.")
