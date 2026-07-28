"""
Survey seed data: 10 companies, each with 12 questions mixing all
four question types. seed_surveys() is idempotent — it only inserts
data if the surveys table is currently empty.
"""

from extensions import db
from models import Survey, Question, Option

SATISFACTION = ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"]
FREQUENCY = ["Never", "Rarely", "Sometimes", "Often", "Always"]
LIKELIHOOD = ["Very Unlikely", "Unlikely", "Neutral", "Likely", "Very Likely"]
AGE_GROUPS = ["Under 18", "18-24", "25-34", "35-44", "45+"]

SURVEYS_DATA = [
    {
        "company": "KFC Kenya",
        "title": "Fast Food Preferences & Dining Experience",
        "description": "Help KFC Kenya understand your fast food habits and improve your dining experience across all branches.",
        "reward": 70,
        "estimated_time": 7,
        "questions": [
            {"question": "How often do you eat at KFC?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Have you visited a KFC outlet in the last 30 days?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which meal do you usually order?", "question_type": "multiple_choice", "options": ["Chicken Bucket", "Zinger Burger", "Streetwise Meal", "Twister Wrap"]},
            {"question": "How satisfied are you with the food quality?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How satisfied are you with the speed of service?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Do you use the KFC mobile app or website to order?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which branch do you visit most often?", "question_type": "text"},
            {"question": "What is your age group?", "question_type": "multiple_choice", "options": AGE_GROUPS},
            {"question": "How likely are you to recommend KFC to a friend?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "Would you like to see more vegetarian options on the menu?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What would you like KFC to improve?", "question_type": "text"},
            {"question": "How do you usually pay for your order?", "question_type": "multiple_choice", "options": ["M-Pesa", "Cash", "Card", "KFC App Wallet"]},
        ],
    },
    {
        "company": "TotalEnergies Kenya",
        "title": "Fuel Station Experience Survey",
        "description": "Share your experience at TotalEnergies fuel stations to help us improve service delivery nationwide.",
        "reward": 80,
        "estimated_time": 8,
        "questions": [
            {"question": "How often do you fuel at TotalEnergies stations?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Do you use the TotalEnergies loyalty card?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which service do you use most at the station?", "question_type": "multiple_choice", "options": ["Fuel", "Car Wash", "Convenience Shop", "Lubricants"]},
            {"question": "How satisfied are you with attendant service?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How satisfied are you with station cleanliness?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Have you experienced fuel shortages at your usual station?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which station do you visit most often?", "question_type": "text"},
            {"question": "How likely are you to recommend TotalEnergies to others?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "Do you prefer self-service or attendant-assisted fueling?", "question_type": "multiple_choice", "options": ["Self-service", "Attendant-assisted", "No preference"]},
            {"question": "Would you be interested in an EV charging option?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What would improve your experience at the station?", "question_type": "text"},
            {"question": "How do you usually pay?", "question_type": "multiple_choice", "options": ["M-Pesa", "Cash", "Card", "Fleet Account"]},
        ],
    },
    {
        "company": "Safaricom",
        "title": "Mobile Data & Network Experience",
        "description": "Tell us about your mobile data usage habits and network experience to help Safaricom serve you better.",
        "reward": 90,
        "estimated_time": 9,
        "questions": [
            {"question": "How would you rate your network coverage?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Do you use M-Pesa daily?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which bundle do you purchase most often?", "question_type": "multiple_choice", "options": ["Daily Bundle", "Weekly Bundle", "Monthly Bundle", "Night Bundle"]},
            {"question": "How satisfied are you with data speeds?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How often do you experience call drops?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Do you use the My Safaricom App?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What device do you primarily use?", "question_type": "multiple_choice", "options": ["Smartphone", "Feature Phone", "Tablet", "Mobile WiFi Router"]},
            {"question": "How likely are you to switch to another network?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "Which Safaricom service do you value most?", "question_type": "text"},
            {"question": "Have you contacted Safaricom customer care in the last month?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What would you like Safaricom to improve?", "question_type": "text"},
            {"question": "What is your age group?", "question_type": "multiple_choice", "options": AGE_GROUPS},
        ],
    },
    {
        "company": "Equity Bank",
        "title": "Digital Banking Experience Survey",
        "description": "Help Equity Bank understand how you use mobile and internet banking to improve digital services.",
        "reward": 100,
        "estimated_time": 10,
        "questions": [
            {"question": "How often do you use the Equity Mobile App?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Do you have an Eazzy Banking account?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which service do you use most?", "question_type": "multiple_choice", "options": ["Mobile Banking", "ATM", "Branch Banking", "Agency Banking"]},
            {"question": "How satisfied are you with app reliability?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How satisfied are you with customer support?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Have you used Eazzy Loan or Eazzy Biz?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "How likely are you to recommend Equity Bank?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "Which branch do you visit most often?", "question_type": "text"},
            {"question": "Do you feel your banking data is secure?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What type of account do you hold?", "question_type": "multiple_choice", "options": ["Personal", "Business", "Diaspora", "Student"]},
            {"question": "What would you like improved in the mobile app?", "question_type": "text"},
            {"question": "What is your age group?", "question_type": "multiple_choice", "options": AGE_GROUPS},
        ],
    },
    {
        "company": "NCBA",
        "title": "Loop by NCBA App Experience",
        "description": "Share your feedback on the Loop app and NCBA's digital banking products.",
        "reward": 85,
        "estimated_time": 8,
        "questions": [
            {"question": "How often do you use the Loop app?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Do you have an NCBA Loop account?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which feature do you use most in Loop?", "question_type": "multiple_choice", "options": ["Savings Pot", "Loans", "Bill Payments", "Send Money"]},
            {"question": "How satisfied are you with the app's design?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How satisfied are you with loan turnaround time?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Have you taken a loan through Loop?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "How likely are you to recommend Loop to others?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "What other NCBA products do you use?", "question_type": "text"},
            {"question": "Do you also bank with a traditional NCBA branch?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What type of account do you hold?", "question_type": "multiple_choice", "options": ["Personal", "Business", "Student", "Asset Finance"]},
            {"question": "What would you like NCBA to improve?", "question_type": "text"},
            {"question": "What is your age group?", "question_type": "multiple_choice", "options": AGE_GROUPS},
        ],
    },
    {
        "company": "Java House",
        "title": "Coffee & Dining Experience Survey",
        "description": "Tell Java House about your café visits, favorite menu items, and overall dining experience.",
        "reward": 65,
        "estimated_time": 6,
        "questions": [
            {"question": "How often do you visit Java House?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Have you visited Java House in the last 2 weeks?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What do you usually order?", "question_type": "multiple_choice", "options": ["Coffee", "Breakfast", "Lunch/Dinner", "Pastries"]},
            {"question": "How satisfied are you with food quality?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How satisfied are you with the ambience?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Do you use Java House for meetings or work?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which branch do you frequent?", "question_type": "text"},
            {"question": "How likely are you to recommend Java House?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "Do you order via delivery apps?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What time of day do you usually visit?", "question_type": "multiple_choice", "options": ["Morning", "Afternoon", "Evening", "Late Night"]},
            {"question": "What menu item would you like added?", "question_type": "text"},
            {"question": "What is your age group?", "question_type": "multiple_choice", "options": AGE_GROUPS},
        ],
    },
    {
        "company": "Naivas",
        "title": "Supermarket Shopping Experience",
        "description": "Help Naivas improve in-store experience, product range, and checkout speed.",
        "reward": 75,
        "estimated_time": 7,
        "questions": [
            {"question": "How often do you shop at Naivas?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Did you shop at Naivas in the last 7 days?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What do you shop for most?", "question_type": "multiple_choice", "options": ["Groceries", "Household Items", "Electronics", "Fresh Produce"]},
            {"question": "How satisfied are you with checkout speed?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How satisfied are you with product availability?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Do you use the Naivas loyalty card?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which branch do you shop at most?", "question_type": "text"},
            {"question": "How likely are you to recommend Naivas?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "Do you use self-checkout when available?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "How do you usually pay?", "question_type": "multiple_choice", "options": ["M-Pesa", "Cash", "Card", "Loyalty Points"]},
            {"question": "What would you like Naivas to improve?", "question_type": "text"},
            {"question": "What is your age group?", "question_type": "multiple_choice", "options": AGE_GROUPS},
        ],
    },
    {
        "company": "Carrefour Kenya",
        "title": "Retail & Product Range Feedback",
        "description": "Share your Carrefour shopping experience to help improve product range and store layout.",
        "reward": 80,
        "estimated_time": 8,
        "questions": [
            {"question": "How often do you shop at Carrefour?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Have you shopped online via the Carrefour app?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What category do you shop for most?", "question_type": "multiple_choice", "options": ["Groceries", "Electronics", "Home & Living", "Fashion"]},
            {"question": "How satisfied are you with store layout?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How satisfied are you with pricing?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Have you used Carrefour home delivery?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "Which mall/branch do you visit most?", "question_type": "text"},
            {"question": "How likely are you to recommend Carrefour?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "Do you compare prices with other supermarkets?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "How do you usually pay?", "question_type": "multiple_choice", "options": ["M-Pesa", "Cash", "Card", "Carrefour Wallet"]},
            {"question": "What product range would you like expanded?", "question_type": "text"},
            {"question": "What is your age group?", "question_type": "multiple_choice", "options": AGE_GROUPS},
        ],
    },
    {
        "company": "Jumia Kenya",
        "title": "Online Shopping Experience Survey",
        "description": "Tell Jumia about your online shopping, delivery, and customer service experience.",
        "reward": 90,
        "estimated_time": 9,
        "questions": [
            {"question": "How often do you shop on Jumia?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Have you made a purchase on Jumia in the last month?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What do you buy most on Jumia?", "question_type": "multiple_choice", "options": ["Electronics", "Fashion", "Home Appliances", "Groceries"]},
            {"question": "How satisfied are you with delivery times?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How satisfied are you with product quality received?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Have you used Jumia Pay?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "How likely are you to recommend Jumia?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "Have you ever returned a product?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What payment method do you use most?", "question_type": "multiple_choice", "options": ["M-Pesa", "Cash on Delivery", "Card", "Jumia Pay"]},
            {"question": "Which city do you usually order to?", "question_type": "text"},
            {"question": "What would you like Jumia to improve?", "question_type": "text"},
            {"question": "What is your age group?", "question_type": "multiple_choice", "options": AGE_GROUPS},
        ],
    },
    {
        "company": "Kenya Airways",
        "title": "Air Travel Experience Survey",
        "description": "Share your Kenya Airways flying experience to help improve in-flight and booking services.",
        "reward": 100,
        "estimated_time": 12,
        "questions": [
            {"question": "How often do you fly with Kenya Airways?", "question_type": "radio", "options": FREQUENCY},
            {"question": "Have you flown with Kenya Airways in the last year?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What class do you usually fly?", "question_type": "multiple_choice", "options": ["Economy", "Premium Economy", "Business", "First Class"]},
            {"question": "How satisfied are you with in-flight service?", "question_type": "radio", "options": SATISFACTION},
            {"question": "How satisfied are you with the booking process?", "question_type": "radio", "options": SATISFACTION},
            {"question": "Are you a member of the Asante Rewards program?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "How likely are you to fly Kenya Airways again?", "question_type": "radio", "options": LIKELIHOOD},
            {"question": "Have you experienced a flight delay in the past year?", "question_type": "yes_no", "options": ["Yes", "No"]},
            {"question": "What type of trips do you take most?", "question_type": "multiple_choice", "options": ["Domestic", "Regional", "International Business", "International Leisure"]},
            {"question": "Which route do you fly most often?", "question_type": "text"},
            {"question": "What would you like Kenya Airways to improve?", "question_type": "text"},
            {"question": "What is your age group?", "question_type": "multiple_choice", "options": AGE_GROUPS},
        ],
    },
]


def seed_surveys():
    if Survey.query.first():
        return  # already seeded

    for entry in SURVEYS_DATA:
        survey = Survey(
            company=entry["company"],
            title=entry["title"],
            description=entry["description"],
            reward=entry["reward"],
            estimated_time=entry["estimated_time"],
            status="active",
        )
        db.session.add(survey)
        db.session.flush()  # get survey.id before inserting questions

        for q in entry["questions"]:
            question = Question(
                survey_id=survey.id,
                question=q["question"],
                question_type=q["question_type"],
            )
            db.session.add(question)
            db.session.flush()

            for opt_text in q.get("options", []):
                db.session.add(Option(question_id=question.id, option_text=opt_text))

    db.session.commit()
    print(f"[seed] Created {len(SURVEYS_DATA)} surveys with questions and options")
