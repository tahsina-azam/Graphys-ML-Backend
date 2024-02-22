from flask import Flask, request
from hugchat import hugchat
from hugchat.login import Login
import json
import os

email = os.environ['USERNAME']
passwd = os.environ['PASSWORD']
sign = Login(email, passwd)
cookies = sign.login()
cookie_path_dir = "./cookies_snapshot"
sign.saveCookiesToDir(cookie_path_dir)
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

app = Flask(__name__)

@app.route("/members")
def members():
    return {"members":["Member1","Member2","Member3"]}

template = """
You have been tasked with analyzing a piece of text and generating a graphical representation of the data contained within. Your tool of choice is a large language model (LLM) that has the ability to process natural language input and output JSON data.

Your goal is to write a program that takes a paragraph of text as input, sends it to the LLM, and receives a JSON response containing an array of objects representing the graph data. Each object in the array should have two properties: "label" and "value". The "label" property should contain the name of a statistical measure (e.g. "Number of Users"), while the "value" property should contain the count of that measure (e.g. 100).

For example, if the input text contains the sentence "There are 100 users and 200 pageviews", the JSON response should look something like this:

{
  "graph": [
    {
      "label": "Number of Users",
      "value": 100
    },
    {
      "label": "Number of Pageviews",
      "value": 200
    }
  ]
}

The catch? The LLM only accepts sentences that are grammatically correct and relevant to the task at hand. You'll need to carefully craft your input text to ensure that the LLM can extract meaningful information from it.

"""

additionalInstructions = """
Caution - Do not include any text other than the json itself with your response. Think yourself as a api server, So you can only return json but you cannot say anything else. Also note, if there are any calculations needed like percentage convert them to real value.
"""

@app.route("/process", methods=['POST'])
def processData():
    req_body = request.get_json()
    prompt = template + "\n" + req_body['prompt'] + "\n" + additionalInstructions
    # resp = 'Think you are a rest endpoint. I want some data extracted from sentences given to you. I want to plot bar charts or pie charts with data points. so for that i would need points strictly with json format like : { "graph": [ { "label": girl,"value": 2}, {"label": boy,"value":10}] given a sentence suppose: "there were 2 girls and 10 boys present in the room". Now i will give you the sentence and extract me information like I mentioned above. Remember that there might be more than one sentence that have relevant information that can be plotted. Send the More Relevant and likely one that you think would be more meaningful to plot / visualise. Remember I need only the json of my data, no other explanatory sentence please. just json should be in your response. Here is the text that you would process for me: "'+text+ '"No additional sentences just the json object and not json array also if you can not find any data just return {} i repeat even if the sentence does not make sense do not say anything else except json.'
    # query_result: str = chatbot.query('Think you are a RESTENDPOINT and you can only send json in this schema format { "_id": UUID, "graph": Array<Integer> }. I will send you a text, which may contain some data points which required to be plotted. You will send me the response of relevant datapoints and nothing else just like the format i specified. Here is the text: tJFfHOut of 3fsdjO 30 males of 9 are Gay')
    query_result: str = str(chatbot.query(prompt))
    start_index = query_result.find('```json')
    print(query_result, start_index)
    if start_index != -1:
        start_index += 7
        end_index = query_result.find('```', start_index)
        json_str = query_result[start_index:end_index]
    else:
        json_str = query_result
    if len(json_str) > 0:
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as ex:
            print(ex.msg)
            data = {}
    else:
        data = {}
    return data


if __name__ == "__main__":
    app.run(debug=True)


    # flask --app app run -h 0.0.0.0 -p 5000