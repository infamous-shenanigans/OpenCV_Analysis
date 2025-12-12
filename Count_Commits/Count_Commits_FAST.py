import git
from collections import defaultdict
import json
import os


def count_commits_by_year_and_month(repo_path):
    if not os.path.exists(repo_path):
        raise ValueError(f"The path '{repo_path}' does not exist.")

    try:
        # Load the repository
        repo = git.Repo(repo_path)

        if repo.bare:
            raise ValueError(f"The repository at '{repo_path}' is bare. Please provide a valid working repository.")

        # Dictionary to store commits organized by year and month
        commits_count = defaultdict(lambda: defaultdict(int))

        # Get all branches in the repository
        branches = repo.references  # Includes both local and remote branches

        for branch in branches:
            print(f"Processing branch: {branch}")

            # Switch to branch
            repo.git.checkout(branch)

            # Iterate through commits in the current branch
            for commit in repo.iter_commits(branch):
                commit_year = commit.committed_datetime.year
                commit_month = commit.committed_datetime.month

                # Update the commit count
                commits_count[commit_year][commit_month] += 1

        return commits_count

    except git.exc.GitError as e:
        print(f"Error interacting with the repository: {e}")
        return None


def print_commit_statistics(commits_count):
    print("\nCommit statistics by year and month:")
    for year, months in sorted(commits_count.items()):
        for month, count in sorted(months.items()):
            print(f"Year: {year}, Month: {month:02}, Commits: {count}")


def save_commits_to_json(commits_count, output_path):
    # Convert defaultdict to a regular dictionary for JSON serialization
    commits_dict = {year: dict(months) for year, months in commits_count.items()}

    try:
        with open(output_path, 'w') as json_file:
            json.dump(commits_dict, json_file, indent=4)
        print(f"\nCommit statistics saved to JSON file at: {output_path}")
    except IOError as e:
        print(f"Error writing to JSON file: {e}")


def save_commits_to_text(commits_count, output_path):
    try:
        with open(output_path, 'w') as text_file:
            # Write commit statistics line-by-line
            text_file.write("Commit statistics by year and month:\n")
            for year, months in sorted(commits_count.items()):
                for month, count in sorted(months.items()):
                    text_file.write(f"Year: {year}, Month: {month:02}, Commits: {count}\n")
        print(f"\nCommit statistics saved to text file at: {output_path}")
    except IOError as e:
        print(f"Error writing to text file: {e}")


if __name__ == "__main__":
    ##### Path to the cloned repository (update this to your repository path) #########
    repo_path = "/path/to/cloned/repo"

    # Specify the output JSON and text file paths
    output_json_path = "/path/to/output.json/"
    output_text_path = "/path/to/output.txt"

    commits_count = count_commits_by_year_and_month(repo_path)

    if commits_count:
        print_commit_statistics(commits_count)
        save_commits_to_json(commits_count, output_json_path)
        save_commits_to_text(commits_count, output_text_path)
CountC