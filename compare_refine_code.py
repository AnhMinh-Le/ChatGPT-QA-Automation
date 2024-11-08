import sys
from chatter import Chatter
import re
import ast


def extract_test_cases(text):
    test_case_blocks = re.split(r"(?:Test case \d+:)", text)[1:]  # Bỏ qua phần đầu tiên vì nó trống
    test_cases = []

    for block in test_case_blocks:
        try:
            input_str, output_str = block.split("Expected output:")
            input_str = input_str.replace("Input:", "").strip()
            output_str = output_str.strip()
        except ValueError:
            continue

        input_list = []

        if input_str and output_str:
            input_parts = re.findall(r"(?:\w+\s*=\s*)?(\[.*?\]|\(.*?\)|\{.*?\}|\'.*?\'|\".*?\"|\d+)", input_str)

            for part in input_parts:
                value_str = part.strip()

                try:
                    parsed_value = ast.literal_eval(value_str)
                except (SyntaxError, ValueError):
                    parsed_value = value_str

                input_list.append(parsed_value)

            if '**' in output_str:
                output_str = output_str.split("**")[0].strip()

            try:
                output = ast.literal_eval(output_str)
            except (SyntaxError, ValueError):
                output = output_str

            test_cases.append({"input": input_list, "output": output})

    return test_cases

def get_function_name(code):

    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node.name
    return None
def compare_code_outputs(code_a, code_b, test_case):
    if not code_a or not code_b:
        return None

    inputs = test_case['input']
    expected_output = test_case['output']


    local_scope = {}
    exec(code_a, {}, local_scope)
    exec(code_b, {}, local_scope)


    func_name_a = get_function_name(code_a)
    func_name_b = get_function_name(code_b)



    if func_name_a is None or func_name_b is None:
        return None

    func_a = local_scope.get(func_name_a)
    func_b = local_scope.get(func_name_b)

    if not func_a or not func_b:
        return None

    result_a = func_a(*inputs)
    result_b = func_b(*inputs)


    if result_a == result_b == expected_output:
        return 0
    elif result_a != expected_output and result_b != expected_output:
        return 1
    elif result_a != result_b and result_a == expected_output:
        return 2
    elif result_a != result_b and result_b == expected_output:
        return 3


def refine_code(code_a, code_b, test_cases_string):

    test_cases = extract_test_cases((test_cases_string))
    refined_code = code_b
    for test_case in test_cases:
        temp = compare_code_outputs(code_a, code_b, test_case)
        temp = 0
        if temp == 0:
            continue
        elif temp == 1:
            #refine code_b based on testcase
            system_prompt = (
                "### System Prompt\n\n"
                "Your task is to refine the following code (code_b) so that it matches the logic and output of test case. "
                "Do not provide any explanations or feedback. Only return the refined code for code_b."
            )

            user_prompt = (
                "### User Prompt\n\n"
                "Please review the following code (code_b) and modify it to match the logic and output of test case, "
                "Code B:\n\n"
                f"```{code_b}```\n\n"
                "Test Case:\n\n"
                f"```{test_case}```\n\n"
                "Return only the modified code for code_b without any explanation or comments."
            )
            chatter = Chatter(system_message=system_prompt)
            full_response = chatter.chat(user_prompt)

            refined_code = full_response.strip()
            code_b = refined_code

        elif temp == 2:
            #refine code_b based on code_a and testcase
            system_prompt = (
                "### System Prompt\n\n"
                "Your task is to refine the following code (code_b) so that it matches the logic and output of code_a. "
                "Ensure that code_b works correctly with the provided test_case.\n\n"
                "Do not provide any explanations or feedback. Only return the refined code for code_b.\n\n"
                "Return only the modified code for code_b."
            )

            user_prompt = (
                "### User Prompt\n\n"
                "Please review the following code (code_b) and modify it to match the behavior and output of code_a, "
                "ensuring that it passes the provided test_case.\n\n"
                "Code A:\n\n"
                f"```{code_a}```\n\n"
                "Code B:\n\n"
                f"```{code_b}```\n\n"
                "Test Case:\n\n"
                f"```{test_case}```\n\n"
                "Return only the modified code for code_b without any explanation or comments."
            )

            chatter = Chatter(system_message=system_prompt)
            full_response = chatter.chat(user_prompt)

            refined_code = full_response.strip()
            code_b = refined_code

        elif temp == 3:
            #refine code_a based on code_b and testcase
            system_prompt = (
                "### System Prompt\n\n"
                "Your task is to refine the following code (code_a) so that it matches the logic and output of code_b. "
                "Ensure that code_b works correctly with the provided test_case.\n\n"
                "Do not provide any explanations or feedback. Only return the refined code for code_a.\n\n"
                "Return only the modified code for code_a."
            )

            user_prompt = (
                "### User Prompt\n\n"
                "Please review the following code (code_a) and modify it to match the behavior and output of code_a, "
                "ensuring that it passes the provided test_case.\n\n"
                "Code A:\n\n"
                f"```{code_a}```\n\n"
                "Code B:\n\n"
                f"```{code_b}```\n\n"
                "Test Case:\n\n"
                f"```{test_case}```\n\n"
                "Return only the modified code for code_a without any explanation or comments."
            )
            chatter = Chatter(system_message=system_prompt)
            full_response = chatter.chat(user_prompt)

            refined_code = full_response.strip()
            code_a = refined_code


    return refined_code

