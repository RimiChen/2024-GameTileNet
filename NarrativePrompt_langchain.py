### because langchain >=2.0 didn't support older command of langchain community
### https://github.com/DataDog/dd-trace-py/issues/8212
### langchain helps to incorperate calls to LLM within python codes
import warnings
from langchain._api import LangChainDeprecationWarning
warnings.simplefilter("ignore", category=LangChainDeprecationWarning)

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from sk import my_sk # importing secret key from python file, openAI API


# ### output parser
# class GradeOutputParser(BaseOutputParser):
#     """Determine whether grade was correct or wrong"""
#     def parse(self, text:str):
#         """Parse the output of an LLM call."""
#         return "wrong" not in text.lower()
    

### define LLM object
llm = ChatOpenAI(model_name="gpt-4", openai_api_key = my_sk, temperature = 0.7)

### defin prompt template

# The relations was limited to "above", "below", "at the right of", "at the left of", and "on top of". \
prompt_template_text = """
You are a storyteller who creates thrilling adventure stories.\
Please generate an adventure story within 100 words.\
Retrieve three key time frames from the story, and describe them with [Object] [Relation] [Object] type of scene descriptions.\

Please tell the story in a captivating and imaginative way, engaging the reader from beginning to end.

Here is a sample format:
"In the heart of the Enchanted Forest, young Elara discovered an ancient map hidden within a hollow oak. It led her to the legendary Crystal Cavern, rumored to grant the finder a single wish. Braving treacherous paths and wild creatures, Elara reached the cavern's shimmering entrance. Inside, she faced the Guardian, a majestic dragon. With courage and wit, she solved the Guardian’s riddle, earning her the wish. Elara wished for peace in her war-torn village. As she exited the cavern, the skies cleared, and harmony was restored, proving that bravery and hope could transform the world."

Time Frame: Elara discovers the ancient map
Hollow oak [contains] ancient map
Elara [stands near] hollow oak
Sunlight [filters through] forest canopy

Time Frame: Elara faces the treacherous paths
Elara [walks along] rocky path
Wild creatures [hide behind] dense bushes
Treacherous paths [lead to] Crystal Cavern

Time Frame: Elara meets the Guardian dragon
Crystal Cavern entrance [glows with] shimmering light
Guardian dragon [sits atop] crystal throne
Elara [stands before] Guardian dragon

After get the time frame, generate a list that map all the relations in the time frames in to the spatial relation categories to help creating game level: "above", "below", "at the right of", "at the left of", and "on top of".
Please show the mapping in the form: relation-mapped result
"""

prompt = PromptTemplate(
    template = prompt_template_text
)

### define chain
chain = LLMChain(
    llm = llm,
    prompt = prompt,
    )

# Generate the adventure story
adventure_story = chain.run({})

# Print the story
print(adventure_story)