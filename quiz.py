import json
import tkinter as tk
from tkinter import messagebox, simpledialog

class UserManager:
    def __init__(self, user_file="users.json"):
        self.user_file = user_file
        self.users = self.load_users()

    def load_users(self):
        """Loads users from the JSON file."""
        try:
            with open(self.user_file, "r") as file:
                data = json.load(file)
                return data.get("users", [])
        except FileNotFoundError:
            return []    
        
    def save_users(self):
        """Saves the updated list of users to the JSON file."""
        with open(self.user_file, "w") as file:
            json.dump({"users": self.users}, file, indent=4)
            
    def register(self, email, username, password):
        """Registers a new user."""
        if any(user['email'] == email for user in self.users):
            print("This email address is already registered.")
            return False
        
        new_user = {
            "email": email,
            "username": username,
            "password": password
        }
        self.users.append(new_user)
        self.save_users()
        print("Registration successful!")
        return True
    
    def login(self, identifier, password):
        """Logs in a user using either email or username."""
        for user in self.users:
            if (user["email"] == identifier or user["username"] == identifier) and user['password'] == password:
                print("Login successful!")
                return True
        print("Invalid email or password.")
        return False

class QuizCategory:
    def __init__(self, category_file="quiz_categories.json"):
        self.category_file = category_file
        self.categories = self.load_categories()
    
    def load_categories(self):
        """Loads categories from the JSON file."""
        try:
            with open(self.category_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("categories", [])
        except FileNotFoundError:
            return []
    
    def save_categories(self):
        """Saves the updated category list to the JSON file."""
        with open(self.category_file, "w", encoding="utf-8") as file:
            json.dump({"categories": self.categories}, file, indent=4, ensure_ascii=False)
            
    def add_category(self, name):
        """Adds a new category."""
        if any(category['name'] == name for category in self.categories):
            print("This category already exists.")
            return False
        
        new_category = {
            "name": name,
            "questions": []
        }
        self.categories.append(new_category)
        self.save_categories()
        print("Category added!")
        return True
    
    def add_question(self, category_name, question, options, correct_answer):
        """Adds a new question to the specified category."""
        for category in self.categories:
            if category["name"] == category_name:
                new_question = {
                    "question": question,
                    "options": options,
                    "correct_answer": correct_answer
                }
                category["questions"].append(new_question)
                self.save_categories()
                print("Question added!")
                return True
        
        print("Category not found.")
        return False

class Leaderboard:
    def __init__(self, leaderboard_file="leaderboard.json"):
        self.leaderboard_file = leaderboard_file
        self.data = self.load_leaderboard()
    
    def load_leaderboard(self):
        """Loads leaderboard data from the JSON file.
        
        Returns a separate dictionary for each category.
        """
        try:
            with open(self.leaderboard_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def save_leaderboard(self):
        """Saves the leaderboard data to the JSON file."""
        with open(self.leaderboard_file, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)
    
    def update_leaderboard(self, category, identifier, score):
        """Updates the leaderboard for the given category."""
        if category not in self.data:
            self.data[category] = {}
        self.data[category][identifier] = score
        self.save_leaderboard()

    def get_rank(self, category, identifier):
        """Returns the user's rank in the specified category."""
        if category not in self.data:
            return None
        sorted_scores = sorted(self.data[category].items(), key=lambda x: x[1], reverse=True)
        rank = next((i for i, (user, s) in enumerate(sorted_scores, start=1) if user == identifier), None)
        return rank

    def get_full_leaderboard(self, category):
        """Returns the leaderboard information for the specified category."""
        if category not in self.data:
            return []
        return sorted(self.data[category].items(), key=lambda x: x[1], reverse=True)

class QuizWorkflow:
    def __init__(self, user_manager, quiz_category, leaderboard):
        self.user_manager = user_manager
        self.quiz_category = quiz_category
        self.leaderboard = leaderboard
        self.scores = {}
        self.status = {}

    def start_quiz(self):
        """Starts the quiz process."""
        print("Welcome to the quiz!")
        
        # Get login credentials from the user
        identifier = input("Email or username: ")
        password = input("Password: ")
        
        if not self.user_manager.login(identifier, password):
            return
        
        # Reset user's score and set status to "In Progress"
        self.scores[identifier] = 0
        self.status[identifier] = "In Progress"
        
        # Show categories
        print("Categories:")
        for i, category in enumerate(self.quiz_category.categories):
            print(f"{i + 1}. {category['name']}")
        
        # Ask the user to select a category
        try:
            category_choice = int(input("Select a category (by number): ")) - 1
            if category_choice < 0 or category_choice >= len(self.quiz_category.categories):
                raise ValueError("Invalid category selection.")
        except ValueError:
            print("Invalid category selection.")
            self.status[identifier] = "QUIT"
            return
        
        selected_category = self.quiz_category.categories[category_choice]
        
        # Display questions and check answers
        for question in selected_category["questions"]:
            print(question["question"])
            for i, option in enumerate(question["options"]):
                print(f"{i + 1}. {option}")
            
            try:
                answer = int(input("Enter your answer (by number, -1 to quit): "))
                if answer == -1:
                    print("Quiz was quit.")
                    self.status[identifier] = "QUIT"
                    return
                answer -= 1
            except ValueError:
                print("Invalid input.")
                continue
            
            if answer < 0 or answer >= len(question["options"]):
                print("Invalid choice.")
                continue
            
            if question["options"][answer] == question["correct_answer"]:
                print("Correct answer!")
                self.scores[identifier] += 10  # Add 10 points for correct answer
            else:
                print(f"Wrong answer. Correct answer: {question['correct_answer']}")
            
            # Display the user's current score and rank
            self.display_user_status(identifier, selected_category["name"])
        
        print(f"Quiz completed! Your total score: {self.scores[identifier]}")
        self.status[identifier] = "Completed"
        # Update the leaderboard with the category information
        self.leaderboard.update_leaderboard(selected_category["name"], identifier, self.scores[identifier])

    def display_user_status(self, identifier, category):
        """Displays the user's current score and ranking."""
        rank = self.leaderboard.get_rank(category, identifier)
        print(f"Your current score: {self.scores[identifier]}, Rank: {rank}")

class Interface:
    def __init__(self):
        # Create instances of the classes.
        self.user_manager = UserManager()
        self.quiz_category = QuizCategory()
        self.leaderboard = Leaderboard()
        # QuizWorkflow instance can be created if needed, but separate functions are used for the interface flow.
        self.quiz_workflow = QuizWorkflow(self.user_manager, self.quiz_category, self.leaderboard)
        self.current_user = None
        self.current_score = 0
        self.current_category = None
        self.current_question_index = 0

        # Main tkinter window
        self.root = tk.Tk()
        self.root.title("Quiz Application")
        self.root.geometry("500x400")
        
        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        self.create_login_screen()
        
    def create_login_screen(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Login", font=("Arial", 16)).pack(pady=10)
        
        tk.Label(self.main_frame, text="Email or Username:").pack()
        self.identifier_entry = tk.Entry(self.main_frame)
        self.identifier_entry.pack()
        
        tk.Label(self.main_frame, text="Password:").pack()
        self.password_entry = tk.Entry(self.main_frame, show="*")
        self.password_entry.pack()
        
        login_btn = tk.Button(self.main_frame, text="Login", command=self.login_callback)
        login_btn.pack(pady=5)
        
        reg_btn = tk.Button(self.main_frame, text="Register", command=self.create_registration_screen)
        reg_btn.pack(pady=5)
    
    def create_registration_screen(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Register", font=("Arial", 16)).pack(pady=10)
        
        tk.Label(self.main_frame, text="Email:").pack()
        self.reg_email = tk.Entry(self.main_frame)
        self.reg_email.pack()
        
        tk.Label(self.main_frame, text="Username:").pack()
        self.reg_username = tk.Entry(self.main_frame)
        self.reg_username.pack()
        
        tk.Label(self.main_frame, text="Password:").pack()
        self.reg_password = tk.Entry(self.main_frame, show="*")
        self.reg_password.pack()
        
        reg_btn = tk.Button(self.main_frame, text="Register", command=self.register_callback)
        reg_btn.pack(pady=5)
        
        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_login_screen)
        back_btn.pack(pady=5)
    
    def login_callback(self):
        identifier = self.identifier_entry.get()
        password = self.password_entry.get()
        if self.user_manager.login(identifier, password):
            self.current_user = identifier
            self.current_score = 0
            self.show_categories()
        else:
            messagebox.showerror("Error", "Invalid email/username or password!")
    
    def register_callback(self):
        email = self.reg_email.get()
        username = self.reg_username.get()
        password = self.reg_password.get()
        if self.user_manager.register(email, username, password):
            messagebox.showinfo("Success", "Registration successful! Redirecting to login screen.")
            self.create_login_screen()
        else:
            messagebox.showerror("Error", "This email is already registered!")
    
    def show_categories(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Select Category", font=("Arial", 16)).pack(pady=10)
        
        # List categories
        self.category_var = tk.StringVar(self.main_frame)
        categories = [cat["name"] for cat in self.quiz_category.categories]
        if not categories:
            tk.Label(self.main_frame, text="No categories found.").pack()
        else:
            self.category_var.set(categories[0])
            tk.OptionMenu(self.main_frame, self.category_var, *categories).pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        select_btn = tk.Button(button_frame, text="Select", command=self.select_category)
        select_btn.pack(side=tk.LEFT, padx=5)
        
        add_cat_btn = tk.Button(button_frame, text="Add Category", command=self.create_add_category_screen)
        add_cat_btn.pack(side=tk.LEFT, padx=5)
        
        add_quest_btn = tk.Button(button_frame, text="Add Question", command=self.create_add_question_screen)
        add_quest_btn.pack(side=tk.LEFT, padx=5)
        
        logout_btn = tk.Button(self.main_frame, text="Logout", command=self.logout_callback)
        logout_btn.pack(pady=10)
    
    def create_add_category_screen(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Add New Category", font=("Arial", 16)).pack(pady=10)
        
        tk.Label(self.main_frame, text="Category Name:").pack()
        self.new_category_entry = tk.Entry(self.main_frame)
        self.new_category_entry.pack()
        
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        add_btn = tk.Button(button_frame, text="Add", command=self.add_category_callback)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(button_frame, text="Back", command=self.show_categories)
        back_btn.pack(side=tk.LEFT, padx=5)

    def add_category_callback(self):
        new_category = self.new_category_entry.get()
        if new_category:
            if self.quiz_category.add_category(new_category):
                messagebox.showinfo("Success", "Category added successfully!")
                self.show_categories()
            else:
                messagebox.showerror("Error", "This category already exists!")
        else:
            messagebox.showerror("Error", "Please enter a category name!")
            
    def create_add_question_screen(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Add New Question", font=("Arial", 16)).pack(pady=10)
        
        # Category selection
        tk.Label(self.main_frame, text="Select Category:").pack()
        self.question_cat_var = tk.StringVar(self.main_frame)
        categories = [cat["name"] for cat in self.quiz_category.categories]
        if not categories:
            messagebox.showerror("Error", "You must add a category first!")
            self.show_categories()
            return
        # Varsayılan değer olarak "Kategori Seçiniz" koyuyoruz
        self.question_cat_var.set("Kategori Seçiniz")
        tk.OptionMenu(self.main_frame, self.question_cat_var, *categories).pack()
        
        # Soru alanları...
        tk.Label(self.main_frame, text="Question Text:").pack()
        self.question_entry = tk.Entry(self.main_frame, width=50)
        self.question_entry.pack()
        
        tk.Label(self.main_frame, text="Options (separate by commas):").pack()
        self.options_entry = tk.Entry(self.main_frame, width=50)
        self.options_entry.pack()
        
        tk.Label(self.main_frame, text="Correct Answer:").pack()
        self.correct_answer_entry = tk.Entry(self.main_frame)
        self.correct_answer_entry.pack()
        
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        add_btn = tk.Button(button_frame, text="Add", command=self.add_question_callback)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(button_frame, text="Back", command=self.show_categories)
        back_btn.pack(side=tk.LEFT, padx=5)


    def add_question_callback(self):
        category = self.question_cat_var.get()
        if category == "Kategori Seçiniz":
            messagebox.showerror("Error", "Lütfen bir kategori seçiniz!")
            return
        question = self.question_entry.get()
        options = [opt.strip() for opt in self.options_entry.get().split(",")]
        correct_answer = self.correct_answer_entry.get()
        
        if len(options) < 2:
            messagebox.showerror("Error", "You must enter at least 2 options!")
            return
        
        if correct_answer not in options:
            messagebox.showerror("Error", "The correct answer must be one of the options!")
            return
        
        if self.quiz_category.add_question(category, question, options, correct_answer):
            messagebox.showinfo("Success", "Question added successfully!")
            self.show_categories()
        else:
            messagebox.showerror("Error", "An error occurred while adding the question!")

    def select_category(self):
        self.current_category = self.category_var.get()
        self.current_question_index = 0
        self.current_score = 0
        self.show_question()
    
    def show_question(self):
        self.clear_frame()
        # Update leaderboard if the current user is set
        if self.current_user:
            self.leaderboard.update_leaderboard(self.current_category, self.current_user, self.current_score)
        current_rank = self.leaderboard.get_rank(self.current_category, self.current_user) if self.current_user else "-"
        info_label = tk.Label(self.main_frame, text=f"Current Score: {self.current_score}    Your Rank: {current_rank}", font=("Arial", 12))
        info_label.pack(pady=5)
        
        # Display question
        category = next((cat for cat in self.quiz_category.categories if cat["name"] == self.current_category), None)
        if not category:
            messagebox.showerror("Error", "Category not found!")
            return
        
        questions = category.get("questions", [])
        if self.current_question_index >= len(questions):
            self.quiz_finished()
            return
        
        current_question = questions[self.current_question_index]
        tk.Label(self.main_frame, text=current_question["question"], wraplength=450, font=("Arial", 14)).pack(pady=10)
        
        for option in current_question["options"]:
            btn = tk.Button(self.main_frame, text=option, 
                            command=lambda opt=option: self.check_answer(opt, current_question))
            btn.pack(pady=2, fill="x", padx=20)
        
        # "Logout" button allows the user to exit the quiz and return to the login screen.
        logout_btn = tk.Button(self.main_frame, text="Logout", command=self.logout_callback)
        logout_btn.pack(pady=10)
    
    def check_answer(self, selected_option, question):
        if selected_option == question["correct_answer"]:
            self.current_score += 10
            messagebox.showinfo("Correct", "Correct answer!")
        else:
            messagebox.showinfo("Incorrect", f"Incorrect answer!\nCorrect answer: {question['correct_answer']}")
        self.leaderboard.update_leaderboard(self.current_category, self.current_user, self.current_score)
        current_rank = self.leaderboard.get_rank(self.current_category, self.current_user)
        messagebox.showinfo("Info", f"Your updated score: {self.current_score}\nYour rank: {current_rank}")
        self.current_question_index += 1
        self.show_question()
    
    def quiz_finished(self):
        self.leaderboard.update_leaderboard(self.current_category, self.current_user, self.current_score)
        rank = self.leaderboard.get_rank(self.current_category, self.current_user)
        messagebox.showinfo("Quiz Finished", f"Quiz completed!\nTotal score: {self.current_score}\nYour rank: {rank}")
        self.show_leaderboard_screen()
    
    def show_leaderboard_screen(self):
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("Global Leaderboard")
        leaderboard_window.geometry("300x400")
        
        tk.Label(leaderboard_window, text=f"{self.current_category} Leaderboard", font=("Arial", 16)).pack(pady=10)
        
        full_lb = self.leaderboard.get_full_leaderboard(self.current_category)
        if not full_lb:
            tk.Label(leaderboard_window, text="No leaderboard data yet.").pack()
        else:
            for rank, (user, score) in enumerate(full_lb, start=1):
                tk.Label(leaderboard_window, text=f"{rank}. {user} - {score} points", font=("Arial", 12)).pack(pady=2)
        
        close_btn = tk.Button(leaderboard_window, text="Close", command=leaderboard_window.destroy)
        close_btn.pack(pady=10)
        self.show_categories()
    
    def logout_callback(self):
        """Resets the current user information and returns to the login screen."""
        self.current_user = None
        self.current_score = 0
        self.current_category = None
        self.current_question_index = 0
        self.create_login_screen()
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def run(self):
        self.root.mainloop()

# When the program starts, the interface window will open:
if __name__ == "__main__":
    interface = Interface()
    interface.run()


