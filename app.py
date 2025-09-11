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
        #change layout based on student selection
        if build_type == "Learning Path":
            #build topic textbox selection
            topic = gr.Textbox(
                label="What topic would you like you build your learning path for? i.e. Python, JavaScript, etc...",
                placeholder="Insert your learning topic here",
                interactive=True,
                visible=True
            )
            #build difficulty level selection
            difficulty = gr.Radio(
                ["Beginner", "Intermediate", "Hard", "Advanced"],
                value="Beginner",
                label="What would you say your current expertise level on the subject is at?",
                visible=True,
                interactive=True
            )
            #build chatbot interface
            chatbot = gr.Chatbot(type="messages")
            #build textbot for message input
            msg = gr.Textbox(visible=False)
        else:
            #build topic textbox selection
            topic = gr.Textbox(visible=False, value='')
            #build difficulty level selection
            difficulty = gr.Radio(visible=False)
            #build chatbot interface
            chatbot = gr.Chatbot(type="messages")
            #build textbox for message input
            msg = gr.Textbox(
                label="What question do you want to build a tutorial for?",
                placeholder="Insert what you wish to learn here",
                visible=True
            )
        return topic, difficulty, chatbot, msg
    
    #build layout for resource type selection
    def resource_selection(build_type, radio):
        #build radio best on build type
        if build_type == "Learning Path":
            radio = gr.Radio(
                ["Learning Path", "Videos"],
                value="Learning Path",
                label="What kind of resources would you like to receive?",
                visible=True
            )
        else:
            radio = gr.Radio(
                ["Learning Path", "Videos"],
                value="Learning Path",
                label="What kind of resources would you like to receive?",
                visible=True
            )
        return radio
    
    #build layout for button functionality
    def buttons(clear_button, submit_button):
        clear_button = gr.Button("Clear", interactive=True)
        submit_button = gr.Button("Build Path", interactive=True)
        return clear_button, submit_button
    
    def check_input():
        return "Test"
    
    def clear_all():
        return "Test"


if __name__ == "__main__":
    demo.launch(show_error=True)