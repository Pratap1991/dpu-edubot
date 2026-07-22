"""
DPU EduBot — Mock ERP student directory (POC only)
Shared by erp_demo.py and app/main.py so both use the same demo data.
Replace with a real ERP API/database lookup when available.
"""

MOCK_STUDENTS = {
    "ERP001": {
        "name": "Pratap Nayadkar", "program": "MBA Online", "batch": "MBA Jan 2026",
        "semester": 1, "specialization": "Marketing", "prn": "DPU2026MBA001",
        "mentor": "Ms. Sneha Mehta",
        "fees": {"total": 189400, "paid": 50000, "outstanding": 139400,
                 "sem1": "Paid (Rs 50,000 on 5 Jan 2026)",
                 "sem2": "Due Rs 50,000 by 15 Feb 2026"},
        "assignments": {"total": 14, "submitted": 9, "pending": 5,
                        "pending_list": [
                            "OMBC-103 Management Accounting — Assignment 2",
                            "OMBC-105 Business Communication — Assignment 1 & 2",
                            "OMBC-107 Environmental Awareness — Assignment 1 & 2"]},
        "exam": {"form": "Submitted", "admit_card": "Available on ERP",
                 "exam_date": "5 March 2026 (Tentative)", "result": "Not declared",
                 "backlog": []},
        "attendance": 78,
        "books": "Delivered on 12 January 2026"
    },
    "ERP002": {
        "name": "Riya Sharma", "program": "MBA Online", "batch": "MBA Jan 2026",
        "semester": 1, "specialization": "Finance", "prn": "DPU2026MBA002",
        "mentor": "Mr. Vivek Nair",
        "fees": {"total": 189400, "paid": 100000, "outstanding": 89400,
                 "sem1": "Paid", "sem2": "Paid (Rs 50,000 on 5 Feb 2026)"},
        "assignments": {"total": 14, "submitted": 14, "pending": 0, "pending_list": []},
        "exam": {"form": "Submitted", "admit_card": "Available on ERP",
                 "exam_date": "5 March 2026", "result": "Not declared", "backlog": []},
        "attendance": 92,
        "books": "Delivered on 10 January 2026"
    },
    "ERP003": {
        "name": "Arjun Mehta", "program": "MBA Online", "batch": "MBA Jan 2026",
        "semester": 1, "specialization": "Operations Management", "prn": "DPU2026MBA003",
        "mentor": "Ms. Priya Rao",
        "fees": {"total": 189400, "paid": 0, "outstanding": 189400,
                 "sem1": "OVERDUE — Rs 50,000 pending since 15 Jan 2026",
                 "sem2": "Not yet due"},
        "assignments": {"total": 14, "submitted": 0, "pending": 14,
                        "pending_list": ["All assignments locked — fees pending"]},
        "exam": {"form": "Not submitted (fees pending)",
                 "admit_card": "Not eligible — pay fees first",
                 "exam_date": "5 March 2026", "result": "Not eligible", "backlog": []},
        "attendance": 0,
        "books": "Not dispatched — awaiting fee payment"
    },
    "ERP006": {
        "name": "Sneha Iyer", "program": "BBA Online", "batch": "BBA Jan 2026",
        "semester": 1, "specialization": "Marketing", "prn": "DPU2026BBA042",
        "mentor": "Ms. Priya Rao",
        "fees": {"total": 165000, "paid": 55000, "outstanding": 110000,
                 "sem1": "Paid (Rs 55,000 on 7 Jan 2026)",
                 "sem2": "Due Rs 55,000 by 1 March 2026"},
        "assignments": {"total": 10, "submitted": 7, "pending": 3,
                        "pending_list": [
                            "OBBAC-103 Introduction to Economics — Assignment 2",
                            "OBBAC-105 Business English — Assignment 1 & 2"]},
        "exam": {"form": "Submitted", "admit_card": "Available on ERP",
                 "exam_date": "20 May 2026", "result": "Not declared", "backlog": []},
        "attendance": 81,
        "books": "Delivered on 14 January 2026"
    },
    "ERP009": {
        "name": "Vikram Joshi", "program": "MBA Online", "batch": "MBA Jul 2024",
        "semester": 4, "specialization": "Business Analytics", "prn": "DPU2024MBA152",
        "mentor": "Mr. Arjun Kumar",
        "fees": {"total": 189400, "paid": 189400, "outstanding": 2500,
                 "sem1": "Paid", "sem2": "Paid"},
        "assignments": {"total": 14, "submitted": 14, "pending": 0, "pending_list": []},
        "exam": {"form": "Submitted (with 1 backlog)", "admit_card": "Available on ERP",
                 "exam_date": "10 March 2026",
                 "result": "Sem 1: 7.2 | Sem 2: 7.5 | Sem 3: FAIL in OMBC-303",
                 "backlog": ["OMBC-303 Strategic Management"]},
        "attendance": 86,
        "books": "Delivered on 18 January 2026"
    },
}
