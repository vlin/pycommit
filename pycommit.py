import subprocess
import openai

def get_diffs_from_staged():
    try:
        return shell('git diff --staged')
    except Exception:
        return ''

def summarize_commit_message(diff):
    prompt = f"""
    As a highly skilled programmer, please craft a one-sentence long git commit message for the following diff, sans preface, Limit: 100 chars in english.
    Here is the diff patch file:
    {diff}

    Drawing from the label list provided, pinpoint the optimal label to assign to your recently crafted commit message.
    - build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
    - chore: Updating libraries, copyrights or other repo setting, includes updating dependencies.
    - ci: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, GitHub Actions)
    - docs: Non-code changes, such as fixing typos or adding new documentation
    - feat: a commit of the type feat introduces a new feature to the codebase
    - fix: A commit of the type fix patches a bug in your codebase
    - perf: A code change that improves performance
    - refactor: A code change that neither fixes a bug nor adds a feature
    - style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
    - test: Adding missing tests or correcting existing tests

    Respone the label and commit message as this format(label: commit message).
    """

    completion = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages = [{'role': 'user', 'content': prompt}],
        temperature = 0.5)
    response = completion.choices[0].message['content']
    return response.strip()

def shell(command):
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception(f'Command {command} failed with exit code {process.returncode}')
        return stdout

if __name__ == '__main__':
    diff = get_diffs_from_staged()
    if diff == '':
        print('No staged commits.')
        exit(0)

    print('OpenAI is summarizing the diffs...')    
    commit_message = summarize_commit_message(diff)
    print(f'Commit message:\n{commit_message}')

    choice = input('Do you want to use this commit message? (y/n)')
    if choice == 'y':
        shell(f'git commit -m "{commit_message}"')
        print(f'Committed.')
    else:
        print('Commit aborted.')
