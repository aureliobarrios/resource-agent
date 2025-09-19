import os
import json
import gradio as gr
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv


with gr.Blocks() as demo:
    # -------------------- Helper Functions --------------------
    
    #function to calculate price
    def get_request_price(input_tokens, output_tokens):
        #price per input token
        input_price = 2.5 / 1_000_000
        #price per output token
        output_price = 10 / 1_000_000
        return (input_price * input_tokens) + (output_price * output_tokens)
    
    #function we intend to use for function calling
    def extract_learning_info(beginner_description, beginner_query, 
                            intermediate_description, intermediate_query, 
                            hard_description, hard_query,
                            advanced_description, advanced_query):
        learning_info = {
            "beginner": {
                "description": beginner_description,
                "query": beginner_query
            },
            "intermediate": {
                "description": intermediate_description,
                "query": intermediate_query
            },
            "hard": {
                "description": hard_description,
                "query": hard_query
            },
            "advanced": {
                "description": advanced_description,
                "query": advanced_query
            }
        }
        return learning_info
    
    #helper function to build data data dictionary for database input
    def build_data(result, topic, difficulty, video):
        #build data dictionary
        data = {}
        #handle data input based on data type
        if video:
            #save resource url
            data["resource"] = f"https://www.youtube.com{result['url_suffix']}"
            #save resource title
            data["title"] = result["channel"].replace("'", "")
            #save resource description
            data["description"] = result["title"].replace("'", "")
        else:
            #save resource url
            data["resource"] = result.url
            #save resource title
            data["title"] = result.title.replace("'", "")
            #save resource description
            data["description"] = result.description.replace("'", "")
        #save resource topic
        data["topic"] = topic
        #save resource difficulty
        data["difficulty"] = difficulty
        #save resource validation
        data["validated"] = False
        #save resource found time
        data["found_time"] = datetime.now()
        return data

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
        #load in the environment
        load_dotenv()
        #used to calculate query price
        INPUT_TOKENS = 0 #prompt tokens
        OUTPUT_TOKENS = 0 #completion tokens
        #load environment variables and build client
        WEB_RESULTS = int(os.getenv("WEB_RESULTS"))
        REDDIT_RESULTS = int(os.getenv("REDDIT_RESULTS"))
        RESOURCES_NEEDED = int(os.getenv("RESOURCES_NEEDED"))
        #set the sleep interval for our google search based on number of web results
        SLEEP_INTERVAL = 0 if WEB_RESULTS < 100 else 5
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")

        client = Groq(
            api_key=GROQ_API_KEY
        )
        #get previous user message
        student_prompt = history[-1]["content"]
        #handle input based on different selections
        if build_type == "Learning Path":
            #get the topic
            topic = student_prompt.split(":")[1].lower()
            #build student prompt
            student_prompt = f"I want to learn {topic}"
        #build prompt that will return context for learning path        
        context_prompt = f'''
        {student_prompt}

        Can you build me a learning path to solve this problem that follows these 
        levels: beginner, intermediate, hard, advanced.

        For each of these levels give me a one sentence query that I can input into
        my search engine that will return resources that will help me solve my problem.

        Make sure to also include a one sentence description of what the current
        difficulty level is teaching me.
        '''
        #build context for learning path
        chat_completion = client.chat.completions.create(
            messages = [
                {
                    "role": "user",
                    "content": context_prompt
                }
            ],
            model = "llama-3.1-8b-instant"
        )

        #update tokens used
        INPUT_TOKENS = INPUT_TOKENS + chat_completion.usage.prompt_tokens
        OUTPUT_TOKENS = OUTPUT_TOKENS + chat_completion.usage.completion_tokens
        #get learning path context
        learning_path_text = chat_completion.choices[0].message.content

        #build current prompt
        prompt = f'''
        Please extract the following information from the given text and return it as a JSON object:

        beginner_description
        beginner_query
        intermediate_description
        intermediate_query
        hard_description
        hard_query
        advanced_description
        advanced_query

        This is the body of text to extract the information from:
        {learning_path_text}
        '''

        #build tool configuration
        tools  = [
            {
                "type": "function",
                "function": {
                    "name": "extract_learning_info",
                    "description": "Extract information from given text and return as JSON object",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "beginner_description": {
                                "type": "string",
                                "description": "Description of what the student is learning in the beginner difficulty level"
                            },
                            "beginner_query": {
                                "type": "string",
                                "description": "The web query the student will use to gather resources for the beginner difficulty level"
                            },
                            "intermediate_description": {
                                "type": "string",
                                "description": "Description of what the student is learning in the intermediate difficulty level"
                            },
                            "intermediate_query": {
                                "type": "string",
                                "description": "The web query the student will use to gather resources for the intermediate difficulty level"
                            },
                            "hard_description": {
                                "type": "string",
                                "description": "Description of what the student is learning in the hard difficulty level"
                            },
                            "hard_query": {
                                "type": "string",
                                "description": "The web query the student will use to gather resources for the hard difficulty level"
                            },
                            "advanced_description": {
                                "type": "string",
                                "description": "Description of what the student is learning in the advanced difficulty level"
                            },
                            "advanced_query": {
                                "type": "string",
                                "description": "The web query the student will use to gather resources for the advanced difficulty level"
                            },
                        },
                        "required": [
                            "beginner_description", "beginner_query",
                            "intermediate_description", "intermediate_query",
                            "hard_description", "hard_query",
                            "advanced_description", "advanced_query"
                        ]
                    }
                }
            }
        ]

        #implement out_json edge case
        out_json = None
        #run process until we have an out_json or less than trials
        while out_json is None:
            print("Building out_json!")
            try:
                #call response
                response = client.chat.completions.create(
                    model = "llama-3.1-8b-instant",
                    messages = [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    tools = tools,
                    tool_choice = "auto"
                )
            except Exception as e:
                print(e)

            #update tokens used
            INPUT_TOKENS = INPUT_TOKENS + response.usage.prompt_tokens
            OUTPUT_TOKENS = OUTPUT_TOKENS + response.usage.completion_tokens

            if response.choices[0].message.tool_calls:
                #get the arguments of the content
                functio_args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
                #run arguments to function
                out_json = extract_learning_info(**functio_args)
                print("Success! Succesfully loaded using tool_calls")
            else:
                #get the content of our response
                content = response.choices[0].message.content

                #get start index of JSON file
                start_index = min([i for i in [content.find("{"), content.find("[")] if i >= 0])
                #get end index of JSON file
                end_index = len(content) - min([i for i in [content[::-1].find("}"), content[::-1].find("]")] if i >= 0])
                #get the entire JSON text
                json_text = content[start_index:end_index]

                try:
                    #load text to json
                    json_response = json.loads(json_text)
                except Exception as e:
                    try:
                        #list of brackets in string
                        brackets = []
                        #mapping of closed brackets to open
                        bracket_map = {
                            "}": "{",
                            "]": "["
                        }
                        #inverse bracket map
                        inverse_map = {v: k for k, v in bracket_map.items()}
                        #save the character index
                        char_index = 0
                        #loop through every character in format string
                        for char in json_text:
                            if char == "}" or char == "]":
                                if brackets[-1] != bracket_map[char]:
                                    #then we must add new bracket
                                    while brackets[-1] != bracket_map[char]:
                                        #add new bracket and remove
                                        json_text = json_text[0:char_index] + inverse_map[brackets[-1]] + json_text[char_index:]
                                        brackets = brackets[:-1]
                                        # print(brackets)
                                    brackets = brackets[:-1]
                                else:
                                    #eliminate brackets
                                    brackets = brackets[:-1]
                            elif char == "{" or char == "[":
                                brackets.append(char)
                            #increment index
                            char_index += 1
                        
                        #handle edge case where last missing bracket is at the end
                        while brackets:
                            json_text = json_text + inverse_map[brackets[0]]
                            brackets = brackets[1:]
                        #load text to json
                        json_response = json.loads(json_text)
                    except Exception as e:
                        print("Failure! Could not load your file to JSON with error", e)  

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
    
    def check_input(build_type, topic, msg):
        if build_type == "Learning Path":
            #list possible learning paths
            possible_topics = ["python", "javascript"]
            #check to see if topic is note empty
            if not topic.strip():
                raise gr.Error("Make sure to include your topic!")
            if topic.lower() not in possible_topics:
                raise gr.Error("Did not recognize topic, make sure to include programming specific topics!")
        else:
            #check tutorial edge cases
            if not msg.strip():
                raise gr.Error("Make sure to input message!")
    
    def clear_all():
        #add build type component
        build_type = gr.Radio(
            ["Learning Path", "Tutorial"],
            label="What do you wish to build today?",
            value=None
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

        return build_type, topic, difficulty, radio, chatbot, msg, clear_button, submit_button
    
    # ---------- Actions ----------
    #handle build type selection
    build_type.select(
        build_layout, build_type, [topic, difficulty, chatbot, msg]
    ).then(
        resource_selection, [build_type, radio], radio
    ).then(
        buttons, [clear_button, submit_button], [clear_button, submit_button]
    )

    #handle user click on clear button
    clear_button.click(
        clear_handle, chatbot, chatbot
    ).then(
        clear_all, None, [build_type, topic, difficulty, radio, chatbot, msg, clear_button, submit_button]
    )

    #handle user click on submit button
    submit_button.click(
        check_input, [build_type, topic, msg], None
    ).success(
        user, [build_type, topic, msg, chatbot], [msg, chatbot]
    ).then(
        bot, [build_type, difficulty, radio, chatbot], chatbot
    )

    #handle topic textbox submit
    topic.submit(
        check_input, [build_type, topic, msg], None
    ).success(
        user, [build_type, topic, msg, chatbot], [topic, chatbot]
    ).then(
        bot, [build_type, difficulty, radio, chatbot], chatbot
    )

    #handle user submit
    msg.submit(
        check_input, [build_type, topic, msg], None
    ).success(
        user, [build_type, topic, msg, chatbot], [msg, chatbot]
    ).then(
        bot, [build_type, difficulty, radio, chatbot], chatbot
    )


if __name__ == "__main__":
    demo.launch(show_error=True)