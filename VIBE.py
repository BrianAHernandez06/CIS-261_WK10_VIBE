# Brian Hernandez
# CIS261
# VIBE Coding

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

GRADE_THRESHOLDS = [90, 80, 70, 60]
GRADE_LETTERS = ["A", "B", "C", "D", "F"]
DATA_FILE = "student_grades.txt"


def get_letter_grade(average: float) -> str:
    """Return the letter grade for a numeric average."""
    for threshold, letter in zip(GRADE_THRESHOLDS, GRADE_LETTERS):
        if average >= threshold:
            return letter
    return "F"


@dataclass
class Student:
    name: str
    student_id: str
    test_scores: List[float] = field(default_factory=list)
    average: float = field(init=False, default=0.0)
    grade: str = field(init=False, default="F")

    def __post_init__(self) -> None:
        if self.test_scores:
            self.recalculate()

    def set_scores(self, scores: List[float]) -> None:
        if len(scores) != 3:
            raise ValueError("Each student must have exactly three test scores.")
        for score in scores:
            if score < 0 or score > 100:
                raise ValueError("Each score must be between 0 and 100.")
        self.test_scores = scores
        self.recalculate()

    def recalculate(self) -> None:
        self.average = sum(self.test_scores) / 3
        self.grade = get_letter_grade(self.average)

    def average_score(self) -> float:
        return self.average

    def letter_grade(self) -> str:
        return self.grade

    def summary(self) -> str:
        scores_text = ", ".join(f"{score:.2f}" for score in self.test_scores)
        return (
            f"Name: {self.name}\n"
            f"ID: {self.student_id}\n"
            f"Scores: [{scores_text}]\n"
            f"Average: {self.average:.2f}\n"
            f"Grade: {self.grade}"
        )


class StudentRecordManager:
    def __init__(self) -> None:
        self.students: List[Student] = []

    def add_student(self, name: str, student_id: str, scores: List[float]) -> Student:
        if self.find_student_by_id(student_id) is not None:
            raise ValueError(f"Student ID '{student_id}' already exists.")
        student = Student(name=name, student_id=student_id)
        student.set_scores(scores)
        self.students.append(student)
        return student

    def remove_student(self, student_id: str) -> None:
        student = self.find_student_by_id(student_id)
        if student is None:
            raise ValueError(f"Student ID '{student_id}' not found.")
        self.students.remove(student)

    def find_student_by_id(self, student_id: str) -> Optional[Student]:
        normalized = student_id.strip().lower()
        for student in self.students:
            if student.student_id.lower() == normalized:
                return student
        return None

    def search_by_name(self, name_query: str) -> List[Student]:
        query = name_query.strip().lower()
        return [student for student in self.students if query in student.name.lower()]

    def class_average(self) -> float:
        if not self.students:
            return 0.0
        return sum(student.average_score() for student in self.students) / len(self.students)

    def highest_average(self) -> float:
        if not self.students:
            return 0.0
        return max(student.average_score() for student in self.students)

    def lowest_average(self) -> float:
        if not self.students:
            return 0.0
        return min(student.average_score() for student in self.students)

    def class_summary(self) -> str:
        if not self.students:
            return "No students available."
        lines = [student.summary() for student in self.students]
        lines.append("Class statistics:")
        lines.append(f"  Highest average: {self.highest_average():.2f}")
        lines.append(f"  Lowest average: {self.lowest_average():.2f}")
        lines.append(f"  Class average: {self.class_average():.2f}")
        return "\n\n".join(lines)

    def grade_distribution(self) -> dict[str, int]:
        distribution = {letter: 0 for letter in GRADE_LETTERS}
        for student in self.students:
            distribution[student.letter_grade()] += 1
        return distribution

    def student_table(self, students: Optional[List[Student]] = None) -> str:
        records = students if students is not None else self.students
        if not records:
            return "No students currently in the record."

        headers = ["Name", "ID", "Test1", "Test2", "Test3", "Average", "Grade"]
        rows = []
        for student in records:
            rows.append([
                student.name,
                student.student_id,
                f"{student.test_scores[0]:.2f}",
                f"{student.test_scores[1]:.2f}",
                f"{student.test_scores[2]:.2f}",
                f"{student.average:.2f}",
                student.grade,
            ])

        widths = [max(len(str(value)) for value in column) for column in zip(headers, *rows)]
        row_format = " | ".join(f"{{:{width}}}" for width in widths)
        separator = "-+-".join("-" * width for width in widths)

        lines = [row_format.format(*headers), separator]
        for row in rows:
            lines.append(row_format.format(*row))
        return "\n".join(lines)

    def save_to_file(self, filename: str) -> None:
        import csv

        try:
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile, delimiter="|")
                for student in self.students:
                    writer.writerow([
                        student.name,
                        student.student_id,
                        f"{student.test_scores[0]:.2f}",
                        f"{student.test_scores[1]:.2f}",
                        f"{student.test_scores[2]:.2f}",
                        f"{student.average:.2f}",
                        student.grade,
                    ])
        except OSError as error:
            raise OSError(f"Unable to save records to '{filename}': {error}") from error

    def load_from_file(self, filename: str) -> int:
        import csv
        import os

        if not os.path.exists(filename):
            return 0

        loaded = 0
        try:
            with open(filename, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile, delimiter="|")
                for row in reader:
                    if len(row) != 7:
                        continue
                    name, student_id, *values = row
                    try:
                        scores = [float(values[i]) for i in range(3)]
                        if self.find_student_by_id(student_id) is not None:
                            continue
                        self.add_student(name, student_id, scores)
                        loaded += 1
                    except ValueError:
                        continue
        except OSError as error:
            raise OSError(f"Unable to load records from '{filename}': {error}") from error
        return loaded


def prompt_non_empty(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def prompt_float(prompt_text: str) -> float:
    while True:
        try:
            value = float(input(prompt_text).strip())
            if value < 0 or value > 100:
                print("Score must be between 0 and 100.")
                continue
            return value
        except ValueError:
            print("Please enter a valid numeric value.")


def prompt_three_scores() -> List[float]:
    scores: List[float] = []
    for index in range(1, 4):
        scores.append(prompt_float(f"Enter score for Test {index} (0-100): "))
    return scores


def display_message(message: str) -> None:
    print(message)


def display_error(message: str) -> None:
    print(f"Error: {message}")


def load_records(manager: StudentRecordManager, filename: str) -> int:
    try:
        return manager.load_from_file(filename)
    except OSError as error:
        display_error(str(error))
        return 0


def save_records(manager: StudentRecordManager, filename: str) -> bool:
    try:
        manager.save_to_file(filename)
        display_message(f"Records saved to '{filename}'.")
        return True
    except OSError as error:
        display_error(str(error))
        return False


def handle_add_student(manager: StudentRecordManager) -> None:
    name = prompt_non_empty("Enter student name: ")
    student_id = prompt_non_empty("Enter student ID: ")
    scores = prompt_three_scores()
    student = manager.add_student(name, student_id, scores)
    display_message(f"Added student '{student.name}' with ID {student.student_id}.")


def handle_search_student(manager: StudentRecordManager) -> None:
    query = prompt_non_empty("Enter name to search: ")
    matches = manager.search_by_name(query)
    if not matches:
        display_message("No matching students found.")
    else:
        print(manager.student_table(matches))


def handle_view_all_students(manager: StudentRecordManager) -> None:
    print(manager.student_table())


def handle_view_class_report(manager: StudentRecordManager) -> None:
    if not manager.students:
        display_message("No students available.")
        return
    print(manager.class_summary())
    distribution = manager.grade_distribution()
    print("\nGrade distribution:")
    for letter in GRADE_LETTERS:
        print(f"  {letter}: {distribution[letter]}")


def handle_remove_student(manager: StudentRecordManager) -> None:
    student_id = prompt_non_empty("Enter student ID to remove: ")
    manager.remove_student(student_id)
    display_message(f"Removed student ID '{student_id}'.")


def get_menu_choice() -> str:
    import sys

    prompt = "Select an option (1-6 or press ESC to quit): "
    try:
        if sys.stdin.isatty():
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                print(prompt, end="", flush=True)
                tty.setraw(fd)
                choice = sys.stdin.read(1)
                termios.tcflush(fd, termios.TCIFLUSH)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            print()
            if choice == "\x1b":
                return "ESC"
            return choice
    except Exception:
        pass

    return input(prompt).strip()


def display_menu() -> None:
    print("\nStudent Record Manager")
    print("1. Add a new student")
    print("2. Search student by name")
    print("3. View all students")
    print("4. View class report")
    print("5. Remove a student")
    print("6. Quit")


def main() -> None:
    manager = StudentRecordManager()
    loaded = manager.load_from_file(DATA_FILE)
    print("Welcome to the student record manager.")
    if loaded:
        print(f"Loaded {loaded} student record(s) from {DATA_FILE}.")

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == "ESC":
            display_message("Exiting and saving student records.")
            save_records(manager, DATA_FILE)
            break

        try:
            if choice == "1":
                handle_add_student(manager)
                save_records(manager, DATA_FILE)

            elif choice == "2":
                handle_search_student(manager)

            elif choice == "3":
                handle_view_all_students(manager)

            elif choice == "4":
                handle_view_class_report(manager)

            elif choice == "5":
                handle_remove_student(manager)
                save_records(manager, DATA_FILE)

            elif choice == "6":
                display_message("Exiting and saving student records.")
                save_records(manager, DATA_FILE)
                break

            else:
                display_error("Please select a valid option from 1 to 6.")

        except ValueError as error:
            display_error(str(error))


if __name__ == "__main__":
    main()
