>> from flask import Flask
>> from main import app
>>     print("Successfully imported app from main.py")
>> except ImportError as e:
>>     print(f"Import error: {e}")
>>     app = Flask(__name__)
    @app.route("/")
    def hello():
        return "UniBabel is starting up..."
    
    @app.route("/health")
    def health():
        return {"status": "ok"}

if __name__ == "__main__":
    app.run()