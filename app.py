import streamlit as st 
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer,WordNetLemmatizer
from nltk import word_tokenize
import re
import pandas as pd
import contractions
import inflect
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from tabulate import tabulate

pickle_in = open("model_sentiment.pkl", 'rb') 
model_sentiment = pickle.load(pickle_in)

pickle_in_tdidf = open("model_sentiment_tfidf.pkl", 'rb') 
model_tfidf = pickle.load(pickle_in_tdidf)

def main():
	st.title("Sentiment Analysis NLP")
	st.subheader("Analyze Amazon product reviews as positive or negative")

if __name__ == '__main__':
	main()
    
stop_words = stopwords.words('english') # remove stop words

def get_percentage(num):
    return "{:.2f}%".format(num*100)

def number_to_text(data):
    temp_str = data.split()
    string = []
    for i in temp_str:

    # if the word is digit, converted to
    # word else the sequence continues

        if i.isdigit():
            temp = inflect.engine().number_to_words(i)
            string.append(temp)
        else:
            string.append(i)
    outputStr = " ".join(string)
    return outputStr

ps = PorterStemmer()
def stem_text(data):
    tokens = word_tokenize(data)
    stemmed_tokens = [ps.stem(word) for word in tokens if word not in (stop_words)]
    return " ".join(stemmed_tokens)

lemma = WordNetLemmatizer()
def lemmatiz_text(data):    
    tokens = word_tokenize(data)
    lemma_tokens = [lemma.lemmatize(word, pos='v') for word in tokens if word not in (stop_words)]
    return " ".join(lemma_tokens)

def cleantext(text):
    text = re.sub(r'[^\w\s]', " ", text) # Remove punctuations
    text = re.sub(r"https?:\/\/\S+", ",", text) # Remove The Hyper Lin
    text = contractions.fix(text) # remove contractions 
    text = number_to_text(text) # convert numbers to text    
    text = text.lower() # convert to lower case
    # don't feel it's worth to use stemming as it may lead to some wrong words
    text = lemmatiz_text(text) # lemmatization
    return text

   
amazonreviewText = st.text_area('Enter the amazon product review text', '')

if st.button("Analyze"):
    cleanReviewText = cleantext(amazonreviewText)
    #st.write(cleanReviewText)    
    tfIdfText = model_tfidf.transform([cleanReviewText])
    predictedVal=model_sentiment.predict(tfIdfText)
    predictedVal= predictedVal[0]
    #st.write(type(predictedVal))
    
    st.markdown("""
        <style>
        .big-font {
            font-size:20px !important;
        }
        
        </style>
        """, unsafe_allow_html=True)
    
    finalPrediction = "The review is positive 😀" if predictedVal=="1" else "The review is negative 😔"
      
    st.markdown("<p class='big-font'>{}</p>".format(finalPrediction),unsafe_allow_html=True)
    
           
    prdictionDist = model_sentiment._predict_proba_lr(tfIdfText)

    dfRes = pd.DataFrame(columns=['Negative', 'Positive'])
    dfRes.loc[1, 'Negative'] = get_percentage(prdictionDist[0][0])
    dfRes.loc[1, 'Positive'] = get_percentage(prdictionDist[0][1])

    # CSS to inject contained in a string
    hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """
    # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

    st.dataframe(dfRes)

    
    
    
