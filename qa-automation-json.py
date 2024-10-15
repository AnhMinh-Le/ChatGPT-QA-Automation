import json
import csv
import logging
import openai
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




def summarize_issue_info(data) -> list:
    '''
    This sub-func will summarize all the quality issues finded by SA tools into the format of list (contains.
    dictionaries)
    '''
    task_id = data.get('task_id', 'Unknown Task')
    issues = data.get('issues', [])

    if not issues:
        return [{"tool": "None", "issue_code": "No Issues", "issue_description": f"No code quality issues detected for task {task_id}."}]

    issue_counts = {}
    for issue in issues:
        tool = issue.get('tool', 'Unknown Tool')
        issue_code = issue['issue_code']
        issue_description = issue['issue_description']

        key = (tool, issue_code, issue_description)

        if key in issue_counts:
            issue_counts[key] += 1
        else:
            issue_counts[key] = 1

    summarized_issues = []
    for (tool, issue_code, issue_description), count in issue_counts.items():
        if count > 1:
            issue_description += f" (Occurred {count} times)"
        issue_dict = {
            "tool": tool,
            "issue_code": issue_code,
            "issue_description": issue_description
        }
        summarized_issues.append(issue_dict)

    return summarized_issues

def generate_issue_description_and_fix_recommendation(name_of_dataset, combined_data, lang="python"):
    '''
    Based on the result of the function above, we call ChatGPT API to expand issue description, and
    generate fix recommendation.
    '''
    res = []

    #With each id
    for data in combined_data:
        task_id = data.get("task_id", "")
        task_description = data.get("prompt", "")
        solution = data.get("solution", "")
        is_quality_issue = data.get("is_quality_issue", 0)

        issues_infos = summarize_issue_info(data)
        processed_issues = []
        for issue in issues_infos:
            tool = issue.get("tool", "")
            issue_code = issue.get("issue_code", "")
            issue_description = issue.get("issue_description", "")

            feedback = dict()

            system_prompt = (
                f"Your task is to review and provide feedback on a {lang} program. "
                "Focus on identifying any quality issues in the code and providing recommendations to improve it. "
                "For each issue, provide both an issue description and a fix recommendation that you generate. "
                "Also, ensure that your response includes line numbers where applicable.\n\n"
                "In the issue description, clearly summarize the code issues, explain their context, and highlight the affected lines. \n"
                "In the fix recommendation, offer specific and actionable suggestions for improving the code, with line numbers where necessary. "
                "INCLUDE THE RELEVANT PROBLEMATIC CODE SNIPPET DIRECTLY WITHIN THE ISSUE DESCRIPTION FOR BETTER CLARITY.\n"
                "With fix recommendation, you need to provide detailed suggestions as specifically as possible for improvements in the code. \n\n"
                "Please generate an issue description followed by a fix recommendation."
            )

            user_prompt = (
                "Please review the following code and identify any quality issues. "
                "After identifying the issues, provide an issue description followed by a fix recommendation.\n\n"
                "With the issue description, summarize the code issues, extend the issue's context, and clearly indicate the line numbers for each issue, if applicable.\n"
                "With the fix recommendation, provide detailed suggestions as specifically as possible for improvements in the code.\n\n"

                f"Here is the existing code:\n{solution}\n\n"
                f"Quality issues detected by Static Analysis Tools:\n{issue_description}\n\n"
                "Please provide the issue description and fix recommendation in this format:\n\n"
                "Issue Description: <A detailed description of the issue, including the relevant problematic code snippet>\n"
                "Fix Recommendation: <Your detailed fix recommendation here>"
                "REMEMBER:INCLUDE THE RELEVANT PROBLEMATIC CODE SNIPPET DIRECTLY WITHIN THE ISSUE DESCRIPTION FOR BETTER CLARITY.\n"
            )


            chatter = Chatter(system_message=system_prompt)
            full_response = chatter.chat(user_prompt)

            issue_desc_start = full_response.find("Issue Description:")
            fix_recommendation_start = full_response.find("Fix Recommendation:")

            issue_description = ""
            fix_recommendation = ""

            if issue_desc_start != -1:
                if fix_recommendation_start != -1:
                    issue_description = full_response[
                                        issue_desc_start + len("Issue Description:"):fix_recommendation_start].strip()
                    fix_recommendation = full_response[fix_recommendation_start + len("Fix Recommendation:"):].strip()
                else:
                    issue_description = full_response[issue_desc_start + len("Issue Description:"):].strip()
                    fix_recommendation = "No specific fix recommendation found."
            else:
                issue_description = "No issue description found."
                fix_recommendation = "No specific fix recommendation found."

            feedback = {
                "tool": tool,
                "issue_code": issue_code,
                "issue_description": issue_description,
                "fix_recommendation": fix_recommendation
            }
            processed_issues.append(feedback)

        res.append({
        "task_id": task_id,
        "solution": solution,
        "is_quality_issue": is_quality_issue,
        "issues": processed_issues
        })

    if name_of_dataset == 'MBPP':
        report_file = os.path.join(r"\src\QA-bot-result\MBPP", "res-report.json")
        with open(report_file, 'w') as f:
            json.dump(res, f, indent=4)

    if name_of_dataset == 'BigCodeBench':
        report_file = os.path.join(r"\src\QA-bot-result\BigCodeBench", "res-report.json")
        with open(report_file, 'w') as f:
            json.dump(res, f, indent=4)



if __name__ == "__main__":
    with open(
            r"\data\benchmark_datasets\processed_data\results\mbpp_python_feedback_0.json",
            'r') as json_file:
        processed_json_data = json.load(json_file)

    csv_data = []
    with open(
            r"\data\benchmark_datasets\processed_data\results\mbpp_python_feedback_0.csv",
            'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            csv_data.append(row)

    sample = get_complete_data(processed_json_data, csv_data)[350:365]
    generate_issue_description_and_fix_recommendation('MBPP', sample)








