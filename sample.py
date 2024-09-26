from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
# provide the path of  pdf file/files.
pdfreader = PdfReader('apjspeech.pdf')
from typing_extensions import Concatenate
# read text from pdf
text = ''
for i, page in enumerate(pdfreader.pages):
    content = page.extract_text()
    if content:
        text += content
llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
llm.get_num_tokens(text)
4001
## Splittting the text
text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=20)
chunks = text_splitter.create_documents([text])
len(chunks)
2
chain = load_summarize_chain(
    llm,
    chain_type='map_reduce',
    verbose=False
)
summary = chain.run(chunks)
summary
"Former President of India, A P J Abdul Kalam, gave a departing speech expressing gratitude for support and collaboration, highlighting the need to accelerate development, empower villages, prioritize agriculture, and promote courage in the face of challenges and calamities. He also emphasized the importance of youth in shaping India's future and preserving its culture and resources."
Map Reduce With Custom Prompts
chunks_prompt="""
Please summarize the below speech:
Speech:`{text}'
Summary:
"""
map_prompt_template=PromptTemplate(input_variables=['text'],
                                    template=chunks_prompt)
final_combine_prompt='''
Provide a final summary of the entire speech with these important points.
Add a Generic Motivational Title,
Start the precise summary with an introduction and provide the
summary in number points for the speech.
Speech: `{text}`
'''
final_combine_prompt_template=PromptTemplate(input_variables=['text'],
                                             template=final_combine_prompt)
summary_chain = load_summarize_chain(
    llm=llm,
    chain_type='map_reduce',
    map_prompt=map_prompt_template,
    combine_prompt=final_combine_prompt_template,
    verbose=False
)
output = summary_chain.run(chunks)
output
'Title: "Empowering India: Reflections and Aspirations"\n\nSummary:\n\n1. Dr. A. P. J. Abdul Kalam reflects on his five years as President of India and highlights important messages he has learned during his time in office.\n2. He emphasizes the aspirations of the youth and the need to accelerate development in the country.\n3. The importance of empowering villages and mobilizing rural core competence for competitiveness is discussed.\n4. Kalam shares his experiences with farmers and emphasizes the importance of agriculture as the backbone of the nation.\n5. Overcoming challenges and disasters through partnership and courage is emphasized.\n6. The power of sea waves, his proposal for a Pan African e-Network, and his admiration for the Indian defense forces are also discussed.\n7. The importance of empowering the youth for a developed India by 2020 is highlighted.\n8. Preserving India\'s rich culture and resources is emphasized.\n9. Dr. Kalam outlines his vision for a developed nation with equitable distribution, quality education, responsive governance, and eradication of poverty and crime.\n10. Dr. Kalam expresses his gratitude and commitment to the mission of making India a developed nation.'
RefineChain For Summarization
chain = load_summarize_chain(
    llm=llm,
    chain_type='refine',
    verbose=True
)
output_summary = chain.run(chunks)