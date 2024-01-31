from transformers import T5ForConditionalGeneration, T5Tokenizer
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import textwrap
text = """The iPhone is a revolutionary smartphone developed by Apple Inc. Since its initial release in 2007, it has redefined the way we communicate, work, and stay connected to the digital world. With its sleek design, cutting-edge technology, and intuitive user interface, the iPhone quickly became an iconic device and a global sensation. The iPhone offers a seamless integration of hardware, software, and services, providing users with a powerful and versatile device. Its high-resolution Retina display, powerful processors, and advanced camera capabilities have consistently set new standards in the smartphone industry. The App Store, an ecosystem of millions of applications, allows users to personalize their iPhone experience and access a wide range of utilities, games, and productivity tools. Beyond its impressive hardware and software, the iPhone has played a significant role in shaping modern mobile communication and internet culture. It has revolutionized social media, mobile photography, and mobile payments. Its FaceTime feature enables seamless video calls, while iMessage allows instant messaging between iPhone users. With each new generation, the iPhone continues to push boundaries and introduce innovative features that captivate consumers and fuel technological advancements. From Touch ID to Face ID, from Siri to Augmented Reality (AR), the iPhone remains at the forefront of innovation, consistently setting the bar for smartphones worldwide. The iPhone's impact extends far beyond just being a device; it has become a symbol of status, elegance, and sophistication. Its dedicated user base, known for its loyalty, eagerly anticipates each new model release, showcasing Apple's commitment to delivering excellence. As the iPhone continues to evolve, its influence on modern society is undeniable. It has transformed the way we interact, work, and entertain ourselves, becoming an essential tool in our daily lives. The iPhone's legacy continues to shape the future of mobile technology, leaving an indelible mark on the digital era.
"""


# print(text)
def ext_summary(text1):
    stopwords = list(STOP_WORDS)
    # print(stopwords)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text1)
    # print(doc)
    tokens = [token.text for token in doc]
    # print(tokens)
    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_freq.keys():
                word_freq[word.text] = 1
            else:
                word_freq[word.text] += 1
    # print(word_freq)
    max_freq = max(word_freq.values())
    # print(max_freq)
    for word in word_freq.keys():
        word_freq[word] = word_freq[word] / max_freq
    # print(word_freq)
    sent_tokens = [sent for sent in doc.sents]
    # print(sent_tokens)
    sent_scores = {}
    for sent in sent_tokens:
        for word in sent:
            if word.text in word_freq.keys():
                if sent not in sent_scores.keys():
                    sent_scores[sent] = word_freq[word.text]
                else:
                    sent_scores[sent] += word_freq[word.text]
    # print(sent_scores)
    select_len = int(len(sent_tokens) * 0.3)
    # print(select_len)
    summary = nlargest(select_len, sent_scores, key=sent_scores.get)
    # print(summary)
    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)
    # print(text)
    # print(summary)
    # print("Length of original text ", len(text.split(' ')))
    # print("Length of summary text ", len(summary.split(' ')))
    return summary
# result = ext_summary(text)
# print(result[0])
# print("Length of original text ", result[2])
# print("Length of summary text ", result[3])
def abs_summ(ext_summ):
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    max_chunk_length = 512
    chunks = textwrap.wrap(ext_summ, width=max_chunk_length)
    summaries = []
    for chunk in chunks:
        input_text = "summarize: " + chunk
        input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=max_chunk_length, truncation=True)
        summary_ids = model.generate(input_ids, max_length=100, num_return_sequences=1, early_stopping=True)
        abs_summa = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summaries.append(abs_summa)

    com_summ = " ".join(summaries)
    sentences = com_summ.split('.')
    capitalized_sentences = [sentence.strip().capitalize() + '.' for sentence in sentences if sentence.strip()]
    capitalized_text = ' '.join(capitalized_sentences)
    return capitalized_text, ext_summ, len(ext_summ.split(' ')), len(com_summ.split(' '))

# ext_result = ext_summary(text)
abs_result = abs_summ(text)
# result1 = abs_summ(result[0])
print("Text: ")
print(abs_result[1])
print("Abstractive Summary: ")
print(abs_result[0])
print("Length of text: ")
print(abs_result[2])
print("Length of the summary: ")
print(abs_result[3])
