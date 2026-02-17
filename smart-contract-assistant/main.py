"""
Main entry point for Smart Contract Assistant
"""
import argparse
import threading
import uvicorn
from api_server import app
from gradio_ui import create_interface
from config import API_PORT, UI_PORT

def main():
    parser = argparse.ArgumentParser(description="Smart Contract Assistant")
    parser.add_argument(
        "--mode", 
        choices=["api", "ui", "both"], 
        default="both",
        help="Run mode: 'api' (backend only), 'ui' (frontend only), or 'both' (default)"
    )
    args = parser.parse_args()
    
    if args.mode == "api":
        print(f" Starting API server on http://localhost:{API_PORT}")
        uvicorn.run(app, host="0.0.0.0", port=API_PORT)
    
    elif args.mode == "ui":
        print(f" Starting Gradio UI on http://localhost:{UI_PORT}")
        ui_app = create_interface()
        ui_app.launch(server_name="0.0.0.0", server_port=UI_PORT, share=False)
    
    else:  # both
        print(f" Starting API server on http://localhost:{API_PORT}")
        api_thread = threading.Thread(
            target=lambda: uvicorn.run(app, host="0.0.0.0", port=API_PORT),
            daemon=True
        )
        api_thread.start()
        
        print(f" Starting Gradio UI on http://localhost:{UI_PORT}")
        print(f" Open http://localhost:{UI_PORT} in your browser")
        ui_app = create_interface()
        ui_app.launch(server_name="0.0.0.0", server_port=UI_PORT, share=False)

if __name__ == "__main__":
    main()
