import re
from typing import List
import torch
from tqdm import tqdm

class Chinese_AliText_Splitter(object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

    def split_text(self, text: str) -> List[str]:
        # The use_document_segmentation parameter specifies whether to use semantic segmentation to segment documents.
        # The document semantic segmentation model adopted here is open sourced by ALI_DAMO nlp_bert_document-segmentation_chinese-base，see paper https://arxiv.org/abs/2107.09278
        # 如If you use the model for document semantic segmentation, you need to install modelscope[nlp]：pip install "modelscope[nlp]" -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html

        text = re.sub(r"\n{3,}", r"\n", text)
        text = re.sub('\s', " ", text)
        text = re.sub(r"\*", '', text)
        text = re.sub(r"\^", '', text)
        text = re.sub("\n\n", "", text)

        from modelscope.pipelines import pipeline

        if torch.cuda.is_available() and self.device.lower().startswith("cuda"):
            p = pipeline(
            task="document-segmentation",
            model='damo/nlp_bert_document-segmentation_chinese-base').to(self.device)
        else:
            p = pipeline(
            task="document-segmentation",
            model='damo/nlp_bert_document-segmentation_chinese-base',
            device="cpu")
        result = p(documents=text)
        sent_list = [i for i in result["text"].split("\n\t") if i]

        return sent_list

class Chinese_text_Splitter(object):
    """ Divide the text into several sentences, mainly considering some logical situations in dealing with quotation marks

    Args:
        text(str): string
        criterion(coarse/fine): Sentence segmentation granularity, two kinds of granularity `coarse` or `fine`,
        `coarse` refers to segmentation according to the period level, `fine` refers to segmentation according to all punctuation,
        Segmentation is performed by fine granularity by default

    Returns:
        list(str): List of sentences after dividing

    Examples:
        text = '中华古汉语，泱泱大国，历史传承的瑰宝。'
        split_sentence = SplitSentence()

        print(split_sentence(text, criterion='fine'))

        # ['中华古汉语，', '泱泱大国，', '历史传承的瑰宝。']

    """

    def __init__(self):
        self.punches_fine_grained = None

    def _prepare(self):
        self.punches_fine_grained = {'…', '...', '\r\n', '，', ',', '。', '.', ';',  '；', ':', '：', '…', '！', '!', '=',
                           '?', '？', '\r', '\n', '“', '”', '‘', '’', '——', '-', '(', ')', '（', '）',
                            '[', ']', '【', '】', '{', '}', '《', '》', '<', '>',
                           }
        self.punches_coarse_grained = {'…',  '。', '.', '！', '!', '？', '?', '\n', '“', '”', '‘', '’'}
        self.front_quote_list = {'“', '‘'}
        self.back_quote_list = {'”', '’'}

        self.punches_coarse_ptn = re.compile('([.。“”…！!?？\n])')
        self.punches_fine_ptn = re.compile('([，：。. ;；“”…！!?？\r\n])')

    def __call__(self, text, criterion='coarse'):

        if self.punches_fine_grained is None:
            self._prepare()

        # initialize text segmentation #
        text = re.sub(r"\n{3,}", "\n", text)
        text = re.sub('\s', ' ', text)
        text = re.sub(r"\*", '', text)
        text = re.sub(r'\$', '', text)
        text = re.sub(r" ", '', text)
        text = re.sub(r"\^", '', text)

        text = text.replace("\n\n", "")

        text = text.strip()  # If there is a redundant \n at the end of the paragraph, remove it
        _text = [i for i in text.split("\n") if i]  # merge the texts

        if criterion == 'coarse':
            tmp_list = self.punches_coarse_ptn.split(_text[0])
        elif criterion == 'fine':
            tmp_list = self.punches_fine_ptn.split(_text[0])

        else:
            raise ValueError('The parameter `criterion` must be '
                             '`coarse` or `fine`.')
        print(tmp_list)
        final_sentences = []
        quote_flag = False

        for sen in tqdm(tmp_list):
            if sen == '' or sen == ' ' or sen == '\n' or sen == '\n\n':
                continue

            if criterion == 'coarse':
                if sen in self.punches_coarse_grained:
                    if len(final_sentences) == 0:  # If the starting character of the text is punctuation
                        if sen in self.front_quote_list:  # If the starting character is a leading quote
                            quote_flag = True
                        final_sentences.append(sen)
                        continue

                    # The following ensures that there must be text and a non-empty string before the current punctuation
                    # If the front quotation mark is special, the following sentence needs to be merged with the front quotation mark, not the previous sentence
                    if sen in self.front_quote_list:
                        if final_sentences[-1][-1] in self.punches_coarse_grained:
                            # There are punctuation points before the front quotation marks, such as periods, quotation marks, etc.
                            # thus start another sentence and merge with this
                            final_sentences.append(sen)
                        else:
                            # There is no terminating punctuation before the front quote, merged with the previous sentence
                            final_sentences[-1] = final_sentences[-1] + sen
                        quote_flag = True

                    else:  # Ordinary symbols, not front quotation marks, are merged with the previous sentence
                        final_sentences[-1] = final_sentences[-1] + sen
                    continue

            elif criterion == 'fine':
                if sen in self.punches_fine_grained:
                    if len(final_sentences) == 0:  # If the starting character of the text is punctuation
                        if sen in self.front_quote_list:  # The starting character is a leading quote
                            quote_flag = True
                        final_sentences.append(sen)
                        continue

                    # The following ensures that there must be text and a non-empty string before the current punctuation
                    # The front quotation mark is special, and the following sentence needs to be merged with the front quotation mark, not the previous sentence
                    if sen in self.front_quote_list:
                        if final_sentences[-1][-1] in self.punches_fine_grained:
                            # # There are punctuation points before the front quotation marks, such as periods, quotation marks, etc.
                            # Thus start another sentence and merge it with this
                            final_sentences.append(sen)
                        else:
                            # There is no terminating punctuation before the front quote, merged with the previous sentence
                            final_sentences[-1] = final_sentences[-1] + sen
                        quote_flag = True

                    else:  # Ordinary symbols, not front quotation marks, are merged with the previous sentence
                        final_sentences[-1] = final_sentences[-1] + sen
                    continue

            if len(final_sentences) == 0:  # The start sentence without punctuation
                final_sentences.append(sen)
                continue

            if quote_flag:  # There is a front quotation mark before the current sentence, which must be merged with the front quotation mark
                final_sentences[-1] = final_sentences[-1] + sen
                quote_flag = False

            else:
                if final_sentences[-1][-1] in self.back_quote_list:
                    # A back quotation mark precedes this sentence,
                    # and it is necessary to check whether there are other terminators to determine whether it is merged with the previous sentence
                    if len(final_sentences[-1]) <= 1:
                        # The previous sentence is only one character.  merge the back quotes
                        final_sentences[-1] = final_sentences[-1] + sen
                    else:  # The previous sentence has multiple characters,
                        if criterion == 'fine':
                            if final_sentences[-1][-2] in self.punches_fine_grained:
                                # If symbols such as commas exist, you need to add another sentence.
                                final_sentences.append(sen)
                            else:  # If there is no period in the previous sentence, it needs to be merged with the previous sentence
                                final_sentences[-1] = final_sentences[-1] + sen

                        elif criterion == 'coarse':
                            if final_sentences[-1][-2] in self.punches_coarse_grained:
                                # If there is a period, you need to start another sentence
                                final_sentences.append(sen)
                            else:  # If there is no period in the previous sentence, it needs to be merged with the previous sentence
                                final_sentences[-1] = final_sentences[-1] + sen
                else:
                    final_sentences.append(sen)
        return final_sentences


def merge_short_sentences(sentences, chunk_size):
    short_sentences = []
    for i, sentence in enumerate(sentences):  
        short_sentences.append(sentence)
        if len(''.join(short_sentences)) > chunk_size:
            return sentences[:i], sentences[i:]
    return sentences, []

def textsplitter_with_overlap(sentences, chunk_size=64, chunk_overlap_rate=0.1):
    """

    : param sentences: sentences = split_sentence(text)
    : param chunk_size:
    : param chunk_overlap_rate:
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

        if len(''.join(overlap_sentences)) + len(sentences[0]) > chunk_size:  # discarding the overlapping sentences
            continue

        sentences = overlap_sentences + sentences  # new sentences set
    return result

split_sentence = Chinese_text_Splitter()

if __name__ == '__main__':
    text =  '她轻轻地哼起了《摇篮曲》：“月儿明，风儿静，树叶儿遮窗棂啊……”' \
            '迈进金黄色的大门，穿过宽阔的风门厅和衣帽厅，就到了大会堂建筑的枢纽部分——中央大厅. JAVA語言比C++語言好。' \
            '中国猿人（全名为“中国猿人北京种”，或简称“北京人”）在我国的发现，是对古人类学的一个重大***^贡献。央视新闻消息，近日，特朗普老友皮尔斯·摩根喊话特朗普：“美国人的生命比你的选举更重要。如果你继续以自己为中心，继续玩弄愚蠢的政治……如果你意识不到自己>的错误，你就做不对!”。目前，特朗普已“取关”了这位老友。' \
           '张华考上了北京大学，在化学系学习：李萍进了中等技术学校，读机械制造专业；我在百货公司当售货员：我们都有光明的前途。爱因斯坦说："想象力比知识更重要，因为知识是有限的，而想象力概括着世界上的一切，推动着进步，并且是知识进化的源泉。“'

    sentences = split_sentence(text, criterion='coarse')
    print(sentences)
    print(textsplitter_with_overlap(sentences))
