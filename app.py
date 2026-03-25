from flask import Flask, request, jsonify, render_template, session
import os

app = Flask(__name__)
app.secret_key = "push_notification_manager_secret_key"

# 🔹 Load Knowledge Base from Knowledge_base/qa.txt
def load_kb():
    path = os.path.join("Knowledge_base", "qa.txt")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            blocks = f.read().split("\n\n")
        qa_pairs = []
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 2:
                # Remove "Q:" and "A:" prefixes if they exist
                question = lines[0].replace("Q:", "").strip().lower()
                answer = lines[1].replace("A:", "").strip()
                qa_pairs.append((question, answer))
        return qa_pairs
    except:
        return []

kb = load_kb()

@app.route("/")
def home():
    session.clear() # Ensures a blank start on refresh
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "").lower().strip()
        main_menu = ["Ask a question", "Permissions", "Timing", "Copywriting", "Exit"]

        # 1. TRIGGER: Only respond if user says a greeting
        if any(word in user_message for word in ["hi", "hello", "hey", "menu", "greetings"]):
            session["started"] = True
            session["state"] = "menu"
            return jsonify({
                "reply": "Hi! I am your Push Notification Manager. What would you like to do?",
                "suggestions": main_menu
            })

        # 2. SUB-MENU: "Ask a question"
        if "ask a question" in user_message or user_message == "ask another":
            session["state"] = "asking"
            return jsonify({
                "reply": "I'm ready! Please type your notification question below.",
                "suggestions": ["Menu"]
            })

        # 3. KNOWLEDGE BASE SEARCH: Only active after clicking "Ask a question"
        if session.get("state") == "asking":
            for question, answer in kb:
                if question in user_message:
                    return jsonify({
                        "reply": answer,
                        "suggestions": ["Ask another", "Menu"]
                    })
            # Fallback if question isn't in qa.txt
            return jsonify({
                "reply": "I'm sorry, I don't have that in my guide. Try asking something else!",
                "suggestions": ["Ask another", "Menu"]
            })

        # 4. FIXED WORKFLOW NODES
        if "permissions" in user_message:
            return jsonify({
                "reply": "Use a 'Soft-Ask' before the system prompt to explain value first. 🛡️",
                "suggestions": main_menu
            })
        if "timing" in user_message:
            return jsonify({
                "reply": "Avoid night-time pings. Use local timezones for maximum impact! ⏰",
                "suggestions": main_menu
            })
        if "copywriting" in user_message:
            return jsonify({
                "reply": "Keep headlines under 40 characters to avoid truncation. Be punchy! ✍️",
                "suggestions": main_menu
            })

        # 5. EXIT
        if user_message == "exit":
            session.clear()
            return jsonify({"reply": "Goodbye! I'm here if you need more help. 🔔", "suggestions": []})

        # Default response if bot is "awake" but doesn't understand
        if session.get("started"):
            return jsonify({"reply": "Please use the menu buttons below:", "suggestions": main_menu})
        
        # If user hasn't said 'Hi' yet, return nothing (stays blank)
        return jsonify({"reply": "", "suggestions": []})

    except Exception as e:
        return jsonify({"reply": "I hit a snag! Type 'Menu' to restart.", "suggestions": ["Menu"]})

if __name__ == "__main__":
    app.run(debug=True)