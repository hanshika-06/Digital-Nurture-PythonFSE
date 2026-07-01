import datetime
from pymongo import MongoClient, ASCENDING

# =============================================================================
# HANDS-ON 5: MongoDB — Document Modelling, CRUD & Aggregation
# =============================================================================

"""
MongoDB Schema Design for the College System:
---------------------------------------------
The 'feedback' collection holds course feedback documents. This schema leverages
MongoDB's dynamic structure to handle varied formats (such as optional tags and attachments) 
without rigid schemas or joins.

Sample Document Structure:
{
    "_id": ObjectId(),
    "student_id": 1,
    "course_code": "CS101",
    "semester": "2022-ODD",
    "rating": 4,
    "comments": "Excellent teaching. Would recommend.",
    "tags": ["challenging", "well-structured", "good-examples"],
    "submitted_at": ISODate("2022-11-30T10:15:00Z"),
    "attachments": [
        { "filename": "notes.pdf", "size_kb": 240 }
    ]
}
"""

def connect_to_mongodb():
    # Attempt to connect to local MongoDB. Adjust URL if necessary.
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    db = client["college_nosql"]
    return client, db

def run_mongodb_exercise():
    client, db = connect_to_mongodb()
    feedback_col = db["feedback"]
    
    # Reset collection for clean execution
    feedback_col.delete_many({})
    
    # -------------------------------------------------------------------------
    # Task 1: Create the Collection and Insert Documents
    # -------------------------------------------------------------------------
    print("--- Task 1: Inserting Feedback Documents ---")
    
    feedback_docs = [
        {
            "student_id": 1,
            "course_code": "CS101",
            "semester": "2022-ODD",
            "rating": 5,
            "comments": "Absolutely loved the Python course! Highly recommended.",
            "tags": ["challenging", "well-structured", "fun"],
            "submitted_at": datetime.datetime(2022, 11, 15, 10, 0),
            "attachments": [{"filename": "cheatsheet.pdf", "size_kb": 120}]
        },
        {
            "student_id": 2,
            "course_code": "CS101",
            "semester": "2022-ODD",
            "rating": 4,
            "comments": "Great explanations, but assignments were a bit hard.",
            "tags": ["challenging", "good-examples"],
            "submitted_at": datetime.datetime(2022, 11, 20, 14, 30),
            "attachments": []
        },
        {
            "student_id": 3,
            "course_code": "CS101",
            "semester": "2022-ODD",
            "rating": 5,
            "comments": "The best coding course I have ever taken.",
            "tags": ["fun", "well-structured"],
            "submitted_at": datetime.datetime(2022, 11, 22, 9, 15),
            "attachments": [{"filename": "final_project.zip", "size_kb": 4500}]
        },
        {
            "student_id": 4,
            "course_code": "CS102",
            "semester": "2022-ODD",
            "rating": 2,
            "comments": "Found the DBMS content outdated and boring.",
            "tags": ["dull", "slow"],
            "submitted_at": datetime.datetime(2022, 11, 25, 16, 0),
            "attachments": []
        },
        {
            "student_id": 5,
            "course_code": "CS102",
            "semester": "2022-ODD",
            "rating": 3,
            "comments": "Decent SQL exercises but lectures were dry.",
            "tags": ["good-examples", "dry"],
            "submitted_at": datetime.datetime(2022, 11, 26, 11, 45),
            "attachments": [{"filename": "sql_queries.txt", "size_kb": 15}]
        },
        {
            "student_id": 6,
            "course_code": "EC101",
            "semester": "2021-EVEN",
            "rating": 5,
            "comments": "Very interesting labs on transistors.",
            "tags": ["fun", "practical"],
            "submitted_at": datetime.datetime(2021, 6, 10, 15, 30),
            "attachments": []
        },
        {
            "student_id": 7,
            "course_code": "EC101",
            "semester": "2022-ODD",
            "rating": 1,
            "comments": "Hard to follow circuit schematics.",
            "tags": ["confusing", "hard"],
            "submitted_at": datetime.datetime(2022, 12, 1, 13, 0),
            "attachments": []
        },
        {
            "student_id": 8,
            "course_code": "ME101",
            "semester": "2021-EVEN",
            "rating": 4,
            "comments": "Thermodynamics was tough but teacher was helpful.",
            "tags": ["challenging", "helpful"],
            "submitted_at": datetime.datetime(2021, 6, 12, 10, 0),
            "attachments": []
        },
        {
            "student_id": 9,
            "course_code": "ME101",
            "semester": "2022-ODD",
            "rating": 2,
            "comments": "Way too mathematical. Less focus on applications.",
            "tags": ["math-heavy", "dry"],
            "submitted_at": datetime.datetime(2022, 12, 5, 17, 30),
            "attachments": [{"filename": "formulas.pdf", "size_kb": 320}]
        },
        # 63. Document that intentionally omits the attachments field
        {
            "student_id": 10,
            "course_code": "CS101",
            "semester": "2022-ODD",
            "rating": 4,
            "comments": "No attachments document to demonstrate schema-less nature.",
            "tags": ["practical"]
            # attachments field is completely omitted
        }
    ]
    
    try:
        insert_res = feedback_col.insert_many(feedback_docs)
        print(f"Successfully inserted {len(insert_res.inserted_ids)} documents.")
        # 64. Verify the inserts using countDocuments()
        count = feedback_col.count_documents({})
        print(f"Total documents in collection: {count}")
    except Exception as e:
        print(f"Error during insertion (is MongoDB service running?): {e}")
        return

    # -------------------------------------------------------------------------
    # Task 2: CRUD Operations
    # -------------------------------------------------------------------------
    print("\n--- Task 2: CRUD Operations ---")
    
    # 65. READ: Find all feedback documents where rating is 5
    print("\n[65] READ: Rating is 5:")
    for doc in feedback_col.find({"rating": 5}):
        print(f" - Student {doc['student_id']} on {doc['course_code']}: rating {doc['rating']}")
        
    # 66. READ: Find feedback for course CS101 where tags array contains 'challenging'
    print("\n[66] READ: CS101 containing 'challenging' tag:")
    query = {"course_code": "CS101", "tags": "challenging"}
    for doc in feedback_col.find(query):
        print(f" - Course: {doc['course_code']}, Tags: {doc['tags']}, Comments: {doc['comments']}")
        
    # 67. READ: Retrieve only student_id, course_code, and rating (projection) - exclude _id
    print("\n[67] READ: Projections (excluding _id):")
    projection = {"student_id": 1, "course_code": 1, "rating": 1, "_id": 0}
    for doc in feedback_col.find({}, projection):
        print(f" - {doc}")
        
    # 68. UPDATE: For all feedback documents with rating < 3, add needs_review: true
    print("\n[68] UPDATE: Add needs_review=True for ratings < 3:")
    up_res = feedback_col.update_many({"rating": {"$lt": 3}}, {"$set": {"needs_review": True}})
    print(f" - Matched: {up_res.matched_count}, Modified: {up_res.modified_count}")
    
    # 69. UPDATE: Push a new tag 'reviewed' into tags array where needs_review is true
    print("\n[69] UPDATE: Push 'reviewed' tag for needs_review docs:")
    push_res = feedback_col.update_many({"needs_review": True}, {"$push": {"tags": "reviewed"}})
    print(f" - Modified: {push_res.modified_count}")
    
    # Verify updates
    print("\nVerification of updates (needs_review documents):")
    for doc in feedback_col.find({"needs_review": True}):
        print(f" - Course {doc['course_code']}, Rating {doc['rating']}, Tags: {doc['tags']}")

    # 70. DELETE: Delete all feedback documents where the semester is '2021-EVEN'
    print("\n[70] DELETE: Removing semester '2021-EVEN':")
    del_res = feedback_col.delete_many({"semester": "2021-EVEN"})
    print(f" - Deleted {del_res.deleted_count} documents.")


    # -------------------------------------------------------------------------
    # Task 3: Aggregation Pipeline
    # -------------------------------------------------------------------------
    print("\n--- Task 3: Aggregation Pipeline ---")
    
    # 71 & 72. Pipeline 1: Filter '2022-ODD', group by course_code, avg_rating, rename to average_rating, round to 1 dec, sort desc
    pipeline_courses = [
        {"$match": {"semester": "2022-ODD"}},
        {
            "$group": {
                "_id": "$course_code",
                "average_rating": {"$avg": "$rating"},
                "total_feedback": {"$sum": 1}
            }
        },
        {
            "$project": {
                "course_code": "$_id",
                "_id": 0,
                "total_feedback": 1,
                "average_rating": {"$round": ["$average_rating", 1]}
            }
        },
        {"$sort": {"average_rating": -1}}
    ]
    
    print("\n[71/72] Aggregation: Course Ratings for 2022-ODD:")
    for res in feedback_col.aggregate(pipeline_courses):
        print(f" - {res}")

    # 73. Pipeline 2: Unwind tags, group by tag to count frequency, sort descending
    pipeline_tags = [
        {"$unwind": "$tags"},
        {
            "$group": {
                "_id": "$tags",
                "tag_count": {"$sum": 1}
            }
        },
        {"$sort": {"tag_count": -1}}
    ]
    
    print("\n[73] Aggregation: Tag Frequency Leaderboard:")
    for res in feedback_col.aggregate(pipeline_tags):
        print(f" - Tag: '{res['_id']}', Count: {res['tag_count']}")

    # 74. Add an index on course_code and verify its usage
    print("\n[74] INDEX: Adding index on course_code and verifying with explain:")
    feedback_col.create_index([("course_code", ASCENDING)])
    
    explain_data = db.command("explain", {
        "find": "feedback",
        "filter": {"course_code": "CS101"}
    }, verbosity="executionStats")
    
    # Extract query planner stages to confirm IXSCAN
    stages = []
    def find_stages(node):
        if not isinstance(node, dict): return
        if "stage" in node:
            stages.append(node["stage"])
        for k, v in node.items():
            if isinstance(v, dict):
                find_stages(v)
            elif isinstance(v, list):
                for item in v:
                    find_stages(item)
                    
    find_stages(explain_data)
    print(f" - Explain Plan Stages found: {stages}")
    is_ixscan = "IXSCAN" in stages
    print(f" - Verification of Index usage: {'SUCCESS (Uses Index Scan)' if is_ixscan else 'FAILED (Uses Collection Scan)'}")

    client.close()

if __name__ == "__main__":
    run_mongodb_exercise()
