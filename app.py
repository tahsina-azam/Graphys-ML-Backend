from flask import Flask
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

@app.route("/process/<text>", methods=['GET'])
def processData(text):
    resp = 'Think you are a rest endpoint. I want some data extracted from sentences given to you. I want to plot bar charts or pie charts with data points. so for that i would need points strictly with json format like : { "graph": [ { "label": girl,"value": 2}, {"label": boy,"value":10}] given a sentence suppose: "there were 2 girls and 10 boys present in the room". Now i will give you the sentence and extract me information like I mentioned above. Remember that there might be more than one sentence that have relevant information that can be plotted. Send the More Relevant and likely one that you think would be more meaningful to plot / visualise. Remember I need only the json of my data, no other explanatory sentence please. just json should be in your response. Here is the text that you would process for me: "'+text+ '"No additional sentences just the json object and not json array also if you can not find any data just return {} i repeat even if the sentence does not make sense do not say anything else except json.'
    # query_result: str = chatbot.query('Think you are a RESTENDPOINT and you can only send json in this schema format { "_id": UUID, "graph": Array<Integer> }. I will send you a text, which may contain some data points which required to be plotted. You will send me the response of relevant datapoints and nothing else just like the format i specified. Here is the text: tJFfHOut of 3fsdjO 30 males of 9 are Gay')
    query_result: str = str(chatbot.query(resp))
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