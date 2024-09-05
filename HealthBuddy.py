import sys
import time
import re
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QPushButton, QWidget, \
    QHBoxLayout, QInputDialog, QMessageBox, QAction
from PyQt5.QtGui import QIcon, QTextCursor, QFont
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime, timedelta
import os
import pandas as pd
from nltk.chat.util import Chat, reflections
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class HealthPredictor:
    def __init__(self, dataset_path):
        # Load and preprocess dataset
        self.dataset = pd.read_csv(dataset_path)
        self.preprocess_dataset()

        # Split dataset into features and labels
        # Exclude 'Outcome variable' from the features (X)
        X = self.dataset.drop(columns=['Disease', 'Medical advice', 'Outcome variable'])
        y = self.dataset['Disease']

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train a RandomForestClassifier
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

    def preprocess_dataset(self):
        # Mapping categorical columns to numerical values
        self.dataset['Fever'] = self.dataset['Fever'].map({'yes': 1, 'no': 0})
        self.dataset['Cough'] = self.dataset['Cough'].map({'yes': 1, 'no': 0})
        self.dataset['Fatigue'] = self.dataset['Fatigue'].map({'yes': 1, 'no': 0})
        self.dataset['Difficulty breathing'] = self.dataset['Difficulty breathing'].map({'yes': 1, 'no': 0})
        self.dataset['Age'] = self.dataset['Age'].fillna(self.dataset['Age'].median())  # Fill missing values
        scaler = StandardScaler()  # Initialize scaler
        self.dataset['Age'] = scaler.fit_transform(self.dataset[['Age']])
        self.dataset['Gender'] = self.dataset['Gender'].map({'male': 1, 'female': 0})
        self.dataset['Blood pressure'] = self.dataset['Blood pressure'].map({'low': 0, 'normal': 1, 'high': 2})
        self.dataset['Cholesterol level'] = self.dataset['Cholesterol level'].map({'low': 0, 'normal': 1, 'high': 2})

        # Handle any other columns that have non-numeric values
        self.dataset['Outcome variable'] = self.dataset['Outcome variable'].map({'Positive': 1, 'Negative': 0, 'Borderline': 2})

    def predict_disease(self, patient_data):
        # Convert patient data to match dataset format (exclude 'Outcome variable')
        patient_df = pd.DataFrame([patient_data])

        # Predict the disease
        predicted_disease = self.model.predict(patient_df)[0]

        # Get medical advice corresponding to the predicted disease
        advice = self.dataset[self.dataset['Disease'] == predicted_disease]['Medical advice'].values[0]

        return predicted_disease, advice

# Define patterns and responses for NLTK chatbot
pairs = [
    [r"my name is (.*)", ["Hello %1, how can I assist you today? you can type 'login' if you need a Health Assistant 🧑‍⚕️.."]],
    [r"hi|hey|hello", ["Hello, how can I help you? you can type 'login' if you need a Health Assistant 🧑‍⚕️..", "Hey there! What can I do for you? you can type 'login' if you need a Health Assistant 🧑‍⚕️..", "Hi! How can I assist you today? you can type 'login' if you need a Health Assistant 🧑‍⚕️.."]],
    [r"i need help|help", ["I'm here to take care of you 😊. What's the problem?🤔🩺", "What happened 😨, what can i do for you?"]],
    [r"i have fever|i think im having a fever|i got fever|fever", ["For common fever, 🛌 rest, stay hydrated with fluids 🥤, use over-the-counter medications like paracetamol or ibuprofen 💊 to reduce fever, and apply a cool compress ❄ or take a lukewarm bath 🛁 to lower body temperature. Consult a healthcare professional if symptoms persist or worsen"]],
    [r"i have cough|im having a cough|i got cough|cough", ["For common cough, 🥤 stay hydrated, use a humidifier or inhale steam 🌫 to soothe the throat, try over-the-counter cough syrups or lozenges 💊, and rest well 🛌. If the cough persists for more than a week or is accompanied by other symptoms, consult a healthcare professional"]],
    [r"what is your name?|what are you|who are you|whats your name", ["I am a chatbot created to assist you 🤖. You can call me Health Buddy 🩺😊","I am a chatbot 🤖. My developers call me Health Buddy 🩺😊", "I am an AI Health Assistant, You can call me Health Buddy 🩺😊"]],
    [r"how are you?", ["I'm good enough to assist you and help you with your health 😊🩺"]],
    [r"can you help me with (.*)", ["Sure, I can help you with %1. Please provide more details."]],
    [r"sorry (.*)", ["It's okay. How can I assist you?"]],
    [r"sorry", ["It's okay. How can I assist you?"]],
    [r"health report|view health report|show health report|update health report|update health check|update report", ["You need to login first to get those information, please type 'login'","To access those information, please type 'login'","First login to get those information, please type 'login'"]],
    [r"thank you|thanks", ["You're welcome!😊", "No problem!😊", "Happy to help!😊"]],
    [r"login", ["Ok, Please enter your name...", "Got it, Please enter your name..."]],
    [r"bye|quit|see you later|goodbye", ["Bye! Have a great day!😊", "Goodbye!😊"]],
    [r"i do not understand|i do not understood|i didnt understand|i didnt understood|i did not understand", ["I am sorry for the Inconvenience, My skill-set is still under development. But you can explore other features, just type 'login' to access Health Assistants"]],
    [r"(.*)", ["I'm sorry, I don't understand that. Can you rephrase?", "Could you please elaborate on that?"]]
]


# Define the NLTK-based chatbot class
class RuleBasedChatbot:
    def __init__(self, pairs):
        self.chat = Chat(pairs, reflections)

    def respond(self, user_input):
        return self.chat.respond(user_input)


# Initialize the NLTK-based chatbot
chatbot = RuleBasedChatbot(pairs)

# ChatbotApp Class Initialisation
class ChatbotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.patient_name = None
        self.medicine_reminders = []
        self.appointments = []
        self.medical_advice_list = self.load_medical_advice()
        self.predictor = HealthPredictor('Disease_and_Medical_Advice_Analysis.csv')
        self.is_dark_mode = True
        self.set_theme()

    def initUI(self):
        self.setWindowTitle("Health Buddy AI Virtual Assistant")
        self.setWindowIcon(QIcon("HealthBuddyLogo.jpeg"))  # logo image path



        monospace_font = QFont("Courier New", 15)
        monospace_font_chathistory = QFont("Courier New", 35)

        self.chat_history = QTextEdit(self)
        self.chat_history.setReadOnly(True)
        self.chat_history.setTextInteractionFlags(Qt.TextBrowserInteraction)

        self.chat_history.setFont(monospace_font_chathistory)

        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Type your message here...")


        self.user_input.setFont(monospace_font)
        self.user_input.returnPressed.connect(self.handle_input)

        self.send_button = QPushButton("Send", self)


        self.send_button.setFont(monospace_font)
        self.send_button.clicked.connect(self.handle_input)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_button)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_history)
        layout.addLayout(input_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Menu bar for Future Updates
        """menubar = self.menuBar()
        viewMenu = menubar.addMenu('View')"""

        toggleThemeAction = QAction('Toggle Theme', self)
        toggleThemeAction.triggered.connect(self.toggle_theme)
        #viewMenu.addAction(toggleThemeAction)

        self.append_message("Bot: Hi! I am Your Virtual AI Doctor, What can I help you with today? You can type 'login' for Medical Assistant 🧑‍⚕️", "bot")
        self.showMaximized()

    def set_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet("""
                QMainWindow {background-color: #1e1e1e;}
                QTextEdit {background-color: #1e1e1e;color: #ffffff;}
                QLineEdit {background-color: #333333;color: #ffffff;}
                QPushButton {background-color: #333333;color: #ffffff;}""")
        else:
            self.setStyleSheet("""
                QMainWindow {background-color: #ffffff;}
                QTextEdit {background-color: #ffffff;color: #000000;}
                QLineEdit {background-color: #f0f0f0color: #000000;}
                QPushButton {background-color: #f0f0f0;color: #000000;}""")

    def toggle_theme(self):
        # Toggle Theme for Dark Mode
        self.is_dark_mode = not self.is_dark_mode
        self.set_theme()
    def load_medical_advice(self):
        # Load the medical advice from the CSV file
        try:
            df = pd.read_csv('MedicalAdvices.csv')
            return df['Medical Advices'].tolist()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"Failed to load medical advice: {e}")
            return []

    def handle_input(self):
        user_message = self.user_input.text().strip()
        if user_message:
            self.append_message(f"User: {user_message}", "user")
            self.user_input.clear()

            bot_response = self.get_bot_response(user_message)
            self.append_message(f"Bot: {bot_response}", "bot")

    def append_message(self, message, sender):
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)

        font_size = "25px"
        cursor.insertHtml(
            f'<div style="text-align: left; color: {"white"}; font-size: {font_size};">{message}</div><br>')

        self.chat_history.setTextCursor(cursor)
        self.chat_history.ensureCursorVisible()

    def get_bot_response(self, message):
        message = message.lower().strip()  # Normalize the user input

        # Handle general interactions first
        response = chatbot.respond(message)
        if response and not ("login" in message or self.patient_name):
            return response

        # Handle the login process for user verification
        if "login" in message or not self.patient_name:
            self.patient_name = self.get_patient_name()
            if self.patient_name:
                if self.check_existing_patient(self.patient_name):
                    # Welcome back message for existing users
                    return (
                        f"Welcome back, {self.patient_name}!\n"
                        "What would you like to do today?\n"
                        "(Options: view health report, update health check, daily medical advice, medicine reminder, doctor appointment, exit)"

                    )
                else:
                    # Greeting message for new users
                    return (
                        f"Hello {self.patient_name}, it seems you're new here.\n"
                        "What would you like to explore today?\n"
                        "(Options: health check, daily medical advice, medicine reminder, doctor appointment, exit)"
                    )
            else:
                return "Please enter your name to log in."

        # Ensure the user is logged in before handling further interactions
        if not self.patient_name:
            return "Please log in first by typing 'login'."

        # Logic for existing users: handle each command after login
        if "view health report" in message:
            if self.check_existing_patient(self.patient_name):
                return self.view_health_report()
            else:
                return (
                    "No health report found. Please complete a health check first before viewing your health report.\n"
                    "Type 'health check' to get started."
                )

        elif "health check" in message:
            responses = self.collect_health_data()
            self.save_health_data(responses)
            return (
                "Thank you for providing your details. Your health data has been recorded 😊.\n"
                "Explore more options:\n"
                "(Options: view health report, update health check, daily medical advice, medicine reminder, doctor appointment, exit)"
            )

        elif "update health check" in message:
            responses = self.collect_health_data()
            self.save_health_data(responses)
            return (
                "Your health check details have been updated 😊.\n"
                "What would you like to do next?\n"
                "(Options: view health report, update health check, daily medical advice, medicine reminder, doctor appointment, exit)"
            )

        elif "daily medical advice" in message:
            return self.get_random_medical_advice()

        elif "medicine reminder" in message:
            self.add_medicine_reminder()
            return (
                "Medicine reminder has been set 👍.\n"
                "What would you like to do next?\n"
                "(Options: view health report, update health check, daily medical advice, medicine reminder, doctor appointment, exit)"
            )

        elif "doctor appointment" in message:
            self.add_doctor_appointment()
            return (
                "Doctor appointment has been scheduled 👍.\n"
                "What would you like to do next?\n"
                "(Options: view health report, update health check, daily medical advice, medicine reminder, doctor appointment, exit)"
            )

        elif "exit" in message or "close" in message:
            self.close()
            return "Closing the application. Have a great day! 👋"

        return "I'm sorry, I didn't understand that. Could you try rephrasing?"

    def get_patient_name(self):
        name, ok = QInputDialog.getText(self, 'Patient Name', 'Please enter your name:')
        if ok and re.match("^[A-Za-z ]*$", name):
            return name
        else:
            QMessageBox.warning(self, 'Invalid Input',
                                'Please enter a valid name without numbers or special characters.')
            return None

    def check_existing_patient(self, name):
        return os.path.exists(f"{name}_health_report.txt")

    def collect_health_data(self):
        responses = {}

        day_response, ok = QInputDialog.getText(self, 'Day Info', 'How did your day go?')
        if ok:
            responses['day'] = day_response

        symptoms = ["Fever", "Cough", "Fatigue", "Difficulty Breathing"]
        for symptom in symptoms:
            while True:
                response, ok = QInputDialog.getText(self, 'Symptom Check', f"Do you have any {symptom}? (yes/no)")
                if ok and response.lower() in ["yes", "no"]:
                    responses[symptom] = response.lower()
                    break
                else:
                    QMessageBox.warning(self, 'Invalid Input', "Please enter 'yes' or 'no'.")

        symptoms2 = ["Age", "Gender", "Blood Pressure", "Cholesterol Level"]
        for symptom2 in symptoms2:
            while True:
                try:
                    if symptom2 == "Blood Pressure":
                        response2, ok = QInputDialog.getText(self, 'Blood Pressure', f"What is your {symptom2}? (low | normal | high)")
                        if ok and response2.lower() in ["low", "normal", "high"]:
                            responses[symptom2] = response2
                            break
                        else:
                            QMessageBox.warning(self, 'Invalid Input', "Please enter only 'low' or 'normal' or 'high' for blood pressure")
                    elif symptom2 == "Cholesterol Level":
                        response2, ok = QInputDialog.getText(self, 'Cholesterol Level', f"What is your {symptom2}? (low | normal | high)")
                        if ok and response2.lower() in ["low", "normal", "high"]:
                            responses[symptom2] = response2
                            break
                        else:
                            QMessageBox.warning(self, 'Invalid Input', "Please enter only 'low' or 'normal' or 'high' for cholesterol level")
                    elif symptom2 == "Gender":
                        response2, ok = QInputDialog.getText(self, 'Gender', f"What is your {symptom2}? (male/female)")
                        if ok and response2.lower() in ["male", "female"]:
                            responses[symptom2] = response2.lower()
                            break
                        else:
                            QMessageBox.warning(self, 'Invalid Input', "Please enter 'male' or 'female'.")
                    else:
                        response2, ok = QInputDialog.getText(self, symptom2, f"What is your {symptom2}? (Answer)")
                        responses[symptom2] = int(response2)
                        break
                except ValueError:
                    QMessageBox.warning(self, 'Invalid Input', "Please enter a valid number.")

        return responses

    def save_health_data(self, responses):
        # Create an instance of HealthPredictor
        predictor = HealthPredictor('Disease_and_Medical_Advice_Analysis.csv')

        # Prepare patient data from responses
        patient_data = {
            'Fever': 1 if responses.get('Fever') == 'yes' else 0,
            'Cough': 1 if responses.get('Cough') == 'yes' else 0,
            'Fatigue': 1 if responses.get('Fatigue') == 'yes' else 0,
            'Difficulty breathing': 1 if responses.get('Difficulty breathing') == 'yes' else 0,
            'Age': int(responses.get('Age', 0)),
            'Gender': 1 if responses.get('Gender') == 'male' else 0,
            'Blood pressure': {'low': 0, 'normal': 1, 'high': 2}.get(responses.get('Blood Pressure'), 0),
            'Cholesterol level': {'low': 0, 'normal': 1, 'high': 2}.get(responses.get('Cholesterol Level'), 0)
        }

        # Predict disease and get medical advice
        predicted_disease, medical_advice = predictor.predict_disease(patient_data)

        # Save health data and prediction results to file
        file_name = f"{self.patient_name}_health_report.txt"
        with open(file_name, 'w') as file:
            file.write(f"Health Report for {self.patient_name}\n")
            file.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("\n")
            for question, answer in responses.items():
                file.write(f"{question.capitalize()}: {answer}\n")
            file.write("\n")
            file.write(f"Predicted Disease: {predicted_disease}\n")
            file.write(f"Medical Advice: {medical_advice}\n")

    def view_health_report(self):
        try:
            with open(f"{self.patient_name}_health_report.txt", "r") as file:
                report = file.read()
            return f"Here is your health report:\n\n{report}"
        except FileNotFoundError:
            return "No health report found."

    def get_random_medical_advice(self):
        if self.medical_advice_list:
            advice = random.choice(self.medical_advice_list)
            return f"Here's a piece of medical advice for you:\n\n{advice}"
        else:
            return "Sorry, no medical advice is available at the moment."

    def add_medicine_reminder(self):
        med_name, ok = QInputDialog.getText(self, 'Medicine Name', 'Enter the name of the medicine 💊:')
        if ok and med_name:
            time_input, ok = QInputDialog.getText(self, 'Reminder Time', 'Enter the reminder time (HH:MM)⏰:')
            if ok and re.match("^[0-2][0-9]:[0-5][0-9]$", time_input):
                reminder_time = datetime.strptime(time_input, '%H:%M').time()
                self.medicine_reminders.append((med_name, reminder_time))
                self.schedule_reminder(med_name, reminder_time)

    def schedule_reminder(self, med_name, reminder_time):
        now = datetime.now()
        today_reminder_time = datetime.combine(now.date(), reminder_time)
        if now > today_reminder_time:
            today_reminder_time += timedelta(days=1)

        delay = (today_reminder_time - now).total_seconds()

        QTimer.singleShot(int(delay * 1000), lambda: self.show_reminder_popup(med_name))

    def show_reminder_popup(self, med_name):
        QMessageBox.information(self, 'Medicine Reminder', f"Time to take your medicine: {med_name}")

    def add_doctor_appointment(self):
        doctor, ok = QInputDialog.getText(self, 'Doctor Appointment', 'Enter the doctor name 👨‍⚕️:')
        if ok:
            time_str, ok = QInputDialog.getText(self, 'Doctor Appointment', 'Enter the appointment time (HH:MM AM/PM)⏰:')
            if ok and re.match(r'^\d{2}:\d{2} [APap][Mm]$', time_str):
                self.appointments.append((doctor, time_str))
                self.schedule_appointment(doctor, time_str)
            else:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid time in HH:MM AM/PM format.')
    def schedule_appointment(self, doctor, time_str):
        now = datetime.now()
        appointment_time = datetime.strptime(time_str, '%I:%M %p')
        appointment_time = now.replace(hour=appointment_time.hour, minute=appointment_time.minute, second=0, microsecond=0)
        if appointment_time < now:
            appointment_time += timedelta(days=1)
        delay = (appointment_time - now).total_seconds()
        QTimer.singleShot(int(delay * 1000), lambda: self.show_appointment_reminder(doctor))

    def show_appointment_reminder(self, doctor):
        QMessageBox.information(self, 'Appointment Reminder', f"You have an appointment with Dr. {doctor}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot_app = ChatbotApp()
    chatbot_app.show()
    sys.exit(app.exec_())
