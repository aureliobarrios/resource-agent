import gradio as gr

with gr.Blocks() as demo:

    def do_something():
        return "Test"
    
if __name__ == "__main__":
    demo.launch(show_error=True)