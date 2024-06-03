# An example LLM chatbot using Cohere API and Streamlit that references a PDF
# Adapted from the StreamLit OpenAI Chatbot example - https://github.com/streamlit/llm-examples/blob/main/Chatbot.py

import streamlit as st
import cohere
import fitz # An alias for PyMuPDF

def pdf_to_documents(pdf_path):
    """
    Converts a PDF to a list of 'documents' which are chunks of a larger document that can be easily searched 
    and processed by the Cohere LLM. Each 'document' chunk is a dictionary with a 'title' and 'snippet' key
    
    Args:
        pdf_path (str): The path to the PDF file.
    
    Returns:
        list: A list of dictionaries representing the documents. Each dictionary has a 'title' and 'snippet' key.
        Example return value: [{"title": "Page 1 Section 1", "snippet": "Text snippet..."}, ...]
    """

    doc = fitz.open(pdf_path)
    documents = []
    text = ""
    chunk_size = 1000
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        part_num = 1
        for i in range(0, len(text), chunk_size):
            documents.append({"title": f"Page {page_num + 1} Part {part_num}", "snippet": text[i:i + chunk_size]})
            part_num += 1
    return documents

# Add a sidebar to the Streamlit app
with st.sidebar:
    if hasattr(st, "COHERE_API_KEY"):
        cohere_api_key = st.secrets["COHERE_API_KEY"]
        # st.write("API key found.")
    else:
        cohere_api_key = st.text_input("Cohere API Key", key="lCJHRdySFOQmCMrb6cD4QUQbMwev3ldgJwa6srCu", type="password")
        st.markdown("[Get a Cohere API Key](https://dashboard.cohere.ai/api-keys)")
    
    my_documents = []
    # selected_doc = st.selectbox("Enter your response:", ["Tai Tam Middle School", "Repulse Bay"])
    # if selected_doc == "lang":
    #     my_documents = pdf_to_documents('docs/HKISTaiTamBusSchedule.pdf')
    # elif selected_doc == "Repulse Bay Bus Schedule":    
    #     my_documents = pdf_to_documents('docs/HKISRepulseBayBusSchedule.pdf')
    # else:
    #     my_documents = pdf_to_documents('docs/HKISTaiTamBusSchedule.pdf')

    # st.write(f"Selected document: {selected_doc}")
my_documents += pdf_to_documents('docs/lang.pdf')
my_documents += pdf_to_documents('docs/RUBRIC.pdf')

print(my_documents)

# Set the title of the Streamlit app
st.title("📚 2023 AP LANGUAGE & COMPOSITION FRQ ESSAY GRADER")

# Initialize the chat history with a greeting message
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "text":"Please enter your sample response to the synthesis essay prompt from the AP English Language & Composition exam from 2023: "}]

# Display the chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["text"])

# Get user input
if prompt := st.chat_input():
    # Stop responding if the user has not added the Cohere API key
    if not cohere_api_key:
        st.info("Please add your Cohere API key to continue.")
        st.stop()

    # Create a connection to the Cohere API
    client = cohere.Client(api_key=cohere_api_key)
    
    # Display the user message in the chat window
    st.chat_message("user").write(prompt)

    preamble = """ You are the AP Grader Bot. You help people by grading their work according to College Board's Advanced Placement test guidelines and rubrics. 
    Using the essay prompt document and the rubric document provided to you, you will grade the input, which is the student's essay, on a scale of 0-6. 
    No points are deducted for an answer, but they may only be added if they fulfill the requirements in the rubric according to the documents.
    Respond with advice on what the student should add and remove from their essay, as well as how they can improve the essay to meet the requirements of getting all the points on the rubric. 
    Finish with some words of encouragement and some more remarks about their essay to help the student improve it. 
    
    """

    # Send the user message and pdf text to the model and capture the response
    response = client.chat(chat_history=st.session_state.messages,
                           message=prompt,
                           documents=my_documents,
                           prompt_truncation='AUTO',
                           preamble=preamble)
    
    # Add the user prompt to the chat history
    st.session_state.messages.append({"role": "user", "text": prompt})
    
    # Add the response to the chat history
    msg = response.text
    st.session_state.messages.append({"role": "assistant", "text": msg})

    # Write the response to the chat window
    st.chat_message("assistant").write(msg)