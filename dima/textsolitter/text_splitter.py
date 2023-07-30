# SoMaJo is a state-of-the-art tokenizer and sentence splitter for German and English web and social media texts.
# It won the EmpiriST 2015 shared task on automatic linguistic annotation of computer-mediated communication / social media.
# As such, it is particularly well-suited to perform tokenization on all kinds of written discourse,
# for example chats, forums, wiki talk pages, tweets, blog comments, social networks, SMS and WhatsApp dialogues.
# In addition to tokenizing the input text, SoMaJo can also output token class information for each token,
# i.e. if it is a number, an emoticon, an abbreviation, etc.:
# echo 'Wow, superTool!;)' | somajo-tokenizer -c -t -
# Wow	regular
# ,	symbol
# super	regular
# Tool	regular
# !	symbol
# ;)	emoticon

# somoja api https://github.com/tsproisl/SoMaJo/blob/master/doc/build/markdown/somajo.md
# SoMaJo can be easily installed using pip (pip3 in some distributions):
#
# pip install -U SoMaJo
# Alternatively, you can download and decompress the latest release or clone the git repository:
#
# git clone https://github.com/tsproisl/SoMaJo.git
# 


from somajo import SoMaJo
import re

def merge_short_sentences(sentences, chunk_size):
    short_sentences = []
    for i, sentence in enumerate(sentences):  # The sentence is too long and needs to be split again
        short_sentences.append(sentence)
        if len(''.join(short_sentences)) > chunk_size:
            return sentences[:i], sentences[i:]
    return sentences, []

def textsplitter_with_overlap(sentences, chunk_size=64, chunk_overlap_rate=0.1):
    """

    :param sentences: sentences = split_sentence(text)
    :param chunk_size:
    :param chunk_overlap_rate:
    :return:
    """
    chunk_overlap = int(chunk_size * chunk_overlap_rate)

    result = []
    while sentences:
        merge_sentences, sentences = merge_short_sentences(sentences, chunk_size)
        # result.append(merge_sentences)
        result.append(''.join(merge_sentences))

        if not sentences:
            break

        overlap_sentences = merge_short_sentences(merge_sentences[::-1], chunk_overlap)[0][::-1]

        if len(''.join(overlap_sentences)) + len(sentences[0]) > chunk_size:  # 丢弃重叠部分
            continue

        sentences = overlap_sentences + sentences  # 新句子集合
    return result

# language ({'de_CMC', 'en_PTB'}) – Language-specific tokenization rules.
# split_camel_case (bool, (default=False)) – Split words written in camelCase (excluding established names and terms).
# split_sentences (bool, (default=True)) – Perform sentence splitting in addition to tokenization.
# xml_sentences (str, (default=None)) – Delimit sentences by XML tags of this name (xml_sentences='s' → <s>…</s>). When used with XML input, this might lead to minor changes to the original tags to guarantee well-formed output (tags might need to be closed and re-opened at sentence boundaries).

class SoMaJo_Text_Splitter(object):
    def __init__(self, split_sentences=True):
        self.split_sentences = split_sentences
        self.front_brackets_list = {"(", "（", "<", "《", "{", "[", "【"}
        self.back_brackets_list  = {")", "）", ">", "》", "}", "]", "】"}
        self.quote_list = {"'", "“"}
        self.punches_fine_grained = {",", ";", ".", "!", "?", "\r", "\n"}

    def __call__(self, text, criterion='coarse'):
        text = text.replace("\n\n", " ")
        text = text.strip()  # If there is a redundant \n at the end of the paragraph, remove it
        _text = [i for i in text.split("\n") if i]  # merge the texts

        tokenizer = SoMaJo(language='en_PTB', split_sentences=True)
        sentences = tokenizer.tokenize_text(_text)

        final_sentences = []
        brackets_flag = False
        quote_counter = 0

        # sentences is a generator
        for sentence in sentences:
            current_sentence = ""
            for sen in sentence:
                if sen.token_class == 'symbol':
                    if sen.text in self.front_brackets_list:
                        if not brackets_flag:
                            brackets_flag = True
                            sen.text = " " + sen.text
                    if sen.text in self.back_brackets_list:
                        brackets_flag = False

                    # count the number of quote, the odd quote is required a space
                    if sen.text in self.quote_list:
                        quote_counter += 1
                        if quote_counter %2 == 1:
                            quote_counter = 1
                            sen.text = " " + sen.text

                    current_sentence += sen.text

                    if criterion == 'fine':
                        if sen.text in self.punches_fine_grained:
                            current_sentence = current_sentence.strip()
                            final_sentences.append(current_sentence)
                            current_sentence = ""
                            continue

                else:
                    if sen.text.find("'") != -1:
                        current_sentence += sen.text
                    else:
                        if brackets_flag:
                            current_sentence += sen.text
                            brackets_flag = False

                        else:
                            # indent space between quotes and texts
                            if current_sentence and current_sentence[-1] in self.quote_list:
                                current_sentence += sen.text
                            else:
                                current_sentence += " " + sen.text

            current_sentence = current_sentence.strip()
            # exclude the void string
            if len(current_sentence):
                final_sentences.append(current_sentence)

        return final_sentences




split_sentence = SoMaJo_Text_Splitter()

if __name__ == '__main__':
    text =" Uncle Tom's Cabin; or, Life Among the Lowly is an anti-slavery novel by American author Harriet Beecher Stowe. Published in two volumes in 1852, the novel had a profound effect on attitudes toward African Americans and slavery in the U.S., and is said to have helped lay the groundwork\
 for the [American Civil[] War]. In the same month, American singer (Madonna) released the single 'Hung Up Song', which contains a sample of the keyboard melody from ABBA's 1979 song 'Gimme! Gimme! Gimme!'"

    sentences = split_sentence(text, criterion='fine')
    print(sentences)