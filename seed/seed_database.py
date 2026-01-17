import json
from models.course import Course
from models.lesson import Lesson
from models.quiz import Quiz
from models.question import Question
from extentions import db
from app import app

with open("seed/course.mock.json", "r") as file:
    data = json.load(file)

with app.app_context():
    print("Dropping and recreating database tables...")
    db.drop_all()
    db.create_all()

    question_id_counter = 0
    quiz_id_counter = 0
    lesson_id_counter = 0

    for course_data in data["courses"]:
        course = Course(
            id=course_data["id"],
            course_number=course_data["course_number"],
            course_title=course_data["title"],
            is_last_course=course_data["isLastCourse"]
        )
        db.session.add(course)

        for lesson_data in course_data["lessons"]:
            lesson_id_counter += 1
            lesson = Lesson(
                id=lesson_id_counter,
                lesson_number=lesson_data["lesson_number"],
                course_id=course.id,
                title=lesson_data["title"],
                duration=lesson_data["duration"],
                is_completed=lesson_data["isCompleted"],
                is_last_lesson=lesson_data["isLastLesson"],
                summary_congrats=lesson_data["summaryCongrats"],
                summary_text=lesson_data["summaryText"]
            )
            db.session.add(lesson)

            quiz_id_counter += 1
            quiz = Quiz(
                id=quiz_id_counter,
                lesson_id=lesson.id,
                quiz_number=lesson_data["quiz"][0]["quiz_number"]
            )
            db.session.add(quiz)

            for question_data in lesson_data["quiz"]:
                question_id_counter += 1
                question = Question(
                    id=question_id_counter,
                    quiz=quiz,
                    question_number=question_data["question_number"],
                    question_text=question_data["question_text"],
                    option_1=question_data["optionsAnswer"][0],
                    option_2=question_data["optionsAnswer"][1],
                    option_3=question_data["optionsAnswer"][2],
                    correct_option=question_data["correctAnswer"]
                )
                db.session.add(question)

    db.session.commit()
    print("Seeding completed successfully.")