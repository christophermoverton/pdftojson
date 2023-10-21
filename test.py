import spacy
import re

nlp = spacy.load("en_core_web_sm")

# Define regular expressions for extracting dates in various formats
date_pattern = re.compile(r"(\w+\s\d{4}[\s—-]?\s\w+\s\d{4}|\w+\s\d{4})")

# Sample resume text
resume_text = """CHRISTOPHER OVERTON
DATA ENGINEERING
OVERLAND PARK, UNITED STATES 9134810582

DETAILS
Overland Park
United States
9134810582
christophermoverton@gmail.com

LINKS
linkedin
github
hackerrank

SKILLS
Git
SQL
Python
Java
Scala
Swift
Xcode
Visual Studio Code

PROFILE
As a devoted Stay-at-Home Parent, I've excelled in multitasking. Accomplished in app
development, scripting, touch UIs, and translation skills, I infuse every team with
adaptability and precision.

EMPLOYMENT HISTORY
Customer Service at Verizon Wireless, Bellevue
August 2000 — January 2005
• Proficiently managed billing inquiries and addressed account-related issues with precision.
• Provided expert guidance on product plans and offered top-tier support for wireless phone products.
• Delivered technical expertise for wireless issues, ensuring swift and effective problem resolution.

Software Developer at Harvest Moon Studios, Los Angeles
July 2016 — February 2017
• Spearheaded the development of an iOS application for NOAA and the National Park Service, with dynamic animated screen transitions, captivating photo galleries, and seamless touch-supported scrollable interfaces.
• Orchestrated and optimized an expansive image library, facilitating efficient batch page instancing across diverse hardware platforms.
• Leveraged Swift in Xcode for the rapid and robust development of the iOS application.
• Pioneered a cutting-edge .NET WPF application, empowering LA civic spaces with touch and multi-touch gesture capabilities, multifaceted page navigation, and visually engaging user interface manipulations, including custom slide tile animations.
• Fostered collaborative synergy within development forums and GitHub for seamless project execution.
• Transformed and transposed a Java-based graphics script into C# for enhanced performance and efficiency.
• Engineered Python scripts to create a dynamic physics collision system for immersive animation rendering.
• Innovatively sourced Heightmap data from public USGS and Open Source GIS software, utilizing native Python scripts for vivid terrain colorization and striking hillshading effects.

Software Developer at SVP Consulting, New Jersey
February 2018 — April 2018
• Engineered a high-performance Forex trading console application, merging Python and MQL4, harnessing the potential of a Forex API.
• Spearheaded the integration of threaded asynchronous handling and event listeners, enabling automated trading with lightning speed.
• Innovatively employed pipenv to manage Python modules within dynamic virtual environments, optimizing workflow efficiency.
• Transformed raw JSON trade exchange data into powerful Pandas dataframe objects, propelling trade analysis and automation.
• Pioneered data import and export functionalities for .txt-based files, streamlining data management.
• Masterfully employed Git for version control, enhancing project management and collaboration.
• Executed the entire project independently, from inception to completion, showcasing a strong foundation of skills.
• Explore my portfolio on Upwork at https://www.upwork.com/freelancers/~016e516f5ff651848b?viewMode=1.

Software Development Support at 3 Fuerzas Technology Solutions (EDZSystems), Overland Park
January 2018 — March 2018
• Spearheaded critical iOS and Android application beta improvements, ensuring rapid deployment on the Google Play Store and Apple Store.
• Revamped production-side code for native and third-party frameworks, guaranteeing polished and high-performance releases.
• Led a comprehensive code updates, mastering data importation models and seamlessly implementing needed integration.
• Utilized XCode and Android Studio, skillfully coding in Objective-C, Swift, Java, and REST for cross-platform excellence.
• Operated seamlessly within MacOS and Windows environments, utilizing Atlassian Bitbucket and Git for streamlined version control.
• Skillfully navigated complex Android and iOS applications, showcasing adaptability and expert problem-solving.

Stay at Home Parent at University of Kansas, KS Olathe Kansas
April 2018 — Present
• Nurtured my daughter's well-being from birth to age 4, serving as her primary caregiver.
• Seized a precious opportunity to be actively present during her formative years before she embarked on her educational journey.
• Eagerly poised to relaunch my career in development, harnessing newfound experiences and skills cultivated during my time as a dedicated parent.

EDUCATION
Bachelors of Science Mathematics, University of Kansas
Hackerrank, Basic Java Certification
August, 2023, Hackerrank
January 2023
Certificate Link
Hackerrank, Basic Python Certification
August, 2023, Basic Python Certification Hackerrank
January 2023
Certificate Link
Coursera, Introduction to Relational Databases (IBM)
September, 2023 - October, 2023, IBM
January 2023
https://coursera.org/share/9f78c1fe77e0dcd3d66e3e2bb22db1e9
Coursera Python Project For Data Engineering, IBM
September 2023 — October 2023
https://www.coursera.org/account/accomplishments/verify/LLY79EQJH8N4
Coursera, Python For Data Science,AI, and Development, IBM
September 2023 — September 2023
Certificate Link
Coursera, Functional Programming Principles in Scala , École Polytechnique Fédérale de Lausanne
September 2023 — October 2023
Certificate Link
Coursera, Introduction to Data Engineering, IBM
September 2023 — September 2023
Certificate Link"""

# Function to parse resume
def parse_resume(resume_text):
    doc = nlp(resume_text)

    resume_data = {
        "name": None,
        "contact": {
            "location": None,
            "phone": None,
            "email": None
        },
        "links": [],
        "skills": [],
        "profile": None,
        "employment_history": [],
        "education": []
    }

    section = None
    for entity in doc.ents:
        print(entity)
    for token in doc:
        if token.text == "PROFILE":
            section = "profile"
        elif token.text == "EMPLOYMENT":
            section = "employment_history"
        elif token.text == "EDUCATION":
            section = "education"
        elif token.text == "LINKS":
            section = "links"
        elif token.text == "SKILLS":
            section = "skills"
        elif token.text == "DETAILS":
            section = "contact"
        elif section:
            if section == "profile":
                resume_data[section] = (resume_data[section] or "") + " " + token.text
            elif section == "contact":
                if re.match(r"[0-9]{10}", token.text):
                    resume_data[section]["phone"] = token.text
                elif re.match(r"[^@]+@[^@]+\.[^@]+", token.text):
                    resume_data[section]["email"] = token.text
                else:
                    resume_data[section]["location"] = (resume_data[section]["location"] or "") + " " + token.text
            else:
                resume_data[section].append(token.text)
        
    # Extract dates from employment history and education sections
    for match in date_pattern.finditer(resume_text):
        if "EMPLOYMENT" in resume_text[match.start():match.end()]:
            resume_data["employment_history"].append({
                "dates": match.group()
            })
        elif "EDUCATION" in resume_text[match.start():match.end()]:
            resume_data["education"].append({
                "dates": match.group()
            })

    return resume_data

# Parse the resume
parsed_resume = parse_resume(resume_text)

# Print the structured data as JSON
import json
#print(json.dumps(parsed_resume, indent=4))
