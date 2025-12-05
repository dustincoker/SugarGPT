# app.py
import gradio as gr
from rag_backend import answer_question

def clear_fn():
    return "", ""

with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align:center;'>SugarGPT</h1>")

    with gr.Row():
        # Left: user_input + buttons
        with gr.Column():
            user_input = gr.Textbox(label="user_input", lines=4, show_label=True)
            with gr.Row():
                clear_btn = gr.Button("Clear")
                submit_btn = gr.Button("Submit")

        # Right: output + flag
        with gr.Column():
            output_box = gr.Textbox(label="output", lines=12, show_label=True)
            flag_btn = gr.Button("Flag")  # you can hook this to a flagging callback later

    submit_btn.click(
        fn=answer_question,
        inputs=user_input,
        outputs=output_box,
    )

    clear_btn.click(
        fn=clear_fn,
        inputs=None,
        outputs=[user_input, output_box],
    )

demo.queue()
demo.launch()
