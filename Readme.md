# Introduction
> This ChatBot serves Students as an AI-Assistant. It can help with general univerity tasks like moodle exercises or more specific ones like computer science tasks. For now the app only supports usage by htw-berlin students.

# Instruction on how to get the application to run
1. Create a virtual environment with Python 3.11
2. Install the requirements (note that [requirements.txt](requirements.txt) is for mac and [requirementsWindows](requirementsWindows.txt) is for windows).
3. Install Ollama and download `llama3:instruct`, `codellama:13b`, `sqlcoder:latest`
4. Start Ollama with `ollama -serve`
5. Start the backend with PyCharm [Main](BE/Rest API/main.py)
6. Start the frontend using this command: 
```shell script
$ streamlit run FE/streamlit_app.py
```

# Instructions on how to use the application
1. When on the signup page make sure to fill in your Matrikelnummer in the following format: "s0XXXXXX".
   Also make sure you fill in a valid htw e-mail and password. When choosing your personal password note that it
   must be at least eight characters long.
2. When logging in use your Matrikelnummer and your self chosen password as credentials.
3. Choose an agent/tool.
4. You can create a chat if you want, otherwise our AI will create one for you and generate a fitting title.
5. Chat with our AI (for the best performance use english)
6. When chatting you can freely switch between agents/tools and select the best fitting. The next prompt will be sent to
   the corresponding agent/tool. An exception to this is the LSF-tool since it is not a chat interface.

# *Use-Cases*
1. The user registers himself on the signup page and logs in. After that he uses the LSF tool and selects six modules he
   wants to book for the coming semester. The application calculates the optimal schedule for this module combination
   and returns it as a table.
2. The user logs in, selects the Moodle tool and asks for the upcoming assignments. The application returns all future
   assignments listed on the Moodle page of the user.
3. The user logs in, selects the coding tool and requests the generation of an HTML demo which is then provided by the application.

# *Services*
### General Agent - llama3:instruct
1. [E-Mail Service (ChromeDB)](BE/Services/mailservice.py)
2. [Wikipedia - Langchain](BE/AI/llm.py)
3. [DuckDUckGo - Langchain](BE/AI/llm.py)
4. [Youtube - Langchain](BE/AI/llm.py)

### Coding Agent - codellama:13b
1. [GitHub Access](BE/AI/llm.py)
2. [python_repl - Lanchain](BE/AI/llm.py)
3. [SQL LLM](BE/AI/llm.py)

### PDF - llama3:instruct
1. [Query PDFs which are already inside our Backend](BE/Services/Pdf_service)

### Moodle Agent - llama3:instruct
1. [get all moodle tasks were time is left](BE/Services/moodle_service.py)

### LSF - llama3:instruct
1. [Calculate the optimal schedule of chosen modules ](BE/Services/lsf_service.py)
   - travel time is not taken into account 

# Error handling
1. If an agent fails the execution of a prompt the prompt will be given to llama3 (without methods)
2. The frontend resends each request if there is a server error
3. If you happen to make a mistake while registering you will have to create a new account. If the htw password is
   incorrect you will have to delete the database since the Matrikelnummer which acts as our username is unique.
