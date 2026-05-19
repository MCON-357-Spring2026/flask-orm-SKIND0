"""Exercises: ORM fundamentals.

Implement the TODO functions. Autograder will test them.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from src.exercises.extensions import db
from src.exercises.models import Student, Grade, Assignment


# ===== BASIC CRUD =====

def create_student(name: str, email: str) -> Student:
    """TODO: Create and commit a Student; handle duplicate email.

    If email is duplicate:
      - rollback
      - raise ValueError("duplicate email")
    """
    student = Student(name=name, email=email)

    try:
        db.session.add(student)
        db.session.commit()
        return student

    except IntegrityError:
        db.session.rollback()
        raise ValueError("duplicate email")



def find_student_by_email(email: str) -> Optional[Student]:
    """TODO: Return Student by email or None."""
    if not email:
        return None
    return Student.query.filter_by(email=email).first()


def add_grade(student_id: int, assignment_id: int, score: int) -> Grade:
    """TODO: Add a Grade for the student+assignment and commit.

    If student doesn't exist: raise LookupError
    If assignment doesn't exist: raise LookupError
    If duplicate grade: raise ValueError("duplicate grade")
    """
    if not Student.query.get(student_id):
        raise LookupError("student does not exist")
    if not Assignment.query.get(assignment_id):
        raise LookupError("assignment does not exist")
    grade = Grade(student_id=student_id, assignment_id=assignment_id, score=score)
    try:
        db.session.add(grade)
        db.session.commit()
        return grade
    except IntegrityError:
        db.session.rollback()
        raise ValueError("duplicate grade")


def average_percent(student_id: int) -> float:
    """TODO: Return student's average percent across assignments.

    percent per grade = score / assignment.max_points * 100

    If student doesn't exist: raise LookupError
    If student has no grades: return 0.0
    """
    if not Student.query.get(student_id):
        raise LookupError("student does not exist")
    grades = Grade.query.filter_by(student_id=student_id).all()
    if not grades:
        return 0.0
    percents = [g.score / g.assignment.max_points * 100 for g in grades]
    return sum(percents) / len(percents)


# ===== QUERYING & FILTERING =====

def get_all_students() -> list[Student]:
    """TODO: Return all students in database, ordered by name."""
    return Student.query.order_by(Student.name).all()


def get_assignment_by_title(title: str) -> Optional[Assignment]:
    """TODO: Return assignment by title or None."""
    return Assignment.query.filter_by(title=title).first()


def get_student_grades(student_id: int) -> list[Grade]:
    """TODO: Return all grades for a student, ordered by assignment title.

    If student doesn't exist: raise LookupError
    """
    if not Student.query.get(student_id):
        raise LookupError("student does not exist")
    return (Grade.query
            .filter_by(student_id=student_id)
            .join(Assignment)
            .order_by(Assignment.title)
            .all())


def get_grades_for_assignment(assignment_id: int) -> list[Grade]:
    """TODO: Return all grades for an assignment, ordered by student name.

    If assignment doesn't exist: raise LookupError
    """
    if not Assignment.query.get(assignment_id):
        raise LookupError("assignment does not exist")
    return (Grade.query
            .filter_by(assignment_id=assignment_id)
            .join(Student)
            .order_by(Student.name)
            .all())


# ===== AGGREGATION =====

def total_student_grade_count() -> int:
    """TODO: Return total number of grades in database."""
    return Grade.query.count()


def highest_score_on_assignment(assignment_id: int) -> Optional[int]:
    """TODO: Return the highest score on an assignment, or None if no grades.

    If assignment doesn't exist: raise LookupError
    """
    if not Assignment.query.get(assignment_id):
        raise LookupError("assignment does not exist")
    result = db.session.query(func.max(Grade.score)).filter_by(assignment_id=assignment_id).scalar()
    return result


def class_average_percent() -> float:
    """TODO: Return average percent across all students and all assignments.

    percent per grade = score / assignment.max_points * 100
    Return average of all these percents.
    If no grades: return 0.0
    """
    grades = Grade.query.join(Assignment).all()
    if not grades:
        return 0.0
    percents = [g.score / g.assignment.max_points * 100 for g in grades]
    return sum(percents) / len(percents)


def student_grade_count(student_id: int) -> int:
    """TODO: Return number of grades for a student.

    If student doesn't exist: raise LookupError
    """
    if not Student.query.get(student_id):
        raise LookupError("student does not exist")
    return Grade.query.filter_by(student_id=student_id).count()


# ===== UPDATING & DELETION =====

def update_student_email(student_id: int, new_email: str) -> Student:
    """TODO: Update a student's email and commit.

    If student doesn't exist: raise LookupError
    If new email is duplicate: rollback and raise ValueError("duplicate email")
    Return the updated student.
    """
    student = Student.query.get(student_id)
    if not student:
        raise LookupError("student does not exist")
    student.email = new_email
    try:
        db.session.commit()
        return student
    except IntegrityError:
        db.session.rollback()
        raise ValueError("duplicate email")


def delete_student(student_id: int) -> None:
    """TODO: Delete a student and all their grades; commit.

    If student doesn't exist: raise LookupError
    """
    student = Student.query.get(student_id)
    if not student:
        raise LookupError("student does not exist")
    db.session.delete(student)
    db.session.commit()


def delete_grade(grade_id: int) -> None:
    """TODO: Delete a grade by id; commit.

    If grade doesn't exist: raise LookupError
    """
    grade = Grade.query.get(grade_id)
    if not grade:
        raise LookupError("grade does not exist")
    db.session.delete(grade)
    db.session.commit()


# ===== FILTERING & FILTERING WITH AGGREGATION =====

def students_with_average_above(threshold: float) -> list[Student]:
    """TODO: Return students whose average percent is above threshold.

    List should be ordered by average percent descending.
    percent per grade = score / assignment.max_points * 100
    """
    students = Student.query.all()
    results = []
    for s in students:
        if s.grades:
            avg = sum(g.score / g.assignment.max_points * 100 for g in s.grades) / len(s.grades)
            if avg > threshold:
                results.append((s, avg))
    results.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in results]


def assignments_without_grades() -> list[Assignment]:
    """TODO: Return assignments that have no grades yet, ordered by title."""
    return (Assignment.query
            .filter(~Assignment.grades.any())
            .order_by(Assignment.title)
            .all())


def top_scorer_on_assignment(assignment_id: int) -> Optional[Student]:
    """TODO: Return the Student with the highest score on an assignment.

    If assignment doesn't exist: raise LookupError
    If no grades on assignment: return None
    If tie (multiple students with same high score): return any one
    """
    if not Assignment.query.get(assignment_id):
        raise LookupError("assignment does not exist")
    grade = (Grade.query
             .filter_by(assignment_id=assignment_id)
             .order_by(Grade.score.desc())
             .first())
    return grade.student if grade else None

