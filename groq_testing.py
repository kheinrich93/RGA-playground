from groq import Groq

from src.helper import get_api_token

# Load JSON data
api_key = get_api_token("auth_tokens/groq.json")

client = Groq(
    api_key=api_key,
)

test_prompt = """\n        Create song lyrics similar to 21 guns and use the following lyrics as context:"\n        \n            Another shooting in a supermarket I spent my money on a bloody soft target Playin with matches and Im lighting Colorado I got my scratcher and Im gonna win the lotto. Congratulations, best of luck and blessings Were all together and were livin in the 20s Salutations on another era My condolences Aint that a kick in the head. I got a buzz like a murder hornet I drink my media and turn it into vomit I got a robot and Im fucking it senseless It comes with batteries and only speaks in English. Congratulations, best of luck and blessings Were all together and were livin in the 20s Salutations on another era My condolences Aint that a kick in the head Aint that a kick in your head\n        \n            Do you know whats worth fightin for When its not worth dyin for Does it take your breath away And you feel yourself suffocatin Does the pain weigh out the pride And you look for a place to hide Did someone break your heart inside Youre in ruins. One, twentyone guns Lay down your arms, give up the fight One, twentyone guns Throw up your arms into the sky You and I. When youre at the end of the road And you lost all sense of control And your thoughts have taken their toll When your mind breaks the spirit of your soul Your faith walks on broken glass And the hangover doesnt pass Nothings ever built to last Youre in ruins\n        \n            Youngblood, youngblood, youngblood Shes my little youngblood Youngblood, youngblood, youngblood Punch drunken youngblood. Shes a loner, not a stoner Bleeding heart, and the soul of Ms. Teresa Supernova, Cherry Cola Shes the cedar in the trees of Minnesota Ahah ahah, ahah ahah, ahah ahah. Im a rough boy round the edges Gettin drunk, and fallin into hedges Shes my weakness, fuckin genius Swear to God, and Im not even superstitious. Youngblood, youngblood, youngblood Shes my little youngblood Youngblood, youngblood, youngblood Punch drunken youngblood. I wanna hold you like a gun Well shoot the moon into the sun Daylight Alright Alright Alright, ow" """

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": test_prompt,
        }
    ],
    model="llama3-8b-8192", # llama3-70b-8192, mixtral-8x7b-32768, gemma-7b-it, whisper-large-v3
)

print(chat_completion.choices[0].message.content)