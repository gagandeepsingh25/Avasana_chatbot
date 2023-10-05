import openai
from django.shortcuts import render, redirect
from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os
from django.views.decorators.csrf import csrf_exempt
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from nltk.tokenize import word_tokenize
from myapp.models import QuestionAnswer
from langchain.document_loaders import DirectoryLoader
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
# from llama_index import LLMPredictor, SimpleDirectoryReader, QuestionAnswerPrompt, GPTVectorStoreIndex, ServiceContext, \
#     VectorStoreIndex
# from llama_index.llms import ChatMessage, MessageRole
from langchain.prompts import PromptTemplate

os.environ["OPENAI_API_KEY"] = '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'
openai.api_key = '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'
chroma_db_path = 'chroma_db'
index_file = os.path.join(chroma_db_path)
if os.path.isfile(chroma_db_path):
    os.remove(chroma_db_path)

text_splitter = RecursiveCharacterTextSplitter(
    # Set a tiny chunk size, just to show.
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    # is_separator_regex=False,
)
embedding_function = OpenAIEmbeddings()
text_loader_kwargs = {'autodetect_encoding': True}


def create_data():
    loader = DirectoryLoader('docs/', glob="**/*", show_progress=True, loader_kwargs=text_loader_kwargs)
    docs = loader.load()
    data = text_splitter.split_documents(docs)
    index_file = Chroma.from_documents(data, embedding_function, persist_directory=chroma_db_path)


# create_data()


# prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
# prompt_helper = QuestionAnswerPrompt(template=temp)
#
# llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=num_outputs))
#
# documents = SimpleDirectoryReader(directory_path).load_data()
# # print(documents,'documents------------------------------------------------------------------')
# service_context = ServiceContext.from_defaults(
#     llm=OpenAI(model="gpt-3.5-turbo", temperature=0.8)
# )
# index = VectorStoreIndex.from_documents(documents, service_context=service_context, show_progress=True)

# index = GPTVectorStoreIndex(documents, llm_predictor=llm_predictor)

# index.save_to_disk(index_file)
#
# # # Text QA Prompt
# # chat_text_qa_msgs = [
# #     ChatMessage(
# #         role=MessageRole.SYSTEM,
# #         content="""your name is Sophia Bennet and you are a conversational chatbot which answer like a normal human.
# #         Reply answers as a normal human conversation. Use context for external knowledge. If you dont know the answer
# #         just say %I am here to help you with information about Avasana. Please ask your question, and I will do my
# #         best to assist you.% Always answer the question like natural conversation, even if the context isn't helpful.""",
# #     )
# # ]
#
#
# # Text QA Prompt
# chat_text_qa_msgs = [
#     ChatMessage(
#         role=MessageRole.SYSTEM,
#         content="""your name is Sophia Bennet and you are a conversational chatbot which answer like a normal human.
#         Reply answers as a normal human conversation. Use context for external knowledge. If you dont know the answer
#         just say %I am here to help you with information about Avasana. Please ask your question, and I will do my
#         best to assist you.% Always answer the question like natural conversation, even if the context isn't helpful""",
#     )
# ]
#
# # Refine Prompt
# chat_refine_msgs = [
#     ChatMessage(
#         role=MessageRole.SYSTEM,
#         content="""your name is Sophia Bennet and you are a conversational chatbot which answer like a normal human.
#         Reply answers as a normal human conversation. Use context for external knowledge. If you dont know the answer
#         just say %I am here to help you with information about Avasana. Please ask your question, and I will do my
#         best to assist you.% Always answer the question like natural conversation, even if the context isn't helpful.""",
#     ),
#     ChatMessage(
#         role=MessageRole.USER,
#         content=(
#             "We have the opportunity to refine the original answer "
#             "(only if needed) with some more context below.\n"
#             "------------\n"
#             "{context_msg}\n"
#             "------------\n"
#             "Given the new context, refine the original answer to better "
#             "answer the question: {query_str}. "
#             "If the context isn't useful, output the original answer again.\n"
#             "Original Answer: {existing_answer}"
#         ),
#     ),
# ]
#
# p_content = """your name is Sophia Bennet and you are a conversational chatbot which answer like a normal human.
# Reply answers as a normal human conversation. Use context for external knowledge. If you dont know the answer
# just say %I am here to help you with information about Avasana. Please ask your question, and I will do my
# best to assist you.% Always answer the question like natural conversation, even if the context isn't helpful."""
# refine_template = ChatPromptTemplate.from_template(p_content)
# text_qa_template = ChatPromptTemplate.from_template(p_content)
#
# print(
#     index.as_query_engine().query("what is your name?")
# )


@csrf_exempt
def chat_interface(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        response = chatbot(request, user_input)
        # response = chatbot(user_input)
        qa = QuestionAnswer()
        qa.question = user_input
        qa.answer = response
        qa.save()
    chats = QuestionAnswer.objects.all()
    return render(request, 'chatbot1.html', locals())


# def chat_new(qes):
#     prompt_template = """your name is Sophia Bennet and you are a conversational chatbot which answer like a normal
#     human. Reply answers as a normal human conversation. in context, we have questions and answers in alternate way
#     of User and Chatbot respectively. You will pick the exact answer from the context Use context for external
#     knowledge. If you dont know the answer just say: /I am here to help you with information about Avasana. Please
#     ask your question, and I will do my best to assist you./ Always answer the question like natural conversation,
#     even if the context isn't helpful. .
#
#     {context}
#
#     Question: {question}
#     Answer in English:"""
#     prompt = PromptTemplate(
#         template=prompt_template, input_variables=["context", "question"]
#     )
#     chain_type_kwargs = {"prompt": prompt}
#
#     index_file = Chroma(persist_directory=chroma_db_path, embedding_function=embedding_function)
#     qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0.4), chain_type="stuff",
#                                      chain_type_kwargs=chain_type_kwargs,
#                                      retriever=index_file.as_retriever()
#                                      )
#
#     # res = conversation.predict(input="what is your name")
#     result = qa.run(qes)
#
#     print(result)
#     return result
#     # tools = load_tools(
#     #     ["human"]
#     # )
#     #
#     # agent_chain = initialize_agent(
#     #     tools,
#     #     ChatOpenAI(temperature=1.0),
#     #     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     #     verbose=True,
#     # )
#     # agent_chain.run("What's my friend Eric's surname?")


def chatbot(request, input_text):
    print(input_text, 'kkk', len(input_text))
    input_text = input_text.lower()
    words = word_tokenize(input_text)
    print(words)

    if 'user_name' in request.session:
        print(request.session['user_name'], "---------uuu")

    # Check if the user is providing their name (using "my name is" or just "name")
    if "my name is" in input_text:
        print("1st if")
        user_name = input_text.split("my name is")[1].strip()
        response = f"Nice to meet you, {user_name}! Would you like to know more about Avasana's data protection policy?"


    elif 'user_name' in request.session and any(word not in words for word in ["hi", "hello"]):
        if request.session['user_name'] == 1:
            response = f"Hello, {input_text}! Would you like to know more about Avasana's data protection policy?"
            del request.session['user_name']

    elif any(word in words for word in ["hi", "hello"]):
        print("3rd if --- ")
        response = "Hello! What's your name?"
        request.session['user_name'] = 1
        print(request.session['user_name'], 'jhhh')

    # elif any(word in words for word in ["hi", "hello"]):
    #     print("3rd if --- ")
    #     response = "Hello! What's your name?"
    #     request.session['user_name'] = 1
    #     print(request.session['user_name'], 'jhhh')

    elif "yes" in input_text or "yes sure" in input_text:
        if 'proceed' not in request.session:

            print("4rd if --- ")
            response = "You can read more about our privacy policy here: https://avasana.app/privacy-policy/. Does that help clarify things? Do you have any further questions or are you ready to proceed?"
            request.session['proceed'] = 1
            print(request.session['proceed'], 'mllll')

        else:
            response = "Ok,Do you have any more questions on how to use Avasana? Otherwise, I am really curious to hear what brings you here today."

    elif input_text.startswith("No") or input_text.startswith("no"):
        response = "Ok,Do you have any more questions on how to use Avasana? Otherwise, I am really curious to hear what brings you here today......"

        if "proceed" in request.session:
            del request.session['proceed']


    # Handle responses to proceeding
    # elif any(word in words for word in ["want to proceed", "yes sure", "yes","proceed"]):
    elif "want to proceed" in input_text or "proceed" in input_text:
        print("5th if --- ")
        response = "Do you have any more questions on how to use Avasana? Otherwise, I am really curious to hear what brings you here today."



    # Handle responses to wanting to know how to use Avasana
    elif "how to use avasana" in input_text:
        print("6th if --- ")
        response = (
            "Before we dive into the specifics, let me quickly inform you about how you can use Avasana to "
            "best suit your needs. \nOption 1: Single Sessions - If you're going through a challenging moment "
            "and need immediate guidance, you can opt for single, spontaneous check-ins. Option 2: Ongoing "
            "Support - If you're looking to make substantial changes in your life and well-being, "
            "it's recommended that we engage in regular sessions over the course of several weeks."
        )

    # # Handle other types of questions
    # elif any(word in words for word in ["what", "how", "why", "when", "where", "who"]):
    #     response = "I'm here to help you with information about Avasana. Please ask your question, and I'll do my best to assist you."

    else:
        # print("else --- ")
        # index = GPTSimpleVectorIndex.load_from_disk(index_file)
        # output = index.query(input_text, response_mode="compact")
        # response = output.response
        # print(output)
        # print(response, 'jjjjj')

        prompt_template = """your name is Sophia Bennet and you are a conversational chatbot which answer like a normal 
           human. Reply answers as a normal human conversation. in context, we have questions and answers in alternate way 
           of User and Chatbot respectively. You will pick the exact answer from the context Use context for external 
           knowledge. If you dont know the answer just say: /I am here to help you with information about Avasana. Please 
           ask your question, and I will do my best to assist you./ Always answer the question like natural conversation, 
           even if the context isn't helpful. .

           {context}

           Question: {question}
           Answer in English:"""
        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": prompt}

        index_file = Chroma(persist_directory=chroma_db_path, embedding_function=embedding_function)
        qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0.4), chain_type="stuff",
                                         chain_type_kwargs=chain_type_kwargs,
                                         retriever=index_file.as_retriever()
                                         )

        response = qa.run(input_text)


    return response


def chat_clear(request):
    qa = QuestionAnswer.objects.all()
    qa.delete()
    return redirect('/')
