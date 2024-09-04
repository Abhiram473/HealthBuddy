# HealthBuddy
🤖 Health Buddy AI Virtual Assistant 🩺  An AI-powered chatbot built with Python and PyQt5 to assist with health needs. Features include health checks, medical advice, medicine reminders, and appointment scheduling. Stay healthy with your virtual doctor! 💊🗓️⏰

Detailed description of each feature of my project Health Buddy AI Virtual Assistant 🩺:

1. Rule-Based Chatbot 🤖
Interactive Conversations: The chatbot uses a rule-based system powered by NLTK's Chat module. It responds to user inputs based on predefined patterns and reflections, offering a conversational interface that can greet users, provide general health advice, and guide them through various features.
Customizable Responses: The chatbot handles greetings, health-related inquiries, apologies, and more, ensuring a personalized experience for each user. The responses can be easily modified or extended by updating the pairs list.
Login Process: The chatbot initiates a simple login process that asks for the user's name. This process is crucial for accessing personalized health reports and other features.
2. User Interface with PyQt5 💻
Main Window: The application opens in a maximized window that hosts the chatbot interface, including a chat history view, a user input field, and a send button.
Dark and Light Theme Support 🌑🌕: Users can switch between dark and light themes for a more comfortable viewing experience, controlled by the toggle_theme function.
Monospace Fonts: The interface uses a monospace font to ensure clear and uniform text display, enhancing readability, especially for the chat history.
3. Health Check and Report 🩺
Collecting Health Data: The application allows users to perform a health check by answering a series of questions related to their symptoms, age, gender, blood pressure, and cholesterol levels. The responses are validated to ensure accurate data entry.
Health Report Generation: Once the health check is completed, the application saves the data in a text file named after the user. This report includes all the provided health information, timestamped for future reference.
Viewing Health Reports: Users can easily retrieve and view their health reports within the application. If no report is found, the app encourages users to perform a health check first.
4. Daily Medical Advice 💡
Advice from CSV: The application loads a list of medical tips from a CSV file and provides a random piece of advice each time the user requests it. This feature ensures that users receive helpful health tips regularly.
Randomized Tips: The randomness in tip selection adds a dynamic element, encouraging users to interact with the app daily for new advice.
5. Medicine Reminders 💊
Setting Reminders: Users can set reminders for taking their medication by entering the medicine name and the time for the reminder. The app validates the time input to ensure reminders are set correctly.
Automated Alerts: The application schedules reminders using Qt's QTimer, ensuring that users receive a popup alert at the specified time, reminding them to take their medication.
6. Doctor Appointments 🗓️
Appointment Scheduling: Users can schedule doctor appointments by providing the doctor's name and the appointment time. The time is validated in a 12-hour format (AM/PM) to avoid errors.
Reminder System: Similar to medicine reminders, the app schedules an alert to remind the user of their appointment with the doctor, ensuring they don’t miss their scheduled visits.
7. Error Handling and Validation 🚦
Input Validation: The application includes multiple layers of input validation, ensuring that users provide the correct format for names, times, and other health-related data.
Exception Handling: The app handles potential errors, such as issues loading the CSV file for medical advice, by displaying user-friendly error messages through QMessageBox.
8. Data Persistence and Management 📂
Health Report Storage: User health data is stored locally in text files, allowing easy retrieval and management of health records.
Persistent Reminders and Appointments: The medicine reminders and doctor appointments are stored within the session, ensuring that the app will alert users even after they have set multiple reminders or appointments.
