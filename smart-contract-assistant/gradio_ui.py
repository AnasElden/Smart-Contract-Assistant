"""
Gradio UI for Smart Contract Assistant
"""
import gradio as gr
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8001"

def chat(message: str, history):
    """Handle chat messages - convert to messages format"""
    if not message.strip():
        return "", history
    
    # Convert history from messages format to API format
    history_list = []
    if history:
        for h in history:
            if isinstance(h, dict):
                role = h.get("role", "")
                content = h.get("content", "")
                if role == "user":
                    history_list.append({"human": content, "assistant": ""})
                elif role == "assistant" and history_list:
                    history_list[-1]["assistant"] = content
    
    try:
        # Call API with history
        use_history = len(history_list) > 0
        response = requests.post(
            f"{API_URL}/qa",
            params={"question": message, "use_history": use_history},
            json=history_list if use_history else [],
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer received")
            
            # Add sources
            if data.get("sources"):
                answer += "\n\n**Sources:**\n"
                for i, source in enumerate(data["sources"][:3], 1):
                    answer += f"{i}. {source.get('filename', 'Unknown')} (Chunk {source.get('chunk_index', 'N/A')})\n"
            
            # Add guardrail warnings if any
            if data.get("guardrails") and not data["guardrails"].get("all_passed", True):
                answer += "\n\n **Note:** Some validation checks failed. Please verify the answer."
            
            if history is None:
                history = []
            
            # Add user message
            history.append({"role": "user", "content": message})
            # Add assistant response
            history.append({"role": "assistant", "content": answer})
            
            return "", history
        else:
            error = f"API Error: {response.status_code}"
            if history is None:
                history = []
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error})
            return "", history
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        error_msg = f"Error: {str(e)}"
        if history is None:
            history = []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        return "", history

def upload_file(file):
    """Handle file upload"""
    if file is None:
        return "No file selected", ""
    
    try:
        with open(file.name, "rb") as f:
            files = {"file": (file.name, f, "application/pdf" if file.name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post(f"{API_URL}/upload", files=files, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            return f"{data.get('message', 'Uploaded successfully')}", f"**File:** {data.get('filename')}\n**Chunks:** {data.get('chunks', 0)}"
        else:
            return f" Error: {response.status_code}", str(response.text)
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        return f" Error: {str(e)}", ""

def create_interface():
    """Create Gradio interface"""
    with gr.Blocks() as app:
        gr.Markdown("# 📄 Smart Contract Assistant")
        
        with gr.Tabs():
            # Upload Tab
            with gr.Tab("📤 Upload Document"):
                file_input = gr.File(label="Upload PDF or DOCX", file_types=[".pdf", ".docx"])
                upload_btn = gr.Button("Upload")
                upload_status = gr.Textbox(label="Status", interactive=False)
                upload_info = gr.Markdown()
                
                upload_btn.click(
                    fn=upload_file,
                    inputs=[file_input],
                    outputs=[upload_status, upload_info]
                )
            
            # Chat Tab
            with gr.Tab("💬 Chat"):
                chatbot = gr.Chatbot(
                    label="Conversation", 
                    height=500,
                    value=[]  # Initialize empty
                )
                msg = gr.Textbox(label="Your Question", placeholder="Ask about your contract...", lines=2)
                clear_btn = gr.Button("Clear")
                summarize_btn = gr.Button("📄 Summarize Document")
                
                def clear_chat():
                    return [], ""
                
                def summarize(history):
                    """Summarize the document"""
                    try:
                        response = requests.post(f"{API_URL}/summarize", timeout=120)
                        if response.status_code == 200:
                            data = response.json()
                            summary = data.get("summary", "Summary not available")
                            if history is None:
                                history = []
                            history.append({"role": "assistant", "content": f"**Document Summary:**\n\n{summary}"})
                            return history
                        else:
                            if history is None:
                                history = []
                            history.append({"role": "assistant", "content": f"Error: {response.status_code}"})
                            return history
                    except Exception as e:
                        if history is None:
                            history = []
                        history.append({"role": "assistant", "content": f"Error: {str(e)}"})
                        return history
                
                msg.submit(chat, inputs=[msg, chatbot], outputs=[msg, chatbot])
                clear_btn.click(clear_chat, outputs=[chatbot, msg])
                summarize_btn.click(summarize, inputs=[chatbot], outputs=[chatbot])
        
        gr.Markdown("---\n**Note:** Upload a document first, then ask questions about it.")
    
    return app

def main():
    """Main entry point"""
    from config import UI_PORT
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=UI_PORT, share=False)

if __name__ == "__main__":
    main()
