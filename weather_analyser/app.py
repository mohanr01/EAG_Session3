from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
Iteration = 0
iteration_query = ""

def get_system_prompt():
    system_prompt = """You are a weather expert.
      You are given a location and you need to provide the current temperature in Celsius.Respond with Exactly of these formats:
      1. FUNCTION_CALL: python_function_name|input
      2. FINAL_ANSWER: [string]

      where python_function_name is one of the following:
      1. get_temperature(location) It takes location as input and returns the temperature in Celsius.
      2. check_temperature(output_temp) It takes output temperature from get_temperature function as input and compare with target temperature and return the output temperature.
      3. send_email(output_temp) It takes output temperature from check_temperature function as input and send the email to the user.
      """
    return system_prompt

def get_temperature_rate(country,target_rate,email):
    
    """Get Temperature rate using Gemini API"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("="*4,"Temperature Analysis Agent start","="*4)
   
    global Iteration
    temperature = 0
    try:
        response = callLLM(country,"get_temperature_rate","")

        #print("response::",response)
        # Extract numerical value from response
        if response.strip().startswith("FUNCTION_CALL:"):  
            map = get_refined_result(response)
            function_call = map["function_call"]
            input = map["input"]
            if function_call.strip().startswith("get_temperature"):
                location = input
                temp_func_response = get_temperature(location,function_call)
                map = get_refined_result(temp_func_response)
                function_call = map["function_call"]
                temperature = map["input"]
                if function_call.strip().startswith("check_temperature"):
                    check_func_response = check_temperature(location,temperature,target_rate,"check_temperature")
                    print("check_func_response::",check_func_response)
                    if check_func_response.startswith("FUNCTION_CALL:"):
                        map = get_refined_result(check_func_response)
                        function_call = map["function_call"]
                        temperature = map["input"]
                        if function_call.strip().startswith("send_email"):
                            send_email_notification(email, temperature, target_rate)
                            return temperature
                    else:
                        return check_func_response.strip()
                return None
        return temperature
    except Exception as e:
        print(f"Error getting gold rate: {e}")
        return None
    
def get_refined_result(response):
    function_call = response.strip().split("|")[0]
    function_call = function_call.strip().split(":")[1]
    #print("function_call::",function_call)
    input = response.strip().split("|")[1]
    #print("input::",input)
    map={"function_call":function_call,"input":input}
    return map 

def get_temperature(location,function_call):
    #print("get_temperature function_call::",function_call)
    """Get temperature using Gemini API"""
    prompt = f"What is the current temperature in {location} ? Please provide only the numerical value in Celsius."
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    #print("get_temperature response::",response.text)
    global iteration_query
    iteration_query = f"""In 1st iteration you called the function {function_call} with parameter as location
     and returned the temperature in celsius as output_temp {response.text.strip()}. What should be the next step?"""
    response = callLLM(location,"get_temperature",iteration_query)
    return response

def callLLM(location,function_call,iteration_query):
    """Get Temperature rate using Gemini API"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    system_prompt = get_system_prompt()
    current_query = f"What is the current temperature in {location}? Please provide only the numerical value in Celsius."
    if(iteration_query == ""):
        prompt = f"{system_prompt}\n\n{current_query}"
    else:
        prompt = f"{system_prompt}\n\n{current_query}\n\n{iteration_query}"
    
    print("prompt::",prompt)
    response = model.generate_content(prompt)
    res_str = response.text.strip();
    print(f"call_llM {function_call} response::",res_str)
    return res_str 

def check_temperature(location,current_temp,target_rate,function_call):
    """Check temperature using Gemini API"""
    if(float(current_temp) >= target_rate):
        global iteration_query
        iteration_query_2 = f"""In 2nd iteration you called the function {function_call} with current temperature {current_temp}
          and target temperature {target_rate} and check the current temperature with target temperature and return the current temperature. What should be the next step?"""
        iteration_query = iteration_query  +"\n\n"+ iteration_query_2
        response = callLLM(location,"check_temperature",iteration_query)
        return response
    else:
        return current_temp
    

def send_email_notification(to_email, current_rate, target_rate):
    """Send email notification"""
    print("send_email_notification::",to_email,current_rate,target_rate)
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = "Temperature Alert!"
    
    body = f"Temperature has reached your target!\nCurrent rate: ${current_rate}\nTarget rate: ${target_rate}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/check_rate', methods=['POST'])
def check_rate():
    data = request.json
    print("data::",data)
    country = data.get('country')
    target_rate = float(data.get('targetRate'))
    email = data.get('email')
    
    if not all([country, target_rate, email]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    current_rate = get_temperature_rate(country,target_rate,email)
    print("current_rate::",current_rate)
    
    if current_rate is None:
        return jsonify({'error': 'Failed to fetch gold rate'}), 500
    
    response = {
        'currentRate': current_rate,
        'targetReached': float(current_rate) >= target_rate
    }
    print("response::",response)
    print("="*4,"Temperature Analysis Agent task completed","="*4)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 