import sys
import os

# Ensure the workspace is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.database.db import engine, Base, SessionLocal
from app.agent.conversation_manager import ConversationManager

# Create tables
Base.metadata.create_all(bind=engine)

def main():
    print("Testing real agent conversation loop...")
    db = SessionLocal()
    try:
        response = ConversationManager.process_message(
            db=db,
            phone_number="9182204400",
            user_name="Ravi",
            message_content="Do you have any eggless chocolate cakes?"
        )
        print("================ Agent Response ================")
        print(response)
        print("=================================================")
    except Exception as e:
        print("Error during processing:")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
