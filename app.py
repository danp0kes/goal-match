from dotenv import load_dotenv
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import pandas as pd
import re


def main():
    load_dotenv()
    st.set_page_config(page_title="Ask your PDF")
    st.header("Ask Goals Database 💬")
    
    #load user_goals
    user_goals = pd.read_csv('user_goals.csv')
      
      # load text
    with open('user_goals.txt') as f:
        text = f.read()
      
      # split into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=100,
        chunk_overlap=20,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
      
    # create embeddings
    embeddings = OpenAIEmbeddings()
    knowledge_base = FAISS.from_texts(chunks, embeddings)
    
    # Create threshold as streamlit slider, have two endpoints 0 and 100, start at 50, and step by 1
    threshold = st.slider("match_rating", 0, 100, (25,75), 1)
    
    # show user input
    goal = st.text_input("Input Goal:")
    if goal != "":
        docs = knowledge_base.similarity_search(goal)
        llm = OpenAI()
        chain = load_qa_chain(llm, chain_type="stuff")
        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=f("""Find the best 3 matches. Give the best one 
                                 first with the matches ID number along with a match rating out of 100. Give rating 
                                 levels to an specific integer, not just a factor of 10. Then give me the second best match. 
                                 Goals may be identical. Goals must be directly inline including the action and the overall benefit. 
                                 For instance, Don't match 'learning to play an instrument' with 'crafting an instrument' because one 
                                 is about learning music and the other is about learning how to make an instrument.If any have a rating 
                                 lower than {threshold}, skip. Only return numbers, Do not return names." + goal"""))
            print(cb)
        
        if not re.search(r'\d', response):
            st.write("No number found.")
            return
            
        else:
            st.write(f"Answer: {response}")
            
            numbers = re.findall(r'\b\d+\b', response)
            id = numbers[0]
                
            if id == "":
                id= 'No ID Match'
                    
            # Create first match header
            st.header('Match 1')

            # show match id
            st.write(f"Match ID Number: {id}")
                
            # Check if id is not an empty string before converting to int
            if id and id.strip():
                try:
                    id_int = int(id)
                    if 0 <= id_int < len(user_goals):
                        matches_names = user_goals.iloc[id_int, 1]
                        #show match name
                        matches_names = user_goals.iloc[int(id), 1]
                        st.write(f"Match Name: {matches_names}")
                        #select second number from answer for rating
                        rating = numbers[1]
                        st.write(f"Match Strength Rating: {rating}")
                            
                    else:
                        st.write("ID is out of range")
                except ValueError:
                    st.write("Invalid ID")
            else:
                st.write("No ID provided")
                
            #show match goal
            matches_goals = user_goals.iloc[int(id), 2]
            st.write(f"Match's Goal: {matches_goals}")
            
            with get_openai_callback() as cb:
                reason = chain.run(input_documents=docs, question="Why is" + matches_names + "a good match for" + goal + "?")
                
            st.write(f"Reason: {reason}")
            
            # Create second match header
            st.header('Match 2')
            
            # show match id
            st.write(f"Match ID Number: {numbers[2]}")
            
            # Save id as variable
            id = numbers[2]
            
            # Check if id is not an empty string before converting to int
            if id and id.strip():
                try:
                    id_int = int(id)
                    if 0 <= id_int < len(user_goals):
                        matches_names = user_goals.iloc[id_int, 1]
                        #show match name
                        matches_names = user_goals.iloc[int(id), 1]
                        st.write(f"Match Name: {matches_names}")
                        #select second number from answer for rating

                        rating = numbers[3]
                        st.write(f"Match Strength Rating: {rating}")
                            
                    else:
                        st.write("ID is out of range")
                except ValueError:
                    st.write("Invalid ID")
            else:
                st.write("No ID provided")
                
            #show match goal
            matches_goals = user_goals.iloc[int(id), 2]
            st.write(f"Match's Goal: {matches_goals}")
            
            # Create third match header
            st.header('Match 3')
            
            # show match id
            st.write(f"Match ID Number: {numbers[4]}")
            
            # Save id as variable
            id = numbers[4]
            
            # Check if id is not an empty string before converting to int
            if id and id.strip():
                try:
                    id_int = int(id)
                    if 0 <= id_int < len(user_goals):
                        matches_names = user_goals.iloc[id_int, 1]
                        #show match name
                        matches_names = user_goals.iloc[int(id), 1]
                        st.write(f"Match Name: {matches_names}")
                        #select third number from answer for rating
                        rating = numbers[5]
                        st.write(f"Match Strength Rating: {rating}")
                            
                    else:
                        st.write("ID is out of range")
                except ValueError:
                    st.write("Invalid ID")
            else:
                st.write("No ID provided")
                
            #show match goal
            matches_goals = user_goals.iloc[int(id), 2]
            st.write(f"Match's Goal: {matches_goals}")

            # show user input
            user_question3 = st.text_input("Question 3:")
            if user_question3:
                st.write(f"Question: {user_question3}")
                answer3 = qa.run(user_question3)
                st.write(f"Answer: {answer3}")
            return
        
        st.write(response)
    
    

if __name__ == '__main__':
    main()
