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
from langchain.prompts import PromptTemplate


open_api_key = "insert OPENAI_API_KEY here"
os.environ["OPENAI_API_KEY"] = open_api_key
openai.api_key = open_api_key
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
    Chroma.from_documents(data, embedding_function, persist_directory=chroma_db_path)
    return redirect('/')


@csrf_exempt
def chat_interface(request):
    empty_question = False
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        if 'stage' in request.session:
            if request.session['stage'] == 0:
                response = bot_llm_call(user_input)
            else:
                if request.session['stage'] == 5:
                    empty_question = True
                response = chatbot(request, user_input)
        else:
            response = chatbot(request, user_input)
            ########################
            if not response:
                response = "I don't Understand, Please Elaborate More!!!"
                # return redirect('/')
            ########################
        if empty_question:
            qa = QuestionAnswer()
            qa.question = ""
            qa.answer = response
            qa.save()
            response = bot_llm_call(user_input)
        qa = QuestionAnswer()
        qa.question = user_input
        qa.answer = response
        qa.save()
        return redirect('/')
    chats = QuestionAnswer.objects.all()
    return render(request, 'chatbot1.html', locals())


def bot_llm_call(question):
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
    response = qa.run(question)
    return response


def chatbot(request, input_text):
    input_text = input_text.lower()
    words = word_tokenize(input_text)
    print(input_text, 'starting---', words)

    if any(word.lower() in words for word in ["hi", "hii", "hello", "helo", "hey"]) and 'stage' not in request.session:
        print("1st if --------")
        response = "How are you?"
        request.session['stage'] = 1

    #############
    elif 'stage' not in request.session:
        return False
    ###############

    elif input_text in ["i am not fine", "not good", "not great", "not well"] and \
            request.session['stage'] <= 1:
        print("2nd if -------")
        response = "Okay, Can I get your name please"
        request.session['user_name'] = 1
        request.session['stage'] = 2

    elif input_text in ["i am fine", "good", "great", "fit as fiddle"] and request.session['stage'] <= 1:
        print("3rd if ---------")
        response = "Great, Can I get your name please"
        request.session['user_name'] = 1
        request.session['stage'] = 2

    elif "my name is" in input_text and request.session['stage'] <= 2:
        print("4th if ---------")
        user_name = input_text.split("my name is")[1].strip()
        response = f"Nice to meet you, {user_name}! Would you like to know more about Avasana's data protection policy?"
        request.session['stage'] = 3

    elif any(word.lower() in words for word in ["no", "dont", "don't", "i dont", "i don't"]) and request.session['stage'] <= 2:
        print("4th if ---------")
        user_name = input_text.split("my name is")[1].strip()
        response = f"Okay! Would you like to know more about Avasana's data protection policy?"
        request.session['stage'] = 3

    elif 'user_name' in request.session and request.session['stage'] <= 2:
        response = f"Hello, {input_text}! Would you like to know more about Avasana's data protection policy?"
        del request.session['user_name']
        request.session['stage'] = 3

    elif input_text.lower() in ["yes", "please", "i'm in", "that sounds good", "sure", "absolutely", " of course"] and \
            request.session['stage'] <= 3:
        response = ("You can find detailed information about our privacy policy by visiting this link: "
                    "<a target='_blank' href='https://avasana.app/privacy-policy/'>https://avasana.app/privacy-policy"
                    "</a>. Does this answer your question and provide the information you were looking for? Is there "
                    "anything else you'd like to know or any next steps you'd like to take?")
        request.session['stage'] = 4

    elif input_text.lower() in ["no", "i don't", "i dont", "i'm not", "i am not"] and request.session['stage'] <= 3:
        print("5th if --------")
        response = ("Alright, do you have any other queries about using Avasana? If not, I 'm quite curious to know "
                    "what' s brought you here today.")
        request.session['stage'] = 5

    elif request.session['stage'] == 4:
        response = ("Alright, do you have any other queries about using Avasana? If not, I 'm quite curious to know "
                    "what' s brought you here today.")
        request.session['stage'] = 5

    elif request.session['stage'] == 5:
        response = ("""Before we get into the details, I'd like to give you a brief overview of how you can make the most of Avasana to meet your specific needs.<br><br>

Option 1: Single Sessions - If you're currently facing a challenging situation and require immediate guidance, you have the choice to schedule single, on-the-spot check-ins.<br><br>

Option 2: Ongoing Support - If your goal is to make significant improvements in your life and overall well-being, it's advisable to participate in regular sessions spanning several weeks.""")
        request.session['stage'] = 0
    else:
        print("in else -------------------")
        if request.session['stage'] == 1:
            response = chatbot(request, 'not good')
        elif request.session['stage'] == 2:
            response = chatbot(request, 'good')
        elif request.session['stage'] == 3:
            response = "Would you like to know more about Avasana's data protection policy?"
        elif request.session['stage'] == 4:
            request.session['stage'] = 5
            response = chatbot(request, input_text)
        elif request.session['stage'] == 5:
            response = chatbot(request, "Final")
        else:
            response = chatbot(request, "hi")
        return response

    return response


def chat_clear(request):
    qa = QuestionAnswer.objects.all()
    qa.delete()
    if 'stage' in request.session:
        del request.session['stage']

    if 'user_name' in request.session:
        del request.session['user_name']
    return redirect('/')
