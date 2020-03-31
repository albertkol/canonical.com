# Standard library
import base64
import json

# Packages
from html import unescape


base_url = "https://boards-api.greenhouse.io/v1/boards/Canonical/jobs"


def _parse_feed_department(feed_department):
    field = {
        "cloud engineering": "engineering",
        "device engineering": "engineering",
        "web and design": "design",
        "operations": "commercialops",
        "human resources": "hr",
    }

    if feed_department.lower() in field:
        return field[feed_department.lower()]

    return feed_department


class Greenhouse:
    def __init__(self, session):
        self.session = session

    def get_vacancies(self, department):
        feed = self.session.get(f"{base_url}?content=true").json()
        path_department = department.replace("-", "")
        vacancies = []
        for job in feed["jobs"]:
            feed_department = _parse_feed_department(
                job["metadata"][2]["value"].replace("-", "")
            )
            if path_department.lower() == "all":
                vacancies.append(
                    {
                        "title": job["title"],
                        "content": unescape(job["content"]),
                        "url": job["absolute_url"],
                        "location": job["location"]["name"],
                        "id": job["id"],
                        "employment": job["metadata"][0]["value"],
                        "date": job["metadata"][1]["value"],
                        "department": job["metadata"][2]["value"],
                        "management": job["metadata"][3]["value"],
                        "office": job["metadata"][4]["value"],
                    }
                )
            elif path_department.lower() == feed_department.lower():
                vacancies.append(
                    {
                        "title": job["title"],
                        "content": unescape(job["content"]),
                        "url": job["absolute_url"],
                        "location": job["location"]["name"],
                        "id": job["id"],
                        "employment": job["metadata"][0]["value"],
                        "date": job["metadata"][1]["value"],
                        "department": job["metadata"][2]["value"],
                        "management": job["metadata"][3]["value"],
                        "office": job["metadata"][4]["value"],
                    }
                )
        return vacancies

    def get_vacancies_by_skills(self, core_skills):
        feed = self.session.get(f"{base_url}?content=true").json()
        vacancies = []
        for job in feed["jobs"]:
            for skill in core_skills:
                if job["metadata"][5]["value"]:
                    if skill in job["metadata"][5]["value"]:
                        vacancies.append(
                            {
                                "title": job["title"],
                                "content": unescape(job["content"]),
                                "url": job["absolute_url"],
                                "location": job["location"]["name"],
                                "id": job["id"],
                                "employment": job["metadata"][0]["value"],
                                "date": job["metadata"][1]["value"],
                                "department": job["metadata"][2]["value"],
                                "management": job["metadata"][3]["value"],
                                "office": job["metadata"][4]["value"],
                                "core_skills": job["metadata"][5]["value"],
                            }
                        )
                        break

        return vacancies

    def get_vacancy(self, job_id):
        feed = self.session.get(f"{base_url}/{job_id}").json()
        if feed.get("status") == 404:
            return None
        else:
            job = {
                "id": job_id,
                "title": feed["title"],
                "content": unescape(feed["content"]),
                "location": feed["location"]["name"],
                "department": feed["metadata"][2]["value"],
            }
            return job

    # Default Job ID (1658196) is used below to submit CV without applying
    # for a specific job
    # https://boards-api.greenhouse.io/v1/boards/Canonical/jobs/1658196.
    def submit_application(
        self, api_key, form_data, form_files, job_id="1658196"
    ):
        # Encode the api_key to base64
        auth = (
            "Basic "
            + str(base64.b64encode(api_key.encode("utf-8")), "utf-8")[:-2]
        )
        # Encode the resume file to base64
        resume = base64.b64encode(form_files["resume"].read()).decode("utf-8")
        # Create headers for api sumbission
        headers = {"Content-Type": "application/json", "Authorization": auth}
        # Create payload for api submission
        payload = {
            "first_name": form_data["first_name"],
            "last_name": form_data["last_name"],
            "email": form_data["email"],
            "phone": form_data["phone"],
            "location": form_data["location"],
            "resume_content": resume,
            "resume_content_filename": form_files["resume"].filename,
        }

        # Add cover letter to the payload if exists
        if form_files["cover_letter"]:
            # Encode the cover_letter file to base64
            cover_letter = base64.b64encode(
                form_files["cover_letter"].read()
            ).decode("utf-8")
            payload["cover_letter_content"] = cover_letter
            payload["cover_letter_content_filename"] = form_files[
                "cover_letter"
            ].filename

        json_payload = json.dumps(payload)

        response = self.session.post(
            f"{base_url}/{job_id}", data=json_payload, headers=headers
        )

        return response
