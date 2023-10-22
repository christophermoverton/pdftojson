import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pagetext = page.extract_text()
            
            pagetext+='\n'
            text += pagetext
    return text

import spacy
import re

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")
date_pattern = re.compile(r"(\w+\s\d{4}[\s—-]?\s\w+\s\d{4}|\w+\s\d{4})")
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
        if "EMPLOYMENT HISTORY" in resume_text[match.start():match.end()]:
            resume_data["employment_history"].append({
                "dates": match.group()
            })
        elif "EDUCATION" in resume_text[match.start():match.end()]:
            resume_data["education"].append({
                "dates": match.group()
            })

    return resume_data

def parse_resume2(resume_text):
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
    # Function to extract sections using regular expressions
    def extract_section(section_name, text):
        pattern = r"(?i)" + re.escape(section_name) + r"\b"
        match = re.search(pattern, text)
        if match:
            start = match.start()
            if section_name == "EDUCATION":
                return text[start:].strip()
            elif section_name == "DETAILS":
                next_section = re.search(r"LINKS", text)
                if next_section:
                    end = next_section.start()
                return text[start:end].strip()
            elif section_name == "LINKS":
                next_section = re.search(r"SKILLS", text)
                if next_section:
                    end = next_section.start()
                return text[start:end].strip()
            elif section_name == "SKILLS":
                next_section = re.search(r"PROFILE", text)
                if next_section:
                    end = next_section.start()
                return text[start:end].strip()
            elif section_name == "PROFILE":
                next_section = re.search(r"EMPLOYMENT HISTORY", text)
                if next_section:
                    end = next_section.start()
                return text[start:end].strip()
            #end = re.search(r"\n\n", text[start:]).end() + start
            elif section_name == "EMPLOYMENT HISTORY":
                # For the employment history section, consider it doesn't end with '\n\n'
                next_section = re.search(r"EDUCATION", text)
                if next_section:
                    end = next_section.start()
                return text[start:end].strip()
            
        return None
    
    def extract_jobs(text):
        job_entries = re.split(r'\n(?=\w{3,}\s\d{4}\s—\s\w{3,}\s\d{0,4})', text)
        jobs = []
        job_titles = []
        job_locs = []
        job_period = []
        job_duties = []
        for entry in job_entries:
            j_title_loc = entry.split('\n')[-1]
            j_title_split = entry.split('\n')
            duties_end_iter = -1
            if ',' in j_title_loc:
                jtlsplit = j_title_loc.split(',')
                job_titles.append(jtlsplit[0])
                job_locs.append(jtlsplit[1])
                
            else:
                job_locs.append(j_title_loc)
                job_titles.append(j_title_split[-2])
                duties_end_iter = -2
            job_period.append(j_title_split[0])
            job_duties.append([j_title_split[1:duties_end_iter]])
        
        job_period = job_period[1:]
        job_titles = job_titles[:-1]
        job_locs = job_locs[:-1]
        job_duties = job_duties[1:]

        for index ,jtitle in enumerate(job_titles):
            ##lines = entry.strip().split('\n')
            jtitle_company = jtitle.split("at")
            job_info = {
                'job_title': jtitle_company[0].strip(),
                'company_name': jtitle_company[1].strip(),
                'company_location': job_locs[index],
                'employment_period': job_period[index],
                'responsibilities': job_duties[index][0],
            }
            jobs.append(job_info)

        return jobs
    
    def extract_education(text):
        edu_entries = re.split(r',', text)
        edu_course_titles = []
        edu_universities = []
        edu_dates = []
        edu_links = []
        for entry in edu_entries:
            nsplitentry = re.split(r'\n',entry)
            if len(nsplitentry) == 1:
                edu_course_titles[-1] += ','+nsplitentry[0]
            else:
                edu_universities.append(nsplitentry[0])
                edu_course_titles.append(nsplitentry[-1])
                if len(nsplitentry) == 2:
                    edu_dates.append(None)
                    edu_links.append(None)
                else:
                    rattrs = nsplitentry[1:-1]
                    dlinks = [edu_dates,edu_links]
                    for i,attr in enumerate(rattrs):
                        dlinks[i].append(attr)
                    if len(rattrs) == 1:
                        edu_links.append(None)
        eds = []
        edu_course_titles = edu_course_titles[0:-1]
        edu_dates = edu_dates[1:]
        edu_links = edu_links[1:]
        edu_universities = edu_universities[1:]
        for index, edu_course_title in enumerate(edu_course_titles):
            edu_info = {"course_degree": edu_course_title, "university": edu_universities[index],
                        "date": edu_dates[index], "links": edu_links[index]}
            eds.append(edu_info)
        return eds
        #edu_entries = re.split(r'\n(?=\w{3,}\s\d{4}\s—{0,1}\s\w{0,}\s\d{0,4})', text)

        

    # Extract personal information
    personal_info = "Christopher Overton" #extract_section("CHRISTOPHER OVERTON", resume_text)
    contact_info = extract_section("DETAILS", resume_text)
    contact_info_dict = {"location":"Overland Park,  United States", "phone":"9134810582",
                         "email":"christophermoverton@gmail.com"}

    # Extract skills
    skills_section = extract_section("SKILLS", resume_text)
    skills = [skill.strip() for skill in skills_section.split('\n')]

    # Extract profile
    profile_section = extract_section("PROFILE",resume_text)

    # Extract employment history
    employment_history = extract_section("EMPLOYMENT HISTORY", resume_text)
    #print(employment_history)
    jobs = extract_jobs(employment_history)

    #jobs = [job.replace('\n', ' ').strip() for job in jobs]

    # Extract education
    education_section = extract_section("EDUCATION", resume_text)
    education = extract_education(education_section)
    #education = [edu.strip() for edu in education_section.split('\n')]

    # Extract links
    links_section = extract_section("LINKS", resume_text)
    links = [link.strip() for link in links_section.split('\n')]
    resume_data["name"] = personal_info
    resume_data["contact"] = contact_info_dict
    resume_data["skills"] = skills
    resume_data["links"] = links
    resume_data["profile"] = profile_section
    resume_data["employment_history"] = jobs
    resume_data["education"] = education
    return resume_data

# Example usage:
resume_text = """
John Doe
johndoe@email.com
(123) 456-7890

Education:
Bachelor of Science in Computer Science
XYZ University
Graduated: 2020

Experience:
Software Engineer
ABC Corp
2018-2021
"""

#parsed_resume = parse_resume(resume_text)
#print(parsed_resume)


import json


def convert_to_json(pdf_path):
    pdf_text = extract_text_from_pdf(pdf_path)
    print(pdf_text)
    structured_data = parse_resume2(pdf_text)
    print(structured_data)
    #structured_data = {}  # Populate this dictionary with the parsed data
    json_data = json.dumps(structured_data, indent=4)
    return json_data


def save_to_json_file(pdf_path, output_path):
    json_data = convert_to_json(pdf_path)
    print(json_data)
    with open(output_path, 'w') as json_file:
        json_file.write(json_data)

save_to_json_file("C:\\Users\\chris\\OneDrive\\Documents\\pdftojson\\Coresume9.pdf","myresume.json")