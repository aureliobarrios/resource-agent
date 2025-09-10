import gradio as gr


with gr.Blocks() as demo:
    # -------------------- Helper Functions --------------------
    
    #function to calculate price
    def get_request_price(input_tokens, output_tokens):
        #price per input token
        input_price = 2.5 / 1_000_000
        #price per output token
        output_price = 10 / 1_000_000
        return (input_price * input_tokens) + (output_price * output_tokens)

    # ---------- Components ----------

    #add build type component
    build_type = gr.Radio(
        ["Learning Path", "Tutorial"],
        label="What do you wish to build today?"
    )

    #add learning path topic textbox
    topic = gr.Textbox(visible=False)

    #add difficulty selection component
    difficulty = gr.Radio(visible=False)

    #build selection gradio
    radio = gr.Radio(visible=False)

    #build chatbot interface
    chatbot = gr.Chatbot(type="messages")

    #build message textbox for chatbot
    msg = gr.Textbox(visible=False)

    #build button row section
    with gr.Row():
        clear_button = gr.Button("Clear", interactive=False)
        submit_button = gr.Button("Build Path", interactive=False)

    # ---------- Functions ----------
    
    #function to receive user input
    def user(build_type, topic, msg, history):
        if build_type == "Learning Path":
            #build chatbot message
            message = f"Requested Learning Path For: {topic}"
            return "", history + [{"role": "user", "content": message}]
        else:
            return "", history + [{"role": "user", "content": msg}]

    #function to return bot output
    def bot(history):
        return history
    
    def clear_handle(history):
        #clear chatbot history
        history = []
        return history
    
    def build_layout(build_type):
        return build_type


if __name__ == "__main__":
    demo.launch(show_error=True)