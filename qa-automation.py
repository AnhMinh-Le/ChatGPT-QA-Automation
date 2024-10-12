import json
import csv
import logging
import openai
import sys
sys.path.append(r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\src")
from libs.config import settings
from chatter import Chatter
import os


def get_complete_data(processed_json_data, csv_data) -> list:
    '''
    We only keep the necessary features of two datasets: csv file and json file.
    '''
    combined_data = []
    for json_entry in processed_json_data:
        task_id = json_entry.get("id", "")
        solution = "\n".join(json_entry.get("generated_code", []))
        is_quality_issue = json_entry.get("is_quality_issue", "")

        issues = []

        for csv_entry in csv_data:
            if csv_entry["id"] == task_id:
                issue = {
                    "tool": csv_entry["analysis_tool"],
                    "issue_code": csv_entry["issue_code"],
                    "issue_description": csv_entry["issue_info"]
                }
                issues.append(issue)

        combined_data.append({
            "task_id": task_id,
            "solution": solution,
            "is_quality_issue": is_quality_issue,
            "issues": issues
        })
    return combined_data




def summarize_issue_description(data):
    '''
    This sub-func will summarize all the quality issues finded by SA tools into only one text format.
    '''
    task_id = data.get('task_id', 'Unknown Task')
    issues = data.get('issues', [])

    if not issues:
        return f"No code quality issues detected for task {task_id}."

    description = f"Issues found in task {task_id}:\n"

    issue_counts = {}
    for issue in issues:
        issue_code = issue['issue_code']
        issue_description = issue['issue_description']

        key = f"{issue_code}: {issue_description}"

        if key in issue_counts:
            issue_counts[key] += 1
        else:
            issue_counts[key] = 1

    for issue_key, count in issue_counts.items():
        if count > 1:
            description += f"- {issue_key} (Occurred {count} times)\n"
        else:
            description += f"- {issue_key}\n"

    return description.strip()

def generate_issue_description_and_fix_recommendation(name_of_dataset, combined_data, lang="python"):
    '''
    Based on the result of the function above, we call ChatGPT API to expand issue description, and
    generate fix recommendation.
    '''

    for data in combined_data:
        task_id = data.get("task_id", "")
        task_name = data.get("prompt", "Unnamed_Task")
        task_description = data.get("prompt", "")
        solution = data.get("solution", "")
        is_quality_issue = data.get("is_quality_issue", 0)
        issues = data.get("issues", [])

        if is_quality_issue or issues:
            issues_description = summarize_issue_description(data)

            system_prompt = (
                f"Your task is to review and provide feedback on a {lang} program. "
                "You should focus on identifying any quality issues in the code and providing recommendations to improve it."
            )

            user_prompt = (
                "Please review the following code and summarize any quality issues you identify, "
                "along with specific recommendations for fixing these problems. "
                "Also, ensure that your response includes line numbers where applicable.\n\n"
                f"Here is the existing code:\n{solution}\n\n"
                f"Task description:\n{task_description}\n\n"
                f"Quality issue detected by Static Analysis Tools:\n{issues_description}\n\n"
                "In your response, include two sections:\n"
                "1. **Issue Description**: Summarize the code issues, extend the issue's context, found and clearly indicate the line numbers for each issue, if applicable.\n"
                "2. **Fix Recommendations**: Provide detailed suggestions as specifically as possible for improvements in the code. "
                "REMEMBER: find any additional issues (if there exists) or quality concerns and include their corresponding line numbers."
            )

            chatter = Chatter(system_message=system_prompt)
            full_response = chatter.chat(user_prompt)

            issue_desc_start = full_response.find("Issue Description:")
            fix_recommendation_start = full_response.find("Fix Recommendations:")
            issue_desc = ""
            fix_recommendation = ""

            if issue_desc_start != -1:
                if fix_recommendation_start != -1:
                    issue_desc = full_response[
                                 issue_desc_start + len("Issue Description:"):fix_recommendation_start].strip()
                    fix_recommendation = full_response[fix_recommendation_start + len("Fix Recommendations:"):].strip()

                    fix_recommendation_lines = fix_recommendation.splitlines()
                    fix_recommendation_lines = [line for line in fix_recommendation_lines if line]  # Xóa dòng trống

                    if not fix_recommendation_lines:
                        fix_recommendation = "No specific fix recommendation found."
                    else:
                        fix_recommendation = "\n".join(fix_recommendation_lines).strip()
                else:
                    issue_desc = full_response[issue_desc_start + len("Issue Description:"):].strip()
                    fix_recommendation = "No specific fix recommendation found."
            else:
                issue_desc = "No issue description found."
                fix_recommendation = "No specific fix recommendation found."

            if name_of_dataset == 'MBPP':
                report_file = os.path.join(r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\src\QA-bot-result\MBPP", f"Taskid{task_id}-report.txt")
                with open(report_file, 'w') as f:
                    f.write(f"Task ID: {task_id}\n" + "Issue Description:\n" + issue_desc + "\n\n" + "Fix Recommendation:\n" + fix_recommendation)

            if name_of_dataset == 'BigCodeBench':
                report_file = os.path.join(r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\src\QA-bot-result\BigCodeBench",
                                           f"Taskid{task_id}-report.txt")
                with open(report_file, 'w') as f:
                    f.write(f"Task ID: {task_id}\n" + "Issue Description:\n" + issue_desc + "\n\n" + "Fix Recommendation:\n" + fix_recommendation)


if __name__ == "__main__":
    with open(
            r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\data\benchmark_datasets\processed_data\results\mbpp_python_feedback_0.json",
            'r') as json_file:
        processed_json_data = json.load(json_file)

    csv_data = []
    with open(
            r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\data\benchmark_datasets\processed_data\results\mbpp_python_feedback_0.csv",
            'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            csv_data.append(row)

    sample = get_complete_data(processed_json_data, csv_data)[200: 205]
    generate_issue_description_and_fix_recommendation('MBPP', sample)








