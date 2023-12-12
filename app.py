from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from openai import OpenAI

def main():
    # Create header
    st.header("Ask Goals Database 💬")

    # Load user_goals
    df = pd.read_csv('user_goals.csv')

    st.sidebar.header("Filter")

    # Set Streamlit elements (sidebar sliders)
    threshold = st.sidebar.slider("Select Minimum Match Rating", 50, 100, 50)
    number_matches = st.sidebar.slider("Select Number of Matches", 1, 10, 3)
    temperature = st.sidebar.slider("Select Temperature", 0.0, 1.0, 0.1)
    token_output = st.sidebar.slider("Select Token Output Number", 1, 100, 20)
    
    # Show database
    st.sidebar.header("Goals Database")
    st.sidebar.write(df.drop(columns=['index']))
    
    
    # Create subheader that displays question
    st.subheader("Parameters")
    
    # Create elements variable
    element7 = st.text_input('Enter input 1 here:', value= "Return a number out of 100 that reflects how well the two goals relate.")
    element8 = st.text_input('Enter input 2 here:', value =  "Do not return words")
    element9 = st.text_input('Enter input 3 here:', value = 'Only return a number')
    element10 = st.text_input('Enter input 4 here:', value = '')


    # Combine elements that are not empty into one string, seperate by line
    elements = ""
    for element in [element7, element8, element9, element10]:
        if element != "":
            #seperate by line
            elements += element + "\n"
    
    # Create subheader that displays goal
    st.subheader("Goal")
    
    # Goal input
    goal = st.text_input('Enter goal here:',value="")  # Replace with actual user input
    
    # Create subheader that displays question
    st.subheader("All Parameters")
    
    # Text input question
    question = (st.text_area('All Inputs:',value= elements,
            height= 200)
                )
    if goal != "":
        # Instantiate the OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Function to compare similarity synchronously between the target sentence and each row in the DataFrame
        def calculate_similarity(row):
            prompt_text = f"{question} +Similarity between {goal} and {row['goals']}?"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt_text}],
                temperature= temperature,
                max_tokens= 20  # Adjust the number of tokens for the desired length of response
            )   
            return response.choices[0].message.content

        # Calculate similarity for each row in the DataFrame
        def process_dataframe(df):
            similarity_scores = []
            for index, row in df.iterrows():
                similarity_score = calculate_similarity(row)
                similarity_scores.append(similarity_score)

            df['similarity_score'] = similarity_scores
            print(df)

        # Execute the process_dataframe function
        process_dataframe(df)
        
        st.write(df)

        # Grab just numeric values from similarity_score
        df['similarity_score'] = df['similarity_score'].str.extract('(\d+)')
        
        # Try to Convert 'similarity_score' column to float
        try:
            df['similarity_score'] = df['similarity_score'].astype(int)
        except:
            pass

        # Display top matches
        st.header(f"Top {number_matches} Matches")
        
        # Convert threshold to int
        threshold = int(threshold)
        
        st.write(df)
        
        # Drop na values in similiarity_score column
        df = df.dropna(subset=['similarity_score'])
        
        # Convert similarity_score to int
        df['similarity_score'] = df['similarity_score'].astype(int)
    
        # create matches dataframe, limiting similarity score to threshold
        matches = df['similarity_score'] >= threshold
        
        # Order matches by similarity score and limit to number_matches
        matches = df.sort_values(by=['similarity_score'], ascending=False).head(number_matches)
        
        st.write(matches)
        
        for i in range(len(matches)):
            st.header(f"Match {i + 1}")
            st.write(f"Match ID Number: {str(matches.iloc[i, 0])}")
            st.write(f"Match Name: {str(matches.iloc[i, 1])}")
            st.write(f"Match Strength Rating: {str(matches.iloc[i, 3])}")
            st.write(f"Match Goal: {str(matches.iloc[i, 2])}")

if __name__ == '__main__':
    main()
