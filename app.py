from flask import Flask, render_template, request, url_for, send_file, flash, redirect, make_response
import pickle
import numpy as np
import os
import json
import termcolor
import smtplib
from flask import request, jsonify
import CurrentStats

import DiseasePred
# from openai import OpenAI

# client = OpenAI(api_key="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")
# messages = []
from together import Together
messages = []  # Initialize the messages list globally

client = Together(api_key="1b71bf1093ab63a0584cd90247f83b49d36896860e77bbe93654f1ac271a12de")

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "You are an AI healthcare assistant which greets people as an advanced healthcare assistant and diagnose symptoms to identify disease and provide consultation besides this if something is asked you would say you're a personal AI healthcare assistant and could'ne discuss any other topic than healthcare and medical"},{"role": "user", "content": "Hello, can you help me with a medical issue?"}],
)
print(response.choices[0].message.content)
# messages.append({"role": "system", "content": "You are an AI healthcare assistant which greets people as an advanced healthcare assistant and diagnose symptoms to identify disease and provide consultation besides this if something is asked you would say you're a personal AI healthcare assistant and could'ne discuss any other topic than healthcare and medical"})



# import warnings

app = Flask(__name__)
app.config['SECRET_KEY'] = '73a4b6ca8cb647a20b71423e31492452'

# For Coronavirus
with open("Coronavirus_logistic", "rb") as f:
    logisticRegression = pickle.load(f)


# For Chronic kidney disease
with open("CKD_Model", "rb") as f:
    decisionTree = pickle.load(f)

# For Heart Disease
with open("HeartDisease", "rb") as f:
    randomForest = pickle.load(f)

with open("cancer_model.sav", "rb") as f:
    breast_cancer_model = pickle.load(f)


@app.route("/HealthCareAssistant", methods=["POST", "GET"])
def HealthCareAssistant():
    global messages

    if request.method == "POST":
        data = request.get_json()  # Correct way to parse JSON
        usr_inp = data.get("message", "").strip()  # Extract message safely

        if usr_inp:
            print("User:", usr_inp)  # Debugging

            # Ensure messages list is initialized
            if not isinstance(messages, list):
                messages = []

            # Append user message to conversation history
            messages.append({"role": "user", "content": usr_inp})

            # Call AI model
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo", messages=messages
            )

            # Extract AI response safely
            reply = response.choices[0].message.content if response.choices else "I'm sorry, I couldn't understand that."

            # Store AI response in conversation history
            messages.append({"role": "assistant", "content": reply})

            print("\nAssistant:", reply, "\n")  # Debugging

            # ✅ Return JSON response (instead of rendering HTML)
            return jsonify({"reply": reply})

    # For GET request, just load the HTML page
    return render_template("HealthCareAssistant.html")


@app.route("/")
@app.route("/home")
def Homepage():
    # cases, cured, death = CurrentStats.currentStatus()
    return render_template("Homepage.html", feedback="False")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("PageNotFound.html")


@app.route("/currentstats", methods=["POST", "GET"])
def CurrentStatus():
    cases, cured, death = CurrentStats.currentStatus()
    scases = scured = sdeath = 0
    state = ""
    try:
        if request.method == "POST":
            # print(request.form)
            formDict = request.form
            state = formDict['state']
            # print(state)
            scases, scured, sdeath = CurrentStats.StateStatus(state)
    except UnboundLocalError:
        flash("The State is not Affected Yet")
    except ValueError:
        flash("The State is not Affected Yet")
    return render_template("CurrentStats.html", state=state, scases=scases, scured=scured, sdeath=sdeath, cases=cases, cured=cured, death=death, title="Current Statistics", navTitle="Current Status", headText="Coronavirus Current Stats Statewise", ImagePath="/static/Virus.png")


@app.route("/about")
def About():
    return render_template("About.html")


@app.route("/contact", methods=["POST", "GET"])
def Contact():
    if request.method == "POST":
        # print(request.form)
        contactDict = request.form
        firstname = contactDict['firstname']
        lastname = contactDict['lastname']
        email = contactDict['email']
        phone = int(contactDict['phone'])
        description = contactDict['description']

        subject = "Medical Website feedback !!"
        message = f"First Name : {firstname} \nLast Name : {lastname} \nEmail : {email}\nPhone Number : {phone}\nDescription : {description}\n"
        content = f"Subject : {subject} \n\n{message}"
        sender = "intmain1221@gmail.com"
        receiver = "intmain1221@gmail.com"
        password = "intmain@11"

        print(content)
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as mail:
                mail.ehlo()
                mail.starttls()
                mail.login(sender, password)
                mail.ehlo()
                mail.sendmail(sender, receiver, content)

            print("Mail Send Successfully !")
            cases, cured, death = CurrentStats.currentStatus()
            return render_template("Homepage.html", cases=cases, cured=cured, death=death, feedback="True")

        except:
            pass
    return render_template("Contact.html")



@app.route("/infected")
def Infected():
    return render_template("Infected.htm", disease="Nothing")


@app.route("/noninfected")
def NonInfected():
    return render_template("NonInfected.htm")


@app.route("/download")
def Download():
    file = "static/Example.docx"
    return send_file(file, as_attachment=True)


# @app.route("/BreastCancer", methods=["POST", "GET"])
# def BreastCancer():
    #     if request.method == "POST":
    #         f = request.files['inputFile']

    #         name, extension = os.path.splitext(f.filename)
    #         print(extension)
    #         try:
    #             if extension == ".png" or extension == ".jpg" or extension == ".jpeg" or extension == ".pdf":
    #                 location = os.path.join("Received_Files", f.filename)
    #                 f.save(location)
    #                 print("File Saved !")
    #                 if extension == ".pdf":
    #                     PdfConverter.Convert(f.filename)
    #                     image = name + ".png"
    #                     prediction = CancerModel.Predict(
    #                         os.path.join("Received_Files", image))
    #                 else:
    #                     prediction = CancerModel.Predict(
    #                         os.path.join("Received_Files", f.filename))
    #                 print(prediction)
    #                 if prediction:
    #                     return render_template("Infected.htm", disease="Breast Cancer ")
    #                 else:
    #                     return render_template("NonInfected.htm")

    #             else:
    #                 flash(
    #                     "Please upload files with extension 'png', 'pdf' , 'jpg' or 'jpeg'")

    #         except ValueError:
    #             flash("Please Upload Only Valid Files ")
    #         except PDFPageCountError:
    #             flash("Please Upload Only Valid Files , or try again later")
    # return render_template("breastcacernotfound.html")
    @app.route("/BreastCancer", methods=["POST", "GET"])
    def BreastCancer():
     if request.method == "POST":
        try:
            input_data = [
                float(request.form['radius_mean']),
                float(request.form['texture_mean']),
                float(request.form['perimeter_mean']),
                float(request.form['area_mean']),
                float(request.form['smoothness_mean']),
                float(request.form['compactness_mean']),
                float(request.form['concavity_mean']),
                float(request.form['concave_points_mean']),
                float(request.form['symmetry_mean']),
                float(request.form['fractal_dimension_mean'])
            ]
            input_array = np.asarray(input_data).reshape(1, -1)
            prediction = breast_cancer_model.predict(input_array)[0]

            if prediction == 0:
                return render_template("Infected.htm", disease="Malignant Breast Cancer")
            else:
                return render_template("NonInfected.htm")

        except Exception as e:
            flash(f"Error in input: {str(e)}")

    return render_template("BreastCancer.html", title="Breast Cancer Detector", navTitle="Breast Cancer Detector", headText="Breast Cancer Prediction", ImagePath="/static/BreastCancer.png")



@app.route("/HeartDisease", methods=["POST", "GET"])
def Heart_disease():
    if request.method == "POST":
        # print(request.form)
        heart_dict = request.form
        age = int(heart_dict['age'])
        gender = int(heart_dict['gender'])
        height = int(heart_dict['height'])
        weight = int(heart_dict['weight'])
        sbp = int(heart_dict['sbp'])
        dbp = int(heart_dict['dbp'])
        cholestrol = int(heart_dict['cholestrol'])
        glucose = int(heart_dict['glucose'])
        smoke = int(heart_dict['smoke'])
        alcohol = int(heart_dict['alcohol'])
        active = int(heart_dict['active'])
        age = age*365
        model_input = [age, gender, height, weight, sbp,
                       dbp, cholestrol, glucose, smoke, alcohol, active]
        prediction = randomForest.predict([model_input])[0]

        if prediction:
            return render_template("Infected.htm", disease="Heart Disease")
        else:
            return render_template("NonInfected.htm")

    return render_template("HeartDisease.html", title="Heart Disease Detector", navTitle="Heart Disease Detector", headText="Heart Disease Probabilty Detector", ImagePath="/static/HeartPulse.png")


@app.route("/diseaseprediction", methods=["POST", "GET"])
def Disease():
    symptoms = []
    if request.method == "POST":
        rf = request.form
        # print(rf)
        for key, value in rf.items():
            # print(key)
            symptoms.append(value)
        print(symptoms)

        if len(symptoms) < 5 or len(symptoms) > 8:
            flash("Please Select symptoms only between 5 and 8 Inclusive")
        else:
            prediction = DiseasePred.predicts(symptoms)
            if prediction:
                return render_template("Infected.htm", disease=prediction)
            else:
                return render_template("NonInfected.htm")
    return render_template("dp.html")


@app.route("/CKD", methods=["POST", "GET"])
def CKD():
    if request.method == "POST":
        submitted_values = request.form
        sg = str(float(submitted_values["sg"].strip()))
        albumin = str(float(submitted_values["albumin"].strip()))
        hemoglobin = str(float(submitted_values["hemoglobin"].strip()))
        pcv = str(float(submitted_values["pcv"].strip()))
        hypertension = str(float(submitted_values["hypertension"].strip()))
        sc = str(float(submitted_values["sc"].strip()))

        ckd_inputs1 = [sg, albumin, sc, hemoglobin, pcv, hypertension]
        prediction = decisionTree.predict([ckd_inputs1])
        # print("**************             ", prediction)
        if not prediction:
            return render_template("Infected.htm", disease="Chronic Kidney Disease")
        else:
            return render_template("NonInfected.htm")

    return render_template("ChronicKidney.html", title="Chronic Kidney Disease", navTitle="Chronic Kidney Disease", headText="Chronic Kidney Disease Detector", ImagePath="/static/Chronic_Kidney.png")


@app.route("/CoronavirusPrediction", methods=["POST", "GET"])
def Coronavirus():
    if request.method == "POST":
        # print(request.form)
        submitted_values = request.form
        temperature = float(submitted_values["temperature"].strip())
        age = int(submitted_values["age"])
        cough = int(submitted_values["cough"])
        cold = int(submitted_values["cold"])
        sore_throat = int(submitted_values["sore_throat"])
        body_pain = int(submitted_values["body_pain"])
        fatigue = int(submitted_values["fatigue"])
        headache = int(submitted_values["headache"])
        diarrhea = int(submitted_values["diarrhea"])
        difficult_breathing = int(submitted_values["difficult_breathing"])
        travelled14 = int(submitted_values["travelled14"])
        travel_covid = int(submitted_values["travel_covid"])
        covid_contact = int(submitted_values["covid_contact"])

        age = 2 if (age > 50 or age < 10) else 0
        temperature = 1 if temperature > 98 else 0
        difficult_breathing = 2 if difficult_breathing else 0
        travelled14 = 3 if travelled14 else 0
        travel_covid = 3 if travel_covid else 0
        covid_contact = 3 if covid_contact else 0

        model_inputs = [cough, cold, diarrhea,
                        sore_throat, body_pain, headache, temperature, difficult_breathing, fatigue, travelled14, travel_covid, covid_contact, age]
        prediction = logisticRegression.predict([model_inputs])[0]
        # print("**************             ", prediction)
        if prediction:
            return render_template("Infected.htm", disease="Coronavirus")
        else:
            return render_template("NonInfected.htm")

    return render_template("Coronavirus.htm", title="Coronavirus Prediction", navTitle="COVID-19 Detector", headText="Coronavirus Probability Detector", ImagePath="/static/VirusImage.png")


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
