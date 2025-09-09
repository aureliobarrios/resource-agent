import gradio as gr


with gr.Blocks() as demo:
    # -------------------- Helper Functions --------------------
    
    # ---------- Components ----------

    #add build type component
    build_type = gr.Radio(
        ["Learning Path", "Tutorial"],
        label="What do you wish to build today?"
    )

if __name__ == "__main__":
    demo.launch(show_error=True)