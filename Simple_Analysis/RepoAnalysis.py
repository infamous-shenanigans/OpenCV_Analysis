import os
from pydriller import Repository
import json
from collections import Counter


class RepoAnalyzer:
    def __init__(self, repo_path, output_dir="./output", json_output="repo_analysis.json"):
        # Initialize the repository analyzer for multi-branch analysis.

        self.repo_path = repo_path
        self.output_dir = output_dir
        self.json_output = json_output

        # Metrics storage for all branches
        self.branch_metrics = {}

        # Ensure the output directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.json_output), exist_ok=True)

    def analyze_repository(self):
        # Analyze all branches in the repository and store metrics for each branch
        print(f"Analyzing repository at {self.repo_path} across all branches...")

        for branch in self._get_all_branches():
            print(f"Analyzing branch: {branch}")
            branch_metrics = self._analyze_branch(branch)
            self.branch_metrics[branch] = branch_metrics

        print("Analysis for all branches completed!")

    def _get_all_branches(self):
        # Retrieve all branches in the repository.
        branches = set()
        # Traverse repository once to collect all branch names
        for commit in Repository(self.repo_path).traverse_commits():
            branches.update(commit.branches)
        return sorted(branches)

    def _analyze_branch(self, branch):
        # Perform analysis for a specific branch.

        metrics = {
            "total_commits": 0,
            "authors": Counter(),
            "file_changes": Counter(),
            "lines_added": 0,
            "lines_removed": 0,
        }

        # Analyze the branch using `only_in_branch`
        for commit in Repository(self.repo_path, only_in_branch=branch).traverse_commits():
            metrics["total_commits"] += 1
            metrics["authors"][commit.author.name] += 1
            metrics["lines_added"] += commit.insertions
            metrics["lines_removed"] += commit.deletions

            for modified_file in commit.modified_files:
                if modified_file.filename:
                    metrics["file_changes"][modified_file.filename] += 1

        return metrics

    def export_to_json(self):
        # Save branch metrics as a JSON file.
        print(f"Exporting branch metrics to {self.json_output}...")
        with open(self.json_output, "w") as f:
            json.dump(self.branch_metrics, f, indent=4)
        print("Export completed.")

    def print_summary(self):
        # Print a summary of the branch analysis.
        print("\nRepository Analysis Summary (By Branch):")
        for branch, metrics in self.branch_metrics.items():
            print(f"\nBranch: {branch}")
            print(f"  Total Commits: {metrics['total_commits']}")
            print(f"  Total Authors: {len(metrics['authors'])}")
            print(f"  Lines Added: {metrics['lines_added']}")
            print(f"  Lines Removed: {metrics['lines_removed']}")

            print("  Top Contributors:")
            for author, count in metrics["authors"].most_common(3):
                print(f"    {author}: {count} commits")

            print("  Most Changed Files:")
            for file, changes in metrics["file_changes"].most_common(3):
                print(f"    {file}: {changes} changes")


def main():
    # Define the repository path and output locations
    # Change Path
    REPO_PATH = "/cloned/repo"  # Path to a cloned Git repository
    OUTPUT_DIR = "./output"
    JSON_OUTPUT = "./output/branch_analysis.json"

    # Initialize the analyzer
    analyzer = RepoAnalyzer(repo_path=REPO_PATH, output_dir=OUTPUT_DIR, json_output=JSON_OUTPUT)

    # Perform repository analysis
    analyzer.analyze_repository()

    # Print a summary of results
    analyzer.print_summary()

    # Export results to JSON
    analyzer.export_to_json()


if __name__ == "__main__":
    main()
