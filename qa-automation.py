import json
import csv
import logging
import openai
import sys
sys.path.append(r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\src")
from libs.config import settings
from chatter import Chatter
import os


with open(
        r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\data\benchmark_datasets\processed_data\mbpp_processed.json",
        'r') as json_file_1:
    jsonl_data = json.load(json_file_1)

with open(
        r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\data\benchmark_datasets\processed_data\results\mbpp_python_feedback_0.json",
        'r') as json_file:
    processed_json_data = json.load(json_file)

csv_rows = []
with open(
        r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\data\benchmark_datasets\processed_data\results\mbpp_python_feedback_0.csv",
        'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        csv_rows.append(row)

combined_data = []

for json_entry in processed_json_data:
    task_id = json_entry.get("id", "")
    solution = "\n".join(json_entry.get("generated_code", []))
    is_quality_issue = json_entry.get("is_quality_issue", "")

    prompt = ""
    for original_entry in jsonl_data:
        if original_entry.get("task_id", "") == int(task_id):
            prompt = original_entry.get("prompt", "")
            break

    issues = []

    for csv_entry in csv_rows:
        if csv_entry["id"] == task_id:
            issue = {
                "tool": csv_entry["analysis_tool"],
                "issue_code": csv_entry["issue_code"],
                "issue_description": csv_entry["issue_info"]
            }
            issues.append(issue)

    combined_data.append({
        "task_id": task_id,
        "prompt": prompt,
        "solution": solution,
        "is_quality_issue": is_quality_issue,
        "issues": issues
    })



combined_data = [{'task_id': '1', 'prompt': 'Write a function to find the minimum cost path to reach (m, n) from (0, 0) for the given cost matrix cost[][] and a position (m, n) in cost[][].', 'solution': 'def min_cost(cost, m, n):\n\n    # Create a 2D array to store the minimum cost to reach each cell\n\n    min_cost_arr = [[0 for j in range(n+1)] for i in range(m+1)]\n\n    \n\n    # Initialize the first cell with the cost of reaching it\n\n    min_cost_arr[0][0] = cost[0][0]\n\n    \n\n    # Initialize the first row with the cumulative cost of reaching each cell\n\n    for j in range(1, n+1):\n\n        min_cost_arr[0][j] = min_cost_arr[0][j-1] + cost[0][j]\n\n    \n\n    # Initialize the first column with the cumulative cost of reaching each cell\n\n    for i in range(1, m+1):\n\n        min_cost_arr[i][0] = min_cost_arr[i-1][0] + cost[i][0]\n\n    \n\n    # Fill the rest of the cells with the minimum cost to reach each cell\n\n    for i in range(1, m+1):\n\n        for j in range(1, n+1):\n\n            min_cost_arr[i][j] = cost[i][j] + min(min_cost_arr[i-1][j], min_cost_arr[i][j-1])\n\n    \n\n    # Return the minimum cost to reach the destination cell\n\n    return min_cost_arr[m][n]', 'is_quality_issue': 1, 'issues': [{'tool': 'flake8', 'issue_code': 'W293', 'issue_description': 'W293 blank line contains whitespace'}, {'tool': 'flake8', 'issue_code': 'W293', 'issue_description': 'W293 blank line contains whitespace'}, {'tool': 'flake8', 'issue_code': 'W293', 'issue_description': 'W293 blank line contains whitespace'}, {'tool': 'flake8', 'issue_code': 'E501', 'issue_description': 'E501 line too long (80 > 79 characters)'}, {'tool': 'flake8', 'issue_code': 'W293', 'issue_description': 'W293 blank line contains whitespace'}, {'tool': 'flake8', 'issue_code': 'E501', 'issue_description': 'E501 line too long (93 > 79 characters)'}, {'tool': 'flake8', 'issue_code': 'W293', 'issue_description': 'W293 blank line contains whitespace'}, {'tool': 'flake8', 'issue_code': 'W292', 'issue_description': 'W292 no newline at end of file'}, {'tool': 'pylint', 'issue_code': 'C0303', 'issue_description': '1-min_cost.py:4:0: C0303: Trailing whitespace (trailing-whitespace)'}, {'tool': 'pylint', 'issue_code': 'C0303', 'issue_description': '1-min_cost.py:7:0: C0303: Trailing whitespace (trailing-whitespace)'}, {'tool': 'pylint', 'issue_code': 'C0303', 'issue_description': '1-min_cost.py:11:0: C0303: Trailing whitespace (trailing-whitespace)'}, {'tool': 'pylint', 'issue_code': 'C0303', 'issue_description': '1-min_cost.py:15:0: C0303: Trailing whitespace (trailing-whitespace)'}, {'tool': 'pylint', 'issue_code': 'C0303', 'issue_description': '1-min_cost.py:20:0: C0303: Trailing whitespace (trailing-whitespace)'}, {'tool': 'pylint', 'issue_code': 'C0304', 'issue_description': '1-min_cost.py:22:0: C0304: Final newline missing (missing-final-newline)'}, {'tool': 'pylint', 'issue_code': 'C0114', 'issue_description': '1-min_cost.py:1:0: C0114: Missing module docstring (missing-module-docstring)'}, {'tool': 'pylint', 'issue_code': 'C0103', 'issue_description': '1-min_cost.py:1:0: C0103: Module name "1-min_cost" doesn\'t conform to snake_case naming style (invalid-name)'}, {'tool': 'pylint', 'issue_code': 'C0116', 'issue_description': '1-min_cost.py:1:0: C0116: Missing function or method docstring (missing-function-docstring)'}]}]

def summarize_issue_description(data):
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
                    f.write("Issue Description:\n" + issue_desc + "\n\n" + "Fix Recommendation:\n" + fix_recommendation)

            if name_of_dataset == 'BigCodeBench':
                report_file = os.path.join(r"C:\Users\IDEAPAD\ChatGPT-CodeGenAnalysis\src\QA-bot-result\BigCodeBench",
                                           f"Taskid{task_id}-report.txt")
                with open(report_file, 'w') as f:
                    f.write("Issue Description:\n" + issue_desc + "\n\n" + "Fix Recommendation:\n" + fix_recommendation)

            print(f"Task ID: {task_id}")
            print(f"Issue Description:\n{issue_desc}")
            print(f"Fix Recommendations:\n{fix_recommendation}")

generate_issue_description_and_fix_recommendation('MBPP', combined_data)


